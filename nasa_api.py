# в скрипте будет использоваться специальная библиотека nasapy для работы с данными предоставляемыми NASA
import nasapy
import datetime
import json
import os
import statistics


def photo_loader(date=None):

    if date is None:
        date = str(datetime.datetime.today())[:10]

    api_key = 'DTd6KuX8SMBa3GvzyaRBoZZHjGc785xutfeBwE64'

    # запрос
    nasa_req = nasapy.Nasa(key=api_key)
    request = nasa_req.mars_rover(earth_date=date)

    # проверка наличия фотографий на дату
    if len(request) == 0:
        massage = "No photo avaliable."
        print(massage)
        return massage
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
            file_name = key + '-' + date + '.json'
            with open(file_name, 'w') as file:
                file.write(json.dumps(photo[key]))

        photo_week(date)


def photo_week(date='2021-12-08'):
    # вычисляем начало и конец недели
    date = datetime.datetime.strptime(date, "%Y-%m-%d")
    week_begin = date - datetime.timedelta(days=(date.weekday()))  # начало недели
    week_end = week_begin + datetime.timedelta(days=6)  # конец

    # формируем список дат по дням недели
    dates = []
    delta_time = week_end - week_begin
    for i in range(delta_time.days + 1):
        dates.append(str(week_begin + datetime.timedelta(i))[:10])


    # выбираем файлы с данными, которые соответсвуют текущей неделе
    files = os.listdir()

    needed_files = []
    for file_name in files:
        for date in dates:
            if ('-' + date) in file_name and file_name.count('.') == 2:
                needed_files.append(file_name)

    # формируем словарь: масросоход-{камера-список количества сделанных фото}
    stat_ = {}
    for file_1 in needed_files:
        with open(file_1) as f:
            file_contents = json.load(f)

        rover_name = file_1[:file_1.index('.')]
        camera_name = file_1[file_1.index('.')+1:file_1.index('-')]
        photos_per_camera = len(file_contents)

        if rover_name not in stat_.keys():
            stat_[rover_name] = {}
        if rover_name in stat_.keys() and camera_name not in stat_[rover_name].keys():
            stat_[rover_name][camera_name] = [photos_per_camera]
        if rover_name in stat_.keys() and camera_name in stat_[rover_name].keys():
            stat_[rover_name][camera_name].append(photos_per_camera)

    # находим статисику по камерам и записываем в json
    date_for_name = str(week_begin)[:10]
    for rover in stat_:
        camera_stats = stat_[rover]
        to_write = []
        # print(camera_stats)
        for key in camera_stats:
            to_write.append(dict(camera_name=key.upper(), avg_photos_amount=statistics.mean(camera_stats[key]),
                                 min_photos_amount=min(camera_stats[key]), max_photos_amount=max(camera_stats[key]),
                                 total_photos_amount=sum(camera_stats[key])))

        file_name = rover + '-' + date_for_name + '.json'
        # print(file_name)
        with open(file_name, 'w') as file:
            file.write(json.dumps(to_write))


def main():
    date = '2019-10-18'
    photo_loader(date)


if __name__ == '__main__':
    main()
