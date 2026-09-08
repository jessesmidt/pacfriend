from src.settings import Constants


class Timers():
    """
    Keeps track of timings, e.g. start countdown, animation timings
    and respawn / protection

    parameters:
    - countdown = int for start of game time
    - animation_t = int, responsible for pacman's 'eating' animation
    - time_left = int, time left in game. When 0 = gameover
    - respawn = when death occurs, this handles time for death
    animation and respawning
    - protection = When eaten, set a timer to prevent multiple lives
    from being lost in one interaction with a ghost
    """
    def __init__(self) -> None:
        self.countdown: int = 0
        self.animation_t: int = 0
        self.time_left: int = 0
        self.respawn: int = 0
        self.protection: int = 0

    def reset_timers(self, level_time: int) -> None:
        """
        Used every time a new level is ran, resets all necessary timers.

        Args:
        - level_time
            The amount of time we need to set per level
        """
        self.countdown = 3 * Constants.TICKSPEED
        self.animation_t = 0
        self.time_left = level_time
        self.protection = 0
