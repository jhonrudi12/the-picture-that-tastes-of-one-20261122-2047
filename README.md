[![make.fun · the-picture-that-tastes-of-one-20261122-2047](https://make.fun/badge/the-picture-that-tastes-of-one-20261122-2047.svg)](https://make.fun/bounty/the-picture-that-tastes-of-one-20261122-2047)
[![rank](https://make.fun/badge/the-picture-that-tastes-of-one-20261122-2047/jhonrudi12/the-picture-that-tastes-of-one-20261122-2047/rank.svg)](https://make.fun/bounty/the-picture-that-tastes-of-one-20261122-2047/leaderboard)
[![reward](https://make.fun/badge/the-picture-that-tastes-of-one-20261122-2047/jhonrudi12/the-picture-that-tastes-of-one-20261122-2047/reward.svg)](https://make.fun/bounty/the-picture-that-tastes-of-one-20261122-2047)

# The Picture That Tastes of One Ingredient

One single large ripe strawberry, big in frame, on a warm cream background.

## What the program does

`main.py` draws the picture from scratch in pure Python — no image files, no
network, no third-party libraries. It renders:

- a warm cream radial-gradient background with a soft vignette,
- one big glossy strawberry: bright red lit shoulder grading to deep red in
  shade, pale-yellow achenes (seeds) in shallow dimples along diagonal rows,
  fine skin speckle, soft specular highlights and a few clear water droplets,
- a fan of six green calyx leaves with lighter centre veins and a short stem,
- a soft elliptical drop shadow beneath the berry.

The output is a single deterministic 1024×1024 PNG. The PNG encoder is
hand-written with `zlib` + `struct` (RGB, 8-bit, filter 0 per scanline), so
the program runs anywhere Python 3.13 runs with only the standard library.

## How to run it

```sh
python3 main.py
```

It writes the image to `/output/entry.png` (creating the directory if
needed). For local testing you can redirect the output with:

```sh
ENTRY_OUTPUT=/tmp/entry.png python3 main.py
```

Runs in a few seconds, well inside the 60-second sandbox budget, and produces
byte-identical output on every run.
