import json

running = True
current_location = 'forest'
debug = False
#
#ALWAYS USE CHECK WHAT SAVE U USE!!!!!!!!!!
#
with open(f'player_data.json', encoding='utf-8') as f:
    player_data=json.load(f)
player, inventory, statuses = player_data['player'], player_data['inventory'], player_data['statuses']

with open('items.json', encoding='utf-8') as f:
    items = json.load(f)

relics_data = {}
for name, item in items.items():
    if 'relic' in item:
        relics_data[name] = item.copy()
        relics_data[name].pop('relic')
        relics_data[name].pop('stackable')


class Player:
    def __init__(self, hp, maxHP, damage, mana, gold, level,
                 armor=0,):
        self.hp = hp
        self.maxHP = maxHP
        self.armor = armor
        self.relics = []
        self.statuses = {e: 0 for e in statuses}
        self.damage = damage
        self.mana = mana
        self.gold = gold
        self.level = level

    def take_damage(self, value):
        absorbed = min(self.armor, value)
        self.armor -= absorbed
        remaining = value - absorbed
        self.hp -= remaining

        if player.hp <= 0:
            print('You died!')
            raise SystemExit

player = Player(**player)

#player inventory________________________
effects_dict = {}
def effect(func):
    effects_dict[func.__name__] = func
    return func


#healing effect________________________
@effect
def heal(args):
    player.hp += args
    player.hp = min(player.hp , player.maxHP)
    print('current player hp:', player.hp)


#potion_cd________________________
# def potion_cd(arg):
#     wait(arg)


#get_mana________________
@effect
def mana_gain(args):
    player.mana += args
    print('current player mana:', player.mana)


#gain gold
@effect
def gain_gold(args):
    player.gold += args
    print('current player gold:', player.gold)


#add item to player inventory________________________
def add(item, amount=1):
    print(item)
    try:
        if items[item]['stackable']:
            inventory[item] = inventory.get(item, 0) + amount
        elif item['relic']:
            player.relics.append(item)
            print(f'relics: {player.relics}')
            return
        else:
            inventory[item] = 1
        print(f'current {item}: {inventory[item]}')
    except KeyError:
        print(f'{item} does not exist')

#________RELICS_______
class Relic:
    def __init__(self, name, price, price_tilt):
        self.name = name
        self.stackable = False
        self.price = price
        self.price_tilt = price_tilt
        self.shop = {
            "price": self.price,
            "price_tilt": self.price_tilt,
        }
        del (self.price, self.price_tilt)

class Anchor(Relic):
    def start_of_battle_effect(self):
        player.armor += 10
        return "player_change"

    def every_turn_effect(self):
        pass

    def end_of_battle_effect(self):
        pass


class Bag_of_Marbles(Relic):
    def start_of_battle_effect(self):
        from combat import combat_info
        for enemy in combat_info['current_targets']:
            enemy.statuses['vulnerable'] += 1
        return "enemy_change"

    def every_turn_effect(self):
        pass

    def end_of_battle_effect(self):
        pass


class Bronze_Scales(Relic):
    def start_of_battle_effect(self):
        from combat import combat_info
        player.statuses['thorns']+=3
        return "player_change"

    def every_turn_effect(self):
        pass

    def end_of_battle_effect(self):
        pass

class Festive_Popper(Relic):
    def start_of_battle_effect(self):
        from combat import combat_info
        for enemy in combat_info['current_targets']:
            enemy.take_damage(9)
            return "enemy_change"

    def every_turn_effect(self):
        pass

    def end_of_battle_effect(self):
        pass

class Happy_Flower(Relic):
    def start_of_battle_effect(self):
        pass

    def every_turn_effect(self):
        from combat import combat_info
        turn = combat_info['fight_turn'] + 1
        if turn % 3 == 0:
            player.hp += 5
        return "player_change"

    def end_of_battle_effect(self):
        pass

class Strike_Dummy(Relic):
    def start_of_battle_effect(self):
        player.statuses['damage_mod'] += 3

    def every_turn_effect(self):
        pass

    def end_of_battle_effect(self):
        pass

relic_classes = {
    'Bag of Marbles': Bag_of_Marbles,
    'Anchor': Anchor,
    'Bronze Scales':Bronze_Scales,
    'Festive Popper':Festive_Popper,
    'Happy Flower':Happy_Flower,
    'Strike Dummy':Strike_Dummy,
}

relics = {name: cls(name=name, **relics_data[name])
          for name, cls in relic_classes.items()}

#player.relics = relics.keys()
