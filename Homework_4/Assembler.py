import struct
import argparse
import json

class Assembler:
    def __init__(self, input_file, bin_out_file, log_file):
        self.input_file = input_file
        self.bin_out_file = bin_out_file
        self.log_file = log_file

    def create_command(self, A, B, C, D=None, E=None):
        # Загрузка константы
        if A == 192:
            return self.create_command_load_constant(B, C)
        # Чтение значения из памяти
        elif A == 247:
            return self.create_command_read_memory(B, C)
        # Запись значения в память
        elif A == 115:
            return self.create_command_write_memory(B, C, D)
        # Бинарная операция "<="
        elif A == 83:
            return self.create_command_binary_op(B, C, D, E)
        else:
            return None

    def main_assem(self):
        logs = []
        commands = []

        with open(self.input_file, 'r') as infile:
            for line in infile:
                elements = line.strip().split()
                if len(elements) == 3:
                    a, b, c = int(elements[0]), int(elements[1]), int(elements[2])
                    command = self.create_command(a, b, c)

                    commands.append(command)
                    line = self.create_for_log(a, b, c, 0, 0, command)
                    logs.append(line)

                elif len(elements) == 4:
                    a, b, c, d = int(elements[0]), int(elements[1]), int(elements[2]), int(elements[3])
                    command = self.create_command(a, b, c, d)

                    commands.append(command)
                    line = self.create_for_log(a, b, c, d, 0, command)
                    logs.append(line)

                elif len(elements) == 5:
                    a, b, c, d, e = int(elements[0]), int(elements[1]), int(elements[2]), int(elements[3]), int(elements[4])

                    command = self.create_command(a, b, c, d, e)
                    commands.append(command)
                    line = self.create_for_log(a, b, c, d, e, command)
                    logs.append(line)

        with open(self.bin_out_file, 'wb') as outfile:
            for command in commands:
                outfile.write(command)
            print("Бинарный файл был успешно записан.")
            print(f'Путь к файлу: {self.bin_out_file}')

        with open(self.log_file, 'w') as log_file:
            json.dump(logs, log_file, indent=2)
            print(f"Файл-лог был успешно записан.")
            print(f'Путь к файлу: {self.log_file}')

    def create_for_log(self, A, B, C, D, E, command):
        line = ""
        for i in range(0, 9, 2):
            line += "0x" + command.hex()[i:i + 2] + " "
        return f'Data: {A}, {B}, {C}, {D}, {E}; Commands: {line.strip()}'

    def create_command_load_constant(self, B, C):
        b_new = (B & 0x7F)  # 7 бит для B
        c_low = C & 0xFF  # Младшие 8 бит C
        c_high = (C >> 8) & 0xFF  # Старшие 6 бит C
        return struct.pack("BBBBB", 192, b_new, c_low, c_high, 0)

    def create_command_read_memory(self, B, C):
        return struct.pack("BBBBB", 247, B, C & 0xFF, (C >> 8) & 0xFF, 0)

    def create_command_write_memory(self, B, C, D):
        return struct.pack("BBBBB", 115, B, C, D & 0xFF, (D >> 8) & 0xFF)

    def create_command_binary_op(self, B, C, D, E):
        return struct.pack("BBBBB", 83, B, C, D, E)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file")
    parser.add_argument("bin_out_file")
    parser.add_argument("log_file")

    args = parser.parse_args()
    assembler = Assembler(args.input_file, args.bin_out_file, args.log_file)
    assembler.main_assem()
