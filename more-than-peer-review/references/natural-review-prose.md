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

## Let the reviewer construct the central case

When the main concern can be expressed as a concrete attack, counterexample, or
failure scenario, let the reviewer take ownership of that reasoning. A natural major
comment may begin with wording such as `Here, I consider the following attack` or
`I read the verification rule as permitting the following construction`. It may then
do the following work in connected prose.

1. Define the actors, starting state, and allowed operations.
2. Walk through the construction using the paper's own notation or components.
3. Identify the weaker property that the mechanism actually checks.
4. Explain why the constructed case still passes that check.
5. Trace the same failure into a safeguard, threshold, experiment, or headline claim.
6. End with the exact unresolved question or a plausible direction the authors need
   to assess.

This is not a mandatory paragraph template. Use first-person scene setting only for
the one central case where it makes the reviewer's reasoning easier to follow. Do not
start several comments with `Here, I define`, `Here, I consider`, or another repeated
formula. Other points may begin abruptly from the consequence of the first point.

Give the central case the space it needs. It may occupy several paragraphs inside one
numbered comment. Related follow-up comments can be much shorter. A brief threshold
problem, table inconsistency, or abstract overclaim may need only one or two sentences
after the main mechanism-level objection has been established. Preserve this unequal
weight instead of expanding every point into the same miniature essay.

## Use human-scale manuscript references

In author-facing and editor-facing prose, locate material only by Section, Figure, or
Table when a locator helps the authors find the disputed claim. Do not include page
numbers, line numbers, or stacked coordinates such as a section followed by a page
and line range. Those details belong in the private evidence record.

If no Section, Figure, or Table identifier is available, name the relevant definition,
claim, paragraph topic, or verification step in ordinary prose. A reviewer can write
`the acceptance rule in Section 4` or `the accuracy result in Table 3`. There is no
need to reproduce the extraction coordinates used to find it.

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

First person can also introduce analysis created during the review. Statements such
as `Here, I consider the following failure case` or `I define this attack as follows`
claim ownership only of the argument being presented. They do not imply prior work,
outside experiments, or personal experience.

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
Preserve literal URLs needed for evidence anchors as well. The validator excludes
Markdown headings, HTTP(S) URLs, and explicitly delimited mathematics (`$...$`,
`$$...$$`, `\(...\)`, or `\[...\]`) from punctuation checks. Surrounding prose
remains subject to the same prohibitions. Do not wrap ordinary prose in math
delimiters to avoid these rules; verify that excluded spans are genuine technical
references during the final read.

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
6. Are all author-facing locators limited to Section, Figure, or Table, with no page
   or line numbers?
7. Was first-person scene setting reserved for a central argument rather than repeated
   as a mannerism?

The final draft should remain professional and anonymous. Humor, conversational
asides, invented emotion, and conspicuous stylistic quirks are normally inappropriate
for journal peer review.
