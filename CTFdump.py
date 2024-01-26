#!/usr/bin/env python3

import requests as req
import os, re, string, sys, json


if len(sys.argv) < 4:
    print('CTFdump [ACCESS_TOKEN_FILE] [BASE_URL] [CTF_PATH]')
    sys.exit()

ACCESS_TOKEN = open(sys.argv[1]).read().strip()
BASE_URL = sys.argv[2]
CTF_PATH = sys.argv[3]

API_URL = BASE_URL + 'api/v1/'
FILES_URL = BASE_URL + 'files/'

s = req.Session()
s.headers.update({'Authorization': f'Token {ACCESS_TOKEN}'})


def folderName(msg: str):
    msg = ''.join(char for char in msg if char in (string.ascii_letters + string.digits + ' '))
    return re.sub(r'\s+', ' ', msg).replace(' ', '_')


def getChallengeInfoList():
    return s.get(
        API_URL + 'challenges', 
        headers = {'Content-Type': 'application/json'}
    ).json()['data']


def getChallengeFiles(challenge_id: int, file_path: str):
    files = []

    r = s.get(
        API_URL + f'challenges/{challenge_id}/files', 
        headers = {'Content-Type': 'application/json'}
    )

    for file_data in r.json()['data']:
        r = s.get(FILES_URL + file_data['location'])
        open(os.path.join(file_path, file_data['location'].rsplit('/')[1]), 'wb').write(r.content)

        files.append(file_data['location'].rsplit('/')[1])

    return [(file, os.path.join(file_path, file)) for file in files]


def getChallengeFlags(challenge_id: int):
    flags = []

    r = s.get(
        API_URL + f'challenges/{challenge_id}/flags', 
        headers = {'Content-Type': 'application/json'}
    )
    for flag_data in r.json()['data']:
        flags.append({
            'data': flag_data['data'], 
            'type': flag_data['type'], 
            'content': flag_data['content']
        })

    return flags


def getChallengeHints(challenge_id: int):
    hints = []

    r = s.get(
        API_URL + f'challenges/{challenge_id}/hints', 
        headers = {'Content-Type': 'application/json'}
    )
    for hint_data in r.json()['data']:
        hints.append({
            'cost': hint_data['cost'], 
            'content': hint_data['content']
        })

    return hints


def getChallengeTags(challenge_id: int):
    r = s.get(
        API_URL + f'challenges/{challenge_id}/tags', 
        headers = {'Content-Type': 'application/json'}
    )

    return [tag_data['value'] for tag_data in r.json()['data']]


def getChallenge(challenge_id: int):
    r = s.get(
        API_URL + f'challenges/{challenge_id}', 
        headers = {'Content-Type': 'application/json'}
    )
    chal_data = r.json()['data']

    chal = {
        'name': chal_data['name'], 
        'category': chal_data['category'], 
        'state': chal_data['state'], 
        'connection_info': chal_data['connection_info']
    }

    # score
    if chal_data['type'] == 'standard':
        chal['type'] = chal_data['type']
        chal['value'] = chal_data['value']
    else:
        chal['type'] = chal_data['type']
        chal['value'] = chal_data['value']
        chal['initial'] = chal_data['initial']
        chal['decay'] = chal_data['decay']
        chal['minimum'] = chal_data['minimum']

    # flags
    chal['flags'] = getChallengeFlags(challenge_id)

    # tags
    chal['tags'] = getChallengeTags(challenge_id)

    dir_name = f'{folderName(chal_data["category"])}/{folderName(chal_data["name"])}'
    os.makedirs(dir_name, exist_ok=True)

    # files
    chal['files'] = getChallengeFiles(challenge_id, dir_name)

    # description
    open(f'{dir_name}/README.md', 'w').write(chal_data['description'])
    chal['description'] = f'{dir_name}/README.md'

    return chal

ori_dir = os.getcwd()

os.makedirs(CTF_PATH, exist_ok=True)
os.chdir(CTF_PATH)

data = []
for chal_info in getChallengeInfoList():
    data.append(getChallenge(chal_info['id']))
open('data.json', 'w').write(json.dumps(data, indent=4))

os.chdir(ori_dir)
