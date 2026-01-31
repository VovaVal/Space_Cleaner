import arcade
import random
import math


class ExplosionEmitter:
    def __init__(self, x, y):
        self.center_x = x
        self.center_y = y
        self.particles = []
        self.is_active = True
        self.lifetime = 0.5  # Длительность взрыва в секундах
        self.timer = 0

        self.create_particles()

    def create_particles(self):
        """Создает частицы для взрыва"""
        num_particles = 50

        for _ in range(num_particles):
            # Случайный угол и скорость
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(100, 400)

            size = random.uniform(2, 8)

            colors = [
                (255, 255, 100),
                (255, 200, 50),
                (255, 150, 0),
                (255, 100, 0),
                (255, 50, 0)
            ]
            color = random.choice(colors)

            particle = {
                'x': self.center_x,
                'y': self.center_y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'size': size,
                'color': color,
                'alpha': 255,
                'life': random.uniform(0.3, 0.8)
            }

            self.particles.append(particle)

    def update(self, delta_time):
        if not self.is_active:
            return

        self.timer += delta_time

        for particle in self.particles:
            particle['x'] += particle['vx'] * delta_time
            particle['y'] += particle['vy'] * delta_time

            particle['vx'] *= 0.95
            particle['vy'] *= 0.95

            # Уменьшаем размер
            particle['size'] *= 0.98

            # Уменьшаем прозрачность
            particle['alpha'] = max(0, particle['alpha'] - 300 * delta_time)

            particle['life'] -= delta_time

        self.particles = [p for p in self.particles if p['life'] > 0]  # Удаление мертвых частиц

        if not self.particles or self.timer >= self.lifetime:  # Если все частицы закончились
            self.is_active = False

    def draw(self):
        if not self.is_active:
            return

        for particle in self.particles:
            arcade.draw_circle_filled(
                particle['x'],
                particle['y'],
                particle['size'],
                particle['color'] + (int(particle['alpha']),)
            )