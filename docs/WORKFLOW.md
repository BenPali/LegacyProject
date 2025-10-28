# Workflow Guide

This document summarizes how we work, the practices we follow, and the pipeline that secures our deliveries.

## Key Principles

- Project management via GitHub Projects (tasks, prioritization, assignments).
- Contribution flow: issue → branch → PR → review (≥1 approval) → merge.
- Direct pushes to `main` are restricted (admin exceptions for controlled emergencies).
- CI runs on every PR and on `main`.
- Code coverage is measured and published by Codecov as a PR comment;
- Dependabot monitors dependencies and opens update PRs automatically.

## Development Cycle

1. Create a GitHub issue with a clear description: module objective, coverage goal, and optional remarks if applicable (these can be risks, TODOs for later, or simple observations).
2. Assign the issue and create a dedicated branch.
3. Develop with regular, coherent commits.
4. Open the Pull Request, link the issue, add a description, checklist, and screenshots/logs if relevant.
5. Review by at least one person (careful reading, constructive comments, suggestions).
6. CI runs tests and reports coverage. There is no automatic merge gate based on coverage; merges are blocked only if CI checks fail. Reviewers consider the Codecov report during approval.
7. Merge to `main` when checks pass and the review is approved.

## Branching and Commit Rules

- Branch naming: prefer `impl/<topic>` that describes what you are working on. For examples, refer to past commits (ignoring those before the project restructuring). Commit messages add details like `fix`, `feat`, etc.
- Commit messages: clear and outcome‑oriented (e.g., `fix(database): handle invalid patches`).
- Keep PRs reasonably sized; split when necessary to ease review.

## CI/CD and Coverage

- Unit tests run on every PR.
- Coverage is published via a Codecov comment;
- No automatic blockage in CI/CD based on coverage; merges are blocked only if the CI fails.
- Keep the pipeline fast and reliable.

## Dependency Security

- Dependabot monitors versions and opens PRs automatically.
- Update PRs follow the same cycle (tests, review, merge).
- If a security alert arises, prioritize the update and document the impact.

## Deployment

- Target: VPS.
- Deployment is orchestrated from `main` after CI validation.

## Review Best Practices

- Check readability, modularity, associated tests, and impact on coverage.
- Require at least one approval; prefer suggestions over mandates.
- Document decisions (in the PR) to record the rationale for changes.

## In Short

A clear flow, reliable CI, and simple rules allow us to ship quickly and confidently. Tools (GitHub Projects, Codecov, Dependabot) automate tracking, quality, and security, while peer review ensures robustness before every merge.
