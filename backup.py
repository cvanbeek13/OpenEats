#!/usr/bin/env python3

# Creates a backup for the OpenEats database and images
#
# In order for this to work the working directory needs to be the OpenEats folder.
# The script will first create and zip a temporary backup and then upload the backup
# to Google Drive.  This means an API key will need to be added to the env_prod.list file

import os
import shutil
import subprocess
import sys

from datetime import datetime


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
    # GOOGLE_API_KEY = vars_dict['GOOGLE_API_KEY']
    DATABASE_NAME = vars_dict['MYSQL_DATABASE'] if 'MYSQL_DATABASE' in vars_dict else "openeats"
    DATABASE_USER = vars_dict['MYSQL_USER'] if 'MYSQL_USER' in vars_dict else "openeats"
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
