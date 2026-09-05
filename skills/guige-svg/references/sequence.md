# Sequence Diagrams

Place participants in equal-width boxes across the top. Draw dashed lifelines downward and arrange messages from top to bottom in chronological order.

Use:

- solid arrow for synchronous request;
- open arrow for asynchronous message;
- dashed reverse arrow for return/response;
- narrow activation bar centered on the active lifeline;
- a right-side loop for self-messages;
- dashed frames with labeled tabs for `alt`, `opt`, `loop`, and `par` blocks.

Keep 42-54 px between messages. Number messages when there are eight or more or when prose refers to specific steps. Put message text above the line and avoid actor boxes.

For conditional frames, show the guard near the frame label and use a dashed divider for alternatives. Size the frame to include complete participating lifelines and all enclosed messages.

Assign participant colors consistently: actor box stroke, activation bar, and optionally outgoing arrows may share the same semantic color.
