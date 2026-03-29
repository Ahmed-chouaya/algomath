# Phase 1: Foundation - Context

**Gathered:** 2025-03-29
**Status:** Ready for planning

<domain>
## Phase Boundary

Build the core workflow engine and context management infrastructure that enables all other AlgoMath workflows. This phase establishes the foundation for extraction, generation, execution, and verification workflows by creating the command interface, state management, and persistence layer.

</domain>

<decisions>
## Implementation Decisions

### Command Interface
- **D-01:** Slash commands as primary interface: /algo-extract, /algo-generate, /algo-run, /algo-verify, /algo-status, /algo-list, /algo-history, /algo-help
- **D-02:** Orchestrator supports two modes: auto mode (full workflow) and step-by-step mode
- **D-03:** User selects mode at session start (auto vs step-by-step)

### Context Storage
- **D-04:** Hybrid storage: Markdown for human-readable content (algorithm descriptions), JSON for structured data (algorithm steps, execution results)
- **D-05:** Context directory: .algomath/ at project root

### State Management
- **D-06:** Flexible branching state machine: User can jump between workflow steps, edit at any point
- **D-07:** State tracks completion status: text extracted → steps structured → code generated → execution complete
- **D-08:** No forced linear progression: User can revisit and modify any step

### Progress Indicators
- **D-09:** Progress bars for quantitative feedback: "Extract: ████████░░ 80%"
- **D-10:** Percentage-based where steps are known, text-based where not

### Git Integration
- **D-11:** Background versioning: Internal version history stored in files
- **D-12:** Git integration optional: User doesn't need git knowledge
- **D-13:** Version tracking automatic, no manual commits required

### Error Handling
- **D-14:** Error handling delegated to OpenCode: System relies on OpenCode's error handling capabilities

### Algorithm Format
- **D-15:** Internal format: JSON Schema for structured, reliable code generation
- **D-16:** Display format: Readable pseudocode for user review and editing
- **D-17:** JSON structure example: {"steps": [{"type": "loop", "condition": "...", "body": [...}]}

### Session Persistence
- **D-18:** Named algorithms: User can name algorithms on extraction and return to them later
- **D-19:** Storage location: .algomath/algorithms/{name}/
- **D-20:** Algorithm browsing: /algo-list shows all saved algorithms
- **D-21:** Optional naming: Unnamed algorithms are session-only

### the agent's Discretion
- Progress bar styling and exact percentage calculation
- Specific JSON Schema structure for algorithm steps
- File naming conventions within .algomath/ directory
- Error message formatting (delegated to OpenCode)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Context
- `.planning/PROJECT.md` — Vision, core value, user profile, key principles
- `.planning/REQUIREMENTS.md` — WFE-01 to WFE-05 (Workflow Engine), CTX-01 to CTX-05 (Context Management)
- `.planning/ROADMAP.md` — Phase 1 goal and success criteria

### Existing Codebase
- `.planning/codebase/STACK.md` — Technology stack (Node.js, JavaScript, Markdown, JSON)
- `.planning/codebase/ARCHITECTURE.md` — GSD framework architecture patterns
- `.planning/codebase/STRUCTURE.md` — Directory organization

### Research
- `.planning/research/FEATURES.md` — Feature categories and complexity notes
- `.planning/research/ARCHITECTURE.md` — System components and data flow
- `.planning/research/PITFALLS.md` — Common mistakes to avoid

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- GSD framework structure: Can reuse workflow patterns from `.opencode/get-shit-done/workflows/`
- State management: Can adapt GSD's STATE.md approach for algorithm context
- Progress display: Reuse GSD's UI patterns (banners, tables) for progress indicators

### Established Patterns
- Markdown documentation: Rich frontmatter, embedded guidelines
- Slash command pattern: Already established in `.claude/commands/gsd/`
- JSON configuration: `.planning/config.json` approach

### Integration Points
- AI assistant interface: Commands will integrate with OpenCode's command system
- Git integration: Can use existing git infrastructure if available
- File system: All state persists to local files in .algomath/

</code_context>

<specifics>
## Specific Ideas

- Command structure modeled after GSD but simplified for algorithm-specific workflows
- State machine visual indicator showing: [Extract] → [Generate] → [Execute] → [Verify] with completion status
- Algorithm names should be descriptive: "Dijkstra Shortest Path", "Quick Sort", "Matrix Factorization"
- JSON Schema should support: variables, loops, conditionals, function calls, mathematical operations

</specifics>

<deferred>
## Deferred Ideas

- Multi-algorithm detection in single text — Phase 2 feature
- Advanced ambiguity resolution — Phase 2 feature
- Alternative implementation options — Phase 3 feature
- Property-based testing — Phase 5 feature
- Formal verification hints — Phase 5 feature
- Export as standalone Python package — v2 feature
- Collaborative features — v2 feature
- Cloud synchronization — out of scope

### Reviewed Todos (not folded)
None — this is the first phase

</deferred>

---

*Phase: 01-foundation*
*Context gathered: 2025-03-29*
