import cv2
import keyboard
import mediapipe as mp
import time
import random
import pygame
from pygame import  mixer
from pygame.locals import *

pygame.mixer.pre_init(44100,-16,2,512)
mixer.init()
pygame.init()

#define fps
clock = pygame.time.Clock()
fps = 10

screen_width = 600
screen_height = 800
screen = pygame.display.set_mode((screen_width,screen_height))
pygame.display.set_caption("Space Invaders")


#define fonts
font30 = pygame.font.SysFont('Constantia', 30)
font40 = pygame.font.SysFont('Constantia', 40)

#load sounds
explosion_fx = pygame.mixer.Sound("img/explosion.wav")
explosion_fx.set_volume(0.1)

explosion2_fx = pygame.mixer.Sound("img/explosion2.wav")
explosion_fx.set_volume(0.1)

laser_fx = pygame.mixer.Sound("img/laser.wav")
laser_fx.set_volume(0.1)

#define game variables
rows = 5
cols = 5
alien_cooldown = 1000#bullet cooldown in milliseconds
last_alien_shot = pygame.time.get_ticks()
countdown = 3
last_count = pygame.time.get_ticks()
game_over = 0 #0 means no game over, 1 means player won, -1 means player lost


#define colors
red = (255,0,0)
green = (0,255,0)
white = (255,255,255)

#load image
bg = pygame.image.load("img/bg.png")

def draw_bg():
    screen.blit(bg, (0, 0))

# define function for creating text
def draw_text(text,font,text_col,x,y):
    img = font.render(text,True,text_col)
    screen.blit(img, (x,y))


#create spaceship class
class Spaceship(pygame.sprite.Sprite):
    def __init__(self,x,y,health):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/spaceship.png")
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.health_start = health
        self.health_remaining = health
        self.last_shot = pygame.time.get_ticks()
    def update(self):
        #set movement speed
        speed = 8
        cooldown = 1000 #milliseconds
        game_over = 0
        #get key press

        # if key[pygame.K_RIGHT] and self.rect.right<screen_width:
        #     self.rect.x += speed

        #record current time
        time_now = pygame.time.get_ticks()

        #update mask
        self.mask = pygame.mask.from_surface(self.image)

        #shoot
        success, img = cap.read()
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(imgRGB)
        # print(results.multi_hand_landmarks)

        if results.multi_hand_landmarks:
            for handLms in results.multi_hand_landmarks:
                h,w,c = img.shape
                x_0 = int(handLms.landmark[4].x * w)
                y_0 = int(handLms.landmark[4].y * h)
                x_1 = int(handLms.landmark[8].x * w)
                y_1 = int(handLms.landmark[8].y * h)
                x_2 = int(handLms.landmark[12].x * w)
                y_2 = int(handLms.landmark[12].y * h)
                x_3 = int(handLms.landmark[16].x * w)
                y_3 = int(handLms.landmark[16].y * h)
                print(x_0,x_1,x_2,y_0,y_1,y_2)
                print(abs(x_1-x_2)/x_1,abs(x_2-x_3)/x_2,abs(y_0-y_1),abs(y_1-y_2))
                if abs(x_1-x_2)/x_1>0.15 and self.rect.left > 0:
                    self.rect.x -= speed
                elif abs(x_2-x_3)/x_2>0.15 and self.rect.right <screen_width:
                    self.rect.x += speed

                if abs(x_0-x_1)/x_0 >0.1 and time_now - self.last_shot > cooldown:
                    laser_fx.play()
                    bullet = Bullets(self.rect.centerx, self.rect.top)
                    bullet_group.add(bullet)
                    self.last_shot = time_now
                # for id, lm in enumerate(handLms.landmark):
                #     # print(id,lm)
                #     h, w, c = img.shape
                #     cx, cy = int(lm.x * w), int(lm.y * h)
                #     # print(id,cx,cy)
                #     if id==4:
                #         if self.rect.left > 0:
                #             self.rect.x -= speed
                #     if id == 8:
                #         cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)

                #     #     print(id,cx,cy)
                #     # if id == 12:
                #     #     cv2.circle(img,(cx,cy),15,(255,0,255),cv2.FILLED)
                #     #     print(id,cx,cy)
                #     if id==4:
                #         cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)
                #         print(cx)

        #draw health bar
        pygame.draw.rect(screen, red, (self.rect.x,(self.rect.bottom+10), self.rect.width,15))
        if self.health_remaining > 0 :
            pygame.draw.rect(screen, green, (self.rect.x, (self.rect.bottom + 10), int(self.rect.width*(self.health_remaining/self.health_start)), 15))
        elif self.health_remaining <=0:
            explosion = Explosion(self.rect.centerx,self.rect.centery,3)
            explosion_group.add(explosion)
            self.kill()
            game_over = -1
        return game_over
class Bullets(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/bullet.png")
        self.rect = self.image.get_rect()
        self.rect.center = [x,y]

    def update(self):
        self.rect.y -= 5
        if self.rect.bottom < 0:
            self.kill()
        if pygame.sprite.spritecollide(self,aliens_group,True):
            self.kill()
            explosion_fx.play()
            explosion = Explosion(self.rect.centerx,self.rect.centery,2)
            explosion_group.add(explosion)

class Aliens(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/alien"+str(random.randint(1,5))+".png")
        self.rect = self.image.get_rect()
        self.rect.center = [x,y]
        self.move_counter = 0
        self.move_direction = 1
    def update(self):
        self.rect.x += self.move_direction
        self.move_counter += 1
        if abs(self.move_counter) > 75:
            self.move_direction *=-1
            self.move_counter *= self.move_direction

class Alien_Bullets(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/alien_bullet.png")
        self.rect = self.image.get_rect()
        self.rect.center = [x,y]

    def update(self):
        self.rect.y += 2
        if self.rect.top > screen_height:
            self.kill()
        if pygame.sprite.spritecollide(self,spaceship_group,False,pygame.sprite.collide_mask):
            #reduce spaceship health
            spaceship.health_remaining -= 1
            self.kill()
            explosion2_fx.play()
            explosion = Explosion(self.rect.centerx,self.rect.centery,1)
            explosion_group.add(explosion)

#create Explosion class
class Explosion(pygame.sprite.Sprite):
    def __init__(self,x,y,size):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range(1,6):
            img = pygame.image.load(f"img/exp{num}.png")
            if size == 1:
                img = pygame.transform.scale(img,(20,20))
            if size == 2:
                img = pygame.transform.scale(img,(40,40))
            if size == 3:
                img = pygame.transform.scale(img,(160,160))
            self.images.append(img)
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x,y]
        self.counter = 0
    def update(self):
        explosion_speed = 3
        #update explosion animation
        self.counter += 1
        if self.counter >= explosion_speed and self.index < len(self.images)-1:
            self.counter = 0
            self.index += 1
            self.image = self.images[self.index]
        #if the animation is complete, delete explosion
        if self.index >= len(self.images)-1 and self.counter >= explosion_speed:
            self.kill()
#create sprite groups
spaceship_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
aliens_group = pygame.sprite.Group()
alien_bullet_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()

def create_aliens():
    #generate aliens
    for row in range(rows):
        for item in range(cols):
            alien = Aliens(100+item*100,100+row*70)
            aliens_group.add(alien)

create_aliens()


#create player
spaceship = Spaceship(int(screen_width/2),screen_height-100,3)
spaceship_group.add(spaceship)

run = True


cap = cv2.VideoCapture(0)
# address = "https://192.168.1.14:8080/video"
# cap.open(address)

mpHands = mp.solutions.hands
hands = mpHands.Hands()
mpDraw = mp.solutions.drawing_utils

pTime = 0
cTime = 0

while run:
    success, img = cap.read()
    # print(results.multi_hand_landmarks)
    # cTime = time.time()
    # fps = 1 / (cTime - pTime)
    # pTime = cTime
    # cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)

    # cv2.imshow("Image", img)
    # cv2.waitKey(1)

    clock.tick(fps)
    # draw background
    draw_bg()

    if countdown == 0:
        # create random alien bullets
        # record current time
        time_now = pygame.time.get_ticks()
        # shoot
        if time_now - last_alien_shot > alien_cooldown and len(alien_bullet_group) < 5 and len(aliens_group) > 0:
            attacking_alien = random.choice(aliens_group.sprites())
            alien_bullet = Alien_Bullets(attacking_alien.rect.centerx, attacking_alien.rect.bottom)
            alien_bullet_group.add(alien_bullet)
            last_alien_shot = time_now

        # check if all the aliens have been killed
        if len(aliens_group) == 0:
            game_over = 1

        # update spaceship

        if game_over == 0:
            game_over = spaceship.update()
            # update sprite groups
            bullet_group.update()
            aliens_group.update()
            alien_bullet_group.update()
        else:
            if game_over == -1:
                draw_text('GAME OVER!', font40, white, int(screen_width / 2 - 100), int(screen_height / 2 + 50))
            if game_over == 1:
                draw_text('YOU WIN!', font40, white, int(screen_width / 2 - 100), int(screen_height / 2 + 50))
    if countdown > 0:
        draw_text('GET READY!', font40, white, int(screen_width / 2 - 110), int(screen_height / 2 + 50))
        draw_text(str(countdown), font40, white, int(screen_width / 2 - 10), int(screen_height / 2 + 100))
        count_timer = pygame.time.get_ticks()
        if count_timer - last_count > 1000:
            countdown -= 1
            last_count = count_timer

    # update explosion group
    explosion_group.update()

    # draw sprite groups
    spaceship_group.draw(screen)
    bullet_group.draw(screen)
    aliens_group.draw(screen)
    alien_bullet_group.draw(screen)
    explosion_group.draw(screen)

    # event handlers
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()

pygame.quit()
