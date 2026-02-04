import arcade
from arcade.gui import UIManager, UIAnchorLayout, UIBoxLayout, UILabel, UIDropdown, UITextureButton, UIOnChangeEvent

from game_resorces import *


class SettingsScreen(arcade.View):
    def __init__(self, db, player):
        super().__init__()

        self.db = db
        self.player_music = player

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

        self.chosen_img = self.db.get_data_from_settings(ship_ind=True)  # какое изображение было выбрано

    def setup_widgets(self):
        home_texture = arcade.load_texture(home_btn_icon_img_path)
        home_btn = UITextureButton(
            texture=home_texture,
            scale=1.0,
            x=30,
            y=SCREEN_HEIGHT - 75,
            texture_hovered=home_texture,
            texture_pressed=home_texture,
            texture_disabled=home_texture
        )

        @home_btn.event('on_click')
        def home_btn_click(event):
            self.click_sound.play()

            from screens.menu_screen import MenuScreen

            print('HOME')

            menu_view = MenuScreen(self.player_music)
            self.window.show_view(menu_view)

        self.manager.add(home_btn)

        title_box = UIBoxLayout(vertical=True, space_between=100)

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
            default='ON' if self.db.get_data_from_settings(sound_background_music=True) else 'OFF'
        )

        @dropdown_background_music.event()
        def on_change(event: UIOnChangeEvent):
            print(f'New choice = {event.new_value}')

            if event.new_value == 'ON':
                self.db.set_data_to_settings(sound_background_music=1)
                self.player_music.play()
            elif event.new_value == 'OFF':
                self.db.set_data_to_settings(sound_background_music=0)
                arcade.stop_sound(self.player_music)

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
            default='ON' if self.db.get_data_from_settings(sound_shoot_sound=True) else 'OFF'
        )

        @dropdown_shoot_sound.event()
        def on_change(event: UIOnChangeEvent):
            print(f'New choice = {event.new_value}')

            if event.new_value == 'ON':
                self.db.set_data_to_settings(sound_shoot_sound=1)
            elif event.new_value == 'OFF':
                self.db.set_data_to_settings(sound_shoot_sound=0)

        shoot_sound_play.add(dropdown_shoot_sound)

        imgs_choice = UIBoxLayout(vertical=False, space_between=70)

        ship_texture1 = arcade.load_texture(ship1_img_path)
        self.ship1_img = UITextureButton(
            texture=ship_texture1,
            scale=1.1
        )

        @self.ship1_img.event('on_click')
        def on_img1_click(event):
            self.chosen_img = 0
            self.db.set_data_to_settings(ship_ind=0)

        imgs_choice.add(self.ship1_img)

        ship_texture2 = arcade.load_texture(ship2_img_path)
        self.ship2_img = UITextureButton(
            texture=ship_texture2,
            scale=1.5
        )

        @self.ship2_img.event('on_click')
        def on_img2_click(event):
            self.chosen_img = 1
            self.db.set_data_to_settings(ship_ind=1)

        imgs_choice.add(self.ship2_img)

        clear_records_box = UIBoxLayout(vertical=False, space_between=30)

        clear_btn_texture = arcade.load_texture(clear_btn_img_path)
        clear_btn = UITextureButton(
            texture=clear_btn_texture,
            scale=0.5
        )
        clear_records_box.add(clear_btn)

        level_dropdown = UIDropdown(
            options=['all levels', 'level 1', 'level 2', 'level 3'],
            width=200,
            default=''
        )

        @clear_btn.event('on_click')
        def on_clear_btn_click(event):
            self.click_sound.play()

            value = level_dropdown.value

            if not value:
                return

            match value:
                case 'all levels':
                    self.db.clear_records(all_levels=True)
                case 'level 1':
                    self.db.clear_records(level=1)
                case 'level 2':
                    self.db.clear_records(level=2)
                case _:
                    self.db.clear_records(level=3)

        clear_records_box.add(level_dropdown)

        title_box.add(music_play_background)
        self.box_layout.add(title_box)
        self.box_layout.add(shoot_sound_play)
        self.box_layout.add(imgs_choice)
        self.box_layout.add(clear_records_box)

    def setup(self):
        pass

    def on_draw(self) -> bool | None:
        self.clear()

        self.camera.use()

        arcade.draw_texture_rect(
            self.background,
            arcade.rect.XYWH(
                SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
                SCREEN_WIDTH, SCREEN_HEIGHT
            )
        )
        self.manager.draw()

        if self.chosen_img == 0:
            arcade.draw_rect_outline(arcade.rect.XYWH(
                self.ship1_img.center_x, self.ship1_img.center_y,
                self.ship1_img.width, self.ship1_img.height),
                color=arcade.color.WHITE,
                border_width=3
            )
        else:
            arcade.draw_rect_outline(arcade.rect.XYWH(
                self.ship2_img.center_x, self.ship2_img.center_y,
                self.ship2_img.width, self.ship2_img.height),
                color=arcade.color.WHITE,
                border_width=3
            )