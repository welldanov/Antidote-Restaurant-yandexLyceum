import os
import sys
import requests
import random

signs = ['plus', 'mines']
numbers = [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08]
small_numbers = [0.01, 0.015, 0.02, 0.025, 0.03, 0.035]


def adjustment_of_coordinates(coordinates):
    coordinates = coordinates.split(',')
    sign = random.choice(signs)
    if sign == 'plus':
        first = float(coordinates[0]) + random.choice(numbers)
        sign = random.choice(signs)
        if sign == 'plus':
            second = float(coordinates[1]) + random.choice(small_numbers)
        else:
            second = float(coordinates[1]) - random.choice(small_numbers)
    else:
        first = float(coordinates[0]) - random.choice(numbers)
        sign = random.choice(signs)
        if sign == 'plus':
            second = float(coordinates[1]) + random.choice(small_numbers)
        else:
            second = float(coordinates[1]) - random.choice(small_numbers)
    coordinates = str(first) + "," + str(second)
    return coordinates


def map_photo(coordinates):
    file = "C:\\Users\\Aidar\\PycharmProjects\\Website\\static\\img\\map\\map.png"
    check_file = os.path.isfile(file)
    # проверяем, существует ли map.png
    if check_file:
        os.remove(file)

    first_mark = adjustment_of_coordinates(coordinates)
    second_mark = adjustment_of_coordinates(coordinates)
    third_mark = adjustment_of_coordinates(coordinates)

    response = None

    map_request = f"https://static-maps.yandex.ru/1.x/?ll={coordinates}&spn=0.09,0.09&l=map&" \
                  f"pt={first_mark},comma~{second_mark},comma~{third_mark},comma"
    response = requests.get(map_request)
    if not response:
        print("Ошибка выполнения запроса:")
        print(map_request)
        print("Http статус:", response.status_code, "(", response.reason, ")")
        sys.exit(1)
    # Запишем полученное изображение в файл.
    map_file = "C:\\Users\\Aidar\\PycharmProjects\\Website\\static\\img\\map\\map.png"
    with open(map_file, "wb") as file:
        file.write(response.content)

    file.close()
    return True
