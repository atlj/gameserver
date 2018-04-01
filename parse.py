__author__ = "atlj"
class parser(object):

    @staticmethod
    def parse_troops(troops):
        returnlist = []
        for troop in troops:
            package = {"size":troop.size, "name":troop.name, "stats":troop.stats}
            returnlist.append(package)
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
            package = {"name":army.name, "general_name":army.general_name,"x":army.ords[0], "y":army.ords[1], "troops":parser.parse_troops(army.troops) }
            parsed_armies.append(package)

        buildings = player.builds
        materials["Odun"] = buildings["Oduncu"].suan
        materials["Demir"] = buildings["MadenOcagi"].suan
        materials["Kil"] = buildings["KilOcagi"].suan
        
    @staticmethod
    def parse_map(camps=[], forts =[], armies=[], villages= []):#villages tbe
        camplist = []
        armylist = []
        fortlist = []
        for obj in camps:
            camp = camps[obj]
            package ={"quickinfo":[camp.name], "marker":"C","type":"camp", "x":camp.ords[0], "y":camp.ords[1], "name":camp.name, "id":camp.id}
            camplist.append(package)
        for obj in armies:
            army = armies[obj]
            if army.isshown:
                package = {"marker":"A", "type":"army", "x":army.ords[0], "y":army.ords[1], "name":army.name, "general_name":army.general_name,"belonger_name":army.belonger_name, "belonger_id":army.belonger_id}
                armylist.append(package)

        for obj in forts:
            fort = forts[obj]
            package = {"usr_name":fort.usr_name, "marker":"P", "type":"fort", "x":fort.ords[0], "y":fort.ords[1], "name":fort.name, "id":fort.id, }
            fortlist.append(package)
        return {"forts":fortlist,
                "camps":camplist,
                "armies":armylist}
