import requests
import json
import os
from tqdm import tqdm
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive


class VK:
    def __init__(self, access_token, user_id, google_drive_credentials, yandex_token):
        self.access_token = access_token
        self.user_id = user_id
        self.google_drive_credentials = google_drive_credentials
        self.yandex_token = yandex_token

    def backup_vk_photos(self, num_photos=5):
        selected_album = self.select_album()
        if not selected_album:
            print("Нет доступных альбомов для резервного копирования фотографий.")
            return

        # Авторизация на Google Drive
        gauth = GoogleAuth()
        gauth.LocalWebserverAuth()
        drive = GoogleDrive(gauth)

        folder_path = f"VK_Backup_Album_{selected_album['id']}"

        # Проверка и создание папки на Google Drive
        folder_id = self.create_folder_on_google_drive(drive, folder_path)

        # Проверка и создание папки 'backup' на Яндекс Диске
        self.create_folder_on_yandex_disk(folder_path)

        photos = self.get_photos_from_album(selected_album['id'])

        if num_photos == "нет":
            largest_photos = photos
        else:
            try:
                num_photos = int(num_photos)
                largest_photos = sorted(photos, key=lambda x: x['likes']['count'], reverse=True)[:num_photos]
            except ValueError:
                print("Неверное количество фотографий.")
                return

        photo_info = []

        with tqdm(total=len(largest_photos), ncols=70, bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt}') as pbar:
            for photo in largest_photos:
                file_name = f"{photo['likes']['count']}_{photo['id']}.jpg"
                photo_url = photo['sizes'][-1]['url']
                self.download_photo(photo_url, file_name)
                self.upload_photo_to_google_drive(drive, file_name, folder_id)
                self.upload_photo_to_yandex_disk(file_name, folder_path)

                photo_info.append({
                    "file_name": file_name,
                    "size": photo['sizes'][-1]['type']
                })

                os.remove(file_name)
                pbar.update(1)

        json_file_name = f"{selected_album['title']}_photos_info.json"
        with open(json_file_name, 'w') as json_file:
            json.dump(photo_info, json_file)

        print(f"Информация о фотографиях сохранена в файле: {json_file_name}")

    def create_folder_on_google_drive(self, drive, folder_path):
        # Проверка и создание папки на Google Drive
        folder_id = None
        folder_name = os.path.basename(folder_path)
        folder_exists = False

        file_list = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
        for file in file_list:
            if file['title'] == folder_name and file['mimeType'] == 'application/vnd.google-apps.folder':
                folder_exists = True
                folder_id = file['id']
                break

        if not folder_exists:
            folder_metadata = {
                'title': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            folder = drive.CreateFile(folder_metadata)
            folder.Upload()
            folder_id = folder['id']
            print(f"Папка '{folder_path}' успешно создана на Google Drive.")

        return folder_id

    def upload_photo_to_google_drive(self, drive, file_name, folder_id):
        # Загрузка фотографии на Google Drive
        file_path = os.path.join(os.getcwd(), file_name)
        gfile = drive.CreateFile({"title": file_name, "parents": [{"id": folder_id}]})
        gfile.SetContentFile(file_path)
        gfile.Upload()
        print(f"Файл '{file_name}' успешно загружен на Google Drive.")

    def get_photos_from_album(self, album_id):
        # Получение списка фотографий из альбома
        photos_url = "https://api.vk.com/method/photos.get"
        params = {
            "access_token": self.access_token,
            "owner_id": self.user_id,
            "album_id": album_id,
            "extended": 1,
            "photo_sizes": 1,
            "count": 1000,
            "v": "5.131"
        }
        response = requests.get(photos_url, params=params)
        data = response.json()
        photos = data['response']['items']
        return photos

    def select_album(self):
            # Выбор альбома для резервного копирования фотографий
            albums_url = "https://api.vk.com/method/photos.getAlbums"
            params = {
                "access_token": self.access_token,
                "owner_id": self.user_id,
                "need_covers": 1,
                "photo_sizes": 1,
                "v": "5.131"
            }
            response = requests.get(albums_url, params=params)
            data = response.json()
            albums = data['response']['items']

            print("Доступные альбомы:")
            for i, album in enumerate(albums):
                print(f"{i+1}. {album['title']} (id: {album['id']})")

            album_index = input("Введите номер альбома для резервного копирования фотографий: ")
            try:
                album_index = int(album_index)
                if album_index < 1 or album_index > len(albums):
                    print("Неверный номер альбома.")
                    return None
                selected_album = albums[album_index - 1]
                return selected_album
            except ValueError:
                print("Неверный номер альбома.")
                return None

    def download_photo(self, photo_url, file_name):
        # Загрузка фотографии по URL и сохранение на диск
        response = requests.get(photo_url)
        with open(file_name, 'wb') as file:
            file.write(response.content)
        print(f"Фотография '{file_name}' успешно загружена.")

    def upload_photo_to_yandex_disk(self, file_name, folder_path):
        # Загрузка фотографии на Яндекс.Диск
        headers = {'Authorization': f"OAuth {self.yandex_token}"}
        upload_url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        params = {
            'path': f"{folder_path}/{file_name}",
            'overwrite': 'true'
        }
        response = requests.get(upload_url, headers=headers, params=params)
        data = response.json()
        href = data['href']
        with open(file_name, 'rb') as file:
            response = requests.put(href, files={'file': file})
        print(f"Фотография '{file_name}' успешно загружена на Яндекс Диск.")

    def create_folder_on_yandex_disk(self, folder_path):
        # Создание папки на Яндекс Диске
        headers = {'Authorization': f"OAuth {self.yandex_token}"}
        create_folder_url = 'https://cloud-api.yandex.net/v1/disk/resources'
        params = {
            'path': folder_path
        }
        response = requests.put(create_folder_url, headers=headers, params=params)
        if response.status_code == 201:
            print(f"Папка '{folder_path}' успешно создана на Яндекс Диске.")
        elif response.status_code == 409:
            print(f"Папка '{folder_path}' уже существует на Яндекс Диске.")
        else:
            print("Ошибка при создании папки на Яндекс Диске.")

access_token = "vk1.a.HoAJZ5_4N42M2CnU5ld2i9G9E0mz8J1JpAfY9ympybHcv0IQsF4NR5rjMFbXXuWOgUNQ3TZIm4Ffcwk68gJqcy6_JEbYgeY9ldD9QnOHeVJn2gxe0SseJJhHYeWvVkt0k880EjgAAZAQNpzI28b20OkAruykGratm-fzSAmG-mMWfJGX-edi9n7YDmZ1MxQBiK2jCNA1xL9DVk8hZhL9Sw"
user_id = input("Введите свой ID VK: ")
google_drive_credentials = "client_secrets.json"
yandex_token = input("Введите свой токен Яндекс Диска: ")

vk = VK(access_token, user_id, google_drive_credentials, yandex_token)

num_photos = input("Введите количество фотографий для резервного копирования (или 'нет' для копирования всех фотографий): ")
vk.backup_vk_photos(num_photos)
