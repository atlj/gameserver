#coding:utf-8
import random
import log
import cPickle as pickle
import os
cdir = os.path.dirname(os.path.realpath(__file__))


__author__ = "atlj"

class infopool(object):
    def __init__(self, name):
        self.name = name
        self.picklename = name+".pooldata"
        self.log = log.log(self.name+"pool")
        self.pool = {}
        self.deletedpool = []
        self.info_ids = []

    def getid(self):
        while 1:
            id = random.randint(1, 10**6)
            if id in self.info_ids:
                continue
            self.info_ids.append(id)
            return id
            
    def findbyid(self, data):
        for info_id in self.pool:
            if self.pool[info_id]["id"] == data["id"]:
                return info_id
        return False
        
    def add(self, data):
        id = self.getid()
        self.pool[id] = data
        
    def replace(self, data):
        old_id = self.findbyid(data)
        if old_id:
            del self.pool[old_id]
        self.add(data)

    def remove_by_id(self, id):
        try:
            del self.pool[id]
            self.info_ids.remove(id)
        except KeyError:
            self.log.write("Havuzda {} Numarali Id Bulunamadigi İcin remove_by_id gerceklestirilemedi".format(str(id)))
            
        
    def remove(self, data):
        info_id = self.findbyid(data)
        global info_ids
        try:
            self.pool[info_id]#Bu blok oncelikle verinin olup olmadigini kontrol etmek icin
            self.deletedpool.append(info_id)
            del self.pool[info_id]
            del self.info_ids[self.info_ids.index(info_id)]
        except KeyError:
            self.log.write("Veri, mevcut veritabaninda bulunmadigindan dolayi silinemedi: "+str(data))
    
    def print_pool(self):
        for id in self.pool:
            print self.pool[id]
    def __getitem__(self, index):
        return self.pool[index]
    def save(self):#cpickle object dondurecek
        global info_ids

        savedata = {"pool":self.pool,
                    "deletedpool":self.deletedpool,
                    "info_ids":self.info_ids}
        with open(os.path.join(cdir, self.picklename), "wb") as dosya:
            pickle.dump(savedata, dosya)
        
    def load(self):#cpickle object alicak
        global info_ids
        try:
            with open(os.path.join(cdir, self.picklename), "rb") as dosya:
                loaddata = pickle.load(dosya)

            self.pool = loaddata["pool"]
            self.deletedpool = loaddata["deletedpool"]
            self.info_ids = loaddata["info_ids"]
        except IOError:
            pass
        
    def process(self, idlist):
        local_idlist = []
        replacelist = []
        dellist = []
        
        idlist = map(lambda x:int(x.encode("utf-8")), idlist)#python 2 ve 3 arasinda unicode ile alakali cozemedigim bir problem meydana geldiginden dolayi unicode decoded object seklinde gelen verileri encode edip once bir string objesine sonra da integer'a ceviriyorum map fonksiyonu ile kisalttim. 

        for id in self.deletedpool:
            if id in idlist:
                dellist.append(id)
                del idlist[idlist.index(id)]
        
        for id in self.pool:
            local_idlist.append(id)
            
        for id in local_idlist:
            if not id in idlist:
                replacelist.append({id:self.pool[id]})
                
        feedback = {"replace":replacelist, 
                    "delete":dellist}
                    
        return feedback
                
    def __str__(self):
        return str(self.pool)

class syncpool(infopool):
    def __init__(self, name):
        infopool.__init__(self, name)

    def add(self, data):
        id = self.getid()
        self.pool[id] = data
        return {"replace":[{id:data}], "delete":[]}

    def replace(self, data):
        old_id = self.findbyid(data)
        if old_id:
            del self.pool[old_id]
        return self.add(data)


    def remove_by_id(self, id):
        try:
            del self.pool[id]
            self.info_ids.remove(id)
            return {"replace":[], "delete":[id]}
        except KeyError:
            self.log.write("Havuzda {} Numarali Id Bulunamadigi İcin remove_by_id gerceklestirilemedi".format(str(id)))


class containerpool(infopool):
    def __init__(self, name):
        infopool.__init__(self, name)

    def register(self, obj_id, obj):
        self.pool[obj_id] = obj
        
    def bring(self, obj_id):
        idpool = []
        for id in self.pool:
            idpool.append(id)
        
        if obj_id in idpool:
            return self.pool[obj_id]
        else:
            self.log.write("id bulunamadi: "+str(obj_id))
        
