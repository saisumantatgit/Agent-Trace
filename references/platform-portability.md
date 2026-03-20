# Platform Portability

The portable core of this skill is:

- `SKILL.md`
- the `references/` folder
- a stable expectation that a repo-universe query interface exists or a fallback is used

Product-specific additions:

- Claude Code: `.claude/` directory with agents, commands, skills
- Codex/OpenAI: `adapters/codex/AGENTS.md`
- Cursor: `adapters/cursor/.cursor/rules/trace.md`
- Aider: `adapters/aider/.aider.conf.yml`

Keep procedural logic in `SKILL.md`.
Keep product metadata in product-specific adapter files.
