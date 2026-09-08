from typing import Dict, List
from src.json_work import JSONWork
import os


class Highscore(JSONWork):
    """
    Inherited from JSONwork, whenever a file path gets processed,
    we'll first check valid JSON (after the required comments).
    Handles adding players, keeping the highscores.json neat
    and a helper function to return number 1 highscorer.

    parameters:
    - highscores = list of max 10 players and their score
    {player_name: score}
    """
    def __init__(self, path: str):
        self.highscores: List[Dict] = []
        super().__init__(path)
        if not os.path.exists(path):
            with open(path, "w") as file:
                file.write("[]")

    def add_player(self, name: str, score: int) -> None:
        """
        Adds a player to the highscores path
        The list in ordered in decending order and only the highest ten ranks
        are stored
        Arguments:
        name: str - the name of the entry to add
        score: int - the amount of points they gathered
        """
        if len(self.highscores) == 0:
            self.load_json()
            self.highscores = self.data
        pos: int = 0
        name = name[:10]
        for player in self.highscores:
            if player["score"] <= score:
                break
            pos += 1
        if pos < 9:
            self.highscores.append({"name": name, "score": score})
        self.highscores.sort(key=lambda x: x["score"], reverse=True)
        while len(self.highscores) > 10:
            self.highscores.pop(-1)
        self.dump_json(self.highscores)

    def return_first(self) -> Dict:
        """
        Scans the highscores and returns the score / name of the 1st player
        """
        if len(self.highscores) == 0:
            self.load_json()
            self.highscores = self.data
        if len(self.highscores) == 0:
            return {"name": "None",
                    "score": 0}
        highest: int = 0
        recordholder: str = ""
        for player in self.highscores:
            if player["score"] > highest:
                recordholder, highest = player["name"], player["score"]
        return {"name": recordholder, "score": highest}
