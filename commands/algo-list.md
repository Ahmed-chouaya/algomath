---
description: "List all saved algorithms"
argument-hint: "[--detailed]"
tools:
  read: true
  write: false
---

<objective>
Display list of all saved algorithms with their status and basic info.
</objective>

<execution>
List algorithms by running:
```bash
npx algomath-extract algolist "$@"
```

Or if algomath-extract is installed globally:
```bash
algolist "$@"
```

This will:
1. Scan .algomath/algorithms/ directory
2. List all saved algorithms
3. Display status and basic info for each
</execution>

<process>
List algorithms:

1. **Scan Algorithms Directory**
   - Read .algomath/algorithms/
   - Find all algorithm folders

2. **Load Metadata**
   - Read metadata.json from each
   - Extract name, state, timestamps

3. **Display List**
   - Algorithm name
   - Current state
   - Step count
   - Last modified date
   - Status indicators

4. **Detailed View (if --detailed)**
   - Show full path
   - Show all files present
   - Show execution results
   - Show verification status

5. **Sort and Format**
   - Sort by last modified
   - Format as table or list
   - Color code by status
</process>

<examples>

**List algorithms:**
/algo-list

**Detailed list:**
/algo-list --detailed

</examples>

<next_steps>
/algo-extract - Create new algorithm
/algo-status - Check specific algorithm
</next_steps>
