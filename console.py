import tkinter as tk
from tkinter import scrolledtext

class Console:

    def __init__(self, cmd_callback):

        self.task = cmd_callback
        self.path = "" # "объявляем" переменную для пути, чтобы в основном классе можно было ее изменить

        self.root = tk.Tk()
        self.root.title("The emulator")

        # цвета
        self.bg_color = "#ffffff"  # фон
        self.text_color = "#000000"  # текст
        self.prompt_user_color = "#006400"  # имя пользователя
        self.prompt_path_color = "#0000ff"  # путь директории

        # создание виджета с прокручиваемым текстом
        self.console = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, height=20, width=70,
                                                 bg=self.bg_color, fg=self.text_color,
                                                 insertbackground=self.text_color)

        self.console.config(font=("Courier New", 12))

        # создаем теги и определяем их цвет
        self.console.tag_configure("user", foreground=self.prompt_user_color)
        self.console.tag_configure("path", foreground=self.prompt_path_color)

        self.console.grid(row=0, column=0, padx=0, pady=0)
        self.console.bind('<Return>', self.execute_command)  # вызов метода при нажатии enter

    def execute_command(self, event):
        # Выполнение команды при нажатии на Enter
        input_text = self.console.get("1.0", tk.END) # извлчение текста из консоли

        comm = (input_text.split("\n")[-2].strip()).split("$")[1].strip()

        if comm == "exit":
            self.root.quit()
            return

        self.console.insert(tk.END, "\n") # новая строка для вывода ответа
        self.task(comm)
        return "break"

    def print(self, text=""):
        # Печать текста в консоль
        self.console.insert(tk.END, f"{text}\n")

    def insert_prompt(self):
        # Вставка приглашения пользователя в консоль
        self.console.insert(tk.END, f"{self.user}", "user")
        self.console.insert(tk.END, f":{self.path}", "path")
        self.console.insert(tk.END, "$ ")
        self.console.mark_set("insert", tk.END) # установка курсора

    def run(self):
        # Запуск интерфейса
        self.root.mainloop()
