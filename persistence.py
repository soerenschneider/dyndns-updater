import logging

class Persistence:
    def write(self, new_ip: str) -> None:
        pass

    def read(self) -> str:
        return None

    def get_plugin_name(self) -> str:
        return "Dummy"

class FilePersistence(Persistence):
    def __init__(self, path):
        if not path:
            raise ValueError("no path supplied")

        self.file_path = path

    def write(self, new_ip: str) -> None:
        if not new_ip:
            return

        with open(self.file_path, "w") as f:
            f.write(new_ip)

    def read(self) -> str:
        with open(self.file_path, "r") as f:
            return f.read().replace("\n", "").strip()
    
    def get_plugin_name(self) -> str:
        return "Filesystem"