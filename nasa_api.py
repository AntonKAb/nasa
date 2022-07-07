# в скрипте будет использоваться специальная библиотека nasapy
# для работы с данными предоставляемыми NASA
import datetime
import json
import os
import statistics
import sys
import argparse
import nasapy
import pathlib


def photo_loader(date):

    # вычисляем начало и конец недели: week_begin и week_end
    date_d = datetime.datetime.strptime(date, "%Y-%m-%d")
    week_begin = date_d - datetime.timedelta(days=(date_d.weekday()))
    week_end = week_begin + datetime.timedelta(days=6)

    directories = directory_creator(week_begin)
    data_dir = directories[0]   # дирректория для хранения данных по дням
    stat_dir = directories[1]   # дирректория для хранения статистики

    api_key = 'DTd6KuX8SMBa3GvzyaRBoZZHjGc785xutfeBwE64'

    # запрос
    nasa_req = nasapy.Nasa(key=api_key)
    request = nasa_req.mars_rover(earth_date=date)

    # проверка наличия фотографий на дату
    if len(request) == 0:
        massage = "No photo is avaliable."
        print(massage)
    else:
        # формируем словарь, где ключ - камера ровера, значение - список фото
        photo = {}
        for element in request:
            rover_name = element['rover']['name']
            cam = element['camera']['name']
            key = rover_name.lower() + '.' + cam.lower()
            if key not in photo.keys():
                photo[key] = []
            photo[key].append({'id': element['id'],
                               'sol': element['sol'],
                               'picture': element['img_src']
                               })

        # создаем json файлы для каждой камеры и записываем список фотографий
        for key in photo:

            file_name = key + '-' + date
            file_path = pathlib.Path(data_dir, file_name + '.json')
            with open(file_path, 'w') as file:
                file.write(json.dumps(photo[key]))

        photo_week(week_begin, week_end, stat_dir, data_dir)


def photo_week(week_begin, week_end, stat_dir, data_dir):
    # формируем список дат по дням недели
    dates = []
    delta_time = week_end - week_begin
    for i in range(delta_time.days + 1):
        weekday = str((week_begin + datetime.timedelta(i)).date())
        dates.append(weekday)

    # выбираем файлы с данными, которые соответсвуют текущей неделе
    needed_files = os.listdir(data_dir)

    # формируем словарь:{масросоход:{камера:[список количества фото]}}
    stat_ = {}
    for file_1 in needed_files:

        file_path = pathlib.Path(data_dir, file_1)
        with open(file_path) as f:
            file_contents = json.load(f)

        rover_name = file_1[:file_1.index('.')]
        camera_name = file_1[file_1.index('.')+1:file_1.index('-')]
        photos_per_camera = len(file_contents)

        if rover_name not in stat_.keys():
            stat_[rover_name] = {}

        if rover_name in stat_.keys():
            if camera_name in stat_[rover_name].keys():
                stat_[rover_name][camera_name].append(photos_per_camera)
            else:
                stat_[rover_name][camera_name] = [photos_per_camera]

    # находим статисику по камерам и записываем в json
    date_for_name = str(week_begin.date())

    for rover in stat_:
        camera_stats = stat_[rover]
        to_write = []

        for key in camera_stats:
            stat_list = camera_stats[key]
            to_write.append(dict(
                camera_name=key.upper(),
                avg_photos_amount=statistics.mean(stat_list),
                min_photos_amount=min(stat_list),
                max_photos_amount=max(stat_list),
                total_photos_amount=sum(stat_list)
            ))

        file_name = rover + '-' + date_for_name
        #file_path = os.path.normpath(f'{stat_dir}/{file_name}.json')
        file_path = pathlib.Path(stat_dir, file_name + '.json')

        with open(file_path, 'w') as file:
            file.write(json.dumps(to_write))


# функция для создания папок хранения данных
def directory_creator(date_begin):
    week = str(date_begin.date())
    data_dir = 'data-' + week
    stat_dir = 'statistic-' + week
    direcrories = [data_dir, stat_dir]
    try:
        os.mkdir(data_dir)
        os.mkdir(stat_dir)
    except FileExistsError:
        pass
    return direcrories


def create_parser():
    date_default = str(datetime.datetime.today().date())
    input_parser = argparse.ArgumentParser()
    input_parser.add_argument('date', nargs='?', default=date_default)
    return input_parser


if __name__ == '__main__':
    parser = create_parser()
    date_arg = parser.parse_args(sys.argv[1:])
    photo_loader(date_arg.date)
