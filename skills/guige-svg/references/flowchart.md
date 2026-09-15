# Flowcharts

## Shapes

| Meaning | Element | Class |
|---|---|---|
| start / end | `<rect rx="22" width="140" height="44">` | `.highlight` |
| process | standard node 160 × 60, `rx=6` | `.secondary` or `.primary` |
| decision | diamond 100 × 70 | `.infra` |
| input / output | parallelogram `points="12,0 160,0 148,60 0,60"` | `.neutral` |
| data store | cylinder | `.data` |
| error / abort | 140 × 44 `rx=22` | `.alert` |

## Layout algorithm

1. Identify the happy path. It runs straight down one center column at `x=600` (node centers).
2. Vertical pitch: 100 px between node centers for process → process, 110 px when a decision is involved.
3. Decision exits: main outcome continues down, the other exits right (or left if the right is occupied) to a branch column 260 px away.
4. Branches rejoin the main column with an L-shaped path into the top edge of the merge node.
5. Loop-backs run up the far side of the diagram at `x = column ± 320`, never through nodes.
6. More than 10 steps: split into swim lanes (region boundary per phase, header label at top) or into two diagrams.

## Coordinates for a typical path

```
y=120  (start)                      center x=600
y=220  [process A]
y=330  <decision?>   -- no -->  x=860 [handle exception]  (class alert)
y=440  [process B]   <-- rejoin from (860,330+35) via L path
y=540  (end)
```

## Decision labels

Put the outcome label immediately after the diamond, horizontal, 12 px from the tip:

```svg
<!-- yes: down -->
<path class="conn-main" d="M 600,365 L 600,410" marker-end="url(#arrow-main)"/>
<text class="edge" x="614" y="388" fill="#34d399" text-anchor="start">是</text>
<!-- no: right -->
<path class="conn-err" d="M 650,330 L 780,330" marker-end="url(#arrow-err)"/>
<text class="edge" x="715" y="324" fill="#fb7185">否</text>
```

## Emphasis

Happy path uses `.conn-main` and `arrow-main`. Ordinary branches use `.conn`. Failure and retry use `.conn-err`. Keep the main column visually straighter and brighter than every branch.
