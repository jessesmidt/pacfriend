# pyright: reportMissingImports=false

try:
    from mazegenerator import MazeGenerator
except ModuleNotFoundError:
    print("\x1b[38;5;196m")
    print("Maze generator Wheel was not found. Make sure to include.")
    print("Otherwise, run \'make install\'")
    print("\x1b[38;5;0m")
    from os import _exit
    _exit(0)

import pygame
from src.settings import Settings, Constants
from src.buttons import TextButton
from src.score import Scoringsystem
from src.gums import PacGums
from src.ghost import GhostManager
from src.timers import Timers
from src.player import Pacman


class Engine(Constants):
    """
    The Engine is the main handler for everything from the menu on.
    It's responsible for the main game loop, keeping track of levels
    and managing the scoring, timers, ghosts and player input.

    Parameters:
    - settings = The settings retrieved from the settings class
    - swidth, sheight = the pixel-width/height of the complete maze
    - screen = Pygame's Screen class, which creates the
    game window
    - clock = Pygame's clock, to keep timings up to the required speed
    - maze_imagepath = Path to maze imagefile
    - button_font / Score font = font styles we reuse from the main menu
    - timers = Our timer class, to keep track of necessary timings
    - scoring = Our scoring class, to keep track of scores
    - seeds = list of map seeds, imported from our settings
    - pac = Player class that handles input, rendering
    - gameover = Boolean for handling gameovers (lives < 0)
    - to_menu = Boolean that is used for handling back to menu inputs
    - running = Boolean that keeps the game running, used for passing levels
    """
    def __init__(self, settings: Settings,
                 clock: pygame.time.Clock,
                 button_font: pygame.font.Font,
                 score_font: pygame.font.Font) -> None:
        self.settings = settings
        self.swidth = self.settings.width * Constants.T_SIZE
        self.sheight = self.settings.height * Constants.T_SIZE
        self.screen = pygame.display.set_mode(
            (self.swidth, self.sheight + self.SBAR_H))
        self.clock: pygame.time.Clock = clock
        self.maze_imagepath = "data/assets/pactiles.png"
        self.button_font: pygame.font.Font = button_font
        self.score_font: pygame.font.Font = score_font
        self.timers = Timers()
        self.scoring = Scoringsystem(
            self.settings.points_per_pacgum,
            self.settings.points_per_super_pacgum,
            self.settings.points_per_ghost
            )
        self.seeds: list[int] = self.settings.seeds
        self.pac = Pacman(self.timers, self.settings)
        self.gameover: bool = False
        self.to_menu: bool = False
        self.running: bool = True

    def level_handler(self) -> bool:
        """
        Generates a level for each of the seeds. When a level
        is completed, load up the next one until all 10 levels
        Are completed or the player is game over.
        """
        completed: int = 0
        while completed < 10 and self.running:
            self.maze = MazeGenerator(
                (self.settings.width, self.settings.height),
                False, [0, 0], [1, 1],
                self.seeds[completed]
            ).maze
            self.run(completed)
            if self.to_menu:
                break
            if self.gameover or completed == 9:
                self.to_menu = self._game_over_overlay()
            elif not self.gameover:
                completed += 1
                if not self.settings.skip_level:
                    self.scoring.level_complete(completed)
        return self.running

    def _pause(self, back_button: TextButton) -> None:
        """
        Seperate loop which pauses gameplay
        When paused is activated.
        """
        paused: bool = True
        paused_font: pygame.font.Font = pygame.font.Font(
            "data/font/Pixeltype.ttf", 100
        )
        paused_text: pygame.Surface = paused_font.render("PAUSED",
                                                         False, "RED")
        instruction_text: pygame.Surface = paused_font.render(
            "press B to go back to menu", False, "white")
        instruction_text = pygame.transform.scale(instruction_text, (300, 32))
        self.screen.blit(
            paused_text,
            (
                self.screen.get_width() // 2 - paused_text.get_width() // 2,
                self.screen.get_height() // 2
            )
        )
        self.screen.blit(
                    instruction_text,
                    (self.screen.get_width() // 2 -
                     instruction_text.get_width() // 2,
                        (self.screen.get_height() // 2) + 64)
                )
        pygame.display.flip()
        while self.running and paused:
            for event in pygame.event.get():
                match event.type:
                    case pygame.MOUSEBUTTONDOWN:
                        if back_button.is_clicked():
                            self.to_menu = True
                            paused = False
                    case pygame.QUIT:
                        self.running = False
                    case pygame.KEYDOWN:
                        match event.key:
                            case pygame.K_ESCAPE:
                                self.running = False
                            case pygame.K_p:
                                paused = False
                            case pygame.K_b:
                                self.to_menu = True
                                paused = False
            self.clock.tick(Constants.TICKSPEED)

    def start_countdown(self) -> bool:
        """
        Count down at the beginning of the game, projects a
        Countdown at the center of the screen.
        Returns True as long as the cooldown is still going.
        """
        if self.timers.countdown > 0:
            self.timers.countdown -= 1
            ctdown_surface = pygame.Surface((128, 128), pygame.SRCALPHA)
            ctdown_text = self.score_font.render(
                f"{int(self.timers.countdown // Constants.TICKSPEED) + 1}",
                False, "white")
            ctdown_surface.blit(ctdown_text, (0, 0))
            ctdown_surface = pygame.transform.scale(ctdown_surface, (256, 256))
            self.screen.blit(ctdown_surface, (
                (self.swidth // 2) - 0.3 * Constants.T_SIZE,
                ((self.sheight + self.settings.SBAR_H) // 2)
                - 0.5 * Constants.T_SIZE))
            return False
        return True

    def run(self, level: int) -> None:
        """
        The main gameplay handler. Uses pygame's clock to handle everything
        from rendering to timers, collisions with ghost, player input on the
        global TICKSPEED variable.

        Args:
        - level
            The current level
        """
        gums = PacGums(self.maze, self.screen, self.scoring, self.settings)
        gums.init_gums()
        self.pac.center_player()
        self.pac.set_maze(self.maze)
        map = self._render_map(level=level)
        self.timers.reset_timers(
            (max(len(gums.gums), 90)) * Constants.TICKSPEED)

        back_button: TextButton = TextButton(
            self.screen, "Back", self.button_font, "Black", "Grey75",
            25, int(self.settings.SBAR_H * 0.15), 1
        )

        ghostmanager: GhostManager = GhostManager(
            self.screen, self.maze, self.settings
        )

        skip_level: TextButton = TextButton(
            self.screen, "Skip", self.button_font, "Black", "Crimson",
            back_button.width + 50, int(self.settings.SBAR_H * 0.15), 0.9,
        )
        if not self.settings.skip_level:
            skip_level.enabled = False

        while (
            self.running and not self.to_menu
            and not self.gameover and gums.gums != []
              ):
            pygame.display.set_caption("Pac-Man | Game")
            gums.render_map_n_gums(map)

            if self.timers.animation_t >= 30:
                self.timers.animation_t = 0
            if self.timers.time_left < 0:
                self.gameover = True

            if self.timers.countdown == 0 and self.timers.respawn == 0:
                for ghost, modification, close in ghostmanager.ghosts:
                    ghost.ghost_times()
                    if ghost.respawn:
                        continue
                    if not (self.timers.time_left // Constants.TICKSPEED) % 10:
                        ghost.start_skattering()
                    if ghost.chase_pacman(
                            (self.pac.ppos_x, self.pac.ppos_y),
                            modification(self.pac.dir),
                            close):
                        if ghost.fleeing:
                            self.scoring.get_points("ghost")
                            ghost.respawn = Constants.TICKSPEED * 3
                        elif (not ghost.fleeing
                              and not self.settings.invincibility
                              and self.pac._lose_life_check_health()):
                            self.gameover = True
                            break
            else:
                for ghost, _, _ in ghostmanager.ghosts:
                    ghost.render()

            self.pac.render_pac(
                [ghost[0] for ghost in ghostmanager.ghosts],
                self.screen
            )
            if gums.visit_tile(self.pac.ppos_x, self.pac.ppos_y):
                for ghost, _, _ in ghostmanager.ghosts:
                    ghost.start_fleeing(10 * Constants.TICKSPEED)
            self.pac.input_handler(pygame.key.get_pressed())
            self.pac.move_tick()

            for event in pygame.event.get():
                match event.type:
                    case pygame.QUIT:
                        self.running = False
                    case pygame.KEYDOWN:
                        match event.key:
                            case pygame.K_p:
                                self._pause(back_button)
                            case pygame.K_b:
                                self.to_menu = True
                            case pygame.K_ESCAPE:
                                self.running = False
                    case pygame.MOUSEBUTTONDOWN:
                        if back_button.is_clicked():
                            self.to_menu = True
                        if self.settings.skip_level:
                            if skip_level.is_clicked():
                                gums.gums = []
            self._score_bar(self.pac.lives, level)
            back_button.draw_button()
            if self.settings.skip_level:
                skip_level.draw_button()
            self.start_countdown()

            pygame.display.flip()
            self.clock.tick(80)
        pygame.event.clear()

    def _render_map(
            self, background_color: str = "black", level: int = 1
            ) -> pygame.Surface:
        """
        Creates a window and maze, converts maze to visual output and adds a
        color overlay to the walls depending on the level

        Args:
        - background_color
            The color the background will project, default black
        - level
            The current level being played, default is one.
        """
        colors = [
            "blue", "red",
            "green", "yellow",
            "cyan", "magenta",
            "orange3", "gainsboro",
            "gold", "white"]
        rainbow = [
            "red", "orange",
            "yellow", "green",
            "blue", "indigo",
            "violet"]

        background = pygame.Surface((self.swidth, self.sheight))
        img = pygame.image.load(self.maze_imagepath).convert_alpha()
        tinted = img.copy()
        tinted_imgs = []

        if level != 9:
            tinted.fill(colors[level], special_flags=pygame.BLEND_RGB_MULT)
        else:
            for c in rainbow:
                variant = img.copy()
                variant.fill(c, special_flags=pygame.BLEND_RGB_MULT)
                tinted_imgs.append(variant)
        background.fill(background_color)

        for iy, y in enumerate(self.maze):
            for ix, x in enumerate(y):
                if level != 9:
                    xt = x * Constants.T_SIZE
                    background.blit(tinted, (ix * Constants.T_SIZE,
                                             iy * Constants.T_SIZE),
                                    area=(xt, 0, Constants.T_SIZE,
                                    Constants.T_SIZE))
                else:
                    xt = x * Constants.T_SIZE
                    background.blit(
                        tinted_imgs[(iy + ix) % 7],
                        (ix * Constants.T_SIZE,
                         iy * Constants.T_SIZE),
                        area=(xt, 0, Constants.T_SIZE,
                              Constants.T_SIZE))
        return background

    def _score_bar(self, lives: int, level: int) -> None:
        """
        Renders score, level, highscore, time left and lives
        in the score bar at the top of the screen.

        Args:
        - lives
            Amount of lives the player has left
        - level
            The current level being played
        """
        self.timers.time_left -= 1
        sbar = pygame.Surface((self.swidth, self.settings.SBAR_H))
        score_text = self.score_font.render(
            f"score: {str(self.scoring.score)}", False, "white")
        highscore_text = self.score_font.render(
            f"highscore: {str(self.scoring.highscore["score"])}",
            False, "white")
        level_text = self.score_font.render(
            f"{level + 1} / 10", False, "white")
        time_left_text = self.score_font.render(
            f"Time : {self.timers.time_left // Constants.TICKSPEED}",
            False, "white")
        sbar.blit(
            score_text, (self.swidth - (((len(str(self.scoring.score))
                         + 6) * 24) + 4), self.settings.SBAR_H - 32))
        sbar.blit(
            highscore_text, (self.swidth
                             - (((len(str(self.scoring.highscore["score"]))
                                  + 9) * 24) + 8), self.settings.SBAR_H - 72))
        self._render_health(lives, sbar)
        sbar.blit(level_text, (32, 96))
        sbar.blit(
            time_left_text, (((self.swidth // 2)
                             - len(str(self.timers.time_left // 60)) * 24),
                             self.settings.SBAR_H * 0.15))
        self.screen.blit(sbar, (0, 0))

    def _render_health(self, lives: int, sbar: pygame.Surface) -> None:
        """
        Print's x amount of pacmans up top at the score bar
        depending on amount of lives

        Args:
        - lives
            Amount of lives the player has left
        - sbar
            The pygame surface score bar to write on
        """
        healthbar = pygame.Surface((96, 32), pygame.SRCALPHA)
        health_img = pygame.image.load("data/assets/pacman_animation.png")
        for i in range(lives):
            healthbar.blit(health_img, ((i * 32), 0), area=(32, 64, 64, 96))
        sbar.blit(
            healthbar, ((self.swidth) / 2 - 48,
                        (self.settings.SBAR_H - 32)))

    @staticmethod
    def _is_alphanumericspace(char: str) -> bool:
        if char.lower() in " abcdefghijklmnopqrstuvwxyz1234567890":
            return True
        return False

    def _game_over_overlay(self) -> bool:
        """
        pauses the game, creates an overlay which lets you enter
        your name, when submitted, adds you to highscores and
        returns to menu.
        """
        timer = 0
        done: int = 0
        name: str = ""
        end_screen = pygame.Surface((640, 480))

        while not done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True
                if event.type == pygame.KEYDOWN:
                    if (event.key == pygame.K_RETURN
                       or event.key == pygame.K_KP_ENTER):
                        if '#' in name or '"' in name or "'" in name:
                            name = "StopTrying"
                        if not self.settings.is_cheating():
                            self.scoring.highscores.add_player(
                                name, self.scoring.score)
                        done = True
                    elif event.key == pygame.K_ESCAPE:
                        if not self.settings.is_cheating():
                            self.scoring.highscores.add_player(
                                name, self.scoring.score)
                        done = True
                    elif event.key == pygame.K_BACKSPACE:
                        name = name[:-1]
                    elif self._is_alphanumericspace(event.unicode):
                        if len(name) < 10:
                            name += event.unicode

            end_screen.fill((30, 30, 30))
            if timer < 30:
                name_surface = self.score_font.render(
                    f"{name}_", False, "white")
            else:
                name_surface = self.score_font.render(name, False, "white")
            timer += 1
            if timer > 60:
                timer = 0

            end_screen = self._win_loss_icons(end_screen)
            enter_name = self.score_font.render("enter name:", False, "white")
            press_enter = self.score_font.render(
                "press ENTER to submit score", False, "white")
            end_screen.blit(enter_name, (320 - (11 * 20 / 2), 82))
            end_screen.blit(name_surface, (320 - (len(name) * 20 / 2), 128))
            end_screen.blit(press_enter, (320 - (27 * 20 / 2), 320))

            self.screen.blit(end_screen, ((self.swidth // 2) - 320,
                                          (self.sheight // 2)
                                          - (240 - self.settings.SBAR_H)))
            pygame.display.flip()
            self.clock.tick(60)
        return True

    def _win_loss_icons(self, end_screen: pygame.Surface) -> pygame.Surface:
        """
        Projects different Icons and text over screen depending on win or loss

        Args:
        - end_screen
            The end sceen, which we will project the icons and text on
        """
        win_loss_icon = pygame.Surface((32, 32), pygame.SRCALPHA)
        if self.pac.lives > 0 and self.timers.time_left > 0:
            win_lost = "YOU WON!"
            win_img = pygame.image.load(self.settings.pacman_img)
            win_loss_icon.blit(win_img, (0, 0), (32, 64, 64, 96))
            end_screen.blit(win_loss_icon, (191, 32))
            win_loss_icon = pygame.transform.flip(win_loss_icon, True, False)
            end_screen.blit(win_loss_icon, (415, 32))
            end_text = self.score_font.render(win_lost, False, "yellow")
        else:
            win_lost = "GAME OVER"
            loss_img = pygame.image.load("data/assets/ghost.png")
            win_loss_icon.blit(loss_img, (0, 0), (0, 32, 64, 64))
            win_loss_icon = pygame.transform.scale(win_loss_icon, (60, 60))
            end_screen.blit(win_loss_icon, (171, 16))
            win_loss_icon = pygame.transform.flip(win_loss_icon, True, False)
            end_screen.blit(win_loss_icon, (425, 16))
            end_text = self.score_font.render(win_lost, False, "red")
        end_screen.blit(end_text, (320 - (len(win_lost) * 20 / 2), 32))
        return end_screen
