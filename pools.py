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
        global info_ids
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
            
        
    def save(self):#cpickle object dondurecek
        global info_ids

        savedata = {"pool":self.pool,
                    "deletedpool":self.deletedpool,
                    "info_ids":self.info_ids}
        with open(os.path.join(cdir, self.picklename), "wb") as dosya:
            pickle.dump(savedata, dosya)
        
    def load(self):#cpickle object alicak
        global info_ids

        with open(os.path.join(cdir, self.picklename), "rb") as dosya:
            loaddata = pickle.load(dosya)

        self.pool = loaddata["pool"]
        self.deletedpool = loaddata["deletedpool"]
        self.info_ids = loaddata["info_ids"]
        
    def process(self, idlist):
        local_idlist = []
        replacelist = []
        dellist = []
        
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
class containerpool(infopool):
    def __init__(self, name):
        infopool.__init__(self, name)
        
    def bring(self, obj_id):
        idpool = []
        for id in self.pool:
            idpool.append(id)
        
        if obj_id in idpool:
            return self.pool[obj_id]
        else:
            self.log.write("id bulunamadi: "+str(obj_id))
        
