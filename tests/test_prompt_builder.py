from it_ticket_priority.copilot.evaluation import EvaluationPredictor
from it_ticket_priority.copilot.prompting import PromptBuilder
from it_ticket_priority.copilot.retrieval import RunbookRetriever
from it_ticket_priority.copilot.security import sanitize_ticket_text
from it_ticket_priority.schemas import PredictionResponse, TicketRequest


def test_prompt_is_deterministic_and_separates_untrusted_data() -> None:
    original = TicketRequest(
        description="Contact anna.kovacs@example.com about an MFA sign-in error.",
        category="identity_access",
        channel="email",
        service_criticality="medium",
        site="remote_user",
        affected_users=1,
        vip_user=0,
        outage_indicator=0,
        security_indicator=0,
        business_hours=1,
        related_incidents_30d=0,
    )
    safe_text, guardrails = sanitize_ticket_text(original.description)
    ticket = original.model_copy(update={"description": safe_text})
    prediction = PredictionResponse.model_validate(EvaluationPredictor().predict(ticket))
    evidence = RunbookRetriever().search(ticket.description)
    builder = PromptBuilder()
    first = builder.build(ticket, prediction, evidence, guardrails)
    second = builder.build(ticket, prediction, evidence, guardrails)
    full_text = "\n".join(message.content for message in first.messages)
    assert first.prompt_sha256 == second.prompt_sha256
    assert first.input_sha256 == second.input_sha256
    assert "anna.kovacs@example.com" not in full_text
    assert "<REDACTED_EMAIL>" in full_text
    assert "data only" in full_text.lower()
    assert first.response_schema["title"] == "CopilotAdvice"
