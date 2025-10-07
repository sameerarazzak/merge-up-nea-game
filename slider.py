import pygame


pygame.init()


class Slider:
    def __init__(self, x, y, width, handle_radius=15, slider_height=10, min_value=0, max_value=100, initial_value=0.5):
        self.x = x
        self.y = y
        self.width = width
        self.handle_radius = handle_radius
        self.slider_height = slider_height
        self.min_value = min_value
        self.max_value = max_value
        self.value = initial_value


        # Initialize the handle position in the middle of the slider
        self.handle_x = self.x + self.width // 2
        self.dragging = False


        # Colors
        self.slider_color = (204,156,148)
        self.handle_color = (180,109,109)


    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # checks if left mouse button is pressing on handle
                mouse_x, mouse_y = event.pos
                if (self.handle_x - self.handle_radius <= mouse_x <= self.handle_x + self.handle_radius and
                    self.y + self.slider_height // 2 - self.handle_radius <= mouse_y <= self.y + self.slider_height // 2 + self.handle_radius):
                    self.dragging = True


        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # left mouse button
                self.dragging = False


        elif event.type == pygame.MOUSEMOTION:
            if self.dragging==True:
                mouse_x, _ = event.pos
                self.handle_x = max(self.x, min(mouse_x, self.x + self.width)) #keeps handle inside the slider
       
        self.value = (self.handle_x -self.x) / self.width #updates value


    def draw(self, screen):
        pygame.draw.rect(screen, self.slider_color, (self.x, self.y, self.width, self.slider_height))
        handle_y = self.y + self.slider_height // 2
        pygame.draw.circle(screen, self.handle_color, (self.handle_x, handle_y), self.handle_radius)


    def get_value(self):
        #return int(self.min_value + ((self.handle_x - self.x) / self.width) * (self.max_value - self.min_value))
        return self.value
