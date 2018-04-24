from __future__ import division #pythonda 4/5 gibi kesirli ifadelerin donusturulmesi icin gereken kutuphane
from timer import Timer
import cPickle, random, time
from mapping import Map
import random
import os
import cPickle as pickle

cdir =  os.path.dirname(os.path.realpath(__file__))
idlist = []
camps = {}
armies = {}
forts = {}
players = {}
villages = {}
fort_names = []
prices = {"troop_price":
    {"yaya_asker":{"Demir":100, "Odun":200, "Kil":100}, 
    "zirhli_asker":{"Demir":100, "Odun":200, "Kil":100},
    "atli_asker":{"Demir":100, "Odun":200, "Kil":100}, 
    "kusatma_makinesi":{"Demir":100, "Odun":200, "Kil":100} },
    "army_price":{"Odun": 100, "Demir": 100, "Kil": 100}}

sleep_times = {"create_troop":{"yaya_asker":2, "atli_asker":2, "kusatma_makinesi":2, "zirhli_asker":2}}

def save():
    global idlist
    global camps
    global armies
    global players
    global villages
    global forts
    global fort_names
    savedata = {"camps":camps, "idlist":idlist, "armies":armies, "players":players, "villages":villages, "forts":forts, "fort_names":fort_names}
    with open(os.path.join(cdir, "serverdata"), "wb") as dosya:
        pickle.dump(savedata, dosya)

def load():
    global idlist
    global camps
    global armies
    global players
    global villages
    global forts
    global fort_names
    if os.path.exists(os.path.join(cdir, "serverdata")):
        with open(os.path.join(cdir, "serverdata"), "rb") as dosya:
            loaddata = pickle.load(dosya)
        idlist = loaddata["idlist"]
        camps = loaddata["camps"]
        armies = loaddata["armies"]
        for id in armies:
            armies[id].hasaction = False
        players = loaddata["players"]
        villages = loaddata["villages"]
        forts = loaddata["forts"]
        fort_names = loaddata["fort_names"]


class Asker(object):

    def level_up(self):
        self.level += 1
        self.calculate_stats()
        
    def __str__(self):
        return "{}".format(self.name+ " Tipi Birlik, Sayi: "+ str(self.size))
    	

class yaya_asker(Asker):
    def __init__(self, size = 50):
        self.level = 1
        self.size= size
        self.type = "troop"
        self.name = "Yaya Asker"
        self.stats = {"health":100,
                      "damage":50,
                      "attack_time":4/5,#saniye
                      "movement_time":1/10, #her birlik hareket etme suresine bu kadar zaman ekler
                      "building_damage": 20}
                      
class zirhli_asker(Asker):
    def __init__(self, size = 50):
        self.level = 1
        self.size = size
        self.type = "troop"
        self.name = "Zirhli Asker"
        self.stats = {"health":200,
                      "damage":70,
                      "attack_time":1,#saniye
                      "movement_time":2/10, #her birlik hareket etme suresine bu kadar zaman ekler
                      "building_damage": 20}

class kusatma_makinesi(Asker):
    def __init__(self, size = 50):
        self.level = 1
        self.size = size
        self.type = "troop"
        self.name = "Kusatma Makinesi"#kesinlikle mancinik degil
        self.stats = {"health":200,
                      "damage":50,
                      "attack_time":4/5,#saniye
                      "movement_time":2/10, #her birlik hareket etme suresine bu kadar zaman ekler
                      "building_damage": 100}
                      
class atli_asker(Asker):
    def __init__(self, size = 50):
        self.level = 1
        self.size = size
        self.type = "troop"
        self.name = "Atli Asker"
        self.stats = {"health":100,
                      "damage":40,
                      "attack_time":3/5,#saniye
                      "movement_time":-1/10, #her birlik hareket etme suresine bu kadar zaman ekler
                      "building_damage": 40}


        
        
class Army(object):#dj army eheuheueheuehu
    def __init__(self, name, general_name, belonger_id, belonger_name):
        global armies
        self.getid()
        self.belonger_id = belonger_id
        self.belonger_name = belonger_name
        self.ords = [0, 0]
        self.isshown = False
        self.hasaction = False
        self.name = name
        self.general_name = general_name
        self.troops = []#bu listenin elemanlari asker objesi olucak.
        armies[self.id] = self
        save()

    def __str__(self):
        trooptext = "\n"
        for troop in self.troops:
            trooptext += str(troop)+"\n"
        return "Ordu Objesi\nId:{} Isim:{}\nGeneral Ismi:{} Sahip:{}\nKonum: {}\n\nBirlikler: {}".format(str(self.id), self.name, self.general_name, self.belonger_name,str(self.ords) , trooptext)
        
    def calculate_dps(self):
        self.dps =0 #damage per second = saniye basina verilen hasar
        for troop in self.troops:
            self.dps += troop.size * (troop.stats["damage"] * (1/troop.stats["attack_time"]))
        return self.dps

    def getid(self):
        global idlist
        while 1:
            self.id = random.randint(0, 10**6)
            if self.id in idlist:
                continue
            idlist.append(self.id)
            break

    def calculate_hp(self):
        self.hp = 0 #hitpoint = can
        for troop in self.troops:
            self.hp += troop.size*troop.stats["health"]

        return self.hp

    def calculate_move_time(self):
        move_time = 0
        for troop in self.troops:
            move_time += troop.size*troop.stats["movement_time"]
        return move_time


    def add(self,troop):
        self.troops.append(troop)
        
    def summerize(self):
        self.troops_sum = []
        for troop in self.troops:
            self.troops_sum.append({"name":troop.name,"amount":troop.size, "stats":troop.stats})
        return {"type":"army", "troops":self.troops_sum, "name":self.name, "general_name": self.general_name}
        
           	



class hammadde(object):
    def __init__(self):
        self.kapasite = 2000
        self.suan = 0
        self.seviye = 1
        self.uretim = self.seviye #sn basina
        self.name = ""
        #Thread(target = self.uret , args =()).start()
       
         
    def level_up(self):
        self.seviye += 1
        self.uretim = self.uretim * self.seviye
        self.kapasite *= self.seviye
    
    def uret(self):
        while True:
            if self.kapasite == self.suan:
                pass
            else:
                Timer(second = 1).start()
                self.suan += self.uretim
                
                
        
    def __str__(self):
        return "{}: ".format(self.name) + str(self.seviye) + "\nSaniye Basina uretim: " +str(self.uretim)+"\nMevcut Hammadde: "+str(self.suan)
        


class Oduncu(hammadde):
    def __init__(self):
        hammadde.__init__(self)
        self.name = "Oduncu"
        self.material_name = "Odun"

class KilOcagi(hammadde):
    def __init__(self):
        hammadde.__init__(self)
        self.name = "Kil Ocagi"
        self.material_name = "Kil"

class MadenOcagi(hammadde):
    def __init__(self):
        hammadde.__init__(self)
        self.name = "Maden"
        self.material_name = "Demir"

    
class Camp(object):
    #ords = Map.create()
    def __init__(self,name ,seviye):
        self.getid()
        self.name = name
        global camps
        self.seviye = seviye

        if seviye == 0:
            seviye = 1
        else:
            self.seviye = seviye
        self.ords = Map.create()
    
        camps[self.id] = self
        save()
    def getid(self):
        global idlist
        while 1:
            self.id = random.randint(0, 10**6)
            if self.id in idlist:
                continue
            idlist.append(self.id)
            break

    def __str__(self):
        return "id: "+str(id)+"name: "+self.name+"ords: "+str(self.ords)

class Kisla(object):
    def __init__(self):
        self.seviye = 1
        self.can = 500
        self.hiz = 1
        self.savunma = 100
        self.asker_siniri = 100
        self.asker_list = []
    
    def level_up(self):
        self.can += self.seviye * 50
        self.seviye += 1
        self.hiz += 1
        self.asker_siniri *= 2


    def asker_uret(self, miktar):
        if len(self.asker_list) + miktar > self.asker_siniri:
            pass
        else:
            i = 0
            while i < miktar:
                asker = Asker()
                #print 'sure' + str(asker.uretimsuresi/self.hiz)
                Timer(second = asker.uretimsuresi / self.hiz ).start()
                self.asker_list.append(asker)
                i  += 1
            
    
    
        
        
class Merkez(object):
    seviye = 1
    can = 1000
    insa_hiz = 1
    savunma = 100
    
    
    def level_up(self):
        self.can += self.seviye * 50
        self.seviye += 1
        self.insa_hiz += 1
    
    def reset(self):
        self.seviye = 1
        self.can = 1000
        self.insa_hiz = 1
    
    def __str__(self):
        return 'Merkez: ' + str(self.seviye)
        

class Player(object):
    player_list = []
    def __init__(self,usr_name):
        global players
        global forts
        self.name = "noname"#ilk olusturulusta
        self.getid()
        self.armies = [] #ordularin id tagleri tutulacak
        self.usr_name = usr_name
        self.player_list.append(self)
        self.builds = {'Merkez': Merkez(),
                       'Kisla' : Kisla(),
                       'Oduncu': Oduncu(),
                       'KilOcagi' :KilOcagi(),
                       'MadenOcagi' : MadenOcagi(),
                       }
        players[self.id] = self
        save()

    def create_fort(self):
        self.ords = Map.create()
        forts[self.id] = self

    def getid(self):
        global idlist
        while 1:
            self.id = random.randint(0, 10**6)
            if self.id in idlist:
                continue

            idlist.append(self.id)
            break
        
    def save(self):
        return cPickle.dumps(self)
        
    
    def __str__(self):
        wood = self.builds["Oduncu"].suan
        iron = self.builds["MadenOcagi"].suan
        clay = self.builds["KilOcagi"].suan
        string = "ID: {}\nUser Name: {}\niron: {} clay: {} wood: {}".format(str(self.id),str(self.usr_name), str(iron), str(clay), str(wood))
        return string

load()
