# Coding Conventions

**Analysis Date:** 2025-03-29

## Naming Patterns

**Files:**
- `kebab-case.md` - Markdown documents
- `gsd-*.md` - Agent/workflow files
- `UPPERCASE.md` - Important templates
- `*.cjs` - CommonJS scripts

**Workflows:**
- Descriptive names: `new-project.md`, `plan-phase.md`, `execute-phase.md`
- Action-oriented verbs

**Templates:**
- Capitalized for major templates: `PROJECT.md`, `ROADMAP.md`, `PLAN.md`
- Descriptive for specialized: `verification-report.md`, `summary-standard.md`

**Agents:**
- Role-based: `gsd-planner.md`, `gsd-executor.md`, `gsd-verifier.md`
- GSD prefix for framework agents

## Code Style

**Formatting:**
- No automated formatter configured
- Markdown preferred for documentation
- XML-like tags for sections: `<purpose>`, `<process>`, `<output>`

**Documentation:**
- Rich frontmatter in templates
- Embedded guidelines within documents
- Self-documenting structure

## Import Organization

**References:**
- Use `@` prefix for framework references: `@/home/milgraph/Projects/algo_framework/.opencode/get-shit-done/workflows/new-project.md`
- Relative paths for local files within workflow

**Order:**
- Framework references first
- Local file references
- Template references

## Error Handling

**Patterns:**
- Validation gates before major steps
- User confirmation at decision points
- Graceful degradation
- State recovery via git

**Error Types:**
- Workflow-defined errors
- User input validation
- File system errors

## Logging

**Framework:**
- Console output from AI assistant
- Structured output via UI patterns

**Patterns:**
- Stage banners for workflow transitions
- Progress indicators for long operations
- Summary blocks at completion

## Comments

**When to Comment:**
- Explain workflow purpose
- Document success criteria
- Clarify decision points

**Template Guidelines:**
- Embedded within documents
- Self-contained explanations

## Document Structure

**Templates:**
- Frontmatter with metadata
- Embedded guidelines section
- Usage examples
- Anti-patterns documented

**Workflows:**
- Purpose section
- Available agent types
- Process steps (numbered)
- Output definition
- Success criteria

---

*Convention analysis: 2025-03-29*
*Update when patterns change*
