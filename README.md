This code represents a program for backing up photos from a selected VKontakte album. The photos are saved to Google Drive and Yandex Disk.

Dependencies
The program requires the installation of the following dependencies:

requests: for sending HTTP requests.
json: for working with JSON data.
os: for working with the file system.
tqdm: for displaying the progress of operations.
pydrive: for working with Google Drive.
You can install the dependencies by executing the following command:


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
