import pygame


pygame.init()


class Toggle:
    def __init__(self, x, y, image_on, image_off, initial=True):
        self.x = x
        self.y = y
        self.image_on = pygame.image.load("sfx on.png")
        self.image_off = pygame.image.load("sfx off.png")
        self.state = initial
        self.rect = self.image_on.get_rect(topleft=(x,y))
        self.clicked = False #not being clicked at the moment


    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN: #is mouse being pressed
            if event.button == 1: #is the button the left mouse button
                if self.rect.collidepoint(event.pos) and not self.clicked: #if in hitbox and clicked
                    self.state = not self.state #changes state
                    self.clicked = True
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.clicked = False


    def draw(self, screen):
        if self.state == True:
            screen.blit(self.image_on, (self.x, self.y))
        else:
            screen.blit(self.image_off, (self.x, self.y))