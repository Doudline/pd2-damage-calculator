# Project Diablo 2 Damage Calculator

## Overview
This project is a graphical damage calculator for the Diablo 2: Lord of Destruction mod "Project Diablo 2". It is designed to help players optimize their builds by accurately calculating damage outputs based on in-game factors that go unreflected on the character sheet.

2nd Completed project.

## Features
- Graphical User Interface (GUI): A PyQt5-based interface that allows users to select character skills, input skill levels, and choose monsters to calculate damage against.
- Damage Modifiers: Incorporates character attributes that modify skill damage such as mastery, elemental pierce and resistance break.
- Effective Damage Calculation: Automatically calculates effective damage to monsters based on skill level, monster resistances and damage modifiers.
- Modularity: Allows manual input of skill damage and monster resistances to test out hypothetical scenarios.
- (Tested on Windows only.)

All data is sourced from the game's text files.

## Requirements
- numpy==1.26.4
- PyQt5==5.15.10
- PyQt5-Qt5==5.15.2
- PyQt5-sip==12.13.0

## Installation
[Download the executable](https://github.com/Doudline/pd2-damage-calculator/tree/main/releases)

To run from the source code (Windows):
1. Clone the root repository to your machine
2. Navigate to the directory
3. Create a venv: "python -m venv venv"
4. Activate the venv: "venv\Scripts\activate"
5. Install the required packages: "pip install -r requirements.txt"
6. Navigate to the /src/ directory

## Usage:
- Run "main.py"
- Check the "Info" menu on the top left for details.

## Keywords:
- NumPY
- PyQt5
- Damage Calculator
- Game, User Mod, Modification