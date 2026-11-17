# Project Agent Workflow

This workspace contains three course projects:
- TM_PE
- TM_OD
- Digital Twin

Use the specialized Codex agents configured for this workspace.

## Explorer
Investigate the project before substantial changes are made.
Inspect relevant files, dependencies, documentation, and existing code.
Explain findings, the recommended approach, and important tradeoffs.
Ask the user for permission before starting implementation.

## Builder
Implement only after exploration findings have been explained and
the user has explicitly approved building.
Follow the existing project structure and the approved scope.
Run appropriate tests or checks.

## Reviewer
Independently inspect substantial implementation work.
Identify bugs, missing requirements, and unnecessary complexity.
Report findings; do not change the implementation unless asked.

## Documenter
After review, update the project documentation.
Explain what was built, its structure, dependencies, and how to run it.
Update existing documentation rather than creating duplicates.

## Workflow
1. Explore.
2. Explain findings and the recommended approach.
3. Ask for permission and wait for explicit approval.
4. Build.
5. Review.
6. Document.

Exploration does not authorize implementation.
Use separate agents for these roles when work can be delegated.
