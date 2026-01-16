#this is a script to automate updating of the changelog
#this script needs to exist in the same directory where git initialized so it access the git logs
#this script writes to a file named CHANGELOG.md so that file must exist for it run properly
#recommended to run in a Python virtual environnment
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

#write to the changelog file
with open(CHANGELOG_FILE, 'a') as changelog_file: 
    changelog_file.write(changelog_entry) 

print (f"Changelog updated: {changelog_entry}")