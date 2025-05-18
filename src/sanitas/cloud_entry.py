""" Entrypoint for the cloud service (scheduler) to call the execution of task_syncer.
Listens to ${PORT} and calls the task_syncer methods on a schedule. """

from fastapi import FastAPI
from fastapi.responses import JSONResponse
import os
import uvicorn

from src.sanitas.sanitas import SanitasDataScraper


app = FastAPI()
scraper = SanitasDataScraper()


@app.get("/")
async def root():
    print("Run Sanitas scraper")
    sanitas_data = scraper.run()
    return JSONResponse(content={"message": "Run Sanitas scraper", "sanitas_data": str(sanitas_data)})


if __name__ == "__main__":
    port = os.getenv("PORT", 8080)
    host = "0.0.0.0"
    print(f"Test locally on http://localhost:{port}")
    print("Run GO")
    uvicorn.run(app, host=host, port=port)
