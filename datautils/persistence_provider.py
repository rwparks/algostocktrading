from typing import Protocol, Any


class PersistenceProviderError(Exception):

    def __init__(self,  message='Persistence provider error'):
        self.message = message
        super().__init__(self.message)


class PersistenceProvider(Protocol):

    def load(self, file_name_format: str, **kwargs) -> Any:
        """ load the data from persistence storage """

    def save(self, data: Any, file_name_format: str, **kwargs) -> None:
        """ save the data to persistence storage """
