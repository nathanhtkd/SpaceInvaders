import pygame
import os
import random

pygame.init()
pygame.font.init() # initialize font 

# set pygame window
width = 750
height = 750
window = pygame.display.set_mode((width, height))
pygame.display.set_caption("Space Shooter")

# Load Ships
redShip = pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png"))
greenShip = pygame.image.load(os.path.join("assets", "pixel_ship_green_small.png"))
blueShip = pygame.image.load(os.path.join("assets", "pixel_ship_blue_small.png"))

# Load Player
yellowShip = pygame.image.load(os.path.join("assets", "testship.png"))

#Load Lasers
redLaser = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
greenLaser = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
blueLaser = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
yellowLaser = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))

# Background
bg = pygame.transform.scale(pygame.image.load(os.path.join("assets", "spacebackground.gif")), (width, height))

# Banner
banner = pygame.transform.scale(pygame.image.load(os.path.join("assets", "banner.png")), ((350, 350)))

# arcade logo
arcade = pygame.transform.scale(pygame.image.load(os.path.join("assets", "arcade.png")), (350, 263))

class Laser:
    def __init__ (self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)
        
    def drawLaser(self, window):
        window.blit(self.img, (self.x, self.y))
        
    def move(self, vel):
        self.y += vel
        
    def offScreen(self, height):
        return not(self.y <= height and self.y >= 0)
    
    def collision(self, obj):
        return collide(obj, self)
    
    
# abstract Ship class, inherit later
class Ship:
    cooldownValue = 30
    def __init__(self, x, y, health = 100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.coolDownCounter = 0    
        
    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.drawLaser(window)
        
    def moveLasers(self, vel, obj):
        # need to check collision
        self.cooldown()
        for laser in self.lasers:
            # move laser based off velocity
            laser.move(vel)
            if laser.offScreen(height):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)
                
    def cooldown(self):
        if self.coolDownCounter >= self.cooldownValue:
            self.coolDownCounter = 0
        elif self.coolDownCounter > 0:
            self.coolDownCounter += 1
            
    def shoot(self):
        if self.coolDownCounter == 0:
           laser = Laser(self.x, self.y, self.laser_img)
           self.lasers.append(laser)
           self.coolDownCounter = 1

    def getWidth(self):
        return self.ship_img.get_width()
    
    def getHeight(self):
        return self.ship_img.get_height()
    
            
# Player ship will inherit from Ship
class Player(Ship):
    def __init__(self, x, y, health = 100):
        super().__init__(x, y, health)
        # Player ship is yellow 
        self.ship_img = yellowShip
        self.laser_img = yellowLaser
        # lets us do pixel perfect collisions
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.maxHealth = health
    # if laser collides with enemy, remove enemy and laser
    def moveLasers(self, vel, objs):
        # need to check collision
        self.cooldown()
        for laser in self.lasers:
            # move laser based off velocity
            laser.move(vel)
            if laser.offScreen(height):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        if laser in self.lasers: 
                            self.lasers.remove(laser)


    def draw(self, window):
        super().draw(window)
        self.healthbar(window)
        

    def healthbar(self, window):
        # generate healthhbar
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health / self.maxHealth), 10))
        
class Enemy(Ship):
    colorMap = {
                "red" : (redShip, redLaser),
                "green" : (greenShip, greenLaser),
                "blue" : (blueShip, blueLaser)
    }
    
    def __init__(self, x, y, color, health = 100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.colorMap[color]
        self.mask = pygame.mask.from_surface(self.ship_img)
        
    def move(self, vel):
        # enemy ship only moves down
        self.y += vel
        
    def shoot(self):
        if self.coolDownCounter == 0:
            laser = Laser(self.x - 18, self.y, self.laser_img)
            self.lasers.append(laser)
            self.coolDownCounter = 1
        
def collide(obj1, obj2):
    offsetX = obj2.x - obj1.x
    offsetY = obj2.y - obj1.y   
    # if masks are overlapping based off offset, return true
    return obj1.mask.overlap(obj2.mask, (offsetX, offsetY)) != None    
        
        
def main():
    run = True
    lost = False
    lostCount = 0
    fps = 80
    level = 0
    lives = 5
    main_font = pygame.font.SysFont("calibri", 50)
    lost_font = pygame.font.SysFont("calibri", 60)
    
    enemies = []
    waveLength = 5
    enemyVelocity = 1
    laserVelocity = 5
    
    playerVelocity = 5
    
    player = Player(320, 630)
    
    clock = pygame.time.Clock()
    
    def redraw_window():
        # redraws surface on pygame window
        window.blit(bg, ((0,0)))
        # draw text (lives, level)
        livesLabel = main_font.render(f"Lives: {lives}", 1, ((255,255,255)))
        levelLabel = main_font.render(f"Level: {level}", 1, ((255,255,255)))
        window.blit(livesLabel, (10,10))
        window.blit(levelLabel, (width - levelLabel.get_width() - 10, 10))
        
        for enemy in enemies:
            enemy.draw(window)
        
        player.draw(window)
        
        if lost:
            lostLabel = lost_font.render("You lost!", 1, (255,255,255))
            window.blit(lostLabel, (width / 2 - lostLabel.get_width() / 2, 350))
        
        pygame.display.update()
        
    
    while run:
        # tick clock on 60 frames per second
        clock.tick(fps)
        redraw_window()
        
        if lives <= 0 or player.health <= 0:
            lost = True
            lostCount += 1
            
        if lost:
            if lostCount > fps * 5:
                run = False
                pygame.quit()
            else: 
                continue
        
        # increase difficulty
        if len(enemies) == 0:
            level += 1
            # add 5 more enemies in the next level
            waveLength += 5
            for i in range(waveLength):
                # make enemies come down at different times after spawn
                enemy = Enemy(random.randrange(50, width - 100), random.randrange(-1500, -100), random.choice(["red", "blue", "green"]))
                enemies.append(enemy)
                
                
        # check for events (pressing a key)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x - playerVelocity > 0: # left
            player.x -= playerVelocity
        if keys[pygame.K_d] and player.x + playerVelocity + player.getWidth() < width: # right
            player.x += playerVelocity
        if keys[pygame.K_w] and player.y - playerVelocity > 0: # up
            player.y -= playerVelocity
        if keys[pygame.K_s] and player.y + playerVelocity + player.getHeight() + 15 < height: # down
            player.y += playerVelocity
            # player shoot
        if keys[pygame.K_SPACE]:
            player.shoot()
        if keys[pygame.K_r]:
            mainMenu()
        
        for enemy in enemies[:]:
            enemy.move(enemyVelocity)
            enemy.moveLasers(laserVelocity, player)
            
            # random lasers from enemy
            if random.randrange(0, 3 * 60) == 1:
                enemy.shoot()
            
            # if enemy collides with player
            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
            # if enemy gets off the screen
            elif enemy.y + enemy.getHeight() > height:
                lives -= 1 
                enemies.remove(enemy)
                
                
        player.moveLasers(-laserVelocity, enemies)
        

def mainMenu():
    run = True
    titleFont = pygame.font.SysFont("calibri", 40)
    
    while run:
        window.blit(bg, (0,0))
        window.blit(banner, (200 ,10))
        window.blit(arcade, (200, 450))
        titleLabel = titleFont.render("Press the mouse to begin... (r to reset)", 1, (255,255,255))
        window.blit(titleLabel, (width / 2 - titleLabel.get_width() / 2, 370))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                    main()                   
    pygame.quit()
        
mainMenu()
            
        
        