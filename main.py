"""Little Leap: a vertical auto-jumper. Run with python main.py."""

import math
import random

import pygame

WIDTH, HEIGHT = 600, 760
STEP = 1 / 120
SPEED, GRAVITY, JUMP_SPEED = 320, 1500, 680
START_Y = HEIGHT - 70
LEVEL_STEPS = 40
PLATFORM_GAP = 95
CYAN = (65, 239, 255)
PINK = (255, 77, 192)
# Height thresholds for the three acts of the climb.
PHASE_HEIGHTS = (0, 1300, 2600)
PHASE_COLORS = ((15, 8, 32), (12, 30, 46), (38, 12, 36))
CONNECTION_PULSE_SECONDS = 0.7


def make_level():
    """A repeatable route with gaps comfortably inside the jump's reach."""
    rng = random.Random(7)
    layout = [(WIDTH / 2 - 85, START_Y, 170, 18)]
    center = WIDTH / 2
    for i in range(1, LEVEL_STEPS + 1):
        center = max(75, min(WIDTH - 75, center + rng.choice((-160, -110, 110, 160))))
        width = 150 if i == LEVEL_STEPS else max(95, 140 - i)
        layout.append((center - width / 2, START_Y - i * PLATFORM_GAP, width, 18))
    return layout


class Game:
    def __init__(self):
        self.font = pygame.font.Font(None, 25)
        self.title_font = pygame.font.Font(None, 40)
        self.head_layer = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.connection_paths = self.make_connections()
        self.effects = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        # Cache layered halos; no full-screen blur is needed each frame.
        self.platform_glows = {}
        for _, _, width, _ in make_level():
            width = round(width)
            if width in self.platform_glows:
                continue
            glow = pygame.Surface((width + 48, 66), pygame.SRCALPHA)
            for spread in range(22, 0, -2):
                pygame.draw.rect(glow, (*CYAN, int(28 * (1 - spread / 24))),
                                 (24 - spread, 24 - spread, width + spread * 2, 18 + spread * 2), border_radius=12)
            self.platform_glows[width] = glow
        self.best = 0
        self.reset()

    def reset(self):
        self.platforms = [pygame.FRect(*p) for p in make_level()]
        self.player = pygame.FRect(WIDTH / 2 - 15, START_Y - 42, 30, 42)
        self.velocity = pygame.Vector2(0, -JUMP_SPEED)
        self.camera = 0.0
        self.facing = 1
        self.coins = [pygame.Vector2(p.centerx, p.top - 30) for p in self.platforms[1:-1]]
        self.total_coins = len(self.coins)
        self.won = self.dead = False
        self.elapsed = 0.0
        self.height = 0
        self.particles = []
        self.landing_pulses = []
        self.particle_rng = random.Random()
        self.jump_count = 0
        self.connection_age = CONNECTION_PULSE_SECONDS
        self.active_connections = ()
        self.pulse_connections()  # The initial launch is a jump too.


    def update(self, dt, direction):
        self.elapsed += dt
        self.connection_age = min(CONNECTION_PULSE_SECONDS, self.connection_age + dt)
        for particle in self.particles:
            particle[0] += particle[2] * dt
            particle[1] += particle[3] * dt
            particle[3] += 240 * dt
            particle[4] -= dt
        self.particles = [p for p in self.particles if p[4] > 0]
        self.landing_pulses = [(x, y, age + dt) for x, y, age in self.landing_pulses if age + dt < 0.5]
        if self.won or self.dead:
            return
        self.velocity.x = direction * SPEED
        if direction:
            self.facing = direction
        # Wrap at the sides, just like a classic vertical jumper.
        self.player.x = (self.player.x + self.velocity.x * dt + self.player.w) % (WIDTH + self.player.w) - self.player.w
        old_bottom = self.player.bottom
        self.velocity.y += GRAVITY * dt
        self.player.y += self.velocity.y * dt
        # Platforms are one-way: only crossing a top while falling lands.
        if self.velocity.y > 0:
            for platform in self.platforms:
                if (old_bottom <= platform.top <= self.player.bottom
                        and self.player.right > platform.left
                        and self.player.left < platform.right):
                    self.player.bottom = platform.top
                    self.velocity.y = -JUMP_SPEED
                    self.pulse_connections()
                    self.landing_pulses.append((self.player.centerx, platform.top, 0))
                    for _ in range(18):
                        self.particles.append([self.player.centerx, platform.top,
                                               self.particle_rng.uniform(-160, 160),
                                               self.particle_rng.uniform(-210, -45),
                                               self.particle_rng.uniform(0.3, 0.65)])
                    if platform is self.platforms[-1]:
                        self.won = True
                    break
        self.coins = [coin for coin in self.coins
                      if not self.player.inflate(12, 12).collidepoint(coin)]
        self.height = max(self.height, int(START_Y - self.player.bottom))
        self.best = max(self.best, self.height)
        # The camera only climbs; falling off the bottom ends the run.
        self.camera = min(self.camera, self.player.centery - HEIGHT * 0.42)
        if self.player.top - self.camera > HEIGHT:
            self.dead = True

    @property
    def phase(self):
        # Use the best height of this run so falling never reverses an act.
        return sum(self.height >= threshold for threshold in PHASE_HEIGHTS[1:])

    def pulse_connections(self):
        if self.phase == 0:
            start = (self.jump_count * 2) % len(self.connection_paths)
            self.active_connections = tuple((start + i * 3) % len(self.connection_paths) for i in range(3))
            self.connection_age = 0.0
        self.jump_count += 1

    @staticmethod
    def make_connections():
        paths = []
        for i in range(9):
            y1 = 280 + i * 22
            y2 = 280 + ((i * 4 + 2) % 9) * 22
            # Each connection bends differently between the two face profiles.
            paths.append([(206, y1), (252, y1 + (i % 3 - 1) * 24),
                          (348, y2 - (i % 3 - 1) * 24), (394, y2)])
        return paths

    def draw_phase_background(self, screen):
        screen.fill(PHASE_COLORS[self.phase])
        if self.phase != 0:
            return  # The other two acts are intentionally just color placeholders.
        layer = self.head_layer
        layer.fill((0, 0, 0, 0))
        # Mirrored angular profiles: forehead, nose, lips, chin, and neck.
        profile = [(98, 530), (105, 462), (76, 420), (62, 350),
                   (74, 281), (105, 240), (160, 233), (195, 254),
                   (206, 298), (211, 320), (228, 347), (212, 356),
                   (216, 374), (207, 384), (213, 397), (207, 425),
                   (181, 448), (170, 484), (184, 530)]
        for mirrored, color in [(False, CYAN), (True, PINK)]:
            def point(x, y):
                return (WIDTH - x if mirrored else x, y)
            outline = [point(x, y) for x, y in profile]
            pygame.draw.polygon(layer, (*color, 12), outline)
            pygame.draw.lines(layer, (*color, 24), True, outline, 9)
            pygame.draw.lines(layer, (*color, 105), True, outline, 2)
            # Sparse wireframe facets and a horizontal eye give the shapes a face.
            for path in [[(76, 350), (133, 316), (195, 254)],
                         [(133, 316), (157, 396), (181, 448)],
                         [(76, 420), (157, 396), (207, 425)],
                         [(105, 462), (170, 484), (98, 530)]]:
                pygame.draw.lines(layer, (*color, 42), False, [point(x, y) for x, y in path], 1)
            pygame.draw.line(layer, (*color, 125), point(164, 320), point(196, 320), 2)
        progress = self.connection_age / CONNECTION_PULSE_SECONDS
        strength = math.sin(math.pi * progress) ** 0.6
        for i, path in enumerate(self.connection_paths):
            pygame.draw.lines(layer, (114, 59, 145, 50), False, path, 1)
            if i not in self.active_connections or progress >= 1:
                continue
            color = CYAN if i % 2 == 0 else PINK
            pygame.draw.lines(layer, (*color, int(32 * strength)), False, path, 11)
            pygame.draw.lines(layer, (*color, int(165 * strength)), False, path, 2)
            # A luminous packet travels along the connection on each bounce.
            segments = [pygame.Vector2(b) - a for a, b in zip(path, path[1:])]
            distance = progress * sum(segment.length() for segment in segments)
            pos = pygame.Vector2(path[-1])
            for start, segment in zip(path, segments):
                if distance <= segment.length():
                    pos = pygame.Vector2(start) + segment.normalize() * distance
                    break
                distance -= segment.length()
            pygame.draw.circle(layer, (*color, int(55 * strength)), pos, 9)
            pygame.draw.circle(layer, (235, 246, 255, int(230 * strength)), pos, 3)
        screen.blit(layer, (0, 0))

    def text(self, surface, message, position, color=(238, 245, 230), large=False):
        font = self.title_font if large else self.font
        surface.blit(font.render(message, True, color), position)

    def draw(self, screen):
        self.draw_phase_background(screen)
        for platform in self.platforms:
            y = round(platform.y - self.camera)
            if y < -30 or y > HEIGHT:
                continue
            rect = pygame.Rect(round(platform.x), y, round(platform.w), 18)
            screen.blit(self.platform_glows[rect.w], (rect.x - 24, rect.y - 24))
            pygame.draw.rect(screen, (12, 30, 48), rect, border_radius=5)
            pygame.draw.rect(screen, CYAN, rect, width=2, border_radius=5)
            pygame.draw.line(screen, (206, 255, 255), (rect.left + 5, rect.top + 2), (rect.right - 5, rect.top + 2), 2)
            for x in range(rect.left + 12, rect.right - 8, 22):
                pygame.draw.line(screen, (32, 99, 128), (x, rect.bottom - 5), (x + 8, rect.bottom - 5))
        self.effects.fill((0, 0, 0, 0))
        for x, y, age in self.landing_pulses:
            pos = (round(x), round(y - self.camera))
            pygame.draw.circle(self.effects, (*PINK, int(180 * (1 - age / 0.5))), pos, round(10 + age * 130), 2)
        for x, y, vx, vy, life in self.particles:
            pos = (round(x), round(y - self.camera))
            alpha = int(255 * min(1, life / 0.3))
            pygame.draw.circle(self.effects, (*PINK, alpha // 4), pos, 8)
            pygame.draw.circle(self.effects, (*PINK, alpha), pos, 3)
        screen.blit(self.effects, (0, 0))
        for coin in self.coins:
            x = round(coin.x)
            y = round(coin.y - self.camera + math.sin(self.elapsed * 4 + coin.x) * 4)
            if -20 < y < HEIGHT + 20:
                half_width = max(3, round(abs(math.cos(self.elapsed * 2 + coin.x)) * 9))
                points = [(x, y - 12), (x + half_width, y), (x, y + 12), (x - half_width, y)]
                pygame.draw.circle(screen, (52, 18, 65), (x, y), 17)
                pygame.draw.polygon(screen, (88, 25, 89), points)
                pygame.draw.polygon(screen, PINK, points, 2)
                pygame.draw.line(screen, (255, 213, 243), (x, y - 6), (x, y + 6), 2)
        finish = self.platforms[-1]
        fx, fy = round(finish.centerx), round(finish.top - self.camera)
        if -100 < fy < HEIGHT + 100:
            pygame.draw.line(screen, CYAN, (fx, fy - 75), (fx, fy), 4)
            pygame.draw.polygon(screen, PINK, [(fx + 2, fy - 75), (fx + 40, fy - 63), (fx + 2, fy - 48)])
        # Draw copies at either edge so wrapping looks continuous.
        for offset in (-WIDTH - self.player.w, 0, WIDTH + self.player.w):
            rect = pygame.Rect(round(self.player.x + offset), round(self.player.y - self.camera), 30, 42)
            pygame.draw.rect(screen, (17, 13, 40), rect.move(0, 3), border_radius=8)
            pygame.draw.rect(screen, PINK, rect, border_radius=8)
            pygame.draw.rect(screen, (48, 22, 70), (rect.x + 4, rect.y + 4, 22, 16), border_radius=5)
            pygame.draw.circle(screen, (17, 13, 40), (rect.centerx + self.facing * 6, rect.y + 12), 3)
            pygame.draw.rect(screen, CYAN, (rect.x + 3, rect.y + 28, 24, 10), border_radius=3)
        pygame.draw.rect(screen, (14, 12, 32), (16, 16, WIDTH - 32, 105), border_radius=12)
        pygame.draw.rect(screen, (72, 44, 106), (16, 16, WIDTH - 32, 105), width=1, border_radius=12)
        self.text(screen, 'NEON LEAP', (32, 27), large=True)
        self.text(screen, f'Height  {self.height}   /   {LEVEL_STEPS * PLATFORM_GAP}', (275, 34))
        self.text(screen, f'Shards  {self.total_coins - len(self.coins)} / {self.total_coins}     Phase {self.phase + 1}/3', (32, 68))
        self.text(screen, 'A/D or arrows steer  •  Auto jump  •  R restart', (32, 94))
        if self.won or self.dead:
            pygame.draw.rect(screen, (14, 12, 32), (70, 270, WIDTH - 140, 180), border_radius=18)
            self.text(screen, 'You reached the top!' if self.won else 'One more jump?', (105, 300), large=True)
            self.text(screen, f'Height {self.height}  •  Shards {self.total_coins - len(self.coins)}', (145, 355))
            self.text(screen, 'Press R to try again', (205, 405))


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Neon Leap — Vertical Jumper')
    clock = pygame.time.Clock()
    game = Game()
    accumulator = 0.0
    running = True
    while running:
        accumulator += min(clock.tick(60) / 1000, 0.05)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    game.reset()
        keys = pygame.key.get_pressed()
        direction = int(keys[pygame.K_d] or keys[pygame.K_RIGHT]) - int(keys[pygame.K_a] or keys[pygame.K_LEFT])
        while accumulator >= STEP:
            game.update(STEP, direction)
            accumulator -= STEP
        game.draw(screen)
        pygame.display.flip()
    pygame.quit()


if __name__ == '__main__':
    main()
