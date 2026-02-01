import arcade
from arcade.gui import UIManager, UIAnchorLayout, UIBoxLayout, UILabel, UIDropdown, UITextureButton

from game_resorces import *


class SettingsScreen(arcade.View):
    def __init__(self):
        super().__init__()

        self.camera = arcade.camera.Camera2D()

        self.manager = UIManager()
        self.manager.enable()

        self.anchor_layout = UIAnchorLayout()
        self.box_layout = UIBoxLayout(vertical=True, space_between=50)

        self.setup_widgets()

        self.anchor_layout.add(self.box_layout)
        self.manager.add(self.anchor_layout)

        self.background = arcade.load_texture(background_img_path)
        self.click_sound = arcade.load_sound(btn_click_sound_path)

    def setup_widgets(self):
        title_box = UIBoxLayout(vertical=True, space_between=150)

        label = UILabel(
            text='Settings',
            font_size=64,
            text_color=arcade.color.WHITE,
            align='center'
        )
        title_box.add(label)

        music_play_background = UIBoxLayout(vertical=False, space_between=20)

        label_background_music = UILabel(
            text='Background music:',
            font_size=32,
            text_color=arcade.color.WHITE,
            align='center'
        )
        music_play_background.add(label_background_music)

        dropdown_background_music = UIDropdown(
            options=['ON', 'OFF'],
            width=200,
            default='ON'
        )
        music_play_background.add(dropdown_background_music)


        shoot_sound_play = UIBoxLayout(vertical=False, space_between=20)

        label_shoot_sound = UILabel(
            text='Shoot sound:',
            font_size=32,
            text_color=arcade.color.WHITE,
            align='center'
        )
        shoot_sound_play.add(label_shoot_sound)

        dropdown_shoot_sound = UIDropdown(
            options=['ON', 'OFF'],
            width=200,
            default='ON'
        )
        shoot_sound_play.add(dropdown_shoot_sound)

        imgs_choice = UIBoxLayout(vertical=False, space_between=70)

        ship_texture1 = arcade.load_texture(ship1_img_path)
        ship1_img = UITextureButton(
            texture=ship_texture1,
            scale=1.1
        )
        imgs_choice.add(ship1_img)

        ship_texture2 = arcade.load_texture(ship2_img_path)
        ship2_img = UITextureButton(
            texture=ship_texture2,
            scale=1.5
        )
        imgs_choice.add(ship2_img)

        title_box.add(music_play_background)
        self.box_layout.add(title_box)
        self.box_layout.add(shoot_sound_play)
        self.box_layout.add(imgs_choice)

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