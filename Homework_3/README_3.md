** Задание 3 **
Разработать инструмент командной строки для учебного конфигурационного
языка, синтаксис которого приведен далее. Этот инструмент преобразует текст из
входного формата в выходной. Синтаксические ошибки выявляются с выдачей
сообщений.

Входной текст на языке toml принимается из файла, путь к которому задан
ключом командной строки. Выходной текст на учебном конфигурационном
языке попадает в файл, путь к которому задан ключом командной строки.

Многострочные комментарии:

{#

Это многострочный
комментарий

#}

Словари:

struct {

 имя = значение,

 имя = значение,

 имя = значение,

 ...

}

Имена:

[_a-zA-Z]+

Значения:

• Числа.

• Строки.

• Словари.

Строки:

"Это строка"

Объявление константы на этапе трансляции:

имя is значение;

Вычисление константного выражения на этапе трансляции (префиксная форма), пример:

!(+ имя 1)

Результатом вычисления константного выражения является значение.

Для константных вычислений определены операции и функции:

1. Сложение.

2. Вычитание.

3. Умножение.

4. abs().

Все конструкции учебного конфигурационного языка (с учетом их
возможной вложенности) должны быть покрыты тестами. Необходимо показать 3
примера описания конфигураций из разных предметных областей.