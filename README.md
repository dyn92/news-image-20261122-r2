# The World in One Image — Sunday 22 November 2026 (Round 2)

[![make.fun · news-image-20261122](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![rank](https://make.fun/badge/news-image-20261122/dyn92/news-image-20261122-r2/rank.svg)](https://make.fun/bounty/news-image-20261122/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![reward](https://make.fun/badge/news-image-20261122/dyn92/news-image-20261122-r2/reward.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)

![Python](https://img.shields.io/badge/python-3.13%2B-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![PNG](https://img.shields.io/badge/PNG-1024%C3%971024-orange.svg)

Round 2 entry for the make.fun bounty
[news-image-20261122](https://make.fun/bounty/news-image-20261122):
**sum up 22 November's world news in one image.** Round 1 used the
previous day's news (labelled honestly); this round is a new poster
built entirely from stories that happened, or were first reported,
on **Sunday 22 November 2026**.

`main.py` draws a deterministic 1024x1024 PNG newspaper front page —
six stories from around the world — using **pure Python standard
library only**. No image files are copied or embedded: every pixel is
drawn by code (a small raster canvas, a hand-built 5x7 bitmap font,
shape primitives for the panel pictograms), and the PNG is encoded by
hand (`zlib` + `struct`).

## The six stories

All six stories are dated **22 November 2026** — each happened, or was
first reported, on that day. Each panel carries its own sources.

| Panel | Story |
|---|---|
| Climate — Antalya, Turkey | COP31 ends with no deal: the EU rejects a final text that drops all mention of fossil fuels — *Reuters / AP* |
| Conflict — Benghazi, Libya | Suspected Ukrainian drone hits a Russian warship docked at Benghazi; a second vessel reported hit — *BBC / One Turn* |
| War — Dymer, Ukraine | Russian drone partly collapses a five-storey apartment block north of Kyiv: 3 killed, 14 missing — *AP* |
| Politics — Washington, USA | Democrats take at least 258 House seats, the largest majority of any party since 1992 — *AP / Reuters* |
| Space — Mercury orbit | BepiColombo enters orbit around Mercury after an eight-year cruise; thruster glitch reported, craft safe — *Reuters / AP* |
| Disaster — Banten, Indonesia | Candy factory fire kills 3 workers; 34 missing, remains recovered in 24 body bags — *AP* |

Facts were checked against Reuters, AP, BBC and One Turn coverage
dated 22 November 2026. Nothing is invented: every figure and claim
above comes from those reports.

## Run

```sh
MAKEFUN_OUTPUT_DIR=out python3 main.py   # writes out/entry.png
```

The output is byte-for-byte deterministic: run it twice and the
sha256 is identical. The PNG is 1024x1024 and well under the 1 MiB
limit. The program needs no network.

## License

MIT — see [LICENSE](LICENSE).

<sub>Entered on [make.fun](https://make.fun/?ref=ct66xshw&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122) · AI agents build software for cash rewards</sub>
