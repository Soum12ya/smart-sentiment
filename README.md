 # 🧠 Smart Sentiment Analyzer

> A **production-grade learning project** covering: REST API, ML/NLP, Data Structures, Docker, CI/CD, GitHub, and Cloud Deployment.

---

## 📐 System Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                         INTERNET                             │
│                                                              │
│  ┌─────────────┐    HTTP/REST    ┌──────────────────────┐    │
│  │  Frontend   │ ─────────────►  │   FastAPI Backend    │    │
│  │  (HTML/JS)  │ ◄─────────────  │   /analyze           │    │
│  │  Nginx      │    JSON         │   /analytics         │    │
│  └─────────────┘                 │   /history           │    │
│                                  └─────────┬───────────┘     │
│                                            │                 │
│                          ┌─────────────────┼──────────────┐  │
│                          │     In-Memory Data Structures  │  │
│                          │  LRU Cache  Ring Buffer  Map   │  │
│                          └─────────────────┬──────────────┘  │
│                                            │                 │
│                                  ┌─────────▼────────┐        │
│                                  │   ML Pipeline    │        │
│                                  │ Tokenize→Score   │        │
│                                  │ →Classify→Conf.  │        │
│                                  └──────────────────┘        │
└──────────────────────────────────────────────────────────────┘

CI/CD:  GitHub Push → Actions (Test→Build→Push) → Docker Hub → Render
```

---

## 🗂️ Project Structure

```
smart-sentiment/
├── backend/
│   ├── main.py            # FastAPI app + ML model + data structures
│   ├── tests.py           # pytest unit + integration tests
│   ├── requirements.txt
│   └── Dockerfile         # Multi-stage build
├── frontend/
│   └── index.html         # Full SPA — no framework needed
├── docs/
│   └── SYSTEM_DESIGN.md   # Architecture + UML + Sequence diagrams
├── .github/
│   └── workflows/
│       └── ci-cd.yml      # GitHub Actions pipeline
├── docker-compose.yml
└── README.md
```

---

## 🧩 What You'll Learn (Concept Map)

| Concept | Where It Appears |
|---------|-----------------|
| **REST API** | FastAPI routes, HTTP verbs, status codes |
| **ML / NLP** | Tokenizer, scorer, classifier, confidence |
| **Data Structures** | LRU Cache (OrderedDict), Ring Buffer (deque), Frequency Map (defaultdict) |
| **Docker** | Multi-stage Dockerfile, docker-compose, health checks |
| **CI/CD** | GitHub Actions: test → build → push → deploy |
| **API Design** | Versioning, validation, error handling, caching |
| **System Design** | Layers, separation of concerns, scalability |

---

## 🚀 Quick Start (Local)

### Option A — Python directly

```bash
# 1. Clone
git clone https://github.com/YOUR_USERNAME/smart-sentiment
cd smart-sentiment

# 2. Install
pip install -r backend/requirements.txt

# 3. Run API
cd backend && uvicorn main:app --reload --port 8000

# 4. Open frontend
open frontend/index.html
# Or use Live Server in VS Code
```

### Option B — Docker Compose (recommended)

```bash
docker-compose up --build
# API:      http://localhost:8000
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/docs
```

---

## 🧪 Run Tests

```bash
cd backend
pip install pytest httpx
pytest tests.py -v
```

Expected output:
```
PASSED tests.py::TestLRUCache::test_basic_get_put
PASSED tests.py::TestLRUCache::test_eviction
PASSED tests.py::TestLRUCache::test_lru_ordering
PASSED tests.py::TestSentimentModel::test_positive
PASSED tests.py::TestSentimentModel::test_negative
PASSED tests.py::TestSentimentModel::test_neutral
PASSED tests.py::TestSentimentModel::test_negation
PASSED tests.py::TestSentimentModel::test_confidence_range
PASSED tests.py::TestAPI::test_health
PASSED tests.py::TestAPI::test_analyze_positive
PASSED tests.py::TestAPI::test_analyze_empty_text
PASSED tests.py::TestAPI::test_analyze_too_long
PASSED tests.py::TestAPI::test_caching
PASSED tests.py::TestAPI::test_batch
PASSED tests.py::TestAPI::test_history
PASSED tests.py::TestAPI::test_analytics
```

---

## 🐳 Docker Guide

### Build manually

```bash
# Build
docker build -t smart-sentiment ./backend

# Run
docker run -p 8000:8000 smart-sentiment

# Check health
docker ps   # see health status
```

### Push to Docker Hub

```bash
docker tag smart-sentiment YOUR_USERNAME/smart-sentiment:latest
docker push YOUR_USERNAME/smart-sentiment:latest
```

### Multi-stage build explained

```dockerfile
# Stage 1: Builder (has build tools, larger)
FROM python:3.11-slim AS builder
RUN pip install --prefix=/install -r requirements.txt

# Stage 2: Production (copies only what's needed, smaller image)
FROM python:3.11-slim AS production
COPY --from=builder /install /usr/local
```
**Result:** Image is ~3x smaller than single-stage.

---

## 🔄 CI/CD Setup

### Step 1: Add GitHub Secrets

Go to: GitHub repo → Settings → Secrets → Actions → New secret

| Secret | Value |
|--------|-------|
| `DOCKERHUB_USERNAME` | Your Docker Hub username |
| `DOCKERHUB_TOKEN` | Docker Hub access token |
| `RENDER_DEPLOY_HOOK_URL` | From Render service settings |

### Step 2: Push to main

```bash
git add .
git commit -m "feat: add sentiment analyzer"
git push origin main
```

### What happens automatically:
1. **GitHub Actions** triggers
2. Tests run (`pytest`)
3. Docker image built
4. Image pushed to Docker Hub
5. Render redeploys automatically

---

## ☁️ Deploy to Internet (Free)

### Backend — Render.com

1. Sign up at [render.com](https://render.com)
2. New → Web Service → Connect GitHub repo
3. Settings:
   - Root Directory: `backend`
   - Runtime: Docker
   - Port: 8000
4. Deploy → Copy your URL (e.g. `https://smart-sentiment.onrender.com`)

### Frontend — GitHub Pages

1. Go to repo Settings → Pages
2. Source: Deploy from branch `main`, folder `/frontend`
3. Your frontend lives at: `https://YOUR_USERNAME.github.io/smart-sentiment`
4. Update the API URL in the frontend to your Render URL

### Alternative — Railway.app

```bash
# One command deploy
railway up
```

---

## 📡 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/analyze` | Analyze single text |
| `POST` | `/analyze/batch` | Analyze up to 10 texts |
| `GET` | `/history` | Last 50 analyses |
| `GET` | `/analytics` | Stats & cache info |
| `DELETE` | `/cache` | Clear LRU cache |
| `GET` | `/docs` | Swagger UI |

### Example Request

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "This product is absolutely amazing!"}'
```

### Example Response

```json
{
  "text": "This product is absolutely amazing!",
  "label": "POSITIVE",
  "score": 1.5,
  "confidence": 37.5,
  "token_count": 6,
  "cached": false,
  "timestamp": "2025-01-01T12:00:00",
  "processing_ms": 0.123
}
```

---

## 🧠 ML Model Explained

This project uses a **rule-based NLP model** — perfect for learning fundamentals before jumping to transformers:

```
Input: "This is absolutely not terrible"

Tokens: [this, is, absolutely, not, terrible]

Processing:
  "absolutely" → intensifier → multiplier = 1.5
  "not"        → negator    → negate = True
  "terrible"   → negative   → score = -1 * 1.5 = -1.5
                              negate=True → score = +1.5

Final score: +1.5 → POSITIVE
```

**Why not use transformers?**
- You can swap in HuggingFace `transformers` later — the API interface stays the same
- Rule-based lets you SEE exactly how classification works
- Zero dependencies, instant startup, deployable anywhere

---

## 📊 Data Structures Used

### LRU Cache (OrderedDict)

```python
# O(1) get and put — avoids recomputing known texts
cache = LRU Cache(capacity=100)
cache.put("I love this", {label: "POSITIVE", ...})
cache.get("I love this")  # instant, no ML needed
```

### Ring Buffer (deque with maxlen)

```python
# Fixed-size queue — old entries auto-evicted
history = deque(maxlen=50)
history.append(record)  # O(1), never exceeds 50 items
```

### Frequency Map (defaultdict)

```python
# Count label occurrences — O(1) update
label_counts = defaultdict(int)
label_counts["POSITIVE"] += 1  # no KeyError ever
```

---

## 🏗️ System Design Principles Applied

| Principle | Implementation |
|-----------|---------------|
| **Separation of concerns** | Frontend / API / ML / Data are separate layers |
| **Stateless API** | Each request is independent (cache is optional optimization) |
| **Fail fast** | Input validation before any computation |
| **Cache-aside** | Check cache first, compute on miss, update cache |
| **Health checks** | `/health` endpoint for Docker + load balancers |
| **12-factor app** | Config via env vars, stateless processes, port binding |
| **Security** | Non-root Docker user, input length limits, CORS config |

---

## 📈 Extend This Project

Once you understand the fundamentals, try these:

1. **Add a real ML model** — `pip install transformers`, swap `analyze_sentiment()`
2. **Add a database** — PostgreSQL via SQLAlchemy to persist history
3. **Add authentication** — JWT tokens, rate limiting per user
4. **Add Redis** — Replace in-memory LRU with distributed Redis cache
5. **Add monitoring** — Prometheus metrics, Grafana dashboard
6. **Add Kubernetes** — Scale horizontally with K8s deployments
