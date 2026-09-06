## What this does

<!-- One or two sentences. If you need a paragraph, the PR is too big. -->

Closes #

## Port affected

<!-- Tick one. If a port changes, the consumer on the other side must approve. -->

- [ ] None, internal to my track
- [ ] feature encoding (ML to RTL)
- [ ] int8 weights / BRAM map (Ilim to Kade)
- [ ] golden vectors (eval spec to verification)
- [ ] scan clock / latch timing (sense board to RTL)
- [ ] step, dir, enable (RTL to motion)
- [ ] magnet / hall threshold (mech to sense board)
- [ ] motor and current budget (driver board to mech)

## How I know it works

<!-- Sim output, waveform, bench photo, test log, board scan. Something. -->

## Checklist

- [ ] Linked an issue above
- [ ] Small enough to review in under 20 minutes
- [ ] If this changes a port, I tagged the consumer
- [ ] Golden-vector tests still pass (RTL and ML changes only)
