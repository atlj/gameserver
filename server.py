#-*- coding: utf-8 -*-
from database import *
import models
from mapping import *
from threading import Thread
from settings import *
import os, socket, json , time
from log import log
from parse import parser
from pools import infopool, containerpool
import generate

__author__ = "easyly"

class GameServer(object):
    sock = socket.socket(socket.AF_INET , socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    def __init__(self):
        self.run = (HOST, PORT)
        self.log = log("SERVER")
        
    def bind(self):
        self.sock.bind(self.run)
        self.sock.listen(2)
        print "Sunucu Basladi!"
        self.newthread(5)

    def sender(self,context,c):
        try:
            data = json.dumps(context)
            c.send(data)
            return True

        except socket.error:
            self.log.write("veri gonderilemedi: "+str(data))
            return False

    def newthread(self, count = 1):
        for times in range(count):
            Thread(target=self.accept).start()

    def cmd(self):
        print "print\twrite\tgenerate\tcmd\texit\tplayers\tarmies"
        while 1:
            cmd = raw_input(">>")
            if cmd == "generate":
                generate.generate_map(5)
                parsed_info = parser.parse_map(models.camps, models.forts,models.armies)
                for element in parsed_info:
                    for info in parsed_info[element]:
                        self.genericpool.add(info)
            if cmd == "exit":
                print "cikis yapiliyor.."
                os._exit(0)

            if cmd == "armies":
                for army in models.armies:
                    print "\n" + str(models.armies[army])
            
            if cmd == "players":
                for player in models.players:
                    print "\n"+str(models.players[player])
            if cmd == "cmd":
                try:
                    inp = input("cmdmode>>")
                except Exception as e:
                    print e
            if cmd == "print":
                print input("print>>")

            if cmd == "write":
                self.log.write(input("write>>"))

    def recver(self, c, addr):
        data = c.recv(1024**2)
        if not data:
            print "kullanici Baglantiyi kesti: "+str(addr[0])
            return False
        try:
            feedback = json.loads(data)
            return feedback
        except ValueError:
            self.log.write("veri islenemedi: "+str(data))
            return False
  
    def accept(self):
            c, addr = self.sock.accept() # Getting connection
            print "{} baglandi".format(addr[0])
            #buraya handler tarzi bi thread acilcak.
            #self.sender({'tag':'feedback','data':[True]}, c)
            player = self.loginandregister(c, addr)
            if not player:
                self.newthread()#asunucudan ayrilan kullanicinin yerine yeni bi dinleyici acmak icin
                return 0#sunucudan ayrilan kullaniciyi atmak icin.
            self.listener(c, addr, player)#anadongu

    def saver(self, obj):
        while 1:
            models.players[obj.id]= obj
            models.save()
            time.sleep(5)
    
    def offline_earn(self, obj):
        
        oduncu = obj.builds['Oduncu']
        kil = obj.builds['KilOcagi']
        maden = obj.builds['MadenOcagi']
        
        Thread(target = oduncu.uret, args = ()).start()
        Thread(target = kil.uret, args = ()).start()
        Thread(target = maden.uret, args = ()).start()
        Thread(target = self.saver, args = (obj, )).start()

    def listener(self, c, addr, obj):#anadongu
        while True:
            data = self.recver(c, addr)
            self.log.write("gelen veri >> "+str(data))
            if data == False:
                print str(addr[0])+" adresli kullanici sunucudan ayrildi"
                break
            tag = data["tag"]
            data = data["data"]
            if tag == "create_army":
                builds = obj.builds
                demir = builds["MadenOcagi"].suan
                kil = builds["KilOcagi"].suan
                odun = builds["Oduncu"].suan
                ucret = models.prices["army_price"]
                for army in models.armies:
                    if army in obj.armies:
                        if models.armies[army].name == data[0]:
                            self.sender({"tag":"create_army_feedback", "data":[False, "err_name"]}, c)
                            continue

                if odun >= ucret["Odun"] and kil >= ucret["Kil"] and demir >= ucret["Demir"]:
                    self.sender({"tag":"create_army_feedback", "data":[True]}, c)
                    data = [data[0].encode("utf-8"), data[1].encode("utf-8")]
                    newarmy = models.Army(data[0], data[1], obj.id, obj.usr_name)
                    models.armies[newarmy.id] = newarmy
                    models.players[obj.id].armies.append(newarmy.id)
                    obj = models.players[obj.id]
                    models.save()
                    self.log.write("Yeni Ordu Olusturuldu: "+str(newarmy))
                else:
                    self.sender({"tag":"create_army_feedback","data":[False, "err_materials"]}, c)
            if tag == "user_control":
                if obj.name == "noname":
                    self.sender({"tag":"feedback", "data":[False]}, c)
                    cr = self.register(c, addr)
                    obj.name = cr
                    obj.create_fort()
                    models.forts[obj.id] = obj
                    models.players[obj.id] = obj
                    models.save()
                else:
                    self.sender({"tag":"feedback", "data":[True]},c)
            if tag == 'ping':
                self.sender({'tag':'pong','data':[]},c)
            
            if tag == "sync":
                feedbackdata = {}
                if "generic" in data[0]:
                    genericpool_feedback = self.genericpool.process(data[1]["generic_idlist"])
                    feedbackdata["generic"] = genericpool_feedback

                if "player" in data[0]:
                    selfpool = self.player_container.bring(obj.id)
                    if not selfpool:
                        self.log.write("oyuncu havuzu containerdan yuklenemedi\noyuncu id'si >> "+ str(obj.id)+"\nhavuz idleri >> "+str(self.player_container))
                    #BURAYI SIL
                    parsed = parser.parse_player(obj, models.armies)
                    selfpool.replace(parsed["materials"])
                    for army in parsed["armies"]:
                        selfpool.replace(army)
                    self.player_container.register(obj.id, selfpool)
                    #BURAYI SIL
                    playerpool_feedback = selfpool.process(data[1]["player_idlist"])
                    feedbackdata["player"]= playerpool_feedback

                if "faction" in data[0]:
                    selfpool = self.factionpool.bring(obj.faction_id)
                    factionpool_feedback = selfpool.process(data[1]["faction_idlist"])
                    feedbackdata["faction"] = factionpool_feedback

                feedback = {"tag":"sync_feedback",
                            "data":[feedbackdata]}
                self.sender(feedback, c)

    def register(self, c, addr):
        while 1:
            feedback = self.recver(c, addr)
            if not feedback:
                return False
            name = feedback["data"][0]
            if not name in models.fort_names:
                models.fort_names.append(name)
                models.save()
                self.sender({"tag":"feedback", "data":[True]}, c)
                return name
            feedback = self.sender({"tag":"feedback", "data":[False, "name_taken"]}, c)
            if not feedback:
                return False

    def loginandregister(self, c, addr):
      while 1:
      
        data = self.recver(c, addr)
        if not data:
            return False
        
        if data['tag'] == 'login':
            usr_name = data['data'][0]['user']
            usr_pass = data['data'][0]['pass']
            db = DBConnector(usr_name)
            db.add(usr_name)
            check = db.login(usr_name, usr_pass)
            
            if check == False:
                fb = self.sender({'tag':'feedback','data':[False]}, c)
                if not fb:
                    return False
                continue

            elif check == None:  ## Ilk giris
                player = models.Player(usr_name)
                db.update(player)
                self.offline_earn(player)
                fb = self.sender({'tag':'feedback','data':[True]}, c)
                if not fb:
                    return False
                return player
            
            else:    #Login
                player = db.login(usr_name, usr_pass)
                player = models.players[player.id]
                fb = self.sender({'tag':'feedback', 'data':[True]}, c)
                if not fb:
                    return False
                return player

        elif data['tag'] == 'register':
            usr_name = data['data'][0]['user']
            usr_pass = data['data'][0]['pass']
            db = DBConnector(usr_name)
            if usr_name in db.name_list:
                fb = self.sender({'tag':'feedback', 'data':[False, 'usr_taken']}, c)
                if not fb:
                    return False
                continue
            
            else:
                db.register(usr_name,usr_pass)
                fb = self.sender({'tag':'feedback','data':[True]}, c)
                if not fb:
                    return False
                continue
                	
    def parseall(self):#su anlik kullanilmiyor.
        parsed_datas = parser.parse_map(models.camps, models.forts,models.armies)
        for element in parsed_datas:
            for data in parsed_datas[element]:
                self.genericpool.add(data)

def prepare_map():
    return parser.parse_map(models.camps, models.forts,models.armies)
                       
def initialize():
    server = GameServer()
    map_elements = prepare_map()
    server.genericpool = infopool("genericpool")
    server.player_container = containerpool("playercontainer") 
    for dic in map_elements:
        for element in map_elements[dic]:
            server.genericpool.add(element)
    server.genericpool.add({"id":-1, "datatype":"prices", "data":models.prices})
    for id  in models.players:
        pool = infopool("playerpool "+ str(id))
        server.offline_earn(models.players[id])
        server.player_container.register(id, pool)
    server.bind()
    Thread(target=server.cmd).start()

if __name__ == "__main__":
    initialize()
