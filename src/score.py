
from src.highscores import Highscore


class Scoringsystem():
    """
    Handles opening the highscores file, fallback, gathering points
    and retrieving highscores for the main screen.

    parameters:
    - score = The players current score in integer, default = 0
    - highscores = The current highscore, retrieved from highscores class.
    Falls back to 0 whenever retrieving fails
    - pacgums_pts, spacgum_pts, ghost_pts = amount of points per consume,
    fetched from settings
    """
    def __init__(
            self, pacgum_pts: int, spacgum_pts: int, ghost_pts: int
            ) -> None:
        self.score: int = 0
        self.highscores: Highscore = Highscore(
            "data/highscores/highscores.json")
        try:
            self.highscore: dict[str, int] = self.highscores.return_first()
        except Exception as e:
            print(F"Error retrieving highscore: {e}")
            self.highscore = {"score": 0}
        self.pacgum_pts: int = pacgum_pts
        self.spacgum_pts: int = spacgum_pts
        self.ghost_pts: int = ghost_pts

    def level_complete(self, level: int) -> None:
        """
        Gives points according on which level has been
        completed.

        Args:
        - level
        Integer that tells which level has been completed.
        """
        scores = [1000, 1250, 1500, 1750, 2000, 2500, 3000, 3500, 4000, 5000]
        self.score += scores[level - 1]

    def get_points(self, target: str) -> None:
        """
        This helper function gets called whenever points
        are supposed to be added, and adds the score.

        Args:
        - target
        String that contains what to add points for.
        """
        if target == "gum":
            self.score += self.pacgum_pts
        elif target == "sgum":
            self.score += self.spacgum_pts
        elif target == "ghost":
            self.score += self.ghost_pts
