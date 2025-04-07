# 📸 VKontakte Photo Backup Utility

_A program to backup photos from VKontakte albums to Google Drive and Yandex Disk_

---

## 🔧 Dependencies

The program requires the following Python packages:

| Package    | Purpose                          |
|------------|----------------------------------|
| `requests` | Sending HTTP requests            |
| `json`     | Working with JSON data           |
| `os`       | File system operations           |
| `tqdm`     | Progress bar visualization       |
| `pydrive`  | Google Drive API integration     |

### Installation

pip install requests pydrive tqdm



pip install requests pydrive tqdm

Setup

Before running the program, you will need to perform a few preliminary steps:

Create a project on the Google Cloud Platform and enable the Google Drive API for it. Obtain the client_secrets.json file, which contains your credentials for accessing Google Drive.

Obtain a Yandex Disk token. You can do this on the Yandex.Disk developer page.

Usage

Run the program.

Enter your VKontakte ID.

Enter your Yandex Disk token.

Choose the album to back up the photos from.

Specify the number of photos to back up or enter "none" to copy all photos from the selected album.

The program will start backing up the photos to Google Drive and Yandex Disk. The progress will be displayed.

Upon completion, information about the photos will be saved in a JSON file.

Important
When downloading, the client_secrets.json file has a more extended name. Rename it to client_secrets.json.

Make sure to move it to the same directory as the main script.

Ensure that you have enough free space on Google Drive and Yandex Disk to save the photos.

All photos will be uploaded to a folder named after the selected album on Google Drive and Yandex Disk.

In case of errors or issues, make sure that the data you entered (VKontakte ID, Yandex Disk token, and the path to the client_secrets.json file) is correct.
