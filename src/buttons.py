from typing import Tuple
from abc import ABC
import pygame


class Button(ABC):
    def __init__(self,
                 surface: pygame.Surface,
                 x: int,
                 y: int,
                 scale: float
                 ):
        self.surface: pygame.Surface = surface
        self.x: int = x
        self.y: int = y
        self.enabled: bool = True
        self.rect: pygame.Rect = self.surface.get_rect()

    def draw_button(self, offset_x: int = 0, offset_y: int = 0) -> None:
        pass

    def update_coordinates_scale(self, pos: None | Tuple[int, int],
                                 scale: None | int) -> None:
        pass

    def is_clicked(self) -> bool:
        mouse_position: Tuple[int, int] = pygame.mouse.get_pos()
        to_return: bool = False
        if pygame.mouse.get_pressed()[0]:
            if self.rect and self.rect.collidepoint(mouse_position):
                to_return = True
        return to_return


class ImageButton(Button):
    def __init__(
            self,
            surface: pygame.Surface,
            image: pygame.Surface,
            x: int,
            y: int,
            scale: float):
        super().__init__(surface, x, y, scale)
        self.image: pygame.Surface = image
        self.width: int = int(self.image.get_width() * scale)
        self.height: int = int(self.image.get_height() * scale)
        self.image_button = pygame.transform.scale(
            self.image,
            (self.width, self.height)
            )
        self.rect: pygame.Rect = self.image.get_rect()
        self.rect.topleft = (self.x, self.y)

    def draw_button(self, offset_x: int = 0, offset_y: int = 0) -> None:
        """
        Draws a button auto sized to fit the text on the screen
        """
        self.surface.blit(
            self.image_button,
            (self.x + offset_x, self.y + offset_y)
        )

    def update_coordinates_scale(self, pos: None | Tuple[int, int],
                                 scale: None | int) -> None:
        if pos:
            self.x, self.y = pos
        if not scale:
            return
        self.width = self.image.get_width() * scale
        self.height = self.image.get_height() * scale
        self.image_button = pygame.transform.scale(
            self.image,
            (self.width, self.height)
        )
        self.rect.topleft = (self.x, self.y)


class TextButton(Button):
    def __init__(
            self,
            surface: pygame.Surface,
            text: str,
            font: pygame.font.Font,
            base_colour: str,
            font_colour: str,
            x: int,
            y: int,
            scale: float):
        super().__init__(surface, x, y, scale)
        self.font: pygame.font.Font = font
        self.font_text: pygame.Surface = font.render(text, False, font_colour)
        self.width: int = int(self.font_text.get_width() * scale)
        self.height: int = int(self.font_text.get_height() * scale)
        self.font_text = pygame.transform.scale(self.font_text,
                                                (self.width, self.height))
        self.base: pygame.Surface = pygame.Surface((self.width * 1.1,
                                                    self.height * 1.1))
        self.base_colour: str = base_colour
        self.base.fill(self.base_colour)
        self.rect: pygame.Rect = self.base.get_rect()
        self.rect.topleft = (self.x, self.y)

    def draw_button(self, offset_x: int = 0, offset_y: int = 0) -> None:
        """
        Draws a button auto sized to fit the text on the screen
        """
        self.surface.blit(
            self.base,
            (self.x, self.y)
        )
        self.surface.blit(
            self.font_text,
            (self.x + self.width * 0.05,
             self.y + self.height * 0.05)
        )

    def update_coordinates_scale(self, pos: None | Tuple[int, int],
                                 scale: None | int) -> None:
        if pos:
            self.x, self.y = pos
            self.rect.topleft = (self.x, self.y)
        if not scale:
            return
        self.width = self.font_text.get_width() * scale
        self.height = self.font_text.get_height() * scale
        self.font_text = pygame.transform.scale(
            self.font_text,
            (self.width, self.height)
            )
        self.base = pygame.Surface((self.width * 1.10,
                                    self.height * 1.10))
        self.base.fill(self.base_colour)
        self.rect = self.font_text.get_rect()
        self.rect.topleft = (self.x, self.y)


class ToggleButton(Button):
    ON_C = "forestgreen"
    OFF_C = "firebrick1"

    def __init__(
            self,
            surface: pygame.Surface,
            x: int, y: int,
            width: int, height: int,
            scale: float, on_off: bool):
        super().__init__(surface, x, y, scale)
        self.width: int = int(width * scale)
        self.height: int = int(height * scale)
        self.on_off: bool = on_off
        self.base: pygame.Surface = pygame.Surface((self.width, self.height))
        self.rect: pygame.Rect = self.base.get_rect()
        self.rect.topleft = (self.x, self.y)
        self.base.fill("khaki3")
        self.colour: pygame.Surface = pygame.Surface(
            (int(self.width * 0.80), int(self.height * 0.80))
        )
        if on_off:
            self.colour.fill(self.ON_C)
        else:
            self.colour.fill(self.OFF_C)

    def draw_button(self, offset_x: int = 0, offset_y: int = 0) -> None:
        """
        Draws a button auto sized to fit the text on the screen
        """
        self.surface.blit(
            self.base, (self.x + offset_x, self.y + offset_y)
        )
        self.surface.blit(
            self.colour,
            (self.x + offset_x + ((self.width + offset_x) * 0.1),
             self.y + offset_y + ((self.height + offset_y) * 0.1))
        )

    def is_clicked(self) -> bool:
        if super().is_clicked():
            self.draw_button()
            if self.on_off:
                self.on_off = False
                self.colour.fill(self.OFF_C)
            else:
                self.on_off = True
                self.colour.fill(self.ON_C)
            return True
        return False
