__author__ = "atlj"
class parser(object):

    @staticmethod
    def parse_player(player):
        return_table = {}
        
        materials = {}
        buildings = player.builds
        materials["Odun"] = buildings["Oduncu"].suan
        materials["Demir"] = buildings["MadenOcagi"].suan
        materials["Kil"] = buildings["KilOcagi"].suan
        
        position = player.ords
    
    @staticmethod
    def parse_map(camps=[], forts =[], armies=[], villages= []):#villages tbe
        camplist = []
        armylist = []
        fortlist = []
        for camp in camps:
            package ={"quickinfo":[camp.name], "marker":"C","type":"camp", "x":camp.ords[0], "y":camp.ords[1], "name":camp.name, "id":camp.id}
            camplist.append(package)
        for army in armies:
            package = {"marker":"A", "type":"army", "x":army.ords[0], "y":army.ords[1], "name":army.name, "general_name":army.general_name,"belonger_name":army.belonger_name, "belonger_id":army.belonger_id}
            armylist.append(package)

        for fort in forts:
            package = {"usr_name":fort.usr_name, "marker":"P", "type":"fort", "x":fort.ords[0], "y":fort.ords[1], "name":fort.name, "id":fort.id, }
            fortlist.append(package)
