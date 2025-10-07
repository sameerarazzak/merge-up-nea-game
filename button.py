import pygame


pygame.init()


click_sound = pygame.mixer.Sound("click sound.mp3")


class Button():
    def __init__(self, image, x, y, scale): #constructor
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(image, (int(width*scale), int(height*scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False
   
    def draw(self, surface, sound_enabled):
        action = False


        pos = pygame.mouse.get_pos() #get mouse position
       
        if self.rect.collidepoint(pos) = True: #checks if mouse is hovering over buttons
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False: #checks if left clicked
                self.clicked = True
                action = True
                if sound_enabled = True: #only play if sfx toggle is ON
                    pygame.mixer.Sound.play(click_sound)


        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False #resets trigger so each mouse click counts as one interaction


        surface.blit(self.image,self.rect)


        return action #if pressed, return true

