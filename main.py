import arcade

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

    background_music = arcade.load_sound(background_music_sound_path)
    player_music = arcade.play_sound(background_music, loop=True)

    menu_view = MenuScreen(player_music)
    window.show_view(menu_view)
    arcade.run()


if __name__ == '__main__':
    main()