import threading
import tarfile
import yaml
from console import Console

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

        # хранение прав доступа к файлам
        self.file_permissions = {}

    # методы обработки команд

    def ls(self, append_path=""):
        path = self.get_append_path(append_path)
        print(path)

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
        if com[0] in ['a', 'q', 'b'] and com[2] in ['r', 'w', 'x'] and com[1] in ['+', '-']:
            # получаем путь файла
            file_main = self.find_file(file)
            if file_main is None:
                return f"File {file} not found."

            who, oper, what = com[0], com[1], com[2]
            num_who = ['a', 'q', 'b'].index(who)
            num_what = ['r', 'w', 'x'].index(what)

            flag = False
            if file not in self.file_permissions:
                flag = True
                self.file_permissions[file] = [1, 1, 1, 1, 1, 0, 0, 0, 0]  # по умолчанию прописываем все права

            before = self.file_permissions[file][num_what]

            if oper == '+':
                self.file_permissions[file][num_who * 3 + num_what] = 1
            else:
                self.file_permissions[file][num_who * 3 + num_what] = 0

            # проверяем, изменились ли права
            if before != self.file_permissions[file][num_what] or flag:
                return "The rights have been successfully changed"
            elif before == self.file_permissions[file][num_what] and not flag:
                return "The file still has the same rights"
            return "An error occurred when changing permissions"
        return "The arguments were set incorrectly"

    def tail(self, file):
        with tarfile.open(self.konf["path_vm"], "r") as tar:
            for member in tar.getmembers():
                # аходим нужный нам файл в архиве
                print(member.name)
                print("path  ", self.path, "   file   ", file)
                if member.name.endswith(file) and member.name[:len(member.name) - len(file)] == self.path and member.isfile():
                    with tar.extractfile(member) as f: # октрываем для чтения
                        text = (line.decode("utf-8") for line in f) # одновременное чтение и декодирование
                        last_lines = list(text)[-10:]
                        return "".join(last_lines)

        return "No such file"

    def clear(self):
        self.console.print("\n" * 20)

    # вспомогательные методы
    # возвращаем путь текущего файла в текстовом виде
    def find_file(self, file):
        with tarfile.open(self.konf["path_vm"], "r") as tar:
            for member in tar.getmembers():
                if member.name.endswith(file) and member.name[:len(member.name) - len(file)] == self.path:
                    return member.name
        return None

    # получение пути для команды ls
    def get_append_path(self, append_file):
        if append_file != "":
            with tarfile.open(self.konf["path_vm"], "r") as tar:
                for member in tar.getmembers():
                    if member.name.endswith(append_file) and member.name.startswith(self.path):
                        return member.name + "/"
        return self.path

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

    def work_with_script(self):
        if self.konf["start_script"]: # проверка наличия скрипта
            with open(self.konf["start_script"], "r") as script:
                self.console.insert_prompt() # вставка приглашения пользователя для ввода
                for line in script:
                    line = line.strip()
                    self.console.print(line)
                    self.perform_command(line)

    def run(self):
        work_of_script = threading.Thread(target=self.work_with_script)
        work_of_script.start()
        self.console.run() # запускаем цикл интерфейса

if __name__ == "__main__":
    task = Main()
    task.console.path = "/"
    task.run()
