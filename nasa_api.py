# в скрипте будет использоваться специальная библиотека nasapy для работы с данными предоставляемыми NASA
import datetime
import json
import os
import statistics
import sys
import argparse
import nasapy


def photo_loader(date):

    # вычисляем начало и конец недели
    date_d = datetime.datetime.strptime(date, "%Y-%m-%d")
    week_begin = date_d - datetime.timedelta(days=(date_d.weekday()))  # начало недели
    week_end = week_begin + datetime.timedelta(days=6)  # конец недели

    directories = directory_creator(week_begin)

    api_key = 'DTd6KuX8SMBa3GvzyaRBoZZHjGc785xutfeBwE64'

    # запрос
    nasa_req = nasapy.Nasa(key=api_key)
    request = nasa_req.mars_rover(earth_date=date)

    # проверка наличия фотографий на дату
    if len(request) == 0:
        massage = "No photo avaliable."
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
            file_path = os.path.join(
                directories[0], '%s.%s' % (file_name, 'json')
            )
            with open(file_path, 'w') as file:
                file.write(json.dumps(photo[key]))

        photo_week(week_begin, week_end, directories[1], directories[0])


def photo_week(week_begin, week_end, directory, dataset):
    # формируем список дат по дням недели
    dates = []
    delta_time = week_end - week_begin
    for i in range(delta_time.days + 1):
        dates.append(str((week_begin + datetime.timedelta(i)).date()))

    # выбираем файлы с данными, которые соответсвуют текущей неделе
    files = os.listdir(dataset)

    needed_files = []
    for file_name in files:
        for date in dates:
            if ('-' + date) in file_name and file_name.count('.') == 2:
                needed_files.append(file_name)

    # формируем словарь: масросоход-{камера-список количества сделанных фото}
    stat_ = {}
    for file_1 in needed_files:
        with open(os.path.join(dataset + '\\' + file_1)) as f:
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
        # print(camera_stats)
        for key in camera_stats:
            to_write.append(dict(camera_name=key.upper(), avg_photos_amount=statistics.mean(camera_stats[key]),
                                 min_photos_amount=min(camera_stats[key]), max_photos_amount=max(camera_stats[key]),
                                 total_photos_amount=sum(camera_stats[key])))

        file_name = rover + '-' + date_for_name
        file_path = os.path.join(
            directory, '%s.%s' % (file_name, 'json')
        )
        with open(file_path, 'w') as file:
            file.write(json.dumps(to_write))


# функция для создания папок хранения данных
def directory_creator(date_begin):
    data_dir = 'data-' + str(date_begin.date())
    stat_dir = 'statistic-' + str(date_begin.date())
    direcroties = [data_dir, stat_dir]
    try:
        os.mkdir(data_dir)
        os.mkdir(stat_dir)
    except FileExistsError:
        pass

    return direcroties


def create_parser():
    date_default = str(datetime.datetime.today().date())
    parser = argparse.ArgumentParser()
    parser.add_argument('date', nargs='?', default=date_default)
    return parser


if __name__ == '__main__':
    parser = create_parser()
    date_arg = parser.parse_args(sys.argv[1:])
    photo_loader(date_arg.date)
