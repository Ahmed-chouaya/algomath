---
description: "Verify execution results and explain algorithm behavior"
argument-hint: "[--step <N>] [--detailed] [--diagnostic] [--expected <value>]"
tools:
  read: true
  write: true
  Bash: true
---

<objective>
Verify execution results, compare to expected values, explain algorithm behavior,
and identify potential edge cases.
</objective>

<execution>
Execute verification by running:

**Option 1 - Using npx (no install required):**
```bash
npx -p algomath-extract algoverify "$@"
```

**Option 2 - If installed globally:**
```bash
algoverify "$@"
```

**Option 3 - If installed locally in project:**
```bash
./node_modules/.bin/algoverify "$@"
```

This will:
1. Load execution results and algorithm steps
2. Verify correctness against expected values
3. Generate explanation of algorithm behavior
4. Identify edge cases and potential issues
</execution>

<process>
Execute verification workflow:


1. **Load Execution Results**
- Read execution.log
- Load algorithm steps
- Check execution status

2. **Check Results**
- Compare output to expected
- Validate return codes
- Check for errors
- Verify output format

3. **Generate Explanation**
- Explain what the algorithm does
- Describe each step
- Show data flow
- Explain mathematical concepts

4. **Identify Edge Cases**
- Empty inputs
- Single element
- Maximum values
- Boundary conditions
- Error conditions

5. **Suggest Tests**
- Propose test cases
- Suggest inputs to try
- Recommend validations

6. **Display Summary**
- Show verification status
- Display explanation
- List edge cases
- Suggest improvements
</process>

<examples>

**Verify current algorithm:**
/algo-verify

**Verify specific step:**
/algo-verify --step 5

**Detailed verification:**
/algo-verify --detailed

**Diagnostic mode:**
/algo-verify --diagnostic

**Compare to expected:**
/algo-verify --expected "[1, 2, 3]"

</examples>

<options>

--step <N>
Explain specific step number

--detailed
Show detailed verification

--diagnostic
Run diagnostic checks

--expected <value>
Compare to expected output

</options>

<next_steps>
/algo-status - Check current state
/algo-list - View all algorithms
</next_steps>
