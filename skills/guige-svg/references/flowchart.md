# Flowcharts

The main or happy path runs top-to-bottom. Branches leave decisions left or right and merge back with orthogonal connectors.

| Meaning | Shape |
|---|---|
| start/end | highly rounded rectangle or capsule |
| action/process | rounded rectangle |
| decision | diamond |
| input/output | parallelogram |
| data store | cylinder |

Place “yes/no”, guard, or outcome labels immediately after the decision, not in the middle of a long connector. Use color and line style to distinguish success, failure, and retry paths.

For loops, route the return line around the outside of the main column. Never draw a loop back through existing nodes. For ten or more steps, split into phases or swim lanes with labeled headers.

Maintain 60-90 px between consecutive nodes so the arrow and its label have room. Keep the main path visually straighter and brighter than exceptions.
