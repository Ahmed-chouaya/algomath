# External Integrations

**Analysis Date:** 2025-03-29

## APIs & External Services

**AI Model APIs:**
- No direct API calls from this framework
- Relies on AI assistant's built-in capabilities
- Models configured via `.planning/config.json` (model_profile setting)

**Web Search (Optional):**
- Framework supports web search via external APIs
- Services: Brave Search, Firecrawl, Exa (detected in codebase)
- Configuration: Via environment or config
- Usage: Research phase for gathering domain knowledge

## Data Storage

**Databases:**
- None - This is a documentation framework
- All state stored in markdown files

**File Storage:**
- Local filesystem only
- `.planning/` directory for project state
- Git for version control

**Caching:**
- None - Stateless by design

## Authentication & Identity

**Auth Provider:**
- None required
- Framework runs in user's local environment
- No user authentication in this context

## Monitoring & Observability

**Error Tracking:**
- None - Framework is documentation-based
- Errors surface in AI assistant interface

**Analytics:**
- None

**Logs:**
- AI assistant console output
- Git commit history
- Workflow output captured in SUMMARY.md files

## CI/CD & Deployment

**Hosting:**
- Not deployed as service
- Distributed via Git repository
- Version controlled locally

**CI Pipeline:**
- GitHub Actions workflows in `.github/workflows/`
- Automated validation and testing

## Environment Configuration

**Development:**
- Required: Node.js for CLI tools
- Optional: AI coding assistant (Claude, Cursor, OpenCode, etc.)
- Configuration: `.planning/config.json`

**Secrets:**
- Framework has no secrets
- Optional: API keys for web search (Brave, Firecrawl, Exa)
- Should be stored in `.env` or user environment

## Webhooks & Callbacks

**Incoming:**
- None

**Outgoing:**
- None

---

*Integration audit: 2025-03-29*
*Update when adding/removing external services*
