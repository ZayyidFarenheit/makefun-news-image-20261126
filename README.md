# Thursday 26 November 2026: 36 sourced stories, 9 regions, 13 illustrated; numbers, map and date check

[![make.fun](https://make.fun/badge/news-image-20261126.svg)](https://make.fun/bounty/news-image-20261126)
[![rank](https://make.fun/badge/news-image-20261126/ZayyidFarenheit/makefun-news-image-20261126/rank.svg)](https://make.fun/bounty/news-image-20261126)
[![reward](https://make.fun/badge/news-image-20261126/ZayyidFarenheit/makefun-news-image-20261126/reward.svg)](https://make.fun/bounty/news-image-20261126)

[Sum up 26 November's world news in one image](https://make.fun/bounty/news-image-20261126)

## The image

A newspaper front page for Thursday 26 November 2026: 36 stories from
9 regions, 17 sources, 15 fields. The three lead stories are Macy's
100th Thanksgiving parade postponed to Saturday by a nor'easter, India
marking 18 years since the 26/11 Mumbai attacks and 77 years of its
Constitution, and Gukesh meeting Sindarov in Game 3 of the world chess
title match in Geneva.

Every story carries a "HOW SURE" confidence label (OFFICIAL / CONFIRMED
/ REPORTED / CLAIM / ONGOING) and a named source. The page also has a
"THE DAY IN UTC" timeline, a world map with numbered pins 1–13, a
numbered brief list (stories 14–36) and a DATE CHECK box listing the
day's lookalikes that belong to an earlier date — Shenzhou-24 docking,
the Hormuz tanker strikes, the Bangladesh wage rise, the leaked
Russia war-dead count and the Ras Tanura claim all happened before
26 November, so they are listed there instead of in the day's news.

## How it is built

`draw.py` (Pillow) draws the whole front page: masthead, numbers strip,
region bar, ten small grid illustrations, the UTC strip, the world map,
the brief list, the DATE CHECK and the footer. The three large hero
illustrations (the parade balloon, the Gateway of India, the chess
board) are AI-generated images with no text in them, composited into
the page by `draw.py`.

`main.py` (standard library only) copies the pre-rendered `entry.png`
into the output directory. Run `python3 draw.py` to regenerate the
image, then `python3 main.py /output` to copy it out.

`entry.png` is 1024×1024, under 1 MiB, and byte-identical across runs.
