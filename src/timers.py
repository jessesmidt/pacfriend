from settings import Constants


class Timers():
    def __init__(self) -> None:
        self.countdown: int = 0
        self.animation_t: int = 0
        self.move_timer: int = 0
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
        self.move_timer = 0
        self.time_left = level_time
        self.protection = 0
