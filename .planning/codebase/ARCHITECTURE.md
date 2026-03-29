# Architecture

**Analysis Date:** 2025-03-29

## Pattern Overview

**Overall:** Multi-Platform Workflow Orchestration Framework

**Key Characteristics:**
- Documentation-driven (no runtime code execution)
- Multi-platform support (Claude, Cursor, OpenCode, Codex, Gemini, Windsurf)
- Template-based code generation
- Agent-orchestrated task execution
- State persistence via markdown files

## Layers

**Workflow Layer:**
- Purpose: Define multi-step procedures for project management
- Contains: Workflow definitions (new-project, plan-phase, execute-phase, etc.)
- Location: `.opencode/get-shit-done/workflows/*.md`
- Depends on: Template layer, Agent layer
- Used by: Command layer, User interactions

**Command Layer:**
- Purpose: Provide slash commands for AI assistants
- Contains: Command definitions with execution context
- Location: `.claude/commands/gsd/*.md`, `.opencode/commands/gsd/*.md`
- Depends on: Workflow layer
- Used by: AI assistants (Claude Code, Cursor, etc.)

**Template Layer:**
- Purpose: Provide reusable document structures
- Contains: Markdown templates with embedded guidelines
- Location: `.opencode/get-shit-done/templates/*.md`
- Depends on: None (self-contained)
- Used by: Workflow layer, Agent layer

**Agent Layer:**
- Purpose: Define specialized subagent capabilities
- Contains: Agent skill definitions and prompts
- Location: `.opencode/get-shit-done/agents/*.md`
- Depends on: Template layer
- Used by: Workflow layer

**Tooling Layer:**
- Purpose: CLI utilities for workflow operations
- Contains: Node.js scripts for common operations
- Location: `.opencode/get-shit-done/bin/gsd-tools.cjs`
- Depends on: Node.js built-ins
- Used by: Workflow layer, Command layer

**Configuration Layer:**
- Purpose: Store project state and settings
- Contains: JSON configs, markdown state files
- Location: `.planning/*.json`, `.planning/*.md`
- Depends on: File system
- Used by: All layers

## Data Flow

**Command Execution:**

1. User invokes slash command (e.g., `/gsd-new-project`)
2. AI assistant loads workflow definition from `.opencode/get-shit-done/workflows/`
3. Workflow references templates from `.opencode/get-shit-done/templates/`
4. Workflow may spawn agents using Agent layer definitions
5. Agents write artifacts to `.planning/` directory
6. Workflow commits changes via git
7. State updated in `.planning/STATE.md`

**State Management:**
- File-based: All state lives in `.planning/` directory
- Markdown frontmatter for structured data
- JSON configs for workflow preferences
- Git-tracked for history and recovery

## Key Abstractions

**Workflow:**
- Purpose: Multi-step procedure definition
- Examples: `new-project.md`, `plan-phase.md`, `execute-phase.md`
- Pattern: Document with `<process>`, `<purpose>`, `<success_criteria>` sections

**Command:**
- Purpose: AI assistant slash command
- Examples: `/gsd-new-project`, `/gsd-plan-phase`, `/gsd-execute-phase`
- Pattern: Markdown file with execution context and workflow reference

**Template:**
- Purpose: Reusable document structure
- Examples: `PROJECT.md`, `ROADMAP.md`, `PLAN.md`
- Pattern: Markdown with embedded guidelines and placeholders

**Agent:**
- Purpose: Specialized subagent for task execution
- Examples: `gsd-planner`, `gsd-executor`, `gsd-verifier`
- Pattern: Skill definition with capabilities and constraints

**Phase:**
- Purpose: Unit of work in roadmap
- Location: `.planning/phases/phase-{N}/`
- Contains: CONTEXT.md, PLAN.md, work/, SUMMARY.md

## Entry Points

**Workflow Entry:**
- Location: `.opencode/get-shit-done/workflows/*.md`
- Triggers: Command invocation from AI assistant
- Responsibilities: Orchestrate multi-step process, spawn agents, manage state

**Tool Entry:**
- Location: `.opencode/get-shit-done/bin/gsd-tools.cjs`
- Triggers: Workflow needs atomic operation
- Responsibilities: Config parsing, model resolution, git commits, phase lookup

**Configuration Entry:**
- Location: `.planning/config.json`
- Triggers: Workflow initialization
- Responsibilities: Store workflow preferences, agent settings, model profiles

## Error Handling

**Strategy:** Workflow-defined error handling with checkpoint patterns

**Patterns:**
- Validation gates before major steps
- User confirmation at decision points
- Graceful degradation (skip optional steps)
- State recovery via git history

## Cross-Cutting Concerns

**Logging:**
- Console output from AI assistant
- Structured output via UI patterns (banners, tables)
- Git commit history as audit trail

**Validation:**
- Frontmatter validation for structured documents
- Path resolution verification
- Model availability checks

**File Operations:**
- Atomic writes via temp file + rename
- Path validation before operations
- Directory creation as needed

---

*Architecture analysis: 2025-03-29*
*Update when major patterns change*
