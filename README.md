# Challenge 8: What an Agent Remembers

|                     |                                       |
| :------------------ | :------------------------------------ |
| `Thursday 12 Nov`   | Released, started in class            |
| `Thursday 19 Nov`   | Due 11:00am                           |
| Points              | 3                                     |

A model knows only what is in the messages it is sent. This challenge is an
experiment on that fact. A conversation opens with a detail the model could
not know any other way, your locker combination. The program buries it under
filler turns, applies a memory strategy, and then asks for the combination.
You predict what will happen, run it, and explain what you see.

You write no code. The experiment is provided, and you run it with your
OpenCode Zen key from Challenge 7.

## The experiment

`src/run.py` runs trials and adds a row per trial to `results/results.csv`.
It takes four settings:

- `--memory`: `full` sends every turn; `window` sends only the last 20
  turns; `summary` first asks the model to summarize everything before the
  last 20 turns in at most 60 words, then sends that summary with the last
  20 turns.
- `--filler`: how many filler turns, from 0 to 2000. About one turn in
  seven is a combination for something else, such as a bike lock.
- `--position`: where the fact sits: `start` (the default), `middle` or
  `end`.
- `--trials`: how many trials, from 1 to 5, each with different filler
  (default 3).

Each row records the settings, the number of tokens sent (estimated as one
per four characters), whether the summary kept the combination, whether the
answer was right, and the answer itself.

## What to do

### In class, Thursday 12 November

1. Make a file named `.env` at the top of this repository holding one line,
   `ZEN_API_KEY=` followed by your key. It is in `.gitignore`, so it is never
   committed. Never commit a key.
2. Fill in `docs/prediction.md` and **commit it before you run anything.**
   The checks confirm that your prediction was committed before your results.
3. Run the three settings with full memory, then commit `results/results.csv`:

   ```bash
   uv run python src/run.py --memory full --filler 0
   uv run python src/run.py --memory full --filler 100
   uv run python src/run.py --memory full --filler 2000
   ```

### By Thursday 19 November

4. Run the other four required settings:

   ```bash
   uv run python src/run.py --memory full --filler 2000 --position middle
   uv run python src/run.py --memory window --filler 100
   uv run python src/run.py --memory summary --filler 100
   uv run python src/run.py --memory summary --filler 2000
   ```

5. Run **one setting of your own**, three trials, chosen to test something
   your results so far left open.
6. Commit the results, then answer the questions in `docs/explanation.md`
   from your own numbers.

All the required runs together send about 400,000 tokens, which costs about
six cents of your monthly limit. Run a setting again only if a run fails
partway.

## Automated checks

Run `uv run gatorgrade --config gatorgrade.yml`. The checks confirm that the
provided experiment works, that your results hold three trials of every
required setting and one of your own, that every row came from the model,
that `src/` is unchanged, and that your prediction was committed before your
results.

## Evaluation

This challenge is worth **3 points**, split evenly. There is no verbal check.

| Component | Value | Graded by |
| :-------- | ----: | :-------- |
| The runs | 1 | the `[RUN]` checks, as the fraction passed |
| The prediction | 1 | committed before the results, with a reason for each setting; it is graded on its reasoning, not on whether it turned out right |
| The explanation | 1 | the instructor, on whether each answer is supported by your own numbers |

## How this assignment was built

I chose the experiment and its settings. Claude wrote the runner, the tests
and the checks, and verified them against a stand-in model that needs no
key. I reviewed the result and ran the experiment on the real model before
release.

## AI use on this challenge

Full policy: **[AI in this course](https://areweagentsyet.com/ai/)**. The
runs are the assignment. The prediction and the explanation are your own
reasoning about your own numbers; disclose any AI use in
`docs/explanation.md`.
