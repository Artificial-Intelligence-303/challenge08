"""The experiment: plant a fact, bury it in conversation, then ask for it.

Provided. You run this through `src/run.py`; you do not edit it.

One trial builds a conversation that opens with a planted fact (or holds it
in the middle or at the end), pads it with filler turns, applies a memory
strategy, and asks the model for the fact. The answer is right if it holds
the fact's combination.

Memory strategies:
    full     all turns are sent
    window   only the last WINDOW turns are sent
    summary  turns before the last WINDOW are replaced by a summary that
             the model writes first, in at most SUMMARY_WORDS words
"""

import json
import os
import random
import re
import urllib.error
import urllib.request
from collections.abc import Callable
from pathlib import Path

URL = "https://opencode.ai/inference/openai/v1/chat/completions"
MODEL = "glm-5.3-flash"
TEMPERATURE = 0.2
WINDOW = 20
SUMMARY_WORDS = 60
ENV_FILE = Path(__file__).parent.parent / ".env"

FACT = "Note for later: my locker combination is 31-7-22."
ANSWER = re.compile(r"31\D{1,3}0?7\D{1,3}22")
QUESTION = (
    "What is my locker combination? Answer with the combination only, "
    "or say that you do not know."
)

Message = dict[str, str]
Model = Callable[[list[Message]], str]

TASKS = [
    "keep a plant alive in a dorm room",
    "study for a statistics exam",
    "write a cover letter",
    "fall asleep earlier",
    "cook rice without a rice cooker",
    "remember people's names",
    "pack for a weekend trip",
    "take notes in a lecture",
    "fix a squeaky door",
    "save money on groceries",
]
TIPS = [
    "Do a little each day rather than a lot at once.",
    "Write down the steps first, then do them in order.",
    "Ask someone who has done it before.",
    "Start with the smallest version that works.",
    "Set a reminder so you do not have to remember it.",
    "Check the result before you move on.",
]
THINGS = ["bike lock", "gym locker", "luggage lock", "storage unit", "shed"]


def filler(count: int, seed: int) -> list[Message]:
    """Return `count` filler turns, a user line and a reply each.

    One turn in seven is a different combination for something else, so
    the planted fact has look-alikes around it.
    """
    rng = random.Random(seed)
    turns: list[Message] = []
    for number in range(count):
        if number % 7 == 6:
            code = "-".join(str(rng.randint(1, 39)) for _ in range(3))
            thing = rng.choice(THINGS)
            turns.append({"role": "user", "content": f"The {thing} is {code}."})
            turns.append({"role": "assistant", "content": "Got it."})
        else:
            task = rng.choice(TASKS)
            turns.append(
                {
                    "role": "user",
                    "content": f"Quick question: how do I {task}?",
                }
            )
            turns.append({"role": "assistant", "content": rng.choice(TIPS)})
    return turns


def conversation(count: int, position: str, seed: int) -> list[Message]:
    """Return the turns with the fact at the start, middle or end."""
    turns = filler(count, seed)
    fact = [
        {"role": "user", "content": FACT},
        {"role": "assistant", "content": "Noted."},
    ]
    where = {"start": 0, "middle": (count // 2) * 2, "end": count * 2}
    if position not in where:
        raise ValueError(f"position must be start, middle or end: {position}")
    at = where[position]
    return turns[:at] + fact + turns[at:]


def summarize(turns: list[Message], model: Model) -> str:
    """Ask the model for a summary of some turns."""
    text = "\n".join(f"{t['role']}: {t['content']}" for t in turns)
    request = [
        {
            "role": "user",
            "content": (
                f"Summarize this conversation in at most {SUMMARY_WORDS} "
                f"words, keeping what the user may need later.\n\n{text}"
            ),
        }
    ]
    return model(request)


def remembered(
    turns: list[Message], memory: str, model: Model
) -> tuple[list[Message], str]:
    """Apply a memory strategy; return the messages and any summary."""
    if memory == "full" or len(turns) <= WINDOW * 2:
        return turns, ""
    recent = turns[-WINDOW * 2 :]
    if memory == "window":
        return recent, ""
    if memory == "summary":
        summary = summarize(turns[: -WINDOW * 2], model)
        note = {
            "role": "system",
            "content": f"Summary of the earlier conversation: {summary}",
        }
        return [note, *recent], summary
    raise ValueError(f"memory must be full, window or summary: {memory}")


def tokens(messages: list[Message]) -> int:
    """Estimate tokens as one per four characters."""
    return sum(len(m["content"]) for m in messages) // 4


def trial(
    count: int, position: str, memory: str, seed: int, model: Model
) -> dict[str, object]:
    """Run one trial and return its row for the results file."""
    turns = conversation(count, position, seed)
    sent, summary = remembered(turns, memory, model)
    messages = [*sent, {"role": "user", "content": QUESTION}]
    answer = model(messages)
    return {
        "memory": memory,
        "filler": count,
        "position": position,
        "seed": seed,
        "tokens_sent": tokens(messages),
        "summary_kept_fact": bool(ANSWER.search(summary)) if summary else "",
        "correct": bool(ANSWER.search(answer)),
        "answer": " ".join(answer.split())[:80],
    }


def api_key() -> str:
    """Read the key from ZEN_API_KEY or from a line in `.env`."""
    key = os.environ.get("ZEN_API_KEY", "")
    if not key and ENV_FILE.exists():
        for line in ENV_FILE.read_text().splitlines():
            if line.startswith("ZEN_API_KEY="):
                key = line.split("=", 1)[1].strip().strip('"')
    if not key:
        raise SystemExit(
            "No key found. Put ZEN_API_KEY=your-key in a file named .env "
            "at the top of this repository."
        )
    return key


def zen(messages: list[Message]) -> str:
    """Send messages to the model on OpenCode Zen and return its reply.

    The model thinks before it replies, and its thinking counts against
    max_tokens. If it uses them all before replying, the reply says so.
    """
    body = json.dumps(
        {
            "model": MODEL,
            "messages": messages,
            "temperature": TEMPERATURE,
            "max_tokens": 8000,
        }
    ).encode()
    request = urllib.request.Request(
        URL,
        data=body,
        headers={
            "Authorization": f"Bearer {api_key()}",
            "Content-Type": "application/json",
            "User-Agent": "cmpsc303-challenge8",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            reply = json.load(response)
    except urllib.error.HTTPError as problem:
        detail = problem.read().decode(errors="replace")[:300]
        raise SystemExit(f"Zen returned {problem.code}: {detail}") from None
    choice = reply["choices"][0]
    content = choice["message"].get("content") or ""
    if not content.strip() and choice.get("finish_reason") == "length":
        return "No answer: the model used all of its tokens thinking."
    return content


def stand_in(messages: list[Message]) -> str:
    """A stand-in for the model, for the tests: no network, no cost.

    It finds the combination only if the fact is in the messages it is sent,
    and its summaries keep only the first line of what they summarize.
    """
    last = messages[-1]["content"]
    if last.startswith("Summarize"):
        return last.split("\n\n", 1)[1].split("\n", 1)[0]
    seen = " ".join(m["content"] for m in messages)
    return "31-7-22" if ANSWER.search(seen) else "I do not know."
