""" Entrypoint for the cloud service (scheduler) to call the execution of task_syncer.
Listens to ${PORT} and calls the task_syncer methods on a schedule. """

from fastapi import FastAPI
from fastapi.responses import JSONResponse
import os
import uvicorn

from src.ticktick_tasks.ticktick_tasks import TickTickTasksScraper

app = FastAPI()


@app.get("/")
async def root():
    tasks_stat = TickTickTasksScraper().run()
    return JSONResponse(content={"message": "Run TickTick Tasks scraper", "data": str(tasks_stat)})


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    host = "0.0.0.0"
    print(f"Test locally on http://localhost:{port}")
    uvicorn.run(app, host=host, port=port)
