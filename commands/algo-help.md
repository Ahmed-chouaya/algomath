---
description: "Show help and available commands"
argument-hint: "[command]"
tools:
  read: true
  write: false
---

<objective>
Display help information, available commands, and usage examples.
</objective>

<execution>
Show help by running:
```bash
npx algomath-extract algohelp "$@"
```

Or if algomath-extract is installed globally:
```bash
algohelp "$@"
```

This will display:
1. Available commands and their descriptions
2. Usage examples
3. Workflow information
</execution>

<process>
Display help:

1. **Show Welcome Banner**
   - AlgoMath logo/name
   - Version
   - Brief description

2. **List Commands**
   - /algo-extract - Extract from PDF/text
   - /algo-generate - Generate Python code
   - /algo-run - Execute code
   - /algo-verify - Verify results
   - /algo-status - Check current state
   - /algo-list - List saved algorithms
   - /algo-help - This help

3. **Show Workflow**
   ```
   PDF/Text → Extract → Generate → Run → Verify
   ```

4. **Show Examples**
   - Basic usage
   - Common flags
   - Tips

5. **Show Documentation Links**
   - User guide
   - Examples
   - Troubleshooting
</process>

<examples>

**Show general help:**
/algo-help

**Show help for specific command:**
/algo-help extract

</examples>

<next_steps>
/algo-extract - Start with a new algorithm
</next_steps>
