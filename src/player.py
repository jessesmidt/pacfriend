import pygame as py
from typing import Tuple, Any
from src.timers import Timers
from src.settings import Constants, Settings
from src.ghost import Ghost


class Pacman():
    """
    This class handles player input, Pacman's movement logic and speeds
    graphic rendering and respawn mechanics

    Parameters:
    - timers = Keeps track of movement timings, pre-game cooldown etc.
    - settings = Necessary for keeping track of cheats
    - dir = the players' actual direction
    - input_dir = the players desired direction
    - maze = the hexadecimal values for checking collisons
    - lives = imports the amount of lives from settings
    - ppos_x, ppos_y = the players position (tile based)
    - x, y = the players position (pixel based)
    """
    def __init__(self, timers: Timers, settings: Settings) -> None:
        self.timers = timers
        self.settings = settings
        self.dir = 1
        self.input_dir = 1
        self.maze: list[list[int]] = []
        self.lives: int = self.settings.lives
        self.ppos_x = 0
        self.ppos_y = 0
        self.x = 0
        self.y = 0

    def set_maze(self, maze: list[list[int]]) -> None:
        """
        Helper function to set maze every level
        """
        self.maze = maze

    def move_tick(self) -> None:
        """
        moves the player for one tick in the given directional if possible
        """
        if self.timers.protection > 0:
            self.timers.protection -= 1
        self.x = self.ppos_x * self.settings.T_SIZE
        self.y = self.ppos_y * self.settings.T_SIZE
        if self.dir != self.input_dir:
            if self._new_heading():
                self.dir = self.input_dir

        self._move_player()

    def _move_player(self) -> None:
        """
        Handles actual moving in self.dir until no
        longer possible if the conditions apply
        """
        if self.settings.fast_pacman:
            multiplier = 2
        else:
            multiplier = 1
        if (self._movement_possible() and not self.timers.countdown
                and not self.timers.respawn):
            if self.dir == 1:
                self.ppos_y -= 2 * multiplier
            elif self.dir == 2:
                self.ppos_x += 2 * multiplier
            elif self.dir == 4:
                self.ppos_y += 2 * multiplier
            elif self.dir == 8:
                self.ppos_x -= 2 * multiplier

    def render_pac(self, ghosts: list[Ghost], screen: py.Surface) -> None:
        """
        Renders Pacman on the screen at it's position.
        Cycles through our pacman images to animate 'eating'

        Args:
        - Ghosts
            List of our Ghosts objects to handle animation
            at collision
        - Screen
            Pointer to the screen we're rendering on
        """
        if self.timers.respawn > 0:
            self._render_pac_death(ghosts, screen)
            return
        poslist = [
            (0, 0, 32, 32), (32, 0, 64, 32),
            (0, 32, 32, 64), (32, 32, 64, 64),
            (0, 64, 32, 96), (32, 64, 64, 96),
            (0, 64, 32, 96), (32, 32, 64, 64),
            (0, 32, 32, 64), (32, 0, 64, 32)
            ]
        player = py.Surface((32, 32), py.SRCALPHA)
        pac_img = py.image.load(
            "data/assets/pacman_animation.png").convert_alpha()
        if (self._movement_possible() and not
                self.timers.countdown and not self.timers.respawn):
            player.blit(
                pac_img, (0, 0),
                area=poslist[int((self.timers.animation_t) // 3)]
                )
        else:
            player.blit(pac_img, (0, 0), area=(0, 0, 32, 32))

        self.timers.animation_t += 1
        if self.dir == 1:
            player = py.transform.rotate(player, 90)
        elif self.dir == 4:
            player = py.transform.rotate(player, 270)
        elif self.dir == 8:
            player = py.transform.flip(player, True, False)

        player = py.transform.scale(player, (40, 40))
        screen.blit(player, (self.ppos_x + (
            0.20 * self.settings.T_SIZE),
            self.ppos_y + self.settings.SBAR_H + (
                0.20 * self.settings.T_SIZE)))

    def _render_pac_death(
            self, ghosts: list[Ghost], screen: py.Surface
            ) -> None:
        """
        Renders the Pacman death animation when the respawn timer
        is up.

        Args:
        - Ghosts
            List of our Ghosts objects to handle animation
            at collision
        - Screen
            Pointer to the surface we're rendering on
        """
        poslist = [
                (0, 0, 32, 32), (32, 0, 64, 32),
                (64, 0, 96, 32), (96, 0, 128, 32),
                (0, 32, 32, 64), (32, 32, 64, 64),
                (64, 32, 96, 64), (96, 32, 128, 64),
                (0, 64, 32, 96), (32, 64, 64, 96),
                (64, 64, 96, 96), (96, 64, 128, 96),
                (0, 96, 32, 128), (32, 96, 64, 128),
                (64, 96, 96, 128), (96, 96, 128, 128)
            ]
        if self.timers.respawn == 1:
            self.center_player()
            for ghost in ghosts:
                ghost.reset_ghost()
        self.timers.respawn -= 1
        self.timers.animation_t = 0
        dying = py.Surface((32, 32), py.SRCALPHA)
        dying_animation = py.image.load(
                        "data/assets/pacdeath.png").convert_alpha()
        dying.blit(
            dying_animation, (0, 0),
            area=poslist[int((120 - self.timers.respawn) // 8)])
        screen.blit(dying, (self.ppos_x + (0.20 * self.settings.T_SIZE),
                    self.ppos_y + self.settings.SBAR_H + (
                    0.20 * self.settings.T_SIZE)))

    def input_handler(self, keys: Any) -> None:
        """
        Handles Pygame's key input and sets our input_dir.

        Args:
        - keys
            pygame's ScancodeWrapper
        """
        if keys[py.K_w]:
            self.input_dir = 1
        elif keys[py.K_d]:
            self.input_dir = 2
        elif keys[py.K_s]:
            self.input_dir = 4
        elif keys[py.K_a]:
            self.input_dir = 8
        elif keys[py.K_UP]:
            self.input_dir = 1
        elif keys[py.K_RIGHT]:
            self.input_dir = 2
        elif keys[py.K_DOWN]:
            self.input_dir = 4
        elif keys[py.K_LEFT]:
            self.input_dir = 8

    def _movement_possible(self) -> bool:
        """
        Checks that the direction of movement is valid and not a wall
        """
        if self.timers.countdown > 0 or self.timers.respawn > 0:
            return False
        tx = int(self.ppos_x // self.settings.T_SIZE)
        ty = int(self.ppos_y // self.settings.T_SIZE)
        if (self.ppos_x % self.settings.T_SIZE == 0 and
                self.ppos_y % self.settings.T_SIZE == 0):
            if (self.dir in self.settings.VALID_DIRS and
                    self.maze[ty][tx] & self.dir):
                return False
        return True

    def _new_heading(self) -> bool:
        """
        Checks that the direction of movement is valid and not a wall
        """
        if self.dir == 1 and self.input_dir == 4:
            return True
        elif self.dir == 4 and self.input_dir == 1:
            return True
        elif self.dir == 2 and self.input_dir == 8:
            return True
        elif self.dir == 8 and self.input_dir == 2:
            return True

        if (self.ppos_x % self.settings.T_SIZE == 0 and
                self.ppos_y % self.settings.T_SIZE == 0):
            tx = int(self.ppos_x // self.settings.T_SIZE)
            ty = int(self.ppos_y // self.settings.T_SIZE)
            if (self.maze[ty][tx] & self.input_dir):
                return False
            return True
        return False

    def center_player(self) -> None:
        """
        Helper function for centering player pos at start of game
        """
        player_pos: Tuple[float, float] = (
            int((self.settings.width - 1) / 2), self.settings.height // 2)
        a, b = player_pos
        self.ppos_x, self.ppos_y = int(a), int(b)
        self.ppos_y *= self.settings.T_SIZE
        self.ppos_x *= self.settings.T_SIZE

    def _lose_life_check_health(self) -> bool:
        """
        Lose a life and checks if there are any lifes left, if 0, return False
        to end game. Sets protection and respawn timer to initiate respawn.
        """
        if not self.timers.protection:
            self.lives -= 1
            self.timers.respawn = 2 * Constants.TICKSPEED
            self.timers.protection = 3 * Constants.TICKSPEED
            if self.lives <= 0:
                return True
        return False
