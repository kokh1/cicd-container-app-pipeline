#this is a script to automate updating of the changelog
#this script needs to exist in the same directory where git initialized so it can access the git log
#this script writes to CHANGELOG.md (unless you set CHANGELOG_FILE to use another file) so ensure it exists
#recommended to run in a Python virtual environnment
#this intended to be run locally after a successful pipeline run to stimulate production
#to run: python3 changelog.py

#import the needed libraries
import os
from datetime import datetime
import subprocess

#path to the changelog file
CHANGELOG_FILE = os.getenv('CHANGELOG_FILE', 'CHANGELOG.md')

#get the latest commit message and SHA
commit_message = subprocess.check_output(['git', 'log', '-1', '--pretty=%B']).decode('utf-8').strip()
commit_sha = subprocess.check_output(['git','log', '-1', '--pretty=%H']).decode('utf-8').strip()

#timestamp of the when the change was made
timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

#entry format for the changelog
changelog_entry = f" ## {timestamp} - {commit_sha}\n\- {commit_message}\n\n"

#read existing content (if file exists)
if os.path.exists(CHANGELOG_FILE):
    with open(CHANGELOG_FILE, 'r') as f:
        previous_entries = f.read()
else:
    previous_entries = ''

#append new entry at top of file
with open (CHANGELOG_FILE, 'w') as f: 
    f.write(changelog_entry + previous_entries)

print (f"Changelog updated: {changelog_entry}")