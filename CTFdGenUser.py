#!/usr/bin/env python3

from tqdm import trange
import requests as req
import sys, string, random, json

if len(sys.argv) < 5:
    print('CTFdGenUser.py [ACCESS_TOKEN_FILE] [BASE_URL] [STUDENT_FILE] [EMAIL_FILE]')
    sys.exit()

ACCESS_TOKEN = open(sys.argv[1]).read().strip()
BASE_URL = sys.argv[2]

API_URL = BASE_URL + 'api/v1/'

CHARSET = string.ascii_letters + string.digits

student_list = open(sys.argv[3], 'r').read().strip().split('\n')
email_list = open(sys.argv[4], 'r').read().strip().split('\n')

s = req.Session()
s.headers.update({'Authorization': f'Token {ACCESS_TOKEN}'})


data_list = []
for i in trange(len(email_list)):
    password = ''.join(random.choices(CHARSET, k=20))

    s.post(
        API_URL + 'users', 
        headers = {'Content-Type': 'application/json'}, 
        json = {
            'name': f'SCIST_{i:02d}', 
            'email': email_list[i], 
            'password': password
        }
    )

    data_list.append({
        'student': student_list[i], 
        'username': f'SCIST_{i:02d}', 
        'email': email_list[i], 
        'password': password
    })

open('data.json', 'w').write(json.dumps(data_list, indent=4, ensure_ascii=False))
