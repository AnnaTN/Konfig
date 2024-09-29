import threading
import tarfile
import yaml
from console import Console  # Импортируем класс Console из другого файла

class Main:
    all_f = []

    konf = {
        "path_vm": "",  # путь к виртуальной файловой системе
        "start_script": "",  # путь к стартовому скрипту
        "user": ""
    }

    def __init__(self):
        self.console = Console(self.perform_command)

        # загрузка конфигурации
        with open('./konf.yaml') as f:
            self.konf = yaml.safe_load(f)

        # установка пути и пользователя для консоли
        self.path = self.konf["path_vm"].replace(".tar", "") + "/"
        self.console.user = self.konf["user"]


        # Для хранения прав доступа к файлам
        self.file_permissions = {}

    # Методы обработки команд

    def ls(self, append_path=""):
        path = self.get_path(append_path)
        elems = []

        with tarfile.open(self.konf["path_vm"], "r") as tar:
            for member in tar.getmembers():
                if member.name.startswith(path):
                    elem_name = member.name.split("/")[path.count("/")]
                    if elem_name not in elems:
                        elems.append(elem_name)

        return "\n".join(elems)

    def cd(self, path):
        if path == "..":
            if self.path != "/" and self.console.path != "/":
                path_parts = self.path.split("/")[:-2]
                self.path = "/".join(path_parts) + "/"
                self.console.path = self.path[len("file_system"):]
                return
            return

        if isinstance(path, str):
            path = path.split("/")

        with tarfile.open(self.konf["path_vm"], "r") as tar:
            for member in tar.getmembers():
                if member.name == self.path + "/".join(path) and member.isdir():
                    break
            else:
                self.console.print("No such directory")

        self.path += "/".join(path) + "/"
        self.console.path = self.path.replace(self.konf["path_vm"].replace(".tar", ""), "")

    def chmod(self, com, file):
        file_main = self.find_file(file)

        if file_main is None:
            return f"File '{file}' not found."

        if com[0] in ['a', 'q', 'b'] and com[2] in ['r', 'w', 'x'] and com[1] in ['+', '-']:
            who, oper, what = com[0], com[1], com[2]
            num_who = ['a', 'q', 'b'].index(who)
            num_what = ['r', 'w', 'x'].index(what)

            flag = False
            # Проверяем права доступа к файлу
            if file not in self.file_permissions:
                flag = True
                self.file_permissions[file] = [1, 1, 1, 1, 1, 0, 0, 0, 0]  # по умолчанию все права разрешены

            before = self.file_permissions[file][num_what]
            print(self.file_permissions[file])
            if oper == '+':
                self.file_permissions[file][num_who * 3 + num_what] = 1
            else:
                self.file_permissions[file][num_who * 3 + num_what] = 0

            # Проверяем, изменились ли права
            print(self.file_permissions[file])
            if before != self.file_permissions[file][num_what] or flag:
                return "The rights have been successfully changed"
            return "An error occurred when changing permissions"

        return "The arguments were set incorrectly"

    def tail(self, path):
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

    def find_file(self, file):
        with tarfile.open(self.konf["path_vm"], "r") as tar:
            for member in tar.getmembers():
                print(f"Checking member: {member.name}")  # Отладочный вывод
                if member.name.endswith(file):
                    return member.name
        print(f"File '{file}' not found.")  # Отладочный вывод
        return None

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
        if command[0] == "ls":
            if len(command) == 1:
                self.console.print(self.ls(""))
            else:
                self.console.print(self.ls(command[1]))

        elif command[0] == "cd" and len(command) > 1:
            self.cd(command[1])

        elif command[0] == "exit":
            self.console.root.quit()

        elif command[0] == "chmod":
            if len(command) == 3:
                self.console.print(self.chmod(command[1], command[2]))
            else:
                self.console.print("The arguments were set incorrectly")

        elif command[0] == "tail":
            self.console.print(self.tail(command[1]))

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

    def check(elem1, elem2):
        for j in range(min(len(elem1), len(elem2))):
            if elem1[j] != elem2[j]:
                return False
        return True

if __name__ == "__main__":
    task = Main()
    task.console.path = "/"
    task.run()
