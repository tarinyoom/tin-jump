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

    def update(self, dt, direction):
        self.elapsed += dt
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

    def text(self, surface, message, position, color=(238, 245, 230), large=False):
        font = self.title_font if large else self.font
        surface.blit(font.render(message, True, color), position)

    def draw(self, screen):
        screen.fill((160, 209, 214))
        pygame.draw.circle(screen, (255, 234, 169), (490, 155), 43)
        # Clouds drift downward as you climb.
        for i in range(9):
            x = (i * 173) % WIDTH - 40
            y = (i * 137 - self.camera * 0.25) % (HEIGHT + 100) - 50
            pygame.draw.ellipse(screen, (225, 240, 233), (x, y, 120, 25))
        for platform in self.platforms:
            y = round(platform.y - self.camera)
            if y < -30 or y > HEIGHT:
                continue
            rect = pygame.Rect(round(platform.x), y, round(platform.w), 18)
            pygame.draw.rect(screen, (81, 76, 71), rect, border_radius=5)
            pygame.draw.rect(screen, (65, 131, 89), (rect.x, rect.y, rect.w, 10), border_radius=4)
            pygame.draw.line(screen, (147, 201, 117), (rect.left + 3, rect.top + 2), (rect.right - 3, rect.top + 2), 3)
        for coin in self.coins:
            pos = (round(coin.x), round(coin.y - self.camera + math.sin(self.elapsed * 4 + coin.x) * 4))
            if -20 < pos[1] < HEIGHT + 20:
                pygame.draw.circle(screen, (166, 116, 47), pos, 11)
                pygame.draw.circle(screen, (255, 216, 100), pos, 8)
                pygame.draw.line(screen, (255, 244, 179), (pos[0], pos[1] - 4), (pos[0], pos[1] + 4), 2)
        finish = self.platforms[-1]
        fx, fy = round(finish.centerx), round(finish.top - self.camera)
        if -100 < fy < HEIGHT + 100:
            pygame.draw.line(screen, (54, 75, 73), (fx, fy - 75), (fx, fy), 4)
            pygame.draw.polygon(screen, (246, 134, 104), [(fx + 2, fy - 75), (fx + 40, fy - 63), (fx + 2, fy - 48)])
        # Draw copies at either edge so wrapping looks continuous.
        for offset in (-WIDTH - self.player.w, 0, WIDTH + self.player.w):
            rect = pygame.Rect(round(self.player.x + offset), round(self.player.y - self.camera), 30, 42)
            pygame.draw.rect(screen, (46, 65, 75), rect.move(0, 3), border_radius=8)
            pygame.draw.rect(screen, (242, 141, 99), rect, border_radius=8)
            pygame.draw.rect(screen, (255, 189, 139), (rect.x + 4, rect.y + 4, 22, 16), border_radius=5)
            pygame.draw.circle(screen, (46, 65, 75), (rect.centerx + self.facing * 6, rect.y + 12), 3)
            pygame.draw.rect(screen, (67, 92, 104), (rect.x + 3, rect.y + 28, 24, 10), border_radius=3)
        pygame.draw.rect(screen, (34, 56, 62), (16, 16, WIDTH - 32, 105), border_radius=12)
        self.text(screen, 'LITTLE LEAP', (32, 27), large=True)
        self.text(screen, f'Height  {self.height}   /   {LEVEL_STEPS * PLATFORM_GAP}', (275, 34))
        self.text(screen, f'Coins  {self.total_coins - len(self.coins)} / {self.total_coins}     Best  {self.best}', (32, 68))
        self.text(screen, 'A/D or arrows steer  •  Auto jump  •  R restart', (32, 94))
        if self.won or self.dead:
            pygame.draw.rect(screen, (34, 56, 62), (70, 270, WIDTH - 140, 180), border_radius=18)
            self.text(screen, 'You reached the top!' if self.won else 'One more jump?', (105, 300), large=True)
            self.text(screen, f'Height {self.height}  •  Coins {self.total_coins - len(self.coins)}', (145, 355))
            self.text(screen, 'Press R to try again', (205, 405))


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Little Leap — Vertical Jumper')
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
