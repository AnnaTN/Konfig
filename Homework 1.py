import threading
import tarfile
import yaml
from console import Console  # Импортируем класс Console из другого файла

class main:

    konf = {
        "path_vm": "", # путь к виртуальной файловой системе
        "start_script": "", # путь к стартовому скрипту
        "user": ""
    }   

    def __init__(self):
        # указываем, что команда, переданная в кач-ве аргумента, будет передана методу perform_command для обработки
        self.console = Console(self.perform_command)

        # загрузка конфигурации
        with open('./konf.yaml') as f:
            self.konf = yaml.safe_load(f)

        # установка пути и пользователя для консоли
        self.path = self.konf["path_vm"].replace(".tar", "") + "/"
        self.console.user = self.konf["user"]

# Методы обработки команд

    def _ls(self, append_path=""):
        # получаем полный путь к директории, содержимое которой хотим вывести
        path = self.get_path(append_path)
        elems = []

        with tarfile.open(self.konf["path_vm"], "r") as tar:
            # проходимся по всем членам исходного архива
            for member in tar.getmembers():
                if member.name.startswith(path): # проверка, начинается ли имя с нужного пути
                    elem_name = member.name.split("/")[path.count("/")] # получаем имя конкретного файла
                    if elem_name not in elems:
                        elems.append(elem_name)

        return "\n".join(elems)

    def _cd(self, path):

        # устанавливаем путь для случая перехода в предыдущую директорию
        if path == ".." and self.path != "/":
            if self.path != "/": # если текущая директория не главная
                path_parts = self.path.split("/")[:-2]
                self.path = "/".join(path_parts) + "/"
                self.console.path = self.path[len((self.konf["path_vm"].split("."))[0]):]
                return
            return

        if isinstance(path, str):
            path = path.split("/")

        # проверка существования заданной директории в архиве
        with tarfile.open(self.konf["path_vm"], "r") as tar:
            for member in tar.getmembers():
                if member.name == self.path + "/".join(path) and member.isdir():
                    break
            else:
                self.console.print("No such directory")

        self.path += "/".join(path) + "/"
        self.console.path = self.path.replace(self.konf["path_vm"].replace(".tar", ""), "")

    def _tail(self, path):
        path = self.get_path(path)[:-1]
        with tarfile.open(self.konf["path_vm"], "r") as tar:
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
            if len(command) == 1: self.console.print(self._ls(""))
            else: self.console.print(self._ls(command[1])) # вывод содержимого директорий, являющихся текущей директорией либо вложенной в нее

        elif command[0] == "cd" and len(command) > 1:
            self._cd(command[1])

        elif command[0] == "exit":
            self.console.root.quit()

        elif command[0] == "chmod":
            if len(command) < 3:
                self.console.print("Usage: chmod <permissions> <file>")
            else:
                self.chmod(command[1:])

        elif command[0] == "tail":
            self.console.print(self._tail(command[1]))

        elif command[0] == "clear":
           self.clear()

        else:
            self.console.print("Unknown command")

        self.console.insert_prompt()

    def run_start_script(self):
        if self.konf["start_script"]:
            with open(self.konf["start_script"], "r") as script:
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
    task.console.path = "/"
    task.run()
