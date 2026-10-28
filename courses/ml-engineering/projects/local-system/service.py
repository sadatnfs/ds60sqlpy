"""Loopback workshop prediction service. State is read-only to this container."""

from __future__ import annotations

import os
import time
from collections import Counter, deque
from datetime import UTC, datetime
from functools import lru_cache
from pathlib import Path

from common import STATE, load_model, ownership, probability, read_json
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, ConfigDict, Field

os.environ.update(
    FEAST_USAGE="False",
    DO_NOT_TRACK="true",
    MLFLOW_DISABLE_AGENT_HINT="1",
    MLFLOW_ENABLE_TELEMETRY="false",
)


app = FastAPI(title="Owned local prediction workshop", docs_url=None, redoc_url=None)
counts = Counter()
latencies = deque(maxlen=200)


class PredictionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    customer_id: int = Field(ge=0, le=11, strict=True)


@lru_cache(maxsize=1)
def store():
    from feast import FeatureStore

    return FeatureStore(repo_path=str(STATE / "feature_repo"))


@app.middleware("http")
async def observations(request, call_next):
    started = time.perf_counter()
    response = await call_next(request)
    counts[str(response.status_code)] += 1
    latencies.append((time.perf_counter() - started) * 1000)
    response.headers["Content-Security-Policy"] = (
        "default-src 'none'; script-src 'unsafe-inline'; style-src "
        "'unsafe-inline'; connect-src 'self'; frame-ancestors "
        "'none'; base-uri 'none'"
    )
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response


@app.get("/health")
def health():
    try:
        owner = ownership()
        pointer, _ = load_model()
        if not (STATE / "feature_repo/online.db").is_file():
            raise ValueError("Missing feature store")
        return {
            "ready": True,
            "owner": owner,
            "version": pointer["version"],
            "mode": "synthetic-local-workshop",
        }
    except (ValueError, OSError) as error:
        raise HTTPException(503, str(error)) from None


@app.post("/predict")
def predict(request: PredictionRequest):
    try:
        pointer, model = load_model()
        retrieved = (
            store()
            .get_online_features(
                features=[
                    "customer_features:usage",
                    "customer_features:tickets",
                    "customer_features:region",
                    "customer_features:feature_epoch",
                ],
                entity_rows=[{"customer_id": request.customer_id}],
            )
            .to_dict()
        )
        feature = {
            name: retrieved[name][0] for name in ("usage", "tickets", "region", "feature_epoch")
        }
        if any(value is None for value in feature.values()):
            raise ValueError("Missing required features")
        age = datetime.now(UTC).timestamp() - feature["feature_epoch"]
        maximum = read_json(STATE / "training.json")["maximum_feature_age_seconds"]
        if not 0 <= age <= maximum:
            counts["stale_features"] += 1
            raise ValueError("Feature freshness contract failed")
        score = probability(model, feature)
        counts["predictions"] += 1
        return {
            "customer_id": request.customer_id,
            "model_version": pointer["version"],
            "probability": score,
            "feature_age_seconds": age,
            "feature_schema": model["feature_schema"],
        }
    except (ValueError, OSError, KeyError, TypeError) as error:
        counts["prediction_errors"] += 1
        raise HTTPException(503, str(error)) from None


@app.get("/metrics")
def metrics():
    ordered = sorted(latencies)
    index = max(0, int(0.95 * len(ordered) + 0.999999) - 1)
    return {
        "counts": dict(counts),
        "retained_latency_samples": len(ordered),
        "p95_ms": ordered[index] if ordered else None,
        "scope": "this service process only",
    }


@app.get("/", response_class=HTMLResponse)
def home():
    return Path(__file__).with_name("index.html").read_text("utf-8")
