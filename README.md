# test-pd-webhook

A test webhook receiver. `POST /webhook` logs the request headers and full body to the container logs and returns an empty `200 OK`.

It runs as two containers:

- `app`: FastAPI on Uvicorn, port 8000, only reachable inside the Docker network.
- `caddy`: terminates HTTPS on 443 with a free Let's Encrypt certificate and forwards to `app`. Port 80 redirects to HTTPS and is used for certificate validation.

No domain is needed. The hostname comes from [sslip.io](https://sslip.io), which resolves `54-12-34-56.sslip.io` to `54.12.34.56`.

## EC2 setup

1. Allocate an Elastic IP and associate it with the instance, so the hostname stays stable.
2. In the instance's security group, allow inbound TCP 80 and 443 from `0.0.0.0/0`.
3. Install Docker and the compose plugin. On Amazon Linux 2023:

   ```sh
   sudo dnf install -y docker
   sudo systemctl enable --now docker
   sudo usermod -aG docker $USER   # log out and back in afterwards
   sudo mkdir -p /usr/local/lib/docker/cli-plugins
   sudo curl -SL "https://github.com/docker/compose/releases/latest/download/docker-compose-linux-$(uname -m)" \
     -o /usr/local/lib/docker/cli-plugins/docker-compose
   sudo chmod +x /usr/local/lib/docker/cli-plugins/docker-compose
   ```

## Deploy

Copy this directory to the instance, then:

```sh
cp .env.example .env
# edit .env: DOMAIN=<elastic-ip-with-dashes>.sslip.io
docker compose up -d --build
```

The first start takes a few seconds while Caddy gets the certificate. Check progress with `docker compose logs caddy`.

## Test

```sh
curl -i -X POST https://54-12-34-56.sslip.io/webhook \
  -H 'Content-Type: application/json' \
  -d '{"hello":"world"}'
```

## View payloads

```sh
docker compose logs -f app
```

JSON bodies are pretty-printed. Anything else is logged as text. Logs rotate at 10 MB, keeping 3 files per container.

## Update or stop

```sh
docker compose up -d --build   # after changing code
docker compose down            # stop; the certificate is kept in the caddy_data volume
```
