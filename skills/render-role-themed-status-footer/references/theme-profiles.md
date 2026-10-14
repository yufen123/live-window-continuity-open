# Built-in role-theme profiles

Use the closest profile only after constructing the canonical record. Translate labels and phrases into the user's language. Preserve semantics over style.

| Theme ID | Role label | State label | Node label | Next label |
| --- | --- | --- | --- | --- |
| `neutral-governance` | Role | Overall status | Current node | Next / stop |
| `code-collaboration` | Worker role | Build status | Current task | Review gate / next delivery |
| `learning-companion` | Learning companion | Progress or feel | Current exercise | Next practice |
| `story-world` | Current character | World state | Current scene | Next scene entrance |
| `daily-companion` | How I am accompanying you | How things are now | Present focus | What comes next |
| `project-work` | Responsible role | Project status | Current phase | Approval gate / next delivery |

## Gate vocabulary

Use role-fitting language while keeping the gate explicit.

| Gate | Neutral | Code | Learning | Story | Companion | Project |
| --- | --- | --- | --- | --- | --- | --- |
| `WAITING_FOR_USER` | Waiting for your choice | Waiting for approval or review | Waiting for your attempt or choice | Waiting for the player's choice | Waiting until you want to continue | Waiting for the decision owner |
| `BLOCKED` | Blocked by the named dependency | Build or evidence blocker | Missing example, attempt, or prerequisite | The scene entrance is not open | Paused by a practical constraint | Blocked by dependency or approval |
| `HOLD` | Stop here | Hold this task | Stay with this exercise | Pause this scene | Rest here for now | Hold at this phase |
| `CLOSED` | Complete or retired | Merged, closed, or retired | Exercise complete | Scene closed | This moment is complete | Delivery complete or route closed |

## Example renders

### Code collaboration

```text
Worker role: Implementation reviewer | Build status: REVISE | Current task: navigation timing check | Review gate: waiting for the implementer; do not modify code
```

### Learning companion

```text
Learning companion: Pronunciation coach | Progress: READY | Current exercise: one relaxed vowel | Next practice: wait for one attempt, then correct only one variable
```

### Story world

```text
Current character: Harbor guide | World state: WATCH | Current scene: sealed lighthouse door | Next scene: wait for the player's choice; the door does not open automatically
```

### Daily companion

```text
How I am accompanying you: quiet planning partner | How things are now: resting | Present focus: after-dinner pause | What comes next: continue only when you feel ready
```

## Custom themes

When a user requests a new theme, define only:

```text
THEME_ID
VISIBLE LABELS
TONE
DENSITY
OPTIONAL ICONS
GATE VOCABULARY
NEUTRAL FALLBACK
```

Reject a custom theme if it cannot express `WAITING_FOR_USER`, `BLOCKED`, `HOLD`, and `CLOSED` plainly or if it changes the canonical record.
