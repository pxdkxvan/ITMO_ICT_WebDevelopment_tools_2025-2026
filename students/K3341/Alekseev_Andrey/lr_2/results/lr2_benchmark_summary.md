# LR2 Benchmark Summary

## Task 1

Target range: `1..10 000 000 000 000`

| Approach | Chunks | Verified | Time, seconds |
| --- | ---: | :---: | ---: |
| threading | 8 | yes | 0.000738 |
| multiprocessing | 8 | yes | 0.008717 |
| asyncio | 8 | yes | 0.000101 |

## Task 2

URLs parsed: `6`

| Approach | URLs | Saved tasks | Errors | Time, seconds |
| --- | ---: | ---: | ---: | ---: |
| threading | 6 | 30 | 0 | 2.801360 |
| multiprocessing | 6 | 30 | 0 | 3.038130 |
| asyncio | 6 | 30 | 0 | 1.893017 |

## Database

`transaction` rows created/updated by LR2 parsers: `90`
