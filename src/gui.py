import numpy as np
import os
import sys
import re

from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import QFont, QIntValidator
from PyQt5.QtCore import Qt

class MyGUI(QMainWindow):
    def __init__(self, dmg, mobs, skills):
        super(MyGUI, self).__init__()

        if getattr(sys, 'frozen', False):
            application_path = os.path.join(sys._MEIPASS, 'assets')
        else:
            application_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets')

        ui_path = os.path.join(application_path, 'MyGui.ui')
        uic.loadUi(ui_path, self)

        self.show()
        self.skills = skills
        self.mobs = mobs
        self.dmg = dmg
        self.class_choice = None
        self.mon_type_choice = None
        self.monster_choice = ""
        self.skill_choice = ""
        self.ele_translate = {"fire": "Fire", "cold": "Cold", "mag": "Magic", "pois": "Poison", "ltng": "Lightning", "Physical": "Physical"}
        self.skill_label.setVisible(False)
        self.skill_cbox.setVisible(False)
        self.tier_label.setVisible(False)
        self.tier_cbox.setVisible(False)
        self.area_label.setVisible(False)
        self.area_cbox.setVisible(False)
        self.mon_label.setVisible(False)
        self.mon_cbox.setVisible(False)

        actions = self.menuInfo.actions()
        for action in actions:
            action.triggered.connect(self.pop_ups)

        self.skill_button.clicked.connect(self.no_skill)
        self.mon_button.clicked.connect(self.no_mon)

        self.class_cbox.currentTextChanged.connect(self.class_skills)
        self.skill_cbox.currentTextChanged.connect(self.skill_widgets)
        self.skill_cbox.currentTextChanged.connect(self.mob_resistance)

        self.mon_type_cbox.currentTextChanged.connect(self.monster_type_selection)
        self.mon_type_cbox.currentTextChanged.connect(self.mob_selection)
        
        self.tier_cbox.currentTextChanged.connect(self.area_selection)
        self.area_cbox.currentTextChanged.connect(self.mob_selection)
        self.mon_cbox.currentTextChanged.connect(self.mob_resistance)

    def pop_ups(self):
        self.info_dic = {
        "info_summons": "Summons and sentries (traps, hydras) now benefit from +% to Elemental Skill Damage.\nSummons (except Fire Golem) now benefit from -% to Enemy Elemental Resistance at 1/2 effectivenes.\n\nBreak applies at the normal rate, like in LoD.\nTo calculate summon/sentry damage, add up their damage and halve your pierce value.\n\nSource: https://projectdiablo2.miraheze.org/wiki/Skill_Changes", 

        "info_break": "What will break immunities:\n\tBattle Cry (Physical)\n\tArctic Blast (Cold)\n\tPoison Creeper (Poison)\n\tAmplify Damage (Physical)\n\tDecrepify (Physical)\n\tLower Resist (Fire/Cold/Lightning/Poison)\n\tConviction (Fire/Cold/Lightning)\n\tSanctuary (Magic)\n\tInferno (Fire)\n\tStatic Field (Lightning)\n\nWhat will not break immunities:\n\t-enemy resistance on gear\n\tCold Mastery\n\tFire Mastery\n\nBreak applies at 1/2 rate (rather than 1/4 in LoD) to break immunities.\n\nSource: https://projectdiablo2.miraheze.org/wiki/Game_Mechanics#Behavior_of_-enemy_resists",

        "info_carryover": "For skills that carry over damage from gear or enchants (e.g. Exploding Arrow), first calculate net damage with the calculator then go into manual entry mode and add the carryover damage.",
        
        "info_su": "Superuniques aren't neatly categorized in the text files, therefore adding their resistance information to every zone/map would be a major time investment.\n\nFor this reason I have only included SUs that are frequently farmed in PD2.",

        "info_lod": "To use this tool with the base game (D2R or LoD without PD2), pay attention to the following:\n\t-don't use skill selection; manually input the damage instead\n\t-monster base resistances are generally identical except for ubers;\n\tconsider manually entering resistances\n\t-break applies at 1/4 rate to break immunities in LoD, therefore enter\n\tonly half your break value\n\t-traps benefit from elemental pierce in D2R; as I have greyed out the\n\tpierce entry for sentries and mastery doesn't apply, the calculator isn't\n\tuseful in this case."}

        option = self.sender().objectName() 
        info_text = self.info_dic[option]
        QMessageBox.information(self, "Info", info_text)

    def no_skill(self):
        self.delete_widgets()
        self.class_choice = None
        self.skill_choice = None

        if self.skill_button.text() == "X":
            self.class_cbox.setVisible(False)
            self.skill_label.setVisible(False)
            self.skill_cbox.setVisible(False)
            self.mob_resistance()
            self.skill_button.setText("✔")

        elif self.skill_button.text() == "✔":
            self.class_cbox.setCurrentText("")
            self.skill_cbox.clear()
            self.class_label.setVisible(True)
            self.class_cbox.setVisible(True)
            self.skill_button.setText("X")

    def no_mon(self):
        self.mon_type_choice = None

        if self.mon_button.text() == "X":
            self.mon_type_cbox.setVisible(False)
            self.tier_label.setVisible(False)
            self.tier_cbox.setVisible(False)
            self.area_label.setVisible(False)
            self.area_cbox.setVisible(False)
            self.mon_label.setVisible(False)
            self.mon_cbox.setVisible(False)
            self.mon_button.setText("✔")

        elif self.mon_button.text() == "✔":
            self.mon_type_cbox.setCurrentText("")
            self.tier_cbox.clear()
            self.area_cbox.clear()
            self.mon_cbox.clear()
            self.mon_type_label.setVisible(True)
            self.mon_type_cbox.setVisible(True)
            self.mon_button.setText("X")
        

        self.mob_resistance()
            

    def class_skills(self):
        self.delete_widgets()
        self.skill_label.setVisible(False)
        self.skill_cbox.setVisible(False)

        self.skill_cbox.clear()
        self.class_choice = self.class_cbox.currentText()
        if self.class_choice:
            self.skill_cbox.addItems(self.skills.spell[self.class_choice])
            self.skill_label.setVisible(True)
            self.skill_cbox.setVisible(True)
        
    def skill_widgets(self):
        self.delete_widgets()

        self.skill_choice = self.skill_cbox.currentText()
        if self.skill_choice and self.skill_button.text() == "X":
            skill_lvl_label = QLabel(f"'{self.skill_choice}'  slvl:")
            skill_lvl_input = QLineEdit("1")

            skill_lvl_input.textChanged.connect(self.dmg.base_dmg)

            validator = QIntValidator(1, 60)
            skill_lvl_input.setValidator(validator)

            self.skills_grid.addWidget(skill_lvl_label, 0, 0, Qt.AlignTop)
            self.skills_grid.addWidget(skill_lvl_input, 0, 1, Qt.AlignTop)

            self.synergy_widgets()
            self.elemental_widgets()
            self.damage_widgets()

    def synergy_widgets(self):
        if self.skill_choice:
            self.skill_row_number = np.where(self.skills.file[:, 0] == self.skill_choice)[0][0]
            self.skill_row = self.skills.file[self.skill_row_number]

            #246 = "EDmgSymPerCalc", 232 = "DmgSymPerCalc"
            self.synergies = re.findall(r"'(.+?)'(?=\D*(\d))", (self.skill_row[246]))
            if not self.synergies:
                self.synergies = re.findall(r"'(.+?)'(?=\D*(\d))", (self.skill_row[232]))
                
            synergy_widgets_list = [(QLabel(f"'{synergy}'  hlvl:"), QLineEdit("0")) for synergy, _ in self.synergies]

            if self.skill_choice == "Cobra Strike":
                synergy_widgets_list = [(QLabel("'Venom'  hlvl:"), QLineEdit("0"))]
            if self.skill_choice == "Royal Strike":
                synergy_widgets_list = [(QLabel("'Fists of Fire'  hlvl:"), QLineEdit("0")), (QLabel("'Claws of Thunder'  hlvl:"), QLineEdit("0")),(QLabel("'Blades of Ice'  hlvl:"), QLineEdit("0"))]
            
            self.add_widgets(synergy_widgets_list, self.skills_grid, 1, [1, 2], Qt.AlignTop, QIntValidator(0,20))
    
    def elemental_widgets(self):
        self.ele_types_list = []
        self.dmg_types_list = []

        # 220 == "MinDam"
        if self.skill_row[220]:
            self.ele_types_list.append("Physical")
            self.dmg_types_list.append("Physical: ")

        # 233 == "EType", 234 checks dmg because cobra strike has type but no dmg
        if self.skill_row[233] and self.skill_row[234]:
            self.ele_types_list.append(self.ele_translate[self.skill_row[233]])
            self.dmg_types_list.append(f"{self.ele_translate[self.skill_row[233]]}: ")

        if self.skill_choice in self.skills.multi_components:
            for dmg_type, _ in self.skills.multi_components[self.skill_choice]:
                for long_type in ["Physical", "Fire", "Cold", "Lightning", "Poison", "Magic"]:
                    if long_type in dmg_type and long_type not in self.ele_types_list:
                        self.ele_types_list.append(long_type)
                        break
                self.dmg_types_list.append(f"{dmg_type}: ")
        
        self.ele_widgets_list = []
        self.ele_widgets_list.append((QLabel(), QLabel("<u>Mastery</u>"), QLabel("<u>Pierce</u>"), QLabel("<u>Break %</u> (?)"), QLabel("<u>Base Monster Resistance</u>")))

        self.ele_widgets_list[0][1].setToolTip(r"Press 8 ingame.")
        self.ele_widgets_list[0][2].setToolTip(r"Press 8 ingame.")
        self.ele_widgets_list[0][3].setToolTip(r"For each element, the total -%res from every skill that can break immunities. See this page: https://projectdiablo2.miraheze.org/wiki/Game_Mechanics.")

        for ele_type in self.ele_types_list:
            mob_res_widget = QLineEdit("0") 
            """ if self.mon_type_choice or self.mon_button.text() == "X":
                mob_res_widget.setReadOnly(True)
                mob_res_widget.setStyleSheet("border: none; background-color: #f0f0f0; color: black;") """

            pierce_widget = QLineEdit("0")    
            if self.skill_choice and ("Hydra" in self.skill_choice or "Sentry" in self.skill_choice):
                pierce_widget.setReadOnly(True)
                pierce_widget.setStyleSheet("border: none; background-color: #f0f0f0; color: black;")

            if ele_type == "Physical":
                self.ele_widgets_list.append((QLabel(f"{ele_type}: "), QLabel(), pierce_widget, QLineEdit("0"), mob_res_widget))
            else:
                self.ele_widgets_list.append((QLabel(f"{ele_type}: "), QLineEdit("0"), pierce_widget, QLineEdit("0"), mob_res_widget))
        
        self.add_widgets(self.ele_widgets_list, self.elemental_grid, 0, [0, 1, 2, 3, 4], Qt.AlignTop, QIntValidator(0, 1000))
        self.damage_widgets()

    def ele_widgets_without_skill_selection(self):
        self.ele_types_list = ["Physical", "Fire", "Cold", "Lightning", "Poison", "Magic"]
        self.dmg_types_list = self.ele_types_list

        self.ele_widgets_list = []
        self.ele_widgets_list.append((QLabel(), QLabel("<u>Mastery</u>"), QLabel("<u>Pierce</u>"), QLabel("<u>Break %</u> (?)"), QLabel("<u>Base Monster Resistance</u>")))

        self.ele_widgets_list[0][1].setToolTip(r"Press 8 ingame.")
        self.ele_widgets_list[0][2].setToolTip(r"Press 8 ingame.")
        self.ele_widgets_list[0][3].setToolTip(r"For each element, the total -%res from every skill that can break immunities. See this page: https://projectdiablo2.miraheze.org/wiki/Game_Mechanics.")

        for ele_type in self.ele_types_list:
            mob_res_widget = QLineEdit("0") 

            """ 
            if self.mon_type_choice or self.mon_button.text() == "X":
                mob_res_widget.setReadOnly(True)
                mob_res_widget.setStyleSheet("border: none; background-color: #f0f0f0; color: black;")     
            """  

            pierce_widget = QLineEdit("0")    
            if self.skill_choice and ("Hydra" in self.skill_choice or "Sentry" in self.skill_choice):
                pierce_widget.setReadOnly(True)
                pierce_widget.setStyleSheet("border: none; background-color: #f0f0f0; color: black;")          

            if ele_type == "Physical":
                self.ele_widgets_list.append((QLabel(f"{ele_type}:    "), QLabel(), pierce_widget, QLineEdit("0"), mob_res_widget))
            else:
                self.ele_widgets_list.append((QLabel(f"{ele_type}:    "), QLineEdit("0"), pierce_widget, QLineEdit("0"), mob_res_widget))
        
        self.add_widgets(self.ele_widgets_list, self.elemental_grid, 0, [0, 1, 2, 3, 4], Qt.AlignTop, QIntValidator(0, 1000))
        self.damage_widgets()

    def monster_type_selection(self):
        self.tier_label.setVisible(False)
        self.tier_cbox.setVisible(False)
        self.area_label.setVisible(False)
        self.area_cbox.setVisible(False)
        self.mon_label.setVisible(False)
        self.mon_cbox.setVisible(False)
        self.tier_cbox.clear()
        self.area_cbox.clear()
        self.mon_cbox.clear()
        
        self.tier_choice = None
        self.area_choice = None

        self.mon_type_choice = self.mon_type_cbox.currentText()
        if self.mon_type_choice == "Maps" or self.mon_type_choice == "Hell Mobs":
            self.tier_label.setVisible(True)
            self.tier_cbox.setVisible(True)
            self.tier_selection()
        
    def tier_selection(self):
        self.tier_cbox.clear()
        if self.mon_type_choice == "Hell Mobs":
            self.tier_label.setText("Act :")
            self.tier_cbox.addItems(["", "Act 1", "Act 2", "Act 3", "Act 4", "Act 5"])

        elif self.mon_type_choice == "Maps":
            self.tier_label.setText("Tier:")
            self.tier_cbox.addItems(["", "T1", "T2", "T3", "Dungeon", "Unique"])

    def area_selection(self):
        self.area_cbox.clear()
        self.mon_cbox.clear()
        self.area_label.setVisible(False)
        self.area_cbox.setVisible(False)
        self.mon_label.setVisible(False)
        self.mon_cbox.setVisible(False)

        self.tier_choice = self.tier_cbox.currentText()
        if self.tier_choice and self.tier_choice != "Dungeon":
            self.area_label.setVisible(True)
            self.area_cbox.setVisible(True)
            self.area_cbox.addItem("")
            
            if self.mon_type_choice == "Hell Mobs":
                self.area_label.setText("Area: ")

                act_choice = self.tier_choice
                areas = self.mobs.hell_area_by_act[act_choice]
                self.area_cbox.addItems(areas)

            elif self.mon_type_choice == "Maps":
                self.area_label.setText("Maps: ")
                
                tier_choice = self.tier_choice
                maps = self.mobs.map_by_tier[tier_choice]
                self.area_cbox.addItems(maps)
        elif self.tier_choice == "Dungeon":
            self.mob_selection()
    
    def mob_selection(self):
        self.mon_cbox.clear()
        self.mon_label.setVisible(False)
        self.mon_cbox.setVisible(False)
        self.area_choice = self.area_cbox.currentText()

        self.mobs_list = []

        # We need this check in case an empty option is selected in one of the # cboxes
        if (self.mon_type_choice and self.mon_type_choice not in ["Hell Mobs", "Maps"]) or self.area_choice or self.tier_choice == "Dungeon":
            self.mon_label.setVisible(True)
            self.mon_cbox.setVisible(True)

        self.mobs_list = []
        # Have to do this because I didn't manually make id/strname pairs
        # for maps and dungeons
        if self.mon_type_choice in ["Hell Mobs", "Maps"] and (self.area_choice or self.tier_choice == "Dungeon"):
            mob_id_list = []
            if self.mon_type_choice == "Hell Mobs":
                mob_id_list = self.mobs.hell_mobs_dic[self.area_choice]
            elif self.mon_type_choice == "Maps" and self.tier_choice == "Dungeon":
                mob_id_list = self.mobs.map_mobs_dic["The Cathedral of Light"]
            else:
                mob_id_list = self.mobs.map_mobs_dic[self.area_choice]
            
            for mob_id in mob_id_list:
                mob_row_index = np.where(self.mobs.mon_stats[:, 0] == mob_id)[0][0]
                mob_name = self.mobs.mon_stats[mob_row_index][5]
                if not any(mob_name in item for item in self.mobs_list):
                    self.mobs_list.append((mob_id, mob_name))

        elif self.mon_type_choice and self.mon_type_choice not in ["Hell Mobs", "Maps"]:
            self.id_dic = {"Ubers": self.mobs.ubers_list, "Hell Bosses": self.mobs.act_bosses_list, "Superuniques": self.mobs.super_uniques_list, "Key Holders": self.mobs.key_holders_list}

            self.mobs_list = self.id_dic[self.mon_type_choice]

        if self.mobs_list:
            self.mon_cbox.addItem("")
            self.mon_cbox.addItems([name for _, name in self.mobs_list])

    def mob_resistance(self):
        self.monster_choice = self.mon_cbox.currentText()

        self.mob_resists = {}
        if self.monster_choice and self.mon_button.text() == "X":
            for id, name in self.mobs_list:
                if self.monster_choice == name:
                    monster_id = id
            
            mob_row_index = np.where(self.mobs.mon_stats[:, 0] == monster_id)[0][0]
            
            #141 = ResDm(H) in mon_stats
            for res, col in zip(["Physical", "Magic", "Fire", "Lightning", "Cold", "Poison"], self.mobs.mon_stats[mob_row_index, 141:147]):
                if not col:
                    col = "0"
                self.mob_resists[res] = col
            
            adjustments = {"Countess": "Fire", "Geleb Flamefinger": "Fire", "Toorc Icefist": "Cold", "Pindle": "Fire"}

            for mob in adjustments:
                if self.monster_choice == mob:
                    self.mob_resists[adjustments[mob]] = str(int(self.mob_resists[adjustments[mob]]) + 75)
        
        else:
            self.mob_resists = {ele: "0" for ele in ["Physical", "Magic", "Fire", "Lightning", "Cold", "Poison"]}

        self.modify_elemental_widget()

    def modify_elemental_widget(self):
        if self.elemental_grid.count() == 0:
            self.ele_widgets_without_skill_selection()
        
        current_row = 1
        for type_1 in self.ele_types_list:
            for type_2 in self.mob_resists:
                if type_1 == type_2:
                    item = self.elemental_grid.itemAtPosition(current_row, 4)
                    if item:
                        widget = item.widget()
                        if widget:
                            widget.setText(self.mob_resists[type_2])
                    current_row += 1
                    break

    def damage_widgets(self):
        self.delete_widgets(1)

        self.damage_widgets_list = []
        self.damage_widgets_list.append((QLabel(), QLabel("<u>Min. Base Dmg</u>"), QLabel("<u>Max. Base Dmg</u>"), QLabel(), QLabel("<u>Min. Net Dmg</u>"), QLabel("<u>Max. Net Dmg</u>"), QLabel(), QLabel("<u>Effective Resistance</u>"), QLabel(), QLabel("<u>Effective Damage</u>")))
        self.tooltips = ["", "After synergies, before mastery", "After synergies, before mastery", "", "Base * (1 + (mastery / 100))", "Base * (1 + (mastery / 100))", "", "Base resistance modified by break and pierce. See: https://projectdiablo2.miraheze.org/wiki/Game_Mechanics#Behavior_of_-enemy_resists", "", "Net * (1 - (effective monster resistance / 100))"]

        for widget, txt in zip(self.damage_widgets_list[0], self.tooltips):
            widget.setToolTip(txt)

        for dmg_type in self.dmg_types_list:
            min_base_dmg_widget = QLabel("0") if self.class_choice else QLineEdit("0") 
            max_base_dmg_widget = QLabel("0") if self.class_choice else QLineEdit("0") 

            self.damage_widgets_list.append((QLabel(dmg_type), min_base_dmg_widget, max_base_dmg_widget, QLabel(), QLabel("0"), QLabel("0"), QLabel(), QLabel("0"), QLabel(), QLabel()))

        if self.skill_choice and self.skill_choice == "Blaze":
            self.damage_widgets_list[1][0].setText("Burn :")

        self.add_widgets(self.damage_widgets_list, self.damage_grid, 0, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9], Qt.AlignTop)
    
    def add_widgets(self, widgets_list, grid, row, cols, align, validator=None):
        for tuple in widgets_list:
            for item, col in zip(tuple, cols):
                if isinstance(item, QLineEdit):
                    if validator and not (grid is self.elemental_grid and col == 4):
                        item.setValidator(validator)
                    item.textChanged.connect(self.dmg.base_dmg)
                grid.addWidget(item, row, col, align)
                grid.setColumnStretch(col, 1)
            row += 1
        grid.setRowStretch(row, 1)

    def delete_widgets(self, delete=0):
        grids = [self.skills_grid, self.damage_grid, self.elemental_grid]
        if delete == 1:
            grids = [self.damage_grid]

        for grid in grids:
            widgets_count = grid.count()
            while widgets_count > 0:
                skill = grid.takeAt(0)
                widget = skill.widget()
                if widget:
                    grid.removeWidget(widget)
                    widget.deleteLater()
                widgets_count -= 1