from common_utils.apis.ticktick.tasks import TickTickTaskHandler
from common_utils.config import load_dotenv


class TickTickTasksScraper:
    def __init__(self):
        load_dotenv()
        self.task_handler = TickTickTaskHandler()