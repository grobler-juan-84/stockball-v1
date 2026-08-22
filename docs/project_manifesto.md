# MoneyBall DB — Project Manifesto

## 1. The Idea

MoneyBall DB is an attempt to study the stock market differently.

The goal is not to build another collection of indicators, reproduce conventional analyst research, or create a system that pretends it can predict the future with certainty.

The goal is to build a **research database and experimentation system capable of discovering repeatable statistical advantages in market behavior**.

The inspiration is Moneyball:

> Stop asking what *should* matter. Measure what actually matters.

Traditional market variables belong in the research. Price, momentum, volatility, macroeconomics, interest rates, earnings, sectors, and market regimes all matter.

But they do not get special treatment.

Election cycles, holidays, calendar effects, unusual correlations, scheduled events, behavioral patterns, cross-asset relationships, and ideas that initially sound ridiculous are allowed to compete against them.

If something can be measured honestly, it can be tested.

---

## 2. We Are Building a Research Laboratory

MoneyBall DB is not initially a trading application.

It is a **data collection and experimentation laboratory**.

The first objective is therefore not:

> "Tell me what stock to buy tomorrow."

It is:

> "Build a trustworthy historical environment in which thousands of questions about markets can be tested."

The database should eventually allow us to describe any historical trading day from several perspectives:

* **When was it?**
* **What happened that day?**
* **What happened afterward?**
* **What state was the market in?**
* **What economic conditions existed?**
* **What known events were occurring?**
* **What calendar conditions surrounded the day?**
* **What unusual or unconventional conditions were present?**

The richer this historical context becomes, the more interesting the questions we can ask.

---

## 3. Data First. Experiments Second. Strategy Last.

The project deliberately separates three things:

### Data

What objectively happened?

### Research

When particular conditions existed historically, what tended to happen afterward?

### Strategy

Can any discovered relationship survive validation and eventually become useful in real-world decision making?

These stages must not be confused.

A pattern is not a strategy.

A correlation is not an edge.

An edge is not automatically profitable.

And a backtest is not reality.

MoneyBall DB should make it difficult for us to fool ourselves.

---

## 4. Reproducibility Is Non-Negotiable

The project must not depend on one computer or one manually assembled database.

A clean clone of the repository should eventually be capable of rebuilding the research environment.

The intended workflow is:

**Clone → Configure → Fetch → Clean → Derive → Validate → Ready**

Two computers running the same version of the project against the same data cutoff should produce the same research dataset.

If data already exists, the system should intelligently update it rather than unnecessarily rebuilding everything.

If the schema changes significantly, we must also be able to deliberately rebuild the database from scratch.

Manual data collection should be the exception, not the foundation.

---

## 5. Local-First, Cloud-Ready

MoneyBall DB is deliberately **local-first, cloud-ready**.

During the sandbox and research phase, the primary database runs on local PostgreSQL.

This keeps the research environment:

* simple
* inexpensive
* fast
* under our control
* easy to rebuild
* independent of unnecessary production infrastructure

But local-first must never mean local-only.

Data acquisition, transformation, validation, schema management, and database migrations must remain reproducible and environment-independent.

The database architecture must avoid unnecessary dependencies on a particular computer, operating environment, or hosting provider.

The rule is:

> **Local-first, cloud-ready.** The research database runs on local PostgreSQL during the sandbox phase. Data acquisition and schema management must be reproducible and environment-independent so the finalized database can later migrate to hosted PostgreSQL/Supabase without redesigning the data model.

When MoneyBall DB eventually requires remote access, persistent hosting, collaboration, an application layer, or production infrastructure, the PostgreSQL database should be capable of moving to a hosted environment such as Supabase without fundamentally redesigning the schema.

**Local PostgreSQL is the current environment. PostgreSQL is the architecture.**

---

## 6. Raw Facts and Derived Knowledge Are Different

Whenever possible, MoneyBall DB should preserve the distinction between:

**Observed data**

and

**Derived data**

For example, a closing price is observed.

Whether that asset was in a momentum regime is derived.

Whether a date was five trading days before month-end is derived.

Whether the next twenty trading days produced a positive outcome is derived.

Derived values are welcome — they are essential to the project — but their derivation must be reproducible.

We should always be able to answer:

> "Where did this number come from?"

---

## 7. The Database Is a Historical Context Engine

Each trading date is more than a price candle.

Over time, MoneyBall DB should allow a date to accumulate context from many independent domains.

Market behavior.

Asset regimes.

Macroeconomic conditions.

Scheduled economic events.

Calendar effects.

Cross-asset behavior.

Corporate events.

Political events.

Sentiment.

Eventually, even unconventional external datasets.

The database therefore becomes a historical context engine:

> **Given everything we know about the conditions surrounding a trading day, what tended to happen next when similar conditions occurred before?**

That is the central research question behind the project.

---

## 8. Orthodox Before Unorthodox

We deliberately begin with conventional market relationships.

Not because we assume they are superior, but because they give us a baseline.

Momentum.

Trend.

Volatility.

Sector strength.

Market regimes.

Macroeconomic conditions.

Cross-asset relationships.

Calendar effects.

Scheduled events.

Once the research machinery is trustworthy, we expand aggressively into unconventional hypotheses.

The strange ideas are not distractions from MoneyBall DB.

They are one of the reasons it exists.

But weird hypotheses deserve the same statistical discipline as conventional ones.

---

## 9. Failure Is Useful Data

Most experiments should fail.

If they do not, our standards are probably too weak.

An experiment that convincingly demonstrates that an idea has no useful relationship with future market behavior is still valuable.

It removes one possibility from the search space.

We therefore record failed experiments rather than hiding or deleting them.

MoneyBall DB should accumulate both:

**evidence of what works**

and

**evidence of what does not.**

---

## 10. Discovery and Validation Must Remain Separate

We must resist designing experiments that reward us for finding the answer we wanted.

Patterns discovered in historical data must be challenged using data that was not used to discover them.

Interesting findings should therefore progress through increasingly difficult stages:

**Hypothesis → Discovery → Validation → Replication → Candidate Edge**

Only after surviving those stages should something begin to influence an actual trading strategy.

The objective is not to produce impressive backtests.

The objective is to discover relationships that refuse to disappear when challenged.

---

## 11. Probabilities, Not Prophecies

MoneyBall DB does not need to predict exactly what the market will do tomorrow.

A useful discovery might instead look like:

> Under condition X, outcome Y historically occurred 63% of the time, compared with a 52% baseline.

That difference may be more valuable than a system claiming certainty.

Markets are probabilistic environments.

The system should therefore become increasingly good at answering questions such as:

> "When conditions looked like this before, what happened next — and how often?"

---

## 12. Small Edges Matter

We should not dismiss an effect simply because it looks boring.

A tiny but persistent advantage may matter more than a spectacular relationship that occurs twice.

MoneyBall thinking means being willing to discover that an apparently insignificant variable contributes useful information when combined with other conditions.

We are looking for ways to **get on base**.

The eventual advantage may not come from one extraordinary predictor.

It may come from combining many small, independent pieces of information.

---

## 13. The Schema Is Allowed to Grow

The initial tables are not the final database.

They are the foundation.

New tables will be added as new research questions require new information.

The rule is:

> **Do not collect data merely because it exists. Collect it because it enables a question worth asking.**

The schema should grow with the research rather than attempting to predict every future requirement today.

---

## 14. Curiosity Is Allowed. Discipline Is Required.

No hypothesis should be rejected merely because it sounds unconventional.

At the same time, no hypothesis should be accepted merely because its result looks exciting.

This project deliberately combines two attitudes:

**Extreme curiosity**

and

**extreme skepticism.**

Curiosity generates experiments.

Skepticism determines which results survive.

We need both.

---

## 15. Build for One Researcher First

MoneyBall DB does not initially need to become a commercial platform.

It needs to work for us.

The priority is:

**Correctness → Reproducibility → Research capability → Speed → Interface**

A beautiful dashboard sitting on unreliable research is worthless.

A command-line script capable of reproducing years of trustworthy research is enormously valuable.

Interfaces can come later.

---

## 16. The Long-Term Vision

Eventually, MoneyBall DB should become capable of examining a current market day and finding historically comparable conditions.

Not because history repeats perfectly.

It does not.

But because markets repeatedly encounter combinations of fear, momentum, volatility, liquidity, economic conditions, events, positioning, and human behavior.

The long-term system should be capable of saying:

> "These are today's measurable conditions."

> "These historical periods looked most similar."

> "These were the distributions of outcomes that followed."

> "These factors appear to increase or decrease the probability of particular outcomes."

That is far more interesting than simply asking whether an RSI crossed 30.

---

# The MoneyBall Rules

**Measure first.**

**Assume nothing.**

**Test everything.**

**Record failures.**

**Challenge successes.**

**Prefer probabilities over predictions.**

**Make every result reproducible.**

**Build local-first, but remain cloud-ready.**

And when an idea sounds stupid but can be measured objectively:

**run the experiment.**
