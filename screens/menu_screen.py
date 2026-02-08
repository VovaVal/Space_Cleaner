import sys
from pathlib import Path

import arcade
from arcade.gui import UIManager, UIAnchorLayout, UIBoxLayout, UILabel, UITextureButton

from game_resorces import *
from screens.game_screen import GameScreen
from database import DataBase
from screens.settings_screen import SettingsScreen


class MenuScreen(arcade.View):
    def __init__(self, player):
        super().__init__()

        self.db = DataBase()  # подключаем/открываем базу данных
        print(self.db.get_data_for_all_levels())

        self.camera = arcade.camera.Camera2D()

        self.manager = UIManager()
        self.manager.enable()

        self.anchor_layout = UIAnchorLayout()
        self.box_layout = UIBoxLayout(vertical=True, space_between=50)

        self.setup_widgets()

        self.anchor_layout.add(self.box_layout)
        self.manager.add(self.anchor_layout)

        self.player_music = player

        if self.db.get_data_from_settings(sound_background_music=True):
            self.player_music.play()
        elif not self.db.get_data_from_settings(sound_background_music=True):
            arcade.stop_sound(self.player_music)

        self.background = arcade.load_texture(resource_path(background_img_path))
        self.click_btn_sound = arcade.load_sound(resource_path(btn_click_sound_path))

    def setup_widgets(self):
        label = UILabel(text='Space Cleaner', font_size=48, text_color=arcade.color.WHITE, align='center')
        self.box_layout.add(label)

        title_box = UIBoxLayout(vertical=True)
        title_box.add(label)

        buttons_box = UIBoxLayout(vertical=True, space_between=40)

        texture_normal1 = arcade.load_texture(resource_path(button_level1_img_path))
        level1_btn = UITextureButton(
            texture=texture_normal1,
            scale=1.0
        )

        texture_normal2 = arcade.load_texture(resource_path(button_level2_img_path))
        level2_btn = UITextureButton(
            texture=texture_normal2,
            scale=1.0
        )

        texture_normal3 = arcade.load_texture(resource_path(button_level3_img_path))
        level3_btn = UITextureButton(
            texture=texture_normal3,
            scale=1.0
        )

        buttons_box.add(level1_btn)
        buttons_box.add(level2_btn)
        buttons_box.add(level3_btn)

        settings_box = UIBoxLayout(vertical=True, space_between=50)

        texture_settings = arcade.load_texture(resource_path(settings_btn_img_path))
        settings_btn = UITextureButton(
            texture=texture_settings,
            scale=1.0
        )

        settings_box.add(settings_btn)

        main_box = UIBoxLayout(vertical=True, space_between=70)
        main_box.add(title_box)
        main_box.add(buttons_box)
        main_box.add(settings_box)

        self.box_layout.add(main_box)

        level1_btn.on_click = lambda event: self.start_level(level=1)
        level2_btn.on_click = lambda event: self.start_level(level=2)
        level3_btn.on_click = lambda event: self.start_level(level=3)
        settings_btn.on_click = lambda event: self.open_settings()

    def setup(self):
        pass

    def open_settings(self):
        '''Открывает окно настроек'''
        self.click_btn_sound.play()

        self.manager.disable()
        self.manager.clear()

        settings_view = SettingsScreen(self.db, self.player_music)
        settings_view.setup()
        self.window.show_view(settings_view)

    def start_level(self, level: int):
        '''Начинает игру по заданному уровню сложности'''
        self.click_btn_sound.play()
        arcade.stop_sound(self.player_music)

        self.manager.disable()
        self.manager.clear()

        game_view = GameScreen(level, self.db, self.player_music)
        game_view.setup()
        self.window.show_view(game_view)

    def on_draw(self) -> bool | None:
        self.clear()

        self.camera.use()

        arcade.draw_texture_rect(
            self.background,
            arcade.rect.XYWH(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, SCREEN_WIDTH, SCREEN_HEIGHT)
        )
        self.manager.draw()

    def on_update(self, delta_time: float) -> bool | None:
        pass


def resource_path(relative_path):
    """ Получить абсолютный путь к ресурсу"""
    try:
        base_path = Path(sys._MEIPASS)
    except Exception:
        base_path = Path(__file__).parent.parent
    return str(base_path / relative_path)