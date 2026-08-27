# pyright: reportMissingImports=false

from score import Scoringsystem
from settings import Settings
import pygame


class PacGums():
    def __init__(self, maze: list[list[int]], screen: pygame.Surface,
                 scoring: Scoringsystem, settings: Settings) -> None:
        self.maze: list[list[int]] = maze
        self.gums: list[dict[tuple, int]] = []
        self.screen = screen
        self.x: int = len(self.maze[0])
        self.y: int = len(self.maze)
        gum_img = pygame.image.load(
            "data/assets/pacgum.png").convert_alpha()
        sgum_img = pygame.image.load(
            "data/assets/s_pacgum.png").convert_alpha()
        self.gum_img = pygame.transform.scale(gum_img, (3, 3))
        self.sgum_img = pygame.transform.scale(sgum_img, (16, 16))
        self.scores: Scoringsystem = scoring
        self.settings: Settings = settings
        self.temp_value: int = 0
        self.tsize = self.settings.T_SIZE

    def init_gums(self) -> None:
        """
        Initializes gums on the map, excludes the area where '42' resides.
        """
        neighbours = [(int(self.x / 2 - 0.5) + dx, int(self.y / 2 - 0.5) + dy)
                      for dx in (-3, -2, -1, 0, 1, 2, 3)
                      for dy in (-2, -1, 0, 1, 2)]

        s_gums_location = [
            (0, 0), (0, self.y - 1), (self.x - 1, 0), (self.x - 1, self.y - 1)]
        for iy, row in enumerate(self.maze):
            for ix, _ in enumerate(row):
                if (ix, iy) in neighbours:
                    pass
                elif (ix, iy) in s_gums_location:
                    self.gums.append({(ix, iy): 2})
                else:
                    self.gums.append({(ix, iy): 1})

    def render_map_n_gums(self, map: pygame.Surface) -> None:
        """
        Gets the map surface and adds the gums over top.

        Args:
        - map
            The pre-rendered Pygame surface.
        """
        gums_overlay = pygame.Surface(
            (self.x * self.tsize, self.y * self.tsize), pygame.SRCALPHA)
        for gum in self.gums:
            for x, y in gum:
                if gum.get((x, y)) == 1:
                    gums_overlay.blit(
                        self.gum_img, ((x + 0.5) * self.tsize - 1.5,
                                       (y + 0.5) * self.tsize))
                elif gum.get((x, y)) == 2:
                    gums_overlay.blit(
                        self.sgum_img, ((x + 0.5) * self.tsize - 8,
                                        (y + 0.5) * self.tsize - 6))
        self.screen.blit(map, (0, 0 + self.settings.SBAR_H))
        self.screen.blit(gums_overlay, (0, 0 + self.settings.SBAR_H))

    def visit_tile(self, x: int, y: int) -> bool:
        """
        Gets called every tick, checks if there's any gums alive around
        the center of the tile, and 'eats' it if there is something.
        Returns True if super gum is eaten, to activate ghost flee.

        Args:
        - X, Y
            Integers of the pixel position of the player.
        """
        if ((x % self.tsize >= 0 and x % self.tsize <= 18) and
                (y % self.tsize >= 0 and y % self.tsize <= 18)) or (
                (x % self.tsize == 0 and x % self.tsize >= 45) and
                (y % self.tsize == 0 and y % self.tsize >= 45)):

            if {(x // self.tsize, y // self.tsize): 1} in self.gums:
                self.gums.remove({(x // self.tsize, y // self.tsize): 1})
                self.scores.get_points("gum")
            elif {(x // self.tsize,
                   y // self.tsize): 2} in self.gums:
                self.gums.remove({
                    (x // self.tsize, y // self.tsize): 2})
                self.scores.get_points("sgum")
                return True
        return False
