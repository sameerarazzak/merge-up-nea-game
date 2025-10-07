import pygame, time
import button, slider, toggle
from game import game_screen
from ffpyplayer.player import MediaPlayer


pygame.init()


width = 1000
height = 600


beige = (238,217,196) 
text_colour = (176,104,104)
font = pygame.font.Font("game font.ttf", 22)


screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Merge Up!")


#function to write volume on screen
def draw_value(screen, label, value, x, y):
    text = font.render(f"{label}: {value}", True, text_colour)
    screen.blit(text, (x, y))




#load in images of logo and buttons
logo = pygame.image.load("logo.png")
logo = pygame.transform.scale(logo, (240,250))
icon = pygame.image.load("icon.png")
pygame.display.set_icon(icon)
bg = pygame.image.load("background.png")


play_button = pygame.image.load("play.png")
quit_button = pygame.image.load("quit.png")


menu_button = pygame.image.load("menu.png")
menu_banner = pygame.image.load("menu banner.png")
menu_banner = pygame.transform.scale(menu_banner, (384,170))
game_over_banner = pygame.image.load("game over banner.png")


restart_button = pygame.image.load("restart.png")
howto_button = pygame.image.load("howto.png")
theme_button = pygame.image.load("theme.png")
resume_button = pygame.image.load("resume.png")


#load in music and sfx
pygame.mixer.music.load("game music.mp3")
pygame.mixer.music.play(-1,0.0,2000) #loops music infinitely


click_sound = pygame.mixer.Sound("click sound.mp3")
sfx_on = "sfx on.png"
sfx_off = "sfx off.png"
merge_sound = pygame.mixer.Sound("merge sound.mp3")
game_over_sound = pygame.mixer.Sound("game over.mp3")


play = button.Button(play_button, 380, 300, 0.25)
menu = button.Button(menu_button, 805, 8, 0.18)
quitB = button.Button(quit_button, 428, 430, 0.15)


restart = button.Button(restart_button, 305, 220, 0.2)
howto = button.Button(howto_button, 515, 210, 0.18)
theme = button.Button(theme_button, 350, 300, 0.3)
resume = button.Button(resume_button, 8, 8, 0.2)


#create audio slider instance
audio_slider = slider.Slider(x=120, y=450, width=400)
pygame.mixer.music.set_volume(audio_slider.get_value())
#create sfx toggle instance
sfx_toggle = toggle.Toggle(x=640, y=430, image_on=sfx_on, image_off=sfx_off, initial=True)


clock = pygame.time.Clock()


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




#home screen function
def home_screen():
    run = True
    while run: #game loop is initialised
        screen.blit(bg, (0,0))
        screen.blit(logo, (380,50))    
       
        if quitB.draw(screen, sfx_toggle.state): #if quit pressed, close window
            run = False
        if play.draw(screen, sfx_toggle.state): #checks if play button is pressed
            transition(screen, clock)
            game_screen(screen, pygame.time.Clock(), menu_screen, sfx_toggle)
       


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False


        pygame.display.flip()


    pygame.quit()


#menu screen function
def menu_screen():
    run = True
    while run: #game loop is initialised
        screen.blit(bg, (0,0))
        screen.blit(menu_banner, (320,50))


        #redraw all buttons to stop them from disappearing with mouse click
        resume.draw(screen, sfx_toggle.state)
        restart.draw(screen, sfx_toggle.state)
        howto.draw(screen, sfx_toggle.state)
        theme.draw(screen, sfx_toggle.state)
   
        sfx_toggle.draw(screen)
        sfx_text = font.render("SFX:", True, text_colour)
        screen.blit(sfx_text, (660,390))


        audio_value = int(audio_slider.get_value()*100) #calculates volume
        pygame.mixer.music.set_volume(audio_slider.get_value())
        audio_slider.draw(screen)
        draw_value(screen, "AUDIO", audio_value, 260, 390) #formats text and volume number


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            #create sliders and toggle
            audio_slider.handle_event(event)
            sfx_toggle.handle_event(event)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if resume.draw(screen, sfx_toggle.state):
                    transition(screen, clock)
                    return #return to game screen
                if restart.draw(screen, sfx_toggle.state):
                    transition(screen, clock)
                    game_screen(screen, pygame.time.Clock(), menu_screen, sfx_toggle) #new game
                if howto.draw(screen, sfx_toggle.state):
                    transition(screen, clock)
                    how_to_play("VIDEOS/how to play.mp4") #play howto vid
                if theme.draw(screen, sfx_toggle.state):
                    transition(screen, clock)
                    change_theme_screen("VIDEOS/change theme.mp4") #play themes vid


       
       
        pygame.display.flip()


    pygame.quit()


def how_to_play(video_name):
    player = MediaPlayer(video_name)
    vid_clock = pygame.time.Clock()


    run = True
    while run:
        frame, value = player.get_frame()


        if value == "eof": #checks if video is over
            break


        if frame is not None: #if there is a next frame, show it
            img, t = frame
            img_surface = pygame.image.frombuffer(img.to_bytearray()[0], img.get_size(), "RGB") #creates frame
            screen.blit(img_surface, (0, 0)) #displays video in fullscreen
            pygame.display.update()
        else:
            frame, value = player.get_frame()


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                run = False #ends if player presses anywhere on screen


        vid_clock.tick(30)


    player.close_player() #automatically closes when video ends


def change_theme_screen(video_name):
    player = MediaPlayer(video_name)
    vid_clock = pygame.time.Clock()


    run = True
    while run:
        frame, value = player.get_frame()


        if value == "eof": #checks if video is over
            break


        if frame is not None: #if there is a next frame, show it
            img, t = frame
            img_surface = pygame.image.frombuffer(img.to_bytearray()[0], img.get_size(), "RGB") #creates frame
            screen.blit(img_surface, (0, 0)) #displays video in fullscreen
            pygame.display.update()


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                run = False #ends if player presses anywhere on screen


        vid_clock.tick(30)


    player.close_player() #automatically closes when video ends






home_screen() #calling on the home screen which the game initially opens to