from api import YandexAPI, HttpException, VkAPI
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
        self.vk_api = VkAPI(access_token)

    def backup_vk_photos(self, num_photos=5):
        selected_album = self.select_album()
        if not selected_album:
            print("No available albums for backing up photos.")
            return

        # Google Drive authentication
        gauth = GoogleAuth()
        gauth.LocalWebserverAuth()
        drive = GoogleDrive(gauth)

        folder_path = f"VK_Backup_Album_{selected_album['id']}"

        # Check and create folder on Google Drive
        folder_id = self.create_folder_on_google_drive(drive, folder_path)

        # Check and create 'backup' folder on Yandex.Disk
        self.create_folder_on_yandex_disk(folder_path)

        photos = self.get_photos_from_album(selected_album['id'])

        if num_photos == "none":
            largest_photos = photos
        else:
            try:
                num_photos = int(num_photos)
                largest_photos = sorted(photos, key=lambda x: x['likes']['count'], reverse=True)[:num_photos]
            except ValueError:
                print("Invalid number of photos.")
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

        print(f"Information about the photos has been saved in the file: {json_file_name}")

    def create_folder_on_google_drive(self, drive, folder_path):
        # Check and create folder on Google Drive
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
            print(f"Folder '{folder_path}' has been successfully created on Google Drive.")

        return folder_id

    def upload_photo_to_google_drive(self, drive, file_name, folder_id):
        # Upload photo to Google Drive
        file_path = os.path.join(os.getcwd(), file_name)
        gfile = drive.CreateFile({"title": file_name, "parents": [{"id": folder_id}]})
        gfile.SetContentFile(file_path)
        gfile.Upload()
        print(f"File '{file_name}' has been successfully uploaded to Google Drive.")

    def get_photos_from_album(self, album_id):
        # Get a list of photos from the album
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
        # Select album for backing up photos
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

        print("Available albums:")
        for i, album in enumerate(albums):
            print(f"{i+1}. {album['title']} (id: {album['id']})")

        album_index = input("Enter the album number to backup photos: ")
        try:
            album_index = int(album_index)
            if album_index < 1 or album_index > len(albums):
                print("Invalid album number.")
                return None
            selected_album = albums[album_index - 1]
            return selected_album
        except ValueError:
            print("Invalid album number.")
            return None

    def download_photo(self, photo_url, file_name):
        # Download photo from URL and save to disk
        response = requests.get(photo_url)
        with open(file_name, 'wb') as file:
            file.write(response.content)
        print(f"Photo '{file_name}' has been successfully downloaded.")

    def upload_photo_to_yandex_disk(self, file_name, folder_path):
        # Upload photo to Yandex.Disk
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
        print(f"Photo '{file_name}' has been successfully uploaded to Yandex.Disk.")

    def create_folder_on_yandex_disk(self, folder_path):
        # Create folder on Yandex.Disk
        headers = {'Authorization': f"OAuth {self.yandex_token}"}
        create_folder_url = 'https://cloud-api.yandex.net/v1/disk/resources'
        params = {
            'path': folder_path
        }
        response = requests.put(create_folder_url, headers=headers, params=params)
        if response.status_code == 201:
            print(f"Folder '{folder_path}' has been successfully created on Yandex.Disk.")
        elif response.status_code == 409:
            print(f"Folder '{folder_path}' already exists on Yandex.Disk.")
        else:
            print("Error creating folder on Yandex.Disk.")

access_token = "vk1.a.HoAJZ5_4N42M2CnU5ld2i9G9E0mz8J1JpAfY9ympybHcv0IQsF4NR5rjMFbXXuWOgUNQ3TZIm4Ffcwk68gJqcy6_JEbYgeY9ldD9QnOHeVJn2gxe0SseJJhHYeWvVkt0k880EjgAAZAQNpzI28b20OkAruykGratm-fzSAmG-mMWfJGX-edi9n7YDmZ1MxQBiK2jCNA1xL9DVk8hZhL9Sw"
user_id = input("Enter your VK ID: ")
google_drive_credentials = "client_secrets.json"
yandex_token = input("Enter your Yandex.Disk token: ")

vk = VK(access_token, user_id, google_drive_credentials, yandex_token)

num_photos = input("Enter the number of photos to backup (or 'none' to backup all photos): ")
vk.backup_vk_photos(num_photos)
