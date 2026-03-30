# Requirements: AlgoMath

**Defined:** 2025-03-29
**Core Value:** Mathematicians can reliably convert complex algorithmic descriptions from academic papers into correct, reproducible, executable code with minimal back-and-forth iterations

## v1 Requirements

### Workflow Engine (WFE)

- [x] **WFE-01**: User can invoke system via natural language commands ("Extract algorithm", "Generate code", "Run it", "Verify")
- [x] **WFE-02**: System detects user intent and routes to appropriate workflow automatically
- [ ] **WFE-03**: System maintains context across workflow steps (text, steps, code, results)
- [ ] **WFE-04**: User can interrupt workflow and resume without losing context
- [x] **WFE-05**: System provides clear progress indicators during multi-step workflows

### Extraction (EXT)

- [ ] **EXT-01**: User can input mathematical text describing an algorithm
- [ ] **EXT-02**: System identifies algorithm boundaries within text
- [ ] **EXT-03**: System extracts algorithm inputs and outputs
- [x] **EXT-04**: System parses algorithm into structured step-by-step representation
- [x] **EXT-05**: System handles common mathematical notation (loops, conditionals, assignments)
- [x] **EXT-06**: User can review and edit extracted steps before proceeding

### Code Generation (GEN)

- [ ] **GEN-01**: System generates Python code from structured algorithm steps
- [ ] **GEN-02**: Generated code includes type hints for mathematical clarity
- [ ] **GEN-03**: Generated code includes docstrings explaining the algorithm
- [ ] **GEN-04**: Generated code is syntactically correct and executable
- [ ] **GEN-05**: System handles standard mathematical operations correctly
- [ ] **GEN-06**: User can review generated code before execution

### Execution (EXE)

- [ ] **EXE-01**: System executes generated code in sandboxed environment
- [ ] **EXE-02**: System captures stdout and stderr from execution
- [ ] **EXE-03**: System implements timeout protection (e.g., 30 seconds)
- [ ] **EXE-04**: System restricts file system access (sandboxed)
- [ ] **EXE-05**: System reports execution status (success/failure) clearly
- [ ] **EXE-06**: System provides meaningful error messages on failure

### Verification (VER)

- [ ] **VER-01**: System verifies code runs without errors
- [ ] **VER-02**: System can compare output against expected results (if provided)
- [ ] **VER-03**: System explains algorithm behavior in natural language
- [ ] **VER-04**: System identifies potential edge cases or issues
- [ ] **VER-05**: User can request detailed explanation of any step

### Context Management (CTX)

- [ ] **CTX-01**: System persists extracted algorithms across sessions
- [ ] **CTX-02**: System persists generated code across sessions
- [ ] **CTX-03**: System persists execution history across sessions
- [ ] **CTX-04**: User can view history of previous algorithm iterations
- [ ] **CTX-05**: System uses git for algorithm versioning

## v2 Requirements

### Enhanced Extraction

- **EXT-07**: Handle multi-algorithm detection in single text
- **EXT-08**: Support citation-aware extraction
- **EXT-09**: Advanced ambiguity resolution with user input

### Enhanced Generation

- **GEN-07**: Generate optimization suggestions
- **GEN-08**: Alternative implementation options
- **GEN-09**: Generate test cases automatically

### Enhanced Verification

- **VER-06**: Property-based testing suggestions
- **VER-07**: Complexity analysis (time/space)
- **VER-08**: Formal correctness hints

### Collaboration

- **COL-01**: Export algorithm as standalone Python package
- **COL-02**: Import external algorithm libraries

## Out of Scope

| Feature | Reason |
|---------|--------|
| Direct PDF/LaTeX parsing | Assume text extraction handled upstream |
| Multi-language code generation | Python focus for v1 |
| Visual/mathematical notation rendering | Text-based only |
| Multi-user collaboration | Single user workflow |
| Integration with external systems | Wolfram, MATLAB out of scope |
| GPU acceleration | CPU only for v1 |
| Formal verification | Too complex, manual review instead |
| Real-time collaboration | Out of scope |
| Cloud synchronization | Local file-based only |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| WFE-01 | Phase 1 | Complete |
| WFE-02 | Phase 1 | Complete |
| WFE-03 | Phase 1 | Pending |
| WFE-04 | Phase 1 | Pending |
| WFE-05 | Phase 1 | Complete |
| CTX-01 | Phase 1 | Pending |
| CTX-02 | Phase 1 | Pending |
| CTX-03 | Phase 1 | Pending |
| CTX-04 | Phase 1 | Pending |
| CTX-05 | Phase 1 | Pending |
| EXT-01 | Phase 2 | Pending |
| EXT-02 | Phase 2 | Pending |
| EXT-03 | Phase 2 | Pending |
| EXT-04 | Phase 2 | Complete |
| EXT-05 | Phase 2 | Complete |
| EXT-06 | Phase 2 | Complete |
| GEN-01 | Phase 3 | Pending |
| GEN-02 | Phase 3 | Pending |
| GEN-03 | Phase 3 | Pending |
| GEN-04 | Phase 3 | Pending |
| GEN-05 | Phase 3 | Pending |
| GEN-06 | Phase 3 | Pending |
| EXE-01 | Phase 4 | Pending |
| EXE-02 | Phase 4 | Pending |
| EXE-03 | Phase 4 | Pending |
| EXE-04 | Phase 4 | Pending |
| EXE-05 | Phase 4 | Pending |
| EXE-06 | Phase 4 | Pending |
| VER-01 | Phase 5 | Pending |
| VER-02 | Phase 5 | Pending |
| VER-03 | Phase 5 | Pending |
| VER-04 | Phase 5 | Pending |
| VER-05 | Phase 5 | Pending |

**Coverage:**
- v1 requirements: 32 total
- Mapped to phases: 32
- Unmapped: 0 ✓

---
*Requirements defined: 2025-03-29*
*Last updated: 2025-03-29 after initial definition*
