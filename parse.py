__author__ = "atlj"
from log import log
log = log("PARSER LOG")
class parser(object):

    @staticmethod
    def parse_troops(troops):
        returnlist = []
        for troop in troops:
            package = {"size":troop.size, "name":troop.name, "stats":troop.stats}
            returnlist.append(package)
        return returnlist

    @staticmethod
    def parse_army(army):
        total_size = 0
        for troop in army.troops:
            total_size += troop.size
        package = {"datatype":"army", "total_size":total_size, "id":army.id, "name":army.name, "general_name":army.general_name, "x":army.ords[0], "y":army.ords[1], "troops":parser.parse_troops(army.troops)}
        return package

    @staticmethod
    def parse_fort(fort):
        package = {"datatype":"place", "quickinfo":[fort.name], "usr_name":fort.usr_name, "marker":"P", "type":"fort", "x":fort.ords[0], "y":fort.ords[1], "name":fort.name, "id":fort.id,"belonger_id":fort.belonger_id }
        return package

    @staticmethod
    def parse_army_map(army):
        if army.isshown:
            package = {"id":army.id, "datatype":"place", "quickinfo":[army.name], "marker":"A", "type":"army", "x":army.ords[0], "y":army.ords[1], "name":army.name, "general_name":army.general_name,"belonger_name":army.belonger_name, "belonger_id":army.belonger_id}
            return package

    @staticmethod
    def parse_player(player, armies=[]):
        return_table = {}
        materials = {}
        self_armies = []
        for id in armies:
            if id in player.armies:
                self_armies.append(armies[id])

        parsed_armies = []
        for army in self_armies:
            total_size = 0
            for troop in army.troops:
                total_size += troop.size
            package = {"datatype":"army", "total_size":total_size,"id":army.id, "name":army.name, "general_name":army.general_name,"x":army.ords[0], "y":army.ords[1], "troops":parser.parse_troops(army.troops) }
            parsed_armies.append(package)

        buildings = player.builds
        materials["Odun"] = buildings["Oduncu"].suan
        materials["Demir"] = buildings["MadenOcagi"].suan
        materials["Kil"] = buildings["KilOcagi"].suan
        materials["id"] = player.id
        materials["datatype"] = "materials"
        return {"armies":parsed_armies, "materials":materials}

    @staticmethod
    def parse_single_player(player):
        package= {"id":player.id, "datatype":"player", "name": player.usr_name, "faction_id":player.faction_id, "win":player.wins, "lose":player.loses}
        return package

    @staticmethod
    def parse_players(players):
        packages = []
        for id in players:
            player = players[id]
            package= {"id":player.id, "datatype":"player", "name": player.usr_name, "faction_id":player.faction_id, "win":player.wins, "lose":player.loses}
            packages.append(package)
        return packages

    @staticmethod
    def parse_map(camps=[], forts =[], armies=[], villages= []):#villages tbe
        camplist = []
        armylist = []
        fortlist = []
        for obj in camps:
            camp = camps[obj]
            package ={"datatype":"place", "quickinfo":[camp.name], "marker":"C","type":"camp", "x":camp.ords[0], "y":camp.ords[1], "name":camp.name, "id":camp.id}
            camplist.append(package)
        for obj in armies:
            army = armies[obj]
            if army.isshown:
                package = {"id":army.id, "datatype":"place", "quickinfo":[army.name], "marker":"A", "type":"army", "x":army.ords[0], "y":army.ords[1], "name":army.name, "general_name":army.general_name,"belonger_name":army.belonger_name, "belonger_id":army.belonger_id}
                armylist.append(package)

        for obj in forts:
            fort = forts[obj]
            package = {"datatype":"place", "quickinfo":[fort.name], "usr_name":fort.usr_name, "marker":"P", "type":"fort", "x":fort.ords[0], "y":fort.ords[1], "name":fort.name, "id":fort.id,"belonger_id":fort.belonger_id }
            fortlist.append(package)
        return {"forts":fortlist,
                "camps":camplist,
                "armies":armylist}
