from datetime import  date, datetime, timedelta
import time
import telebot
import ast
from telebot import types
from settings import TOKEN,DATA_BASE_NAME,BOT_USER_NAME,BOT_URL
from base_editor import DBConnector
from praytimes_calculation import PrayTimes
from language import LANGUAGES
import functions
import requests

my_db = DBConnector(DATA_BASE_NAME)
pray_times = PrayTimes(method="MWL")
bot = telebot.TeleBot(TOKEN)


# buttons KeyboardButton
def keyboard(lang):
    key_buttons = types.ReplyKeyboardMarkup(resize_keyboard=True,row_width=3)
    key_buttons.row(
        types.KeyboardButton(lang["buttons"]["btn_today"]),
        types.KeyboardButton(lang["buttons"]["btn_tomorrow"]),
       )
    key_buttons.row(
        types.KeyboardButton(lang["buttons"]["btn_week"]),
        types.KeyboardButton(lang["buttons"]["btn_location"],request_location=True)
    )
    key_buttons.row(
        types.KeyboardButton(lang["buttons"]["btn_set_loc"]),
        types.KeyboardButton(lang["buttons"]["btn_set_lan"]),
    )
    
    return key_buttons


# region buttnlarini xosil qilish
def region_in_buttons(lang):
    regions = my_db.get_all_regions(lang)
    markup = types.InlineKeyboardMarkup(row_width=2)
    count = 0
    for reg in regions:
        if len(regions) > count:
            if not count%2 == 0:
                count = count + 1
                continue
            btn = regions[count + 1]
            markup.row(
            types.InlineKeyboardButton(reg['name'],callback_data="reg" + str(reg['id'])),
            types.InlineKeyboardButton(btn['name'],callback_data="reg" + str(btn['id']))
            )
            count = count + 1
        else:
            markup.row(
            types.InlineKeyboardButton(reg['name'],callback_data="reg" + str(reg['id'])),
            )
        
    markup.add(types.InlineKeyboardButton(LANGUAGES[lang]['buttons']['btn_back'],callback_data="back_reg"))
    return markup

def district_buttons(dis_id,lang):
    dis = my_db.get_all_districts(dis_id,lang)
    markup = types.InlineKeyboardMarkup(row_width=2)
    length = len(dis)
    count = 0
    if length % 2 == 0:
        for reg in dis:
            if len(dis) > count:
                if not count%2 == 0:
                    count = count + 1
                    continue
                btn = dis[count + 1]
                markup.row(
                types.InlineKeyboardButton(reg['name'],callback_data="dis" + str(reg['id'])),
                types.InlineKeyboardButton(btn['name'],callback_data="dis" + str(btn['id']))
                )
                count = count + 1    
    else:
        for reg in dis:
            if len(dis) - 1 > count:
                if not count%2 == 0:
                    count = count + 1
                    continue
                btn = dis[count + 1]
                markup.row(
                types.InlineKeyboardButton(reg['name'],callback_data="dis" + str(reg['id'])),
                types.InlineKeyboardButton(btn['name'],callback_data="dis" + str(btn['id']))
                )
                count = count + 1 
        markup.row(
            types.InlineKeyboardButton(dis[length-1]['name'],callback_data="dis" + str(dis[length-1]['id'])),
            )   
    markup.add(types.InlineKeyboardButton(LANGUAGES[lang]['buttons']['btn_back'],callback_data="back_dis"))
    return markup

def adding_to_base(tg_id,first_name,user_name,lang):
    get = my_db.identify_user(tg_id)
    if get == False:
        my_db.add_user(tg_id,first_name,user_name,lang)
    elif get == True:
        my_db.update_user_lang(lang,tg_id)
        my_db.update_user_status(True,tg_id)
        
def get_user_lang(tg_id):
    lang = my_db.get_user_lang(tg_id)
    return lang['lang']

def replace_character(old_char,new_char,str):
    return str.replace(old_char,new_char)

def get_user_district_id(tg_id):
    id =  my_db.get_user_district_id(tg_id)
    return id['dis_id']

def get_address(lat,long):
    # import module
    from geopy.geocoders import Nominatim
    # initialize Nominatim API
    geolocator = Nominatim(user_agent="geoapiExercises")
    # Latitude & Longitude input
    Latitude = str(lat)
    Longitude = str(long)
    location = geolocator.reverse(Latitude+","+Longitude)
    address = "<b>Manzil: " + location.raw['display_name']+"</b>"
    return address

def pray_time_change(time,lat,long):
    times = pray_times.getTimes(time,(float(lat),float(long)),5)
    for i in ['Fajr', 'Sunrise', 'Dhuhr', 'Asr', 'Sunset', 'Maghrib', 'Isha', 'Midnight']:
        if i == 'Maghrib':
            times[i.lower()] = functions.add5minut(times['sunset'])
        if i == 'Isha':
            times[i.lower()] = functions.add5minut(times[i.lower()])    
    return times

def get_pray_times(type,u_l,user_id,day=0,latt=0,longg=0):
    user_dis_id = get_user_district_id(user_id)
    dis = my_db.get_one_district(user_dis_id,u_l)
    lang = LANGUAGES[u_l]
    #bugungi kun bo'yicha namoz vaqtlarini qaytarish
    if type == "today":
        lat = dis["latitude"]
        long = dis["longitude"]
        now_time = functions.CurrentDate()
        tt=datetime.date(now_time) 
        times = pray_time_change(tt,lat,long)
        message_one = '<b>' + dis["name"] + '</b>\n'
        message_one =message_one + str(tt.day) +" - " + lang['month_names'][tt.month]+", " + lang['day_names'][tt.weekday()] +"\n"
        message = ''
        for i in ['Fajr', 'Sunrise', 'Dhuhr', 'Asr', 'Sunset', 'Maghrib', 'Isha', 'Midnight']:
            message +=(lang['pray_names'][i]+ ': '+ times[i.lower()]  + '\n')
        return message_one + message +"\n"+BOT_USER_NAME
    elif type == "tomorrow":
        lat = dis["latitude"]
        long = dis["longitude"]
        now_time = functions.CurrentDate() 
        tt=datetime.date(now_time) + timedelta(days=1)
        times = pray_time_change(tt,lat,long)
        message_one = '<b>' + dis["name"] + '</b>\n'
        message_one = message_one + str(tt.day) +" - " + lang['month_names'][tt.month]+", " + lang['day_names'][tt.weekday()] +"\n"
        message = ''
        for i in ['Fajr', 'Sunrise', 'Dhuhr', 'Asr', 'Sunset', 'Maghrib', 'Isha', 'Midnight']:
            message +=(lang['pray_names'][i]+ ': '+ times[i.lower()] + '\n')
        return message_one + message +"\n"+BOT_USER_NAME
    elif type == "weekly":
        lat = dis["latitude"]
        long = dis["longitude"]
        now_time = functions.CurrentDate() 
        tt=datetime.date(now_time) + timedelta(days=day)
        times = pray_time_change(tt,lat,long)
        message_one = '<b>' + dis["name"] + '</b>\n'
        message_one = message_one + str(tt.day) +" - " + lang['month_names'][tt.month]+", " + lang['day_names'][tt.weekday()] +"\n"
        message = ''
        for i in ['Fajr', 'Sunrise', 'Dhuhr', 'Asr', 'Sunset', 'Maghrib', 'Isha', 'Midnight']:
            message +=(lang['pray_names'][i]+ ': '+ times[i.lower()] + '\n')
        return message_one + message +"\n"+BOT_USER_NAME 
    elif type == "location":
        lat = latt
        long = longg
        now_time = functions.CurrentDate() 
        tt=datetime.date(now_time)
        times = pray_time_change(tt,lat,long)
        message_one = ''
        message_one = str(tt.day) +" - " + lang['month_names'][tt.month]+", " + lang['day_names'][tt.weekday()] +"\n"
        message = ''
        for i in ['Fajr', 'Sunrise', 'Dhuhr', 'Asr', 'Sunset', 'Maghrib', 'Isha', 'Midnight']:
            message +=(lang['pray_names'][i]+ ': '+ times[i.lower()] + '\n')
        return message_one + message +"\n"+BOT_USER_NAME 

def count_all_user():
    all = my_db.count_all_user()
    return all[0]

def count_active_user():
    all = my_db.count_active_user()
    return all[0]
def count_user_today():
    return my_db.count_user_added_today()
     

@bot.message_handler(commands=['start','stat'])
def handle_start(update):
    if update.text.startswith("/start"):
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(types.InlineKeyboardButton("O'zbek lotin 🇺🇿",callback_data="uzbek"),
        types.InlineKeyboardButton("Ўзбек крил 🇺🇿",callback_data="kril"))
        bot.send_message(chat_id=update.chat.id,text="🇺🇿 Tilni tanlang\n🇺🇿 Тилни танланг",reply_markup=markup,
        parse_mode="HTML")
    elif update.text.startswith("/stat"):
        ur_lang = get_user_lang(update.from_user.id)
        lan_dic = LANGUAGES[ur_lang]
        all_users = count_all_user()
        active_users = count_active_user()
        today_users = count_user_today()
        bot.send_message(chat_id=update.chat.id,text= "{} : {}\n{} : {}\n{} : {}".format(
        lan_dic['texts']['all_users'],all_users,
        lan_dic['texts']['today_users'],today_users,
        lan_dic['texts']['active_users'],active_users),
        parse_mode="HTML")

                


@bot.callback_query_handler(func=lambda update:True)
def region_callback(update):
    try:
        call = update.data
        if call == "uzbek" or call == "kril": #Til tanlanganda
            bot.delete_message(update.from_user.id,update.message.id)
            user = update.from_user
            lang = LANGUAGES[update.data]  
            adding_to_base(user.id,user.first_name,user.username,update.data)
            markup = region_in_buttons(update.data)
            bot.send_message(chat_id=user.id, text=lang['texts']['reg_choose']+" 👇👇👇", reply_markup = markup)
        elif call.startswith("reg"): #Viloyat tanlanganda
            bot.delete_message(update.from_user.id,update.message.id)
            reg_id = int(replace_character("reg","",call))
            user = update.from_user
            lang = get_user_lang(user.id)
            markup = district_buttons(reg_id,lang)
            bot.send_message(chat_id=user.id, text=LANGUAGES[lang]['texts']["dis_choose"]+" 👇👇👇", reply_markup = markup)    
        elif call.startswith("dis"): #Tuman tanlanganda
            bot.delete_message(update.from_user.id,update.message.id)
            user_lang = get_user_lang(update.from_user.id)
            lang = LANGUAGES[user_lang]
            dis_id = int(replace_character("dis","",call))
            my_db.update_user_district(int(dis_id),update.from_user.id)
            dis = my_db.get_one_district(dis_id,user_lang)
            dis_name = dis['name']
            bot.send_message(chat_id=update.from_user.id,
            text="{} {}".format(dis_name,lang['texts']['dis_chosen']),reply_markup = keyboard(lang))
        elif call.startswith("back_reg"):
            bot.delete_message(update.from_user.id,update.message.id)
            markup = types.InlineKeyboardMarkup(row_width=2)
            markup.add(types.InlineKeyboardButton("O'zbek lotin 🇺🇿",callback_data="uzbek"),
            types.InlineKeyboardButton("Ўзбек крил 🇺🇿",callback_data="kril"))
            bot.send_message(chat_id=update.from_user.id,text="🇺🇿 Tilni tanlang\n🇺🇿 Тилни танланг",reply_markup=markup,
            parse_mode="HTML")
        elif call.startswith("back_dis"):
            bot.delete_message(update.from_user.id,update.message.id)
            user_lang = get_user_lang(update.from_user.id)
            lang = LANGUAGES[user_lang]
            markup = region_in_buttons(user_lang)
            bot.send_message(chat_id=update.from_user.id, text=lang['texts']['reg_choose']+" 👇👇👇", reply_markup = markup)
        elif call.startswith("set"):
            bot.delete_message(update.from_user.id,update.message.id)
            l = replace_character("set","",call)
            my_db.update_user_lang(l,update.from_user.id)
            bot.send_message(chat_id=update.from_user.id,
            text=l,reply_markup = keyboard(LANGUAGES[l]))
 

    except Exception as e:
        print(e)
@bot.message_handler(func=lambda message: True, content_types=['text'])
def send_today_times(update):
    try:
        user_lang = get_user_lang(update.from_user.id)
        lang = LANGUAGES[user_lang]
        if update.text == lang["buttons"]["btn_today"]:
            text = get_pray_times("today",user_lang,update.from_user.id)
            bot.send_message(update.from_user.id,text,parse_mode="HTML")
        elif update.text == lang["buttons"]["btn_tomorrow"]:
            text = get_pray_times("tomorrow",user_lang,update.from_user.id)
            bot.send_message(update.from_user.id,text,parse_mode="HTML")
        elif update.text == lang["buttons"]["btn_week"]:
            for d in range(7):
                text = get_pray_times("weekly",user_lang,update.from_user.id,d)
                bot.send_message(update.from_user.id,text,parse_mode="HTML")
        elif update.text == lang["buttons"]["btn_set_loc"]:
            bot.send_message(chat_id=update.from_user.id,text=lang["texts"]["message_lang"],reply_markup = types.ReplyKeyboardRemove())           
            markup = region_in_buttons(user_lang)
            bot.send_message(chat_id=update.from_user.id, text=lang['texts']['reg_choose']+" 👇👇👇", reply_markup = markup)
        elif update.text == lang["buttons"]["btn_set_lan"]:
            bot.send_message(chat_id=update.from_user.id,text=lang["texts"]["message_lang"],reply_markup = types.ReplyKeyboardRemove())           
            markup = types.InlineKeyboardMarkup(row_width=2)
            markup.add(types.InlineKeyboardButton("O'zbek lotin 🇺🇿",callback_data="setuzbek"),
            types.InlineKeyboardButton("Ўзбек крил 🇺🇿",callback_data="setkril"))
            bot.send_message(chat_id=update.chat.id,text="🇺🇿 Tilni tanlang\n🇺🇿 Тилни танланг",reply_markup=markup,
            parse_mode="HTML")
    except Exception as e:
        print(e)
        time.sleep(1)

@bot.message_handler(func=lambda message: True, content_types=['location'])
def location_time(update):
    user_lang = get_user_lang(update.from_user.id)
    lang = LANGUAGES[user_lang]
    lat = update.location.latitude
    long = update.location.longitude
    mes = get_address(lat,long)
    bot.send_message(update.from_user.id,mes,parse_mode="HTML")
    text = get_pray_times("location",user_lang,update.from_user.id,latt=lat,longg=long)
    bot.send_message(update.from_user.id,text)

@bot.message_handler(func=lambda message:True,content_types=['audio', 'photo', 'voice', 'video', 'document','sticker'])
def message_sender(update):    
    # download photo in to tmp as image.jpg and send it to user
    if update.content_type == "photo":
        print(update.photo)
        file  = bot.get_file(update.photo[0].file_id)
        downloaded_file = bot.download_file(file.file_path)
        with open("tmp\image.jpg","wb") as new_file:
            new_file.write(downloaded_file)
        kaka = bot.send_photo(update.from_user.id,photo=requests.get(file.file_path),caption=update.caption,parse_mode="HTML")
    if update.content_type == "audio":
        file = bot.get_file(update.audio.file_id)
        downloaded_file = bot.download_file(file.file_path)
        with open("tmp\\audio.mp3","wb") as new_file:
            new_file.write(downloaded_file)
        bot.send_audio(update.from_user.id,audio=open("tmp\\audio.mp3","rb"),caption=update.caption,parse_mode="HTML")
            

while True:
    try:
        bot.polling(non_stop=True,interval=0,timeout=0)
    except :
        time.sleep(10)