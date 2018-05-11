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
# let g:syntastic_python_python_exec="python"

__author__ = "easyly"

class GameServer(object):
    sock = socket.socket(socket.AF_INET , socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    def __init__(self):
        self.run = (HOST, PORT)
        self.log = log("SERVER")
        self.socketqueue = []
        self.clients = {}
        
    def bind(self, threadcount):
        self.sock.bind(self.run)
        self.sock.listen(2)
        print "\n\t------------------\n\tSOCKET GAME SERVER\n\t" + "-"*18
        print "\nSunucu Basladi!\n"
        self.newthread(threadcount)

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
        komutlar = ["write","generate","cmd","exit","players","armies", "print"]
        spacecount = 30
        text = ""
        for com in komutlar:
            if komutlar.index(com) % 2 == 0:
                text += com
                textlen = len(com)
                if komutlar.index(com) +1 == len(komutlar):
                    text += "\n"
            else:
                count = spacecount -textlen
                textlen = 0
                text += " "*count + com+"\n"
        print text
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
                    print "-"*15
                    print "\n" + str(models.armies[army])
                print "\n"
            
            if cmd == "players":
                for player in models.players:
                    print "\n"+str(models.players[player])
                print "\n"

            if cmd == "cmd":
                try:
                    inp = input("cmdmode>>")
                except Exception as e:
                    print e
            if cmd == "print":
                try:
                    print input("print>>")
                except NameError as e:
                    print e

            if cmd == "write":
                self.log.write(input("write>>"))

    def recver(self, c, addr):
        if self.socketqueue == [""]:
            self.socketqueue = []
        if self.socketqueue == []:
            data = c.recv(1024**2)
            if not data:
                print "kullanici Baglantiyi kesti: "+str(addr[0])
                self.newthread()
                return False

            if not "\\n" in data:
                parsed = data.split("\n")

            for element in parsed:
                self.socketqueue.append(element)

        toreturn = self.socketqueue.pop(0)
        self.log.write("Decodelanacak veri: {}".format(toreturn))
        return json.loads(toreturn)
  
    def accept(self):
            c, addr = self.sock.accept() # Getting connection
            print "{} baglandi".format(addr[0])
            #buraya handler tarzi bi thread acilcak.
            #self.sender({'tag':'feedback','data':[True]}, c)
            player = self.loginandregister(c, addr)
            if not player:
                return 0#sunucudan ayrilan kullaniciyi atmak icin.
            self.listener(c, addr, player)#anadongu

    def saver(self):
        while 1:
            models.save()
            time.sleep(5)
    
    def offline_earn(self, obj):
        
        Thread(target = models.players[obj.id].builds['Oduncu'].uret, args = ()).start()
        Thread(target = models.players[obj.id].builds['KilOcagi'].uret, args = ()).start()
        Thread(target = models.players[obj.id].builds['MadenOcagi'].uret, args = ()).start()

    def listener(self, c, addr, obj):#anadongu
        while True:
            data = self.recver(c, addr)
            self.log.write("gelen veri >> "+str(data))
            if data == False:
                del self.clients[obj.id]
                return 0
            tag = data["tag"]
            data = data["data"]
            if tag == "action":
                try:
                    data[0]["id"] = self.actionpool.getid()
                    data[0]["from"] = obj.id
                    data[0]["has_trigger"] = False
                    data[0]["paid"] = False
                except TypeError:
                    self.log.write("Gecersiz Action Tanimlama : {}".format(str(data[0])))
                    continue
                self.actionpool.add(data[0])
                self.actionpool.save()
                self.action_trigger_chainer(self.actionpool)

            if tag =="notification_control":
                if not self.pendingpool.pool[obj.id] == []:
                    pending = []
                    for ntf in self.pendingpool.pool[obj.id]:
                        pending.append(ntf)
                    self.sender({"tag":"notification", "data":pending}, c)
                    self.pendingpool.pool[obj.id] = []
                    self.pendingpool.save()

            if tag == "create_army":
                pass_switch = False
                for army in models.armies:
                    if army in obj.armies:
                        if models.armies[army].name == data[0]:
                            self.sender({"tag":"create_army_feedback", "data":[False, "err_name"]}, c)
                            pass_switch = True

                if pass_switch:
                    continue

                if self.check_and_pay(obj.id, "army_price"):
                    self.sender({"tag":"create_army_feedback", "data":[True]}, c)
                    army_name = data[0].encode("utf-8")
                    general_name = data[1].encode("utf-8")
                    newarmy = models.Army(army_name, general_name, obj.id, obj.usr_name)
                    newarmy.ords[0] = obj.ords[0]
                    newarmy.ords[1] = obj.ords[1]
                    models.armies[newarmy.id] = newarmy
                    models.players[obj.id].armies.append(newarmy.id) 
                    obj = models.players[obj.id]
                    models.save()
                else:
                    self.sender({"tag":"create_army_feedback","data":[False, "err_materials"]}, c)
            if tag == "user_control":
                if obj.name == "noname":
                    self.sender({"tag":"feedback", "data":[False]}, c)
                    cr = self.register(c, addr)
                    obj.name = cr
                    obj.create_fort()
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
                    parsed = parser.parse_player(models.players[obj.id], models.armies)
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
                self.pendingpool.pool[player.id]=[]
                self.pendingpool.save()
                self.clients[player.id] = c
                return player

            else:    #Login
                player = db.login(usr_name, usr_pass)
                player = models.players[player.id]
                fb = self.sender({'tag':'feedback', 'data':[True]}, c)
                if not fb:
                    return False
                if not player.id in self.pendingpool.pool:
                    self.pendingpool.pool[player.id]=[]
                    self.pendingpool.save()
                self.clients[player.id] = c
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

    def create_troop_trigger(self, poolid):
        action = self.actionpool[poolid]
        try:
            army = models.armies[action["army_id"]]
        except KeyError:
            self.actionpool.log.write("{} id li actionun isaret ettigi {} id li ordu bulunamadigi icin action havuzdan kaldirildi".format(str(poolid), str(action["army_id"])))
            self.notify(action["from"], "Birlik Olusturulamadi", "Belirtilen ID Degerli Bir Ordunuz Olmadigindan Dolayi Birlik Olusturulamadi.")
            self.actionpool.remove_by_id(poolid)
            return 0
        if not action["troop_type"] in [0, 1, 2, 3]:
            self.actionpool.log.write("{} id li actiondaki troop_type degeri eldeki hicbir veriyle uyusmadigindan dolayi havuzdan kaldirildi action: {}".format(str(poolid), str(action)))
            self.actionpool.remove_by_id(poolid)
            return 0
        if not action["from"] <0:
            if not action["army_id"] in models.players[action["from"]].armies:
                self.actionpool.log.write("{} id li aksiyonu gonderen {} id liplayerin havuzunda {} id li ordu bulunmadigi icin aksiyon havuzdan kaldirildi".format(str(poolid), str(action["from"]), str(action["army_id"])))
                self.actionpool.remove_by_id(poolid)
                return 0
        price_id = ["yaya_asker", "zirhli_asker", "atli_asker", "kusatma_makinesi"][action["troop_type"]]
        price_id = models.prices["troop_price"][price_id]
        if not action["paid"]:
            payment = self.check_and_pay(action["from"],price_id, True )
            if payment:
                self.actionpool[poolid]["paid"] = True
                action["paid"] = True
            else:
                self.log.write("{} id li actiond odeme basarisiz oldugundan dolayi action havuzdan temizlendi, player id:{}".format(str(poolid), str(action["from"])))
                self.actionpool.remove_by_id(poolid)
                self.notify(action["from"], "Birlik Olusturulamadi", "Yeterli Materyallere Sahip Olmadiginizdan Dolayi Birlik Olusturulamadi.")
                return 0
        times = models.sleep_times["create_troop"]
        tp = action["troop_type"]
        if tp == 0:
            sleep_time = times["yaya_asker"]
        if tp == 1:
            sleep_time = times["zirhli_asker"]
        if tp == 2:
            sleep_time = times["atli_asker"]
        if tp == 3:
            sleep_time = times["kusatma_makinesi"]

        if models.armies[action["army_id"]].isshown:
            self.actionpool.log.write("{} id li ordu herhangi bir karargahta bulunmadigindan dolayi {} id li aksiyon havuzdan kaldirildi".format(str(action["army_id"]), str(poolid)))
            self.notify(action["from"], "Birlik Olusturulamadi", "Ordunuz Herhangi Bir Karargahta Bulunmadigindan Dolayi Birlik Olusturulamadi.")
            return 0
        if models.armies[action["army_id"]].hasaction:
            self.actionpool.log.write("{} id li actionda bahsedilen {} id li ordu zaten bir aksiyon icinde oldugundan dolayi aksiyon havuzdan kaldirildi".format(str(poolid), str(action["army_id"])))
            self.notify(action["from"], "Birlik Olusturulamadi", "Ordunuz Zaten Bir Aksiyon Icerisinde Oldugundan Birlik Olusturulamadi")
            self.actionpool.remove_by_id(poolid)
            return 0
        models.armies[action["army_id"]].hasaction = True
        self.create_troop_process(tp, action["army_id"], sleep_time)
        self.actionpool.remove_by_id(poolid)
        self.notify(action["from"], "Birlik Basariyla Olusturuldu", "Talep Ettiginiz Birliklerin Olusturulmasi Basariyla Gerceklesti")
        models.armies[action["army_id"]].hasaction = False


    def create_troop_process(self, troop_type,army_id, sleep_time):
        time.sleep(sleep_time)
        if troop_type == 0:
            troop = models.yaya_asker()
        if troop_type == 1:
            troop = models.zirhli_asker()
        if troop_type == 2:
            troop = models.atli_asker()
        if troop_type == 3:
            troop = models.kusatma_makinesi()
        models.armies[army_id].troops.append(troop)
        del troop

    def check_and_pay(self, player_id, price_id, manual = False):
        if manual:
            prices = price_id
        else:
            prices = models.prices[price_id]
        liste = []
        if not models.players[player_id].builds["MadenOcagi"].suan >=prices["Demir"] :
            return False
        if not models.players[player_id].builds["KilOcagi"].suan >= prices["Kil"]:
            return False
        if not models.players[player_id].builds["Oduncu"].suan >= prices["Odun"]:
            return False

        models.players[player_id].builds["MadenOcagi"].suan -= prices["Demir"]
        models.players[player_id].builds["KilOcagi"].suan -= prices["Kil"]
        models.players[player_id].builds["Oduncu"].suan -= prices["Odun"]
        return True

    def notify(self, id, header, desc):
        pos = models.players[id].ntfpos
        models.players[id].ntfpos += 1
        if not id in self.clients:
            package={"header":header, "desc":desc, "pos":pos, "type":"ntf"}
            self.pendingpool[id].append(package)
        else:
            self.sender({"tag":"notification", "data":[{"header":header, "desc":desc, "pos":pos, "type":"ntf"}]}, self.clients[id])

    def move_army_trigger(self, poolid):
        action = self.actionpool[poolid]
        try:
            army = models.armies[action["army_id"]]
        except KeyError:
            self.actionpool.log.write("{} numarali ordu id si bulunamadigi icin {} id li action calistirilamadi ve havuzdan eksiltildi".format(str(action["army_id"]), str(action["id"])))
            self.actionpool.remove_by_id(poolid)
            self.actionpool.save()
            return 0
        if army.hasaction:
            self.actionpool.log.write("{} idli ordu zaten bir aksiyon icerisinde oldugundan dolayi {} id li aksiyon havuzdan eksiltildi".format(str(action["army_id"]), str(action["id"])))
            self.notify(action["from"], "Ordu Hareket Ettirilemedi", "Ordunuz Zaten Bir Aksiyon Icerisinde  Oldugundan Dolayi Hareket Ettirilemedi")
            self.actionpool.remove_by_id(poolid)
            self.actionpool.save()
            return 0
        if not action["from"] <0:
            if not action["army_id"] in models.players[action["from"]].armies:
                self.actionpool.log.write("{} id li actionda {} id li playera ait ordularin icerisinde {} id li ordu bulunmadigi icin action havudan kaldirildi".format(str(poolid), str(action["from"]), str(action["army_id"])))
                self.actionpool.remove_by_id(poolid)
                return 0
        if action["x"] <=0 or action["y"] <= 0:
            self.actionpool.remove_by_id(poolid)
            self.actionpool.save()
            self.actionpool.log.write("{} idli actionun x veya y degerleri 0 a kucukesit oldugu icin aksiyon silindi aksiyon: {}".format(str(poolid), str(action)))
            return 0
        x_count = action["x"] - army.ords[0]
        y_count = action["y"] - army.ords[1]
        process_count = abs(x_count) + abs(y_count)
        process_list = []
        move_time = army.calculate_move_time()
        models.armies[army.id].hasaction = True
        army = models.armies[army.id]

        for process in xrange(process_count):
            if not x_count == 0:
                if x_count <0:
                    process_list.append("a")
                    x_count +=1

                else:
                    process_list.append("d")
                    x_count = x_count -1

            if not y_count == 0:
                if y_count <0:
                    process_list.append("w")
                    y_count += 1
                else:
                    process_list.append("s")
                    y_count = y_count - 1

        for inst in process_list:
            try:
                self.actionpool[poolid]
            except KeyError:
                return 0
            self.move_army_process(army, inst, move_time)
        self.actionpool.remove_by_id(poolid)
        self.actionpool.save()
        self.notify(action["from"], "Ordu Basariyla Hareket Ettirildi", "Talep Ettiginiz Ordunuzu Hareket Ettirme Islemi Basariyla Gerceklesti")
        models.armies[army.id].hasaction = False

    def move_army_process(self, army, key, sleeptime):
        if sleeptime < 0:
            sleeptime = 0
        time.sleep(sleeptime)
        army.isshown = True
        print str(army.ords)
        if key == "w":
            army.ords[1] = army.ords[1] - 1
        if key == "s":
            army.ords[1] += 1
        if key == "a":
            army.ords[0] = army.ords[0] - 1
        if key == "d":
            army.ords[0] += 1
        models.armies[army.id] = army
        parsed = parser.parse_map([], [], {army.id: army})
        self.genericpool.replace(parsed["armies"][0])



    def action_trigger_chainer(self,pool):#ATC, her aksiyonun bir triggeri oldugundan emin olunmasini saglar.Her sunucu baslangicinda cagirilmasi gerekir
        for action_id in pool.pool:
            if not pool.pool[action_id]["type"] in ["move_army", "create_troop"]:
                pool.remove_by_id(action_id)
                pool.log.write("{} id li aksiyonun tipi herhangi bir ontanimli tipe uymadigi icin havuzdan eksiltildi".format(str(action_id)))
                continue
            if not pool.pool[action_id]["has_trigger"]:
                pool.pool[action_id]["has_trigger"] = True
                if pool.pool[action_id]["type"] == "move_army":
                    Thread(target = self.move_army_trigger, args=(action_id, )).start()

                if pool.pool[action_id]["type"] == "create_troop":
                    Thread(target = self.create_troop_trigger, args=(action_id, )).start()

def prepare_map():
    return parser.parse_map(models.camps, models.forts,models.armies)
                       
def initialize():
    server = GameServer()
    map_elements = prepare_map()
    server.genericpool = infopool("genericpool")
    server.player_container = containerpool("playercontainer")
    server.actionpool = infopool("actionpool")
    server.actionpool.load()
    server.pendingpool = infopool("pending")
    server.pendingpool.load()
    for action in server.actionpool.pool:
        server.actionpool.pool[action]["has_trigger"] = False
    server.action_trigger_chainer(server.actionpool)
    for dic in map_elements:
        for element in map_elements[dic]:
            server.genericpool.add(element)
    server.genericpool.add({"id":-1, "datatype":"prices", "data":models.prices})
    parsed_players = parser.parse_players(models.players)
    for player in parsed_players:
        server.genericpool.add(player)
    for id  in models.players:
        pool = infopool("playerpool "+ str(id))
        server.offline_earn(models.players[id])
        server.player_container.register(id, pool)
        
    Thread(target = server.saver).start()
    server.bind(5)
    Thread(target=server.cmd).start()

if __name__ == "__main__":
    initialize()
