---
description: "Execute generated Python code"
argument-hint: "[--skip] [--timeout <seconds>]"
tools:
  read: true
  write: true
---

<objective>
Execute generated Python code in a safe sandboxed environment.
Captures stdout, stderr, and execution results.
</objective>


<process>
Execute code in sandbox:

1. **Load Generated Code**
   - Read generated.py from current algorithm
   - Validate code exists
   - Check syntax

2. **Create Sandbox**
   - Create isolated temp directory
   - Copy code to sandbox
   - Set resource limits

3. **Execute Code**
   - Run in subprocess with timeout (default 30s)
   - Capture stdout and stderr
   - Monitor resource usage
   - Handle exceptions

4. **Process Results**
   - Capture output
   - Record execution time
   - Check for errors
   - Format results

5. **Save Results**
   - Write to execution.log
   - Update metadata.json
   - Update state to EXECUTION_COMPLETE

6. **Display Results**
   - Show output
   - Show execution time
   - Show status (success/error)
   - Suggest next steps
</process>

<examples>

**Execute code:**
/algo-run

**Skip execution:**
/algo-run --skip

**Custom timeout:**
/algo-run --timeout 60

</examples>

<options>

--skip
Skip execution and proceed directly to verification

--timeout <seconds>
Maximum execution time (default: 30)

</options>

<next_steps>
/algo-verify - Verify execution results
/algo-status - Check algorithm state
</next_steps>
