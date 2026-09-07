"""
External API integrations for EcoFinwize.

Each service follows the same pattern:
- Config loaded from env via Settings (see app.config)
- Graceful degradation when API keys are missing
- Consistent error handling and logging
- Async-first design with httpx or aiohttp
"""
