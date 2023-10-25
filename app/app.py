# Dependency Imports
import fastapi
import loguru

# Initialize app:
app = fastapi.FastAPI()

# Write some health check or other function here

# Add routers to the app - create a for loop

from app.routes.ingestion import router as ingest_query
from app.routes.post import router as get_query

for router in [ingest_query, get_query]:
    app.include_router(router)
