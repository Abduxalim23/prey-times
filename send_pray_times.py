import datetime
import time

from geopy import location
from base_editor import DBConnector
from settings import DATA_BASE_NAME,TOKEN
from praytimes_calculation import PrayTimes
from language import LANGUAGES
import requests
import functions


class Send_Preytime_EveryDay():
    def __init__(self, *args):
        self.my_db = DBConnector(DATA_BASE_NAME)
        self.praytimes = PrayTimes(method="MWL")
        self.costant_time = datetime.time(19,30,0)

  

    def send_prey_time(self):
        from datetime import date,timedelta
        users = self.my_db.get_users()
        for user in users:
            user_lang = user['lang']
            dis = self.my_db.get_one_district(user['dis_id'],user_lang)
            lat = dis['latitude']
            long = dis['longitude']
            lang = LANGUAGES[user_lang]
            t_time = functions.today() + timedelta(days=1)
            times = self.praytimes.getTimes(t_time,(float(lat),float(long)),5)
            message_one = "<b>"+dis['name']+"</b>\n"
            message_one = message_one + str(t_time.day) +" - " + lang['month_names'][t_time.month]+", " + lang['day_names'][t_time.weekday()] +"\n"
            message = ''
            for i in ['Fajr', 'Sunrise', 'Dhuhr', 'Asr', 'Sunset', 'Maghrib', 'Isha', 'Midnight']:
                message +=(lang['pray_names'][i]+ ': '+ times[i.lower()] + '\n')
            
            message = message_one + message
            text = "http://api.telegram.org/bot"+ TOKEN +"/sendMessage?chat_id="+ user['tg_id'] + "&text="+lang['texts']['smt']+"&parse_mode=HTML" 
            requests.get(text)    
            send_text = "http://api.telegram.org/bot"+ TOKEN +"/sendMessage?chat_id="+ user['tg_id'] + "&text=" + message + "&parse_mode=HTML"
            requests.get(send_text)


    def send_message(self):
        while True:
            time.sleep(1)
            current_time = functions.CurrentDate()
            now =datetime.time(current_time.hour,current_time.minute,current_time.second)
            print(now)
            if now == self.costant_time:
                self.send_prey_time()
                False

s = Send_Preytime_EveryDay()
s.send_message()
