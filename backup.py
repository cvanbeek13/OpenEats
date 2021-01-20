#!/usr/bin/env python3

# Creates a backup for the OpenEats database and images
#
# See docs/Taking_and_Restoring_Backups.md for directions on using this script

import errno
import os
import shutil
import subprocess
import sys

from datetime import datetime

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account

# Backup Options
BACKUP_GOOGLE_DRIVE = True

# Other Variables
OPENEATS_DIR = "/home/pi/OpenEats"
TMP_DIR = "/tmp"
ENV_FILE = "env_prod.list"
SQL_DUMP_FILE_NAME = "openeats_dump.sql"
IMAGES_DIR_NAME = "images"


def mkdir(dir):
    try:
        os.mkdir(dir)
    except OSError as e:
        print(f"Problem creating directory at {dir}: {e}", file=sys.stderr)
        exit(1)


def run_process(cmd, shell=False):
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=shell)
    out, err = process.communicate()
    if len(out) > 0:
        print(out)
    if len(err) > 0:
        print(err, file=sys.stderr)
    if process.returncode != 0:
        cmd_string = " ".join(cmd)
        print(f"process ({cmd_string}) exited with code {process.returncode}")
        exit(1)


# Script Start
os.chdir(OPENEATS_DIR)

try:
    with open(ENV_FILE, 'r') as fh:
        vars_dict = dict(
            tuple(line.strip().split('='))
            for line in fh.readlines() if not line.startswith('#') and line.strip()
        )
except Exception as e:
    print(f"Unable to load vars from {ENV_FILE}: {e}", file=sys.stderr)
    exit(1)

try:
    DATABASE_PASSWORD = vars_dict['MYSQL_ROOT_PASSWORD']
    DATABASE_NAME = vars_dict['MYSQL_DATABASE'] if 'MYSQL_DATABASE' in vars_dict else "openeats"
    DATABASE_USER = vars_dict['MYSQL_USER'] if 'MYSQL_USER' in vars_dict else "openeats"
    if BACKUP_GOOGLE_DRIVE:
        GOOGLE_DRIVE_CREDENTIALS_FILE = vars_dict['GOOGLE_DRIVE_CREDENTIALS_FILE']
        GOOGLE_DRIVE_BACKUP_FOLDER_ID = vars_dict['GOOGLE_DRIVE_BACKUP_FOLDER_ID']
except KeyError as e:
    print(f"MYSQL_ROOT_PASSWORD or GOOGLE_API_KEY missing from {ENV_FILE}: {e}", file=sys.stderr)
    exit(1)


backup_name = datetime.now().strftime("openeats-%Y-%m-%d_%H_%M")
backup_dir = os.path.join(TMP_DIR, backup_name)

mkdir(backup_dir)

# Get a SQL dump from the MySQL Database.
# Note that my Fork hosts the database on the RPi, not Docker for me the command is:
# mysqldump openeats -u openeats -p"<PASSWORD>" > dump.sql
dump_cmd = f"mysqldump {DATABASE_NAME} -u {DATABASE_USER} --password='{DATABASE_PASSWORD}' > {os.path.join(backup_dir, SQL_DUMP_FILE_NAME)}"
run_process(dump_cmd, shell=True)

# Backup the images
images_dir = os.path.join(backup_dir, IMAGES_DIR_NAME)
mkdir(images_dir)
img_cp_cmd = ["docker", "cp", "openeats_api_1:/code/site-media/", images_dir]
run_process(img_cp_cmd)

# Zip the folder
backup_zip = shutil.make_archive(backup_dir, 'zip', backup_dir)
shutil.rmtree(backup_dir)

drive_backup_failure = False
if BACKUP_GOOGLE_DRIVE:
    try:
        if not os.path.exists(GOOGLE_DRIVE_CREDENTIALS_FILE):
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), GOOGLE_DRIVE_CREDENTIALS_FILE)

        # Load the creds and create the service
        SCOPES = ['https://www.googleapis.com/auth/drive.file']
        creds = service_account.Credentials.from_service_account_file(GOOGLE_DRIVE_CREDENTIALS_FILE, scopes=SCOPES)
        service = build('drive', 'v3', credentials=creds)

        print(f"Uploading file {backup_zip} to Google Drive...")
        _, drive_file_name = os.path.split(backup_zip)

        # Create and send the file creation request
        body = {
            'name': drive_file_name,
            'parents': [GOOGLE_DRIVE_BACKUP_FOLDER_ID]
        }
        media = MediaFileUpload(backup_zip, mimetype='application/zip')
        drive_file = service.files().create(body=body, media_body=media).execute()

        print(f"Created file {drive_file.get('name')} id {drive_file.get('id')}.")

    except Exception as e:
        print(f"Unable to upload {backup_zip} to Google Drive: {e}")
        drive_backup_failure = True

if BACKUP_GOOGLE_DRIVE:
    os.remove(backup_zip)

exit(drive_backup_failure)
