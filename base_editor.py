import datetime
import sqlite3
import functions 



class DBConnector:
    def __init__(self,db_name):
        self.conn = sqlite3.connect(db_name,check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

    def get_all_regions(self,lang):
        try:
            if lang == "uzbek":
                return self.cursor.execute("select id,name from regions order by name").fetchall()
            elif lang == 'kril':
                return self.cursor.execute("select id,name_kril as name from regions order by name").fetchall()
        except Exception as e:
            print(e)

    def get_all_districts(self,region_id,lang):
        try:
            if lang == 'uzbek':
                return self.cursor.execute("select id,name from districs where region_id=? order by name",(region_id,)).fetchall()
            elif lang == 'kril':
                return self.cursor.execute("select id,name_kril as name from districs where region_id=? order by name",(region_id,)).fetchall()
        except Exception as e:
            print(e)   

    def get_user(self,tg_id):
        try:
            return self.cursor.execute("select * from users where tg_id=?",(tg_id,)).fetchone()
        except Exception as e:
            print(e)
    def get_one_district(self,dis_id,lang):
        try:
            if lang =='uzbek':
                return self.cursor.execute("select id,name,region_id,latitude,longitude from districs where id=?",(dis_id,)).fetchone()
            elif lang == 'kril':
                return self.cursor.execute("select id,name_kril as name,region_id,latitude,longitude from districs where id=?",(dis_id,)).fetchone()
        except Exception as e:
            print(e)
    
    def count_all_user(self):
        try:
            return self.cursor.execute("select count(*) from users").fetchone()
        except Exception as e:
            return e
    
    def count_active_user(self):
        try:
             return self.cursor.execute("select count(*) from users where status = ?",("1",)).fetchone()
        except Exception as e:
            return e

    def count_user_added_today(self):
        try:
            user =  self.cursor.execute("select id,add_time from users").fetchall()
            day = functions.CurrentDate().date().day
            count = 0
            for item in user:               
                t = datetime.datetime.strptime(item["add_time"],"%Y-%m-%d %H:%M:%S")
                if t.day == day:
                    count = count + 1
            return count
        except Exception as e:
            return e

    def identify_user(self,tg_id):
        try:
            collacate = self.cursor.execute("select exists(select 1 from users where tg_id =? collate nocase)",(tg_id,)).fetchone()
            if collacate[0] == 1:
                return True
            else:
                return False
        except Exception as e:
            print(e)

    def add_user(self,tg_id,first_name,user_name,lang):
        try:
            timed = functions.CurrentDate()
            self.cursor.execute("insert into users(tg_id,first_name,user_name,add_time,status,lang) values(?,?,?,?,1,?)",(tg_id,first_name,user_name,timed,lang))
            self.conn.commit()
        except Exception as e:
            print(e)
    def get_users(self):
        try:
            return self.cursor.execute("select * from users where status = 1").fetchall()
        except Exception as e:
            print(e)          
    
    def update_user_status(self,status,tg_id):
        try:
            self.cursor.execute("update users set status = ? where tg_id = ?",(status,tg_id))
            self.conn.commit()
        except Exception as e:
            print(e)
    
    def get_user_lang(self,tg_id):
        try:
           return self.cursor.execute("select * from users where tg_id=?",(tg_id,)).fetchone()
        except Exception as e:
            print(e)

    def update_user_district(self,dis_id,tg_id):
        try:
            self.cursor.execute("update users set dis_id = ? where tg_id = ?",(int(dis_id),tg_id))
            self.conn.commit()
        except Exception as e:
            print(e)

    def update_user_lang(self,lang,tg_id):
        try:
            self.cursor.execute("update users set lang = ?  where tg_id = ?",(lang,tg_id))
            self.conn.commit()
        except Exception as e:
            print(e)        

    def get_user_district_id(self,tg_id):
        try:
            return self.cursor.execute("select dis_id from users where tg_id=?",(tg_id,)).fetchone()     
        except Exception as e:
            print(e)


 





