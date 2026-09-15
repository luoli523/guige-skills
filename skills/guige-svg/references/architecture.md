# Architecture Diagrams

## Direction

- Left-to-right for request paths, pipelines, data movement: clients at left, stores at right.
- Top-to-bottom for layered stacks and deployments: clients at top, infrastructure at bottom.

## Layout algorithm

1. Group components into layers by role: client, edge/gateway, service, messaging, data, infrastructure.
2. One layer per column (LTR) or row (TTB). Column starts every 220 px from `x=60`; row starts every 120 px from `y=110`.
3. Inside a layer, stack peers on a shared axis. Center the shorter layers on the tallest one so all layers share a vertical midline.
4. Draw regions around layers or sublayers that share infrastructure; pad 20 px inside the boundary and leave room for the region label.
5. Draw connectors between adjacent layers only. Skip-layer links use `.conn-dim`.
6. Place a legend only if a class is not obvious from the labels.

## LTR grid, four layers, 1200 × 750

```
x=60            x=280           x=500           x=720           x=940
[Web]           [Gateway]       [Order Svc]     [Kafka bus]     [(PostgreSQL)]
[Mobile]                        [Payment Svc]                   [(Redis)]
[Partner API]                   [Inventory Svc]                 [(S3)]
```

Peers inside a column: `y = 140, 240, 340` (60-high nodes, 40-px gaps).

## TTB grid

```
y=110   [Browser]  [Mobile]  [CLI]                 class primary
y=230   [        Load Balancer / API Gateway ]     class neutral, width spans the row
y=350   [Auth]     [User]    [Order]               class secondary
y=450   ==== event bus =====================       class bus, 14 px tall
y=530   [(Redis)]  [(PostgreSQL)]  [(S3)]          class data
```

## Connectors

Adjacent layers, one arrow per real dependency:

```svg
<path class="conn" d="M 220,170 L 280,170" marker-end="url(#arrow)"/>
```

Many services into one gateway: trunk first, then one entry (see design-system connector rules). Services onto a bus: short vertical stubs down to the bar, no arrowheads, and the bar carries the label.

```svg
<path class="conn" d="M 580,400 L 580,450"/>
```

## Region nesting

Outer to inner: cloud provider (`stroke-dasharray="12 4"`), region or VPC (`8 4`), zone or subnet (`4 4`). Region labels use the same stroke color as the boundary. At most three nesting levels.

## Class assignment

client `.primary`; gateway and load balancer `.neutral`; service `.secondary`; queue `.bus`; database, cache, object store `.data` as cylinders; cloud region `.infra` boundary; security zone `.alert` boundary.
