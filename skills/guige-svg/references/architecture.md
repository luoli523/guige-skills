# Architecture Diagrams

Use one primary direction:

- left-to-right for requests, pipelines, or data movement;
- top-to-bottom for layered systems and deployment stacks.

Group components by role or boundary: clients, edge/gateway, services, messaging, data, and infrastructure. Draw region boundaries before connectors. Nest boundaries only when the nesting conveys deployment or ownership.

For left-to-right layouts, assign one column per layer and stack peers vertically. For top-to-bottom layouts, assign one row per layer. Place databases and durable stores at the final layer unless the architecture requires otherwise.

Route busy connections orthogonally with `<path>` segments. Use a horizontal or vertical bus bar for a shared queue/event bus instead of drawing every pairwise connection. De-emphasize secondary links with lower opacity.

Represent common components consistently:

- user-facing/client: rounded rectangle, primary cyan;
- service/process: rounded rectangle, secondary emerald;
- database/store: cylinder, data violet;
- queue/bus: narrow bar or capsule, connector orange;
- external dependency: neutral dashed boundary;
- security boundary or failure path: alert rose.

Keep region labels at the upper-left inside each boundary. Put a legend outside all regions when symbols or colors are not self-explanatory.
