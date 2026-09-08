from typing import Dict, List
from src.json_work import JSONWork
from src import errors as PME
import os
import random


class Constants:
    """

    An old style class which stores the constants which are used
    throughout the program

    """
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
    DATA = [
        "data/assets/ghost.png",
        "data/assets/instructions.png",
        "data/assets/pacdeath.png",
        "data/assets/pacgum.png",
        "data/assets/pacman_animation.png",
        "data/assets/pacman_play.png",
        "data/assets/pactiles.png",
        "data/assets/s_pacgum.png",
        "data/font/Pixeltype.ttf",
        "data/mazegenerator-00001-py3-none-any.whl"
    ]


class Settings(Constants):
    """
    The purpose of the Settings class is to mange, validate and set the
    settings which will be used throughout the Pac-Man project

    before anything is stored, we check for correct files / permissions

    parameters:
    - path_to_settings = default settings file location
    - highscore_filename = default highscore filename
    - pacman_img = location to pacman img
    - lives = integer for amount of lives, overwritable by config
    - width, height = default maze size, overwritable by config
    - seeds = list of 10 integers, used for map seeds. Uses default
    - points_per_* = default points amount in case of missing settings
    - invincibility = cheat for debugging, not able to lose live
    - skip_level = cheat for debugging, ability to skip levels
    - always_flee = cheat, ghosts will be permanently in fleeing state
    - fast_pacman = cheat, double pacman speed
    - slow_ghosts = cheat, ghosts move half their normal speed
    - random_seeds = used for debugging, or testing different maps
    - loaded = Settings which were loaded in case of valid settings file
    """
    def __init__(self) -> None:
        self._validate_assets()
        self._validate_filepath(self.DEFAULT_SETTINGS_PATH)
        self._validate_filepath(self.DEFAULT_HIGHSCORES_PATH)
        self.path_to_settings: str = self.DEFAULT_SETTINGS_PATH
        self.highscore_filename: str = self.DEFAULT_HIGHSCORES_PATH
        self.pacman_img: str = "data/assets/pacman_animation.png"
        self.lives: int = 3
        self.width: int = 15
        self.height: int = 15
        self.seeds: List[int] = self.DEFAULT_SEEDS

        self.points_per_pacgum: int = 10
        self.points_per_super_pacgum: int = 50
        self.points_per_ghost: int = 200

        self.invincibility: bool = False
        self.skip_level: bool = False
        self.always_flee: bool = False
        self.fast_pacman: bool = False
        self.slow_ghosts: bool = False
        self.random_seeds: bool = False

        self.loaded: None | JSONWork = None

    def _validate_assets(self) -> None:
        """
        Validates the existance and permissions on all assets we deliver,
        as they could be changed by the user.
        """
        for asset_path in Constants.DATA:
            if not os.path.exists(asset_path):
                print(f"{asset_path} raised an error:\nFile not Found")
                from os import _exit
                _exit(0)
            if not os.access(asset_path, os.R_OK):
                print(f"{asset_path} raised an error:\nNo permissions")
                from os import _exit
                _exit(0)

    def _validate_filepath(self, path: str, should_exit: bool = True) -> bool:
        """

        Validates the provided path for permissions, exiting or equivalent
        If an error is raised the program will quit as this is fundamental
        change to the provided

        Args:
            path (str): The path to the file which need to be validated

            should_exit (bool): If program should exit if it is an
                                invalid program

        Returns:
            bool: False is invalid path and True if valid

        """
        try:
            with open(path, "r"):
                pass
            with open(path, "a"):
                pass
        except Exception as e:
            if not should_exit:
                return False
            print(f"{path} raised an error:\n{e}")
            from os import _exit
            _exit(0)
        finally:
            return True

    def is_cheating(self) -> bool:
        """

        Returns the state of the game if cheets have been enabled

        """
        return (self.invincibility
                or self.skip_level
                or self.always_flee
                or self.fast_pacman
                or self.slow_ghosts)

    def extract_settings(self, path_to_settings: str | None) -> "Settings":
        """

        Tries to load the JSON settings file or reverts to default
        settings.

        Args:
            path_to_settings (str): path to the settings file

        Returns:
            Settings: An instance of the current class

        """
        if path_to_settings:
            if not self._validate_filepath(path_to_settings, False):
                path_to_settings = self.DEFAULT_SETTINGS_PATH
            self.path_to_settings = path_to_settings
        if self.loaded is None:
            self.loaded = JSONWork(self.path_to_settings)
        try:
            self.loaded.load_json()
            if isinstance(self.loaded.data, dict):
                for key in self.loaded.data.keys():
                    if key in self.__dict__.keys():
                        if type(self.loaded.data[key]) is int:
                            setattr(self, key, (self.loaded.data[key]))
            else:
                print("Invalid settings: Settings must be a valid dictionary")
            seed_len: int = len(self.seeds)
            if seed_len < 10:
                for _ in range(10 - seed_len):
                    self.seeds.append(random.randint(0, 999))
            elif seed_len > 10:
                self.seeds = self.seeds[10:]
            if self.width < 10:
                self.width = 10
            elif self.width > 45:
                self.width = 45
            if self.height < 10:
                self.height = 10
            elif self.height > 30:
                self.height = 30
        except (PME.InvalidJson, PME.NonExistingPath) as e:
            print(f"Invalid settings: {e}")
            print("Returning to default settings")
        return self

    def save_settings(self) -> None:
        """

        Saves the current state of the class to the specified settings file

        """
        data: Dict = dict([])
        for value in self.__dict__:
            if type(self.__getattribute__(value)) == int:
                data[value] = self.__getattribute__(value)
        if self.loaded is None:
            print("JSONWork is not loaded so unable to save settings")
            return
        self.loaded.dump_json(data)
