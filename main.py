import json
import re

from bs4 import BeautifulSoup
import requests


URL_template = 'https://www.npmjs.com/package/{}?activeTab=dependencies'

class DependenciesInfo:
    package_name = ""
    depth = 1
    dependencies=[]


    def __init__(self, package_name, depth):
        self.package_name=package_name
        self.depth=depth


    def check_dependencies(self, package_name):
        URL = URL_template.format(package_name)
        page = requests.get(URL)
        if page.status_code != 200: #проверяем, установилось ли соединение
            #  print("ERROR: " + str(page.status_code) + "page: " + package_name)
            pass
        else:
            soup = BeautifulSoup(page.text, "html.parser")  # ищем скрипт в котором находятся все зависимости
            sc = soup.find('script')
            string = sc.string
            ind = string.find('"dependencies":')  # отделяем кусок текста только с зависимостями
            string = string[ind:]
            ind = string.find('}')
            string=string[15:ind]
            dependencies = []  # сюда закидываем окончательные названия завивимостей
            deps = re.findall(r'"[^"]*"', string)
            for i in range(0, len(deps), 2):
                dependencies.append(deps[i][1:-1])
            return dependencies

    def add_dependencies(self, dependence_list, package_name):
            for dependency in dependence_list:
                dependency_str = "\t" + package_name + " -> " + dependency
                self.dependencies.append(dependency_str)


    def execute(self):
        package_list=[self.package_name]
        cur_depth = 0
        while(cur_depth<self.depth and len(package_list)>0):  # пока у зависимостей есть зависимости или не достигли нужного уровня глубины
            new_package_list=[]  # все найденные пакеты кидаем сюда
            for package in package_list:
                dependence_list = self.check_dependencies(package)  # получаем список зависимостей
                if not (dependence_list is None):
                    self.add_dependencies(dependence_list, package)  # добавляем в список для вывода наши зависимости
                    for depend in dependence_list:
                        new_package_list.append(depend) # кидаем в список пакетов
            package_list=new_package_list  # обновляем список пакетов для следующего уровня глубины
            cur_depth=cur_depth+1  # увеличиваем уровень глубины


    def print_dependencies(self):
        self.execute()
        print(f'// "{self.package_name}" package dependencies')
        print(f'digraph {self.package_name}' + " {")
        for formated_dependency in self.dependencies:
            print("\t" + formated_dependency)
        print("}")






name = input()
depth = int(input())
di = DependenciesInfo(name, depth)
di.print_dependencies()

