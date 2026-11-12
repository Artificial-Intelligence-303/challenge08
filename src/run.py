"""Run trials of the experiment and add their rows to results/results.csv.

Provided. Examples:
    uv run python src/run.py --memory full --filler 100
    uv run python src/run.py --memory summary --filler 2000 --trials 3
    uv run python src/run.py --memory full --filler 2000 --position middle

Each trial uses a different seed, so the filler differs between trials.
"""

import argparse
import csv
import datetime
from pathlib import Path

import memory_lab

RESULTS = Path(__file__).parent.parent / "results" / "results.csv"
FIELDS = [
    "time",
    "model",
    "temperature",
    "memory",
    "filler",
    "position",
    "seed",
    "tokens_sent",
    "summary_kept_fact",
    "summary",
    "correct",
    "answer",
]


def main() -> None:
    """Read the settings, run the trials, print and save each row."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--memory", choices=["full", "window", "summary"], required=True
    )
    parser.add_argument("--filler", type=int, required=True)
    parser.add_argument(
        "--position", choices=["start", "middle", "end"], default="start"
    )
    parser.add_argument("--trials", type=int, default=3)
    settings = parser.parse_args()
    if not 0 <= settings.filler <= 2000:
        parser.error("--filler must be from 0 to 2000")
    if not 1 <= settings.trials <= 5:
        parser.error("--trials must be from 1 to 5")

    RESULTS.parent.mkdir(exist_ok=True)
    new_file = not RESULTS.exists()
    with RESULTS.open("a", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        if new_file:
            writer.writeheader()
        for seed in range(1, settings.trials + 1):
            row = memory_lab.trial(
                settings.filler,
                settings.position,
                settings.memory,
                seed,
                memory_lab.zen,
            )
            row["time"] = datetime.datetime.now().isoformat(timespec="seconds")
            row["model"] = memory_lab.MODEL
            row["temperature"] = memory_lab.TEMPERATURE
            writer.writerow(row)
            handle.flush()
            verdict = "right" if row["correct"] else "wrong"
            print(
                f"trial {seed}: {verdict}, about {row['tokens_sent']} "
                f"tokens sent, answer: {row['answer']}"
            )


if __name__ == "__main__":
    main()
