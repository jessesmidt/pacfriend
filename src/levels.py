from settings import Settings
import random


class Levels():
    def __init__(self, settings: Settings):
        self.settings: Settings = settings

    def get_seeds(self) -> list[int]:
        sdamt = len(self.settings.seeds)
        if sdamt < 10:
            for _ in range(10-sdamt):
                self.settings.seeds.append(random.randint(0, 999))
        elif sdamt >= 10:
            return self.settings.seeds[10:]
        return self.settings.seeds
