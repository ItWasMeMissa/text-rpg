from data_file.map import *

def test_inv_event_move():
    map_info['in_event'] = True
    map_info['current_location'] = 'forest'

    road_step()

    assert map_info['current_location'] == 'forest'

def test_cant_move_without_steps():
    create_nodes(15)
    map_info['in_event'] = False
    map_info['steps'] = 15
    map_info['current_steps'] = 1
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