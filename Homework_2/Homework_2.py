import os
import urllib.request
import json
import yaml

def build_graphviz_code(dict_of_deps):
    # создаем описание графа, которое будет выведено на экран и записано в файл
    code_from_graph = "digraph Dependencies {\n"
    for package, depends in dict_of_deps.items():  # проходим по каждому пакету и его зависимостям
        for dep in depends:  # проходим по каждой зависимости пакета
            code_from_graph += f'  "{package}" -> "{dep}"\n'
    code_from_graph += "}\n"
    return code_from_graph

def get_npm_dependencies(pkg_name):
    # получение зависимостей пакета
    npm_url = f'https://registry.npmjs.org/{pkg_name}' # формируем URL для запроса к npm registry

    try:
        with urllib.request.urlopen(npm_url) as response: # выполняем HTTP-запрос на получение информации о пакете

            # проверка корректности статуса ответа
            if response.status != 200:
                raise Exception(f"Ошибка получения данных пакета: {response.status}")

            package_info = json.loads(response.read().decode()) # читаем и декодируем JSON-ответ

    except urllib.error.URLError as e: # ошибка сети / неверного URL
        raise Exception(f"Ошибка сети или неверный URL: {e}")

    except json.JSONDecodeError: # ошибка, связанная с JSON
        raise Exception("Ошибка разбора JSON ответа.")

    latest_version = package_info['dist-tags']['latest'] # получение последней версии пакета
    return package_info['versions'][latest_version].get('dependencies', {}) # возврат зависимостей пакета

def resolve_dependencies(pkg_name, dict_of_deps):
    # рекурсивное получение зависимостей зависимостей

    if pkg_name in dict_of_deps:
        return dict_of_deps

    try:
        dependencies = get_npm_dependencies(pkg_name)  # зависимости для текущего пакета
        dict_of_deps[pkg_name] = dependencies
        for dep in dependencies:  # рекурсивно проходим по каждой зависимости и собираем для нее свои зависимости
            resolve_dependencies(dep, dict_of_deps)

    except Exception as e:
        print(f"Ошибка обработки пакета {pkg_name}: {e}")

    return dict_of_deps

def write_to_file(file_path, code_of_deps):
    try:
        with open(file_path, 'w') as file:
            file.write(code_of_deps)
        print(f"Данные успешно сохранены в {file_path}")

    except IOError as err:
        print(f"Ошибка записи файла: {err}")


def run():
    # Чтение данных конфигурации
    configuration_filename = 'hw_2.yaml'
    try:
        with open(configuration_filename, 'r') as config_file:
            settings = yaml.safe_load(config_file)  # читаем конфигурацию

    except yaml.YAMLError as err: # другие ошибки
        print(f"Ошибка разбора YAML файла: {err}")
        return

    graphviz_path = settings.get('graphviz_path')
    package_name = settings.get('package_name')
    output_file = settings.get('path_to_result_file')

    # получение зависимостей пакета
    print(f"Происходит получение зависимостей пакета {package_name}")
    dependencies = resolve_dependencies(package_name, {})

    # генерируем Graphviz код на основе зависимостей
    graphviz_output = build_graphviz_code(dependencies)

    print("Сгенерированный Graphviz код:")
    print(graphviz_output)

    # запись кода в файл
    write_to_file(output_file, graphviz_output)

    # генерация изображения с помощью Graphviz
    try:
        os.system(f'"{graphviz_path}" -Tpng {output_file} -o output.png')
        print(f"Визуализация графа завершена, результат сохранен в 'output.png'.")
    except Exception as err:
        print(f"Ошибка выполнения Graphviz: {err}")

if __name__ == '__main__':
    run()
