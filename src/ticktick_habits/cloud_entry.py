""" Entrypoint for the cloud service (scheduler) to call the execution of task_syncer.
Listens to ${PORT} and calls the task_syncer methods on a schedule. """

from fastapi import FastAPI
from fastapi.responses import JSONResponse
import os
import uvicorn

from src.ticktick_habits.ticktick_habits import TicktickHabitsScraper

app = FastAPI()


@app.get("/")
async def root():
    habit_data = TicktickHabitsScraper().run()
    return JSONResponse(content={"message": "Run TickTick scraper", "data": str(habit_data)})


if __name__ == "__main__":
    port = os.getenv("PORT", 8080)
    host = "0.0.0.0"
    print(f"Test locally on http://localhost:{port}")
    uvicorn.run(app, host=host, port=port)
