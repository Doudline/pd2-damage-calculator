import numpy as np
import re
from PyQt5.QtWidgets import QLabel, QLineEdit

class Damage():
    def __init__(self, desc_file, missile_file):
        self.gui = None
        self.desc_file = desc_file
        self.missile_file = missile_file
        self.skill_slvl = None
        self.hit_shift_dic = {shift: 1 / (2 ** (8 - shift)) for shift in range(8, -1, -1)}

    def set_gui(self, ui):
        self.gui = ui

    def base_dmg(self):
        self.damage_label_row = 1
        self.dmg_type = None
        self.min_base_dmg = None
        self.max_base_dmg = None

        if self.gui.skill_choice and self.gui.skill_button.text() == "X":
            self.skill_slvl = self.allowed_range(self.gui.skills_grid, 0, 1, 0, 60)
            self.skill_row = self.gui.skills.file[self.gui.skill_row_number]
            self.hit_shift = self.hit_shift_dic[int(self.skill_row[np.where(self.gui.skills.file[0, :] == "HitShift")[0][0]])]
            # 220, 226 = MinDam, MaxDam
            if self.skill_row[220]:
                self.min_base_dmg = int(self.skill_row[220])
                self.max_base_dmg = int(self.skill_row[226])
                self.dmg_type = "Physical"
                self.scaling_dmg(221, 227)
                self.synergy_dmg_skill(232)
            # 234, 240, 233 = EMin, EMax, EType
            if self.skill_row[234]:
                self.min_base_dmg = int(self.skill_row[234])
                self.max_base_dmg = int(self.skill_row[240])
                self.dmg_type = self.skill_row[233]
                self.scaling_dmg(235, 241)
                self.synergy_dmg_skill(246)
            if self.gui.skill_choice in self.gui.skills.multi_components:
                self.missile_base_dmg()
        else:
            for ele_type in self.gui.ele_types_list:
                self.min_base_dmg = 0
                self.max_base_dmg = 0
                self.dmg_type = ele_type

                self.mastery_dmg()
                self.dmg_output()

    def missile_base_dmg(self):
        for type, missile_name in self.gui.skills.multi_components[self.gui.skill_choice]:
            self.skill_row = self.missile_file[int(np.where(self.missile_file[:, 0] == missile_name)[0][0])]

            self.hit_shift = self.hit_shift_dic[int(self.skill_row[np.where(self.missile_file[0, :] == "HitShift")[0][0]])]

            # 116, 122 = MinDamage, MaxDamage
            if "Physical" in type:
                self.min_base_dmg = int(self.skill_row[116])
                self.max_base_dmg = int(self.skill_row[122])
                self.dmg_type = "Physical"
                self.scaling_dmg(117, 123)
                self.synergy_dmg_missile(128)

            # 130, 136 = EMin, EMax
            else:
                self.min_base_dmg = int(self.skill_row[130])
                self.max_base_dmg = int(self.skill_row[136])
                self.dmg_type = self.skill_row[129]
                self.scaling_dmg(131, 137)
                self.synergy_dmg_missile(142)
                
    def scaling_dmg(self, min_scale_index, max_scale_index):
        min_scaling_list = [int(dmg) for dmg in self.skill_row[min_scale_index:min_scale_index + 5]]
        max_scaling_list = [int(dmg) for dmg in self.skill_row[max_scale_index:max_scale_index + 5]]

        level = 1
        for threshold, min_scale, max_scale in zip([8, 16, 22, 28, 60], min_scaling_list, max_scaling_list):
            while level < self.skill_slvl and level < threshold:
                self.min_base_dmg += min_scale
                self.max_base_dmg += max_scale

                level += 1
        
        self.min_base_dmg *= self.hit_shift        
        self.max_base_dmg *= self.hit_shift

        self.dot_adjustment(min_scale_index, max_scale_index)

    def dot_adjustment(self, min_scale_index, max_scale_index):
        multiplier = 1

        if self.skill_row[min_scale_index - 2] == "pois" and self.min_base_dmg:
            multiplier = int(self.skill_row[max_scale_index + 6])

        # for burn missiles e.g. meteorfire, as they don't have a descdam
        # but all apply 3x per frame (25 x 3)
        elif (self.skill_row[0][0]).islower() and "fire" in self.skill_row[0] and self.skill_row[0] != "fistsoffirenova":
            multiplier = 75
        
        elif self.skill_row[0] == "fofmeteor":
            multiplier = 2

        elif (self.skill_row[0][0]).isupper():
            self.desc_dam = self.desc_file[np.where(self.desc_file[:, 0] == self.skill_row[3])][0][12]

            if self.gui.skill_choice == "Inferno Sentry":
                multiplier = 25/3
            # firewall, blaze, etc.
            elif self.desc_dam in "9 27":
                multiplier = 75
            # inferno, artic blast, etc.
            elif self.desc_dam == "8":
                multiplier = 25
            # magic/cold/fire arrows
            elif self.desc_dam == "26":
                multiplier = 1/2

        self.min_base_dmg *= multiplier
        self.max_base_dmg *= multiplier

    def synergy_dmg_skill(self, params_col):
        synergies = re.findall(r"'(.+?)'(?=\D*(\d))", (self.skill_row[params_col]))
        skill_widgets_rows = self.gui.skills_grid.count() // 2

        self.synergy_percentage = 0
        for current_row in range(1, skill_widgets_rows):
            for synergy_name, synergy_param in synergies:
                if synergy_name.lower() in self.get_txt(self.gui.skills_grid, current_row, 1).lower():
                    param_index = int(np.where(self.gui.skills.file[0, :] == f"Param{synergy_param}")[0][0])

                    synergy_dmg = int(self.skill_row[param_index])
                    synergy_level = self.allowed_range(self.gui.skills_grid, current_row, 2, 0, 20)

                    self.synergy_percentage += synergy_dmg * synergy_level
                    break

        self.min_base_dmg = int(self.min_base_dmg * (1 + (self.synergy_percentage / 100)))
        self.max_base_dmg = int(self.max_base_dmg * (1 + (self.synergy_percentage / 100)))

        self.mastery_dmg()
        self.dmg_output()

    def synergy_dmg_missile(self, params_col):
        synergies = re.findall(r"'(.+?)'(?=\D*(\d))", (self.skill_row[params_col]))
        skill_widgets_rows = self.gui.skills_grid.count() // 2

        self.synergy_percentage = 0
        for current_row in range(1, skill_widgets_rows):
            for synergy_name, synergy_dmg in synergies:
                if self.skill_row[0] == "meteorfire" and synergy_name == "Fire Wall": # SEE TO THIS
                    synergy_name = ("Inferno")
                if synergy_name.lower() in self.get_txt(self.gui.skills_grid, current_row, 1).lower():
                    synergy_level = self.allowed_range(self.gui.skills_grid, current_row, 2, 0, 20)
                    self.synergy_percentage += int(synergy_dmg) * synergy_level
                    break
        
        self.min_base_dmg = int(self.min_base_dmg * (1 + (self.synergy_percentage / 100)))
        self.max_base_dmg = int(self.max_base_dmg * (1 + (self.synergy_percentage / 100)))

        self.mastery_dmg()
        self.dmg_output()

    def mastery_dmg(self):
        self.mastery_percentage = 0
        for index, mastery_type in enumerate(self.gui.ele_types_list):
            if self.dmg_type and (mastery_type == self.dmg_type or (self.dmg_type in self.gui.ele_translate and mastery_type == self.gui.ele_translate[self.dmg_type])):
                mastery_input = self.get_txt(self.gui.elemental_grid, 1 + index, 1, 0)
                if mastery_input:
                    self.mastery_percentage = int(mastery_input)
                break
        
        if self.gui.skill_choice == "Meteor":
            mastery_input = self.get_txt(self.gui.elemental_grid, 2, 1, 0)
            if mastery_input:
                self.mastery_percentage = int(mastery_input)

        if not self.min_base_dmg and not self.max_base_dmg:
            self.min_base_dmg = int(self.get_txt(self.gui.damage_grid, self.damage_label_row, 1, 0))
            self.max_base_dmg = int(self.get_txt(self.gui.damage_grid, self.damage_label_row, 2, 0))

        self.min_net_dmg = int(self.min_base_dmg * (1 + (self.mastery_percentage / 100))) 
        self.max_net_dmg = int(self.max_base_dmg * (1 + (self.mastery_percentage / 100))) 

    def dmg_output(self):
        self.effective_resistance()
        self.effective_damage()

        cols = [1, 2, 4, 5, 9]
        for input, col in zip([self.min_base_dmg, self.max_base_dmg, self.min_net_dmg, self.max_net_dmg, self.effective_dmg], cols):
            damage = self.gui.damage_grid.itemAtPosition(self.damage_label_row, col)
            if damage:
                widget = damage.widget(
                )
                if widget and isinstance(widget, QLabel):
                    widget.setText(str(input))
                elif widget:
                    widget.textChanged.disconnect(self.base_dmg)
                    widget.setText(str(input))
                    widget.textChanged.connect(self.base_dmg)


        self.damage_label_row += 1
  
    def effective_resistance(self):
        self.effective_res = 0
        for index, ele_type in enumerate(self.gui.ele_types_list):
            if self.dmg_type and (ele_type == self.dmg_type or (self.dmg_type in self.gui.ele_translate and ele_type == self.gui.ele_translate[self.dmg_type])):
                pierce = int(self.get_txt(self.gui.elemental_grid, 1 + index, 2, 0))
                perc_break = int(self.get_txt(self.gui.elemental_grid, 1 + index, 3, 0))
                initial_res = self.allowed_range(self.gui.elemental_grid, 1 + index, 4, -100, 200)

                if initial_res >= 100:
                    broken_res = initial_res - (perc_break // 2)
                else:
                    broken_res = initial_res
                    pierce += perc_break

                if broken_res > 100:
                    self.effective_res = broken_res

                elif broken_res < 0:
                    self.effective_res = broken_res - (pierce // 2)

                elif broken_res < 100:
                    pierced_res = broken_res - pierce

                    if pierced_res < 0:
                        pierced_res //= 2

                    self.effective_res = pierced_res

                txt = self.gui.damage_grid.itemAtPosition(self.damage_label_row, 7)
                if txt:
                    widget = txt.widget()
                    if widget:
                        widget.setText(str(self.effective_res))
                
                break
        
    def effective_damage(self):
        # Repeat from effective_resistance fx in case user enters their own value
        self.effective_res = int(self.get_txt(self.gui.damage_grid, self.damage_label_row, 7, 0))

        if self.effective_res < -100:
            self.effective_res = -100

        self.min_effective_dmg = self.min_net_dmg * (1 - (self.effective_res / 100)) if self.effective_res < 100 else 0
        self.max_effective_dmg = self.max_net_dmg * (1 - (self.effective_res / 100)) if self.effective_res < 100 else 0
    
        self.effective_dmg = f"{int(self.min_effective_dmg)}-{int(self.max_effective_dmg)} dmg"

    def allowed_range(self, grid, x, y, min_level, max_level):
        item = grid.itemAtPosition(x, y)
        txt = None
        if item:
            widget = item.widget()
            if widget:
                txt = widget.text()

        # Only case where I want the default to be 0 is monster resist
        if not txt and grid is self.gui.elemental_grid and y == 4:
            return 0
        if not txt:
            return min_level

        if isinstance(widget, QLineEdit):
            widget.textChanged.disconnect(self.base_dmg)
        try:
            if int(txt) < min_level:
                widget.setText(f"{min_level}")
                txt = min_level
            elif int(txt) > max_level:
                widget.setText(f"{max_level}")
                txt = max_level
        except ValueError:
            txt = "0"
        if isinstance(widget, QLineEdit):
            widget.textChanged.connect(self.base_dmg)
        
        return int(txt)

    def get_txt(self, grid, x, y, min_value = None):
        txt = grid.itemAtPosition(x, y)
        if txt:
            widget = txt.widget()
            if widget:
                if not widget.text():
                    return str(min_value)
                return widget.text()