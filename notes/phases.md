# Phases — What Still Needs Answering

Inside the locked frame (`concepts/00-locked-frame.md`). These phases do not reopen the stance; they force the remaining gaps into the open.

---

## Phase A — Unit and ledger

**Status:** Partially locked.

Joules are adopted as the first calculable unit. Observation vs intervention is formalized with a conservation audit.

Still open:

- Is energy sufficient as the sole ledger, or do geometry / topology / information require independent accounts that do not fully reduce to Joules?
- What is the minimal state vector that must be sampled so that the energy calculation is meaningful for the class of transitions we care about (density shift, interface stabilization, soft → ordered)?

**Exit criterion:** A short written rule for what must be in the state vector for an energy audit to be considered valid in this project.

---

## Phase B — Terrestrial forcing

**Status:** Promissory.

Constraint #3 says Earth systems are the primary data. The abstract language has not yet been required to answer to a specific real process.

Work:

- Select one concrete terrestrial process (candidate areas: high-pressure ice / water phase boundaries, anisotropic crystal growth, fluid or melt migration pathways).
- Force the locked vocabulary (density as driven, harness, observation vs intervention, Joule ledger) to describe that process without invention.
- Record where the language fits and where it fails or stays silent.

**Exit criterion:** One terrestrial process write-up in `terrestrial/` that either validates, stretches, or breaks parts of the current frame — with the breaks made explicit.

---

## Phase C — What is tracked during the transition

**Status:** Atmospheric.

We know attention belongs to the interval of change. We do not yet have a precise answer to: what is the unit of attention *during* the transition?

Candidates already named: local field value, topological relation, active constraint set, energy flux. Phase A and B should narrow this.

**Exit criterion:** A single, testable statement of the form: "During a controlled transition of type T, the primary quantity being tracked is X, sampled at resolution Y."

---

## Phase D — Representation limits

**Status:** Named but not tested.

Code represents relations; it is not the thing. Failure modes of the representation are not yet operationalized beyond the energy audit.

Work:

- List signatures that would indicate the computational model has drifted from the mechanism it claims to track (beyond energy non-conservation).
- Decide what, if anything, is deliberately left unrepresented.

**Exit criterion:** A short "representation contract" — what the code is allowed to claim, and what counts as evidence that the claim has failed.

---

## Phase E — First computational experiment

**Status:** Not started.

Only after A–D have enough structure to keep the experiment inside the frame.

Candidate toys (from earlier notes):

- anisotropic phase-field (faceting)
- stabilized interface / harness term with explicit Joule accounting
- minimal density field held away from equilibrium under continuous intervention cost

**Exit criterion:** One runnable sketch that obeys the observation/intervention boundary and the conservation audit, and that can be described in the locked vocabulary without embarrassment.

---

## Phase F — Use (deferred)

Use-questions are recorded when they appear. They are not allowed to steer mechanism work until the mechanism has more structure (post E at earliest).

Holding pattern: append use-ideas to a list; do not expand them into design drivers yet.

---

## Suggested order

A (finish unit/ledger rules) → B (terrestrial forcing) → C (sharpen what is tracked) → D (representation contract) → E (first experiment).

B can run in parallel with finishing A. C and D depend on A and B. E depends on all prior.

---

*Frame is locked. Phases answer inside it.*
