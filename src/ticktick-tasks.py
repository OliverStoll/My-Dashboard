import requests
from datetime import datetime, timezone
from dataclasses import dataclass
from common_utils.apis.ticktick.habits import TicktickHabitHandler
from common_utils.web.selenium import DriverAction as Action, SeleniumHandler
from common_utils.config import load_dotenv


@dataclass
class TickTickProject:
    id: str
    name: str
    muted: bool
    closed: bool
    group_id: str | None = None

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "muted": self.muted,
            "closed": self.closed,
            "groupId": self.group_id,
        }


@dataclass
class TickTickTask:
    id: str
    project_id: str
    title: str
    status: int
    deleted: bool
    start_date: datetime | None
    due_date: datetime | None
    priority: int = 0
    is_all_day: bool = True
    content: str | None = None

    def to_dict(self):
        return {
            "id": self.id,
            "projectId": self.project_id,
            "title": self.title,
            "startDate": self.start_date,
            "dueDate": self.due_date,
            "status": self.status,
            "deleted": self.deleted,
            "priority": self.priority,
            "isAllDay": self.is_all_day,
            "content": self.content,
        }

    def is_active(self, projects: list[TickTickProject]):
        project = next((project for project in projects if project.id == self.project_id), None)
        assert project, f"Project with id {self.project_id} not found"
        current_time = datetime.now(timezone.utc)
        if project.closed or project.muted or (not self.start_date and not self.due_date):
            return False
        if self.start_date > current_time:
            return False
        if self.status != 0:
            return False
        return True











class TickTickTasksScraper:
    def __init__(self):
        load_dotenv()
        self.habits_handler = TicktickHabitHandler(headless=True, download_driver=True)
        self.headers = self.habits_handler.headers

    def get_tasks(self):
        url = "https://api.ticktick.com/api/v2/batch/check/0"
        response = self.make_get_request(url)
        tasks_data = response["syncTaskBean"]["update"]
        projects_data = response["projectProfiles"]
        return response

    def make_get_request(self, url):
        response = requests.get(url, headers=self.headers)
        return response.json()


if __name__ == "__main__":
    scraper = TickTickTasksScraper()
    tasks = scraper.get_tasks()
    print(tasks)