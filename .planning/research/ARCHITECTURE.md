# Architecture Research: AlgoMath

**Research Date:** 2025-03-29

## System Components

### Workflow Engine
- **Purpose:** Route user requests to appropriate workflow
- **Responsibilities:**
  - Detect user intent from natural language
  - Maintain workflow state
  - Orchestrate transitions between workflows
  - Handle interruptions and context switching

### Extraction Service
- **Purpose:** Parse mathematical descriptions into structured steps
- **Responsibilities:**
  - Identify algorithm boundaries
  - Extract algorithm inputs/outputs
  - Parse mathematical notation
  - Generate step-by-step breakdown
- **Input:** Raw mathematical text
- **Output:** Structured algorithm representation (JSON/Markdown)

### Code Generation Service
- **Purpose:** Convert structured algorithm to executable code
- **Responsibilities:**
  - Map algorithm steps to Python constructs
  - Generate type hints
  - Add documentation
  - Handle edge cases
- **Input:** Structured algorithm
- **Output:** Python code file

### Execution Service
- **Purpose:** Run generated code safely
- **Responsibilities:**
  - Sandboxed execution environment
  - Capture output and errors
  - Resource limits (time, memory)
  - Input injection if needed
- **Input:** Python code
- **Output:** Execution results (stdout, stderr, return code)

### Verification Service
- **Purpose:** Validate results and provide explanations
- **Responsibilities:**
  - Check output correctness
  - Compare against expected results
  - Explain algorithm behavior
  - Identify potential issues
- **Input:** Execution results, expected output (optional)
- **Output:** Verification report

### Context Manager
- **Purpose:** Maintain state across workflows
- **Responsibilities:**
  - Store current text, steps, code, results
  - Version control for algorithm iterations
  - Persistence across sessions
- **Storage:** File-based (.planning/ or project directory)

## Data Flow

```
User Request
    ↓
[Intent Detection] → Route to workflow
    ↓
[Extraction Workflow]
    ↓
Raw Text → Structured Steps
    ↓
[Generation Workflow]
    ↓
Structured Steps → Python Code
    ↓
[Execution Workflow]
    ↓
Python Code → Results
    ↓
[Verification Workflow]
    ↓
Results → Verification/Explanation
    ↓
User
```

## State Management

**Session State:**
```json
{
  "current_text": "...",
  "extracted_steps": [...],
  "generated_code": "...",
  "last_result": "...",
  "workflow_history": [...]
}
```

**Persistence:**
- File-based storage in `.planning/` or similar
- JSON format for structured data
- Markdown for human-readable content
- Git-tracked for version history

## Integration Points

**AI Assistant Integration:**
- Commands/workflows triggered via slash commands
- Natural language intent detection
- Rich output formatting (banners, tables)

**Python Environment:**
- Local Python interpreter
- Virtual environment support
- Package management via pip/requirements.txt

## Security Considerations

**Sandboxed Execution:**
- Restricted file system access
- No network access from generated code
- CPU/memory limits
- Timeout protection

**Input Validation:**
- Sanitize user-provided text
- Validate algorithm structure
- Check for malicious patterns

## Build Order

1. **Workflow Engine** — Foundation for all other components
2. **Context Manager** — Needed for state persistence
3. **Extraction Service** — First user-facing workflow
4. **Code Generation Service** — Depends on extraction output
5. **Execution Service** — Depends on generated code
6. **Verification Service** — Depends on execution results

---
*Architecture research: 2025-03-29*
