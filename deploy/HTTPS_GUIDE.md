# HTTPS Deployment Guide

This document explains how I configured HTTPS for ReadyAPI on the VPS. I wrote it in a student-friendly way, but it still reflects the real setup used in the project.

The production architecture is intentionally simple:

1. the FastAPI application runs locally on `127.0.0.1:8000`
2. `nginx` receives public traffic on ports 80 and 443
3. Let's Encrypt provides the trusted TLS certificate
4. HTTP traffic is redirected to HTTPS
5. the certificate is renewed automatically with Certbot

This is a realistic production pattern and it also makes the system easier to explain in a dissertation.

---

## 1. Why I Used This Setup

I did not expose the Python application directly to the internet. Instead, I placed `nginx` in front of the app and used it as a reverse proxy. I chose this design because it is:

- more secure than exposing FastAPI directly
- easier to manage in production
- closer to a real-world deployment
- simple enough to explain clearly in an academic report

The VPS in this project is public, so HTTPS is important. Without HTTPS, credentials, API requests, and user data would travel in plain text.

---

## 2. Production Deployment Overview

### 2.1 What Happens in Production

The real production flow is:

```text
User browser
	↓
https://readyapi.net
	↓
nginx on the VPS
	↓
FastAPI running on 127.0.0.1:8000
	↓
Search engine, authentication, and database logic
```

### 2.2 Main Files Used

The deployment is based on these files:

- `deploy/nginx.conf` for the reverse proxy and TLS configuration
- `deploy/setup_https.sh` for automatic installation and certificate setup
- `scripts/run_server_https.py` for local HTTPS development
- `scripts/run_server.py` for normal local development

---

## 3. Production HTTPS Configuration

### 3.1 Server Requirements

Before enabling HTTPS, the server needs:

- a Linux VPS with root or sudo access
- a domain pointing to the VPS public IP
- ports 80 and 443 open in the firewall
- the FastAPI app running locally on port 8000

### 3.2 What the Setup Script Does

The script `deploy/setup_https.sh` automates the deployment process. Based on the actual script in the repository, it does the following:

1. checks that it is running as root
2. asks for the domain and email address
3. installs `nginx`, `certbot`, and `python3-certbot-nginx`
4. replaces the placeholder domain in `nginx.conf`
5. enables the nginx site and disables the default site
6. tests the nginx configuration
7. restarts nginx
8. requests a certificate from Let's Encrypt
9. enables automatic renewal using `certbot.timer`

This is useful because it reduces manual errors and gives me a repeatable deployment process.

### 3.3 Nginx Configuration

The file `deploy/nginx.conf` contains two server blocks.

#### HTTP block

- listens on port 80
- serves the Let's Encrypt challenge path
- redirects all normal traffic to HTTPS

#### HTTPS block

- listens on port 443 with SSL and HTTP/2
- uses the certificate stored in `/etc/letsencrypt/live/readyapi.net/`
- applies modern TLS settings
- adds security headers
- forwards requests to `http://127.0.0.1:8000`

The important idea is that only `nginx` is public. The Python app stays private on the local machine.

### 3.4 Security Headers

The nginx configuration includes these headers:

- `Strict-Transport-Security`
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`

These do not replace proper application security, but they improve the overall protection of the site.

### 3.5 Automatic Certificate Renewal

Let's Encrypt certificates expire, so renewal is important. The script enables `certbot.timer` to make the process automatic.

You can test renewal with:

```bash
sudo certbot renew --dry-run
```

This is a safe test because it checks the renewal process without actually changing the live certificate.

---

## 4. Production Service Management

### 4.1 Why the App Should Run as a Service

On the VPS, the application should run continuously in the background. For that reason, the correct approach is to run it through `systemd` and `gunicorn`, not manually inside a terminal.

This gives me:

- automatic restart if the process crashes
- better control over startup and shutdown
- a more professional production setup
- a clearer explanation in the project report

### 4.2 Typical Service Configuration

In this project, the service is expected to start FastAPI through Gunicorn and Uvicorn workers, bound to `127.0.0.1:8000`.

```ini
[Unit]
Description=ReadyAPI FastAPI Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/AI_API
Environment="PATH=/var/www/AI_API/venv/bin"
ExecStart=/var/www/AI_API/venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 127.0.0.1:8000
Restart=always

[Install]
WantedBy=multi-user.target
```

This separation between the web server and the application server is an important part of the deployment design.

---

## 5. Local HTTPS for Development

For local testing, the project includes `scripts/run_server_https.py`.

### 5.1 What the Script Does

This script:

1. loads the application settings
2. checks whether the certificate files already exist
3. creates a self-signed certificate with `openssl` if needed
4. starts Uvicorn with SSL enabled

The result is a local HTTPS server on `https://localhost:8000`.

### 5.2 Why I Added It

I needed this script so I could test HTTPS behavior before deployment. It is useful for:

- checking that the application starts correctly with SSL
- testing the docs page locally
- validating HTTPS-related configuration without using the production certificate

### 5.3 Important Limitation

The certificate created by this script is self-signed, so browsers will show a warning. That is normal. It should only be used for development and testing.

---

## 6. How I Configured the Server in Practice

The real production setup for ReadyAPI follows these principles:

- the domain is `readyapi.net`
- the public IP of the VPS is used only for incoming traffic
- `nginx` manages the public HTTPS endpoint
- FastAPI is hidden behind the reverse proxy
- Let's Encrypt provides the trusted certificate
- Certbot handles certificate renewal

This is a strong configuration because it keeps the application simple while still giving it a professional production layer.

---

## 7. Verification Steps

After deployment, I would verify the server with these commands:

```bash
curl -I http://readyapi.net
curl https://readyapi.net/api/v1/search/health
sudo nginx -t
sudo certbot renew --dry-run
```

### 7.1 What Each Check Confirms

- `curl -I http://readyapi.net` checks that HTTP redirects to HTTPS
- `curl https://readyapi.net/api/v1/search/health` checks that the public API is responding correctly
- `sudo nginx -t` checks that nginx syntax is valid
- `sudo certbot renew --dry-run` checks that certificate renewal works

These checks are important because deployment is not only about installation. It is also about verifying that the server behaves correctly over time.

---

## 8. Post-Deployment Checklist

Before considering the HTTPS setup complete, I would confirm that:

- HTTPS works on the public domain
- HTTP redirects automatically to HTTPS
- the certificate is valid and trusted
- the Python app only listens on the local interface
- `DEBUG` is disabled in production
- the allowed origins use the HTTPS domain
- the firewall only exposes the necessary ports
- automatic renewal is enabled
- nginx logs are available for debugging

---

## 9. Troubleshooting

### 9.1 If nginx Does Not Start

```bash
sudo nginx -t
sudo journalctl -u nginx
```

This helps identify configuration mistakes or service errors.

### 9.2 If Port 443 Is Busy

```bash
sudo lsof -i :443
sudo systemctl status nginx
```

This tells me whether another process is already using the HTTPS port.

### 9.3 If Certificate Renewal Fails

```bash
sudo journalctl -u certbot
sudo certbot renew --force-renewal
```

This helps diagnose certificate-related problems.

### 9.4 If the Browser Shows "Not Secure"

That usually means one of these things:

- the certificate is self-signed
- the domain does not match the certificate
- the HTTPS redirect is not working
- the browser cache is outdated

In production, this should not happen if the setup is correct.

---

## 10. Why This Is a Good Solution for My TFG

I think this configuration is appropriate for my final year project because it demonstrates a complete deployment workflow:

- application development in Python
- production HTTPS configuration
- certificate management
- reverse proxy deployment
- secure server organization

It also shows that I understand not only how to build an API, but also how to deploy it in a realistic and maintainable way.

---

## 11. Short Summary

In summary, the HTTPS setup used in ReadyAPI is based on:

- a FastAPI app running locally on the VPS
- an `nginx` reverse proxy in front of it
- a Let's Encrypt certificate for production
- a self-signed certificate only for local testing
- automatic renewal through Certbot

This gave me a secure, understandable, and production-style deployment that fits the technical goals of the project.

---

## 12. Useful Files

- `deploy/nginx.conf` - public HTTPS and reverse proxy configuration
- `deploy/setup_https.sh` - automated HTTPS setup
- `scripts/run_server_https.py` - local HTTPS testing server
- `scripts/run_server.py` - normal local development server

---

## 13. References

- Let's Encrypt Documentation: https://letsencrypt.org/docs/
- Nginx SSL Configuration: https://ssl-config.mozilla.org/
- FastAPI Deployment Guide: https://fastapi.tiangolo.com/deployment/
