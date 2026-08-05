# Beyond Clicks Team Workflow

## Branching Strategy

- The `main` branch always contains stable and releasable code.
- Every new feature is developed in a separate feature branch.
- Feature branches follow the naming convention:
  - feature/[description]
  - fix/[description]
  - docs/[description]
  - refactor/[description]
  - chore/[description]
- Feature branches are deleted after they are merged into `main`.

---

## Commit Message Convention

We follow Conventional Commits.

Format:

[type]: description

Types used:
- feat – New feature
- fix – Bug fix
- docs – Documentation updates
- refactor – Code improvements without changing functionality
- chore – Maintenance tasks

This makes the project history easy to understand.

---

## Pull Request Process

- Every feature is developed in its own branch.
- A Pull Request is created before merging into `main`.
- At least one teammate should review the code.
- Review focuses on:
  - Code correctness
  - Readability
  - Data integrity
  - Documentation

---

## Issue Tracking

- Every task begins with a GitHub Issue.
- Issues include a title, description, label, and assignee.
- Pull Requests reference issues using:

Closes #Issue_Number

- Issues are automatically closed after the Pull Request is merged.