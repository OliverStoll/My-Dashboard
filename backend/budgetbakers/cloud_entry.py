""" Entrypoint for the cloud service (scheduler) to call the execution of task_syncer.
Listens to ${PORT} and calls the task_syncer methods on a schedule. """

from fastapi import FastAPI
from fastapi.responses import JSONResponse
import os
import uvicorn

from backend.budgetbakers.budgetbakers import BudgetBakersDataScraper

app = FastAPI()
scraper = BudgetBakersDataScraper()


@app.get("/")
async def root():
    budgetbakers_data = scraper.run()
    return JSONResponse(
        content={"message": "Run Budgetbaker scraper", "data": str(budgetbakers_data)}
    )


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    host = "0.0.0.0"
    print(f"Test locally on http://localhost:{port}")
    uvicorn.run(app, host=host, port=port, log_level="warning")
