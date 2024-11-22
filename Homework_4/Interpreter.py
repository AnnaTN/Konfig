import xml.etree.ElementTree as ET
import struct
import argparse


class Interpreter:
    def __init__(self, binary_file, result_file, memory_range):
        self.binary_file = binary_file
        self.result_file = result_file
        self.memory = [0] * memory_range[1]  # ячейки памяти
        self.memory_range = memory_range

    def run(self):
        with open(self.binary_file, 'rb') as file:
            while command := file.read(5):  # Чтение 5 байт для каждой команды
                args = struct.unpack("BBBBB", command)
                print(f"Распакованные аргументы: {args}")
                self.execute_command(args)

    def execute_command(self, args):
        a, b, c, d, e = args

        # Объединение старших и младших 8 бит для константы
        constant = (d << 8) | c

        # Загрузка константы
        if a == 192:
            self.memory[b] = constant
            print(f"Загружена константа {constant} в регистр {b}")

        # Чтение значения из памяти
        elif a == 247:
            address = constant  # Адрес из поля C
            if address < len(self.memory):
                self.memory[b] = self.memory[address]
                print(f"Прочитано значение из памяти по адресу {address}, загружено в регистр {b}")
            else:
                print(f"Ошибка: адрес {address} выходит за пределы памяти.")

        # Запись значения в память
        elif a == 115:

            # формирование адреса регистра, куда будет занесено значение
            first_address = self.memory[b]
            final_address = first_address + d

            value_to_store = self.memory[c]

            if final_address < len(self.memory):
                self.memory[final_address] = value_to_store
                print(f"Записано значение {value_to_store} в память по адресу {final_address}")
            else:
                print(f"Ошибка: адрес {final_address} выходит за пределы памяти.")

        # Бинарная операция "<="
        elif a == 83:
            # находим операнды
            value1 = self.memory[c]
            address2 = self.memory[d] + e
            value2 = self.memory[address2]

            result = int(value1 <= value2)

            self.memory[b] = result
            print(f"Результат бинарной операции '<=' сохранен в регистр {b}: {result}")

        else:
            raise ValueError(f"Неизвестный опкод: {a}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file")
    parser.add_argument("output_file")
    parser.add_argument("memory_range", nargs=2, type=int)

    args = parser.parse_args()

    interpreter = Interpreter(args.input_file, args.output_file, tuple(args.memory_range))
    interpreter.run()
