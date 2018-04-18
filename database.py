from settings import *
import sqlite3 as sql
from models import Player
import os, random, cPickle
from threading import Thread

class DBConnector(object):
    name_list = [] 
    
    def __init__(self, dbname):
        self.dbname = dbname
        
    def add(self, usrname):    
        self.name_list.append(usrname)
    
    def connect(self):
        self.connection = sql.connect(os.path.join(DB_PATH,'{}.db'.format(self.dbname)))
        self.connection.row_factory = sql.Row
        self.cursor = self.connection.cursor()
        self.cursor.execute ("""
        	CREATE TABLE IF NOT EXISTS users 
        	(id ,
        	usr_name, 
        	usr_pass, 
        	pickled_data)
        	""")
        
    def login(self, usrname, usrpass):
        """
        @:return: None or False or Player Object
        """
        self.connect()
        self.usrname = usrname
        self.usrpass = usrpass
        self.cursor.execute("SELECT * FROM users WHERE (usr_name = ? AND usr_pass = ?)",(usrname,usrpass))
        query = self.cursor.fetchone()
        self.close()
        if query:
            try:
                return self.get_object(self.usrname)
            except:
                return None
        else:
            return False
        
    
    
    def register(self, usrname, usrpass):
        self.connect()
        self.cursor.execute("INSERT INTO users ( usr_name, usr_pass, pickled_data) VALUES ( ?, ?, ?)",(usrname, usrpass, None))
        self.connection.commit()
        self.close()
        
        
    def list_db(self):
        self.connect()
        self.cursor.execute("SELECT * FROM users")
        query = self.cursor.fetchall()
        self.close()

        if query:
            return query
        else:
            return None
            
           

    def list_name(self):
        name_list = []
        for i in self.list_db():
            name_list.append(i[1])
        
        return name_list
    
    def insert(self, obj):
        self.connect()
        self.cursor.execute("INSERT INTO users (id, usr_name, usr_pass, pickled_data) VALUES ( ?, ? , ? , ? )",(obj.id ,self.usrname,self.usrpass,obj.save()))
        self.connection.commit()
        self.close()
        
    def update(self, obj):
        self.connect()
        self.cursor.execute("UPDATE users SET pickled_data = ? WHERE usr_name  = ?",(obj.save(),obj.usr_name))
        self.connection.commit()
        self.close()
        
    def get_object(self, usrname):
        self.connect()
        self.cursor.execute("SELECT * FROM users WHERE (usr_name = ?)",(usrname,))
        query = self.cursor.fetchone()
        self.close()
        if query:
            return cPickle.loads(str(query['pickled_data']))
            
    def close(self):
        self.cursor.close()
        self.connection.close()
    



class DBCamp(object):
    def connect(self):
        self.connection = sql.connect(os.path.join(DB_PATH,'database.db'))
        self.connection.row_factory = sql.Row
        self.cursor = self.connection.cursor()
        self.cursor.execute ("""
        	CREATE TABLE IF NOT EXISTS camps (id ,bilgiid INTEGER PRIMARY KEY AUTOINCREMENT , pickled_data)
        	""")
        	 
    def insert(self, obj):
        self.cursor.execute("INSERT INTO camps ( id, pickled_data ) VALUES (?,?)",(obj.id, obj.save()))
        self.connection.commit()
        
    def get_all_object(self):
        self.cursor.execute("SELECT * FROM camps")
        query = self.cursor.fetchall()
        if query:
            return query
        else:
            return False
            
    def get_object(self, id):
        self.cursor.execute("SELECT * FROM camps WHERE (id = ?)",(id,))
        query = self.cursor.fetchone()
        if query:
            return cPickle.loads(str(query['pickled_data']))
        else:
            return None
            
        
    def close(self):
        self.cursor.close()
        self.connection.close()
        

      

if __name__ == '__main__':
    db = DBConnector()
    db.connect()
    db.register('easyly','haktr12345')
    db.register('test','testpass')
    
    check = db.login('easyly','haktr12345')
    if check == None:
        p = Player('easyly')
        db.update(p)
    elif check == False:
        print 'Yanlis'
    
    else:
        profile = check
        print profile
