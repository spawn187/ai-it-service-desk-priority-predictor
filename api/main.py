"""FastAPI service exposing the trained priority classifier."""

from __future__ import annotations

from functools import lru_cache

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from it_ticket_priority.inference import TicketPriorityPredictor
from it_ticket_priority.schemas import HealthResponse, PredictionResponse, TicketRequest

app = FastAPI(
    title="AI IT Service Desk Priority API",
    version="1.0.0",
    description=(
        "Predict P1-P4 priority for IT service desk tickets using ticket text "
        "and operational metadata."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@lru_cache(maxsize=1)
def get_predictor() -> TicketPriorityPredictor:
    return TicketPriorityPredictor()


@app.get("/", tags=["system"])
def root() -> dict[str, str]:
    return {
        "service": "AI IT Service Desk Priority API",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", response_model=HealthResponse, tags=["system"])
def health() -> HealthResponse:
    try:
        predictor = get_predictor()
        return HealthResponse(
            status="ok",
            model_loaded=True,
            model_version=predictor.model_version,
        )
    except FileNotFoundError:
        return HealthResponse(status="degraded", model_loaded=False, model_version="unknown")


@app.get("/model-info", tags=["system"])
def model_info() -> dict:
    try:
        predictor = get_predictor()
        return predictor.metadata
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.post("/predict", response_model=PredictionResponse, tags=["prediction"])
def predict(ticket: TicketRequest) -> PredictionResponse:
    try:
        result = get_predictor().predict(ticket)
        return PredictionResponse.model_validate(result)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
