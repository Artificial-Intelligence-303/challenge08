"""Provided: the experiment does what the README says, on a stand-in model.

The stand-in needs no key and costs nothing: it finds the combination only
when the fact is in the messages it is sent.
"""

import memory_lab
from memory_lab import stand_in, trial


def test_the_fact_is_planted_where_asked() -> None:
    """Start, middle and end put the fact at those places."""
    for position, index in (("start", 0), ("middle", 20), ("end", 40)):
        turns = memory_lab.conversation(20, position, seed=1)
        assert turns[index]["content"] == memory_lab.FACT


def test_full_memory_sends_every_turn() -> None:
    """Nothing is dropped, so the stand-in finds the fact."""
    assert trial(200, "start", "full", 1, stand_in)["correct"] is True


def test_a_window_drops_an_early_fact() -> None:
    """With more turns than the window, an early fact is not sent."""
    row = trial(200, "start", "window", 1, stand_in)
    assert row["correct"] is False
    assert row["tokens_sent"] < trial(200, "start", "full", 1, stand_in)[
        "tokens_sent"
    ]


def test_a_window_keeps_a_recent_fact() -> None:
    """A fact at the end is inside the window."""
    assert trial(200, "end", "window", 1, stand_in)["correct"] is True


def test_a_summary_records_whether_it_kept_the_fact() -> None:
    """The row says whether the summary held the combination."""
    row = trial(200, "middle", "summary", 1, stand_in)
    assert row["summary_kept_fact"] is False
    assert row["correct"] is False
