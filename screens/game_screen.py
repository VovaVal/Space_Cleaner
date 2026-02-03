import random

import arcade
from arcade import PymunkPhysicsEngine
from arcade.gui import UIManager, UITextureButton, UILabel, UIAnchorLayout, UIBoxLayout
from arcade.particles import Emitter, EmitBurst, FadeParticle

from game_resorces import *


class GameScreen(arcade.View):
    def __init__(self, level: int, db):
        super().__init__()

        self.camera = arcade.camera.Camera2D()

        self.background_speed = 2

        self.background1 = arcade.load_texture(background_img_path)
        self.background1_y = SCREEN_HEIGHT / 2

        self.background2 = arcade.load_texture(background_img_path)
        self.background2_y = SCREEN_HEIGHT / 2 + SCREEN_HEIGHT

        self.top_blackout = arcade.load_texture(blackout_top_img_path)
        self.full_blackout = arcade.load_texture(full_blackout_img_path)
        self.lives_img = arcade.load_texture(lives_img_path)
        self.pause_btn_img = arcade.load_texture(pause_btn_img_path)

        self.level = level
        self.pause = False
        self.game_end = False
        self.emitters = []
        self.score = 0.0
        self.db = db
        self.trash_velocity = None
        self.trash_schedule = None  # как часто будет появляться мусор
        self.shoot_sound_play = bool(self.db.get_data_from_settings(sound_shoot_sound=True))

        self.camera_shake = arcade.camera.grips.ScreenShake2D(
            self.camera.view_data,
            max_amplitude=7.0,
            acceleration_duration=0.1,
            falloff_time=0.5,
            shake_frequency=7.0,
        )

        match self.level:
            case 1:
                self.trash_velocity = LEVEL1_TRASH_VELOCITY
                self.trash_schedule = LEVEL1_TRASH_SCHEDULE
            case 2:
                self.trash_velocity = LEVEL2_TRASH_VELOCITY
                self.trash_schedule = LEVEL2_TRASH_SCHEDULE
            case _:
                self.trash_velocity = LEVEL3_TRASH_VELOCITY
                self.trash_schedule = LEVEL3_TRASH_SCHEDULE

        self.dragging = False
        self.mouse_x = 0
        self.mouse_y = 0

        self.bullet_sound = arcade.load_sound(bullet_sound_path)
        self.destroy_sound = arcade.load_sound(destroy_sound_path)
        self.click_sound = arcade.load_sound(btn_click_sound_path)

        arcade.schedule(self.create_bullet, 1.0)
        arcade.schedule(self.create_trash, self.trash_schedule)

        self.ui_manager_play = UIManager()
        self.ui_manager_pause = UIManager()
        self.ui_manager_end = UIManager()

    def setup(self):
        self.keys_pressed = set()

        self.player_list = arcade.SpriteList()
        self.player = Ship(self.db)
        self.player_list.append(self.player)

        self.trash_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()

        self.physics_engine = PymunkPhysicsEngine(
            damping=0.9,
            gravity=(0, 0)
        )
        self.physics_engine.add_sprite(
            self.player,
            mass=0.5,
            moment_of_inertia=PymunkPhysicsEngine.MOMENT_INF,
            max_velocity=500,
            friction=0.0,
            elasticity=0.0,
            collision_type='player'
        )

        self.setup_ui_play()

        self.score_text = arcade.Text(
            'Score: 0',
            130, SCREEN_HEIGHT - 40,
            color=arcade.color.BLACK,
            font_size=25,
            anchor_x='center'
        )

        wall_thickness = 1
        walls = [
            # нижняя стена
            arcade.SpriteSolidColor(SCREEN_WIDTH + wall_thickness * 2, wall_thickness, color=(0, 0, 0, 0)),
            # вверхняя стена
            arcade.SpriteSolidColor(SCREEN_WIDTH + wall_thickness * 2, wall_thickness, color=(0, 0, 0, 0)),
            # левая стена
            arcade.SpriteSolidColor(wall_thickness, SCREEN_HEIGHT + wall_thickness * 2, color=(0, 0, 0, 0)),
            # правая стена
            arcade.SpriteSolidColor(wall_thickness, SCREEN_HEIGHT + wall_thickness * 2, color=(0, 0, 0, 0)),
        ]

        walls[0].center_x = SCREEN_WIDTH / 2
        walls[0].center_y = -wall_thickness / 2

        walls[1].center_x = SCREEN_WIDTH / 2
        walls[1].center_y = (SCREEN_HEIGHT / 5) * 4 + wall_thickness / 2

        walls[2].center_x = -wall_thickness / 2 - self.player.width / 5 * 2
        walls[2].center_y = SCREEN_HEIGHT / 2

        walls[3].center_x = SCREEN_WIDTH + wall_thickness / 2 + self.player.width / 5 * 2
        walls[3].center_y = SCREEN_HEIGHT / 2

        for wall in walls:
            self.physics_engine.add_sprite(
                wall,
                body_type=PymunkPhysicsEngine.STATIC,
                friction=0.0,
                elasticity=0.0,
                collision_type="boundary"
            )

        def ignore_collision(sprite1, sprite2, arbiter, space, data):
            return False

        self.physics_engine.add_collision_handler("trash", "boundary",
                                                  begin_handler=ignore_collision,
                                                  pre_handler=ignore_collision,
                                                  post_handler=ignore_collision,
                                                  separate_handler=ignore_collision)

        self.physics_engine.add_collision_handler("bullet", "boundary",
                                                  begin_handler=ignore_collision,
                                                  pre_handler=ignore_collision,
                                                  post_handler=ignore_collision,
                                                  separate_handler=ignore_collision)

    def move_backgrounds(self):
        '''Изменяет координаты Y для двух фонов для иллюзии полёта'''
        if self.pause:
            return

        self.background1_y -= self.background_speed
        self.background2_y -= self.background_speed

        if self.background1_y == -SCREEN_HEIGHT / 2:
            self.background1_y = SCREEN_HEIGHT / 2 + SCREEN_HEIGHT
        if self.background2_y == -SCREEN_HEIGHT / 2:
            self.background2_y = SCREEN_HEIGHT / 2 + SCREEN_HEIGHT

    def setup_ui_play(self):
        '''Создаёт gui элементы для экрана игры'''
        pause_button = UITextureButton(
            x=SCREEN_WIDTH - 45,
            y=SCREEN_HEIGHT - 40,
            width=33,
            height=29,
            texture=self.pause_btn_img
        )

        @pause_button.event("on_click")
        def on_click_pause_button(event):
            self.click_sound.play()

            self.pause = True
            self.ui_manager_play.disable()
            self.setup_ui_pause()
            print('PAUSE')

        self.ui_manager_play.add(pause_button)

        self.ui_manager_play.enable()

    def setup_ui_pause(self):
        '''Создаёт gui элементы для экрана паузы игры'''
        anchor_layout = UIAnchorLayout()
        box_vertical_layout = UIBoxLayout(vertical=True, space_between=70)
        box_horizontal_layout = UIBoxLayout(vertical=False, space_between=30)

        label = UILabel(
            text='PAUSE',
            font_size=64,
            text_color=arcade.color.WHITE,
            width=300,
            align='center'
        )
        box_vertical_layout.add(label)

        continue_btn = UITextureButton(
            texture=arcade.load_texture(continue_btn_img_path), scale=0.6
        )

        @continue_btn.event("on_click")
        def on_click_continue_button(event):
            self.click_sound.play()

            self.pause = False
            self.ui_manager_pause.disable()
            self.setup_ui_play()
            print('CONTINUE')

        box_horizontal_layout.add(continue_btn)

        home_btn = UITextureButton(
            texture=arcade.load_texture(home_btn_img_path), scale=0.6
        )

        @home_btn.event("on_click")
        def on_click_home_button(event):
            self.click_sound.play()

            self.ui_manager_pause.disable()
            self.ui_manager_play.disable()
            self.ui_manager_end.disable()

            self.ui_manager_pause.clear()
            self.ui_manager_play.clear()
            self.ui_manager_end.clear()

            from screens.menu_screen import MenuScreen
            menu_view = MenuScreen()
            menu_view.setup()
            self.window.show_view(menu_view)

            print('HOME')

        box_horizontal_layout.add(home_btn)

        box_vertical_layout.add(box_horizontal_layout)
        anchor_layout.add(box_vertical_layout)

        self.ui_manager_pause.add(anchor_layout)

        self.ui_manager_pause.enable()

    def setup_ui_game_end(self, scores: list[int]):
        '''Создаёт gui элементы для экрана окончания игры'''
        anchor_layout = UIAnchorLayout()
        box_vertical_layout = UIBoxLayout(vertical=True, space_between=50)
        box_vertical_layout_records = UIBoxLayout(vertical=True, space_between=15)
        box_horizontal_layout = UIBoxLayout(vertical=False, space_between=30)

        label = UILabel(
            text='Last Records:',
            font_size=64,
            text_color=arcade.color.WHITE,
            width=350,
            align='center'
        )
        box_vertical_layout.add(label)

        label1 = UILabel(
            text=f'1) {scores[0] if len(scores) > 0 else '-'}',
            text_color=arcade.color.WHITE,
            font_size=30,
            width=250,
            align='center'
        )
        box_vertical_layout_records.add(label1)

        label2 = UILabel(
            text=f'2) {scores[1] if len(scores) > 1 else '-'}',
            text_color=arcade.color.WHITE,
            font_size=30,
            width=250,
            align='center'
        )
        box_vertical_layout_records.add(label2)

        label3 = UILabel(
            text=f'3) {scores[2] if len(scores) > 2 else '-'}',
            text_color=arcade.color.WHITE,
            font_size=30,
            width=250,
            align='center'
        )
        box_vertical_layout_records.add(label3)

        label4 = UILabel(
            text=f'4) {scores[3] if len(scores) > 3 else '-'}',
            text_color=arcade.color.WHITE,
            font_size=30,
            width=250,
            align='center'
        )
        box_vertical_layout_records.add(label4)

        label5 = UILabel(
            text=f'5) {scores[4] if len(scores) > 4 else '-'}',
            text_color=arcade.color.WHITE,
            font_size=30,
            width=250,
            align='center'
        )
        box_vertical_layout_records.add(label5)

        home_btn = UITextureButton(
            texture=arcade.load_texture(home_btn_img_path), scale=0.6
        )

        @home_btn.event("on_click")
        def on_click_home_button(event):
            self.click_sound.play()

            self.ui_manager_pause.disable()
            self.ui_manager_play.disable()
            self.ui_manager_end.disable()

            self.ui_manager_pause.clear()
            self.ui_manager_play.clear()
            self.ui_manager_end.clear()

            from screens.menu_screen import MenuScreen
            menu_view = MenuScreen()
            menu_view.setup()
            self.window.show_view(menu_view)

            print('HOME')

        box_horizontal_layout.add(home_btn)

        play_again_btn = UITextureButton(
            texture=arcade.load_texture(play_again_btn_img_path),
            scale=0.6
        )

        @play_again_btn.event("on_click")
        def on_click_play_again_button(event):
            self.click_sound.play()

            self.ui_manager_pause.disable()
            self.ui_manager_play.disable()
            self.ui_manager_end.disable()

            self.ui_manager_pause.clear()
            self.ui_manager_play.clear()
            self.ui_manager_end.clear()

            game_view = GameScreen(self.level, self.db)
            game_view.setup()
            self.window.show_view(game_view)

            print('PLAY AGAIN')

        box_horizontal_layout.add(play_again_btn)

        box_vertical_layout.add(box_vertical_layout_records)
        box_vertical_layout.add(box_horizontal_layout)
        anchor_layout.add(box_vertical_layout)

        self.ui_manager_end.add(anchor_layout)

        self.ui_manager_end.enable()

    def on_draw(self):
        self.clear()

        self.camera_shake.update_camera()
        self.camera.use()

        arcade.draw_texture_rect(
            self.background1,
            arcade.rect.XYWH(SCREEN_WIDTH / 2, self.background1_y, SCREEN_WIDTH + 20, SCREEN_HEIGHT + 20)
        )
        arcade.draw_texture_rect(
            self.background2,
            arcade.rect.XYWH(SCREEN_WIDTH / 2, self.background2_y, SCREEN_WIDTH + 20, SCREEN_HEIGHT + 20)
        )

        self.player_list.draw()
        self.bullet_list.draw()
        self.trash_list.draw()

        arcade.draw_texture_rect(
            self.top_blackout,
            arcade.rect.XYWH(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 25, SCREEN_WIDTH + 20, 70)
        )

        self.camera_shake.readjust_camera()

        if self.player.lives > 0:
            arcade.draw_texture_rect(
                self.lives_img,
                arcade.rect.XYWH(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 25,33, 29)
            )
        if self.player.lives > 1:
            arcade.draw_texture_rect(
                self.lives_img,
                arcade.rect.XYWH(SCREEN_WIDTH / 2 - 40, SCREEN_HEIGHT - 25, 33, 29)
            )
        if self.player.lives > 2:
            arcade.draw_texture_rect(
                self.lives_img,
                arcade.rect.XYWH(SCREEN_WIDTH / 2 + 40, SCREEN_HEIGHT - 25, 33, 29)
            )

        self.ui_manager_play.draw()

        self.score_text = arcade.Text(
            f'Score: {int(self.score)}',
            130, SCREEN_HEIGHT - 40,
            color=arcade.color.BLACK,
            font_size=25,
            anchor_x='center'
        )

        self.score_text.draw()

        for emitter in self.emitters:
            emitter.draw()

        if self.pause or self.game_end:
            arcade.draw_texture_rect(
                self.full_blackout,
                arcade.rect.XYWH(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, SCREEN_WIDTH, SCREEN_HEIGHT)
            )

            if self.game_end:
                self.ui_manager_end.draw()
            elif self.pause:
                self.ui_manager_pause.draw()

    def make_explosion_emitter(self, x: float, y: float):
        """Создаёт встроенный Emitter для взрыва."""

        def gravity_drag(p):  # Для искр: чуть вниз и затухание скорости
            p.change_y += -0.03
            p.change_x *= 0.92
            p.change_y *= 0.92

        return Emitter(
            center_xy=(x, y),
            emit_controller=EmitBurst(50),
            particle_factory=lambda e:FadeParticle(
                filename_or_texture=random.choice([arcade.make_circle_texture(20, arcade.color.RED),
                                                   arcade.make_circle_texture(20, arcade.color.RED_ORANGE),
                                                   arcade.make_circle_texture(20, arcade.color.RED_BROWN)]),
                change_xy=arcade.math.rand_in_circle((0.0, 0.0), 9.0),
                lifetime=random.uniform(0.5, 1.5),
                start_alpha=255, end_alpha=0,
                scale=random.uniform(0.35, 0.6),
                mutation_callback=gravity_drag
            ),
        )

    def create_bullet(self, delta: float):
        '''Создаёт пулю'''
        if self.pause:
            return

        if self.shoot_sound_play:
            self.bullet_sound.play()

        bullet = Bullet(self.player.center_x, self.player.center_y + self.player.height / 2)
        self.bullet_list.append(bullet)

        self.physics_engine.add_sprite(
            bullet,
            mass=0.1,
            moment_of_inertia=PymunkPhysicsEngine.MOMENT_INF,
            elasticity=0.0,
            friction=0.0,
            collision_type="bullet"
        )
        self.physics_engine.set_velocity(bullet, (0, 1200))

    def create_trash(self, delta: float):
        '''Создаёт мусор'''
        if self.pause:
            return

        trash = Trash(self.level)
        self.trash_list.append(trash)

        self.physics_engine.add_sprite(
            trash,
            mass=1.0,
            moment_of_inertia=PymunkPhysicsEngine.MOMENT_INF,
            elasticity=0.2,
            friction=0.0,
            collision_type="trash"
        )

        self.physics_engine.set_velocity(trash, (0, -self.trash_velocity))

    def check_for_collision(self):
        '''Проверяет коллизии'''
        trash_ship_hit_list = arcade.check_for_collision_with_list(self.player, self.trash_list)
        if trash_ship_hit_list:
            for trash in trash_ship_hit_list:

                if self.shoot_sound_play:
                    self.destroy_sound.play()

                trash.remove_from_sprite_lists()
                self.camera_shake.start()
                self.emitters.append(self.make_explosion_emitter(trash.center_x, trash.center_y))
                self.player.lives -= trash.get_lives()

                self.score += (trash.get_class() + 1) * 100

                if self.player.lives <= 0:
                    self.db.add_score_to_level(level=self.level, score=int(self.score))
                    scores = self.db.get_scores_for_level(level=self.level)
                    scores = sorted([score[0] for score in scores], reverse=True)
                    print(scores)

                    self.setup_ui_game_end(scores)
                    self.game_end = True
                    self.pause = True

        for bullet in self.bullet_list:
            trash_hit_list = arcade.check_for_collision_with_list(bullet, self.trash_list)

            for trash in trash_hit_list:
                trash.minus_live()

                if not trash.is_alive():
                    if self.shoot_sound_play:
                        self.destroy_sound.play()

                    self.camera_shake.start()
                    trash.remove_from_sprite_lists()
                    self.emitters.append(self.make_explosion_emitter(trash.center_x, trash.center_y))

                    self.score += (trash.get_class() + 1) * 100

                else:
                    vx, vy = self.physics_engine.get_physics_object(trash).body.velocity
                    self.physics_engine.set_velocity(trash, (0, -self.trash_velocity))

                bullet.remove_from_sprite_lists()

    def on_update(self, delta_time: float):
        self.camera_shake.update(delta_time=delta_time)

        self.player_list.update()
        self.bullet_list.update()
        self.trash_list.update()

        self.check_for_collision()

        self.move_backgrounds()

        self.ui_manager_play.on_update(delta_time)

        if not self.pause:
            self.score += delta_time * 10

        force_magnitude = 1200
        stop_force_multiplier = 5.0

        vx, vy = self.player.velocity

        if self.dragging and not self.pause:

            dx = self.mouse_x - self.player.center_x
            dy = self.mouse_y - self.player.center_y
            distance = (dx ** 2 + dy ** 2) ** 0.5
            if distance > 10.0:
                dir_x, dir_y = dx / distance, dy / distance
                target_vx = dir_x * 300
                target_vy = dir_y * 300

                # Плавное приближение к целевой скорости
                force = ((target_vx - vx) * force_magnitude * 0.01,
                        (target_vy - vy) * force_magnitude * 0.01)
                self.physics_engine.apply_force(self.player, force)
            else:
                # Остановка
                self.physics_engine.set_velocity(self.player, (0, 0))

        elif self.keys_pressed and not self.pause:
            target_vx, target_vy = 0, 0

            if arcade.key.LEFT in self.keys_pressed or arcade.key.A in self.keys_pressed:
                target_vx = -300
            if arcade.key.RIGHT in self.keys_pressed or arcade.key.D in self.keys_pressed:
                target_vx = 300
            if arcade.key.UP in self.keys_pressed or arcade.key.W in self.keys_pressed:
                target_vy = 300
            if arcade.key.DOWN in self.keys_pressed or arcade.key.S in self.keys_pressed:
                target_vy = -300

            # Плавное ускорение/торможение
            force_x = (target_vx - vx) * force_magnitude * 0.01
            force_y = (target_vy - vy) * force_magnitude * 0.01
            self.physics_engine.apply_force(self.player, (force_x, force_y))

        else:
            force_x = -vx * stop_force_multiplier
            force_y = -vy * stop_force_multiplier
            self.physics_engine.apply_force(self.player, (force_x, force_y))

            speed = (vx ** 2 + vy ** 2) ** 0.5
            if speed < 5:
                self.physics_engine.set_velocity(self.player, (0, 0))

        for emitter in self.emitters[:]:
            emitter.update()

        for emitter in self.emitters[:]:
            if emitter.can_reap():
                self.emitters.remove(emitter)

        if not self.pause:
            self.physics_engine.step()

    def on_key_press(self, symbol: int, modifiers: int):
        self.keys_pressed.add(symbol)
        self.dragging = False

    def on_key_release(self, symbol: int, modifiers: int):
        if symbol in self.keys_pressed:
            self.keys_pressed.remove(symbol)

    def on_mouse_drag(
        self, x: int, y: int, dx: int, dy: int, _buttons: int, _modifiers: int
    ) -> bool | None:
        self.mouse_x = x
        self.mouse_y = y
        self.dragging = True

    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int) -> bool | None:
        self.dragging = False


class Ship(arcade.Sprite):
    def __init__(self, db):
        super().__init__()
        self.texture = arcade.load_texture(ship1_img_path) if db.get_data_from_settings(ship_ind=True) == 0\
            else arcade.load_texture(ship2_img_path)
        self.center_x = SCREEN_WIDTH / 2
        self.center_y = SCREEN_HEIGHT / 6
        self.scale = 1.0 if db.get_data_from_settings(ship_ind=True) == 0 else 1.3
        self.lives = 3


class Bullet(arcade.Sprite):
    def __init__(self, x: int, y: int):
        super().__init__()
        self.texture = arcade.load_texture(bullet_img_path)
        self.center_x = x
        self.center_y = y
        self.scale = 1.0


class Trash(arcade.Sprite):
    def __init__(self, level: int):
        super().__init__()

        if level == 1:
            self.trash_class = 0

        else:
            self.trash_class = 1 if random.random() > 0.7 else 0  # выбираем класс мусора
        self.texture = arcade.load_texture(trash1_img_path) if self.trash_class == 0\
            else arcade.load_texture(trash2_img_path)
        self.scale = 0.8
        self.center_x = random.randint(self.texture.width, SCREEN_WIDTH - self.texture.width)
        self.center_y = SCREEN_HEIGHT + self.texture.height
        self.lives = 1 if self.trash_class == 0 else 2

    def minus_live(self):
        '''Отнимает жизнь у объекта мусора'''
        self.lives -= 1

    def is_alive(self):
        '''Возвращает булевое значение: True => мусор жив; False => у мусора 0 жизней'''
        return self.lives > 0

    def get_lives(self):
        '''Возвращает жизни мусора'''
        return self.lives

    def get_class(self):
        '''Возвращает класс мусора'''
        return self.trash_class