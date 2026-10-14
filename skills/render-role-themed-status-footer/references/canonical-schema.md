# Canonical status-footer schema

Use this reference to construct or validate the semantic record beneath a themed footer.

## Required fields

| Field | Meaning | Failure to avoid |
| --- | --- | --- |
| `ROLE` | The real active role; include lineage only when needed | Treating a page, tone, or theme as a role claim |
| `STATE` | The latest supported overall state | Turning reported, inferred, or candidate state into verified fact |
| `NODE` | The current bounded point in the interaction or workflow | Naming a whole project when a specific current node is known |
| `AUTHORITY` | What the role may decide or do now | Inferring permission from capability, context recovery, or a next step |
| `GATE` | Whether and under what condition continuation may occur | Hiding a user decision, blocker, HOLD, or closed route |
| `NEXT_STOP` | The next route receipt plus its stopping edge | Writing a plan as though it has already been authorized |

## Recommended gate values

| Gate | Meaning | Visible requirement |
| --- | --- | --- |
| `OPEN_WITHIN_SCOPE` | Continue only inside already authorized scope | State the bounded next action when ambiguity is possible |
| `WAITING_FOR_USER` | A user choice or confirmation is required | Say that the footer is waiting for the user |
| `BLOCKED` | A named dependency or evidence gap prevents progress | Name the blocker and do not imply automatic retry |
| `HOLD` | Stop at the current node | Use explicit stop language |
| `CLOSED` | The route or task is complete or retired | Do not advertise an active next action |

## Truth-state discipline

Distinguish these when material:

```text
FACT / VERIFIED / REPORTED / INFERRED / CANDIDATE
ACCEPTED / WATCH / PARK / REVISE / SUPERSEDED / CLOSED
PLANNED / STARTED / COMPLETED / VERIFIED
```

Coherence is not verification. A recovered context is not action authority. A named next step is not permission.

## Safe compression

A four-part visible footer may combine fields as follows:

```text
VISIBLE ROLE      <- ROLE
VISIBLE STATUS    <- STATE + material GATE
VISIBLE NODE      <- NODE
VISIBLE NEXT      <- AUTHORITY boundary + NEXT_STOP
```

Compress only when a reader can still answer:

1. Who is responding?
2. What is true now?
3. Where is the interaction?
4. May the role continue?
5. What happens next, and where must it stop?

## Semantic back-map test

Read only the rendered footer and reconstruct all six fields. Fail the render if:

- two materially different canonical records could produce the same wording;
- an unauthorized action sounds available;
- a HOLD or blocker is visible only through tone or emoji;
- the role or node depends on private history not present in the footer's selected context;
- the next step lacks a stopping edge.

On failure, expand the footer or use the neutral fallback.
