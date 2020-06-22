import logging
from pathlib import Path
from typing import Optional


class ATLogger():
    """Extentension of logging to easily log for both back and front end 
    in one line."""

    def __init__(self, name: str):
        self.name = name
        self._logger = logging.getLogger(name)
        self._config = {}
        self._job_id = None
        self._levels = {
            "debug": self._logger.debug,
            "info": self._logger.info,
            "error": self._logger.error,
            "warning": self._logger.warning
        }
        logging.basicConfig(level=logging.NOTSET)

    def set_config(self, config: dict) -> None:
        self._config = config
        if "job_id" in self._config:
            self._job_id = self._config["job_id"]
            self._mkdir()

    def log(
        self, level: str, message: str, 
        name: Optional[str] = None, fe_message: Optional[str] = None
    ) -> None:
        self._levels[level.lower()](message)
        if self._job_id and name:
            t_message = fe_message if fe_message else message
            Path(f"/tmp/{self._job_id}/{name}.out").write_text(t_message)
        
    def _mkdir(self) -> None:
        if not Path(f"/tmp/{self._job_id}").exists():
            Path(f"/tmp/{self._job_id}").mkdir()
