import csv
import threading
import tarfile
import yaml
import json
from datetime import datetime
import zipfile
import tkinter as tk
from tkinter import scrolledtext


class Console:
    bg_color = "#2e2e2e"
    text_color = "#ffffff"
    prompt_color = "#00ff00"
    prompt_user_color = "#00ff00"
    prompt_path_color = "#00bfff"

    def __init__(self, cmd_callback):
        self.cmd_callback = cmd_callback
        self.path = "/"

        self.root = tk.Tk()
        self.root.title("Not Bash")

        self.console = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, height=20, width=70,
                                                 bg=self.bg_color, fg=self.text_color,
                                                 insertbackground=self.text_color)
        self.console.grid(row=0, column=0, padx=0, pady=0)
        self.console.bind('<Return>', self.execute_command)
        self.console.config(font=("Courier New", 12))

        self.console.tag_configure("user", foreground=self.prompt_user_color)
        self.console.tag_configure("path", foreground=self.prompt_path_color)

    def execute_command(self, event):
        input_text = self.console.get("1.0", tk.END)

        command = input_text.split("\n")[-2].strip()
        command = command.split("$")[1].strip()

        if command == "exit":
            self.root.quit()
            return

        self.console.insert(tk.END, "\n")
        self.cmd_callback(command)

        return "break"

    def print(self, text=""):
        self.console.insert(tk.END, f"{text}\n")

    def insert_prompt(self):
        self.console.insert(tk.END, f"{self.user}@computer", "user")
        self.console.insert(tk.END, f":{self.path}", "path")
        self.console.insert(tk.END, "$ ")
        self.console.mark_set("insert", tk.END)

    def set_path(self, path):
        self.path = path

    def run(self):
        self.root.mainloop()


class NotBash:
    path = "/"
    config = {
        "path_vm": "",
        "start_script": "",
        "user": "user"
    }

    def __init__(self):
        self.console = Console(self.cmd_processing)

        # Load config
        with open('./konf.yaml') as f:
            self.config = yaml.safe_load(f)

        # Set current path
        self.path = self.config["path_vm"].replace(".tar", "") + "/"

        # Check required keys
        required_keys = ["user", "path_vm", "start_script"]
        for key in required_keys:
            if key not in self.config:
                raise KeyError(f"Missing key in config: {key}")

        self.console.user = self.config["user"]

    # --- Commands processing ---

    def _ls(self, append_path=""):
        path = self.get_path(append_path)
        elems = set()
        with tarfile.open(self.config["path_vm"], "r") as tar:
            for member in tar.getmembers():
                if not member.name.startswith(path):
                    continue
                elems.add(member.name.split("/")[path.count("/")])

        return "\n".join(elems)

    def _cd(self, path):
        self.path = self.path.replace("//", "/")

        # Преобразуем путь в список
        if isinstance(path, str):
            path = path.split("/")

        # Проверка на пустой путь
        if not path or (len(path) == 1 and path[0] == ""):
            return  # Ничего не делаем, если путь пустой

        # Обработка ".."
        if path[0] == "..":
            # Если текущий путь не корень, то переходим на уровень выше
            if self.path != "/":
                self.path = "/".join(self.path.split("/")[:-2]) + "/"
            return self._cd(path[1:])  # Рекурсивный вызов для остальных частей пути

        # Остальные случаи: обработка ".", переход в директорию
        if path[0] == ".":
            return self._cd(path[1:])

        # Обработка перехода в директорию
        with tarfile.open(self.config["path_vm"], "r") as tar:
            for member in tar.getmembers():
                # Проверяем, существует ли директория по указанному пути
                if member.name == self.path + "/".join(path) and member.isdir():
                    break
            else:
                return "No such directory"  # Если директория не найдена

        # Обновляем текущий путь
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

    def _du(self, path=""):
        path = self.get_path(path)[:-1]
        with tarfile.open(self.config["path_vm"], "r") as tar:
            for member in tar.getmembers():
                if member.name == path and member.isdir():
                    break
            else:
                return "No such directory"

            total_size = 0
            result = ""
            for member in tar.getmembers():
                if member.name.startswith(path):
                    if not member.isfile():
                        continue

                    size = member.size
                    name = "/" + "/".join(member.name.split("/")[2:])

                    total_size += size
                    result += f"{size}\t{name}" + "\n"

            return result + f"Total size: {total_size} bytes"

    def clear(self):
       self.console.print("\n" * 20)

    def chmod(self, permissions):
        # Dummy function, implement permission change logic here
        self.console.print("chmod command executed with params: " + " ".join(permissions))

    # --- Class methods ---

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

    def cmd_processing(self, command):
        command = command.split(" ")
        match command[0]:
            case "ls":
                self.console.print(self._ls(command[1] if len(command) > 1 else ""))
            case "cd":
                error = self._cd(command[1])
                if error:
                    self.console.print(error)

                new_path = self.path.replace(
                    self.config["path_vm"].replace(".tar", ""), "")
                self.console.set_path(new_path)
            case "tail":
                self.console.print(self._tail(command[1]))
            case "du":
                self.console.print(self._du(command[1] if len(command) > 1 else ""))
            case "clear":
                self.clear()
            case "chmod":
                if len(command) < 3:
                    self.console.print("Usage: chmod <permissions> <file>")
                else:
                    self.chmod(command[1:])
            case "exit":
                self.console.insert_prompt()
                self.console.root.quit()
                return
            case _:
                self.console.print("Unknown command")

        self.console.insert_prompt()

    def run_start_script(self):
        if self.config["start_script"]:
            with open(self.config["start_script"], "r") as script:
                self.console.insert_prompt()
                for line in script:
                    line = line.strip()
                    self.console.print(line)
                    self.cmd_processing(line)

    def run(self):
        start_cmds = threading.Thread(target=self.run_start_script)
        start_cmds.start()

        self.console.run()


if __name__ == "__main__":
    not_bash = NotBash()
    not_bash.run()
