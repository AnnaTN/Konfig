import struct
import sys

def assemble_command(command):
    parts = command.split()
    op_code = int(parts[0])  # Получаем код операции

    binary_command = None

    if op_code == 192:  # Загрузка константы
        A = op_code
        B = int(parts[1])
        C = int(parts[2])
        # Формат команды: [A, B, C], 5 байт
        binary_command = struct.pack('BII', A, B, C)

    elif op_code == 247:  # Чтение значения из памяти
        A = op_code
        B = int(parts[1])
        C = int(parts[2])
        # Формат команды: [A, B, C], 5 байт
        binary_command = struct.pack('BII', A, B, C)

    elif op_code == 115:  # Запись значения в память
        A = op_code
        B = int(parts[1])
        C = int(parts[2])
        D = int(parts[3])
        # Формат команды: [A, B, C, D], 5 байт
        binary_command = struct.pack('BIII', A, B, C, D)

    elif op_code == 83:  # Бинарная операция "<="
        A = op_code
        B = int(parts[1])
        C = int(parts[2])
        D = int(parts[3])
        E = int(parts[4])
        # Формат команды: [A, B, C, D, E], 5 байт
        binary_command = struct.pack('BIIII', A, B, C, D, E)

    else:
        raise ValueError(f"Неизвестный код операции: {op_code}")

    return binary_command


def assemble(input_file, output_file, log_file):
    commands = []
    # Открываем входной файл и считываем команды
    with open(input_file, 'r') as infile:
        for line in infile:
            # обработка каждой строки
            line = line.strip()  # если нужно убрать символ новой строки
            commands.append(line)
    print(commands)

    # Создадим список для логирования команд
    log_data = []

    # Открываем выходной файл для записи бинарных данных
    with open(output_file, 'wb') as outfile:
        for command in commands:
            # Собираем бинарные данные для команды
            binary_command = assemble_command(command)

            # Записываем команду в файл
            outfile.write(binary_command)

            # Формируем строку для лога в формате "0xC0, 0x29, 0xE3, 0x00, 0x00"
            log_string = ", ".join([f"0x{byte:02X}" for byte in binary_command])
            print(command, binary_command)
            # Добавляем запись в список
            log_data.append(f"Тест ({command}):\n{log_string}")

    # Записываем лог в текстовый файл с правильной кодировкой UTF-8
    with open(log_file, 'w', encoding='utf-8') as log_text:
        log_text.write("\n\n".join(log_data))


def main():
    if len(sys.argv) != 4:
        print("Usage: python assembler.py <input_file> <output_file> <log_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    log_file = sys.argv[3]

    assemble(input_file, output_file, log_file)
    print(f"Assembly completed. Binary output saved to {output_file} and log saved to {log_file}")


if __name__ == "__main__":
    main()
