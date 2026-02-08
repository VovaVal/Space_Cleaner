import arcade

import sys
from pathlib import Path

from screens.menu_screen import MenuScreen
from game_resorces import SCREEN_WIDTH, SCREEN_HEIGHT, GAME_TITLE, background_music_sound_path


def main():
    window = arcade.Window(width=SCREEN_WIDTH, height=SCREEN_HEIGHT, title=GAME_TITLE, visible=False)
    screen_width, screen_height = arcade.get_display_size()
    window.set_location(
        (screen_width - SCREEN_WIDTH) // 2,
        50
    )
    window.set_visible(True)

    background_music = arcade.load_sound(resource_path(background_music_sound_path))
    player_music = arcade.play_sound(background_music, loop=True)

    menu_view = MenuScreen(player_music)
    window.show_view(menu_view)
    arcade.run()


def resource_path(relative_path):
    """ Получить абсолютный путь к ресурсу"""
    try:
        base_path = Path(sys._MEIPASS)
    except Exception:
        base_path = Path(__file__).parent
    return str(base_path / relative_path)


if __name__ == '__main__':
    main()