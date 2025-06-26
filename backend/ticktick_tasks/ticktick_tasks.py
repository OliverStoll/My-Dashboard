import os
import requests
import pytz
from datetime import datetime, timezone
from dataclasses import dataclass, fields
from common_utils.apis.ticktick.habits import TicktickHabitHandler
from common_utils.config import load_dotenv
from common_utils.apis.firebase import FirebaseClient


@dataclass
class TickTickProject:
    id: str
    name: str
    muted: bool
    closed: bool
    inAll: bool
    groupId: str | None = None

    @classmethod
    def from_dict(cls, data):
        field_names = {field.name for field in fields(cls)}
        filtered_data = {key: value for key, value in data.items() if key in field_names}
        return TickTickProject(**filtered_data)


@dataclass
class TickTickTask:
    id: str
    projectId: str
    title: str
    status: int
    deleted: bool
    startDate: str | datetime | None = None
    dueDate: str | datetime | None = None
    priority: int = 0
    isAllDay: bool = True
    content: str | None = None
    projectClass: TickTickProject | None = None

    def __post_init__(self):
        self.startDate = datetime.fromisoformat(self.startDate) if self.startDate else None
        self.dueDate = datetime.fromisoformat(self.dueDate) if self.dueDate else None

    @classmethod
    def from_dict(cls, data):
        field_names = {field.name for field in fields(cls)}
        filtered_data = {key: value for key, value in data.items() if key in field_names}
        return TickTickTask(**filtered_data)

    def is_active(self):
        project = self.projectClass
        current_time = datetime.now(timezone.utc)
        if project.closed or project.muted or not project.inAll:
            return False
        if (not self.startDate and not self.dueDate) or self.startDate > current_time:
            return False
        if self.status != 0:
            return False
        return True


class TickTickTasksScraper:
    inbox_project = TickTickProject(id="0", name="Inbox", muted=False, closed=False, inAll=True)
    firebase_path = "/DATA/Tasks/TickTick"

    def __init__(self):
        load_dotenv()
        self.habits_handler = TicktickHabitHandler(
            cookies_path="ticktick-cookies.json", headless=True, download_driver=True
        )
        self.headers = self.habits_handler.headers
        self.firebase = FirebaseClient(realtime_db_url=os.environ["FIREBASE_REALTIME_DB_URL"])

    def run(self):
        active_tasks = self.get_tasks(only_active=True)
        self.store_num_active_tasks_firebase(active_tasks)
        return active_tasks

    def get_projects(self):
        url = "https://api.ticktick.com/api/v2/batch/check/0"
        response = self._make_get_request(url)
        projects_data = response["projectProfiles"]
        projects = [TickTickProject.from_dict(project_data) for project_data in projects_data]
        return projects

    def get_tasks(self, only_active=False):
        url = "https://api.ticktick.com/api/v2/batch/check/0"
        response = self._make_get_request(url)
        tasks_data = response["syncTaskBean"]["update"]
        tasks = [TickTickTask.from_dict(task_data) for task_data in tasks_data]
        projects_data = response["projectProfiles"]
        projects = [TickTickProject.from_dict(project_data) for project_data in projects_data]
        projects_map = {project.id: project for project in projects}
        for task in tasks:
            task.projectClass = projects_map.get(task.projectId, None)
            if not task.projectClass and "inbox" in task.projectId:
                task.projectClass = self.inbox_project
        if only_active:
            tasks = [task for task in tasks if task.is_active()]
        return tasks

    def _make_get_request(self, url):
        response = requests.get(url, headers=self.headers)
        return response.json()

    def store_num_active_tasks_firebase(self, active_tasks):
        now = datetime.now(pytz.timezone("Europe/Berlin"))
        current_date = now.strftime("%Y-%m-%d")
        hour = now.strftime("%H")
        minute = now.strftime("%M")
        ref = f"{self.firebase_path}/Aktive-Aufgaben-Stats/{current_date}/{hour}"
        old_data = self.firebase.get_entry(ref=ref)
        new_data = old_data if old_data else {}
        new_data[minute] = len(active_tasks)
        self.firebase.set_entry(ref=ref, data=new_data)


if __name__ == "__main__":
    scraper = TickTickTasksScraper()
    tasks = scraper.run()
