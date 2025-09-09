import asyncio
import pygame
import sys
import random

pygame.init()

# Window setup
infoObject = pygame.display.Info()
windowWidth = infoObject.current_w
windowHeight = infoObject.current_h
screen = pygame.display.set_mode((windowWidth, windowHeight))
dontmove = False
pygame.display.set_caption('Jump Test')
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 32)
dialogue_box = pygame.Surface((windowWidth - 100, 80), pygame.SRCALPHA)
dialogue_box.fill((0, 0, 0, 180))
score = 0
notjumpedyet = True
bg_image = pygame.image.load("grassy.png").convert_alpha()
bg_image = pygame.transform.scale(bg_image, (windowWidth, windowHeight))
player_image = pygame.image.load("puffinpixel.png").convert_alpha()
penguin_image = pygame.image.load("newpenguinspike.png")

def background(x): 
    screen.blit(x, (0,0))

def make_extra_rect(width_position, height_position, npc_width, npc_height):
    return pygame.Rect(width_position, height_position, npc_width, npc_height)

# Colors
WHITE = (255, 255, 255)
BLUE = (50, 100, 255)
BLACK = (0, 0, 0)
pipe1_visible = True
player_visible = True

# Player setup
player_width, player_height = 50, 50
player_rect = pygame.Rect(
    windowWidth // 2 - player_width // 2,
    windowHeight - player_height,
    player_width,
    player_height
)
player_rect.x += 100
player_rect.y += 100
player_y_velocity = 0

# Physics
gravity = 0.5
jump_force = -12

# Game state
game_started = False
game_over = False
pipe1 = make_extra_rect(750, 500, 50, 500)
pipe2 = make_extra_rect(750, 0, 50, random.randint(200, 400))  # top pipe
laser_rect = make_extra_rect(100, 200, player_width - windowWidth, 50)
laser_visible = False
penguin_rect = make_extra_rect(pipe1.x + 150, random.randint(200, windowHeight - 100), 48, 48)
penguin_visible = True
def reset_game():
    global player_rect, player_y_velocity, score, game_started, game_over, pipe1, bg_image, penguin_rect, penguin_visible
    player_rect.x = windowWidth // 2 - player_width // 2 + 100
    player_rect.y = windowHeight - player_height - 100
    player_y_velocity = 0
    score = 0
    game_started = False
    game_over = False
    pipe1 = make_extra_rect(750, 500, 50, 500)
    pipe2.x = pipe1.x
    # pipe2 size stays the same on reset
    penguin_visible = True
    penguin_rect = make_extra_rect(pipe1.x + 150, 100, 48, 48)


async def main():
    global player_y_velocity, game_started, game_over, score, notjumpedyet, player_visible, pipe1_visible, pipe1, pipe2, laser_visible, laser_rect, penguin_rect, penguin_visible
    running = True
    while running:
        await asyncio.sleep(0)  # required for pygbag
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_x:  # quit with X
                    running = True # removed quitting with x cause it doesn't really matter on web
                elif event.key == pygame.K_r:  # restart with R
                    reset_game()
                    game_started = False
                    score = 0
                elif event.key == pygame.K_SPACE and not dontmove:
                    notjumpedyet = False
                    if not game_started:
                        reset_game()
                        game_started = True  # start gravity
                    player_y_velocity = jump_force

        if not game_over and game_started:
            # Apply gravity
            player_y_velocity += gravity
            player_rect.y += player_y_velocity

            # Move pipes
            if score < 15:

                pipe1.x -= 10
                pipe2.x -= 10
            elif score >= 15:
                pipe1.x -= 15
                pipe2.x -= 15

            # Score logic
            if player_rect.x > pipe1.x and player_rect.x <= pipe1.x + 10:
                score += 1
            if player_rect.x > pipe2.x and player_rect.x <= pipe2.x + 10:
                score += 0  # pipe2 doesn’t give points
            if player_rect.x > pipe1.x and player_rect.x <= pipe1.x + 15 and score >= 15:
                score += 1
            if player_rect.x > pipe2.x and player_rect.x <= pipe2.x + 15 and score >= 15:
                score += 0  # pipe2 doesn’t give points
            # Respawn pipes when off-screen
            if pipe1.right < 0:
                new_height = random.randint(300, 450) 
                pipe1 = make_extra_rect(windowWidth, new_height, 50, 500)
                penguin_rect.y = random.randint(200, windowHeight - 300)
                penguin_visible = True
            if pipe2.right < 0:
                pipe2 = make_extra_rect(windowWidth, 0, 50, random.randint(150, 200))


            # Collision detection
            if pygame.Rect.colliderect(player_rect, pipe1) and pipe1_visible:
                game_over = True
            if pygame.Rect.colliderect(player_rect, pipe2) and pipe1_visible:
                game_over = True
            if pygame.Rect.colliderect(player_rect, penguin_rect) and penguin_visible:
                game_over = True
            # Floor collision
            if player_rect.bottom >= windowHeight:
                player_rect.bottom = windowHeight
                player_y_velocity = 0
                game_over = True

            # Ceiling collision
            if player_rect.top <= 0:
                player_rect.top = 0
                player_y_velocity = 0
                game_over = True

        # Drawing
        background(bg_image)
        falling_player_image = pygame.transform.rotate(player_image, -45)
        text_surface = font.render(f"Score: {score}", True, (0, 0, 0))
        screen.blit(text_surface, (windowWidth - 200, windowHeight - 600))
        if player_visible and player_y_velocity <= 0:
            screen.blit(player_image, player_rect)
        elif player_visible and player_y_velocity > 0:
            screen.blit(falling_player_image, player_rect)

        if keys[pygame.K_z]:
            laser_visible = True
        else:
            laser_visible = False
        if laser_visible:
            # Make the laser come out from the right side of the puffin
            laser_rect.x = player_rect.right  # right edge of the puffin
            laser_rect.y = player_rect.y + player_height // 2 - 5  # centered vertically on puffin
            laser_rect.width = 100  # how long the laser is
            laser_rect.height = 10   # thickness of the laser
            pygame.draw.rect(screen, (255, 0, 0), laser_rect)

        if penguin_visible:
            penguin_rect.x = pipe1.x + 150
            screen.blit(penguin_image, penguin_rect)
        if penguin_visible and pygame.Rect.colliderect(penguin_rect, laser_rect) and laser_visible:
            penguin_visible = False
            score += 1

        if pipe1_visible:
            pygame.draw.rect(screen, (255, 0, 0), pipe1)
        if pipe1_visible:
            pygame.draw.rect(screen, (255, 0, 0), pipe2)

        if not game_started and notjumpedyet:
            jump_surface = font.render("Press Space to Start Jumping!  Press Z to use your laser vision.", True, (0, 0, 0))
            screen.blit(jump_surface, (windowWidth // 2 - 500, windowHeight // 2 - 50))
            jump_surface2 = font.render("Hit penguins to get extra score!", True, (0,0,0))
            screen.blit(jump_surface2, (windowWidth // 2 - 500, windowHeight // 2 + 100))
        if game_over:
            screen.fill(BLACK)
            text_surface = font.render("You Died - Press R to Restart", True, (255, 255, 255))
            screen.blit(text_surface, (windowWidth - 850, windowHeight - 350))
            textsurface = font.render(f"Your Final Score was: {score}!", True, (255, 255, 255))
            screen.blit(textsurface, (windowWidth - 835, windowHeight - 300))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

asyncio.run(main())
