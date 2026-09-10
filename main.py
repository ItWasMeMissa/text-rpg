from commands import commands_dict, load, event_choice
from data import running
from data_file.map import map_info

# load([])
while running:
    try:
        cmd_input = input('> ').strip().lower()
        if cmd_input == '':
            continue

        # split cmd on commands and another parts________________________
        parts = cmd_input.split()
        cmd = parts[0]
        args = parts[1:]
        if cmd in commands_dict :
            commands_dict[cmd](args)
            continue
        elif map_info['in_event']:
            if event_choice(cmd) == 'leave':
                map_info['current_options'] = None
                map_info['current_event'] = None
                map_info['in_event'] = False
                continue
        else:
            print(f'Unknown command > help ')
    except KeyboardInterrupt:
        running = False
