"""
The game data used in this program is documented in text files. I placed
the important ones in /assets/, along with the D2ExcelPlus.exe necessary to 
organize and read the files properly.

To use: double-click on D2ExcelPlus.exe, click on File then Open and choose a .txt file in the /assets/ folder.
"""

import char_skills
import gui
import damage
import monsters_and_areas

import os
import sys
import numpy as np
from PyQt5.QtWidgets import QApplication


# 'frozen' is an attribute of bundled programs, e.g. using PyInstaller
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
    asset_path = os.path.join(application_path, 'assets')
else:
    application_path = os.path.dirname(__file__)
    asset_path = os.path.join(os.path.dirname(application_path), 'assets')

with open(os.path.join(asset_path, "Skills.txt"), "r") as s_file, \
     open(os.path.join(asset_path, "SkillDesc.txt"), "r") as d_file, \
     open(os.path.join(asset_path, "Missiles.txt"), "r") as m_file, \
     open(os.path.join(asset_path, "Levels.txt"), "r") as a_file, \
     open(os.path.join(asset_path, "MonStats.txt"), "r") as st_file:

    # The asset tables are much easier to manipulate with numpy
    skill_file = np.array([line.split("\t") for line in s_file])
    desc_file = np.array([line.split("\t") for line in d_file])
    missile_file = np.array([line.split("\t") for line in m_file])
    area_file= np.array([line.split("\t") for line in a_file])
    stat_file= np.array([line.split("\t") for line in st_file])

    skills = char_skills.CharSkill()
    skills.reduce_skill_file(skill_file)
    
    app = QApplication([])
    mobs = monsters_and_areas.MonsterAreas(area_file, stat_file)
    dmg = damage.Damage(desc_file, missile_file)
    ui = gui.MyGUI(dmg, mobs, skills)

    dmg.set_gui(ui)
    app.exec_()