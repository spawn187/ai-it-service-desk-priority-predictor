"""FastAPI service exposing the trained classifier and guarded copilot workflow."""

from __future__ import annotations

from functools import lru_cache

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from it_ticket_priority.copilot import CopilotDecision, ServiceDeskCopilot
from it_ticket_priority.inference import TicketPriorityPredictor
from it_ticket_priority.schemas import HealthResponse, PredictionResponse, TicketRequest

app = FastAPI(
    title="AI IT Service Desk Copilot API",
    version="2.0.0",
    description=(
        "Predict P1-P4 priority and produce guarded, retrieval-grounded, "
        "human-approved service-desk triage guidance."
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


@lru_cache(maxsize=1)
def get_copilot() -> ServiceDeskCopilot:
    return ServiceDeskCopilot(get_predictor())


@app.get("/", tags=["system"])
def root() -> dict[str, str]:
    return {
        "service": "AI IT Service Desk Copilot API",
        "docs": "/docs",
        "health": "/health",
        "prediction": "/predict",
        "copilot": "/copilot/triage",
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


@app.post("/copilot/triage", response_model=CopilotDecision, tags=["copilot"])
def copilot_triage(ticket: TicketRequest) -> CopilotDecision:
    """Run redaction, injection checks, ML scoring, retrieval, and safe advice."""

    try:
        return get_copilot().triage(ticket)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
