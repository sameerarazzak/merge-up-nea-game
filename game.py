import pygame, pymunk, sys, time, button, toggle
import numpy as np


pygame.init()
random_num_generator = np.random.default_rng() #initialise a random number generator


size = width, height = np.array([1000, 600]) #tuple to hold dimensions of screen
PAD = tuple((302, 120)) #distance of container from edge of window


#define corners of container
A = (302, 120) #top left
B = (302,550) #bottom left
C = (694,550) #bottom right
D = (694,120) #top right


#defining colours
bg_colour = (238,217,196)
wall_colour = (129, 82, 82)
colours = [
    (195, 87, 87),
    (232, 146, 148),
    (247, 180, 132),
    (252, 216, 130),
    (183, 205, 168),
    (112, 150, 107),
    (201, 226, 247),
    (99, 141, 181),
    (202, 165, 212),
    (150, 125, 184),
    (245, 175, 194)
]
#loading images
bg = pygame.image.load("background.png")
game_bg = pygame.image.load("game screen setup.png")


pygame.display.set_caption("Merge Up!")


#defining constants
fps = 240 #limited to prevent lag
radii = [17, 25, 32, 38, 50, 63, 75, 87, 100, 115, 135] #size of fruits
thickness = 10 #container wall thickness
density = 0.001 #to later calculate mass and inertia
elasticity = 0.1 #behaviour upon collision (stick/bounce)
impulse = 10000 #burst of force when items merge
gravity = 2000 #pulls items down
damping = 0.8 #simulates air resistance (slows falling objects)
next_delay = fps #time between placing items
bias = 0.00001 #how fast collisions are resolved
points = [1, 3, 6, 10, 15, 21, 28, 36, 45, 55, 66] #scoring system


shape_to_particle = dict() #mapping values to a dictionary to look up later


class Particle:
    def __init__(self, pos, n, space, mapper): #constructor
        self.n = n % 11 #decides size
        self.radius = radii[self.n] #creates actual shape
        self.body = pymunk.Body(body_type=pymunk.Body.DYNAMIC) #forces can act on item
        self.body.position = tuple(pos)
        self.shape = pymunk.Circle(body=self.body, radius=self.radius)
        self.shape.density = density
        self.shape.elasticity = elasticity
        self.shape.collision_type = 1 #item-item or item-wall collision
        self.shape.friction = 0.2
        self.has_collided = False
        mapper[self.shape] = self


        space.add(self.body, self.shape)
        self.alive = True


    def draw(self, screen):
        if self.alive:
            colour1 = np.array(colours[self.n]) #outline colour
            colour2 = (colour1*0.8).astype(int)
            pygame.draw.circle(screen, tuple(colour2), self.body.position, self.radius)
            pygame.draw.circle(screen, tuple(colour1), self.body.position, self.radius*0.9)


    def kill(self, space):
        space.remove(self.body, self.shape)
        self.alive = False
   
    @property
    def pos(self):
        return np.array(self.body.position)


class PreParticle: #before drop, item is just a shape that can move within the spawn area
    def __init__(self, x, n):
        self.n = n % 11
        self.radius = radii[self.n]
        self.x = x


    def draw(self, screen):
        colour1 = np.array(colours[self.n]) #circle colour
        colour2 = (colour1*0.8).astype(int) #outline colour
        pygame.draw.circle(screen, tuple(colour2), (self.x, PAD[1]//2), self.radius)
        pygame.draw.circle(screen, tuple(colour1), (self.x, PAD[1]//2), self.radius*0.9)


    def set_x(self, x):
        lim = 306 + self.radius + thickness // 2
        self.x = np.clip(x, lim, width-lim) #stops item going outside of container
   
    def release(self, space, mapper):
        return Particle((self.x, PAD[1]//2), self.n, space, mapper)


class Wall:
    thickness = thickness


    def __init__(self, a, b, space):
        self.body = pymunk.Body(body_type=pymunk.Body.STATIC) #static because it is not affected by forces
        self.shape = pymunk.Segment(self.body, a, b, self.thickness//2) #line segment
        self.shape.friction = 10 #how easily items slide
        space.add(self.body, self.shape)


    def draw(self, screen):
        pygame.draw.line(screen, (wall_colour), self.shape.a, self.shape.b, self.thickness)
                 
def resolve_collision(item1, item2, space, particles, mapper):
    global impulse
    if item1.n == item2.n: #if two of the same item touch
        distance = np.linalg.norm(item1.pos - item2.pos) #find distance between centres
        if distance < 2*item1.radius: #if overlapping...
            item1.kill(space) #remove both from space
            item2.kill(space)
            itemn = Particle(np.mean([item1.pos, item2.pos], axis=0), item1.n+1, space, mapper) #create new item
            pygame.mixer.Sound.play(merge_sound) #sound effect for merge
            for item in particles: #check the rest of items in the container
                if item.alive:
                    vector = item.pos - itemn.pos #direction of impulse
                    distance = np.linalg.norm(vector) #impulse only affects nearby items
                    if distance < itemn.radius + item.radius: #if close enough...
                        impulse = impulse * vector / (distance ** 2)
                        item.body.apply_impulse_at_local_point(tuple(impulse)) #apply impulse to nearby items
            return itemn
    return None




#creating game window
screen = pygame.display.set_mode((width,height))
pygame.display.set_caption("GAME SCREEN v3")
clock = pygame.time.Clock()
text_colour = (176,104,104)
font = pygame.font.Font("game font.ttf", 30)
game_over_banner = pygame.image.load("game over banner.png")


click_sound = pygame.mixer.Sound("click sound.mp3")
merge_sound = pygame.mixer.Sound("merge sound.mp3")
game_over_sound = pygame.mixer.Sound("game over.mp3")


menu_button = pygame.image.load("menu.png")
menu = button.Button(menu_button, 805, 8, 0.18)
retry_button = pygame.image.load("retry.png")
retry = button.Button(retry_button, 398, 320, 0.2)


sfx_on = "sfx on.png"
sfx_off = "sfx off.png"
sfx_toggle = toggle.Toggle(x=640, y=430, image_on=sfx_on, image_off=sfx_off, initial=True)


#writing score
def draw_value(screen, label, value, x, y):
    text = font.render(f"{label}: {value}", True, text_colour)
    screen.blit(text, (x, y))


#writing the live list of recent points
def draw_score(screen, scores, x, y):
    for i, score in enumerate(reversed(scores)):
        score_text = font.render(f"+{score}", True, text_colour)
        screen.blit(score_text, (x, y+30+(i*30)))


#transition function between screen
def transition(screen, clock, duration=0.5):
    fade_surface = pygame.Surface((width, height), pygame.SRCALPHA)  #transparent background
    centre = (width // 2, height // 2)  #screen centre


    max_radius = int((width ** 2 + height ** 2) ** 0.5) // 2  #circle's biggest size to cover whole screen
    steps = 30  #smoothness
    delay = duration / steps  #time delay between circle shrinking


    for r in range(max_radius, 0, -max_radius // steps):  #makes circle smaller
        fade_surface.fill((0, 0, 0, 255))  #fills screen with black
        pygame.draw.circle(fade_surface, (0, 0, 0, 0), centre, r)  #hole in centre
        screen.blit(fade_surface, (0, 0))  #draws transition to screen
        pygame.display.update()
        time.sleep(delay)  #controls fade speed


def game_screen(screen, clock, open_menu, sfx_toggle, resume_state=None):
    transition(screen, clock)
    #assigning variables to space
    space = pymunk.Space()
    space.gravity = (0, gravity)
    space.damping = damping
    space.collision_bias = bias


    #continues gameplay
    if resume_state == True:
        particles = resume_state["particles"]
        score = resume_state["score"]
    else:
        particles = []
        score = 0


    #creating walls of container
    left = Wall(A, B, space)
    bottom = Wall(B, C, space)
    right = Wall(C, D, space)
    walls = [left, bottom, right]


    #list to store particles
    wait_next = 0
    next_particle = PreParticle(width//2, random_num_generator.integers(0,5))
    particles = []


    handler = space.add_collision_handler(1,1)


    recent_scores = []


    def collide(arbiter, space, data):
        shape1, shape2 = arbiter.shapes #two colliding particles
        _mapper = data["mapper"]
        particle1 = _mapper[shape1] #assigns them particle1 and particle2
        particle2 = _mapper[shape2]
        condition = bool(particle1.n != particle2.n) #checks if sizes are different
        particle1.has_collided = condition
        particle2.has_collided = condition
        if not condition: #if the same particles collide...
            new_particle = resolve_collision(particle1, particle2, space, data["particles"], _mapper)
            data["particles"].append(new_particle)
            data["score"] += points[particle1.n] #gain points


            recent_scores.append(points[particle1.n]) #update live score counter
            if len(recent_scores) > 7: #only display the last 7 point additions
                recent_scores.pop(0)
        return condition


    handler.begin = collide
    handler.data["mapper"] = shape_to_particle
    handler.data["particles"] = particles
    handler.data["score"] = 0


    paused = False
    game_over = False


    while not game_over:
        if not paused:
            screen.blit(game_bg,(0,0))
            menu.draw(screen, sfx_toggle.state)


            #redraw walls and item so transition doesn't blit over
            for w in walls:
                w.draw(screen)
            for p in particles:
                p.draw(screen)
           
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit() #closes game window if X clicked
                elif event.type == pygame.MOUSEBUTTONDOWN: #if mouse click detected...
                    #separates clicks (clicking menu button doesn't drop an item)
                    print("click")
                    if menu.draw(screen, sfx_toggle.state): #if menu button pressed
                        paused = True
                        transition(screen, clock)
                        open_menu()
                        paused = False                        
                    elif wait_next == 0: #if game pressed
                        particles.append(next_particle.release(space, shape_to_particle)) #generates new item
                        wait_next = next_delay
                        if sfx_toggle.state==True:
                            pygame.mixer.Sound.play(click_sound)
                elif event.type == pygame.KEYDOWN:  #detects any key press
                    print("key press")      
            next_particle.set_x(pygame.mouse.get_pos()[0])


            if wait_next > 1:
                wait_next -= 1
            elif wait_next == 1:
                next_particle = PreParticle(next_particle.x, random_num_generator.integers(0,5)) #spawn new item
                wait_next -= 1
       
            score = font.render(f"Score: {handler.data['score']}", True, text_colour)
            screen.blit(score, (75,50))
       
            if wait_next == 0:
                next_particle.draw(screen)
            for w in walls:
                w.draw(screen)
            for p in particles:
                p.draw(screen)
                if p.pos[1] < PAD[1] and p.has_collided: #checks if game has ended
                    pygame.mixer.Sound.play(game_over_sound)
                    game_over = True
                    screen.blit(game_over_banner, (200,200))
                    time.sleep(3)
                    transition(screen, clock)
                    game_over_screen(screen, open_menu, sfx_toggle, handler.data["score"])


            space.step(1/fps)
            draw_score(screen, recent_scores, 115, 160)
            pygame.display.update()
            clock.tick(fps)
           
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()


def game_over_screen(screen, open_menu, sfx_toggle, final_score):
    transition(screen, clock)
    run = True
    while run:
        screen.blit(bg,(0,0))
        screen.blit(game_over_banner, (200,100))


        final_score_text = font.render("FINAL SCORE:", True, text_colour)
        text_rect = final_score_text.get_rect(center=(width // 2, 250))  #centre final score text
        screen.blit(final_score_text, text_rect.topleft)


        score_text = font.render(str(final_score), True, text_colour)
        score_rect = score_text.get_rect(center=(width // 2, text_rect.bottom + 20))  
        screen.blit(score_text, score_rect.topleft) #dislay final score


        if retry.draw(screen, sfx_toggle.state): #if retry button clicked, open a new game
            transition(screen, clock)
            game_screen(screen, pygame.time.Clock(), open_menu, sfx_toggle)


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
           
        pygame.display.flip()


    pygame.quit()