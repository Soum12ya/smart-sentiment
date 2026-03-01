"""
Smart Sentiment Analyzer - FastAPI Backend
Demonstrates: REST API, ML (NLP), Data Structures, System Design
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import time
import re
from collections import deque, defaultdict
from datetime import datetime
import statistics

app = FastAPI(
    title="Smart Sentiment Analyzer API",
    description="ML-powered text sentiment analysis with analytics",
    version="1.0.0"
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Data Structures ──────────────────────────────────────────────────────────
# LRU Cache using OrderedDict (O(1) get/put)
from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity: int = 100):
        self.cache = OrderedDict()
        self.capacity = capacity

    def get(self, key: str):
        if key not in self.cache:
            return None
        self.cache.move_to_end(key)
        return self.cache[key]

    def put(self, key: str, value):
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)

# Ring buffer for recent history (fixed-size queue)
history_buffer: deque = deque(maxlen=50)

# Frequency map for analytics
label_counts: defaultdict = defaultdict(int)
confidence_scores: List[float] = []

# Cache instance
cache = LRUCache(capacity=100)


# ─── Simple ML Model (Rule-Based NLP) ─────────────────────────────────────────
POSITIVE_WORDS = {
    "great", "excellent", "awesome", "amazing", "fantastic", "good", "love",
    "happy", "wonderful", "best", "beautiful", "outstanding", "superb", "joy",
    "perfect", "brilliant", "delightful", "pleasant", "fabulous", "terrific"
}
NEGATIVE_WORDS = {
    "bad", "terrible", "awful", "horrible", "worst", "hate", "ugly", "poor",
    "disappointing", "dreadful", "pathetic", "dull", "boring", "sad", "angry",
    "frustrated", "useless", "broken", "failure", "disgusting"
}
INTENSIFIERS = {"very", "extremely", "absolutely", "totally", "completely", "so"}
NEGATORS = {"not", "no", "never", "neither", "nor", "barely", "hardly"}


def analyze_sentiment(text: str) -> dict:
    """
    Naive but educational ML pipeline:
    Tokenize → Normalize → Score → Classify → Confidence
    """
    tokens = re.findall(r'\b\w+\b', text.lower())
    
    score = 0
    multiplier = 1.0
    negate = False

    for i, token in enumerate(tokens):
        if token in NEGATORS:
            negate = True
            continue
        if token in INTENSIFIERS:
            multiplier = 1.5
            continue
        
        word_score = 0
        if token in POSITIVE_WORDS:
            word_score = 1 * multiplier
        elif token in NEGATIVE_WORDS:
            word_score = -1 * multiplier

        if negate:
            word_score *= -1
            negate = False

        score += word_score
        multiplier = 1.0  # reset after use

    # Classify
    if score > 0.5:
        label = "POSITIVE"
    elif score < -0.5:
        label = "NEGATIVE"
    else:
        label = "NEUTRAL"

    # Confidence: sigmoid-like normalization
    confidence = min(abs(score) / (len(tokens) + 1) * 100, 99.0)
    if label == "NEUTRAL":
        confidence = max(60.0, 100 - abs(score) * 10)

    return {
        "label": label,
        "score": round(score, 3),
        "confidence": round(confidence, 1),
        "token_count": len(tokens)
    }


# ─── Schemas ──────────────────────────────────────────────────────────────────
class AnalyzeRequest(BaseModel):
    text: str
    user_id: Optional[str] = "anonymous"

class AnalyzeResponse(BaseModel):
    text: str
    label: str
    score: float
    confidence: float
    token_count: int
    cached: bool
    timestamp: str
    processing_ms: float


# ─── Routes ───────────────────────────────────────────────────────────────────
@app.get("/")
def root():
    return {"message": "Smart Sentiment Analyzer API", "docs": "/docs"}

@app.get("/health")
def health():
    """Health check endpoint — used by Docker & CI/CD"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(req: AnalyzeRequest):
    """
    Analyze sentiment of input text.
    Uses LRU cache to avoid re-computing known texts.
    """
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    if len(req.text) > 1000:
        raise HTTPException(status_code=400, detail="Text exceeds 1000 characters")

    start = time.perf_counter()
    
    # Check cache
    cache_key = req.text.strip().lower()
    cached_result = cache.get(cache_key)
    
    if cached_result:
        result = cached_result
        cached = True
    else:
        result = analyze_sentiment(req.text)
        cache.put(cache_key, result)
        cached = False

    elapsed_ms = (time.perf_counter() - start) * 1000

    # Update analytics data structures
    label_counts[result["label"]] += 1
    confidence_scores.append(result["confidence"])

    record = {
        "text": req.text[:100],
        "label": result["label"],
        "confidence": result["confidence"],
        "timestamp": datetime.utcnow().isoformat(),
        "user_id": req.user_id,
    }
    history_buffer.append(record)  # O(1) deque append

    return AnalyzeResponse(
        text=req.text,
        label=result["label"],
        score=result["score"],
        confidence=result["confidence"],
        token_count=result["token_count"],
        cached=cached,
        timestamp=datetime.utcnow().isoformat(),
        processing_ms=round(elapsed_ms, 3)
    )

@app.post("/analyze/batch")
def analyze_batch(texts: List[str]):
    """Batch analyze up to 10 texts"""
    if len(texts) > 10:
        raise HTTPException(status_code=400, detail="Max 10 texts per batch")
    return [analyze_sentiment(t) for t in texts]

@app.get("/history")
def get_history():
    """Return recent analysis history from ring buffer"""
    return {"history": list(history_buffer), "count": len(history_buffer)}

@app.get("/analytics")
def get_analytics():
    """Aggregate statistics from in-memory data structures"""
    total = sum(label_counts.values())
    avg_conf = round(statistics.mean(confidence_scores), 1) if confidence_scores else 0
    
    return {
        "total_analyzed": total,
        "label_distribution": dict(label_counts),
        "average_confidence": avg_conf,
        "cache_size": len(cache.cache),
        "cache_capacity": cache.capacity,
    }

@app.delete("/cache")
def clear_cache():
    """Clear LRU cache"""
    cache.cache.clear()
    return {"message": "Cache cleared"}