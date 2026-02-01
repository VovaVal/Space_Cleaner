import arcade
from arcade.gui import UIManager

from game_resorces import *


class SettingsScreen(arcade.View):
    def __init__(self):
        super().__init__()

        self.camera = arcade.camera.Camera2D()

        self.manager = UIManager()
        self.manager.enable()

        self.background = arcade.load_texture(background_img_path)

    def setup(self):
        pass

    def on_draw(self) -> bool | None:
        self.clear()

        self.camera.use()

        arcade.draw_texture_rect(
            self.background,
            arcade.rect.XYWH(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, SCREEN_WIDTH, SCREEN_HEIGHT)
        )
        self.manager.draw()