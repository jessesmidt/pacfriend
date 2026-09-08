from typing import Tuple
from abc import ABC
import pygame


class Button(ABC):
    """

    The base class all buttons are based on with the same base functionality

    Attributes:
        surface (pygame.Surface): The surface on whch the button mmust be drawn
        x (int): The x coodinate of topleft of button
        y (int): The y coordinate of the topleft of the button
        scale (int): the scale at which the button should be drawn
        enabled (bool): If the button is visible and clickable
        rect (pygame.Rect): the rectangle which is clickable

    """
    def __init__(self,
                 surface: pygame.Surface,
                 x: int,
                 y: int,
                 scale: float
                 ):
        """
        Arguments:
            surface (pygame.Surface): The surface on which the button is drawn
            x (int): x coordinate of the topleft of button
            y (int): y coordinate of the toopleft of the button
            scale (float): The scale at which the biutton will be drawn
        """
        self.surface: pygame.Surface = surface
        self.x: int = x
        self.y: int = y
        self.enabled: bool = True
        self.rect: pygame.Rect = self.surface.get_rect()

    def draw_button(self, offset_x: int = 0, offset_y: int = 0) -> None:
        """

        Draws a button auto sized to fit the text on the screen

        Args:
            offset_x (int): the amount the button is offset on the x-axis
            offset_y (int): the amount the button is offset on the y-axis

        """
        pass

    def update_coordinates_scale(self, pos: None | Tuple[int, int],
                                 scale: None | float) -> None:
        """

        Updates the location the button is drawnb and at whicgh scale

        Arggs:
            pos (Tuple[int, int]):  Coordinates on screen the
                                    button should be drawn
            scale (float):  The scale at which the button should now be
                            displayed

        """
        pass

    def is_clicked(self) -> bool:
        """

        Keeps track of the mouse cursor and tracks if
        the button has been clicked

        Returns:


        """
        mouse_position: Tuple[int, int] = pygame.mouse.get_pos()
        to_return: bool = False
        if pygame.mouse.get_pressed()[0]:
            if self.rect and self.rect.collidepoint(mouse_position):
                to_return = True
        return to_return


class ImageButton(Button):
    """

    A button which can be loaded with an image

    Attributes:
        surface (pygame.Surface): The surface on whch the button must be drawn
        image (pygame.Surface): The image which is going to be displayed by the
                                button and is preloaded
        x (int): The x coodinate of topleft of button
        y (int): The y coordinate of the topleft of the button
        scale (int): the scale at which the button should be drawn
        enabled (bool): If the button is visible and clickable
        rect (pygame.Rect): the rectangle which is clickable
        width (int): The width of the image/button
        height (int): The hight of the image/button

    """
    def __init__(
            self,
            surface: pygame.Surface,
            image: pygame.Surface,
            x: int,
            y: int,
            scale: float):
        """
            Args:
                surface (pygame.Surface):   The surface on whch the button must
                                            be drawn
                image (pygame.Surface): The image which is going to be
                                        displayed by the button and is
                                        preloaded
                x (int): The x coodinate of topleft of button
                y (int): The y coordinate of the topleft of the button
                scale (int): the scale at which the button should be drawn

        """
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

        Args:
            offset_x (int): the amount the button is offset on the x-axis from
                            its original position
            offset_y (int): the amount the button is offset on the y-axis from
                            its original position

        """
        if not self.enabled:
            return
        self.surface.blit(
            self.image_button,
            (self.x + offset_x, self.y + offset_y)
        )

    def update_coordinates_scale(self, pos: None | Tuple[int, int],
                                 scale: None | float) -> None:
        """

        Updates the location the button is drawnb and at whicgh scale

        Arggs:
            pos (Tuple[int, int]):  Coordinates on screen the
                                    button should be drawn
            scale (None | int): The scale at which the button should now be
                                displayed

        """
        if pos:
            self.x, self.y = pos
        if not scale:
            return
        self.width = int(self.image.get_width() * scale)
        self.height = int(self.image.get_height() * scale)
        self.image_button = pygame.transform.scale(
            self.image,
            (self.width, self.height)
        )
        self.rect.topleft = (self.x, self.y)


class TextButton(Button):
    """

    A button class which can be displayed with text over it

    Attributes:
        surface (pygame.Surface): The surface on whch the button mmust be drawn
        text (str): the text whichg will be played the button and sets its size
        font (pygame.font.Font): The font in which the text will be displayed
        font_text (pygame.Surface): The text loaded with the font
        base (pygame.Surface): The base which will be behind the text
        base_colour (str): the colour of the base
        x (int): The x coodinate of topleft of button
        y (int): The y coordinate of the topleft of the button
        scale (int): the scale at which the button should be drawn
        enabled (bool): If the button is visible and clickable
        rect (pygame.Rect): the rectangle which is clickable
        width (int): The width of the image/button
        height (int): The hight of the image/button

    """
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
        """
        Creates an instance  of TextButton

        Arguments:
                surface (pygame.Surface): The surface on whch the button mmust
                                          be drawn
                text (str): The text whichg will be played the button and sets
                            its size
                font (pygame.font.Font): The font in which the text will be
                                        displayed
                font_colour (str): Colour of the font
                base_colour (str): The colour of the base
                x (int): The x coodinate of topleft of button
                y (int): The y coordinate of the topleft of the button
                scale (int): The scale at which the button should be drawn
        """
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

        Args:
            offset_x (int): The amount the button is offset on the x-axis from
                            its original position
            offset_y (int): The amount the button is offset on the y-axis from
                            its original position

        """
        if not self.enabled:
            return
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
                                 scale: None | float) -> None:
        """

        Updates the location the button is drawnb and at whicgh scale

        Arggs:
            pos (Tuple[int, int]):  Coordinates on screen the
                                    button should be drawn
            scale (int, None): The scale at which the button should now be
                               displayed

        """
        if pos:
            self.x, self.y = pos
            self.rect.topleft = (self.x, self.y)
        if not scale:
            return
        self.width = int(self.font_text.get_width() * scale)
        self.height = int(self.font_text.get_height() * scale)
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
    """

    A button class which can be displayed with text over it

    Attributes:
        surface (pygame.Surface): The surface on whch the button mmust
                                  be drawn
        width (int): The width of the ToggleButton
        height (int): The height of the TggleButton
        scale (int): The scale at which the button should be drawn
        on_off (bool): The innitial state
        base (pygame.Surface): The base which will be behind the text
        rect (pygame.Rect): the rectangle which is clickable
        width (int): The width of the image/button
        height (int): The hight of the image/button
        colour (pygame.Surface): The colour in the middle of the button

    """
    ON_C = "forestgreen"
    OFF_C = "firebrick1"

    def __init__(
            self,
            surface: pygame.Surface,
            x: int, y: int,
            width: int, height: int,
            scale: float, on_off: bool):
        """
        Creates an instance  of ToggleButton

        Arguments:
                surface (pygame.Surface): The surface on whch the button mmust
                                          be drawn
                x (int): The x coodinate of topleft of button
                y (int): The y coordinate of the topleft of the button
                width (int): The width of the ToggleButton
                height (int): The height of the TggleButton
                scale (int): The scale at which the button should be drawn
                on_off (bool): The innitial state
        """
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

        Args:
            offset_x (int): the amount the button is offset on the x-axis from
                            its original position
            offset_y (int): the amount the button is offset on the y-axis from
                            its original position

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
        """

        Keeps track of the mouse cursor and tracks if
        the button has been clicked. In addition it changes
        the colour of the button to match the state of
        the button

        Returns:
            bool: if the button was clicked or not

        """
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
