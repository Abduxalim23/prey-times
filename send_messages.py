from requests.api import get
from settings import TOKEN,DATA_BASE_NAME
from base_editor import DBConnector
import os
import requests
import time

db = DBConnector(DATA_BASE_NAME)

def send_text_message(message):
    users = db.get_users()
    for user in users:
        send_text = "http://api.telegram.org/bot"+ TOKEN +"/sendMessage?chat_id="+ user['tg_id'] + "&text=" + message
        response = requests.get(send_text)
        print(response.json())
        status = response.ok
        db.update_user_status(status,user['tg_id'])
      
"""
__location__ = os.path.realpath(os.path.join(os.getcwd(),os.path.dirname(__file__)))
print(__location__)
message = open(os.path.join(__location__,"message.txt")) 

text_bot  = message.read() 
"""
start_message = """
Noqulayliklar uchun uzur so'raymiz botda tuzatish ishlari olib borildi. Botni qayta ishga tushirish uchun menudan /start ni bosing.
"""
# run
send_text_message(start_message)

