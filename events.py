from __future__ import division#gercek anlamda kesirli bolme yapabilmek icin gereken kutuphane

__author__ = "atlj"
class Siege(object):#kusatma
    def __init__(self, attacker, defender):
        self.attacker = attacker
        self.defender = defender
        self.calculate()
        self.result = self.finish()
        
    def __str__(self):
        	text = self.result[0]
        	for data in self.result[2]:
        	    text += str(data)
        	text += str(self.result[3])
        	return text
            	
         
        	
        	
        
    def finish(self):#zaiyati hesaplama
        if self.winner:
            loses = []
            if self.winner == "attacker":
                self.damage_taken = self.defender_dps*self.attacker_wintime
                for troop in self.attacker.troops:
                    if self.damage_taken <= 0:
                        break
                    elif self.damage_taken < troop.size * troop.stats["health"]:
                        count = int(self.damage_taken/troop.stats["health"])-1
                        troop.size = troop.size- count
                        self.damage_taken = 0
                        lose = troop
                        lose.size = count
                        loses.append(lose)
                        del lose #hafizada gereksiz yer kaplamamasi icin
                        
                        
                    else:
                        self.damage_taken = self.damage_taken - troop.size*troop.stats["health"]
                        loses.append(troop)
                        del self.attacker.troops[self.attacker.troops.index(troop)]#birlik silindi
                return ["attacker", self.attacker, loses, self.attacker_wintime]
            
            elif self.winner == "defender":
                self.damage_taken = self.attacker_dps*self.defender_wintime
                
                for troop in self.defender.troops:
                    if self.damage_taken <= 0:
                        break
                    
                    elif self.damage_taken < troop.size*troop.stats["health"]:
                        count = int(self.damage_taken/troop.stats["health"])-1
                        troop.size = troop.size - count
                        self.damage_taken = 0
                        lose = troop
                        lose.size = count
                        loses.append(lose)
                        del lose #hafiza seysi
                        
                    else:
                        self.damage_taken = self.damage_taken - troop.size*troop.stats["health"]
                        loses.append(troop)
                        del self.defender.troops[self.defender.troops.index(troop)]#birlik silindi 
                        
                return ["defender", self.defender,loses, self.defender_wintime]
                
        return ["tie", False, False]  
        
    def calculate(self):#kazananin hesaplanmasi
       self.attacker_dps = self.attacker.calculate_dps()
       self.attacker_hp = self.attacker.calculate_hp()

       self.defender_dps = self.defender.calculate_dps()
       self.defender_hp = self.defender.calculate_hp()

       self.attacker_wintime = self.defender_hp/self.attacker_dps
       self.defender_wintime = self.attacker_hp/self.defender_dps

       if self.attacker_wintime < self.defender_wintime:#saldiran kismin kazanmasi
           self.winner = "attacker"

       elif self.defender_wintime < self.attacker_wintime:#savunan kismin kazanmasi
           self.winner = "defender"


       else:#beraberlik
           self.winner = False
