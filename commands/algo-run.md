---
description: "Execute generated Python code"
argument-hint: "[--skip] [--timeout <seconds>]"
tools:
  read: true
  write: true
  Bash: true
---

<objective>
Execute generated Python code in a safe sandboxed environment.
Captures stdout, stderr, and execution results.
</objective>

<execution>
Execute the generated code by running:

**Option 1 - Using npx (no install required):**
```bash
npx -p algomath-extract algorun "$@"
```

**Option 2 - If installed globally:**
```bash
algorun "$@"
```

**Option 3 - If installed locally in project:**
```bash
./node_modules/.bin/algorun "$@"
```

This will:
1. Load the generated Python code
2. Execute in a sandboxed environment
3. Capture output and results
4. Display execution summary
</execution>

<process>
Execute code in sandbox:


1. **Load Generated Code**
- Read generated.py from current algorithm
- Validate code exists
- Check for syntax errors

2. **Prepare Execution**
- Create isolated sandbox
- Set resource limits
- Prepare input data
- Set timeout (default: 30s)

3. **Execute Code**
- Run in subprocess
- Capture stdout/stderr
- Monitor execution
- Handle timeouts

4. **Capture Results**
- Save output to execution.log
- Capture return code
- Record execution time
- Store any generated files

5. **Display Results**
- Show stdout
- Show stderr (if any)
- Display execution time
- Show success/failure status
</process>

<examples>

**Execute current algorithm:**
/algo-run

**Execute with custom timeout:**
/algo-run --timeout 60

**Skip execution (for testing):**
/algo-run --skip

</examples>

<options>

--skip
Skip execution, just validate

--timeout <seconds>
Set execution timeout (default: 30)

</options>

<next_steps>
/algo-verify - Verify execution results
/algo-status - Check current state
</next_steps>
