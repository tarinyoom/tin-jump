"""Little Leap: an asset-free pygame-ce platformer. Run with python main.py."""

import math
import pygame

WIDTH, HEIGHT = 960, 540
WORLD_WIDTH = 3300
STEP = 1 / 120
SPEED, GRAVITY, JUMP_SPEED = 310, 1800, 650
# (x, y, width, height); coordinates are in world space.
PLATFORM_LAYOUT = [
    (0, 460, 620, 120), (740, 460, 500, 120),
    (1390, 460, 620, 120), (2200, 460, 1100, 120),
    (230, 355, 150, 22), (450, 270, 145, 22),
    (650, 350, 135, 22), (940, 350, 150, 22),
    (1160, 270, 150, 22), (1350, 350, 140, 22),
    (1660, 345, 145, 22), (1850, 265, 145, 22),
    (2040, 345, 150, 22), (2400, 350, 150, 22),
    (2600, 265, 150, 22), (2800, 350, 150, 22),
]
JUMP_KEYS = (pygame.K_SPACE, pygame.K_w, pygame.K_UP)


class Game:
    def __init__(self):
        self.platforms = [pygame.FRect(*p) for p in PLATFORM_LAYOUT]
        self.font = pygame.font.Font(None, 25)
        self.title_font = pygame.font.Font(None, 40)
        self.reset()

    def reset(self):
        self.spawn = (70, 410)
        self.player = pygame.FRect(*self.spawn, 30, 42)
        self.velocity = pygame.Vector2()
        self.grounded = False
        self.coyote = self.jump_buffer = self.camera = 0.0
        self.facing = 1
        self.coins = [pygame.Vector2(x + w / 2, y - 30)
                      for x, y, w, h in PLATFORM_LAYOUT if h == 22]
        self.total_coins = len(self.coins)
        self.checkpoint = self.won = False
        self.elapsed = 0.0

    def respawn(self):
        self.player.topleft = self.spawn
        self.velocity.update(0, 0)
        self.grounded = False
        self.coyote = self.jump_buffer = 0.0

    def update(self, dt, direction):
        self.elapsed += dt
        if self.won:
            return
        self.coyote = 0.1 if self.grounded else max(0, self.coyote - dt)
        self.jump_buffer = max(0, self.jump_buffer - dt)
        if self.jump_buffer > 0 and self.coyote > 0:
            self.velocity.y = -JUMP_SPEED
            self.grounded = False
            self.coyote = self.jump_buffer = 0
        self.velocity.x = direction * SPEED
        if direction:
            self.facing = direction
        self.player.x += self.velocity.x * dt
        for platform in self.platforms:
            if self.player.colliderect(platform):
                if direction > 0:
                    self.player.right = platform.left
                elif direction < 0:
                    self.player.left = platform.right
        self.player.x = max(0, min(self.player.x, WORLD_WIDTH - self.player.w))
        self.velocity.y = min(self.velocity.y + GRAVITY * dt, 1000)
        self.player.y += self.velocity.y * dt
        self.grounded = False
        for platform in self.platforms:
            if self.player.colliderect(platform):
                if self.velocity.y > 0:
                    self.player.bottom = platform.top
                    self.grounded = True
                elif self.velocity.y < 0:
                    self.player.top = platform.bottom
                self.velocity.y = 0
        self.coins = [coin for coin in self.coins
                      if not self.player.inflate(12, 12).collidepoint(coin)]
        if not self.checkpoint and self.player.colliderect(pygame.FRect(1510, 395, 40, 65)):
            self.checkpoint = True
            self.spawn = (1515, 410)
        if self.player.y > HEIGHT + 200:
            self.respawn()
        if self.player.colliderect(pygame.FRect(3130, 345, 45, 115)):
            self.won = True
        target = max(0, min(self.player.centerx - WIDTH * 0.38, WORLD_WIDTH - WIDTH))
        self.camera += (target - self.camera) * min(1, dt * 8)

    def text(self, surface, message, position, color=(238, 245, 230), large=False):
        surface.blit((self.title_font if large else self.font).render(message, True, color), position)

    def draw(self, screen):
        screen.fill((160, 209, 214))
        pygame.draw.circle(screen, (255, 234, 169), (790, 100), 43)
        for layer, color in [(0.18, (124, 178, 175)), (0.35, (91, 151, 147))]:
            for i in range(-1, 9):
                x = i * 480 - int(self.camera * layer) % 480
                pygame.draw.polygon(screen, color, [(x - 100, 460), (x + 160, 185 + i % 3 * 40), (x + 450, 460)])
        for i in range(7):
            x = int(i * 410 - self.camera * 0.15) % (WIDTH + 250) - 125
            pygame.draw.ellipse(screen, (225, 240, 233), (x, 65 + i % 3 * 30, 120, 25))
        for platform in self.platforms:
            rect = pygame.Rect(round(platform.x - self.camera), round(platform.y), round(platform.w), round(platform.h))
            pygame.draw.rect(screen, (81, 76, 71), rect, border_radius=4)
            pygame.draw.rect(screen, (114, 102, 83), rect.inflate(-8, -10), border_radius=3)
            pygame.draw.rect(screen, (65, 131, 89), (rect.x, rect.y, rect.w, 10), border_radius=3)
            pygame.draw.line(screen, (147, 201, 117), (rect.left + 3, rect.top + 2), (rect.right - 3, rect.top + 2), 3)
        for coin in self.coins:
            pos = (round(coin.x - self.camera), round(coin.y + math.sin(self.elapsed * 4 + coin.x) * 4))
            pygame.draw.circle(screen, (166, 116, 47), pos, 11)
            pygame.draw.circle(screen, (255, 216, 100), pos, 8)
            pygame.draw.line(screen, (255, 244, 179), (pos[0], pos[1] - 4), (pos[0], pos[1] + 4), 2)
        for x, top, color in [(1530, 395, (255, 214, 104) if self.checkpoint else (219, 236, 221)), (3150, 345, (246, 134, 104))]:
            sx = round(x - self.camera)
            pygame.draw.line(screen, (54, 75, 73), (sx, top), (sx, 460), 4)
            pygame.draw.polygon(screen, color, [(sx + 2, top), (sx + 40, top + 12), (sx + 2, top + 27)])
        rect = pygame.Rect(round(self.player.x - self.camera), round(self.player.y), 30, 42)
        pygame.draw.rect(screen, (46, 65, 75), rect.move(0, 3), border_radius=8)
        pygame.draw.rect(screen, (242, 141, 99), rect, border_radius=8)
        pygame.draw.rect(screen, (255, 189, 139), (rect.x + 4, rect.y + 4, 22, 16), border_radius=5)
        eye_x = rect.centerx + self.facing * 6
        pygame.draw.circle(screen, (46, 65, 75), (eye_x, rect.y + 12), 3)
        pygame.draw.rect(screen, (67, 92, 104), (rect.x + 3, rect.y + 28, 24, 10), border_radius=3)
        pygame.draw.rect(screen, (34, 56, 62), (16, 16, 928, 64), border_radius=12)
        self.text(screen, 'LITTLE LEAP', (32, 24), large=True)
        self.text(screen, f'Coins  {self.total_coins - len(self.coins)} / {self.total_coins}', (320, 37))
        self.text(screen, 'A/D move    Space jump    R restart', (560, 37))
        if self.checkpoint and not self.won:
            self.text(screen, 'Checkpoint reached', (24, 98), (34, 56, 62))
        if self.won:
            panel = pygame.Rect(230, 170, 500, 180)
            pygame.draw.rect(screen, (34, 56, 62), panel, border_radius=18)
            self.text(screen, 'You made it!', (365, 202), large=True)
            self.text(screen, f'Collected {self.total_coins - len(self.coins)} of {self.total_coins} coins', (355, 255))
            self.text(screen, 'Press R to play again', (375, 295))


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Little Leap')
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
                elif event.key in JUMP_KEYS:
                    game.jump_buffer = 0.12
            elif event.type == pygame.KEYUP and event.key in JUMP_KEYS:
                if game.velocity.y < -250:
                    game.velocity.y = -250
            elif event.type == pygame.WINDOWFOCUSLOST:
                game.jump_buffer = 0
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
