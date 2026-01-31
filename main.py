import arcade

from screens.menu_screen import MenuScreen
from game_resorces import SCREEN_WIDTH, SCREEN_HEIGHT, GAME_TITLE


def main():
    window = arcade.Window(width=SCREEN_WIDTH, height=SCREEN_HEIGHT, title=GAME_TITLE)
    menu_view = MenuScreen()

    window.show_view(menu_view)
    arcade.run()


if __name__ == '__main__':
    main()