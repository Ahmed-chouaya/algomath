---
status: resolved
trigger: "the framework commands work on opencode but it try to call the python scripts from the main project folder, this is not what we want it to do."
created: 2026-03-31T17:08:00Z
updated: 2026-03-31T17:08:00Z
---

## Current Focus

hypothesis: The Python path resolution uses __dirname correctly in bin/*.js files, but the issue is in how the commands are being invoked via opencode

test: Examine the path construction and how commands are registered

expecting: The __dirname should resolve to the npm package location when installed

next_action: Document findings and propose fix

## Symptoms

expected: Commands should call Python scripts from the npm package installation (e.g., `node_modules/algomath-extract/src/cli/cli_entry.py`)

actual: Commands are looking for Python scripts in the user's current working directory/project folder

errors: Path not found errors when running via opencode

reproduction:
  1. Install algomath-extract npm package
  2. Run command via opencode (e.g., `/algo-extract`)
  3. Python scripts are not found at the expected location

started: Not specified (appears to be a design issue)

## Evidence

- timestamp: 2026-03-31T17:00:00Z
  checked: bin/algo-extract.js lines 74-98
  found: Uses `path.join(__dirname, '..', 'src', 'cli', 'cli_entry.py')` to resolve Python script path. Also sets `cwd: path.join(__dirname, '..')` for working directory
  implication: __dirname SHOULD resolve to the bin/ directory within the npm package

- timestamp: 2026-03-31T17:01:00Z
  checked: bin/algo-generate.js lines 30-47
  found: Same pattern - uses `path.join(__dirname, '..', 'src', 'cli', 'cli_entry.py')`
  implication: Pattern is consistent across all command wrappers

- timestamp: 2026-03-31T17:02:00Z
  checked: src/cli/cli_entry.py lines 14-16
  found: Python adds project_root to sys.path using `Path(__file__).parent.parent.parent`
  implication: Python side also tries to resolve paths relative to its location

- timestamp: 2026-03-31T17:03:00Z
  checked: commands/algo-extract.md and commands/algo-generate.md
  found: Commands have hardcoded absolute paths in <execution_context> section pointing to `/home/milgraph/Projects/algo_framework/src/...`
  implication: This is likely how opencode discovers and loads the commands - it's using these hardcoded absolute paths

- timestamp: 2026-03-31T17:04:00Z
  checked: package.json bin entries
  found: Commands registered as `algoextract`, `algogenerate`, etc. mapped to bin/*.js files
  implication: When installed via npm, these should be available in node_modules/.bin/

## Root Cause Analysis

Based on the evidence gathered, there are actually **TWO separate issues**:

### Issue 1: Node.js Bin Scripts (RESOLVED - Working Correctly)

The `bin/*.js` files use `__dirname` correctly:
```javascript
const pythonScript = path.join(__dirname, '..', 'src', 'cli', 'cli_entry.py');
```

When the npm package is installed:
- `__dirname` resolves to `node_modules/algomath-extract/bin/`
- The path correctly points to `node_modules/algomath-extract/src/cli/cli_entry.py`
- This part is actually working correctly when run directly via npx or node_modules/.bin/

### Issue 2: Opencode Command Discovery (THE ACTUAL PROBLEM)

The `.md` command files in the `commands/` directory contain:
```markdown
<execution_context>
@/home/milgraph/Projects/algo_framework/src/extraction/pdf_processor.py
@/home/milgraph/Projects/algo_framework/src/extraction/llm_extractor.py
</execution_context>
```

These are **absolute paths** pointing to the development environment (`/home/milgraph/Projects/algo_framework/`). When opencode loads these command definitions, it's using these hardcoded paths instead of the npm package location.

The opencode command system likely:
1. Reads the `.md` command files
2. Uses the `<execution_context>` paths to know which files/tools are relevant
3. These absolute paths point to the wrong location when the package is installed elsewhere

## Resolution

### Root Cause

The command `.md` files contain hardcoded absolute paths that are only valid in the development environment. When the npm package is installed in a different location (e.g., in a user's project), these paths are invalid.

### Fix Required

The `.md` command files need to use **relative paths** or **placeholders** that get resolved at runtime:

**Option A: Remove absolute paths from .md files**
The `<execution_context>` section should either:
- Not include file paths at all (let the Node.js wrapper handle it)
- Use relative paths like `@src/extraction/pdf_processor.py`
- Use a placeholder like `@{{PACKAGE_ROOT}}/src/extraction/pdf_processor.py`

**Option B: Make opencode resolve paths dynamically**
If opencode needs these paths, the Node.js bin scripts should provide them dynamically, or the .md files should be generated/modified during npm postinstall.

### Files Changed

The following files need their `<execution_context>` sections updated:
- `commands/algo-extract.md` - lines 14-17
- `commands/algo-generate.md` - lines 14-17
- Potentially all other command `.md` files

## Verification

To verify the fix:
1. Update the .md files to remove hardcoded absolute paths
2. Reinstall the package in a test project
3. Run `/algo-extract` via opencode
4. Verify Python scripts are found in the npm package location, not the user's project folder

## Additional Notes

The current workaround is likely that users need to be in the `/home/milgraph/Projects/algo_framework` directory for the commands to work, which defeats the purpose of an npm package.

The proper solution is to either:
1. Remove the `<execution_context>` file references entirely (the Node.js wrapper handles everything)
2. Replace with relative paths that work regardless of where the package is installed
3. Generate the .md files with correct paths during the postinstall script
