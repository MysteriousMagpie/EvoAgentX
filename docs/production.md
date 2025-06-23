# Production Deployment Guide

This guide covers how to serve EvoAgentX in production using a reverse proxy with HTTPS and how to run the application automatically after system reboot.

## Reverse Proxy Setup

EvoAgentX runs on `localhost:8000` by default. To expose it as `https://evoagentx.duckdns.org` you can use either **Nginx** or **Caddy**.

### Using Nginx

1. Install Nginx and obtain TLS certificates with Certbot (or any ACME client).
2. Create a configuration like:

```nginx
server {
    listen 80;
    server_name evoagentx.duckdns.org;
    location / { return 301 https://$host$request_uri; }
}

server {
    listen 443 ssl;
    server_name evoagentx.duckdns.org;

    ssl_certificate     /etc/letsencrypt/live/evoagentx.duckdns.org/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/evoagentx.duckdns.org/privkey.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Using Caddy

Create a `Caddyfile`:

```Caddyfile
evoagentx.duckdns.org {
    reverse_proxy localhost:8000
}
```

Run `caddy run --config /path/to/Caddyfile`. Caddy will automatically manage HTTPS certificates.

## Systemd Service

To keep EvoAgentX running after reboot, create `deploy/vite.service`:

```ini
[Unit]
Description=EvoAgentX FastAPI server
After=network.target

[Service]
Type=simple
WorkingDirectory=/path/to/EvoAgentX
ExecStart=/usr/bin/python run_evoagentx.py
Restart=always
Environment=OPENAI_API_KEY=<your-openai-api-key>

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl enable /path/to/EvoAgentX/deploy/vite.service
sudo systemctl start vite.service
```

## Building the Frontend

The React frontend is located in the `client` directory. Build the production assets with Vite:

```bash
cd client
npm install
npm run build
```

The compiled files are placed in `client/dist`. Serve this directory with a static web server or configure the FastAPI backend to serve it.

