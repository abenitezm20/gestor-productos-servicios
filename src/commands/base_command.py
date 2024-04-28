from abc import ABC, abstractmethod


class BaseCommand(ABC):
    @abstractmethod
    def execute(self):
        raise NotImplementedError(
            "Por favor implementar la funcionalidad en una subclase")
