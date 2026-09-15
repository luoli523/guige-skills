# Sequence Diagrams

## Layout algorithm

1. Participants across the top at `y=100`, boxes 140 × 44, centers 200 px apart starting at `x=160`.
2. Lifelines from the bottom of each box to the last message + 40 px, class `.lifeline`.
3. Messages top to bottom, 48 px apart, first message at `y=180`.
4. Activation bars 10 px wide, centered on the lifeline, spanning from the incoming call to its return.
5. Number messages when there are 8 or more or when prose refers to step numbers.

## Participant

```svg
<g transform="translate(90,100)">
  <rect class="mask" width="140" height="44" rx="6"/>
  <rect class="node primary" width="140" height="44" rx="6"/>
  <text class="label" x="70" y="27">Browser</text>
</g>
<line class="lifeline" x1="160" y1="144" x2="160" y2="620"/>
```

Assign each participant one class and reuse it for its box stroke and activation bar.

## Messages

```svg
<!-- sync call -->
<path class="conn" d="M 164,180 L 356,180" marker-end="url(#arrow)"/>
<text class="edge" x="260" y="174">POST /orders</text>

<!-- return: dashed, open arrow, muted italic -->
<path class="conn" d="M 356,276 L 164,276" stroke-dasharray="6 3" marker-end="url(#arrow-open)"/>
<text class="edge" x="260" y="270" font-style="italic">201 Created</text>

<!-- async -->
<path class="conn" d="M 364,228 L 556,228" marker-end="url(#arrow-open)"/>

<!-- self message -->
<path class="conn" d="M 364,324 L 404,324 L 404,348 L 368,348" marker-end="url(#arrow)"/>
<text class="edge" x="412" y="340" text-anchor="start">validate()</text>
```

Message text is horizontal, 6 px above the line, centered between the two lifelines. Leave a 4 px gap between the line end and the lifeline or activation bar.

## Activation bar

```svg
<rect class="node secondary" x="355" y="180" width="10" height="96" rx="2"/>
```

## Frames (alt / opt / loop / par)

```svg
<rect class="region" x="120" y="360" width="700" height="140" rx="4" stroke="#64748b" stroke-dasharray="4 3"/>
<rect class="node neutral" x="120" y="360" width="46" height="18" rx="4"/>
<text class="edge" x="143" y="373">alt</text>
<text class="annot" x="176" y="373" font-style="italic">[stock available]</text>
<line class="divider" x1="120" y1="430" x2="820" y2="430" stroke-dasharray="4 3"/>
<text class="annot" x="130" y="446" font-style="italic">[else]</text>
```

Size the frame to include every participating lifeline plus 20 px on each side, and all enclosed messages plus 16 px top and bottom.

## Numbering

```svg
<circle class="node highlight" cx="146" cy="180" r="9"/>
<text class="edge" x="146" y="183.5" fill="#60a5fa">1</text>
```
