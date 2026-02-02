import requests
from datetime import datetime

time = int(datetime.now().timestamp())
payload = {
    'username': 's.pra1ham',
    'enc_password': f'#PWD_INSTAGRAM_BROWSER:0:{time}:pass#Pratham@G228$'
}

with requests.Session() as s:
    s.get("https://www.instagram.com/accounts/login/")
    csrf = s.cookies['csrftoken']
    login = s.post("https://www.instagram.com/accounts/login/ajax/", 
                   data=payload, headers={"x-csrftoken": csrf})
    print(s.cookies.get("sessionid"))  # Extract sessionid after login   