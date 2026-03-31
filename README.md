```
    █████╗ ██╗      ██████╗  ██████╗ ███╗   ███╗ █████╗ ████████╗██╗  ██╗
   ██╔══██╗██║     ██╔════╝ ██╔═══██╗████╗ ████║██╔══██╗╚══██╔══╝██║  ██║
   ███████║██║     ██║  ███╗██║   ██║██╔████╔██║███████║   ██║   ███████║
   ██╔══██║██║     ██║   ██║██║   ██║██║╚██╔╝██║██╔══██║   ██║   ██╔══██║
   ██║  ██║███████╗╚██████╔╝╚██████╔╝██║ ╚═╝ ██║██║  ██║   ██║   ██║  ██║
   ╚═╝  ╚═╝╚══════╝ ╚═════╝  ╚═════╝ ╚═╝     ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝
```

# AlgoMath Framework

**AlgoMath** transforms mathematical algorithm descriptions from PDFs and text files into executable Python code through an intuitive workflow integrated with opencode.

**Core Value:** Mathematicians can reliably convert complex algorithmic descriptions from research papers into correct, reproducible, executable code with minimal manual intervention.

---

## Installation

### Quick Install (Recommended)
```bash
# Global install (no sudo needed)
sudo npx algomath-extract@latest
```

The interactive installer will:
1. Check for Python 3.11+ (auto-install guidance if missing)
2. Ask which runtime to install to (OpenCode, Claude Code, or both)
3. Ask for installation location (global or local)
4. Install Python dependencies (pdfplumber, pydantic)
5. Copy command files to the selected runtime

> **Note:** Use `sudo` when installing globally or locally if your `.opencode` directory was previously created with elevated permissions.

### Manual Install
```bash
# Global install
sudo npm install -g algomath-extract

# Or local install per-project
npm install algomath-extract
```

---

## Quick Start

### 1. Extract Algorithm from PDF
```bash
/algo-extract research_paper.pdf
```
This will:
- Extract text from the PDF
- Parse the algorithm using LLM
- Structure it into steps
- Save to `.algomath/algorithms/{name}/`

### 2. Generate Python Code
```bash
/algo-generate
```
Generates executable Python code with:
- Type hints for mathematical clarity
- Docstrings explaining the algorithm
- Executable code from structured steps

### 3. Execute Code
```bash
/algo-run
```
Safely executes in sandboxed environment with:
- Timeout protection (30s default)
- Output capture
- Error handling

### 4. Verify Results
```bash
/algo-verify
```
Verifies correctness with:
- Execution status check
- Algorithm explanation
- Edge case detection

---

## Available Commands

| Command | Purpose | Mode |
|---------|---------|------|
| `/algo-extract <file>` | Extract algorithm from PDF/text | Interactive |
| `/algo-generate` | Generate Python code | Auto |
| `/algo-run` | Execute code | Auto |
| `/algo-verify` | Verify results | Interactive |
| `/algo-status` | Show current state | Info |
| `/algo-list` | List saved algorithms | Info |
| `/algo-help` | Show help | Info |

### CLI Commands (via npm)

After installation, you can also use these CLI commands:

| Command | Description |
|---------|-------------|
| `npx algoextract <file>` | Extract from command line |
| `npx algogenerate` | Generate code from CLI |
| `npx algorun` | Run from CLI |
| `npx algoverify` | Verify from CLI |
| `npx algostatus` | Check status |
| `npx algolist` | List algorithms |
| `npx algohelp` | Show help |

---

## Workflow Modes

### Step-by-Step (Default)
```bash
/algo-extract research.pdf
```
- Prompts at each stage
- Shows extracted text for review
- Shows structured steps for editing
- User controls the process

### Auto Mode
```bash
/algo-extract --auto research.pdf
```
- Extracts without prompts
- Saves automatically
- Fastest path

### Step Explanation
```bash
/algo-verify --step 3
```
Explains step 3 in detail.

---

## Architecture

```
PDF/Text → Extract → Steps → Generate → Code → Run → Verify
    │         │         │          │        │      │
    │         │         │          │        │      └─ Explanation
    │         │         │          │        │         Edge cases
    │         │         │          │        └─ Sandbox execution
    │         │         │          │           Output capture
    │         │         │          └─ Python generation
    │         │         │             Type hints
    │         │         │             Docstrings
    │         │         └─ LLM parsing
    │         │            Mathematical notation
    │         └─ Text extraction
    │            PDF/Text files
    │            Auto-detection
    └─ Your research paper
```

---

## Features

### PDF Processing
- Extracts text from text-based PDFs
- Supports `.txt`, `.md` files
- Auto-detects file type
- Handles encoding issues

### Algorithm Extraction
- LLM-powered parsing
- Identifies inputs, outputs, steps
- Handles mathematical notation
- Supports loops, conditionals, assignments

### Code Generation
- Template-based (fast, reliable)
- LLM-enhanced (for complex expressions)
- Type hints included
- Docstrings explain algorithm
- Standard library only

### Safe Execution
- Subprocess isolation
- Timeout protection (30s default)
- Resource limits
- No filesystem escape
- Output capture

### Verification
- Execution status check
- Results comparison
- Natural language explanation
- Edge case detection
- Diagnostic mode for failures

---

## Directory Structure

```
.algomath/
├── algorithms/
│   └── {algorithm-name}/
│       ├── metadata.json       # Algorithm info
│       ├── source.txt          # Original text
│       ├── steps.json          # Structured steps
│       ├── generated.py        # Python code
│       ├── execution.log       # Run results
│       └── verification.log    # Verification
└── context.py                  # State management
```

---

## State Machine

```
IDLE → EXTRACTED → STEPS → CODE → EXECUTED → VERIFIED
```

- Resume from any state
- Multiple algorithms in progress
- Git versioning per algorithm
- Cross-session persistence

---

## Dependencies

### Python
- Python 3.11+
- pdfplumber (PDF text extraction)
- pydantic (data validation)

### Node.js (for installer)
- chalk (terminal colors)
- inquirer (interactive prompts)
- commander (CLI framework)

---

## Example

```bash
# Extract from paper
/algo-extract "research_paper.pdf" --name "dijkstra"

# Review extracted steps
/algo-status

# Generate code
/algo-generate

# Run the algorithm
/algo-run

# Verify it worked
/algo-verify

# Done!
```

---

## Configuration

Set in `.algomath/config.json`:

```json
{
  "mode": "step-by-step",
  "timeout": 30,
  "parallel": true
}
```

---

## License

MIT License - see LICENSE file

---

**AlgoMath** - Making algorithm implementation reliable.
