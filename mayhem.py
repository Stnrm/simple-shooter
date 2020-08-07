""" 
Mayhem game 
Author: Steinar Minde
"""

import pygame
from config import *
from pygame import Vector2
import os
import random

# Assets
game_folder = os.path.dirname(__file__)
images = os.path.join(game_folder, "image")

# Screen surface
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Mayhem Clone')

# Loading images
spaceship = pygame.transform.scale(pygame.image.load(os.path.join(images, "ship.png")), [55,75]).convert_alpha()
spaceship2 = pygame.transform.scale(pygame.image.load(os.path.join(images, "ship2.png")), [55,75]).convert_alpha()
barrel = pygame.transform.scale(pygame.image.load(os.path.join(images, "barrel.png")), [50,60]).convert_alpha()
platform = pygame.transform.scale(pygame.image.load(os.path.join(images, "platform.png")), [300,60]).convert_alpha()
bg = pygame.transform.scale(pygame.image.load(os.path.join(images, "bg.jpg")), [SCREEN_WIDTH, SCREEN_HEIGHT]).convert_alpha()

clock = pygame.time.Clock()
pygame.font.init()
pygame.init()

class Ship(pygame.sprite.Sprite):
    "Class for spaceships"
    def __init__(self, posx, posy, image):
        super().__init__()
        self.image = image
        self.original = self.image
        self.rect = self.image.get_rect()
       
        self.pos = Vector2(posx, posy)
        self.vel = Vector2(0, 0)
        self.gravity = Vector2(0, 0.1)

        self.radius = 27
        self.fuel = FUEL
        self.rot = 0

    def collision(self):
        """ Method for spaceship collision with walls """
        if self.pos.x > SCREEN_WIDTH - self.rect.height:
            self.vel.x = -3
        if self.pos.y > SCREEN_HEIGHT - self.rect.height / 2:
            self.vel.y = -3
        if self.pos.x < 0 + self.rect.height:
            self.vel.x = 3
        if self.pos.y < 0 + self.rect.height:
            self.vel.y = 3

    def update(self, screen):
        """ Update method for the spaceship position and rotation """ 
        self.collision()

        # Rotation, rotate original picture, update new
        self.rot = self.rot % 360
        self.image = pygame.transform.rotate(self.original, self.rot)
        self.rect = self.image.get_rect()

        # Update pos based on variable changes
        self.gravity += self.vel * PLAYER_GRAVITY
        self.vel = self.gravity
        self.pos += self.vel + self.gravity
        self.rect.center = self.pos

    def shoot(self, all_sprites, bullets):
        """ Method for shooting bullets """
        # -self.rot or selse it rotates wrong way
        direction = Vector2(1.5, 0).rotate(-self.rot + 270)
        bullet = Bullet(self.pos, direction)
        all_sprites.add(bullet)
        bullets.add(bullet)

class Bullet(pygame.sprite.Sprite):
    """ Class for bullets """
    def __init__(self, pos, dir):
        super().__init__()
        self.image = pygame.Surface((15, 15))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        
        # Pos is spaceship position 
        self.pos = Vector2(pos)
        self.rect.center = pos
        
        # Dir is the direction spaceship is pointing + 20(speed)
        self.vel = dir * 20

    def update(self, screen):
        """ Movement method for bullets """
        self.pos += self.vel 
        self.rect.center = self.pos

class FuelBarrel(pygame.sprite.Sprite):
    """ Class for fuel barrels """
    def __init__(self):
        super().__init__()
        self.image = barrel
        self.rect = self.image.get_rect()
        self.rect.center = Vector2(random.randint(self.rect.width, (SCREEN_WIDTH - self.rect.width)), random.randint(self.rect.height, (SCREEN_HEIGHT - self.rect.height)))

    def refuel(self, ship):
        """ Refuel function if spaceship collides with barrel """
        if ship.fuel < 1000:
            ship.fuel += 200

class Obstacle(pygame.sprite.Sprite):
    """ Platform obstacle class """
    def __init__(self):
        super().__init__()
        self.image = platform
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH / 2, 700)

class Player(object):
    """ Class for players """
    def __init__(self, players):
        """ Initialize players """
        self.players = players
        if self.players == 0:  
            self.spaceship = Ship(SCREEN_WIDTH /4, 200, spaceship)
        if self.players == 1:
            self.spaceship = Ship(SCREEN_WIDTH / 1.5, 200, spaceship2)
        self.fuel = 500
        self.score = 0

    def fuel_text(self, posx, posy, player):
        """ Method for placing text on screen """
        myfont = pygame.font.SysFont('Helvetica MS', 50)
        # PlayerOne's score and fuel text
        if player == 0:
            fueltext = myfont.render("Fuel P1: " + str(self.fuel), True, (RED))
            scoretext = myfont.render("score P1: " + str(self.score), True, (RED))

            text_width = fueltext.get_width()
            text_height = fueltext.get_height()

            screen.blit(fueltext,(posx + 10, posy + text_height))
            screen.blit(scoretext,(posx, posy + (text_height * 2)))

        # PlayerTwo's score and fuel text
        if player == 1:
            fueltext = myfont.render("Fuel P2: " + str(self.fuel), True, (WHITE))
            scoretext = myfont.render("score P2: " + str(self.score), True, (WHITE))

            text_width = fueltext.get_width()
            text_height = fueltext.get_height()

            screen.blit(fueltext,(posx - text_width - 20, text_height))
            screen.blit(scoretext,(posx - text_width - 40, (text_height * 2)))

    def forward(self):
        """ Spaceship thrust """
        self.spaceship.gravity = Vector2(4, 0).rotate(-self.spaceship.rot + 270)
        self.fuel -= 1
        
    def backward(self):
        """ Spaceship backwards movement at half speed """
        self.spaceship.gravity = -Vector2(2, 0).rotate(-self.spaceship.rot + 270)
        self.fuel -= 1

    def rotate_right(self):
        """ Rotate right """
        self.spaceship.rot -= ROTATE_SPEED

    def rotate_left(self):
        """ Rotate left """
        self.spaceship.rot += ROTATE_SPEED
    
    def gravity(self):
        """ Constant gravity on spaceship """
        self.spaceship.gravity += Vector2(0, 0.1)

class Mayhem(object):
    """ Main game class """
    def __init__(self):
        self.running = True
        self.game_over = False

        #Set up groups
        self.all_sprites = pygame.sprite.Group()
        self.barrels = pygame.sprite.Group()
        self.bulletsP1 = pygame.sprite.Group()
        self.bulletsP2 = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        self.players = pygame.sprite.Group()
        
        # Create objects
        self.playerOne = Player(0)
        self.playerTwo = Player(1)
        self.barrel = FuelBarrel()
        self.obstacle = Obstacle()

        # Add objects to groups
        self.players.add(self.playerOne.spaceship, self.playerTwo.spaceship)
        self.obstacles.add(self.obstacle)
        self.barrels.add(self.barrel)
        self.all_sprites.add(self.playerTwo.spaceship, self.playerOne.spaceship, self.barrel, self.obstacle)

    def events(self):
        """ Event method, all things 'event' """

        # Event handler
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                # Exit game by pressing ESCAPE
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                # Shooting for playerOne
                if event.key == pygame.K_SPACE:
                    self.playerOne.spaceship.shoot(self.all_sprites, self.bulletsP1)
                # Shooting for playerTwo
                if event.key == pygame.K_g:
                    self.playerTwo.spaceship.shoot(self.all_sprites, self.bulletsP2)
                # Restarte game
                if event.key == pygame.K_r:
                    self.__init__()
        
        # Game-over text
        if self.game_over == True:
            myfont1 = pygame.font.SysFont('Helvetica MS', 150)
            myfont2 = pygame.font.SysFont('Helvetica MS', 50)
            gameover = myfont1.render("GAME OVER", True, (BLUE))
            retry = myfont2.render("Press 'R' to restart", True, (BLUE))
            text_width = gameover.get_width()
            text_height = gameover.get_height()
        
            screen.blit(gameover,(SCREEN_WIDTH /2 - text_width / 2, SCREEN_HEIGHT /2))
            screen.blit(retry, (SCREEN_WIDTH /2 - text_width / 2, 550))
        
        # Key handler for spaceships
        keys = pygame.key.get_pressed()
        
        # MOVEMENT FOR PLAYER ONE
        if keys[pygame.K_UP] and self.playerOne.fuel > 0:
            self.playerOne.forward()
        if keys[pygame.K_DOWN] and self.playerOne.fuel > 0:
            self.playerOne.backward()   
        if keys[pygame.K_RIGHT]:
            self.playerOne.rotate_right()
        if keys[pygame.K_LEFT]:
            self.playerOne.rotate_left()

        # MOVEMENT FOR PLAYER TWO
        if keys[pygame.K_w] and self.playerTwo.fuel > 0:
            self.playerTwo.forward()
        if keys[pygame.K_s] and self.playerTwo.fuel > 0:
            self.playerTwo.backward()
        if keys[pygame.K_d]:
            self.playerTwo.rotate_right()
        if keys[pygame.K_a]:
            self.playerTwo.rotate_left()

    def collision_detection(self):
        """ Collision detection between sprites, groups """
        #Checks if player one got the fuel barrel, respawn barrel
        fuel_hit1 = pygame.sprite.spritecollide(self.playerOne.spaceship, self.barrels, True)
        for hit in fuel_hit1:
            self.barrel = FuelBarrel()
            self.all_sprites.add(self.barrel)
            self.barrels.add(self.barrel)
            self.barrel.refuel(self.playerOne)

        #Checks if player two got the fuel barrel, respawn barrel
        fuel_hit2 = pygame.sprite.spritecollide(self.playerTwo.spaceship, self.barrels, True)
        for hit in fuel_hit2:
            self.barrel = FuelBarrel()
            self.all_sprites.add(self.barrel)
            self.barrels.add(self.barrel)
            self.barrel.refuel(self.playerTwo)

        # Checks if Player one has been hit by bullet
        bullet_hitOne = pygame.sprite.spritecollide(self.playerOne.spaceship, self.bulletsP2, True)
        if bullet_hitOne:
            self.playerTwo.score += 10
            if self.playerOne.score >= 10:
                self.playerOne.score -= 10
            if self.playerTwo.score >= 100:
                self.all_sprites.remove(self.playerOne.spaceship)
                self.game_over = True

        # Checks if Player two has been hit by bullet
        bullet_hitTwo = pygame.sprite.spritecollide(self.playerTwo.spaceship, self.bulletsP1, True)
        if bullet_hitTwo:
            self.playerOne.score += 10
            if self.playerTwo.score >= 10:
                self.playerTwo.score -= 10
            if self.playerOne.score >= 100:
                self.all_sprites.remove(self.playerTwo.spaceship)
                self.game_over = True

        # If bullets hit platform, then remove bullets   
        pygame.sprite.spritecollide(self.obstacle, self.bulletsP1, True)
        pygame.sprite.spritecollide(self.obstacle, self.bulletsP2, True)

        # Checks for spaceship collision
        spaceship_collide = pygame.sprite.collide_circle(self.playerOne.spaceship, self.playerTwo.spaceship)
        if spaceship_collide:
            vel = Vector2(1, 1)
            if self.playerOne.score > 0:
                self.playerOne.score -= 5
            if self.playerTwo.score > 0:
                self.playerTwo.score -= 5
            self.playerOne.spaceship.vel -= vel.rotate(-self.playerTwo.spaceship.rot + 270)
            self.playerTwo.spaceship.vel += vel.rotate(-self.playerOne.spaceship.rot + 270)

        # Checks for obstacle and spaceship collision
        if pygame.sprite.spritecollide(self.playerOne.spaceship, self.obstacles, False):
            vel = Vector2(1, 1)
            self.playerOne.spaceship.vel -= vel.rotate(-self.playerOne.spaceship.rot + 270)
        if pygame.sprite.spritecollide(self.playerTwo.spaceship, self.obstacles, False):
            vel = Vector2(1, 1)
            self.playerTwo.spaceship.vel -= vel.rotate(-self.playerTwo.spaceship.rot + 270)
         
    def update(self):
        """" Update method for game """
        self.events()
        self.playerTwo.gravity()
        self.playerOne.gravity()

        self.playerOne.fuel_text(10, 0, 0)
        self.playerTwo.fuel_text(SCREEN_WIDTH, 0, 1)

        self.collision_detection()
        self.all_sprites.draw(screen)
        
        self.all_sprites.update(screen)

    def run(self):
        """ Main game loop """
        while self.running:
            clock.tick(FPS)
            # Screen background
            screen.blit(bg, (0, 0))

            self.update()
  
            # Update screen
            pygame.display.flip()
            
        pygame.quit()

if __name__ == '__main__':
    run = Mayhem()
    run.run()