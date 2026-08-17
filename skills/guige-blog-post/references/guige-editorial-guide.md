# Guige Editorial Guide

Use this guide when planning, drafting, and reviewing every article produced by `guige-blog-post`.

## Brand Position

Guige writes for Chinese-speaking AI and technology practitioners. The reader already follows industry news and does not need another generic recap. They want an experienced practitioner to identify what matters, explain the mechanism, and show where an attractive idea may fail in practice.

The brand promise is:

> An AI and technology veteran helps practitioners see what the excitement leaves out.

Authority must come from sound judgment, concrete evidence, honest limits, and useful experience. Never rely on seniority alone.

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
| Tension | Is there a real conflict, tradeoff, or unanswered question? |
| Specificity | Does it contain a concrete object, consequence, or judgment? |
| Brand fit | Does it sound like an experienced practitioner rather than a media account? |
| Credibility | Can every implication be defended by the article? |
| Memorability | Is there a phrase or idea the reader can recall later? |

Reject a title if `Credibility` scores below 4, regardless of its total. Break ties in favor of `Brand fit`, then `Clarity`.

Avoid:

- Unverified numbers or superlatives
- “震惊”“彻底”“颠覆一切” and similar inflation
- Hiding the actual subject only to manufacture curiosity
- Claiming first-hand use when the article is based on secondary sources
- A title that could be attached unchanged to ten unrelated AI articles

## Opening Test

Draft three openings using different mechanisms, then select one:

1. Scene: a real moment that contains the article's tension
2. Contradiction: two facts or beliefs that cannot comfortably coexist
3. Judgment: a sharp, defensible conclusion followed by the evidence it must earn

The chosen opening should pass all four checks:

- The subject is identifiable within the first 150 Chinese characters.
- The tension is specific rather than generic urgency.
- The reader understands what insight the article promises.
- The tone creates trust rather than suspicion of clickbait.

## Shareability Without Begging

Design for three legitimate reasons to share:

| Share motive | Article should provide |
|--------------|------------------------|
| “This expresses what I have struggled to explain” | A precise, earned judgment |
| “This will help a colleague make a decision” | A reusable model, checklist, or boundary |
| “We need to discuss this” | A credible tension with consequences for the reader's work |

Do not add explicit “please repost” language unless the user asks for a campaign-style call to action.

After the article, prepare optional distribution copy outside `index.md`:

- One 50-80 Chinese character Moments post
- One 100-150 Chinese character WeChat forwarding note
- Three excerpt candidates taken or lightly adapted from the article

These are delivery assets, not part of the article body.

## Four-Pass Editorial Review

Review the complete draft in four separate passes. Revise after each pass.

### Pass 1: Truth and evidence

- Are changing facts verified and sources included?
- Are fact, inference, opinion, and personal experience distinguishable?
- Does any sentence exaggerate what the evidence supports?
- Is a counterexample, limitation, or uncertainty missing?

Any invented experience, quote, result, or statistic is a release blocker.

### Pass 2: Brand and argument

- Is there one clear thesis rather than a broad topic summary?
- Does the article contain a judgment only an experienced practitioner is likely to foreground?
- Is expertise demonstrated through reasoning rather than asserted through status?
- Does every major section advance the thesis?

### Pass 3: Reading and voice

- Does the opening establish subject, tension, and promise quickly?
- Are abstract stretches grounded by examples?
- Does the prose vary naturally in sentence length and rhythm?
- Are humor and callbacks precise rather than frequent?
- Can generic transitions, repeated conclusions, and throat-clearing be deleted?

### Pass 4: Utility and spread

- What will the reader remember tomorrow?
- What can the reader apply at work?
- Which sentence would they quote, and has the article earned it?
- Who would they send it to, and why?
- Does the ending deepen the opening instead of merely summarizing it?

## Release Scorecard

Score each dimension from 1 to 5:

| Dimension | Release standard |
|-----------|------------------|
| Thesis | One clear, arguable, consequential claim |
| Evidence | Claims supported; uncertainty and sources handled honestly |
| Veteran insight | Practical judgment beyond a news recap or documentation summary |
| Reader value | A useful model, decision, method, or change in perspective |
| Voice | Professional, conversational, restrained, recognizably Guige |
| Narrative pull | Specific tension sustains attention without clickbait |
| Memorability | At least one earned idea or formulation survives outside the article |
| Share reason | A specific practitioner has a credible reason to send it onward |

Release only when:

- No dimension scores below 3
- `Thesis`, `Evidence`, `Veteran insight`, and `Voice` each score at least 4
- Total score is at least 31 out of 40

If the draft fails, identify the two lowest dimensions and revise those sections. Do not inflate the score without changing the article.

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
