"""MongoDB support removed — all data now in PostgreSQL.

This module is retained as a stub for backwards compatibility only.
Active code should use app.database.postgres instead.
"""


async def get_mongo():
    raise RuntimeError(
        "MongoDB is no longer used. All content data is in PostgreSQL. "
        "Use app.database.postgres.get_db() instead."
    )


async def close_mongo():
    pass
