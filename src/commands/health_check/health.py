from src.commands.base_command import BaseCommand


class Health(BaseCommand):
    def __init__(self):
        """
        Health check command
        """
        pass

    def execute(self):
        return "pong"
