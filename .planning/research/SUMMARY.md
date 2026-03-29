# Research Summary: AlgoMath

**Research Date:** 2025-03-29

## Stack Recommendation

**Primary:** Python 3.11+ with NumPy, SciPy ecosystem
**Secondary:** Markdown/JSON for documentation and state
**Supporting:** pytest for testing, Jupyter for exploration

## Table Stakes Features

1. **Algorithm Extraction**
   - Parse natural language mathematical descriptions
   - Extract structured steps
   - Handle common notation

2. **Code Generation**
   - Python code from algorithm steps
   - Syntactically correct output
   - Basic documentation

3. **Code Execution**
   - Safe, sandboxed execution
   - Output capture
   - Error handling

4. **Verification**
   - Run verification
   - Result explanation
   - Error detection

5. **Context Management**
   - State persistence across workflows
   - Algorithm versioning
   - Workflow history

## Key Architecture Components

1. **Workflow Engine** — Intent detection and routing
2. **Extraction Service** — Text → Structured steps
3. **Code Generation Service** — Steps → Python code
4. **Execution Service** — Code → Results
5. **Verification Service** — Results → Validation
6. **Context Manager** — State persistence

## Critical Pitfalls to Avoid

1. **Over-engineering NLP** — Accept some manual correction
2. **Assuming code correctness** — Always verify
3. **Context window limits** — Process one algorithm at a time
4. **Brittle workflows** — Support interruptions and editing
5. **Unsafe execution** — Sandbox generated code
6. **Poor error messages** — Design for recovery
7. **Version control issues** — Use git for algorithms
8. **Over-promising verification** — Be honest about limitations

## Watch Out For

- Mathematical notation ambiguity
- Floating point precision issues
- Side effects in generated code
- Security in code execution
- User context switching mid-workflow

## Recommended Phasing

**Phase 1:** Workflow engine + Context manager + Basic extraction
**Phase 2:** Code generation service
**Phase 3:** Execution service with sandboxing
**Phase 4:** Verification and explanation features
**Phase 5:** Polish, edge cases, optimization

---
*Research synthesis complete*
