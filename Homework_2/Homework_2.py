import os
import requests
import yaml


def generate_graphviz_code(graph):
    """Генерация кода для Graphviz из графа зависимостей."""
    graphviz_code = "digraph G {\n"
    for package, deps in graph.items():
        for dep in deps.keys():
            graphviz_code += f'    "{package}" -> "{dep}"\n'
    graphviz_code += "}\n"
    return graphviz_code


def get_npm_dependencies(package_name):
    """Получение зависимостей пакета через запрос к npm registry."""
    url = f'https://registry.npmjs.org/{package_name}'
    response = requests.get(url)

    if response.status_code != 200:
        raise Exception(f"Не удалось получить данные пакета: {response.status_code}")

    package_data = response.json()
    latest_version = package_data['dist-tags']['latest']
    dependencies = package_data['versions'][latest_version].get('dependencies', {})
    return dependencies


def get_transitive_dependencies(package_name, collected):
    """Рекурсивное получение зависимостей, включая транзитивные."""
    if package_name in collected:
        return collected

    try:
        dependencies = get_npm_dependencies(package_name)
        collected[package_name] = dependencies
        for dep in dependencies:
            get_transitive_dependencies(dep, collected)
        return collected
    except Exception as e:
        print(f"Ошибка при обработке {package_name}: {e}")
        return collected


def save_output_to_file(output_path, content):
    """Сохранение сгенерированного кода в файл."""
    try:
        with open(output_path, 'w') as f:
            f.write(content)
        print(f"Результат сохранен в {output_path}")
    except Exception as e:
        print(f"Ошибка при сохранении в файл: {e}")


def main():
    # Чтение конфигурации из YAML файла
    config_file = 'hw_2.yaml'
    try:
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Файл конфигурации {config_file} не найден.")
        return
    except yaml.YAMLError as e:
        print(f"Ошибка при чтении YAML файла: {e}")
        return

    # Чтение параметров из YAML файла
    graphviz_path = config.get('graphviz_path')
    package_name = config.get('package_name')
    output_path = config.get('path_to_result_file')

    if not all([graphviz_path, package_name, output_path]):
        print("Ошибка: Проверьте, что все необходимые поля (graphviz_path, package_name, path_to_result_file) заданы в YAML файле.")
        return

    # Получение всех зависимостей, включая транзитивные
    print(f"Получение зависимостей для пакета {package_name}...")
    all_dependencies = get_transitive_dependencies(package_name, {})

    # Генерация кода Graphviz
    graphviz_code = generate_graphviz_code(all_dependencies)

    # Вывод кода на экран
    print("Сгенерированный код Graphviz:")
    print(graphviz_code)

    # Сохранение кода в файл
    save_output_to_file(output_path, graphviz_code)

    # Выполнение программы Graphviz для генерации визуализации (если нужно)
    if os.path.exists(graphviz_path):
        try:
            os.system(f'"{graphviz_path}" -Tpng {output_path} -o output.png')
            print(f"Граф был успешно визуализирован и сохранен в 'output.png'.")
        except Exception as e:
            print(f"Ошибка при визуализации: {e}")
    else:
        print(f"Путь к Graphviz не найден: {graphviz_path}")


if __name__ == '__main__':
    main()
