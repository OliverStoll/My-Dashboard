""" Entrypoint for the cloud service (scheduler) to call the execution of task_syncer.
Listens to ${PORT} and calls the task_syncer methods on a schedule. """

from fastapi import FastAPI
from fastapi.responses import JSONResponse
import os
import uvicorn
from threading import Thread

from src.sanitas import SanitasDataScraper
from src.budgetbakers import BudgetBakersDataScraper


app = FastAPI()


@app.get("/")
async def root():
    sanitas_data = SanitasDataScraper().run()
    budgetbakers_data = BudgetBakersDataScraper().run()
    return JSONResponse(content={"message": "Run Sanitas & BudgetBakers scrapers", "sanitas_data": str(sanitas_data), "budgetbakers_data": str(budgetbakers_data)})


if __name__ == "__main__":
    port = os.getenv("PORT", 8080)
    host = "0.0.0.0"
    print(f"Test locally on http://localhost:{port}")
    uvicorn.run(app, host=host, port=port)
