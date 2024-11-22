import xml.etree.ElementTree as ET
import struct
import argparse


class Interpreter:
    def __init__(self, binary_file, result_file, memory_range):
        self.binary_file = binary_file
        self.result_file = result_file
        self.memory = [0] * 65536  # 65536 ячеек памяти
        self.memory_range = memory_range

    def run(self):
        with open(self.binary_file, 'rb') as file:
            while command := file.read(5):  # Чтение 5 байт для каждой команды
                print(f"Команда: {command}")
                args = struct.unpack("BBBBB", command)
                print(f"Распакованные аргументы: {args}")
                self.execute_command(args)

        # Создание XML с результатами
        result = ET.Element("result")
        for i in range(self.memory_range[0], self.memory_range[1] + 1):  # Используем заданный диапазон
            mem_elem = ET.SubElement(result, "memory")
            mem_elem.set("address", str(i))
            mem_elem.text = str(self.memory[i])

        ET.indent(result, space="  ", level=0)
        tree = ET.ElementTree(result)
        tree.write(self.result_file)

    def execute_command(self, args):
        a, b, c, d, e = args

        # Объединение старших и младших 8 бит для константы
        constant = (d << 8) | c
        print(f"Обрабатываем команду с опкодом {a}, регистр {b}, константа {constant}")

        if a == 192:  # Загрузка константы
            self.memory[b] = constant
            print(f"Загружена константа {constant} в регистр {b}")

        elif a == 247:  # Чтение значения из памяти
            address = constant  # Адрес из поля C
            if address < len(self.memory):  # Проверка на допустимый адрес
                self.memory[b] = self.memory[address]
                print(f"Прочитано значение из памяти по адресу {address}, загружено в регистр {b}")
            else:
                print(f"Ошибка: адрес {address} выходит за пределы памяти.")

        elif a == 115:  # Запись значения в память
            # Получаем адрес из регистра по адресу B
            base_address = self.memory[b]  # Содержимое регистра по адресу B
            # Добавляем смещение из поля D
            final_address = base_address + d
            # Получаем значение из памяти по адресу C
            value_to_store = self.memory[c]  # Значение из памяти по адресу C
            # Записываем это значение в память по вычисленному адресу
            if final_address < len(self.memory):  # Проверка на допустимость адреса
                self.memory[final_address] = value_to_store
                print(f"Записано значение {value_to_store} в память по адресу {final_address}")
            else:
                print(f"Ошибка: адрес {final_address} выходит за пределы памяти.")

        elif a == 83:  # Бинарная операция "<="
            # Первый операнд - значение из памяти по адресу C
            value1 = self.memory[c]  # Значение из памяти по адресу C

            # Второй операнд - значение в памяти по адресу, вычисленному как D + E
            address2 = self.memory[d] + e  # Адрес для второго операнда
            value2 = self.memory[address2]  # Значение по этому адресу

            # Операция "<=" между двумя операндами
            result = int(value1 <= value2)  # Результат бинарной операции

            # Сохраняем результат в память по адресу B
            self.memory[b] = result
            print(f"Результат бинарной операции '<=' сохранен в регистр {b}: {result}")

        else:
            raise ValueError(f"Неизвестный опкод: {a}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", help="путь к входному бинарному файлу")
    parser.add_argument("output_file", help="путь к выходному файлу для результата (XML)")
    parser.add_argument("memory_range", nargs=2, type=int, help="диапазон памяти для вывода результата (начальный и конечный адрес)")

    args = parser.parse_args()

    interpreter = Interpreter(args.input_file, args.output_file, tuple(args.memory_range))
    interpreter.run()
