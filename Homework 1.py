import threading
import tarfile
import yaml
from console import Console  # Импортируем класс Console из другого файла

class main:

    config = {
        "path_vm": "", # путь к виртуальной файловой системе
        "start_script": "", # путь к стартовому скрипту
        "user": ""
    }

    def __init__(self):
        # указываем, что команда, переданная в кач-ве аргумента, будет передана методу perform_command для обработки
        self.console = Console(self.perform_command)

        # загрузка конфигурации
        with open('./konf.yaml') as f:
            self.config = yaml.safe_load(f)

        # установка пути и пользователя для консоли
        self.path = self.config["path_vm"].replace(".tar", "") + "/"
        self.console.user = self.config["user"]

# Методы обработки команд

    # команда ls
    def _ls(self, append_path=""):
        # получаем полный путь к директории, содержимое которой хотим вывести
        path = self.get_path(append_path)
        elems = []

        with tarfile.open(self.config["path_vm"], "r") as tar:
            # проходимся по всем членам исходного архива
            for member in tar.getmembers():
                if member.name.startswith(path): # проверка, начинается ли имя с нужного пути
                    elem_name = member.name.split("/")[path.count("/")] # получаем имя конкретного файла
                    if elem_name not in elems:
                        elems.append(elem_name)

        return "\n".join(elems)

    def _cd(self, path):
        # функция либо изменит путь на нужный нам, либо сообщит об ошибке
        if len(path) == 0:
            return

        if isinstance(path, str):
            path = path.split("/")

        if path[0] == "..":
            if self.path != "/": # если не главная директория
                path_parts = self.path.split("/")[:-2]
                self.path = "/".join(path_parts) + "/"
            return self._cd(path[1:])

        # проверка существования заданной директории в архиве
        with tarfile.open(self.config["path_vm"], "r") as tar:
            for member in tar.getmembers():
                if member.name == self.path + "/".join(path) and member.isdir():
                    break
            else:
                return "No such directory"

        self.path += "/".join(path) + "/"
        self.path = self.path.replace("//", "/")

    def _tail(self, path):
        path = self.get_path(path)[:-1]
        with tarfile.open(self.config["path_vm"], "r") as tar:
            for member in tar.getmembers():
                if member.name == path and member.isfile():
                    break
            else:
                return "No such file"

            with tar.extractfile(member) as f:
                lines = f.readlines()
                lines = [line.decode("utf-8") for line in lines]
                return "".join(lines[-min(len(lines), 10):])

    def clear(self):
        self.console.print("\n" * 20)

    def chmod(self, permissions):
        self.console.print("chmod command executed with params: " + " ".join(permissions))

    # --- Вспомогательные методы ---

    def get_path(self, path):
        path = path.split("/")
        result_path = self.path
        if path[0] == "" and len(path) > 1:
            result_path = "./file_system/"
            path = path[1:]
        for elem in path:
            if elem == "..":
                result_path = "/".join(result_path.split("/")[:-2]) + "/"
            elif elem == ".":
                continue
            else:
                result_path += elem + "/"
            result_path = result_path.replace("//", "/")
        return result_path

    def perform_command(self, command):
        command = command.split(" ")
        if command[0] ==  "ls":
                if len(command) == 1: self.console.print(self._ls())
                else: self.console.print(command[1])

        elif command[0] == "cd" and len(command) > 1:
            error = self._cd(command[1])
            if error:
                self.console.print(error)
            new_path = self.path.replace(self.config["path_vm"].replace(".tar", ""), "")
            self.console.set_path(new_path)
        elif command[0] == "tail":
            self.console.print(self._tail(command[1]))
        elif command[0] == "clear":
           self.clear()
        elif command[0] == "chmod":
            if len(command) < 3:
                self.console.print("Usage: chmod <permissions> <file>")
            else:
                self.chmod(command[1:])
        elif command[0] == "exit":
            self.console.insert_prompt()
            self.console.root.quit()
            return
        else:
            self.console.print("Unknown command")

        self.console.insert_prompt()

    def run_start_script(self):
        if self.config["start_script"]:
            with open(self.config["start_script"], "r") as script:
                self.console.insert_prompt()
                for line in script:
                    line = line.strip()
                    self.console.print(line)
                    self.perform_command(line)

    def run(self):
        start_cmds = threading.Thread(target=self.run_start_script)
        start_cmds.start()

        self.console.run()


if __name__ == "__main__":
    task = main()
    task.run()
