from typing import Dict, List
from json_work import JSONWork
import errors as PME
import random
import json


class Constants:
    DEFAULT_SETTINGS_PATH = "data/settings/default_settings.json"
    DEFAULT_HIGHSCORES_PATH = "data/highscores/highscores.json"
    GHOST_IMG_PATH = "data/assets/ghost.png"
    TICKSPEED = 80
    T_SIZE = 64
    SBAR_H = 128
    INPUT_TICK = 22
    VALID_DIRS = [1, 2, 4, 8]
    CARDINALS = {0: (0, 0), 1: (0, -1), 2: (1, 0), 4: (0, 1), 8: (-1, 0)}
    CORRIDORS = [5, 10]
    DEFAULT_SEEDS = [100, 23, 31, 4, 53, 61, 7, 81, 91, 42]


class Settings(Constants):
    def __init__(self) -> None:
        self.path_to_settings: str = self.DEFAULT_SETTINGS_PATH
        self.highscore_filename: str = self.DEFAULT_HIGHSCORES_PATH
        self.pacman_img: str = "data/assets/pacman_animation.png"
        self.lives: int = 3
        self.width: int = 15
        self.height: int = 15
        self.seeds: List[int] = self.DEFAULT_SEEDS
        self.max_time_per_level: int = 90
        self.points_per_pacgum: int = 10
        self.points_per_super_pacgum: int = 50
        self.points_per_ghost: int = 200

        self.invincibility: bool = False
        self.skip_level: bool = False
        self.always_flee: bool = False
        self.fast_pacman: bool = False
        self.slow_ghosts: bool = False
        self.random_seeds: bool = False

    def is_cheating(self) -> bool:
        """
        Checks if cheats are enabled
        """
        return (self.invincibility
                and self.skip_level
                and self.always_flee
                and self.fast_pacman
                and self.slow_ghosts)

    @staticmethod
    def extract_settings(path_to_settings: str | None) -> "Settings":
        """
        Tries to load the JSON settings file or reverts to default
        settings.

        Args:
        - path_to_settings:
            address to the settings file
        """
        if not path_to_settings:
            path_to_settings = Constants.DEFAULT_SETTINGS_PATH
        settings: Settings = Settings()
        try:
            loaded: JSONWork = JSONWork(path_to_settings)
            loaded.load_json()
            if isinstance(loaded.data, dict):
                for key in loaded.data.keys():
                    if key in settings.__dict__.keys():
                        setattr(settings, key, loaded.data[key])
                settings.path_to_settings = path_to_settings
            else:
                print("Invalid settings: Settings must be a valid dictionary")
        except (PME.InvalidJson, PME.NonExistingPath) as e:
            print(f"Invalid settings: {e}")
            print("Returning to default settings")
        seed_len: int = len(settings.seeds)
        if seed_len < 10:
            for _ in range(10 - seed_len):
                settings.seeds.append(random.randint(0, 999))
        elif seed_len > 10:
            settings.seeds = settings.seeds[10:]
        if settings.width < 10:
            settings.width = 10
        elif settings.width > 45:
            settings.width = 45
        if settings.height < 10:
            settings.height = 10
        elif settings.height > 30:
            settings.height = 30
        return settings

    def save_settings(self) -> None:
        """
        Saves the current settings to the specified path
        """
        data: Dict = {"highscore_filename": self.highscore_filename}
        for value in self.__dict__:
            if value == "max_time_per_level":
                continue
            if type(self.__getattribute__(value)) == int:
                data[value] = self.__getattribute__(value)
        with open(self.path_to_settings, "w") as file:
            json.dump(data, file, indent=2)
