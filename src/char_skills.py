import numpy as np


class CharSkill():
    """
    Manually lists and categorizes class skills from Skills.txt

    Initially accomplished through column filters and regex, but Skills.txt is not consistent therefore I consistently had to add/modify data and
    decided to write it out.

    ama, sor, nec, pal, bar, dru, ass = Amazon, Sorceress, Necromancer, Paladin, Barbarian, Druid, Assassin.

    Multi-component skills have damage components determined by multiple
    existing skills. The components are typically located in Missiles.txt

    Most categories go unused.
    """
    def __init__(self):
        self.mastery = ['Javelin and Spear Mastery', 'Fire Mastery', 'Lightning Mastery', 'Cold Mastery', 'Skeleton Mastery', 'Golem Mastery', 'Sword Mastery', 'General Mastery', 'Mace Mastery', 'Pole Arm and Spear Mastery', 'Throwing Mastery', 'Spear Mastery', 'Claw Mastery']
        self.buff = ['Cold Enchant', 'Enchant', 'Might', 'Holy Fire', 'Concentration', 'Holy Freeze', 'Holy Shock', 'Sanctuary', 'Fanaticism','Holy Shield', 'Grim Ward', 'Battle Command', 'Frenzy', 'Werewolf', 'Wearbear', 'Feral Rage', 'Heart of Wolverine', 'Venom']
        self.summon = {'ama': ['Dopplezon', 'Valkyrie'], 'nec': ['Raise Skeleton', 'Clay Golem', 'Raise Skeletal Mage', 'BloodGolem', 'Raise Skeleton Archer', 'IronGolem', 'FireGolem'], 'dru': ['Raven', 'Plague Poppy', 'Summon Spirit Wolf', 'Summon Fenris', 'Summon Grizzly'], 'ass': ['Shadow Warrior', 'Shadow Master']}
        self.spell = {'ama': ['Magic Arrow', 'Fire Arrow', 'Cold Arrow', 'Power Strike', 'Poison Javelin', 'Exploding Arrow', 'Lightning Bolt', 'Ice Arrow', 'Charged Strike', 'Plague Javelin', 'Immolation Arrow', 'Freezing Arrow', 'Lightning Strike', 'Lightning Fury'], 'sor': ['Fire Bolt', 'Charged Bolt', 'Ice Bolt', 'Inferno', 'Telekinesis', 'Frost Nova', 'Ice Blast', 'Blaze', 'Fire Ball', 'Nova', 'Lightning', 'Shiver Armor', 'Fire Wall', 'Chain Lightning', 'Glacial Spike', 'Meteor', 'Thunder Storm', 'Blizzard', 'Chilling Armor', 'Hydra', 'Frozen Orb', 'Ice Barrage', 'Combustion', 'Lesser Hydra'], 'nec': ['Teeth', 'Poison Dagger', 'Corpse Explosion', 'Desecrate', 'Bone Spear', 'Poison Nova', 'Bone Spirit'], 'pal': ['Holy Bolt', 'Holy Fire', 'Blessed Hammer', 'Holy Freeze', 'Sanctuary', 'Fist of the Heavens', 'Holy Nova', 'Holy Light'], 'bar': ['War Cry'], 'dru': ['Firestorm', 'Molten Boulder', 'Arctic Blast', 'Eruption', 'Rabies', 'Fire Claws', 'Twister', 'Shock Wave', 'Volcano', 'Tornado', 'Armageddon', 'Hurricane'], 'ass': ['Fire Trauma', 'Psychic Hammer', 'Shock Field', 'Fists of Fire', 'Cobra Strike', 'Charged Bolt Sentry', 'Wake of Fire Sentry', 'Claws of Thunder', 'Chain Lightning Sentry', 'Inferno Sentry', 'Mind Blast', 'Blades of Ice', 'Royal Strike', 'Death Sentry', 'Lightning Sentry']}
        #'pal': ['Holy Bolt', 'Holy Fire', 'Blessed Hammer', 'Holy Freeze', 'Holy Shock', 'Sanctuary', 'Fist of the Heavens', 'Holy Nova', 'Holy Light']
        self.physical = {'ama': ['Jab', 'Multiple Shot', 'Guided Arrow', 'Strafe', 'Fend'], 'pal': ['Sacrifice', 'Smite', 'Zeal', 'Charge', 'Vengeance', 'Joust'], 'bar': ['Bash', 'Double Swing', 'Stun', 'Double Throw', 'Leap Attack', 'Concentrate', 'Whirlwind', 'Berserk'], 'dru': ['Maul', 'Fury'], 'ass': ['Tiger Strike', 'Dragon Talon', 'Dragon Claw',  'Dragon Tail', 'Dragon Flight', 'Blade Sentinel', 'Blade Fury', 'Blade Shield', 'Blade Dance']}
        self.multi_components = {"Meteor": [("Burn", "meteorfire")], "Blaze": [("Fire", "blaze2ignite")], "Molten Boulder": [("Burn", "moltenboulderfirepath")], "Armageddon": [("Burn", "armageddonfire")], "Immolation Arrow": [("Burn", "immolationarrow fire")], "Fists of Fire": [("Nova Fire", "fistsoffirenova"), ("Meteor Physical", "fofmeteor"), ("Meteor Fire", "fofmeteor"), ("Meteor Burn", "fofmeteorfire")], "Claws of Thunder": [("Lightning Nova", "claws of thundernova"), ("Lightning Bolts", "claws of thunderbolt")], "Royal Strike": [("Meteor Fire", "royalstrikemeteor"), ("Meteor Burn", "royalstrikemeteorfire"), ("Lightning", "royalstrikechainlightning"), ("Cold", "royalstrikechaosice")], "Cobra Strike": [("Poison Bolt", "cobrastrikepoisonbolt"), ("Poison Cloud", "cobrastrikepoisoncloud")], "Vengeance": [("Fire"), ("Cold"), ("Lightning")]}
        self.sorc_masteries = {"Fire Mastery": [(20, 4), (1, 1, 30)], "Cold Mastery": [(10, 2), (5, 1, 45)], "Lightning Mastery": [(50, 10), (0,0, 0)]}
        self.file = None

    def reduce_skill_file(self, skill_file):
        """
        Skills.txt contains all skills, including monster
        skills. Here I filter the file to remove every row that isn't a class skill, to make later manipulations simpler.

        The main filter row[2] is the "charclass" col. i.e. a class skill.
        temp and Shattering Arrow are unimplemented class skills
        """
        rows_to_delete = []
        for row_index, row in enumerate(skill_file[1:]):
            if not row[2] or "temp" in row[0] or "Shattering Arrow" in row[0]:
                rows_to_delete.append(row_index + 1)
        
        self.file = np.delete(skill_file, rows_to_delete, axis=0)