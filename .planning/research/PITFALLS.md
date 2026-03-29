# Pitfalls Research: AlgoMath

**Research Date:** 2025-03-29

## Common Mistakes in Algorithm Implementation Frameworks

### Pitfall 1: Over-Engineering the NLP Layer

**Issue:** Trying to parse all possible mathematical notation variations
**Why it happens:** Mathematical notation is extremely diverse
**Impact:** Endless edge cases, brittle parsing, maintenance burden
**Prevention:**
- Focus on structured output, not perfect parsing
- Accept that some manual correction may be needed
- Use examples to guide extraction rather than exhaustive grammar

**Warning Signs:**
- Parser code growing exponentially
- Endless regex additions
- Special cases for every paper

**Phase to address:** Phase 1 (Extraction service design)

---

### Pitfall 2: Assuming Code Correctness

**Issue:** Treating generated code as automatically correct
**Why it happens:** LLMs produce confident-looking code
**Impact:** Silent errors, wrong results, loss of user trust
**Prevention:**
- Always include verification step
- Encourage test cases
- Make correctness checking explicit

**Warning Signs:**
- Skipping verification for "simple" algorithms
- No test coverage
- Users reporting wrong results

**Phase to address:** Phase 4 (Verification service)

---

### Pitfall 3: Ignoring Context Window Limits

**Issue:** Trying to process entire papers in one go
**Why it happens:** Papers can be very long
**Impact:** Context overflow, lost information, poor results
**Prevention:**
- Process one algorithm at a time
- Allow user to specify boundaries
- Support incremental processing

**Warning Signs:**
- "The algorithm continues but was cut off"
- Missing steps in extraction
- Incomplete code generation

**Phase to address:** Phase 1 (Extraction workflow)

---

### Pitfall 4: Brittle Workflow Transitions

**Issue:** Rigid workflow that can't handle interruptions
**Why it happens:** Designing for the happy path only
**Impact:** Frustrated users, broken sessions, lost work
**Prevention:**
- Support workflow resumption
- Allow editing at any stage
- Graceful handling of failures

**Warning Signs:**
- "You must start over" messages
- Lost context on error
- No way to fix mistakes

**Phase to address:** Phase 0 (Workflow engine)

---

### Pitfall 5: Security in Execution

**Issue:** Running untrusted generated code without sandboxing
**Why it happens:** Sandboxing seems complex
**Impact:** Security vulnerabilities, data loss, system compromise
**Prevention:**
- Use subprocess with restricted permissions
- Implement timeouts
- Limit resource usage

**Warning Signs:**
- Code can read arbitrary files
- Network requests from generated code
- System crashes from bad code

**Phase to address:** Phase 3 (Execution service)

---

### Pitfall 6: Poor Error Messages

**Issue:** Cryptic errors when things go wrong
**Why it happens:** Focusing on success cases
**Impact:** Users can't recover, abandon tool
**Prevention:**
- Design error messages for mathematicians, not programmers
- Suggest next steps
- Explain what went wrong in context

**Warning Signs:**
- Stack traces shown to users
- "Something went wrong" messages
- Users asking "what do I do now?"

**Phase to address:** All phases

---

### Pitfall 7: Version Control Confusion

**Issue:** Generated code overwrites previous versions without history
**Why it happens:** Simple file write approach
**Impact:** Lost iterations, can't compare versions, can't revert
**Prevention:**
- Use git for algorithm versioning
- Store intermediate states
- Support branching/variants

**Warning Signs:**
- "Where did my previous version go?"
- Can't compare different approaches
- No way to undo changes

**Phase to address:** Phase 0 (Context manager)

---

### Pitfall 8: Over-Promising on Verification

**Issue:** Claiming to "verify correctness" when that's impossible
**Why it happens:** Verification sounds powerful
**Impact:** False confidence, missed bugs, user disappointment
**Prevention:**
- Be honest about verification limitations
- Distinguish "runs without error" from "mathematically correct"
- Encourage manual review

**Warning Signs:**
- "Verified correct" badges on unverified code
- Users trusting verification blindly
- Wrong results passing verification

**Phase to address:** Phase 4 (Verification service)

---

## Implementation-Specific Pitfalls

### Python Code Generation

- **Floating point assumptions:** Assuming math translates directly to floating-point operations
- **Mutability issues:** Not handling side effects correctly
- **Import management:** Missing imports or circular dependencies
- **Recursion depth:** Not handling deep recursion safely

### Mathematical Notation

- **Subtle notation differences:** Confusing similar symbols (vectors vs scalars)
- **Implicit assumptions:** Missing context from surrounding text
- **Ambiguous operations:** Operations that need clarification (matrix operations)
- **Domain-specific notation:** Notation varies by field

---
*Pitfalls research: 2025-03-29*
