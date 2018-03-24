from database import *
import models
from mapping import *
from threading import Thread
from settings import *
import socket, json , time
from log import log
from parse import parser
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
        print 'Sunucu Basladi!'
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
        print "\ngenerate\tcmd\t"
        while 1:
            cmd = raw_input(">>")
            if cmd == "generate":
                generate.generate_map(50)
            if cmd == "cmd":
                try:
                    inp = input("<<")
                except Exception as e:
                    print e

    def recver(self, c, addr):
        data = c.recv(1024**2)
        if not data:
            print "kullanici Baglantiyi kesti: "+str(addr[0])
            return False
        try:
            feedback = json.loads(data)
            return feedback
        except ValueError:
            self.log.write("veri islenemedi: "+str(feedback))
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

    def offline_earn(self, c, obj):
        
        db = DBConnector(obj.usr_name)
        oduncu = obj.builds['Oduncu']
        kil = obj.builds['KilOcagi']
        maden = obj.builds['MadenOcagi']
        
        Thread(target = oduncu.uret, args = ()).start()
        Thread(target = kil.uret, args = ()).start()
        Thread(target = maden.uret, args = ()).start()
        
        while True:
            db.update(obj)
            time.sleep(.1)#database disk yiyeceginden dolayi timeout koymak daha mantikli
    
    
        
    def listener(self, c, addr, obj):#anadongu
        while True:
            data = self.recver(c, addr)
            tag = data["tag"]
            data = data["data"]

            if data['tag'] == 'ping':
                self.sender({'tag':'pong','data':[]},c)
            
            if tag == "sync":
                feedbackdata = {}
                if "generic" in data[0]:
                    genericpool_feedback = self.genericpool.process(data[1]["generic_idlist"])
                    feedbackdata["generic"] = genericpool_feedback

                if "player" in data[0]:
                    selfpool = self.playerpool.bring(obj.id)
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
        feedback = self.sender({"tag":"register_info", data:[]},c)
        if not feedback:
            return False
        
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
                fb = self.sender({'tag':'feedback','data':[False , 'user_pass_err']}, c)
                if not fb:
                    return False
                continue

            elif check == None:  ## Ilk giris
                register_info = self.register(c, addr)
                
                if register_info == False:
                    return False

                player = models.Player(usr_name, register_info)
                db.update(player)
                fb = self.sender({'tag':'feedback','data':[True]}, c)
                if not fb:
                    return False
                Thread(target = self.offline_earn, args = (c,  player)).start()
                return player
            
            else:    #Login
                player = db.login(usr_name, usr_pass)
                fb = self.sender({'tag':'feedback', 'data':[True]}, c)
                if not fb:
                    return False
                Thread(target = self.offline_earn, args = (c, player)).start()
                return player

        elif data['tag'] == 'register':
            usr_name = data['data'][0]['user']
            usr_pass = data['data'][0]['pass']
            if usr_name in db.name_list:
                fb = self.sender({'tag':'feedback', 'data':[False, 'usr_taken']}, c)
                if not fb:
                    return False
                continue
            
            else:
                db = DBConnector(usr_name)
                db.register(usr_name,usr_pass)
                fb = self.sender({'tag':'feedback','data':[True]}, c)
                if not fb:
                    return False
                continue
                	
                
def prepare_map():
    parser.parse_map(models.camps, models.players, models.armies)
                       
def initialize():
    prepare_map()
    server = GameServer()
    Thread(target=server.cmd).start()
    server.bind()

if __name__ == "__main__":
    initialize()
