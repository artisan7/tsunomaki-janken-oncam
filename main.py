import sys, pygame, random, math, enum
from jankencam import JankenCam

# INITIALIZE PYGAME
pygame.mixer.pre_init(size=-8)
pygame.init()

# ADD FRAMERATE CAP
fps = 60
clock = pygame.time.Clock()
clock.tick(fps)

# CUSTOM EVENTS CREATION
bgm_ended_event = pygame.USEREVENT + 1
timer_event = pygame.USEREVENT + 2
flip_event = pygame.USEREVENT + 3

# SETUP MAIN DISPLAY SCREEN
screen_size = width, height = 540, 960 #width, height
black = 0,0,0
screen = pygame.display.set_mode(screen_size)
pygame.display.set_caption("Tsunomaki Janken")

# game states
class State(enum.Enum):
    INACTIVE = 1
    PREGAME = 2
    INGAME = 3
    POSTGAME = 4

class PlayingHand(enum.Enum):
    INVALID = -1
    ROCK = 0
    PAPER = 1
    SCISSORS = 2

class Result(enum.Enum):
    INVALID = -1
    WIN = 0
    DRAW = 1
    LOSE = 2

# initialize variables needed for the game

bgm_channel = pygame.mixer.Channel(0)

bgms = []

hand_images = []
bg_image = pygame.transform.scale( pygame.image.load('assets/bg.png'), screen_size )
watame_image = pygame.transform.scale( pygame.image.load('assets/watambe.png'), (512, 512) )
watame_flipped_image = pygame.transform.scale( pygame.image.load('assets/watambe_flip.png'), (512, 512) )
win_image = pygame.transform.scale( pygame.image.load('assets/kachi.png'), screen_size )
lose_image = pygame.transform.scale( pygame.image.load('assets/make.png'), screen_size )

black_overlay = pygame.Surface(screen_size)
black_overlay.fill(black)
overlay_opacity = 0
max_overlay_opacity = 200
result_image_start_center = -200
result_image_center = 0

active_sprite_idx = 0
watame_flip = False
playing_hand = PlayingHand.INVALID
state = State.INACTIVE
result = Result.INVALID
player = None

# initialize assets
bgms.append(pygame.mixer.Sound('assets/jan.wav'))
bgms.append(pygame.mixer.Sound('assets/ken.wav'))
bgms.append(pygame.mixer.Sound('assets/pon.wav'))

bgm_channel.set_endevent(bgm_ended_event)

hand_images.append(pygame.image.load('assets/gu32.png'))
hand_images.append(pygame.image.load('assets/pa32.png'))
hand_images.append(pygame.image.load('assets/ch32.png'))


# selects the hand that is shown in the display
def update_hand():
    global active_sprite_idx

    if state == State.INGAME: #shuffles between images
        active_sprite_idx = (active_sprite_idx + 1) % 3
    elif state == State.POSTGAME: #shows the playing hand of COM
        active_sprite_idx = playing_hand.value

# draw call
def draw(surface):
    global watame_image

    # draw background
    rect = bg_image.get_rect(center=(width/2, height/2))
    surface.blit(bg_image, rect)

    # draw watame
    
    if watame_flip:
        rect = watame_flipped_image.get_rect(center=(width/2, height*3/4))
        surface.blit(watame_flipped_image, rect)
    else:
        rect = watame_image.get_rect(center=(width/2, height*3/4))
        surface.blit(watame_image, rect)
        
    # draw hand
    img = hand_images[active_sprite_idx]
    img = pygame.transform.scale(img, (256, 256))

    rect = img.get_rect(center=(width/2, height/4))

    surface.blit(img, rect)

    # draw results related assets
    if state == State.POSTGAME or (state == State.INACTIVE and result != Result.INVALID):
        #draw overlay
        rect = black_overlay.get_rect()
        surface.blit(black_overlay, rect)

        #draw result image
        if result == Result.WIN:
            rect = win_image.get_rect(center=(width/2, result_image_center))
            surface.blit(win_image, rect)
        else:
            rect = lose_image.get_rect(center=(width/2, result_image_center))
            surface.blit(lose_image, rect)


# flips watambe
def flip_watame():
    global watame_flip
    watame_flip = not watame_flip

# returns playing hand as string
def get_playing_hand():
    return playing_hand.name

# triggered when a music buffer is ended
def music_ended():
    global state

    if state == State.PREGAME:
        set_state(State.INGAME)
    elif state == State.INGAME:
        set_state(State.POSTGAME)
    elif state == State.POSTGAME:
        set_state(State.INACTIVE)

# evaluate player hand vs ai hand
def evaluate_play():
    p1 = player.play
    p2 = playing_hand.value

    if p1 == -1:
        return Result.INVALID
    elif (p1+2)%3 == p2:
        return Result.WIN
    elif (p1+1)%3 == p2:
        return Result.LOSE
    elif p1 == p2:
        return Result.DRAW

# updates the state
def set_state(s):
    global state, playing_hand, player, result, overlay_opacity, result_image_center
    state = s

    print("State updated to", state)

    if state == State.PREGAME:
        random.seed()
        playing_hand = PlayingHand( math.floor(random.random()*3) )

        bgm_channel.play(bgms[0])
        bgm_channel.set_volume(0.3)

        player = JankenCam(debugMode=True)
        
        pygame.time.set_timer(timer_event, 100)

    elif state == State.INGAME:
        bgm_channel.play(bgms[1])
        bgm_channel.set_volume(0.3)
        pygame.time.set_timer(flip_event, 600)

    elif state == State.POSTGAME:
        bgm_channel.play(bgms[2])
        bgm_channel.set_volume(0.3)
        pygame.time.set_timer(timer_event, 0)
        pygame.time.set_timer(flip_event, 0)
        player.capture(True)

        result = evaluate_play()

        update_hand()

    elif state == State.INACTIVE:
        overlay_opacity = 0
        result_image_center = result_image_start_center
        if result == Result.INVALID:
            print("INVALID MATCH")
        else:
            print(f"MATH RESULT: {result.name}")

def update_results_screen():
    global overlay_opacity, result_image_center

    overlay_opacity += (max_overlay_opacity) / fps
    overlay_opacity = min(overlay_opacity, max_overlay_opacity)
    black_overlay.set_alpha(overlay_opacity)
    
    result_image_center += 200 / fps
    result_image_center = min(result_image_center, height/2)

def update():
    if state == State.INGAME:
        player.capture(False)
    elif state == State.POSTGAME:
        update_results_screen()

# GAME LOOP
while True:
    for event in pygame.event.get(): #EVENT HANDLING
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            left, _, _ = pygame.mouse.get_pressed()
            if left and state == State.INACTIVE:
                set_state(State.PREGAME)
        elif event.type == bgm_ended_event:
            music_ended()
        elif event.type == timer_event:
            update_hand()
        elif event.type == flip_event:
            flip_watame()
    #print(state)
    update()

    screen.fill(black)
    draw(screen)

    pygame.display.flip()