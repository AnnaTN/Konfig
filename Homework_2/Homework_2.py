import os
import urllib.request
import json
import yaml


def build_graphviz_code(dependency_graph):
    """Создание кода Graphviz на основе графа зависимостей."""
    code = "digraph Dependencies {\n"  # Начало Graphviz графа
    for pkg, deps in dependency_graph.items():  # Проходим по каждому пакету и его зависимостям
        for dep in deps:  # Проходим по каждой зависимости пакета
            code += f'    "{pkg}" -> "{dep}"\n'  # Добавляем строку, которая определяет зависимость между двумя узлами
    code += "}\n"  # Завершаем описание графа
    return code  # Возвращаем сгенерированный код Graphviz



def fetch_npm_dependencies(pkg_name):
    """Получение зависимостей пакета с npm registry."""
    npm_url = f'https://registry.npmjs.org/{pkg_name}'
    try:
        with urllib.request.urlopen(npm_url) as response:
            if response.status != 200:
                raise Exception(f"Ошибка получения данных пакета: {response.status}")
            package_info = json.loads(response.read().decode())
    except urllib.error.URLError as e:
        raise Exception(f"Ошибка сети или неверный URL: {e}")
    except json.JSONDecodeError:
        raise Exception("Ошибка разбора JSON ответа.")

    latest_version = package_info['dist-tags']['latest']
    return package_info['versions'][latest_version].get('dependencies', {})


def resolve_dependencies(pkg_name, accumulated_deps):
    """Рекурсивное получение зависимостей и их транзитивных зависимостей."""
    if pkg_name in accumulated_deps:
        return accumulated_deps

    try:
        dependencies = fetch_npm_dependencies(pkg_name)
        accumulated_deps[pkg_name] = dependencies
        for dep in dependencies:
            resolve_dependencies(dep, accumulated_deps)
    except Exception as e:
        print(f"Ошибка обработки пакета {pkg_name}: {e}")
    return accumulated_deps


def write_to_file(file_path, data):
    """Запись данных в файл."""
    try:
        with open(file_path, 'w') as file:
            file.write(data)
        print(f"Данные успешно сохранены в {file_path}")
    except IOError as err:
        print(f"Ошибка записи файла: {err}")


def run():
    # Чтение данных конфигурации
    config_filename = 'hw_2.yaml'
    try:
        with open(config_filename, 'r') as config_file:
            settings = yaml.safe_load(config_file)
    except FileNotFoundError:
        print(f"Файл конфигурации {config_filename} не найден.")
        return
    except yaml.YAMLError as err:
        print(f"Ошибка разбора YAML файла: {err}")
        return

    # Извлечение параметров конфигурации
    graphviz_bin = settings.get('graphviz_path')
    npm_package = settings.get('package_name')
    output_file = settings.get('path_to_result_file')

    if not all([graphviz_bin, npm_package, output_file]):
        print("Ошибка: Убедитесь, что все обязательные поля указаны в конфигурации (graphviz_path, package_name, path_to_result_file).")
        return

    # Получение зависимостей пакета
    print(f"Получение зависимостей пакета {npm_package}...")
    dependencies = resolve_dependencies(npm_package, {})

    # Генерация Graphviz кода
    graphviz_output = build_graphviz_code(dependencies)

    # Отображение кода
    print("Сгенерированный Graphviz код:")
    print(graphviz_output)

    # Запись кода в файл
    write_to_file(output_file, graphviz_output)

    # Генерация изображения с помощью Graphviz, если указано
    if os.path.exists(graphviz_bin):
        try:
            os.system(f'"{graphviz_bin}" -Tpng {output_file} -o output.png')
            print(f"Визуализация графа завершена, результат сохранен в 'output.png'.")
        except Exception as err:
            print(f"Ошибка выполнения Graphviz: {err}")
    else:
        print(f"Путь к Graphviz не найден: {graphviz_bin}")


if __name__ == '__main__':
    run()
