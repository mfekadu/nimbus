#!/usr/bin/env python3


from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth


gauth = GoogleAuth()
gauth.LocalWebserverAuth()

# Create GoogleDrive instance with authenticated GoogleAuth instance.
drive = GoogleDrive(gauth)


# FILENAME = "bert-base-srl-2020.03.24.tar.gz"

FILENAME = input("filename: ")


# Create GoogleDriveFile instance with title FILENAME.
file1 = drive.CreateFile({"title": FILENAME})
file1.SetContentFile(FILENAME)
file1.Upload()  # Upload the file.


print(f"title: {file1['title']}, id: {file1['id']}")


# title: Hello.txt, id: {{FILE_ID}}
