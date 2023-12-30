import numpy as np

class MonsterAreas:
    def __init__(self, area_file, stat_file):
        self.areas = area_file
        self.mon_stats = stat_file
        self.map_mobs_dic = {}
        self.hell_mobs_dic = {}

        self.monster_type()

    def monster_type(self):
        # Superuniques/non-act bosses like bloodwitch or the councilmembers
        # don't necessarily have their own entries in monstats.txt, they may
        # use generic templates + attributes in superuniques.txt
        self.key_holders_list = [("bloodraven", "Blood Raven"), ("countess", "Countess"), ("summoner", "The Summoner"), ("bloodwitch", "Bloodwitch the Wild"), ("izual", "Izual"), ("nihlathakboss", "Nihlathak")]
        self.super_uniques_list = [("councilmember2", "Geleb Flamefinger"), ("councilmember1", "Toorc Icefist"), ("councilmember1", "Ismail Vilehand"), ("overseer1", "Shenk"), ("minion1", "Eldritch"),("reanimatedhorde5", "Pindle")]
        self.act_bosses_list = [("andariel", "Andariel"), ("duriel", "Duriel"), ("mephisto", "Mephisto"), ("diablo", "Diablo"), ("baalcrab", "Baal")]
        self.ubers_list = [("uberduriel", "Duriel"), ("uberandariel", "Lilith"), ("uberizual", "Izual"), ("ubermephisto", "Mephisto"), ("uberdiablo", "Diablo"), ("uberbaal", "Baal"), ("rathmaPoison", "Mendeln"), ("rathmaBone", "Rathma"), ("diabloclone", "Diablo Clone")]

        if not self.map_mobs_dic:
            self.map_zones()
        
        if not self.hell_mobs_dic:
            self.hell_zones()

        self.mobs_per_zone()


    def map_zones(self):
        # 166, 125, 100, 111 = LevelWarp, umon, nmon1, nmon12

        self.map_by_tier = {"T1": ["The Arreat Battlefield", "Bastion Keep", "Horazon's Memory", "Phlegethon", "The Torajan Jungle", "The Lost Temple", "The Ruined Cistern"], "T2": ["The Ancestral Trial", "The Fall of Caldeum", "The Royal Crypts", "The Ruins of Viz-Jun", "The Sanatorium", "Shadows of Westmarch"], "T3": ["The Ashen Plains", "The Blood Moon", "The Canyon of Sescheron", "The Kehjistan Marketplace", "The Pandemonium Citadel", "The River of Blood", "The Sewers of Harrogath", "The Throne of Insanity", "The Tomb of Zoltun Kulle"], "Dungeon": ["The Cathedral of Light", "The Plains Of Torment", "The Sanctuary of Sin"], "Unique": ["Zhar Rivers", "Zhar Ice", "Zhar Kurast", "Stygian Caverns 1", "Stygian Caverns 2"]}

        map_list = []
        for area in self.areas[141:]:
            #print(area)
            if "Pvp" not in area[165] and "Rathma" not in area[165] and "Event" not in area[165] and area[125]:
                map_list.append(area)
        self.map_file = np.array(map_list)
        
        to_remove = ["Monastery Map Basement", "Hole of Terror", "Black Abyss Map", "Zhar Library"]

        names = {name[0]: name[166][3:] for name in self.map_file}
        self.map_names = {key: names[key] for key in names if key not in to_remove}

        corrections = {"Sewers": "The Sewers of Harrogath", "Lava": "Phlegethon", "Kurast": "The Ruins of Viz-Jun", "Crypts Map": "The Royal Crypts", "Westmarch Map": "Shadows of Westmarch", "Zhar Rivers": "Zhar Rivers", "Zhar Ice": "Zhar Ice", "Zhar Kurast": "Zhar Kurast", "Hellcaves": "Stygian Caverns 1", "Hellcave Fortress": "Stygian Caverns 2", "Sanctuary Of Sin Map": "The Sanctuary of Sin"}

        for key in self.map_names:
            if "Map" in self.map_names[key]:
                self.map_names[key] = self.map_names[key][0:-3]
            if key in corrections:
                self.map_names[key] = corrections[key]

    def hell_zones(self):
        area_list = [area for area in self.areas[1:134] if area[100] and "top" not in area[0]]
        self.hell_area_file = np.array(area_list)

        self.hell_area_names = {name[0]: name[166][3:] for name in self.hell_area_file}

        self.hell_area_by_act = {"Act 1": [], "Act 2": [], "Act 3": [], "Act 4": [], "Act 5": []}
        for key in self.hell_area_names:
            # area names in levels.text start with "Act [x]", which we use
            # to categorize by act
            if self.hell_area_names[key] not in self.hell_area_by_act[key[0:5]]:
                self.hell_area_by_act[key[0:5]].append(self.hell_area_names[key])

    def mobs_per_zone(self):
        self.map_mobs_dic = {}
        for key in self.map_names:
            map_index = np.where(self.map_file[:, 0] == key)[0][0]
            self.map_mobs_dic[self.map_names[key]] = [mob for mob in self.map_file[map_index, 100:112] if mob]

        self.hell_mobs_dic = {}        
        for key in self.hell_area_names:
            area_index = np.where(self.hell_area_file[:, 0] == key)[0][0]
            self.hell_mobs_dic[self.hell_area_names[key]] = [mob for mob in self.hell_area_file[area_index, 100:112] if mob]