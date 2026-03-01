"""
Unit + Integration Tests
Run: pytest tests/ -v
"""
import pytest
from fastapi.testclient import TestClient
from main import app, cache, LRUCache, analyze_sentiment

client = TestClient(app)


# ─── Unit Tests: Data Structures ────────────────────────────────────────────
class TestLRUCache:
    def test_basic_get_put(self):
        c = LRUCache(3)
        c.put("a", 1)
        assert c.get("a") == 1

    def test_eviction(self):
        c = LRUCache(2)
        c.put("a", 1)
        c.put("b", 2)
        c.put("c", 3)  # evicts "a"
        assert c.get("a") is None
        assert c.get("b") == 2

    def test_lru_ordering(self):
        c = LRUCache(2)
        c.put("a", 1)
        c.put("b", 2)
        c.get("a")    # access "a" -> "b" is now LRU
        c.put("c", 3) # should evict "b"
        assert c.get("b") is None
        assert c.get("a") == 1


# ─── Unit Tests: ML Model ────────────────────────────────────────────────────
class TestSentimentModel:
    def test_positive(self):
        result = analyze_sentiment("This is great and amazing!")
        assert result["label"] == "POSITIVE"

    def test_negative(self):
        result = analyze_sentiment("This is terrible and awful")
        assert result["label"] == "NEGATIVE"

    def test_neutral(self):
        result = analyze_sentiment("This is a sentence")
        assert result["label"] == "NEUTRAL"

    def test_negation(self):
        result = analyze_sentiment("This is not great")
        assert result["label"] in ["NEUTRAL", "NEGATIVE"]  # negation flips

    def test_confidence_range(self):
        result = analyze_sentiment("good product")
        assert 0 <= result["confidence"] <= 100


# ─── Integration Tests: API ──────────────────────────────────────────────────
class TestAPI:
    def test_health(self):
        r = client.get("/health")
        assert r.status_code == 200
        assert r.json()["status"] == "healthy"

    def test_analyze_positive(self):
        r = client.post("/analyze", json={"text": "I love this amazing product!"})
        assert r.status_code == 200
        data = r.json()
        assert data["label"] == "POSITIVE"
        assert "confidence" in data
        assert "processing_ms" in data

    def test_analyze_empty_text(self):
        r = client.post("/analyze", json={"text": "   "})
        assert r.status_code == 400

    def test_analyze_too_long(self):
        r = client.post("/analyze", json={"text": "x" * 1001})
        assert r.status_code == 400

    def test_caching(self):
        text = "unique test phrase for caching"
        r1 = client.post("/analyze", json={"text": text})
        r2 = client.post("/analyze", json={"text": text})
        assert r1.json()["cached"] == False
        assert r2.json()["cached"] == True

    def test_batch(self):
        r = client.post("/analyze/batch", json=["good", "bad", "neutral text"])
        assert r.status_code == 200
        assert len(r.json()) == 3

    def test_history(self):
        r = client.get("/history")
        assert r.status_code == 200
        assert "history" in r.json()

    def test_analytics(self):
        r = client.get("/analytics")
        assert r.status_code == 200
        assert "total_analyzed" in r.json()