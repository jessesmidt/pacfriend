from typing import Tuple, List, Set, Callable
from settings import Constants, Settings
from math import floor
import pygame
import random


class GhostManager(Constants):
    def __init__(self, screen: pygame.Surface, maze: List[List[int]],
                 settings: Settings):
        sp: List[List[int]] = [
            [0, 0],
            [0, (settings.height - 1) * self.T_SIZE],
            [(settings.width - 1) * self.T_SIZE, 0],
            [(settings.width - 1) * self.T_SIZE,
             (settings.height - 1) * self.T_SIZE]
        ]
        random.shuffle(sp)
        self.red_ghost: Ghost = Ghost(
            screen, maze, settings,
            "Red", sp[0][0], sp[0][1]
        )
        self.pink_ghost: Ghost = Ghost(
            screen, maze, settings,
            "fuchsia", sp[1][0], sp[1][1]
        )
        self.blue_ghost: Ghost = Ghost(
            screen, maze, settings,
            "paleturquoise", sp[2][0], sp[2][1]
        )
        self.orange_ghost: Ghost = Ghost(
            screen, maze, settings,
            "yellow1", sp[3][0], sp[3][1]
        )
        self.no_change: Callable = lambda direction: direction
        self.no_prediction: Callable = lambda direction: 0
        self.ghosts: List[Tuple[Ghost, Callable, bool]] = [
            (self.red_ghost, self.no_prediction, True),
            (self.pink_ghost, self.no_change, True),
            (self.blue_ghost, self.opposite_direction, True),
            (self.orange_ghost, self.no_change, False)
        ]

    def opposite_direction(self, direction: int) -> int:
        """
        Returns the opposite cardinal direction of a given direction
        If not a valid innitial direction or opposite in valid cardinals
        it returns 0
        """
        if direction << 2 in self.VALID_DIRS:
            return direction << 2
        elif direction >> 2 in self.VALID_DIRS:
            return direction >> 2
        return 0


class Ghost(Constants):
    TD = 2
    SLOW_SPEED = 48

    def __init__(self, screen: pygame.Surface, maze: List[List[int]],
                 settings: Settings, color: str,
                 start_x_pos: int, start_y_pos: int
                 ):
        self.screen: pygame.Surface = screen
        self.maze: List[List[int]] = maze
        self.scores: List[List[int]] = [[]]
        self.x_pos: int = start_x_pos
        self.y_pos: int = start_y_pos
        self.home_x: int = start_x_pos
        self.home_y: int = start_y_pos
        self.movement_speed: int = 0
        self.direction: int = 0
        self.settings: Settings = settings
        self.color: str = color
        self.fleeing: bool = settings.always_flee
        self.flee_duration: int = 0
        self.respawn: int = 0
        self.skatter: int = 0
        self.hitbox_scale: float = 0.5
        self.ghost_img: pygame.Surface = pygame.image.load(
            self.GHOST_IMG_PATH).convert_alpha()
        self._calculated_board(
            0, 0
        )

    def start_skattering(self) -> None:
        """
        Sets the amount of time gost are going to skatter which means to target
        their home coordinates instead of pacman
        """
        self.skatter = self.TICKSPEED

    def start_fleeing(self, duration: int) -> None:
        """
        Sets the time which the ghost should flee
        """
        if self.settings.always_flee:
            return
        self.flee_duration += duration
        self.fleeing = True

    def ghost_times(self) -> None:
        """
        Conts all the timers and sets events such as fleeing status when they
        reach 0
        """
        if self.respawn > 0:
            self.respawn -= 1
        if self.flee_duration > 0:
            self.flee_duration -= 1
        else:
            self.fleeing = self.settings.always_flee
        if self.skatter > 0:
            self.skatter -= 1

    def reset_ghost(self) -> None:
        """
        Resets the ghost to its initial starting position
        """
        self.x_pos = self.home_x
        self.y_pos = self.home_y
        self.direction = 0

    def chase_pacman(self, pacman_coordinates: Tuple[int, int],
                     pacman_direction: int, close: bool) -> bool:
        """
        A program that calculates the pathfinding, renders the ghost and checks
        if they overlap

        target_x: int : Current x coordinate of goal on pixel scale
        target_y: int : Current y coordinate of goal on pixel scale
        """
        target_x, target_y = pacman_coordinates
        x_tile: int = (self.x_pos // self.T_SIZE)
        y_tile: int = (self.y_pos // self.T_SIZE)
        # Many ghost target a tile in proportion to the direction of movement
        # this there is a direction and that if they already reacehd the target
        # that they will target pacman
        if not self.fleeing and self.skatter == 0:
            pac_x_tile: int = floor(target_x / self.T_SIZE)
            pac_y_tile: int = floor(target_y / self.T_SIZE)
            if (not close or abs(x_tile - pac_x_tile)
               + abs(y_tile - pac_y_tile) >= self.TD):
                target_x, target_y = self._set_target(
                    pacman_direction,
                    pac_x_tile,
                    pac_y_tile
                )
        if self.skatter > 0:
            target_x = self.home_x // self.T_SIZE
            target_y = self.home_y // self.T_SIZE
        # Moves only when the player is on the top left of a tile
        # this makes it that the character obeys walls and inputs with
        # and prevents clipping
        if self.direction == 0 or (self.x_pos % self.T_SIZE == 0
                                   and self.y_pos % self.T_SIZE == 0):
            # Calculates only when there is no scores or pacman has moved
            # print(f"Second: {pacman_coordinates}")
            self._calculated_board(
                (target_x // self.T_SIZE),
                (target_y // self.T_SIZE)
            )
            # Adds a more random element to the direction
            # ghost flee away from pacman
            # Impossible calculation as surface area of the maze plus one
            cost: int = self.settings.width * self.settings.height + 1
            # When fleeing target larger distance rather than smaller
            if self.fleeing:
                random.shuffle(self.VALID_DIRS)
                cost = -1
            for dir in self.VALID_DIRS:
                if self.maze[y_tile][x_tile] & dir:
                    continue
                xd, yd = self.CARDINALS[dir]
                xd += x_tile
                yd += y_tile
                if not self._in_bounds(xd, yd):
                    continue
                if self.fleeing and self.scores[yd][xd] > cost:
                    cost = self.scores[yd][xd]
                    self.direction = dir
                elif self.scores[yd][xd] < cost:
                    cost = self.scores[yd][xd]
                    self.direction = dir
        self._move_ghost()
        self.render()
        collision_status: bool = self._collides(
            pacman_coordinates[0],
            pacman_coordinates[1]
        )
        if self.fleeing and collision_status:
            self.reset_ghost()
        return collision_status

    def render(self) -> None:
        """
        Renders he ghost in the map and already adjusts for te size of the
        score bar
        """
        poslist: List[Tuple[int, int, int, int]] = [
            (0, 0, 32, 32),  # Left / Right
            (32, 0, 64, 32),  # Down
            (0, 32, 64, 64),  # Up
            (32, 32, 64, 64),  # Flee Left / Right
            (0, 64, 32, 96),  # Flee Down
            (32, 64, 64, 96)  # Flee up
        ]
        position: int = 0
        flipped: bool = False
        match self.CARDINALS[self.direction]:
            case (-1, 0):  # Left
                position = 0
            case (1, 0):  # Right
                position = 0
                flipped = True
            case (0, 1):  # Down
                position = 1
            case (0, -1):  # Up
                position = 2
            case _:
                position = 2
        if self.fleeing:
            position += 3
        ghost: pygame.Surface = pygame.Surface((32, 32), pygame.SRCALPHA)
        ghost.blit(self.ghost_img, (0, 0), poslist[position])
        ghost = pygame.transform.flip(ghost, flipped, False)
        ghost = pygame.transform.scale(ghost, (60, 60))
        ghost = pygame.transform.grayscale(ghost)
        if self.fleeing:
            colour: str = "Cyan"
            if (0 < self.flee_duration <= self.TICKSPEED * 1.5
               and self.flee_duration % 2):
                colour = "Ivory"
            ghost.fill(colour, special_flags=pygame.BLEND_RGB_MULT)
        else:
            ghost.fill(self.color, special_flags=pygame.BLEND_RGB_MULT)
        self.screen.blit(ghost, (self.x_pos, self.y_pos + self.SBAR_H))

    def _in_bounds(self, x_tile: int, y_tile: int) -> bool:
        """
        Validates if a coordinate is in the boundaries of the 2D List map
        """
        if not (0 <= x_tile < self.settings.width):
            return False
        if not (0 <= y_tile < self.settings.height):
            return False
        return True

    def _is_in_map(self, x_change: int, y_change: int) -> bool:
        """
        Checks that the change will still be in bounds of the pixels of the map

        x_change: int = change in x coordinate on pixel scale
        y_change: int = change in y coordinate on pixel scale
        """
        if self.x_pos + x_change < 0:
            return False
        if self.x_pos + x_change > self.settings.width * self.T_SIZE:
            return False
        if self.y_pos + y_change < 0:
            return False
        if self.y_pos + y_change > self.settings.height * self.T_SIZE:
            return False
        return True

    def _calculated_board(self, target_x: int, target_y: int) -> None:
        """
        Calculates using A* the shortest path to pacman. if fleeing all cells
        are calculate so that the ghost can flee in any direction

        Modified slightly so if the difference between to adjacent cells is
        larger than one, its value will be recalculated
        """
        neighbours: List[Tuple[int, int]] = [(target_x, target_y)]
        visited: Set[Tuple[int, int]] = {(target_x, target_y)}
        maxi: int = (self.settings.width * self.settings.height) + 1
        self.scores = [[maxi for _ in range(self.settings.width)]
                       for _ in range(self.settings.height)]
        x_tile_goal: int = self.x_pos // self.T_SIZE
        y_tile_goal: int = self.y_pos // self.T_SIZE
        self.scores[target_y][target_x] = 0
        while neighbours:
            if not self.fleeing:
                neighbours.sort(key=lambda coords: abs(coords[0] - x_tile_goal)
                                + abs(coords[1] - y_tile_goal))
            x, y = neighbours.pop(0)
            if not self.fleeing and (x == x_tile_goal and y == y_tile_goal):
                break
            for dir in self.VALID_DIRS:
                if self.maze[y][x] & dir:
                    continue
                xd, yd = self.CARDINALS[dir]
                xd += x
                yd += y
                if (xd, yd) in visited:
                    continue
                if not self._in_bounds(xd, yd):
                    continue
                visited.add((xd, yd))
                neighbours.append((xd, yd))
                self.scores[yd][xd] = self.scores[y][x] + 1

    def _move_ghost(self) -> None:
        """
        moves the ghost by the movement speed
        movement_speed: The amount of pixels that the ghost moves per tick
        moement_speed = tile size / input tick

        Preverably the tile size and input tick must be perfectly divisible as
        other ticks can cause issues
        """
        if self.x_pos % self.T_SIZE == 0 and self.y_pos % self.T_SIZE == 0:
            if self.settings.slow_ghosts or self.fleeing:
                self.movement_speed = floor(self.T_SIZE / self.SLOW_SPEED)
            else:
                self.movement_speed = floor(self.T_SIZE / self.INPUT_TICK)
            if (self.maze[self.y_pos // self.T_SIZE]
               [self.x_pos // self.T_SIZE] & self.direction):
                self.direction = 0
        x_change, y_change = self.CARDINALS[self.direction]
        x_change *= self.movement_speed
        y_change *= self.movement_speed
        if self._is_in_map(x_change, y_change):
            self.x_pos += x_change
            self.y_pos += y_change

    def _collides(self, target_x: int, target_y: int) -> bool:
        """
        Checks if the centre of the ghost falls in the borders of pacman after
        the borders have been adjiusted through player_grace and hitbox size.
        The smaller the hitbox modifier the larger the hitbox
        """
        # Grace given to players so that their hitbox is smaller
        player_grace: int = int((self.T_SIZE * self.hitbox_scale) // 2)
        overlap_x: bool = False
        overlap_y: bool = False
        ghost_centre_x: int = self.x_pos + floor(self.T_SIZE / 2)
        ghost_centre_y: int = self.y_pos + floor(self.T_SIZE / 2)
        if (target_x + player_grace <= ghost_centre_x <=
           target_x + self.T_SIZE - player_grace):
            overlap_x = True
        if (target_y + player_grace <= ghost_centre_y <=
           target_y + self.T_SIZE - player_grace):
            overlap_y = True
        return overlap_x and overlap_y

    def _set_target(self, search_direction: int, target_x: int,
                    target_y: int, nbr_tiles: int = TD) -> Tuple[int, int]:
        """
        Sets a target in the specified direction a set amount of tiles distance
        """
        explore_directions: List[int] = [num for num in self.VALID_DIRS
                                         if num != search_direction]
        if search_direction:
            explore_directions = [search_direction] + explore_directions
        while nbr_tiles:
            invalid: int = 0
            for direction in explore_directions:
                if not nbr_tiles:
                    break
                if (direction << 2 == search_direction
                   or direction >> 2 == search_direction):
                    invalid += 1
                    continue
                if self.maze[target_y][target_x] & direction:
                    invalid += 1
                    continue
                target_x += self.CARDINALS[direction][0]
                target_y += self.CARDINALS[direction][1]
                search_direction = direction
                nbr_tiles -= 1
            # Invalid will at max be 4 if 3 walls are blocked and it can't go
            # back
            if invalid == 4:
                break
        return (target_x * self.T_SIZE, target_y * self.T_SIZE)
