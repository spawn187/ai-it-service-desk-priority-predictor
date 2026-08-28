from it_ticket_priority.config import PROJECT_ROOT
from it_ticket_priority.copilot.evaluation import PromptEvaluationRunner


def test_reference_prompt_contract_suite_passes() -> None:
    runner = PromptEvaluationRunner()
    cases = runner.load_cases(PROJECT_ROOT / "evals" / "prompt_eval_cases.jsonl")
    summary = runner.run(cases)
    assert summary.total_cases == 10
    assert summary.failed_cases == 0
    assert summary.pass_rate == 1.0
