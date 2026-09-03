# Natural Reviewer Prose

Use this reference only after the substantive review is complete. Its purpose is to
make the author-facing draft read like a careful reviewer thinking through this
particular paper. It does not authorize hiding AI assistance, evading detection, or
changing the evidence record.

## Preserve substance first

Freeze the recommendation reasons, factual claims, manuscript locators, numbers,
counterexamples, uncertainty, and scope of every requested action. A prose edit may
combine or reorder sentences, but it must not strengthen an allegation, invent a
fact, add a citation, or turn an unresolved question into a demonstrated error.

## Let the issue determine the paragraph

Do not make adjacent comments look as though they were generated from one form.

- A decisive logical defect may need a counterexample and several sentences.
- A numerical inconsistency may need only two direct sentences.
- A genuine question can end with the question itself.
- A conclusion may stand without a ritual `Please clarify` sentence when the remedy
  is already obvious or the flaw is not repairable within ordinary revision.

Vary length and syntax because the arguments differ, not by randomly perturbing the
text. Do not split one issue merely to create short points or fuse unrelated issues
to create a long one.

## Write from a reviewer's point of view

Use direct judgments when the evidence supports them: `This condition does not imply
agreement`, `I could not find a rule that orders these updates`, or `Figure 6 measures
throughput, not safety`. First person is acceptable when it accurately describes the
reviewer's reading or uncertainty; it must not disclose identity or fabricate work
performed.

Use first person to report a genuine reading reaction when helpful. Examples include
`I kept coming back to Equation 12`, `I do not see what forces the honest nodes to
agree`, and `Perhaps I missed a transition, but the copied state appears stale after
the next credit`. These statements make the reviewer's reasoning visible without
inventing a biography.

Never claim prior work, implementation experience, deployments, publications, or
expertise that the user did not provide as true. If the user supplies real experience
and asks to use it, generalize it enough to preserve anonymity and omit project,
system, institution, collaborator, and paper names. A phrase such as `In a similar
system I worked on` is allowed only when it is factually true.

Do not manufacture praise before criticism. Mention a strength when it matters to
the evaluation, not to satisfy a balanced template. Mixed judgments are useful when
they are real: a metric can be well chosen while the inference drawn from it is too
strong.

## Remove common model-written signals

Revise when several of these occur together:

- consecutive points have nearly identical word counts or sentence counts;
- every point follows `observation -> consequence -> Please ...`;
- every paragraph ends with a requested action;
- openings use generic phrases such as `addresses an important problem`, `timely and
  valuable`, or `a welcome contribution` without saying what specifically matters;
- repeated transitions (`However`, `Moreover`, `Furthermore`, `Additionally`) do the
  work that the argument should do;
- abstract nouns and emphasis words replace the actual technical object;
- lists are forced into groups of three, or contrasts repeatedly use `not only ...
  but also ...`;
- headings restate the same severity label for every point; or
- the prose explains obvious implications at length instead of trusting the reader.

Prefer ordinary verbs and concrete nouns. Delete throat-clearing such as `It is
important to note that` and `It should be emphasized that`. Do not impose blanket
bans on passive voice, technical terms, or long sentences.

For this skill's submission-ready author and editor prose, apply these house-style
rules without exception:

- do not use an em dash (`—`);
- do not use semicolons (`;`); and
- do not use colons (`:`) inside prose paragraphs or numbered comments.

Rewrite the sentence instead of replacing one disallowed mark with another. Markdown
headings and template labels may contain a colon because they are not submission
prose. Preserve mathematical notation verbatim only when changing its punctuation
would make the technical reference incorrect; otherwise describe it in words.

## Final read-aloud pass

Read only the author-facing section once as continuous prose. Check:

1. Could the opening belong unchanged to many unrelated papers? If so, make it
   specific or remove it.
2. Do adjacent points begin, develop, and end the same way? Change the prose only
   where the underlying reasoning allows it.
3. Is any sentence present solely to sound constructive, emphatic, or polished?
   Delete it.
4. Does each question identify what remains unresolved rather than asking the
   authors to `clarify` in general?
5. Did the edit preserve every evidence anchor and recommendation reason?

The final draft should remain professional and anonymous. Humor, conversational
asides, invented emotion, and conspicuous stylistic quirks are normally inappropriate
for journal peer review.
