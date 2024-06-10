#!/usr/bin/env python3
"""
        CopyLeft 2021 Michael Rouves

        This file is part of Pygame-DoodleJump.
        Pygame-DoodleJump is free software: you can redistribute it and/or modify
        it under the terms of the GNU Affero General Public License as published by
        the Free Software Foundation, either version 3 of the License, or
        (at your option) any later version.

        Pygame-DoodleJump is distributed in the hope that it will be useful,
        but WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
        GNU Affero General Public License for more details.

        You should have received a copy of the GNU Affero General Public License
        along with Pygame-DoodleJump. If not, see <https://www.gnu.org/licenses/>.
"""

import asyncio

import pygame

import settings as config
from camera import Camera
from level import Level
from player import Player
from singleton import Singleton


class Game(Singleton):
    """
    A class to represent the game.

    used to manage game updates, draw calls and user input events.
    Can be access via Singleton: Game.instance .
    (Check Singleton design pattern for more info)
    """

    # constructor called on new instance: Game()
    def __init__(self) -> None:

        # ============= Initialisation =============
        self.__alive = True
        self.won = False
        self.sound_on = True
        self.game_over_sound_played = False
        # Window / Render
        self.window = pygame.display.set_mode(config.DISPLAY, config.FLAGS)
        self.clock = pygame.time.Clock()

        # Instances
        self.camera = Camera()
        self.lvl = Level()
        self.player = Player(
            self,  # Passa l'istanza del gioco
            config.HALF_XWIN - config.PLAYER_SIZE[0] / 2,  # X POS
            config.HALF_YWIN + config.HALF_YWIN / 2,  # Y POS
            *config.PLAYER_SIZE,  # SIZE
            config.PLAYER_COLOR  # COLOR
        )

        # Load sounds
        self.jump_sound = pygame.mixer.Sound('sounds/jump.ogg')
        self.hit_sound = pygame.mixer.Sound('sounds/hit.ogg')
        self.game_over_sound = pygame.mixer.Sound('sounds/game_over.ogg')
        self.win_sound = pygame.mixer.Sound('sounds/win.ogg')
        self.background_music = 'sounds/background_music.ogg'

        # Load images
        self.background_image = pygame.image.load('images/BACKGROUND_GAME.png').convert()
        self.sound_on_image = pygame.image.load('images/sound_on.png').convert_alpha()
        self.sound_off_image = pygame.image.load('images/sound_off.png').convert_alpha()

        self.sound_icon_rect = self.sound_on_image.get_rect(topright=(config.XWIN - 10, 10))

        # User Interface
        self.score = 0
        self.score_txt = config.SMALL_FONT.render("0 $ market cap", 1, config.GRAY)
        self.score_pos = pygame.math.Vector2(10, 10)

        self.gameover_txt = config.LARGE_FONT.render("Game Over", 1, config.GRAY)
        self.gameover_rect = self.gameover_txt.get_rect(center=(config.HALF_XWIN, config.HALF_YWIN))

        self.win_txt = config.LARGE_FONT.render("1 DOG = 1 $", 1, config.GRAY)
        self.win_rect = self.win_txt.get_rect(center=(config.HALF_XWIN, config.HALF_YWIN))

        # Red squares
        self.squares = [
            {
                'rect': pygame.Rect(config.HALF_XWIN - 25, -100, 50, 50),
                'speed': 5,
                'score': 2_300_000_000,
                'spawned': False,
                'image': pygame.image.load('images/BONK.png')
            },
            {
                'rect': pygame.Rect(config.HALF_XWIN - 25, -100, 50, 50),
                'speed': 5,
                'score': 3_000_000_000,
                'spawned': False,
                'image': pygame.image.load('images/FLOKI.png')
            },
            {
                'rect': pygame.Rect(config.HALF_XWIN - 25, -100, 50, 50),
                'speed': 5,
                'score': 3_400_000_000,
                'spawned': False,
                'image': pygame.image.load('images/WIF.png')
            },
            {
                'rect': pygame.Rect(config.HALF_XWIN - 25, -100, 50, 50),
                'speed': 5,
                'score': 6_200_000_000,
                'spawned': False,
                'image': pygame.image.load('images/PEPE.png')
            },
            {
                'rect': pygame.Rect(config.HALF_XWIN - 25, -100, 50, 50),
                'speed': 5,
                'score': 15_000_000_000,
                'spawned': False,
                'image': pygame.image.load('images/SHIB.png')
            },
            {
                'rect': pygame.Rect(config.HALF_XWIN - 25, -100, 50, 50),
                'speed': 5,
                'score': 23_000_000_000,
                'spawned': False,
                'image': pygame.image.load('images/DOGE.png')
            },
            {
                'rect': pygame.Rect(config.HALF_XWIN - 25, -100, 50, 50),
                'speed': 5,
                'score': 99_000_000_000,
                'spawned': False,
                'image': pygame.image.load('images/MOON.png')
            }
        ]

        # Play music in loop
        pygame.mixer.music.load(self.background_music)
        pygame.mixer.music.play(-1)

    def close(self):
        self.__alive = False

    def reset(self):
        self.camera.reset()
        self.lvl.reset()
        self.player.reset()
        self.score = 0
        self.won = False
        self.game_over_sound_played = False
        self.game_over_sound.stop()
        for square in self.squares:
            square['spawned'] = False

    def toggle_sound(self):
        self.sound_on = not self.sound_on
        if self.sound_on:
            pygame.mixer.unpause()
            pygame.mixer.music.unpause()
        else:
            pygame.mixer.pause()
            pygame.mixer.music.pause()

    def draw_horizontal_line(self, y, text):
        pygame.draw.line(self.window, config.WHITE, (0, y), (config.XWIN, y), 2)
        text_surface = config.SMALL_FONT.render(text, True, config.WHITE)
        text_rect = text_surface.get_rect(center=(config.HALF_XWIN, y - 10))
        self.window.blit(text_surface, text_rect)

    def _event_loop(self):
        # ---------- User Events ----------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.close()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.close()
                if event.key == pygame.K_RETURN and (self.player.dead or self.won):
                    self.reset()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.sound_icon_rect.collidepoint(event.pos):
                    self.toggle_sound()
            self.player.handle_event(event)

    async def _update_loop(self):
        # ----------- Update -----------
        self.player.update(self)
        await self.lvl.update()

        if not self.player.dead and not self.won:
            self.camera.update(self.player.rect)
            # calculate score and update UI txt
            self.score = -self.camera.state.y * 500_000  # Increases the speed of score accumulation
            self.score_txt = config.SMALL_FONT.render(
                f"{self.score:,.0f} $ market cap", 1, config.GRAY)

            for square in self.squares:
                if self.score >= square['score'] and not square['spawned']:
                    square['spawned'] = True
                    square['rect'].y = self.camera.state.y - 100

                if square['spawned']:
                    square['rect'].x += square['speed']
                    # Checks whether the square has reached the edges of the window
                    if square['rect'].right >= config.XWIN or square['rect'].left <= 0:
                        square['speed'] = -square['speed']

            if self.score >= 100_000_000_001:
                self.won = True
                if self.sound_on:
                    self.win_sound.play()

    def _render_loop(self):
        # ----------- Display -----------
        self.window.blit(self.background_image, (0, 0))
        self.lvl.draw(self.window)
        self.player.draw(self.window)

        # Draw the squares if spawned and the lines
        for square in self.squares:
            if square['spawned']:
                self.draw_horizontal_line(
                    self.camera.apply_rect(square['rect']).centery,
                    f"${square['score']:,}"
                )
                self.window.blit(square['image'], self.camera.apply_rect(square['rect']))

        # Draw the sound icon
        if self.sound_on:
            self.window.blit(self.sound_on_image, self.sound_icon_rect)
        else:
            self.window.blit(self.sound_off_image, self.sound_icon_rect)

        # User Interface
        if self.player.dead:
            self.window.blit(self.gameover_txt, self.gameover_rect)  # gameover txt
            if self.sound_on and not self.game_over_sound_played:
                self.game_over_sound.play()
                self.game_over_sound_played = True
        elif self.won:
            self.window.blit(self.win_txt, self.win_rect)  # win txt
        else:
            self.window.blit(self.score_txt, self.score_pos)  # score txt

        pygame.display.update()  # window update
        self.clock.tick(config.FPS)  # max loop/s

    async def run(self):
        # ============= MAIN GAME LOOP =============
        while self.__alive:
            self._event_loop()
            await self._update_loop()
            self._render_loop()
            await asyncio.sleep(0)
        pygame.quit()


async def main():
    game = Game()
    await game.run()


if __name__ == "__main__":
    # ============= PROGRAM STARTS HERE =============
    pygame.mixer.init()
    pygame.init()
    asyncio.run(main())
