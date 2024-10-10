import argparse
import json
import os
import yaml


def generate_graphviz_code(graph):
    """Генерация кода для Graphviz из графа зависимостей."""
    graphviz_code = "digraph G {\n"
    for package, deps in graph.items():
        for dep in deps.keys():
            graphviz_code += f'    "{package}" -> "{dep}"\n'
    graphviz_code += "}\n"
    return graphviz_code


def get_local_dependencies(package_name):
    """Получение зависимостей из локального package.json."""
    # Путь к package.json
    package_json_path = os.path.join(os.getcwd(), 'package.json')

    if not os.path.exists(package_json_path):
        raise FileNotFoundError(f"Файл package.json не найден в {os.getcwd()}")

    with open(package_json_path, 'r') as f:
        package_data = json.load(f)

    # Получаем зависимости
    dependencies = package_data.get('dependencies', {})
    dev_dependencies = package_data.get('devDependencies', {})
    return {**dependencies, **dev_dependencies}


def get_transitive_dependencies(package_name, collected):
    """Получение транзитивных зависимостей из локального package.json."""
    if package_name in collected:
        return collected

    try:
        dependencies = get_local_dependencies(package_name)
        collected[package_name] = dependencies
        for dep in dependencies:
            get_transitive_dependencies(dep, collected)
        return collected
    except Exception as e:
        print(e)
        return collected


def save_output_to_file(output_path, content):
    """Сохранение сгенерированного кода в файл."""
    with open(output_path, 'w') as f:
        f.write(content)


def main():
    # Чтение конфигурации из YAML файла
    with open('hw_2.yaml', 'r') as f:
        config = yaml.safe_load(f)

    graphviz_path = config['graphviz_path']
    package_name = config['package_name']
    output_path = config['path_to_result_file']

    # Получение всех зависимостей, включая транзитивные
    all_dependencies = get_transitive_dependencies(package_name, {})

    # Генерация кода Graphviz
    graphviz_code = generate_graphviz_code(all_dependencies)

    # Вывод кода на экран
    print(graphviz_code)

    # Сохранение кода в файл
    save_output_to_file(output_path, graphviz_code)


if __name__ == '__main__':
    main()
