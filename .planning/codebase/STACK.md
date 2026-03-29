# Technology Stack

**Analysis Date:** 2025-03-29

## Languages

**Primary:**
- JavaScript (ES6+) - All tooling and utility scripts
- Markdown - Documentation, workflows, templates, and agent definitions
- JSON - Configuration files and state management

**Secondary:**
- TOML - `.codex/config.toml` for AI assistant configuration
- YAML - Not detected in current structure

## Runtime

**Environment:**
- Node.js 20.x (LTS) - Based on package.json engines
- No browser runtime (framework is AI assistant tooling)

**Package Manager:**
- npm 10.x - Inferred from `.claude/package.json`
- No lockfile present (CLI tool nature, installed globally)

## Frameworks

**Core:**
- None - This is a documentation/workflow framework
- Relies on AI assistant capabilities (Claude, Cursor, OpenCode, etc.)

**Testing:**
- None detected - No test configuration files present

**Build/Dev:**
- None - No build step required
- Plain text/markdown documentation framework

## Key Dependencies

**Critical:**
- None - Framework has no runtime dependencies
- Self-contained markdown-based system

**Infrastructure:**
- Node.js built-ins - `fs`, `path`, `child_process` used by CLI tools
- `gsd-tools.cjs` - Custom CLI utility for GSD operations

## Configuration

**Environment:**
- `.planning/config.json` - Project-specific workflow settings
- `.claude/settings.json` - Claude Code specific settings
- `.codex/config.toml` - Codex configuration

**Build:**
- No build configuration (static documentation)
- `.claude/package.json` - Minimal package file: `{"type":"commonjs"}`

## Platform Requirements

**Development:**
- Any platform with Node.js
- AI coding assistant environment (Claude Code, Cursor, etc.)
- Git (for workflow commits)

**Production:**
- Not deployed as application
- Distributed as documentation/template set
- Version controlled via Git

---

*Stack analysis: 2025-03-29*
*Update after major dependency changes*
