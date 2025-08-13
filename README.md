Here’s your full content combined into a single `README.md` file, ready to use:

```markdown
# Thumbworx - Week 5 Full Integration

## Project Overview
This project demonstrates a full-stack integration of a live vehicle tracking and analytics system using:

- **Flask**: AI / tracking microservice (polls Traccar, caches positions, ETA stub)
- **Laravel**: API backend for orchestration, authentication, and persistence
- **Next.js**: Frontend live map and dashboard (react-leaflet)
- **PostgreSQL & Redis**: Data persistence and caching
- **Metabase**: Analytics & dashboards

Data flow:  
`Traccar demo → Flask microservice → Redis/Postgres → Laravel API → Next.js dashboard → Metabase analytics`.

---

## Project Layout

```

thumbworx/
├─ backend-laravel/     # Laravel app (API + migrations)
├─ ai-flask/            # Flask microservice (Traccar proxy, ETA)
├─ frontend-next/       # Next.js app (map + dashboard)
├─ infra/               # docker-compose.yml, scripts
└─ docs/                # README, architecture, presentation slides

````

---

## 1. Local Development (Docker Compose)

Use `infra/docker-compose.yml` to spin up all services locally:

```bash
docker-compose up --build
````

**Services included:**

* **Postgres**: `postgres:15`, database `thumbworx`
* **Redis**: `redis:7` caching for positions
* **Flask**: `ai-flask` microservice, polls Traccar, caches to Redis, persists to DB
* **Laravel**: `backend-laravel` API backend
* **Next.js**: `frontend-next` live map/dashboard

**Docker Compose snippet (minimal example)**

```yaml
version: "3.8"
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: thumbworx
      POSTGRES_USER: thumb_user
      POSTGRES_PASSWORD: thumb_pass
    ports: ["5432:5432"]
    volumes: ["pgdata:/var/lib/postgresql/data"]

  redis:
    image: redis:7
    ports: ["6379:6379"]

  flask:
    build: ../ai-flask
    command: gunicorn app:app -b 0.0.0.0:5000 --workers=3
    ports: ["5000:5000"]
    environment:
      - DATABASE_URL=postgresql://thumb_user:thumb_pass@postgres:5432/thumbworx
      - REDIS_URL=redis://redis:6379/0
      - TRACCAR_BASE_URL=https://demo.traccar.org
      - TRACCAR_USER=demo_user
      - TRACCAR_PASS=demo_pass
    depends_on: ["postgres","redis"]

  laravel:
    build: ../backend-laravel
    ports: ["8000:80"]
    environment:
      - DB_HOST=postgres
      - DB_DATABASE=thumbworx
      - DB_USERNAME=thumb_user
      - DB_PASSWORD=thumb_pass
      - TRACCAR_BASE_URL=https://demo.traccar.org
      - TRACCAR_USER=demo_user
      - TRACCAR_PASS=demo_pass
    depends_on: ["postgres"]

  next:
    build: ../frontend-next
    ports: ["3000:3000"]
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000

volumes:
  pgdata:
```

---

## 2. Flask Microservice (`ai-flask`)

**Features:**

* Polls Traccar REST API endpoints `/api/devices` & `/api/positions`
* Caches latest positions in Redis (TTL 30s)
* Persists positions to PostgreSQL
* Lightweight ETA endpoint (`/api/predict_eta`) using geodesic distance

**Example Flask app snippet:**

```python
@app.route("/api/traccar/positions")
def positions_api():
    res = requests.get(f"{TRACCAR_BASE}/api/positions", auth=traccar_auth(), params=request.args)
    items = res.json()
    r.set("latest_positions", json.dumps(items), ex=30)
    with engine.begin() as conn:
        for p in items:
            conn.execute(positions.insert().values(
                device_id=p.get("deviceId"),
                latitude=p.get("latitude"),
                longitude=p.get("longitude"),
                speed=p.get("speed"),
                timestamp=datetime.fromtimestamp(p.get("deviceTime")/1000.0) if p.get("deviceTime") else datetime.utcnow(),
                attributes=json.dumps(p.get("attributes", {}))
            ))
    return jsonify(items)
```

**Dependencies:**

```
Flask
requests
redis
psycopg2-binary
SQLAlchemy
gunicorn
python-dotenv
geopy
joblib
```

**Run locally:**

```bash
docker build -t ai-flask ./ai-flask
docker run -p 5000:5000 ai-flask
```

---

## 3. Laravel Backend (`backend-laravel`)

* Acts as API gateway and orchestration layer
* Routes:

  * `/api/traccar/devices` → fetch devices from Traccar
  * `/api/traccar/positions` → fetch positions from Flask or Traccar
* Optional: persist positions to PostgreSQL

**Example migration:**

```php
Schema::create('positions', function (Blueprint $table) {
    $table->id();
    $table->integer('device_id')->nullable();
    $table->decimal('latitude', 10, 7)->nullable();
    $table->decimal('longitude', 10, 7)->nullable();
    $table->integer('speed')->nullable();
    $table->timestamp('device_time')->nullable();
    $table->json('attributes')->nullable();
    $table->timestamps();
});
```

**Traccar Controller example:**

```php
$response = Http::withBasicAuth(config('services.traccar.user'), config('services.traccar.pass'))
                ->get(config('services.traccar.base_url').'/api/positions');
$data = $response->json();
```

---

## 4. Next.js Frontend (`frontend-next`)

* Live map with `react-leaflet` showing device markers
* Auto-refresh every 5s using `swr`
* Fetches positions from Laravel API (or directly from Flask)

**Install dependencies:**

```bash
npm install react-leaflet leaflet swr
```

**Example usage:**

```javascript
const { data } = useSWR(`${api}/api/traccar/positions`, fetcher, { refreshInterval: 5000 });
<MapWithNoSSR positions={data || []} />
```

---

## 5. Live Data Patterns

**A. Polling (simplest)**
Flask or Laravel periodically calls Traccar `/api/positions` and caches/persists results. Frontend polls your API.

**B. Event Forwarding (webhook)**
Traccar can forward real-time notifications to your Flask endpoint (requires self-hosted Traccar).

**Example Flask poller (cron / APScheduler):**

```python
from apscheduler.schedulers.background import BackgroundScheduler
def poll_positions():
    requests.get("http://localhost:5000/api/traccar/positions")
sched = BackgroundScheduler()
sched.add_job(poll_positions, 'interval', seconds=10)
sched.start()
```

---

## 6. Deployment Recommendations

| Service  | Platform         | Notes                          |
| -------- | ---------------- | ------------------------------ |
| Flask    | Render           | Supports Gunicorn, env vars    |
| Laravel  | Railway / Heroku | PHP + Postgres, run migrations |
| Next.js  | Vercel           | Frontend hosting               |
| Postgres | Railway / Render | Managed DB                     |
| Redis    | Railway / Render | Managed cache                  |
| Metabase | Docker / Cloud   | Analytics dashboards           |

---

## 7. Metabase Analytics

* Connect to PostgreSQL
* Dashboards examples:

  * Latest positions → map/heatmap
  * Position history → average speed by region
  * Driver performance → join with deliveries

---

## 8. Security & Environment Variables

* Never commit `.env`
* Use platform secrets / config vars
* HTTPS endpoints
* Limit CORS
* Store Traccar credentials securely

---

## 9. CI & GitHub

* Single repo recommended
* Include:

  * README.md
  * `infra/docker-compose.yml`
  * `backend-laravel/`, `ai-flask/`, `frontend-next/`
  * `docs/` for deployment logs, slides, demo scripts
* Optional: GitHub Actions for CI/CD

---

## 10. Quick Commands

**Redis cache example (Flask):**

```python
r.set("thumbworx:heatmap:data", json.dumps(positions), ex=30)
```

**Next.js client fetch:**

```javascript
const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/traccar/positions`);
const positions = await res.json();
```

**Run Laravel migrations:**

```bash
php artisan migrate --force
```

---

## 11. Final Deliverables

* README.md (architecture, endpoints, deploy steps)
* `infra/docker-compose.yml`
* `backend-laravel/` with migrations + Traccar proxy
* `ai-flask/` with `app.py`, Dockerfile, model artifacts
* `frontend-next/` with map/dashboard
* `docs/`:

  * Deployment logs
  * Presentation slides
  * Demo script
  * Live URLs + test credentials

---

## 12. Suggested Timeline

* **Day 1:** Local Docker compose + Flask + Next.js map
* **Day 2:** Laravel API endpoints & Postgres persistence
* **Day 3:** Redis caching & scheduled poller
* **Day 4:** Deploy Flask + Laravel, configure env vars
* **Day 5:** Deploy Next.js + Metabase, polish README & demo

```

This version is ready to be saved as `README.md`
```
