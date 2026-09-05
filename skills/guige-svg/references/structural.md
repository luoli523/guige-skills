# Structural Diagrams

Use this mode for class diagrams, ER diagrams, component/package diagrams, and org charts.

## Class and component diagrams

Use a three-compartment box for class name, attributes, and methods. Use a two-compartment box when behavior is irrelevant. Mark interfaces and abstract classes in the title area.

Relationship vocabulary:

| Relationship | Line | Endpoint |
|---|---|---|
| inheritance | solid | empty triangle at parent |
| implementation | dashed | empty triangle at interface |
| composition | solid | filled diamond at owner |
| aggregation | solid | empty diamond at owner |
| dependency | dashed | open arrow at dependency |
| association | solid | optional open arrow |

Place multiplicity labels close to their endpoints without touching boxes.

## ER diagrams

Use entity name plus attribute compartment. Prefix or badge primary and foreign keys. Use crow's-foot endpoints and show cardinality/optionality explicitly. Arrange entities to minimize crossed relationships; central entities belong near the canvas center.

## Org charts

Use a top-down tree. Center the root, distribute siblings evenly, and connect each level through a shared horizontal rail. Use color for departments or roles, not individual people. For five or more levels, consider a left-to-right tree.
