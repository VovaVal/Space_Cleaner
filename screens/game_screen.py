import random

import arcade
from arcade import PymunkPhysicsEngine

from game_resorces import *
from explosion_emitter import ExplosionEmitter


class GameScreen(arcade.View):
    def __init__(self, level: int):
        super().__init__()

        self.camera = arcade.camera.Camera2D()
        self.background = arcade.load_texture(background_img_path)
        self.top_blackout = arcade.load_texture(blackout_top_img_path)
        self.lives_img = arcade.load_texture(lives_img_path)
        self.pause_btn_img = arcade.load_texture(pause_btn_img_path)
        self.level = level
        self.pause = False
        self.explosions = []

        self.dragging = False
        self.mouse_x = 0
        self.mouse_y = 0

        self.bullet_sound = arcade.load_sound(bullet_sound_path)
        self.destroy_sound = arcade.load_sound(destroy_sound_path)

        arcade.schedule(self.create_bullet, 1.0)
        arcade.schedule(self.create_trash, 3.0)

    def setup(self):
        self.keys_pressed = set()
        self.explosions = []

        self.player_list = arcade.SpriteList()
        self.player = Ship()
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

        wall_thickness = 1
        walls = [
            # низ
            arcade.SpriteSolidColor(SCREEN_WIDTH + wall_thickness * 2, wall_thickness, color=(0, 0, 0, 0)),
            # вверх
            arcade.SpriteSolidColor(SCREEN_WIDTH + wall_thickness * 2, wall_thickness, color=(0, 0, 0, 0)),
            # левое
            arcade.SpriteSolidColor(wall_thickness, SCREEN_HEIGHT + wall_thickness * 2, color=(0, 0, 0, 0)),
            # правое
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

    def on_draw(self):
        self.clear()

        self.camera.use()

        arcade.draw_texture_rect(
            self.background,
            arcade.rect.XYWH(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, SCREEN_WIDTH, SCREEN_HEIGHT)
        )

        self.player_list.draw()
        self.bullet_list.draw()
        self.trash_list.draw()

        arcade.draw_texture_rect(
            self.top_blackout,
            arcade.rect.XYWH(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 25, SCREEN_WIDTH, 50)
        )

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

        arcade.draw_texture_rect(
            self.pause_btn_img,
            arcade.rect.XYWH(SCREEN_WIDTH - 40, SCREEN_HEIGHT - 25, 33, 29)
        )

        for explosion in self.explosions:
            explosion.draw()

    def create_explosion(self, x, y):
        """Создает взрыв в указанных координатах"""
        explosion = ExplosionEmitter(x, y)
        self.explosions.append(explosion)
        return explosion

    def create_bullet(self, delta: float):
        '''Создаёт пулю'''
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
        self.physics_engine.set_velocity(trash, (0, -200))

    def check_for_collision(self):
        '''Проверяет коллизии'''
        trash_ship_hit_list = arcade.check_for_collision_with_list(self.player, self.trash_list)
        if trash_ship_hit_list:
            for trash in trash_ship_hit_list:

                self.destroy_sound.play()
                trash.remove_from_sprite_lists()
                self.create_explosion(trash.center_x, trash.center_y)
                self.player.lives -= trash.get_lives()

        for bullet in self.bullet_list:
            trash_hit_list = arcade.check_for_collision_with_list(bullet, self.trash_list)

            for trash in trash_hit_list:
                trash.minus_live()

                if not trash.is_alive():
                    self.destroy_sound.play()
                    trash.remove_from_sprite_lists()
                    self.create_explosion(trash.center_x, trash.center_y)

                else:
                    vx, vy = self.physics_engine.get_physics_object(trash).body.velocity
                    self.physics_engine.set_velocity(trash, (0, -200))

                bullet.remove_from_sprite_lists()

    def on_update(self, delta_time: float):
        self.player_list.update()
        self.bullet_list.update()
        self.trash_list.update()

        self.check_for_collision()

        force_magnitude = 1200
        stop_force_multiplier = 5.0

        vx, vy = self.player.velocity

        if self.dragging:

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

        elif self.keys_pressed:
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

        for explosion in self.explosions[:]:
            explosion.update(delta_time)
            if not explosion.is_active:
                self.explosions.remove(explosion)

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
    def __init__(self):
        super().__init__()
        self.texture = arcade.load_texture(ship1_img_path)
        self.center_x = SCREEN_WIDTH / 2
        self.center_y = SCREEN_HEIGHT / 6
        self.scale = 1.0
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