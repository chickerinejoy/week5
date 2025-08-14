# Thumbworx - Week 5 Full Integration

## Overview
Full-stack vehicle tracking & analytics using Flask, Laravel, Next.js, PostgreSQL, Redis, and Metabase.

Data flow: `Traccar demo → Flask → Redis/Postgres → Laravel → Next.js → Metabase`

## Clone & Run Locally
```bash
git clone <repo_url>
cd thumbworx/infra
docker-compose up --build
```
Services:
- PostgreSQL: `thumbworx` DB
- Redis: caching
- Flask: AI/tracking microservice
- Laravel: API backend
- Next.js: dashboard

## Flask Microservice
- Polls `/api/devices` & `/api/positions`
- Caches in Redis (TTL 30s)
- Persists positions to PostgreSQL
- ETA endpoint `/api/predict_eta`

Run locally:
```bash
docker build -t ai-flask ../ai-flask
docker run -p 5000:5000 ai-flask
```

## Laravel Backend
- API gateway: `/api/traccar/devices` & `/api/traccar/positions`
- Persists positions to PostgreSQL

Run migrations:
```bash
php artisan migrate --force
```

## Next.js Frontend
- Live map with `react-leaflet`
- Auto-refresh every 5s

Install deps:
```bash
npm install react-leaflet leaflet swr
```

## Quick Commands
Fetch positions:
```javascript
const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/traccar/positions`);
const positions = await res.json();
```

Redis cache example (Flask):
```python
r.set("thumbworx:heatmap:data", json.dumps(positions), ex=30)
```

## Deployment Recommendations
- Flask: Render
- Laravel: Railway / Heroku
- Next.js: Vercel
- PostgreSQL / Redis: Managed
- Metabase: Docker / Cloud

## Security
- Never commit `.env`
- Use platform secrets
- HTTPS endpoints
- Limit CORS

## Deliverables
- README.md
- `infra/docker-compose.yml`
- `backend-laravel/`
- `ai-flask/`
- `frontend-next/`
- `docs/` (logs, slides, demo scripts, test credentials)

