# Stage log — commit boundaries

Each cascade stage appends its commit shas here so the review phase can scope its per-checkpoint
review to the right changes.

| Stage | learning-pi shas | learning-system shas |
| --- | --- | --- |
| P0 | `d00acf3` `5d7af31` `e42a817` `d40f9de` `baad482` `5ce4573` | `0882821` `64893fe` |
| P0 baseline (before cascade) | `e344abc` | `64893fe` |
| P1 | `957d735` `e297dd6` `68a70ad` `c1eac94` | `829f5b9` `308cd48` `2ed8d8e` |
| P2 | `96dde7e` `125a672` `45d5434` | `8bd7f73` `dffb06e` |
| P3 | _deferred (user, 2026-10-08)_ | _deferred_ |
| REVIEW | `acf0b9f` (+ review docs commit) | `9a06820` |
