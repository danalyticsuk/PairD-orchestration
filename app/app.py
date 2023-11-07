# Dependency Imports
import fastapi
import loguru

m
# Initialize app:
app = fastapi.FastAPI()

# Write some health check or other function here

# General Model initializations:



# Add routers to the app - create a for loop

from app.routes.input_ingestion import router as input_ingest
from app.routes.input_post import router as input_post
from app.routes.output_ingestion import router as output_ingest
from app.routes.output_post import router as output_post

for router in [input_ingest, input_post, output_ingest, output_post]:
    app.include_router(router)
