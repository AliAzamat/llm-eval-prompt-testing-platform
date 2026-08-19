"""evalctl — the one-command eval CLI. `evalctl eval` registers a prompt version,
imports the dataset, runs it, diffs against a baseline run, prints the verdict,
and EXITS NON-ZERO on a regression so CI fails a bad prompt change automatically."""
from __future__ import annotations

import argparse
import sys

from evalctl.client import EvalClient


def cmd_eval(args: argparse.Namespace) -> int:
    client = EvalClient(args.base_url)

    template = open(args.prompt_file, "r", encoding="utf-8").read()
    version = client.register_version(args.name, args.task, template, args.model, args.notes)
    print(f"registered {args.name} v{version['version']} ({version['id']})")

    client.import_dataset(args.dataset_name, args.task, args.dataset_file)
    run = client.run(version["id"], args.dataset_name, args.judge_model)
    print(f"ran {run['n_items']} items -> run {run['run_id']}")

    if not args.baseline_run:
        print("no baseline given; skipping regression gate")
        return 0

    d = client.diff(args.baseline_run, run["run_id"])
    print(f"overall delta {d['overall_delta']:+.4f} -> {d['verdict'].upper()}")
    for m in d["worst_items"]:
        print(f"  {m['item_key']}: {m['delta']:+.4f}")
    # The exit code IS the CI gate: non-zero fails the pipeline on a regression.
    return 1 if d["verdict"] == "regressed" else 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="evalctl")
    sub = p.add_subparsers(dest="cmd", required=True)

    e = sub.add_parser("eval", help="register, run, and regression-gate a prompt version")
    e.add_argument("--name", required=True)
    e.add_argument("--task", required=True)
    e.add_argument("--prompt-file", required=True)
    e.add_argument("--model", default="gpt-4o-mini")
    e.add_argument("--dataset-name", required=True)
    e.add_argument("--dataset-file", required=True)
    e.add_argument("--judge-model", default="gpt-4o")
    e.add_argument("--baseline-run", default=None)
    e.add_argument("--notes", default=None)
    e.add_argument("--base-url", default="http://localhost:8000")
    e.set_defaults(func=cmd_eval)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
