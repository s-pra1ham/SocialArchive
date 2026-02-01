import requests
from datetime import datetime

time = int(datetime.now().timestamp())
payload = {
    'username': 'your_username',
    'enc_password': f'#PWD_INSTAGRAM_BROWSER:0:{time}:your_password'
}

with requests.Session() as s:
    s.get("https://www.instagram.com/accounts/login/")
    csrf = s.cookies['csrftoken']
    login = s.post("https://www.instagram.com/accounts/login/ajax/", 
                   data=payload, headers={"x-csrftoken": csrf})
    print(s.cookies.get("sessionid"))  # Extract sessionid after login   