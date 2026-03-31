# AlgoMath Framework Design Document

**Version:** 0.1.0  
**Last Updated:** 2025-03-29  
**Status:** Design Complete, Ready for Implementation

---

## 1. Overview

### 1.1 Purpose
AlgoMath is an agentic framework that transforms AI coding assistants into a reliable mathematical problem-solving environment. It provides structured workflows for converting algorithms described in academic papers into correct, reproducible, executable code.

### 1.2 Core Value
Mathematicians can reliably convert complex algorithmic descriptions from academic papers into correct, reproducible, executable code with minimal back-and-forth iterations.

### 1.3 Target Users
- **Primary:** Mathematicians working with academic papers
- **Technical Level:** Non-technical users focused on mathematics, not AI management
- **Goal:** Reliable translation from paper to working code

### 1.4 Key Principles
1. **No Free-Form Chat:** All problem-solving follows structured workflows
2. **Controlled Execution:** Execution is predictable and reproducible
3. **Reduced Ambiguity:** Clear state tracking and progress indicators
4. **Accessibility:** Simple experience for non-technical users
5. **Persistence:** Named algorithms with version control

---

## 2. Core Architecture

### 2.1 System Components

```
User Input → Intent Detection → Workflow Router → Workflow Execution → State Update
     ↑                                                              ↓
     └←←←←←←←←←←←←←←←←← Context Manager ←←←←←←←←←←←←←←←←←←←←←←←┘
```

**Components:**
1. **Intent Detection Module** — Classifies user input into workflow intent
2. **Workflow Router** — Routes to appropriate workflow based on intent
3. **Workflow Engine** — Executes specific workflows (Extract, Generate, Execute, Verify)
4. **Context Manager** — Maintains state across all workflows
5. **Persistence Layer** — File-based storage with automatic git versioning

### 2.2 State Management

**Workflow States:**
```
IDLE → TEXT_EXTRACTED → STEPS_STRUCTURED → CODE_GENERATED → EXECUTION_COMPLETE → VERIFIED
```

**Flexible Branching:**
- User can navigate between any states
- Forward transitions require data existence
- Backward transitions always allowed (for editing)
- State persists across sessions

### 2.3 Data Flow

```
1. User provides mathematical text
   ↓
2. Extraction Workflow → Structured steps (JSON)
   ↓
3. Generation Workflow → Python code
   ↓
4. Execution Workflow → Results (stdout, stderr, status)
   ↓
5. Verification Workflow → Validation report
```

---

## 3. The Four Core Workflows

### 3.1 Extraction Workflow

**Purpose:** Parse mathematical descriptions into structured algorithm steps

**Trigger:**
- Slash command: `/algo-extract [name]`
- Natural language: "Extract the algorithm from this text"

**Input:**
- Mathematical text describing algorithm
- Optional: Algorithm name for persistence

**Process:**
1. Prompt user for mathematical text
2. Parse text to identify:
   - Algorithm name (if not provided)
   - Input parameters
   - Output/return value
   - Step-by-step procedure
3. Convert to structured JSON format
4. Validate structure
5. Present extracted steps for review

**Output:**
- Algorithm metadata (name, description)
- Structured steps (JSON format)
- State: TEXT_EXTRACTED

**JSON Structure:**
```json
{
  "name": "algorithm_name",
  "description": "What this algorithm does",
  "inputs": [
    {"name": "n", "type": "int", "description": "Input size"}
  ],
  "outputs": [
    {"name": "result", "type": "float", "description": "Computed value"}
  ],
  "steps": [
    {
      "id": 1,
      "type": "initialize",
      "variables": [
        {"name": "sum", "value": "0", "type": "float"}
      ]
    },
    {
      "id": 2,
      "type": "loop",
      "iterator": "i",
      "range": {"start": "1", "end": "n"},
      "body": [
        {"id": 3, "type": "assignment", "target": "sum", "expression": "sum + i"}
      ]
    },
    {
      "id": 4,
      "type": "return",
      "value": "sum"
    }
  ],
  "complexity": {
    "time": "O(n)",
    "space": "O(1)"
  }
}
```

**Success Criteria:**
- ✓ Algorithm boundaries correctly identified
- ✓ Inputs and outputs extracted
- ✓ Steps are structured and unambiguous
- ✓ User can review and edit before proceeding

---

### 3.2 Generation Workflow

**Purpose:** Convert structured algorithm steps into executable Python code

**Trigger:**
- Slash command: `/algo-generate`
- Natural language: "Generate the code" or "Turn this into Python"

**Input:**
- Structured steps from extraction (JSON)

**Process:**
1. Load structured steps from context
2. Map steps to Python constructs:
   - Initialize → Variable assignments
   - Loop → for/while statements
   - Conditional → if/elif/else
   - Assignment → Variable updates
   - Return → return statement
3. Generate Python code with:
   - Type hints for clarity
   - Docstrings explaining algorithm
   - Comments for each step
   - Input validation
4. Present code for review
5. Validate syntax

**Output:**
- Python code (executable)
- State: CODE_GENERATED

**Example Output:**
```python
"""
Calculate the sum of first n natural numbers.

This algorithm iterates from 1 to n and accumulates the sum.
Time complexity: O(n)
Space complexity: O(1)
"""

def calculate_sum(n: int) -> int:
    """
    Calculate sum of first n natural numbers.
    
    Args:
        n: The number of terms to sum
        
    Returns:
        The sum of first n natural numbers
        
    Raises:
        ValueError: If n is negative
    """
    if n < 0:
        raise ValueError("n must be non-negative")
    
    # Initialize sum
    total: int = 0
    
    # Loop from 1 to n
    for i in range(1, n + 1):
        total += i
    
    return total
```

**Success Criteria:**
- ✓ Code is syntactically correct
- ✓ Includes type hints
- ✓ Includes docstrings
- ✓ Handles edge cases
- ✓ User can review before execution

---

### 3.3 Execution Workflow

**Purpose:** Execute generated code safely and capture results

**Trigger:**
- Slash command: `/algo-run [inputs]`
- Natural language: "Run it" or "Execute the code"

**Input:**
- Generated Python code
- Optional: Input values for algorithm parameters

**Process:**
1. Load generated code from context
2. Set up sandboxed execution environment:
   - Restricted file system access
   - Timeout protection (30 seconds default)
   - Memory limits
   - No network access
3. Parse input values (if provided)
4. Execute code in subprocess
5. Capture:
   - stdout
   - stderr
   - Execution time
   - Return value
   - Status (success/failure)
6. Store results

**Output:**
- Execution results:
  ```json
  {
    "status": "success",
    "stdout": "Result: 15\n",
    "stderr": "",
    "return_value": 15,
    "execution_time": 0.001,
    "timestamp": "2025-03-29T12:00:00"
  }
  ```
- State: EXECUTION_COMPLETE

**Error Handling:**
- Syntax errors → Show line and suggestion
- Runtime errors → Show traceback and explanation
- Timeout errors → Explain and suggest optimization
- Security violations → Block and report

**Success Criteria:**
- ✓ Code runs in sandboxed environment
- ✓ Output captured correctly
- ✓ Errors handled gracefully
- ✓ Execution time recorded
- ✓ User sees clear results

---

### 3.4 Verification Workflow

**Purpose:** Verify execution correctness and explain results

**Trigger:**
- Slash command: `/algo-verify`
- Natural language: "Is this correct?" or "Verify the result"

**Input:**
- Original algorithm description
- Structured steps
- Generated code
- Execution results

**Process:**
1. Verify code ran without errors
2. Check if results match expected behavior (if expected provided)
3. Analyze code for:
   - Correctness of implementation
   - Edge cases
   - Potential issues
   - Optimization opportunities
4. Generate explanation:
   - What the algorithm did
   - Step-by-step execution trace
   - Why the result is correct (or not)
5. Suggest test cases
6. Present verification report

**Output:**
- Verification report:
  ```
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ALGO ► VERIFICATION
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  
  Status: ✓ PASSED
  
  Execution Summary:
  - Input: n=5
  - Expected: Sum of 1+2+3+4+5 = 15
  - Actual: 15
  - Match: ✓
  
  Step-by-Step Trace:
  1. Initialized total = 0
  2. Loop iteration 1: total = 0 + 1 = 1
  3. Loop iteration 2: total = 1 + 2 = 3
  ...
  6. Return total = 15
  
  Correctness Analysis:
  ✓ Algorithm correctly implements sum formula
  ✓ Edge cases handled (n=0 returns 0)
  ✓ No integer overflow issues for reasonable n
  
  Suggested Test Cases:
  - n = 0 (edge case)
  - n = 1 (minimum)
  - n = 100 (typical)
  - n = -1 (error case)
  
  Verification: ██████████ 100%
  ```
- State: VERIFIED

**Success Criteria:**
- ✓ Confirms execution succeeded
- ✓ Can compare against expected results
- ✓ Provides clear explanation
- ✓ Identifies edge cases
- ✓ Suggests additional tests

---

## 4. Command Interface

### 4.1 Slash Commands

All commands follow pattern: `/algo-<command>`

| Command | Description | Usage |
|---------|-------------|-------|
| `/algo-extract [name]` | Extract algorithm from text | `/algo-extract "Dijkstra"` |
| `/algo-generate` | Generate Python code | `/algo-generate` |
| `/algo-run [inputs]` | Execute generated code | `/algo-run n=5` |
| `/algo-verify` | Verify execution | `/algo-verify` |
| `/algo-status` | Show current state | `/algo-status` |
| `/algo-list` | List saved algorithms | `/algo-list` |
| `/algo-help` | Show help | `/algo-help` |

### 4.2 Orchestrator Modes

**Auto Mode:**
- User selects mode at session start
- Full workflow automation: Extract → Generate → Run → Verify
- Pauses at checkpoints for user review

**Step-by-Step Mode:**
- User manually triggers each workflow
- Full control over progression
- Can edit at any point

### 4.3 Natural Language Support

**Intent Detection:**
- "Extract this algorithm" → /algo-extract
- "Generate the code" → /algo-generate
- "Run it" → /algo-run
- "Is this correct?" → /algo-verify

**Confidence Thresholds:**
- >0.8: Execute directly
- 0.5-0.8: Confirm with user
- <0.5: Ask for clarification

---

## 5. State Management

### 5.1 Context Structure

```python
{
  "current_algorithm": "algorithm_name",
  "current_state": "code_generated",
  "data": {
    "text": "original mathematical text",
    "steps": [...],
    "code": "generated python code",
    "results": {...}
  },
  "created_at": "2025-03-29T12:00:00",
  "updated_at": "2025-03-29T12:05:00"
}
```

### 5.2 Storage Locations

- **Session state:** `.algomath/session.json`
- **Named algorithms:** `.algomath/algorithms/{name}/algorithm.json`
- **Version history:** Git commits (automatic)

### 5.3 Persistence Strategy

**Named Algorithms:**
- Saved to `.algomath/algorithms/{name}/`
- Auto-committed to git
- Can be resumed across sessions
- Support version history

**Session-Only:**
- Stored in `.algomath/session.json`
- Cleared on new unnamed session
- Not persisted to git
- For quick experiments

### 5.4 Progress Indicators

**Progress Bar:**
```
Extract: ██████████░░ 40%
```

**State Display:**
```
[IDLE] → [TEXT_EXTRACTED] → [STEPS_STRUCTURED] → [CODE_GENERATED] → [EXECUTION_COMPLETE] → [VERIFIED]
```

---

## 6. Data Formats

### 6.1 Algorithm JSON Schema

```json
{
  "$schema": "algomath/algorithm-v1",
  "name": "string (required)",
  "description": "string",
  "inputs": [
    {
      "name": "string",
      "type": "int|float|string|list|dict",
      "description": "string",
      "optional": false
    }
  ],
  "outputs": [
    {
      "name": "string",
      "type": "int|float|string|list|dict",
      "description": "string"
    }
  ],
  "steps": [
    {
      "id": "integer",
      "type": "initialize|loop|condition|assignment|return|call",
      "description": "string"
    }
  ],
  "complexity": {
    "time": "string",
    "space": "string"
  }
}
```

### 6.2 Execution Results JSON

```json
{
  "status": "success|error|timeout",
  "stdout": "string",
  "stderr": "string",
  "return_value": "any",
  "execution_time": "float (seconds)",
  "timestamp": "ISO8601"
}
```

---

## 7. Error Handling

### 7.1 Error Categories

1. **Syntax Errors**
   - Detection: During generation
   - Response: Show error, suggest fix

2. **Runtime Errors**
   - Detection: During execution
   - Response: Capture traceback, explain

3. **Validation Errors**
   - Detection: During verification
   - Response: Show mismatch, explain

4. **State Errors**
   - Detection: When trying invalid transition
   - Response: Show valid next steps

### 7.2 Recovery Strategies

- **Partial Results:** Save what worked, allow retry from that point
- **Rollback:** Restore to previous state
- **Edit Mode:** Allow modification and re-execution

---

## 8. Security Considerations

### 8.1 Sandboxed Execution

- **File System:** Restricted to project directory
- **Network:** No external access
- **Time:** 30-second timeout default
- **Memory:** Reasonable limits (e.g., 512MB)

### 8.2 Input Sanitization

- Validate algorithm names (no special chars)
- Limit text input size (e.g., 10MB)
- Check for malicious patterns
- Escape special characters in outputs

---

## 9. Implementation Phases

### Phase 1: Foundation (Current)
- Context manager and state persistence
- Workflow engine and command interface
- Basic test infrastructure

### Phase 2: Extraction
- Intelligent algorithm parsing
- Mathematical notation handling
- Ambiguity resolution

### Phase 3: Generation
- Code generation from JSON
- Type hints and docstrings
- Optimization suggestions

### Phase 4: Execution
- Sandboxed execution
- Result capture
- Error handling

### Phase 5: Verification
- Correctness checking
- Explanation generation
- Test case suggestions

---

## 10. Success Metrics

### 10.1 User Experience
- Time from text to working code: <5 minutes
- Number of iterations: <3 on average
- User satisfaction: >4/5

### 10.2 Technical
- Extraction accuracy: >90%
- Code generation correctness: >95%
- Execution success rate: >98%

### 10.3 Reliability
- State persistence: 100%
- Version control: All changes tracked
- Recovery rate: >95% from interruptions

---

## 11. Future Enhancements (v2+)

- Multi-algorithm detection in single text
- Advanced ambiguity resolution
- Alternative implementation options
- Property-based testing
- Complexity analysis
- Export as Python package
- Collaborative features
- Integration with external systems (Wolfram, MATLAB)

---

## 12. Implementation Status

**Completed:**
- ✓ Project initialization
- ✓ Requirements definition
- ✓ Roadmap creation (5 phases)
- ✓ Phase 1 context gathering
- ✓ Plan 01-01: Context Manager (implemented)
- ✓ Phase 1 planning (3 plans)

**In Progress:**
- Plan 01-02: Workflow Engine (current)
- Plan 01-03: Test Suite (pending)

**Pending:**
- Phase 2-5: Feature implementation
- Verification and testing
- Documentation

---

*Design Document v0.1.0*
*AlgoMath Framework*
*2025-03-29*
