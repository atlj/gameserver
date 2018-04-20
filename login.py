#-*-coding:utf8;-*-
#qpy:2
#qpy:console

from peewee import SqliteDatabase, TextField, Model, BooleanField, DateTimeField
import os, peewee, md5, datetime
#from settings import DB_PATH


DB = SqliteDatabase('/sdcard/test.db')

def init():
    DB.connect()
    DB.create_tables([User], safe = True)
    DB.close()


class User(Model):
    name = TextField(unique = True)
    password = TextField()
    isAdmin = BooleanField(default = False)
    
    class Meta:
        database = DB


def addUser(name, password):
    try:
        User.create(name = name, 
        	          password = md5.new(password).hexdigest(),)
    except peewee.IntegrityError:
        raise ValueError('Ayni Isimden daha once olusmus')
        
        
def delUser(name = None, id = None):
    try:
        instance = User.select().where((User.name == name) | (User.id == id)).get()
        instance.delete_instance()
    except User.DoesNotExist:
        raise ValueError('Oyle bir kayit yok')


def login(name, password):
    try:
        obj = User.select().where((User.name == name) & (User.password == md5.new(password).hexdigest())).get()
        return True
    except User.DoesNotExist:
        return False
        
        
def addAdmin(name, password):
    try:
        User.create(name = name, 
        	          password = md5.new(password).hexdigest(),
        	          isAdmin = True)
    except peewee.IntegrityError:
        raise ValueError('Ayni isimden daha once olusmus')

def setAdmin(name = None, id = None):
    try:
        obj = User.select().where((User.name == name) | (User.id == id)).get()
        obj.isAdmin = True
        obj.save()
    except User.DoesNotExist:
        raise ValueError('Oyle bir kayit yok')



if __name__ == '__main__':
    init()
    import time
    now = time.time()
    #for i in range(100):
   #     addUser(name = 'User'+str(i), password = 'parola'+str(i))
        
    print 'Gecen Zaman'
    print now - time.time()
    
