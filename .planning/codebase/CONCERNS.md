# Codebase Concerns

**Analysis Date:** 2025-03-29

## Tech Debt

**Multi-platform duplication:**
- Issue: Same files replicated across .claude/, .github/, .opencode/, .cursor/, etc.
- Files: All platform directories contain similar agent/workflow files
- Why: Each AI assistant platform needs its own directory structure
- Impact: Updates must be made in multiple places, risk of divergence
- Fix approach: Consider symlinks or single source of truth with build step

**Minimal package.json:**
- Issue: `.claude/package.json` contains only `{"type":"commonjs"}`
- Why: Placeholder for future expansion
- Impact: No dependency management, no scripts
- Fix approach: Add proper metadata if this becomes installable package

## Known Bugs

**None identified** - Framework is documentation-based, no runtime code

## Security Considerations

**File permissions:**
- Risk: gsd-tools.cjs has execute permissions
- Current mitigation: Standard file system permissions
- Recommendations: Review permissions if distributed

**Path traversal:**
- Risk: CLI tools accept file paths
- Current mitigation: Path validation in tools
- Recommendations: Continue validating all paths

## Performance Bottlenecks

**None identified** - No runtime execution

## Fragile Areas

**Cross-platform consistency:**
- Issue: 6 platform directories must stay synchronized
- Common failures: Updates made to one platform not propagated
- Safe modification: Update all platform files simultaneously
- Test coverage: No automated sync verification

**Template references:**
- Issue: Hardcoded paths in workflow files
- File: `workflows/*.md` contain absolute paths
- Why: Workflows need concrete file locations
- Impact: Breaks if directory structure changes
- Fix approach: Use relative references or path variables

## Scaling Limits

**Repository size:**
- Current: ~2MB (mostly documentation)
- Limit: GitHub repo size limits (2GB soft limit)
- Scaling path: Split into packages if grows

## Dependencies at Risk

**Node.js version:**
- Risk: Framework requires Node.js for CLI tools
- Impact: Compatibility with future Node versions
- Migration plan: Keep tools simple, avoid deprecated APIs

## Missing Critical Features

**Automated testing:**
- Problem: No automated test suite for workflows
- Current workaround: Manual execution testing
- Blocks: No CI/CD validation
- Implementation complexity: Medium (need workflow test harness)

**Version management:**
- Problem: No semantic versioning for framework
- Current workaround: Git commits track changes
- Blocks: Can't specify framework version dependencies
- Implementation complexity: Low (add VERSION file)

## Test Coverage Gaps

**Workflow integration:**
- What's not tested: Cross-workflow interactions
- Risk: Workflows may break each other's assumptions
- Priority: Medium
- Difficulty to test: Need integration test framework

**Template rendering:**
- What's not tested: All template variations
- Risk: Templates may have undiscovered edge cases
- Priority: Low
- Difficulty to test: Exhaustive template testing needed

---

*Concerns audit: 2025-03-29*
*Update as issues are fixed or new ones discovered*
