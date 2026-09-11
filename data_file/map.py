import data
import random, json, pytest
from combat import combat_start, combat_info, fights
from data import relic_classes, player, add

items = data.items

with open('events_data.json', encoding='utf-8' ) as f:
    events_data=json.load(f)
events_list, event_resalts = events_data['events_options'], events_data['events_resalts']

with open(f'options.json', encoding='utf-8') as f:
    options = json.load(f)

# 1 > event : 2 > text, 3 > [option1, option2]

events_dict = {}
def events(func):
    events_dict[func.__name__] = func
    return func

locations = {
#exemple
    'forest':{
                'cleaned':True,
                'events':[
                    'altar',
                    'berries',
                    'broken_cart',
                    'footprints',
                    'traveler',
                    ],
                },
#exemple^^^^^^^^^^^^^^^^^^^^
    'abandoned_village':{
                    'cleaned':False,
                    'npc':[],
                },
    'cave_entrance': {
                'cleaned':False,
                }
    }



def unknown_event(func):
    events_list[func.__name__]['func'] = func
    return func

map_info = {
    'current_location': 'forest',
    'current_room': None,
    'in_event':False,
    'steps' : None,
    'current_steps':None,
    'random_num' : None,
    'num_of_elements' : None,
    'current_options': None,
    'current_event': None,
    'easy_fights_count': 0
    }
rooms = {
    'monster':{
        'base':0.18,
        'increase':0.05
        },
    'elite': {
        'base': 0.02,
        'increase': 0.01
    },
    'camp': {
        'base': 0.05,
        'increase': 0.02
    },
    'merchant': {
        'base': 0.04,
        'increase': 0.02
    },
}
roads = [
    ['forest', 'abandoned_village', 15],
    ['abandoned_village', 'cave_entrance', 15],
]
for road in roads:
    loc_1, loc_2, steps = road
    locations[loc_1].setdefault('steps', {})
    locations[loc_1]['steps'][loc_2] = steps
    #___________________
    locations[loc_2].setdefault('steps', {})
    locations[loc_2]['steps'][loc_1] = steps

merchant_pool = {
    'items': 3,
    'options': 2,
    "global": {
        "items":[],
        "options":[]
    },
}

for location in locations:
    merchant_pool[location] = {
        "items": [],
        "options": [],
    }
for name, item in items.items():
    if "location" in item  and item['relic']:
        for location in item['locations']:
            merchant_pool[location]['items'].append(name)
    else:
        if 'relic' in item:
            merchant_pool['global']['items'].append(name)

for name, effect in options.items():
    if "location" in effect:
        for location in effect['location']:
            merchant_pool[location]["options"].append(name)
    else:
        merchant_pool["global"]['options'].append(name)
#-----------------------------------------------------------------------------------
#rooms on map
nodes = {}
def create_nodes(steps):
    current_chances = {}

    for room, data in rooms.items():
        current_chances[room] = data["base"]

    # update_node_chances
    def room_roll():
        # unknown room chances + roll
        roll = random.random()
        current = 0
        # roll chance
        for room, chance in current_chances.items():
            current += chance

            if roll < current:
                return room

        return 'unknown'

    def chances_up(room):
        for e in rooms:
            if e == room:
                current_chances[e] = rooms[e]["base"]
            else:
                current_chances[e] += rooms[e]["increase"]

    for _ in range(1, steps+1):
        room = room_roll()
        nodes[_] = room
        chances_up(room)

    nodes[steps // 2] = 'treasure'
    nodes[steps-1] = 'camp'
    nodes[steps] = 'boss'

# #choose location
def choose_location():
    print('choose...')
    num = 1
    next_location = {}
    print(f'available roads')
    #text of possible roads
    for e1, e2 in locations[map_info['current_location']]['steps'].items():
        next_location[num] = {'next_location': e1, 'steps': e2}
        print(f'{num}. {e1} ({e2} steps)')
        num+=1
    #choose num and ^set next location and steps
    while True:
        cmd = input('chose num to select road\n> ')
        try:
            cmd = int(cmd)
            if cmd < num:
                for e in next_location[cmd].items():
                    map_info[e[0]] = e[1]
                map_info['steps'] = next_location[cmd]['steps']
                #cleaned ?
                if locations[map_info['next_location']]['cleaned']:
                    end_road()
                    break
                #creat rooms
                create_nodes(map_info['steps'])
                map_info['current_steps'] = 0
                #events slot wip
                print(f'next location => {map_info['next_location']} in {map_info['steps']} steps')
                break
            else:
                print('num out of range')
        except ValueError:
            print('error: enter number')

#road events-----------------------------------------------------------------------------------
#end road
def end_road(clean=False):
    global nodes
    if clean:
         locations[map_info['current_location']]['cleaned'] = True
    map_info['current_location'] = map_info['next_location']
    map_info['next_location'] = None
    map_info['steps'] = None
    map_info['current_steps'] = None
    map_info['current_room'] = None
    nodes = None

    print(f'u reached {map_info['current_location']}')
    if clean:
        print('pass cleaned u can fast travel')
    return

#step
def road_step():
    if map_info['in_event']:
        print('u cant move in event')
        return

    if combat_info['in_combat']:
        print('u cant step in combat')
        return

    if map_info['current_steps'] >= map_info['steps']:
        end_road(True)
        return

    map_info['current_steps'] += 1

    room = nodes[map_info["current_steps"]]
    map_info['current_room'] = room
    node_script(room)



#node script
def node_script(room):
    from commands import event_choice
    print(map_info['current_room'])
    if room is None:
        return

    map_info['in_event'] = True
    map_info['current_room'] = room

    events_dict[room]()
    print(17 * '_')

#_______________________________events
@events
def monster():
    pool = []
    if map_info['current_location'] == 'forest' and map_info['easy_fights_count'] <= 3:
        map_info['easy_fights_count']+=1
        for _ in fights[map_info['current_location']]['easy_fights'].keys():
            pool.append(_)
        return combat_start(random.choice(pool))
    elif map_info['easy_fights_count'] <= 2:
        for _ in fights[map_info['current_location']]['easy_fights'].keys():
            pool.append(_)
        return combat_start(random.choice(pool))
    else:
        for _ in fights[map_info['current_location']]['hard_fights'].keys():
            pool.append(_)
        return combat_start(random.choice(pool), 'hard_fights')


@events
def elite():
    # combat_start()
    return


@events
def camp():
    map_info['in_event'] = True
    pass

#merchant_________________________________________________________
#creating pool and choose loop
def create_merchant_list():
    current_options = {}
    def set_price(item):
        if item in items:
            item = items[item]
            return(
                    item['price']
                    + random.randint(-item['price_tilt'],
                                     item['price_tilt'])
            )
        if item in options:
            item = options[item]
            return(
                item['price']
                + random.randint(-item['price_tilt'],
                                 item['price_tilt'])
            )

    def merchant_list(thing, count, n=1):
        pool = merchant_pool[map_info['current_location']][thing] + merchant_pool['global'][thing]
        chosen = random.sample(pool, min(count, len(pool)))
        for item in chosen:
                current_options[n] = {
                    'item': item,
                    'price': set_price(item),
                    'available':True
                }
                n += 1
        return n

    n = merchant_list('items', merchant_pool['items'])
    n = merchant_list('options', merchant_pool['options'], n)
    current_options[n] = 'leave'

    return current_options

@events
def merchant():
    map_info['current_options'] = create_merchant_list()
    # text_____________________________________
    for num, stats in map_info['current_options'].items():
        if map_info['current_options'][num] != 'leave':
            if map_info['current_options'][num]['available']:
                print(f'{num}. => {stats['item']} for {stats['price']}$')
            else:
                print(f'{num}. => {stats['item']} unavailable')
        else:
            print(f'{num}. => {stats}')
    # ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

@events
def treasure():
    map_info['in_event'] = True
    random_relic = random.choice(relic_classes)
    player.relics.append(random_relic)
    relic_classes.pop(random_relic)
    print(f'u get {random_relic.name}')

@events
def boss():
    map_info['in_event'] = True
    pass

@events
def unknown():
    map_info['in_event'] = True
    map_info['current_event'] = random.choice(
        locations[map_info["current_location"]]["events"]
    )

    event = events_list[map_info['current_event']]

    map_info["current_options"] = create_unknown_pool()

def create_unknown_pool():
    current_options = {}
    n=1
    for _ in events_list[map_info['current_event']]['options']:
        current_options[n] = _
        n+=1
    n=1
    print(events_list[map_info['current_event']]['text'])
    for num, option in current_options.items():
        print(f'{num}. => {option}')
    return current_options

@unknown_event
def altar(info):
    print (event_resalts['altar']['0'])
    if info == 1:
        data.player.gold-=5
        print(event_resalts['altar']['1'])
        if random.choice(range(2)) == 1:
            print(event_resalts['altar']['2'])
            add('Rusty Key')
        else:
            print(event_resalts['altar']['3'])
            # spawn('skeleton')
    if info == 2:
        print(event_resalts['altar']['4'])
    return 'leave'

@unknown_event
def berries(info):
    if info == 0:
        print(event_resalts['berries']['0'])
        data.add('berries',2)
    if info == 1:
        data.heal(15)
        print(event_resalts['berries']['1'])
    if info == 2:
        print(event_resalts['berries']['2'])

    return 'leave'

@unknown_event
def broken_cart(info):
    if info == 0:
        print(event_resalts['broken_cart']['0'])
        #+random items of loc pool in inv
        #add()
    if info == 1:
        print(event_resalts['broken_cart']['1'])
    if info == 2:
        print(event_resalts['broken_cart']['2'])
    return 'leave'

@unknown_event
def footprints(info):
    if info == 0:
        print(event_resalts['footprints']['0'])
        n = random.choice(range(2))
        if n == 0:
            print('Nothing...')
        elif n == 1:
            data.add('small_potion')
        else:
            pass
    if info == 1:
        print(event_resalts['footprints']['1'])
    if info == 2:
        print(event_resalts['footprints']['2'])
    return 'leave'

@unknown_event
def traveler(info):
    if info == 0:
        data.add('small_potion')
        print(event_resalts['traveler']['0'])
    if info == 1:
        print(event_resalts['traveler']['1'])
        merchant()
    if info == 2:
        print(event_resalts['traveler']['2'])
    return 'leave'


# for _ in events_list.keys():
#     print('@unknown_event\n'
#           f'def {_}():\n'
#           f'    map_info["current_options"] = create_unknown_pool()\n'
#           )

def test_inv_event_move():
    map_info['in_event'] = True
    map_info['current_location'] = 'forest'

    road_step()

    assert map_info['current_location'] == 'forest'

def test_cant_move_without_steps():
    map_info['in_event'] = False
    map_info['steps'] = 0
    map_info['current_location'] = 'forest'

    road_step()

    assert map_info['current_location'] == 'forest'

def test_move():
    map_info['in_event'] = False
    map_info['steps'] = 15
    map_info['current_steps'] = 15
    map_info['current_location'] = 'forest'
    map_info['next_location'] = 'cave'

    road_step()

    assert map_info['current_location'] == 'cave'