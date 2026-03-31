---
description: "Verify execution results and explain algorithm behavior"
argument-hint: "[--step <N>] [--detailed] [--diagnostic] [--expected <value>]"
tools:
  read: true
  write: true
---

<objective>
Verify execution results, compare to expected values, explain algorithm behavior,
and identify potential edge cases.
</objective>

<execution_context>
@/home/milgraph/Projects/algo_framework/src/verification/checker.py
@/home/milgraph/Projects/algo_framework/src/verification/explainer.py
@/home/milgraph/Projects/algo_framework/src/verification/edge_cases.py
</execution_context>

<process>
Execute verification workflow:

1. **Load Execution Results**
   - Read execution.log
   - Load algorithm steps
   - Get generated code

2. **Verify Execution**
   - Check if execution succeeded
   - Verify no errors
   - Validate output present

3. **Compare Results (if --expected)**
   - Compare actual vs expected output
   - Support numeric tolerance for floats
   - Show differences

4. **Generate Explanation**
   - Brief mode: 1-2 sentence summary
   - Detailed mode: Step-by-step walkthrough
   - Step mode: Explain specific step N

5. **Detect Edge Cases**
   - Empty inputs
   - Boundary values
   - Division by zero
   - Array bounds
   - Infinite loops

6. **Diagnostic Mode (if failed)**
   - Analyze error
   - Suggest fixes
   - Explain failure point

7. **Save Report**
   - Write to verification.log
   - Update state to VERIFIED

8. **Display Summary**
   - Execution status
   - Explanation
   - Edge cases found
   - Next steps
</process>

<examples>

**Verify results:**
/algo-verify

**Explain specific step:**
/algo-verify --step 3

**Detailed explanation:**
/algo-verify --detailed

**Compare with expected:**
/algo-verify --expected "42"

**Diagnostic for failed runs:**
/algo-verify --diagnostic

</examples>

<options>

--step <N>
Explain step number N in detail

--detailed
Show detailed step-by-step explanation

--diagnostic
Run diagnostic mode for failed executions

--expected <value>
Expected output for comparison

</options>

<next_steps>
/algo-extract - Start with new algorithm
/algo-status - Check current state
</next_steps>
