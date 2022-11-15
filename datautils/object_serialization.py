import logging
from logging import Logger
import pickle
from pathlib import Path
from typing import Any
from attr import define, field

from datautils.persistence_provider import PersistenceProviderError


@define
class ObjectSerialization:
    persist_dir: str = field(default='.')
    dir_path: Path = field(init=False)
    logger: Logger = field(init=False)

    @logger.default
    def _set_logger(self):
        logger = logging.getLogger(__name__)
        return logger

    @persist_dir.validator
    def check_persist_path(self, attribute, value):
        self.dir_path = Path(value)
        if not self.dir_path.is_dir():
            self.dir_path.mkdir(parents=True)

    def load(self, file_name_format: str, **kwargs) -> Any:
        persist_path = Path(f'{self.dir_path.absolute()}/'
                            f'{file_name_format.format(**kwargs)}')
        if persist_path.is_file():
            self.logger.debug(f'Loading data from {persist_path.absolute()}')
            return pickle.load(open(persist_path.absolute(), 'rb'))
        else:
            raise PersistenceProviderError(f"{persist_path.absolute()} is not a file")

    def save(self, data: Any, file_name_format: str, **kwargs) -> None:
        persist_path = Path(f'{self.dir_path.absolute()}/'
                            f'{file_name_format.format(**kwargs)}')
        self.logger.debug(f'Dumping data to {persist_path.absolute()}')
        with open(persist_path.absolute(), 'wb') as f:
            pickle.dump(data, f)
