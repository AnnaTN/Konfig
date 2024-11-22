import struct
import argparse
import json


class Assembler:
    def __init__(self, input_file, output_file, log_file):
        self.input_file = input_file
        self.output_file = output_file
        self.log_file = log_file

    def assemble(self):
        logs = []  # Список для хранения логов
        with open(self.input_file, 'r') as infile, open(self.output_file, 'wb') as outfile:
            for line in infile:
                if line.startswith("#"):
                    continue  # Пропуск комментариев
                if not line.strip():
                    continue  # Пропуск пустых строк

                parts = line.strip().split()
                if len(parts) == 3:
                    A = int(parts[0])  # Опкод
                    B = int(parts[1])  # Адрес регистра
                    C = int(parts[2])  # Константа
                    command = self.create_command(A, B, C)
                    if command:
                        outfile.write(command)
                        logs.append({'opcode': A, 'reg_address': B, 'constant': C, 'command': command.hex()})
                elif len(parts) == 4:
                    A = int(parts[0])  # Опкод
                    B = int(parts[1])  # Адрес регистра
                    C = int(parts[2])  # Адрес для чтения/записи
                    D = int(parts[3])  # Смещение
                    command = self.create_command(A, B, C, D)
                    if command:
                        outfile.write(command)
                        logs.append({'opcode': A, 'reg_address': B, 'constant': C, 'address': D, 'command': command.hex()})
                elif len(parts) == 5:
                    A = int(parts[0])  # Опкод
                    B = int(parts[1])  # Адрес регистра
                    C = int(parts[2])  # Адрес регистра первого операнда
                    D = int(parts[3])  # Адрес с суммой для второго операнда
                    E = int(parts[4])  # Смещение второго операнда
                    command = self.create_command(A, B, C, D, E)
                    if command:
                        outfile.write(command)
                        logs.append({'opcode': A, 'reg_address': B, 'operands': (C, D, E), 'command': command.hex()})

        # Сохраняем лог в формате JSON
        with open(self.log_file, 'w') as log_file:
            json.dump(logs, log_file, indent=4)
            print(f"Лог команд сохранен в {self.log_file}")

    def create_command(self, A, B, C, D=None, E=None):
        # Собираем команду в зависимости от опкода
        if A == 192:  # Загрузка константы
            return self.create_command_load_constant(B, C)
        elif A == 247:  # Чтение значения из памяти
            return self.create_command_read_memory(B, C)
        elif A == 115:  # Запись значения в память
            return self.create_command_write_memory(B, C, D)
        elif A == 83:  # Бинарная операция "<="
            return self.create_command_binary_op(B, C, D, E)
        else:
            return None

    def create_command_load_constant(self, B, C):
        # Создание команды для загрузки константы
        b_and_c = (B & 0x7F) | ((C >> 7) & 0x80)  # 7 бит для B, 1 бит для старшего бита C
        c_low = C & 0xFF  # Младшие 8 бит C
        c_high = (C >> 8) & 0xFF  # Старшие 6 бит C
        return struct.pack("BBBBB", 192, b_and_c, c_low, c_high, 0)  # Пятый байт всегда 0

    def create_command_read_memory(self, B, C):
        # Чтение значения из памяти
        return struct.pack("BBBBB", 247, B, C & 0xFF, (C >> 8) & 0xFF, 0)

    def create_command_write_memory(self, B, C, D):
        # Запись значения в память
        return struct.pack("BBBBB", 115, B, C, D & 0xFF, (D >> 8) & 0xFF)

    def create_command_binary_op(self, B, C, D, E):
        # Бинарная операция "<="
        return struct.pack("BBBBB", 83, B, C, D, E)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", help="путь к входному файлу")
    parser.add_argument("output_file", help="путь к выходному бинарному файлу")
    parser.add_argument("log_file", help="путь к файлу лога")

    args = parser.parse_args()

    assembler = Assembler(args.input_file, args.output_file, args.log_file)
    assembler.assemble()
