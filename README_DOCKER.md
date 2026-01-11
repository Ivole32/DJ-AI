# DJ-AI Docker Setup

## Quick Start

1. Install Docker and Docker Compose.
2. Navigate to the `docker` directory:
   ```bash
   cd docker
   ```
3. Start all services:
   ```bash
   docker-compose up --build
   ```

## Services

- **PostgreSQL**: User and playlist database (port 5432)
- **Redis**: API caching (port 6379)
- **API**: FastAPI backend (port 8080)
- **Analyzer**: Audio feature extraction
- **ML Model**: Track transition prediction
- **Frontend**: Web UI (port 3000)

## Volumes

- PostgreSQL and Redis data are persisted in local volumes for durability.

## Environment Variables

- API environment variables are set via `.env` in `/api`.
- You can scale or restart services individually as needed.
- Code changes in `/api`, `/frontend`, `/analyzer`, `/ml_model` are reflected in containers for development.

## Troubleshooting

View logs for all services:
```bash
docker-compose logs -f
```

---
For more details, see the main project README.
