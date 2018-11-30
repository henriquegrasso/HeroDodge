from start_screen import start_screen
from game_loop import game_loop
from game_over_screen import game_over_screen

def main_loop():
    action = 'start_screen'
    score = Score()
    while action != 'quit':
        if action == 'start_screen':
            action = start_screen()
        elif action == 'play':
            action = game_loop()
        elif action == 'game_over_screen':
            action = game_over_screen()

main_loop()