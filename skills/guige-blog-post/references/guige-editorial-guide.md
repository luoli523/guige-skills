# Guige Editorial Guide

Use this guide when planning, drafting, and reviewing every article produced by `guige-blog-post`.

## Brand Position

Guige writes for Chinese-speaking AI practitioners, developers, technology enthusiasts, founders, product managers, and technical managers. Each article serves one concrete task or decision within this audience. Do not assume a job title implies familiarity with a specific AI concept or with recent news; establish prior knowledge and the knowledge gap in the editorial brief.

The brand promise is:

> Guige explains AI technology, products, and engineering as an experienced peer, helping readers understand mechanisms, make choices, complete work, and recognize the limits of the advice.

Authority must come from sound judgment, concrete evidence, honest limits, and useful experience. Never rely on seniority alone.

## Article-Type Delivery Standards

Choose the dominant type from the reader's task. For mixed articles, add only the standards needed by the promises actually made; do not concatenate every template.

| Type | Reader gain | Required delivery |
|------|-------------|-------------------|
| Tutorial | Complete a task | Prerequisites, smallest working path, expected result and how to check it, likely failures and recovery |
| Mechanism explainer | Explain how and why something works | A concrete running example, causal steps, key distinctions or misconceptions, and the mechanism's limits |
| Tool evaluation or selection | Decide whether an option fits | Target scenario, meaningful baseline or alternatives, evidence basis, cost and limitations, conditional recommendation |
| Engineering retrospective | Diagnose or avoid a similar problem | Symptom and impact, investigation evidence, root cause, repair and verification, transferable lesson; attribute public cases |
| Industry or product analysis | Adjust a judgment or action | Verified change, causal reasoning, affected users or workflows, credible alternatives and uncertainty, conditions for action |
| Reflective essay | Understand an experience or recognize a pattern | An honestly sourced scene or observation, developed interpretation, and a specific insight; no forced checklist |

A useful synthesis may supply value through explanation, integration, or reduced effort. It does not need to disagree with conventional wisdom. Commentary needs a defensible thesis; other types need a clear central question and a demonstrated answer.

## Technical Evidence Requirements

Apply these to the claims and deliverables actually present:

- **Code and commands:** state relevant environment, dependencies and versions, expected output, and verification method. Identify unexecuted examples as untested and pseudocode as illustrative. Never imply a successful run without execution evidence.
- **Model or tool evaluation:** identify tasks, sample size or selection, baseline, configuration, evaluation criteria, and observed failures where available. A demo or a few examples support only a bounded observation, not a general ranking.
- **Performance and cost:** give measurement conditions, units, scope, and calculation assumptions. Distinguish estimates from measurements and identify omitted cost components that could change the decision.
- **Evidence origin:** distinguish author measurements, vendor claims, third-party reports, and illustrative examples. If hands-on evidence is unavailable, scope the article as source-based analysis and narrow its conclusions accordingly.
- **Sources and freshness:** link key factual claims near the claim, with a reference list for navigation. State verification date and relevant version for fast-changing capabilities, pricing, and procedures.

Missing evidence should lead to a narrower claim, an explicit unknown, or further research. It must not be filled with invented experiments or apparent precision.

## Voice Coordinates

| Dimension | Target | Avoid |
|-----------|--------|-------|
| Expertise | Experienced peer who has built and operated systems | Lecturer displaying credentials |
| Confidence | Clear judgment with explicit limits | Certainty unsupported by evidence |
| Humor | Dry, observant, self-aware, occasionally surprising | Meme stacking, forced punchlines, mockery |
| Language | Conversational, precise, economical | Academic review, corporate memo, AI-generated cadence |
| Emotion | Calm curiosity with controlled intensity | Manufactured outrage, anxiety, or triumph |
| Reader relationship | Talking with capable colleagues | Teaching down to beginners |

## Signature Moves

Use these selectively. Repetition across every article turns a signature into a template.

### The veteran's second question

After describing an exciting capability, ask the operational question that experience makes unavoidable:

- What happens when it fails?
- Who pays the latency, cost, or maintenance bill?
- Which assumption stops being true at production scale?
- What human or organizational problem is being mislabeled as a model problem?

Also look for constructive opportunities:

- What previously impractical task has become feasible?
- Under which conditions is it worth trying now?
- What is the smallest useful experiment, and what outcome would justify continuing?
- Does the evidence overturn an assumption learned from earlier systems?

Choose questions that illuminate this material. Do not turn every article into a warning about production complexity.

### Concrete before abstract

Open a conceptual argument with a real decision, failure, user interaction, debugging session, or observed contradiction. Do not fabricate a scene. If no first-hand scene exists, attribute the public example honestly.

### Restrained reversal

Let the article's surface subject lead to a deeper conclusion:

```text
Surface: a new model is better at coding
Deeper turn: the scarce skill is deciding what deserves to be built
```

The turn must follow from the evidence. It is not a trick ending.

### Setup and callback

Plant a concrete image, phrase, or question near the beginning. Return to it near the end after the reader's understanding has changed. Use one callback, not a chain of theatrical reveals.

### Earned quotability

A quotable sentence compresses an argument already demonstrated by the article. It should remain meaningful when copied out of context.

Good pattern:

```text
Specific evidence -> explanation -> concise judgment
```

Weak pattern:

```text
Unsupported slogan -> three parallel slogans -> request to repost
```

## Humor System

Humor is seasoning and evidence of personality, not a quota.

Preferred techniques:

- Dry understatement after describing obvious complexity
- A precise analogy drawn from engineering or working life
- Self-deprecation that increases trust without weakening the argument
- Misdirection followed by a technically accurate turn
- A callback that rewards readers who remember the opening

Guardrails:

- Never joke at the expense of vulnerable people or inexperienced readers.
- Never use humor to hide weak evidence.
- Avoid internet slang that will age the article quickly.
- Remove a joke if it competes with the paragraph's technical meaning.
- Do not label a sentence as humorous; let the turn do the work.

## Title Lab

Generate 8-12 titles before choosing one. Include at least four title approaches, but do not publish the full candidate list unless the user requests it.

Score the three strongest candidates from 1 to 5:

| Criterion | Question |
|-----------|----------|
| Clarity | Can the intended reader tell what the article concerns? |
| Reader relevance | Does it name a useful task, question, consequence, or tradeoff? |
| Specificity | Does it contain a concrete object, consequence, or judgment? |
| Brand fit | Does it sound like an experienced practitioner rather than a media account? |
| Credibility | Can every implication be defended by the article? |
| Memorability | Is there a phrase or idea the reader can recall later? |

Reject a title if `Credibility` scores below 4, regardless of its total. Break ties in favor of `Clarity`, then `Reader relevance`. A straightforward task title can be stronger than a clever one for a tutorial.

Avoid:

- Unverified numbers or superlatives
- “震惊”“彻底”“颠覆一切” and similar inflation
- Hiding the actual subject only to manufacture curiosity
- Claiming first-hand use when the article is based on secondary sources
- A title that could be attached unchanged to ten unrelated AI articles

## Opening Test

Choose an opening suited to the article. Try alternatives when needed:

1. Scene: a real moment that contains the article's tension
2. Contradiction: two facts or beliefs that cannot comfortably coexist
3. Judgment: a sharp, defensible conclusion followed by the evidence it must earn
4. Task: the goal, applicability, and expected result
5. Explanation: a concrete question and example that expose what needs explaining

The chosen opening should pass all four checks:

- The subject is identifiable within the first 150 Chinese characters.
- The task, question, or tension is specific rather than generic urgency.
- The reader understands the promised gain and whether it fits their situation.
- The tone creates trust rather than suspicion of clickbait.

## Shareability Without Begging

Design for three legitimate reasons to share:

| Share motive | Article should provide |
|--------------|------------------------|
| “This expresses what I have struggled to explain” | A precise, earned judgment |
| “This will help a colleague make a decision” | A reusable model, checklist, or boundary |
| “We need to discuss this” | A credible tension with consequences for the reader's work |

Do not add explicit “please repost” language unless the user asks for a campaign-style call to action.

## Four-Pass Editorial Review

Review the complete draft in four separate passes. Revise after each pass.

### Pass 1: Truth and evidence

- Are changing facts verified and sources included?
- Are fact, inference, opinion, and personal experience distinguishable?
- Does any sentence exaggerate what the evidence supports?
- Is a counterexample, limitation, or uncertainty missing?
- Do technical claims meet the applicable evidence requirements above?

Any invented experience, quote, result, or statistic is a release blocker.

### Pass 2: Reader gain and explanation

- Is the central reader question clear, with an arguable thesis when the type calls for one?
- Does the draft deliver the selected article type's required content?
- Are prerequisites and causal steps sufficient for the stated reader, with examples that make the explanation usable?
- Is expertise demonstrated through evidence, explanation, and judgment rather than asserted through status?
- Does every major section help answer the central question?

### Pass 3: Reading and voice

- Does the opening establish subject, applicability, and reader gain quickly?
- Are abstract stretches grounded by examples?
- Does the prose vary naturally in sentence length and rhythm?
- If humor, memorable lines, or callbacks are present, do they help rather than interrupt understanding?
- Can generic transitions, repeated conclusions, and throat-clearing be deleted?

### Pass 4: Utility and spread

- What will the reader remember tomorrow?
- What can the reader apply at work?
- Even if the reader accepts the conclusion, what would they still be unable to explain, choose, or do?
- What example, explanation, procedure, or decision rule would be useful to revisit?
- Who would they send it to, and why?
- Does the ending supply an appropriate verification step, action, decision condition, or earned reflection? A concise operational recap is valid when it helps the reader use the article.

## Release Scorecard

Score each dimension from 1 to 5:

| Dimension | Release standard |
|-----------|------------------|
| Focus | One clear reader question; a defensible thesis for commentary |
| Evidence | Claims supported; uncertainty and sources handled honestly |
| Reader value | The promised gain is demonstrated by the required article-type deliverable |
| Explanation clarity | The intended reader can follow the mechanism, procedure, or reasoning without a material missing step |
| Applicability and limits | Readers can recognize when the explanation or advice applies and where it fails |
| Voice | Professional, conversational, restrained, recognizably Guige |
| Reading efficiency | Structure, examples, and level of detail make the answer easy to follow and revisit |
| Reusable value | A specific reader has a reason to revisit or share the explanation, method, or judgment |

Release only when:

- No dimension scores below 3
- `Evidence`, `Reader value`, and `Explanation clarity` each score at least 4
- Total score is at least 31 out of 40
- The selected article type's required delivery is complete; missing essentials cannot be offset by style points

For each score, name a concrete passage or deliverable that supports it and any remaining gap. Use 3 for useful but incomplete work, 4 for meeting the stated standard, and 5 only when additional demonstrated quality warrants it. Self-scoring is an editing aid, not proof of reader outcomes.

If the draft fails, address release blockers first, then revise the two lowest dimensions and reassess. Do not inflate the score without changing the article.

## De-AI Pass

Search for and rewrite these common signals:

- Repeated “不是……而是……” constructions
- Mechanical triples and symmetrical parallel sentences
- Every section ending with a bold slogan
- Excessive rhetorical questions
- Empty transitions such as “值得注意的是” or “更重要的是”
- Unnecessary English labels where clear Chinese exists
- Generic conclusions that could fit any topic
- Uniform paragraph and sentence lengths

Do not remove all structure or polish. The goal is human judgment and natural rhythm, not deliberate roughness.
