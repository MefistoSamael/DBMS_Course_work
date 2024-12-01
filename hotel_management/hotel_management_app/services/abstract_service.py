from abc import ABC, abstractmethod


class AbstractService(ABC):
    @staticmethod
    @abstractmethod
    def create(*args, **kwargs):
        """Method to create a new record."""
        pass

    @staticmethod
    @abstractmethod
    def update(*args, **kwargs):
        """Method to update an existing record."""
        pass
