import logging
from pathlib import Path


class ATLogger():
    """Extentension of logging to easily log for both back and front end 
    in one line"""

    def __init__(self, name: str):
        self.name = name
        self._logger = logging.getLogger(name)
        self._config = {}
        self._job_id = None
        self._levels = {
            "debug": self._logger.debug,
            "info": self._logger.info,
            "error": self._logger.error,
        }

    def set_config(self, config: dict) -> None:
        self._config = config
        if "job_id" in self._config:
            self._job_id = self._config["job_id"]
            self._mkdir()

    def log(self, level: str, message: str, name: str = None) -> None:
        self._levels[level](message)
        if self._job_id and name:
            Path(f"/tmp/{self._job_id}/{name}.out").write_text(message)
        
    def _mkdir(self):
        if not Path(f"/tmp/{self._job_id}").exists():
            Path(f"/tmp/{self._job_id}").mkdir()
