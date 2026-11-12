# Challenge 8: What an Agent Remembers

|                     |                                       |
| :------------------ | :------------------------------------ |
| `Thursday 12 Nov`   | Released, required runs done in class |
| `Thursday 19 Nov`   | Due 11:00am                           |
| Points              | 3                                     |

A model knows only what is in the messages it is sent. This challenge is an
experiment on that fact. A conversation opens with a detail the model could
not know any other way, your locker combination. The program buries that
detail under ordinary conversation, decides how much of the conversation to
send, and then asks the model for the combination. You predict what will
happen, run the experiment, and explain what you see.

The experiment is provided in `src/`, and your work is the prediction, the
runs and the explanation. The program talks to the model with your OpenCode
Zen key from Challenge 7.

## The experiment

`src/run.py` runs one setting of the experiment a few times and adds a row
for each trial to `results/results.csv`. A setting is made of four choices,
given on the command line.

`--memory` is how the program decides what to send the model before it
asks the question. It has three values:

- `full` sends the conversation from its first turn to its last.
- `window` sends only the last 20 turns, so anything said earlier is left
  out.
- `summary` first asks the model to summarize the turns before the last 20
  in at most 60 words. It then sends that summary followed by the last 20
  turns.

`--filler` is how many turns of ordinary conversation surround the
combination, from 0 to 2000. A turn is a short question from the user and a
short reply, such as how to fix a squeaky door. About one turn in seven
gives a combination for something else, such as a bike lock, so the locker
combination has look-alikes around it.

`--position` is where the combination sits among the filler turns:
`start` (the default), `middle` or `end`.

`--trials` is how many times to run the setting, from 1 to 5, with 3 as
the default. Each trial uses different filler, so three trials tell you
whether a result holds up or happened once by chance. The filler is chosen
at random from a starting number called a seed: trial 1 uses seed 1, trial
2 uses seed 2, and so on. The same seed produces the same filler on any
laptop, so your classmates send the same conversations you do, and a
difference between your results comes from the model itself.

Each row of `results/results.csv` records the setting, the number of tokens
sent (estimated as one per four characters), the summary and whether it
kept the combination, whether the answer was right, and the answer itself.
The model thinks before it writes, and if it uses up its room thinking, the
summary or the answer says so. The program also prints a line for each trial
as it finishes.

### The flow of one run

A run of one setting makes three trials, one for each seed.

```text
run.py main
 └─ for seed in 1, 2, 3:
     └─ trial
         ├─ conversation ── filler      fact + count turns, built from TASKS, TIPS, THINGS
         ├─ remembered                  full: all turns   window: last 20
         │   └─ summarize ── zen        summary only: a first call, 60 words
         ├─ + QUESTION
         ├─ zen                         the call that is graded
         └─ ANSWER                      right or wrong → one row in results.csv
```

## What to do

### In class, Thursday 12 November

1. Make a file named `.env` at the top of this repository holding one line,
   `ZEN_API_KEY=` followed by your key. The file is listed in `.gitignore`,
   so git leaves it out of your commits and your key stays on your laptop.
2. Fill in `docs/prediction.md` and **commit it before you run anything.**
   The checks confirm that your prediction was committed before your
   results.
3. Run the three settings with full memory:

   ```bash
   uv run python src/run.py --memory full --filler 0
   uv run python src/run.py --memory full --filler 100
   uv run python src/run.py --memory full --filler 2000
   ```

4. Run the other four required settings, then commit `results/results.csv`:

   ```bash
   uv run python src/run.py --memory full --filler 2000 --position middle
   uv run python src/run.py --memory window --filler 100
   uv run python src/run.py --memory summary --filler 100
   uv run python src/run.py --memory summary --filler 2000
   ```

### By Thursday 19 November

5. Run **one setting of your own**, three trials, chosen to test something
   your results so far left open.
6. Commit the results, then answer the questions in `docs/explanation.md`
   using your own numbers.

The seven required settings together send about 400,000 tokens, which costs
about six cents of your monthly limit. Run a setting again only if a run
fails partway.

## Automated checks

Run `uv run gatorgrade --config gatorgrade.yml`. The checks confirm that the
provided experiment works, that your results hold three trials of each
required setting and one of your own, that each row came from the model,
that `src/` is unchanged, and that your prediction was committed before your
results.

## Evaluation

This challenge is worth **3 points**, split evenly. There is no verbal check.

| Component | Value | Graded by |
| :-------- | ----: | :-------- |
| The runs | 1 | the `[RUN]` checks, as the fraction passed |
| The prediction | 1 | committed before the results, with a reason for each setting; it is graded on its reasoning, so a prediction that turns out wrong earns full credit when its reasons are sound |
| The explanation | 1 | the instructor, on whether each answer is supported by your own numbers |

## How this assignment was built

I chose the experiment and its settings. Claude wrote the runner, the tests
and the checks, and tested them against a stand-in model that needs no key.
I ran the experiment on the real model before release, and Claude fixed the
problems that run turned up.

## AI use on this challenge

Full policy: **[AI in this course](https://areweagentsyet.com/ai/)**. This
challenge runs an AI model, and that use needs no disclosure. The prediction
and the explanation are your own reasoning about your own numbers, so if you
use an AI tool for either one, please disclose it at the end of
`docs/explanation.md`.

> ### The skill this time: if an answer depends on something said long ago, check that the tool still has it
>
> A model answers from the messages it is sent. When an earlier part of a
> conversation has been cut or summarized, the model can still answer
> confidently from what is left.
