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
| P4 foundation-beats | `d995343` `adff218` `2eceaae` `f8722e4` `0e9eb32` | — |
| scout-audit gate | `ec612f5` `dbf9528` `f7b89eb` | — |
| teach rewrite | `de19850` `52ff04b` | — |
| bridge Phase 1 + deploy Phase 3 + contract v6 (55 invariants) | `bf9d5ab` `494e021` `8afccda` `a36d9c4` `edc9bc1` `e2ad5fb` `c7dbf69` `95d99cc` `e89df2b` `8ad83ab` `1b9854f` `bcb5a46` `22ab8d4` | — |
