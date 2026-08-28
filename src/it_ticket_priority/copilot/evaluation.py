"""Deterministic prompt/RAG contract evaluation suitable for CI quality gates."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from it_ticket_priority.schemas import TicketRequest

from .models import PromptEvalCheck, PromptEvalResult, PromptEvalSummary
from .orchestrator import ServiceDeskCopilot


class PromptEvalCase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    case_id: str
    ticket: TicketRequest
    expected_runbook_ids: list[str] = Field(default_factory=list)
    expect_injection: bool = False
    expect_redaction: bool = False
    expect_human_review: bool = False
    min_citations: int = Field(default=1, ge=0)


class EvaluationPredictor:
    """Stable policy-shaped predictor used only to isolate prompt/RAG tests."""

    model_version = "eval-policy-1.0"

    def predict(self, ticket: TicketRequest | dict[str, Any]) -> dict[str, Any]:
        request = (
            ticket
            if isinstance(ticket, TicketRequest)
            else TicketRequest.model_validate(ticket)
        )
        if request.security_indicator or (
            request.outage_indicator
            and request.service_criticality == "mission_critical"
            and request.affected_users >= 50
        ):
            priority, confidence = "P1", 0.92
        elif request.outage_indicator or request.affected_users >= 25 or request.vip_user:
            priority, confidence = "P2", 0.82
        elif request.affected_users <= 1:
            priority, confidence = "P3", 0.78
        else:
            priority, confidence = "P4", 0.76
        probabilities = {"P1": 0.02, "P2": 0.06, "P3": 0.12, "P4": 0.80}
        probabilities[priority] = confidence
        remainder = round((1.0 - confidence) / 3, 6)
        probabilities = {
            key: (confidence if key == priority else remainder)
            for key in probabilities
        }
        return {
            "predicted_priority": priority,
            "confidence": confidence,
            "probabilities": probabilities,
            "requires_human_review": priority == "P1" or confidence < 0.65,
            "top_contributors": [],
            "model_version": self.model_version,
        }


class PromptEvaluationRunner:
    SUITE_VERSION = "1.0.0"

    def __init__(self, copilot: ServiceDeskCopilot | None = None) -> None:
        self.copilot = copilot or ServiceDeskCopilot(EvaluationPredictor())

    @staticmethod
    def load_cases(path: str | Path) -> list[PromptEvalCase]:
        cases: list[PromptEvalCase] = []
        for line in Path(path).read_text(encoding="utf-8").splitlines():
            if line.strip():
                cases.append(PromptEvalCase.model_validate_json(line))
        return cases

    def run(self, cases: list[PromptEvalCase]) -> PromptEvalSummary:
        results = [self._run_case(case) for case in cases]
        passed = sum(result.passed for result in results)
        total = len(results)
        return PromptEvalSummary(
            suite_version=self.SUITE_VERSION,
            total_cases=total,
            passed_cases=passed,
            failed_cases=total - passed,
            pass_rate=round(passed / total, 4) if total else 0.0,
            results=results,
            interpretation=(
                "This suite validates deterministic engineering invariants—redaction, injection "
                "handling, evidence retrieval, citation discipline, schema validation, and human "
                "approval gates. It is not a claim of production LLM quality."
            ),
        )

    def _run_case(self, case: PromptEvalCase) -> PromptEvalResult:
        decision = self.copilot.triage(case.ticket)
        retrieved_ids = {item.document_id for item in decision.evidence}
        prompt_text = "\n".join(message.content for message in decision.prompt_package.messages)
        checks = [
            self._check(
                "injection_detection",
                decision.guardrails.injection_detected == case.expect_injection,
                (
                    f"expected={case.expect_injection}, "
                    f"actual={decision.guardrails.injection_detected}"
                ),
            ),
            self._check(
                "sensitive_data_redaction",
                (decision.guardrails.redaction_count > 0) == case.expect_redaction,
                f"expected={case.expect_redaction}, count={decision.guardrails.redaction_count}",
            ),
            self._check(
                "runbook_retrieval",
                set(case.expected_runbook_ids).issubset(retrieved_ids),
                f"expected_subset={case.expected_runbook_ids}, actual={sorted(retrieved_ids)}",
            ),
            self._check(
                "citation_count",
                len(decision.advice.citations) >= case.min_citations,
                f"minimum={case.min_citations}, actual={len(decision.advice.citations)}",
            ),
            self._check(
                "human_review_policy",
                decision.advice.human_review_required == case.expect_human_review,
                (
                    f"expected={case.expect_human_review}, "
                    f"actual={decision.advice.human_review_required}"
                ),
            ),
            self._check(
                "no_autonomous_execution",
                (
                    not decision.advice.automation_allowed
                    and not decision.guardrails.automation_allowed
                ),
                "automation must remain disabled in both policy layers",
            ),
            self._check(
                "instruction_data_separation",
                (
                    "data only" in prompt_text.lower()
                    and "do not follow instructions" in prompt_text.lower()
                ),
                "prompt must explicitly treat ticket and context as untrusted data",
            ),
            self._check(
                "structured_output_contract",
                decision.advice.prompt_version == decision.prompt_package.prompt_version,
                "validated output must retain the prompt version",
            ),
        ]
        original = case.ticket.description
        if "@" in original:
            checks.append(
                self._check(
                    "raw_email_absent_from_prompt",
                    original not in prompt_text and "<REDACTED_EMAIL>" in prompt_text,
                    "raw ticket containing email must not be copied into the prompt",
                )
            )
        return PromptEvalResult(
            case_id=case.case_id,
            passed=all(check.passed for check in checks),
            checks=checks,
        )

    @staticmethod
    def _check(name: str, passed: bool, detail: str) -> PromptEvalCheck:
        return PromptEvalCheck(name=name, passed=passed, detail=detail)

    @staticmethod
    def write_summary(summary: PromptEvalSummary, path: str | Path) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(
            json.dumps(summary.model_dump(), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
