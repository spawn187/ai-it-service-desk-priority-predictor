"""Run deterministic prompt/RAG contract tests and optionally fail CI."""

from __future__ import annotations

import argparse
from pathlib import Path

from it_ticket_priority.config import PROJECT_ROOT
from it_ticket_priority.copilot.evaluation import PromptEvaluationRunner


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--cases",
        type=Path,
        default=PROJECT_ROOT / "evals" / "prompt_eval_cases.jsonl",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / "artifacts" / "prompt_eval_metrics.json",
    )
    parser.add_argument("--fail-on-regression", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    runner = PromptEvaluationRunner()
    cases = runner.load_cases(args.cases)
    summary = runner.run(cases)
    runner.write_summary(summary, args.output)
    print(
        f"Prompt contract evaluation: {summary.passed_cases}/{summary.total_cases} "
        f"passed ({summary.pass_rate:.1%})."
    )
    for result in summary.results:
        print(f"{'PASS' if result.passed else 'FAIL'}  {result.case_id}")
        if not result.passed:
            for check in result.checks:
                if not check.passed:
                    print(f"  - {check.name}: {check.detail}")
    if args.fail_on_regression and summary.failed_cases:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
