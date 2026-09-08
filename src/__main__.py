from typing import Dict, List
from src.settings import Settings, Constants
from src.buttons import TextButton, ImageButton, ToggleButton
from src.engine import Engine
from src.highscores import Highscore
import pygame
from src import errors as PME
import sys
import os


def pacman_main() -> None:
    """
    The main body from which pacman is launched.
    A lot of our fonts and buttons are imported here.
    The visual of the main menu is made here.
    """
    if len(sys.argv) > 2:
        print("Please provide only one valid JSON configuration file")
        return
    settings: Settings = Settings()
    try:
        if len(sys.argv) == 1:
            settings = settings.extract_settings(None)
        else:
            settings = settings.extract_settings(sys.argv[1])
    except PME.InvalidJson as e:
        print(f"JSON ERROR: {e}")
        return
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    pygame.init()
    clock: pygame.time.Clock = pygame.time.Clock()
    pygame.display.set_caption("Pac-Man | Main Menu")
    main_menu = pygame.display.set_mode((1500, 1000))
    my_font_caption: pygame.font.Font = pygame.font.Font(
        "data/font/Pixeltype.ttf", 150
    )
    my_font: pygame.font.Font = pygame.font.Font(
        "data/font/Pixeltype.ttf", 100
    )
    score_font: pygame.font.Font = pygame.font.Font(
        "data/font/Pixeltype.ttf", 64
    )
    settings_button: TextButton = TextButton(
        main_menu, "Settings", my_font, "Grey20", "Grey75", 175, 475, 1
    )
    highscore_button: TextButton = TextButton(
        main_menu, "Highscores", my_font, "Grey20", "Grey75", 1050, 475, 1
    )
    play_button_image = pygame.image.load("data/assets/pacman_play.png")
    play_button: ImageButton = ImageButton(
        main_menu, play_button_image, 494, 246, 1
    )
    title: pygame.Surface = my_font_caption.render(
        "Pac-Man", False, "Yellow"
    )
    underline: pygame.Surface = my_font_caption.render(
        "---------", False, "Gold"
    )
    instructions = pygame.transform.scale(
        pygame.image.load("data/assets/instructions.png"), (720, 360))
    running: bool = True
    animation: int = 0
    up_down: bool = True
    while running:
        main_menu.fill("Black")
        main_menu.blit(title, (555, 50))
        main_menu.blit(underline, (500, 100))
        main_menu.blit(instructions, (0, 670), area=(0, 0, 360, 360))
        main_menu.blit(instructions, (1120, 670), area=(360, 0, 720, 360))
        settings_button.draw_button()
        highscore_button.draw_button()

        if animation >= 50:
            up_down = False
        elif animation <= 0:
            up_down = True
        if up_down:
            animation += 1
        else:
            animation -= 1

        main_menu.fill("Black", play_button.rect)
        play_button.draw_button(0, int(animation / 5))

        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    running = False
                case pygame.KEYDOWN:
                    match event.key:
                        case pygame.K_ESCAPE:
                            running = False
                        case _:
                            pass
                case pygame.MOUSEBUTTONDOWN:
                    if play_button.is_clicked():
                        if settings.random_seeds:
                            import random
                            settings.seeds = [random.randint(1, 1000)
                                              for _ in range(10)]
                        else:
                            settings.seeds = Constants.DEFAULT_SEEDS
                        engine: Engine = Engine(
                            settings, clock, my_font, score_font
                        )
                        running = engine.level_handler()
                        if running:
                            main_menu = pygame.display.set_mode((1500, 1000))
                    elif settings_button.is_clicked():
                        running = display_settings(
                            main_menu, clock, settings
                        )
                    elif highscore_button.is_clicked():
                        running = display_highscores(
                            main_menu, clock, settings
                        )
                    if not running:
                        continue
                    pygame.display.set_caption("Pac-Man | Main Menu")
                    title = my_font_caption.render(
                        "Pac-Man", False, "Yellow"
                    )
                    underline = my_font_caption.render(
                        "---------", False, "Gold"
                    )
        clock.tick(60)
        pygame.display.flip()
    pygame.quit()


def display_highscores(screen: pygame.Surface,
                       clock: pygame.time.Clock,
                       settings: Settings) -> bool:
    """
    reads and dsiplays the highscores of the game
    Args:
    clock    -  pygame.Clock and the tickspeed at which it is run
    settings -  the current loaded settings of Pacman when the game is launched
                which includes the path to highscores
    """
    SCREEN_WIDTH = screen.get_width()
    pygame.display.set_caption("Pac-Man | Highscores")
    keep_displaying: bool = True
    caption_font: pygame.font.Font = pygame.font.Font(
        "data/font/Pixeltype.ttf",
        150
    )
    basic_font: pygame.font.Font = pygame.font.Font(
        "data/font/Pixeltype.ttf",
        100
    )
    back_button: TextButton = TextButton(
        screen, "Back", basic_font, "Black", "Grey75",
        50, 50, 1
    )
    screen.fill("Black")
    caption: pygame.Surface = caption_font.render("Highscores",
                                                  False, "Yellow")
    screen.blit(caption, ((SCREEN_WIDTH // 2) - (caption.get_width() // 2),
                          50))
    underline: pygame.Surface = caption_font.render("----------",
                                                    False, "Gold")
    screen.blit(underline, ((SCREEN_WIDTH // 2) - (underline.get_width() // 2),
                            caption.get_height() + 20))
    back_button.draw_button()
    data: List[Dict] = []
    if os.path.exists(settings.highscore_filename):
        hs: Highscore = Highscore(settings.highscore_filename)
        try:
            hs.load_json()
            data = hs.data
        except PME.InvalidJson:
            data = []
    start_x: int = SCREEN_WIDTH // 3
    start_y: int = 300
    x_offset: int = 0
    y_offset: int = 0
    for i, d in enumerate(data):
        if "name" not in d.keys() or "score" not in d.keys():
            continue
        i += 1
        information: str = f"{i}. {d["name"]}: {d["score"]}"
        player: pygame.Surface = basic_font.render(
            f"{information:<30}", False, "White"
        )
        screen.blit(
            player,
            (start_x - (player.get_width() // 2) + x_offset,
             start_y + y_offset)
        )
        x_offset = int(start_x * (i // 5) * 1.5)
        y_offset += player.get_height() + 25
        if i == 5:
            y_offset = 0
    running: bool = True
    while running and keep_displaying:
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    return False
                case pygame.KEYDOWN:
                    match event.key:
                        case pygame.K_ESCAPE:
                            running = False
                        case pygame.K_b:
                            keep_displaying = False
                        case _:
                            pass
                case pygame.MOUSEBUTTONDOWN:
                    if back_button.is_clicked():
                        keep_displaying = False
        clock.tick(60)
        pygame.display.flip()
    pygame.event.clear()
    return running


def display_settings(screen: pygame.Surface, clock: pygame.time.Clock,
                     settings: Settings) -> bool:
    """
    Displays and provides a interface to change the uploaded settings of
    the current game
    Args:
    clock    -  pygame.Clock and the tickspeed at which it is run
    settings -  the current loaded settings of Pacman when the game is launched
    """
    SCREEN_WIDTH = screen.get_width()
    screen.fill("Black")
    caption_font: pygame.font.Font = pygame.font.Font(
        "data/font/Pixeltype.ttf",
        150
    )
    basic_font: pygame.font.Font = pygame.font.Font(
        "data/font/Pixeltype.ttf",
        100
    )
    back_button: TextButton = TextButton(
        screen, "Back", basic_font, "Black", "Grey75",
        50, 50, 1
    )
    back_button.draw_button()

    start_y: int = 275
    start_x: int = 100
    off_x_1: int = 450
    off_x_2: int = 600
    dif: int = 100
    t_invincibility: pygame.Surface = basic_font.render(
        "Invincibility", False, "White")
    invincibility: ToggleButton = ToggleButton(
        screen, start_x + off_x_1, start_y + (dif * 0), 50, 50, 1,
        settings.invincibility
    )
    screen.blit(t_invincibility, (start_x, start_y + (dif * 0)))
    invincibility.draw_button()

    t_skip_level: pygame.Surface = basic_font.render("Skip level",
                                                     False, "White")
    skip_level: ToggleButton = ToggleButton(
        screen, start_x + off_x_1, start_y + (dif * 1), 50, 50, 1,
        settings.skip_level
    )
    screen.blit(t_skip_level, (start_x, start_y + (dif * 1)))
    skip_level.draw_button()

    t_always_fleeing: pygame.Surface = basic_font.render("Always fleeing",
                                                         False, "White")
    always_fleeing: ToggleButton = ToggleButton(
        screen, start_x + off_x_1, start_y + (dif * 2), 50, 50, 1,
        settings.always_flee
    )
    screen.blit(t_always_fleeing, (start_x, start_y + (dif * 2)))
    always_fleeing.draw_button()

    t_fast_pacman: pygame.Surface = basic_font.render("Fast pacman",
                                                      False, "White")
    fast_pacman: ToggleButton = ToggleButton(
        screen, start_x + off_x_1, start_y + (dif * 3), 50, 50, 1,
        settings.fast_pacman
    )
    screen.blit(t_fast_pacman, (start_x, start_y + (dif * 3)))
    fast_pacman.draw_button()

    t_slow_ghost: pygame.Surface = basic_font.render("Slow ghost",
                                                     False, "White")
    slow_ghost: ToggleButton = ToggleButton(
        screen, start_x + off_x_1, start_y + (dif * 4), 50, 50, 1,
        settings.slow_ghosts
    )
    screen.blit(t_slow_ghost, (start_x, start_y + (dif * 4)))
    slow_ghost.draw_button()

    t_random_seeds: pygame.Surface = basic_font.render("Random seeds",
                                                       False, "White")
    random_seeds: ToggleButton = ToggleButton(
        screen, start_x + off_x_1, start_y + (dif * 5), 50, 50, 1,
        settings.random_seeds
    )
    screen.blit(t_random_seeds, (start_x, start_y + (dif * 5)))
    random_seeds.draw_button()

    t_width: pygame.Surface = basic_font.render("Width", False, "White")
    inc_w: TextButton = TextButton(
        screen, "+", basic_font, "Grey50", "White", start_x + off_x_2 + 225,
        start_y + (dif * 0), 1
    )
    dec_w: TextButton = TextButton(
        screen, "-", basic_font, "Grey50", "White", start_x + off_x_2 + 300,
        start_y + (dif * 0), 1
    )
    screen.blit(t_width, (start_x + off_x_2, start_y + (dif * 0)))
    inc_w.draw_button()
    dec_w.draw_button()

    t_height: pygame.Surface = basic_font.render("Height", False, "White")
    inc_h: TextButton = TextButton(
        screen, "+", basic_font, "Grey50", "White", start_x + off_x_2 + 225,
        start_y + (dif * 1), 1
    )
    dec_h: TextButton = TextButton(
        screen, "-", basic_font, "Grey50", "White", start_x + off_x_2 + 300,
        start_y + (dif * 1), 1
    )
    screen.blit(t_height, (start_x + off_x_2, start_y + (dif * 1)))
    inc_h.draw_button()
    dec_h.draw_button()

    caption: pygame.Surface = caption_font.render(
        "Settings", False, "Yellow"
    )
    screen.blit(
        caption, ((SCREEN_WIDTH // 2) - (caption.get_width() // 2), 50)
    )
    underline: pygame.Surface = caption_font.render(
        "--------", False, "Gold"
    )
    screen.blit(underline, ((SCREEN_WIDTH // 2) - (underline.get_width() // 2),
                            caption.get_height() + 20))
    keep_displaying: bool = True
    running: bool = True
    wr: pygame.Rect | None = None
    hr: pygame.Rect | None = None
    while running and keep_displaying:
        w_value: pygame.Surface = basic_font.render(
            f"{settings.width}", False, "White"
        )
        if wr:
            wr.topleft = (start_x + off_x_2 + 400, start_y + (dif * 0))
            screen.fill("Black", wr)
        screen.blit(w_value, (start_x + off_x_2 + 400, start_y + (dif * 0)))
        h_value: pygame.Surface = basic_font.render(
            f"{settings.height}", False, "White"
        )
        if hr:
            hr.topleft = (start_x + off_x_2 + 400, start_y + (dif * 1))
            screen.fill("Black", hr)
        screen.blit(h_value, (start_x + off_x_2 + 400, start_y + (dif * 1)))

        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    running = False
                    keep_displaying = False
                case pygame.KEYDOWN:
                    match event.key:
                        case pygame.K_ESCAPE:
                            running = False
                        case pygame.K_b:
                            keep_displaying = False
                        case _:
                            pass
                case pygame.MOUSEBUTTONDOWN:
                    if back_button.is_clicked():
                        keep_displaying = False
                    elif invincibility.is_clicked():
                        settings.invincibility = invincibility.on_off
                        invincibility.draw_button()
                    elif skip_level.is_clicked():
                        settings.skip_level = skip_level.on_off
                        skip_level.draw_button()
                    elif always_fleeing.is_clicked():
                        settings.always_flee = always_fleeing.on_off
                        always_fleeing.draw_button()
                    elif fast_pacman.is_clicked():
                        settings.fast_pacman = fast_pacman.on_off
                        fast_pacman.draw_button()
                    elif slow_ghost.is_clicked():
                        settings.slow_ghosts = slow_ghost.on_off
                        slow_ghost.draw_button()
                    elif random_seeds.is_clicked():
                        settings.random_seeds = random_seeds.on_off
                        random_seeds.draw_button()
                    elif inc_w.is_clicked():
                        if settings.width < 45:
                            settings.width += 1
                    elif dec_w.is_clicked():
                        if settings.width > 10:
                            settings.width -= 1
                    elif inc_h.is_clicked():
                        if settings.height < 30:
                            settings.height += 1
                    elif dec_h.is_clicked():
                        if settings.height > 10:
                            settings.height -= 1
        wr = w_value.get_rect()
        hr = h_value.get_rect()
        clock.tick(60)
        pygame.display.flip()
    pygame.event.clear()
    settings.save_settings()
    return running
