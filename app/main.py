import json
import logging

from fastapi import FastAPI, Request, Response

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("webhook")

app = FastAPI()


@app.post("/webhook")
async def webhook(request: Request) -> Response:
    body = await request.body()
    try:
        payload = json.dumps(json.loads(body), indent=2)
    except ValueError:
        payload = body.decode("utf-8", errors="replace")
    log.info("Webhook received\nHeaders: %s\nBody:\n%s", dict(request.headers), payload)
    return Response(status_code=200)
