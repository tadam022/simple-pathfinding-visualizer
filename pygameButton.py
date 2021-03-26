import pygame

class Button:

    def __init__(self, button_name, x, y, text, text_color, button_color, font, active=True):
        self.button_name = button_name
        self.x = x
        self.y = y
        self.text = text
        self.text_color = text_color
        self.original_text_color = text_color
        self.font = font
        self.button_color = button_color
        self.original_color = button_color
        self.text = font.render(text, True, text_color)
        self.text_rect = self.text.get_rect(topleft=(x, y))
        self.size = self.text.get_size()
        self.active = active
        self.rect = pygame.Rect(self.x, self.y, self.size[0], self.size[1] + 3)
        self.algorithms = dict()
        self.counter = 0

    def change_text_color(self, text_color):
        self.text_color = text_color

    def change_button_color(self, button_color):
        self.button_color = button_color

    def change_text(self, new_text):
        self.text = self.font.render(new_text, True, self.text_color)

    def is_clicked(self, event):
        x, y = pygame.mouse.get_pos()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 or event.button == 3:
                if self.rect.collidepoint(x, y):
                    return True
        return False

    def is_hovered(self):
        x, y = pygame.mouse.get_pos()
        if self.rect.collidepoint(x, y):
            return True

    def set_active(self, active):
        self.active = active

        if not active:
            self.change_button_color((32, 33, 32))
            self.text_color = (150, 160, 27)
        else:
            self.change_button_color(self.original_color)
            self.text_color = self.original_text_color

    def is_active(self):
        return self.active
