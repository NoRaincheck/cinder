# Agentic engineering — durable way of working

**Status:** durable — the process this repo follows on every change.
**Sources:** gist `NoRaincheck/ee6b6a80235b9405abc35dff5a68c945`
(`agentic-engineering.md`, 2026-09-14) and
[Kenn: How Kenn is doing Agentic Engineering](https://kenn.io/blog/agentic-engineering-aug-2026/)
(2026-08-12). This file is the durable conversion; the gist and blog are
background, not dependencies.
**Date:** 2026-09-16

> **Durability contract:** this document states the workflow as invariants in
> domain language with stable repo paths and role-based runbooks. Planning
> documents (`docs/superpowers/…`) may point here, never the reverse.

Legend: 🧠 human leans in · ⚙️ agent runs it.

## 1. Research

1. 🧠🔬 **Design together.** The human engages with every brainstorming
   decision and design section. Design is never delegated to agents;
   delegated design is slop. *When unsure:* seek an adversarial second
   opinion — a separate agent session, ideally a different model family,
   judges the decision or design section.
2. ⚙️📡 **Write the spec.** Specs are written for agents, not humans. A human
   who engaged in design does not need to line-read the spec for reassurance.
   Lives at `docs/superpowers/specs/<date>-<topic>.md` while work is in
   flight; deleted or converted at close-out (§5–6).
3. ⚙️📡 **Adversarial spec review.** A separate agent session reviews the
   spec and reports findings. Fix, re-review, repeat until convergence —
   a revision loop between steps 2 and 3.

## 2. Plan and implement

4. ⚙️🦾 **Plan, then subagent-driven implementation.** Convert the converged
   spec into an implementation plan (`docs/superpowers/plans/<date>-<topic>.md`),
   then execute with a fresh implementer and reviewer per task
   (`writing-plans` → `subagent-driven-development`).
   *Review cadence:* plans with >10 tasks pause every ~5 tasks to close out
   reviews (`roborev-fix`) so reviews never pile up; plans with ≤10 tasks may
   close out reviews at the end.

## 3. Review

5. 🧠🔍 **Close-out gate.** Before any PR: every review is closed out, and
   all generated specs and plans are either converted to durable documents
   (`ref/docs/`, `README.md`, `tools/*.md`) or deleted. Planning documents
   land in the default branch only for a specific reason (e.g. a follow-up
   PR requires them).

## 4. Decision register

6. 🧠📖 **Make the work durable.** Durable artifacts state their invariants
   directly in domain language, using stable paths, role-based runbooks, and
   meaningful metadata (status, date, toolchain pins). Planning documents may
   point to durable artifacts, but never the reverse. Delete the planning
   tree post-merge: the repository must still explain itself, and the default
   branch alone must be sufficient to operate and recover the system.
   *Terminal action:* explain the change, open the PR, and own the merge.

## Role-based runbook

- **Human:** owns design decisions (§1.1), judges convergence (§1.3),
  enforces the close-out gate (§3), owns the merge (§4).
- **Agent:** writes specs for implementers (§1.2), reviews adversarially
  (§1.3), implements plan tasks with per-task reviewer (§2), converts or
  deletes planning docs at close-out (§3–4).
- **Repo mapping:** durable process lives here (`ref/docs/`); ephemeral
  planning lives in `docs/superpowers/specs/` + `docs/superpowers/plans/`;
  product invariants live in `ref/docs/SRD.md`; author/operator/agent
  runbooks live in `ref/docs/SRD.md` §Runbooks.

## Addendum — ubiquitous language

Domain-Driven Design (Evans) shrinks the business–technical gap via
ubiquitous language and bounded contexts. With agents in the loop this
matters more, not less: it dictates how requirements are stated to the model
and how its reasoning is interpreted in return. Prefer domain terms
(passage, hub, row, funnel, ending, one-shot, scene gate) over
implementation slang in specs, plans, and durable docs alike.
