# How we work

Short version: every change starts as an issue, lands as a PR, and gets one
review from whoever owns that area. Nothing goes straight to `main`.

## The rules

1. **No direct pushes to `main`.** It is protected. Branch, PR, review, merge.
2. **Every PR closes an issue.** If there is no issue, open one first. It takes
   thirty seconds and it is how anyone else knows the work is happening.
3. **Issues get a track label, a size, and an assignee before work starts.**
   Unassigned issues are up for grabs. Assign yourself when you start, not when
   you finish.
4. **One concern per PR.** If the title needs an "and", split it.
5. **If you change a port, the consumer reviews it.** Ports are the contracts
   between tracks, listed in `docs/port-contracts.md`. Changing one without
   telling the other side is the single most expensive mistake available to us.
6. **Open a draft PR early.** Day one of the work, not day seven. A draft PR is
   how you ask for help without scheduling a meeting.
7. **Reviews within 48 hours.** If you are named in CODEOWNERS you are on the
   hook. "Looks fine" is not a review; say what you checked.
8. **Stuck for more than an hour, comment on the issue.** Not a DM. The comment
   is searchable and the next person hits the same wall.

## Branch names

```
track/yourname/short-description

rtl/dhruv/accumulator-fsm
ml/ilim/int8-export
hw/giuseppe/sense-matrix-rev-a
```

## Commit messages

```
rtl: add saturating accumulator for clipped relu
ml: export int8 weights in row-major bram order
hw: fix hall sensor pullups on rev A
```

Prefix with the track. Imperative mood. Body optional, use it when the "why"
is not obvious from the diff.

## The 80-20

Twenty percent of your time can go to a track that is not yours. Those issues
carry `type:learning` and are written by whoever owns the destination track.
Rules: your own track's work comes first, you pick it up in the open through an
issue rather than quietly, and the area owner is your mentor for it.

If you want to learn something nobody has written an issue for, ask the owner
to write one. Writing the issue is how they level up too.

## Weekly rhythm

- **Meeting:** triage new issues, unblock anything labelled `status:blocked`,
  demo whatever moved.
- **Before the meeting:** update your issues. A stale board is worse than none.
- **After the meeting:** every open issue has an assignee or is closed.

## Reviewing

Check these, in order:
1. Does it do what the linked issue said?
2. Is there evidence it works? Sim output, waveform, bench photo, test log.
3. Does it touch a port? If yes, is the consumer tagged?
4. Would you be able to debug this in November?

Style nits go in a comment, not a blocked merge.
