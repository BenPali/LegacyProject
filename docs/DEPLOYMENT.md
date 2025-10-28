# GeneWeb Deployment Guide

Quick guide for deploying GeneWeb locally or on a server.

## Prerequisites

- Python 3.11+
- Docker (optional, for containerized deployment)

## Directory Structure

```
LegacyProject/
├── geneweb_databases/    # Your genealogical databases
│   ├── *.ged            # GEDCOM input files
│   └── *.gwb/           # Generated databases (gitignored)
├── modernProject/        # Python implementation
└── Makefile             # Deployment commands
```

---

## Local Deployment

### Start Daemon

```bash
make start-daemon
```

Access at: http://localhost:2317/

### Manage Daemon

```bash
make status-daemon    # Check if running
make stop-daemon      # Stop daemon
make restart-daemon   # Restart daemon
```

### Logs

```bash
cat /tmp/geneweb-daemon.log
```

---

## Docker Deployment

### Build Image

```bash
make docker-build
```

Creates a 266MB optimized image with:
- Python 3.11 slim base
- Non-root user (security)
- Health checks
- Auto-restart

### Run Container

```bash
make docker-run
```

Access at: http://localhost:2317/

### Manage Container

```bash
make docker-logs      # View logs
make docker-stop      # Stop container
docker ps             # Check status
```

---

## Server/VPS Deployment

### Quick Setup

1. **Clone repository:**
```bash
git clone <your-repo-url>
cd LegacyProject
```

2. **Add your databases:**
```bash
cp yourfile.ged geneweb_databases/
```

3. **Start with Docker:**
```bash
make docker-build
make docker-run
```

4. **Access from anywhere:**
```
http://YOUR_SERVER_IP:2317/
```

### With Domain & HTTPS

1. **Install nginx:**
```bash
sudo apt update
sudo apt install nginx certbot python3-certbot-nginx
```

2. **Configure nginx:**
```bash
sudo nano /etc/nginx/sites-available/geneweb
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:2317;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

3. **Enable site:**
```bash
sudo ln -s /etc/nginx/sites-available/geneweb /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

4. **Get SSL certificate:**
```bash
sudo certbot --nginx -d your-domain.com
```

5. **Access securely:**
```
https://your-domain.com/
```

---

## Database Management

### Auto-Import (Recommended)

Simply place `.ged` files in `geneweb_databases/` and start the daemon:

```bash
cp yourfile.ged geneweb_databases/
make start-daemon
```

The daemon automatically converts any `.ged` files that don't have corresponding `.gwb` databases.

### Manual Import

```bash
cd modernProject
PYTHONPATH=. python -m bin.ged2gwb \
  ../geneweb_databases/yourfile.ged \
  -o ../geneweb_databases/yourfile.gwb
```

### Location

All databases are in: `geneweb_databases/`
- `.ged` files: GEDCOM input (keep in git)
- `.gwb/` directories: Generated databases (gitignored, auto-created)

### Backup

```bash
tar -czf backup-$(date +%Y%m%d).tar.gz geneweb_databases/*.gwb
```

### Restore

```bash
tar -xzf backup-20251028.tar.gz
```

---

## Makefile Commands

### Daemon Management
```bash
make start-daemon     # Start local daemon on port 2317
make stop-daemon      # Stop daemon and cleanup
make restart-daemon   # Restart daemon
make status-daemon    # Show daemon status and PID
```

### Docker
```bash
make docker-build     # Build production image
make docker-run       # Start container (detached)
make docker-stop      # Stop and remove container
make docker-logs      # Follow container logs
```

### Testing
```bash
make test            # Run all tests
make coverage        # Generate coverage report
```

### Cleanup
```bash
make clean           # Remove test artifacts
make fclean          # Deep clean all generated files
```

---

## Configuration

### Port

Default: 2317

Change in:
- `Makefile`: `-p 2317`
- `docker-compose.yml`: `ports: "2317:2317"`
- `Dockerfile`: CMD arguments

### Database Directory

Default: `geneweb_databases/`

Configured in:
- `Makefile`: `-wd ../geneweb_databases`
- `docker-compose.yml`: volume mount
- `Dockerfile`: `-wd /data`

### Workers

Default: 20 worker threads

Set in `bin/gwd.py` initialization

---

## Security Checklist

### For Production:

- [ ] Use HTTPS (nginx + certbot)
- [ ] Configure firewall
- [ ] Non-root user in Docker ✓
- [ ] Regular backups
- [ ] Update dependencies
- [ ] Monitor logs
- [ ] Health checks enabled ✓

### Firewall (UFW):
```bash
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable
```

---

## Troubleshooting

### Port Already in Use

```bash
make stop-daemon
# or
lsof -i :2317
kill <PID>
```

### Daemon Won't Start

Check logs:
```bash
cat /tmp/geneweb-daemon.log
```

### Docker Issues

View logs:
```bash
make docker-logs
```

Check container:
```bash
docker ps -a
docker inspect geneweb-daemon
```

### Database Not Found

Verify location:
```bash
ls -la geneweb_databases/*.gwb
```

Ensure daemon uses correct path:
```bash
make status-daemon
```

---

## Performance Tuning

### Docker Resources

Edit `docker-compose.yml`:
```yaml
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 2G
```

### System Resources

Recommended for production:
- CPU: 2+ cores
- RAM: 2+ GB
- Disk: 10+ GB SSD

---

## Monitoring

### Health Check

Container health:
```bash
docker inspect --format='{{.State.Health.Status}}' geneweb-daemon
```

Manual check:
```bash
curl http://localhost:2317/
```

### Logs

Local daemon:
```bash
tail -f /tmp/geneweb-daemon.log
```

Docker:
```bash
make docker-logs
```

---

## Quick Reference

| Task | Command |
|------|---------|
| Start locally | `make start-daemon` |
| Start with Docker | `make docker-run` |
| Stop all | `make stop-daemon && make docker-stop` |
| View status | `make status-daemon` |
| View logs | `cat /tmp/geneweb-daemon.log` |
| Import GEDCOM | See "Database Management" above |
| Backup databases | `tar -czf backup.tar.gz geneweb_databases/*.gwb` |

---

**For more details:** See root `DEPLOYMENT.md`
**For development:** See `../README.md`

**Last Updated:** 2025-10-28
