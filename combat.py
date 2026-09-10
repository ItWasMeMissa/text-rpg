import random, json

from data import player, inventory, items, relic_classes, relics

combat_info= {
    'in_combat' : False,
    'player_turn' : True,
    'current_targets' : None,
    'fight_turn': 0
}

with open(f'enemies.json',encoding='utf-8') as f:
    enemies_data = json.load(f)
statuses = ["damage_mod", 'armor_mod', "vulnerable","weakness","thorns"]
excepts = ['damage_mod', 'armor_mod', 'thorns']

#enemy data
class Enemy:
    def __init__(self, name, loot, hp, armor=0, turn=1, last_action=None):
        self.name = name
        self.loot = loot
        self.hp = hp
        self.maxHP = hp
        self.statuses = {e: 0 for e in statuses}
        self.armor = armor
        self.turn = turn
        self.last_action = last_action

    def attack(self, value):
        player.take_damage(value+self.statuses['damage_mod'])
        if player.statuses.get('thorns', 0) > 0:
            self.take_damage(player.statuses['thorns'])

    def attack_buff(self, value=1):
        self.statuses['damage_mod'] += value

    def shield(self, value):
        self.armor += value
        print('func shield')

    def take_damage(self, value):
        absorbed = min(self.armor, value)
        self.armor -= absorbed
        remaining = value - absorbed
        self.hp -= remaining


class Small_Grey_Slime(Enemy):
    enemy_type = 'slime'
    size = 'small'

    def choose_option(self):
        self.armor = 0
        def tackle():
            self.attack(3)

        def goop():
            player.statuses['armor_mod'] -= 1

        actions = [tackle, goop]

        action = random.choice(actions)

        while action == self.last_action:
            action = random.choice(actions)

        self.last_action = action
        return action()


class Big_Grey_Slime(Enemy):
    enemy_type = 'slime'
    size = 'big'
    def choose_option(self):
        self.armor = 0
        def clump_shot():
            self.attack(8)

        def sticky_shot():
            player.statuses['armor_mod'] -= 2
            pass

        actions = [clump_shot, sticky_shot]

        if combat_info['fight_turn'] == 0:
            return sticky_shot()

        action = random.choice(actions)

        while action == self.last_action:
            action = random.choice(actions)

        self.last_action = action
        return action()


class Small_Green_Slime(Enemy):
    enemy_type = 'slime'
    size = 'small'

    def choose_option(self):
        self.armor = 0
        return self.attack(4)


class Big_Green_Slime(Enemy):
    enemy_type = 'slime'
    size = 'big'

    def choose_option(self):
        def chomp():
            self.attack(11)
        def sticky_shot():
            player.statuses['weakness'] += 1

        actions = [chomp, sticky_shot]

        if combat_info['fight_turn'] == 0:
            return sticky_shot()
        if random.random() < 0.67:
            action = chomp
        else:
            action = sticky_shot

        while action == self.last_action:
            self.armor = 0
            if combat_info['fight_turn'] == 0:
                return sticky_shot()
            if random.random() < 0.67:
                action = chomp
            else:
                action = sticky_shot
        self.last_action = action
        return action()


class Nibbit(Enemy):
    num = 0
    def choose_option(self):
        self.armor = 0

        def butt():
            self.attack(12)
        def hesitant():
            self.attack(6)
            self.shield(5)
        def hiss():
            self.attack_buff(2)

        actions = [ butt, hesitant, hiss]

        if len(combat_info['current_targets'])==1  and combat_info['fight_turn'] == 0:
            hesitant()
            return
        elif combat_info['fight_turn'] == 0:
            hiss()
            return
        else:
            actions[self.num]()
            self.num+=1
            if self.num > 2:
                self.num=0


class Beetle(Enemy):
    pass
    def choose_option(self):
        print('option')


class Spiter(Enemy):
    pass
    def choose_option(self):
        print('option')


class Inklets(Enemy):
    pass
    def choose_option(self):
        print('option')

# exemple #always on bottom
# class ... (Enemy) :
#    ...
#    def choose_option(self)
#        self.armor = 0
#       if ... :
#           action = ...
#    self.last_action = action
#    return action()
#enemy_list



fights = {
    'forest':{
        'easy_fights':{
            'fight_1': [
                lambda :
                    Small_Grey_Slime(name='small grey slime',
                                     **enemies_data['small_grey_slime']),
                lambda : random.choice([
                        Big_Green_Slime(name='big green slime',
                                        **enemies_data['big_green_slime']),
                        Big_Grey_Slime(name='big grey slime',
                                       **enemies_data['big_grey_slime'])]
                    ),
                lambda: Small_Green_Slime(name='small green slime',
                                      **enemies_data['small_green_slime']),
            ],
            'fight_2': [
                lambda : Nibbit(name='nibbit',
                           **enemies_data['nibbit'])
            ],
            'fight_3': [
                lambda : Beetle(name='beetle',
                           **enemies_data['beetle'])
            ],
            'fight_4': [
                lambda : Spiter(name='spiter',
                           **enemies_data['spiter'])
            ]
        },
        'hard_fights':{
            'fight_1':[
                lambda: Inklets(name='inklets',
                                 **enemies_data['inklets']),
                lambda: Inklets(name='inklets',
                                **enemies_data['inklets']),
                lambda: Inklets(name='inklets',
                                **enemies_data['inklets']),
            ],
            'fight_2':[
                lambda: Nibbit(name='nibbit',
                               **enemies_data['nibbit']),
                lambda: Nibbit(name='nibbit',
                               **enemies_data['nibbit'])
            ],
            'fight_3':[
                lambda: Big_Grey_Slime(name='big grey slime',
                                         **enemies_data['big_grey_slime']),
                lambda:Big_Green_Slime(name='big green slime',
                                        **enemies_data['big_green_slime']),
                lambda: Small_Green_Slime(name='small grey slime',
                                       **enemies_data['small_grey_slime']),
                lambda: Small_Grey_Slime(name='small green slime',
                                        **enemies_data['small_green_slime']),
            ],
            'fight_4':[
                lambda: Beetle(name='beetle',
                               **enemies_data['beetle']),
                lambda: Spiter(name='spiter',
                               **enemies_data['spiter'])
            ]
        },
        'bosses':{
            'fight_1':[

            ],
            'fight_2':[

            ],
            'fight_3':[

            ],
        }
    },
    'location': { #test name
        'easy_fights': {

        },
        'hard_fights': {

        }
    }
}

def player_attack(target):
    try:
        alive = [e for e in combat_info['current_targets'] if e.hp > 0]
        current_target = alive[target]
        current_target.take_damage(player.damage)
    except IndexError:
        print('num out of range')
        return

    if all(e.hp <= 0 for e in combat_info['current_targets']):
        return win()

    show_stats()
    enemy_attack()

def win():
        show_stats()
        for relic in player.relics:
            relics[relic].end_of_battle_effect()

        print('You win!')

        gold_total = 0
        loot_total = {}
        for enemy in combat_info['current_targets']:
            for loot, num in enemy.loot.items():
                if loot == 'gold':
                    player.gold += num
                    gold_total += num
                else:
                    inventory.add_loot(loot, num)
                    loot_total [loot] = num
        if loot_total != {}:
            print(f'total profit:\n'
                  f'gold +{gold_total}\n'
                  f'loot +{loot_total}')
        else:
            print(f'total profit:\n'
                  f'gold +{gold_total}\n')

        combat_info['in_combat'] = False
        combat_info['fight_turn'] = None
        combat_info['current_targets'] = None

def turn_up():
    for relic in player.relics:
        relics[relic].every_turn_effect()
    player.armor = 0

    combat_info['fight_turn'] += 1

    for enemy in combat_info['current_targets']:
        for status in enemy.statuses:
            if status in excepts:
                continue

            enemy.statuses[status] = max(0, enemy.statuses[status] - 1)

#enemy attack
def enemy_attack():
    for _ in [e for e in combat_info['current_targets'] if e.hp > 0]:
        _.choose_option()
    print('player hp:',player.hp)
    print(17*'_')

    turn_up()

#stats combat
def combat_start(preset, difficulty='easy_fights'):
    from data_file.map import map_info

    combat_info['in_combat'] = True
    combat_info['fight_turn'] = 0
    combat_info['current_targets'] = []

    for enemy in fights[map_info['current_location']][difficulty][preset]:
        combat_info['current_targets'].append(enemy())

    my_relics = ''
    for e in player.relics:
        my_relics += e +' | '

    print(my_relics )

    show_stats()

    changes = [relics[relic].start_of_battle_effect() for relic in player.relics]

    if "player_change" in changes:
        show_player_stats()
    if "enemy_change" in changes:
        show_enemy_stats()

def format_mods(statues):
    text = ''
    for name, value in statues.items():
        if value == 0:
            continue
        stat = name.replace('_mod', '')
        if stat == 'damage':
            kind = 'buff' if value > 0 else 'debuff'
            text += f'{stat} {kind} => {value}| '
        else:
            text += f'{name} {value} | '
        return text

def show_player_stats():
    if combat_info['fight_turn'] !=0:
        print(f'turn {combat_info['fight_turn']}')
    mods = format_mods(player.statuses)
    if mods:
        header = f'player hp: {player.hp}/{player.maxHP}\n' if player.armor <= 0 \
            else f'player hp {player.hp}/{player.maxHP}, {player.armor} armor'
        print(f'{header}\n {mods}')
    else:
        print(f'player {player.hp} hp ')

def show_enemy_stats():
    if combat_info['fight_turn'] !=0:
        print(f'turn {combat_info['fight_turn']}')
    num = 1
    for enemy in combat_info['current_targets']:
        if enemy.hp <= 0:
            print('    ', enemy.name, ' ', )
            continue
        mods = format_mods(enemy.statuses)
        if mods:
            header = f'{num} -> {enemy.name}, {enemy.hp}/{enemy.maxHP} hp\n' if enemy.armor <= 0 \
                else f'{num} -> {enemy.name}, {enemy.hp}/{enemy.maxHP} hp, {enemy.armor} armor'
            print(f'{header}\n {mods}')
        else:
            print(f'{num} -> {enemy.name}, {enemy.hp}/{enemy.maxHP} hp ')
        num += 1

#enemy hp text
def show_stats():
    if combat_info['fight_turn'] !=0:
        print(f'turn {combat_info['fight_turn']}')
    show_player_stats()
    print(17*'~')
    show_enemy_stats()
    print(17*'_')
#-----------------------------------------------------------------------------------

# fight start
#   combat_start(preset, difficulty):
#       return 'combat_stat'