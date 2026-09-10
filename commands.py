import json, data, random
from combat import player_attack, combat_info
from data import player, inventory, effects_dict
from data_file.map import map_info, locations, create_nodes, road_step, events_list, nodes

#___________________________
with open('items.json', encoding='utf-8') as f:
    items = json.load(f)

#list off player available commands________________________
commands_dict = {}
def commands(func):
    commands_dict[func.__name__] = func
    return func

#save date________________________
@commands
def save(args):
    if not combat_info['in_combat']:
        if len(args) != 0:
            print('Usage: save')
            return
        if map_info['in_event']:
            print('unavailable in event')
            return
        save_data = {
            'player': player.__dict__,
            'inventory': inventory,
            'combat_info': combat_info,
            'map_info': map_info,
            'nodes': nodes
        }
        with open(f'save.json', 'w') as f:
            json.dump(save_data, f)
        print(f'file save created')
    else:
        print('u cant save in combat')


#load data________________________
@commands
def load(args):
    if len(args) != 0:
        print('Usage: load')
        return
    if map_info['in_event']:
        print('unavailable in event')
        return
    try:
        with open(f'save.json', 'r') as f:
            save_data = json.load(f)

        player.__dict__.update(save_data['player'])

        inventory.clear()
        inventory.update(save_data['inventory'])

        combat_info.clear()
        combat_info.update(save_data['combat_info'])

        map_info.clear()
        map_info.update(save_data['map_info'])

        nodes.clear()
        nodes.update(save_data['nodes'])
        print('data loaded')
    except FileNotFoundError:
        pass


#show player stats________________________
@commands
def stats(args):
    if len(args) != 0:
        print('Usage: stats')
        return
    for stat, value in player.items():
        print(f'{stat}: {value}')


#show player inventory________________________
@commands
def inv(args):
    if len(args) != 0:
        print('Usage: inv')
        return
    #args = player_num(num)
    for item, value in inventory.items():
        print(f'{item}: {value}')


#use item from player inventory________________________
@commands
def use(args):
    if len(args) != 1:
        print("Usage: use <item>")
        return
    item = args[0]
    if item not in inventory:
        print("item not found")
        return
    if item not in items:
        print("item data missing")
        return
    # 1. use effect of item
    try:
        for effect, value in items[item]['effects'].items():
            if effect in effects_dict:
                effects_dict[effect](value)
            else:
                print("effect error")
    except KeyError:
        print("item doesn't have usage ")
        return
    # 2. decrees amount of used item
    inventory[item] -= 1
    if inventory[item] <= 0:
        del inventory[item]


#remove item from player inventory________________________
@commands
def remove(args):
    if len(args) != 2:
        print('Usage: remove <item> <amount>')
        return
    if map_info['in_event']:
        print('unavailable in event')
        return
    if not args[1].isdigit():
        print('Usage: remove <item> <amount>'
              '\n                   ^^^^^^^^ must be number')
        return
    item = args[0]
    amount = int(args[1])
    if args[0] not in inventory:
        print('u dont have that item')
        return
    inventory[item] -= amount
    if inventory[item] <= 0:
        del inventory[item]


#-----------------------------------------------------------------------------------
#player attack
@commands
def attack(args):
    if len(args) != 1:
        print('Usage: attack num')
        return

    args = int(args[0])-1

    if not combat_info['in_combat']:
        print('command available only in combat')
        return

    player_attack(args)



#-----------------------------------------------------------------------------------map
# map / map ? / map travel
@commands
def map(args):
    from data_file.map import locations, choose_location
    elements = ['?', 'travel', 'help']
    if map_info['in_event']:
        print('unavailable in event')
        return
    if len(args) == 0:
        print('unlocked locations')
        for e in locations:
            if locations[e]['cleaned']:
                print(e)
            else:
                print('?')
        print(17 * '_')
        return
    #
    arg = args[0]
    if arg not in elements:
        print('such args does not exist print help to show available args')
        return

    if arg == '?':
        choose_location()
    if arg == 'travel':
        print('travel')
        return
    if arg == 'help':
        print('help')
        return


#step
@commands
def step(args):
    if len(args) != 0:
        print('Usage: step')
        return
    if combat_info['in_combat']:
        print('unavailable in combat')
        return
    if map_info['in_event']:
        print('unavailable in event')
        return
    if map_info['next_location'] is None:
        print('first choose location( map <?> )')
        return
    road_step()


#choose in unknown_event and merchant_event
def event_choice(option):
    if map_info['current_options'] is None:
        return

    if option == 'leave':
        return 'leave'

    try:
        option = int(option)
    except ValueError:
        return

    if option not in map_info['current_options']:
        print('out of range')
        return

    selected = map_info['current_options'][option]

    if map_info['current_room'] == 'unknown':
        if selected == 'leave':
            return 'leave'

        return events_list[map_info['current_event']]['func'](option-1)

    if map_info['current_room'] == 'merchant':
        if selected == 'leave':
            return 'leave'

        if not selected["available"]:
            print("Already bought.")
            return

        gold = player.gold

        if gold < selected['price']:
            print('Not enough gold.')
            return

        selected["available"] = False
        player.gold -= selected["price"]

        try:
            inventory[selected['item']] += 1
        except KeyError:
            inventory[selected['item']] = 1

        print(f"You bought {selected['item']}")
        print(f"current player gold {player.gold}$")


#exit rpg________________________
@commands
def leave(args):
    if map_info['in_event']:
        return
    if len(args) != 0:
        print('Usage: leave')
        return
    raise SystemExit


#item info
@commands
def info(args):
    if len(args) != 1:
        print('Usage: info <item>')
        return
    item = args[0]
    if item not in items:
        print(f'item dose not exist')
    else:
        print(17 * '_')
        print(f'name: {item}')
        if 'effects' in items[item]:
            print(f'Usable: True')
        for item_1, value_1 in items[item].items():
            if isinstance(value_1, dict):
                print(f"{item_1}: {value_1}")
            else:
                print(f"_____{item_1}_____: ")
                for item_2, value_2 in value_1.items():
                    print(f'{item_2}: {value_2}')


#help________________________
@commands
def help(args):
    if len(args) != 0:
        print('Usage: help')
        return
    for e in commands_dict:
        if e != 'help':
            print(e)


# -----------------------------------------------------------------------------------
# TEST/TEST/TEST/TEST/TEST
# map([])
# map('?')
# map('travel')
# map('help')

# map_info['next_location'] = 'abandoned_village'
# map_info['steps'] = locations[map_info['current_location']]['steps'][map_info['next_location']]
# create_nodes(map_info['steps'])
# step([])
#-----------------------------------------------------------------------------------
