# Conceptual, Algorithmic, Security, and Systems Review

Use this reference when a paper's contribution depends on an algorithm, protocol,
architecture, security argument, systems design, or claim about computation. It is
an inquiry guide, not a checklist. Report only concerns supported by the manuscript.

## Reconstruct the contribution contract

Before reviewing implementation details, write down privately:

- What real problem motivates the work, and for whom does it matter?
- What is claimed beyond the closest existing approach?
- Which mechanism is asserted to produce the claimed property?
- Which actors, inputs, states, clocks, identities, components, and data are trusted?
- Under which operating conditions and adversary capabilities should the claim hold?
- What observable test would distinguish success from a weaker proxy?

Keep these elements separate. A paper may solve its formalized task while the task
does not represent the motivating problem; implement a mechanism correctly while
the mechanism proves only a proxy; or show benchmark gains without supporting the
stated explanation for those gains.

## Stress-test the logic before requesting experiments

Trace the central claim as a chain:

`motivation -> definition -> assumptions -> mechanism -> established property -> evidence -> conclusion`

Look for the earliest unsupported link. In particular, ask:

- Does the verification predicate establish the claimed property, or only
  consistency, possession, correlation, recoverability, or performance above a
  threshold?
- Can an actor choose both sides of a comparison, construct the accepted state after
  the fact, replay an artifact, or satisfy the predicate without doing the claimed
  work?
- Is the invoked theorem or cryptographic property relevant to the natural attack,
  or does the attack avoid that property entirely?
- Does a guarantee depend on stable serialization, determinism, synchronized time,
  trusted identity, trusted hardware, or an honest setup that the protocol does not
  actually provide?
- Is an economic, deployment, or threat-model assumption doing most of the security
  work? If so, is the paper's conclusion scoped to that assumption?
- Could a degenerate or already-converged input pass while defeating the research
  objective?
- Are two concepts being conflated, such as ownership and learning, linkage and
  provenance, prediction and explanation, robustness and security, or detection and
  attribution?

A minimal thought experiment or attack trace is often the clearest evidence. State
the allowed inputs and actions, show why the stated check accepts, and identify the
claim that therefore does not follow. Do not label a construction an "attack" unless
it is permitted by the manuscript's stated model; if the model excludes it, review
whether that exclusion is justified by the motivating setting.

When this construction becomes the central author-facing concern, present it as a
piece of reviewer reasoning rather than a generic missing-property complaint. Define
the scenario, walk through the states or operations using the paper's notation, and
then separate what the verifier observes from what the paper claims. First-person
wording such as `Here, I consider the following attack` is appropriate when it makes
clear that the reviewer is introducing a concrete test case. Use it once for the main
construction, not as the repeated opening of every numbered point.

Continue vertically from the same construction. A later point may ask why the stated
safeguard does not reject it. Another may show that a fixed performance threshold
only demonstrates prior convergence. A final short point may identify the resulting
overclaim in a figure, table, abstract, or conclusion. These are connected effects of
one root failure, not categories that need independent treatment.

## Choose a review thesis and stop

Do the broad search privately, but do not turn the final review into a report on every
category inspected. Select the earliest and most consequential break in the central
claim chain. That becomes the review thesis.

Normally choose one or two root fault lines. A fault line qualifies when it is central to
the claimed contribution, supported by a concrete manuscript location or
counterexample, and strong enough to change the recommendation or the paper's stated
scope. Once these points are established, stop looking for unrelated material to pad
the author-facing review.

Pursue the selected problem vertically instead. For a non-Accept recommendation,
normally turn the analysis into four numbered comments and never fewer than three.
The comments do not need to be independent. One may establish the root counterexample,
the next may show why the paper's proposed safeguard does not close it, and later
comments may trace the same failure into the protocol specification, evaluation, or
headline conclusion. They should read as one sustained argument rather than a tour of
review categories.

An additional issue belongs in the final review only when at least one of these is
true:

- it is a distinct defect that would change the recommendation by itself;
- resolving it would materially change the central claim or system design; or
- the authors need it to understand a mechanism, consequence, or proposed remedy in
  the primary argument.

Keep ordinary reproducibility gaps, minor numerical discrepancies, baseline breadth,
presentation issues, and optional improvements in the private record unless they
directly support the review thesis. Comprehensive internal checking is useful.
Comprehensive output is not the goal.

## Review the story and motivation

Assess whether the introduction establishes a consequential gap rather than merely
the absence of the proposed technique. Check whether:

- the motivating scenario matches the formal problem and evaluation setting;
- the proposed capability would change a real decision or system outcome;
- the baseline or closest alternative already supplies the material capability;
- novelty lies in a substantive idea rather than a new composition, name, or
  application of known components; and
- limitations narrow the claim consistently across the abstract, introduction,
  evaluation, and conclusion.

Do not substitute "the motivation is unclear" for analysis. Identify the missing
link—for example, the system detects artifact consistency but the motivating user
needs evidence of costly computation.

## Then assess empirical evidence

Experiments should test the paper's actual differentiating claims. Check construct
validity before benchmark coverage: whether the metric, threshold, workload,
baseline, ablation, or attack measures the property named in the claim. Then assess
coverage, uncertainty, sensitivity, reproducibility, and external validity.

Request new experiments only when empirical evidence could resolve the central
uncertainty. If the issue is definitional or logical, ask for a corrected claim,
changed mechanism, formal argument, explicit limitation, or revised threat model.
More runs cannot establish a property that the acceptance rule does not identify.

## Turn analysis into reviewer comments

Lead each major concern with the conclusion, then explain the failure path in enough
detail that the authors can dispute or address it. Questions are useful when they
expose the exact unresolved point, but the review should not be only a list of vague
questions.

Group issues that share one root cause, but keep independently fatal assumptions or
attack paths separate. Avoid manufacturing balance: a paper with one decisive flaw
does not need several generic experimental criticisms, and a technically sound paper
does not need a token weakness.
