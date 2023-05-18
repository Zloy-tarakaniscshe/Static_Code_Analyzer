from sys import argv
from copy import copy
import os
import re
import ast

# Проверка длины текста

def S001(count, text, path):
    if len(text) > 79:
        print(f'{path}: Line {count+1}: S001 long text')

# Проверка правильности отступов

def S002(count, text, path):
    if (len(text) - len(text.lstrip())) % 4 != 0:
        print(f'{path}: Line {count + 1}: S002 Indentation is not a multiple of four')

# Проверка синтаксиса в части лишних символов

def S003(count, text, path):
    if ';' in text:
        x = text.find(';')
        if "'" not in text[x:] and "#" not in text[:x]:
            print(f'{path}: Line {count + 1}: S003 Unnecessary semicolon')

# Проверка отступов в комментариях

def S004(count, text, path):
    if '#' in text:
        x = text.find('#')
        if text[x-2] != ' ' and x != 0:
            print(f'{path}: Line {count + 1}: S004 At least two spaces required before inline comments')

# Проверка наличия слова to_TODO в комментариях

def S005(count, text, path):
    if 'todo' in text.lower() and '#' in text:
        print(f'{path}: Line {count + 1}: S005 TODO found')

# Проверка лишних пустых строк, не более двух

def S006(count, path):
    print(f'{path}: Line {count + 1}: S006 More than two blank lines used before this line')

# Проверка отступов после объявления класса

def S007(count, text, path):
    if 'def' in text or 'class' in text:
        text = text.lstrip()
        x = text.find(' ')
        if text[x+1] == ' ':
            text = text.split()
            print(f"{path}: Line {count + 1}: S007 Too many spaces after '{text[0]}'")

# Проверка стиля написания названий класса

def S008(count, text, path):
    if 'class' in text:
        x = text.find('(:')
        new_text = text[:x]
        new_text = new_text.split()
        template = f'[A-Z][A-Za-z]*'
        if re.match(template, new_text[1]) == None:
            print(f"{path}: Line {count + 1}: S008 Class name '{new_text[1]}' should use CamelCase")

# Проверка стиля написания названий функций и/или методов

def S009(count, text, path):
    if 'def' in text:
        x = text.find('(')
        new_text = text[:x]
        new_text = new_text.split()
        template = '_*[a-z]+_*[a-z]+'
        if re.match(template, new_text[1]) == None:
            print(f"{path}: Line {count + 1}: S009 Function name '{new_text[1]}' should use snake_case")

# Проверка имен аргументов передаваемых в функцию

def S010(tree):
    arguments_name = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            for arg in node.args.args:
                if arg != ast.arg(None, None):
                    arguments_name.append(arg.arg)
    return arguments_name

# Проверка стиля написания переменных в теле функции

def S011(tree):
    id_name = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            if isinstance(node, ast.Name):
                id_name.append(node.id)
    return id_name

# Проверка изменяемых значений параметров передаваемых в функцию *args/**kwargs

def S012(tree):
    defaults = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            for arg in node.args.args:
                if arg != ast.arg(None, None) and arg.arg != 'self':
                    defaults.append(arg.arg)
    return defaults

# Передаём путь к файлу для чтения и последующей обработки с использованием
# абстрактного синтаксического дерева

def Entrys(path):
    with open(path, 'r') as file:
        new_file = file.read()
        new_file2 = copy(new_file)

        tree = ast.parse(new_file2)

        arguments_name = S010(tree)
        id_name = S011(tree)
        defaults = S012(tree)

        text = new_file.splitlines()
        indents = 0
        for i in range(len(text)):
            S001(i, text[i], path)
            S002(i, text[i], path)
            S003(i, text[i], path)
            S004(i, text[i], path)
            S005(i, text[i], path)
            if len(text[i]) == 0:
                indents += 1
            elif len(text[i]) != 0 and indents <= 2:
                indents = 0
            elif len(text[i]) != 0 and indents > 2:
                S006(i, path)
                indents = 0
            S007(i, text[i], path)
            S008(i, text[i], path)
            S009(i, text[i], path)

            for name in arguments_name:
                if name + '=' in text[i] and name not in id_name and name + '=None' not in text[i]:
                    template = r'_*[a-z]+_[a-z]+'
                    if re.match(template, name) == None:
                        print(f"{path}: Line {i + 1}: S010 Argument name '{name}' should be snake_case")
                        arguments_name.remove(name)

            for name in id_name:
                if name + ' =' in text[i]:
                    template = r'_*[a-z]+_*[a-z]+'
                    if re.match(template, name) == None:
                        print(f"{path}: Line {i + 1}: S011 Variable '{name}' in function should be snake_case")
                        id_name.remove(name)
                        break

            for key in defaults:
                if key + '=[]' in text[i]:
                    print(f'{path}: Line {i + 1}: S012 Default argument value is mutable')
                    defaults.remove(key)
                    break

# Консольный ввод пути к проверяемому одному или нескольким файлам

path = argv[1]
file = os.path.split(path)
if '.py' in file[1]:
    Entrys(path)
else:
    directory_file = os.listdir(path)
    for direct in directory_file:
        if '.py' in direct and 'tests.py' != direct:
            path_new = path + '\\' + direct
            Entrys(path_new)