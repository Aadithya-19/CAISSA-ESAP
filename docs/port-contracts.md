# Port contracts

A port is an artifact one person publishes and another builds against. If you
change one, the consumer reviews the PR. Owner column is the producer.

| Port | Producer | Consumer | Artifact | Status |
|---|---|---|---|---|
| feature encoding | Kim | Arvind, Dhruv | `docs/eval-spec.md` | not started |
| int8 weights, BRAM map | Ilim | Kade | `ml/quantize/export/` + layout doc | not started |
| golden vectors | Kim, Ilim | Jasmine | `rtl/tb/vectors/` | not started |
| scan clock, latch timing | Giuseppe | Hieu | `docs/sense-timing.md` | not started |
| step, dir, enable | Kade | Adithya | `docs/motion-interface.md` | not started |
| magnet, hall threshold | Amy | Giuseppe | `docs/mechanical-constraints.md` | not started |
| motor and current budget | Gabe | Amy | `docs/mechanical-constraints.md` | not started |

## Rules

- A port is not real until the artifact is committed. Verbal agreement at a
  meeting is not a port.
- Version them. When the int8 layout changes, the RTL side needs to know which
  commit their loader targets.
- Two ports flow upward against the obvious direction: magnet spec constrains
  the sense board, and the current budget constrains the gantry. Decide those
  early, because reversing them means rebuilding hardware.
- If you are blocked waiting on a port, open an issue labelled
  `status:blocked` and link it. Do not wait quietly.
