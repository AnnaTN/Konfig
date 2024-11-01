import toml
import re
import argparse

def check_line(line):
    if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*\s*=\s*(("[^"\\]*(?:\\.[^"\\]*)*")|true|false|-?\d+(\.\d+)?)\s*$', line):
        return True
    return False

# Чтение TOML и преобразование в учебный формат
def convert_toml(inf_from_toml):
    result = []
    dict = {}
    flag = False
    flag_2 = False
    for i in inf_from_toml:
        if re.match(r'#.*', i) and not flag_2:
            if inf_from_toml[0] != i:
                result.append('')
            result.append("{#")
            line = i[i.index('#') + 1:]
            line = line[line.index(" ") + 1:]
            result.append(line)
            flag_2 = True
            if flag_2 and inf_from_toml[-1] == i:
                result.append("#}")
        elif flag_2 and i != '' and i[0] == '#':
            line = i[i.index('#') + 1:]
            line = line[line.index(" ") + 1:]
            result.append(line)
        elif flag_2 and i != '' and i[0] != '#':
            result.append("#}")
            result.append('')
            flag_2 = False

        if not flag and not i: # словарь не открыт и строа пустая
            continue
        elif re.match(r'\[.*\]', i):
            result.append('')
            result.append(i[1:-1] + " is struct {")
            flag = True
        # операции с переменными
        elif len(i) >= 1 and re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*\s*=\s*"\!\((\+|\*|-|abs)\s+[a-zA-Z_][a-zA-Z0-9_]*\s*\d*\)"$', i):
            if i.split()[2][-1] in ['+', '-', '*']:
                value = i.split()[-1]
                value = value[:value.index(')')]
                num = int(value) if value.isdigit() else float(value)

            if i.split()[2][-1] == '+':
                dict[i.split()[-2]] = dict[i.split()[-2]] + num
            elif i.split()[2][-1] == '*':
                dict[i.split()[-2]] = dict[i.split()[-2]] * num
            elif i.split()[2][-1] == '-':
                dict[i.split()[-2]] = dict[i.split()[-2]] - num
            elif i.split()[2][-3] + i.split()[2][-2] + i.split()[2][-1] == "abs":
                 dict[i.split()[-1][:i.split()[-1].index(')')]] = abs(dict[i.split()[-1][:i.split()[-1].index(')')]])
            if i.split()[2][-3] + i.split()[2][-2] + i.split()[2][-1] != "abs":
                result.append(i.split()[0] + " = " + str(dict[i.split()[-2]]))
            else:
                result.append(i.split()[0] + " = " + str(dict[i.split()[-1][:i.split()[-1].index(')')]]))

        elif check_line(i):
            if flag: result.append("  " + i.split()[0] + " is " + i.split()[-1])
            else: result.append(i.split()[0] + " is " + i.split()[-1])
            # регулярное выр-ие для чисел
            if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*\s*=\s*(-?\d+(\.\d+)?|-?\d*\.\d+)\s*$', i):
                value = i.split()[-1]
                if re.match(r'^-?\d+(\.\d+)?$', value):
                    dict[i.split()[0]] = float(value) if '.' in value else int(value)
        elif flag and i == "":
            flag = False
            result.append("}")
    return result


def main(input_file, output_file):
    inf_toml = []
    with open(input_file, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            inf_toml.append(line)
    converted_content = convert_toml(inf_toml)

    with open(output_file, 'w', encoding='utf-8') as file:
        for i in converted_content:
            file.write(i)
            file.write('\n')

# C:\Users\Анна\PycharmProjects\Konfig\Homework_3\main.py -i C:\Users\Анна\PycharmProjects\Konfig\Homework_3\file.toml -o C:\Users\Анна\PycharmProjects\Konfig\Homework_3\result.txt

# Обработка аргументов командной строки
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", required=True)
    parser.add_argument("-o", "--output", required=True, help="Path to output file.")

    args = parser.parse_args()

    main(args.input, args.output)
