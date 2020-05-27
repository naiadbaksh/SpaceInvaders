import pygame
import os
import time
import random
pygame.font.init() 

#Create a window and name it 'Space Invaders'
WIDTH, HEIGHT = 750, 750
WIN = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("Space Invaders")

# Load images
RED_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png"))
GREEN_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_green_small.png"))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_blue_small.png"))

# Create the player player 
YELLOW_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_yellow.png"))

# Lasers
RED_LASER =  pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
GREEN_LASER =  pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
BLUE_LASER =  pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
YELLOW_LASER =  pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))

# Background - call the image from assets folder and scales it to the width and height
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background-black.png")), (WIDTH, HEIGHT))

class Laser:
	def __init__(self, x, y, img):
		self.x = x
		self.y = y
		self.img = img
		self.mask = pygame.mask.from_surface(self.img)

	def draw(self, window):
		window.blit(self.img, (self.x, self.y))

	def move(self, vel):
		 self.y += vel

	def off_screen(self, height):
		return not (self.y <= HEIGHT and self.y >= 0) 

	def collision(self, obj): 
		return collide(obj, self)

class Ship:

	COOLDOWN = 30

	def __init__(self, x, y, health=100):
		self.x = x
		self.y = y
		self.health = health
		self.ship_img = None
		self.laser_img = None
		self.lasers = []
		self.cool_down_counter = 0

	def draw(self, window):
		window.blit(self.ship_img, (self.x, self.y))
		for laser in self.lasers:
			laser.draw(window)

	def move_lasers(self, vel, obj):
		# Method that moves the lasers and checks if they have collided with anything  
		self.cooldown()
		for laser in self.lasers:
			laser.move(vel)
			if laser.off_screen(HEIGHT):
				self.lasers.remove(laser)
			elif laser.collision(obj):
				obj.health -= 10
				self.lasers.remove(laser)

	def cooldown(self):
		#Method that sets a counter for the laser's cooldown so you can't shoot too often
		if self.cool_down_counter >= self.COOLDOWN:
			self.cool_down_counter = 0
		elif self.cool_down_counter > 0:
			self.cool_down_counter += 1


	def shoot(self):
		#Method that checks if the laser is cool, add a laser to the list and set the cooldown counter to 1
		if self.cool_down_counter == 0:
			laser = Laser(self.x, self.y, self.laser_img)
			self.lasers.append(laser)
			self.cool_down_counter = 1 

	def get_width(self):
		return self.ship_img.get_width()

	def get_height(self):
		return self.ship_img.get_height()

class Player(Ship):
	def __init__(self, x, y, health=100):
		# The "super" method is the parent class Ship and uses that __init__ method to define the variables from the parent class
		super().__init__(x, y, health)
		self.ship_img = YELLOW_SPACE_SHIP
		self.laser_img = YELLOW_LASER
		#Create a mask to allow for pixel-perfect collisions 
		self.mask = pygame.mask.from_surface(self.ship_img)
		self.max_health = health

	def move_lasers(self, vel, objs):
		self.cooldown()
		for laser in self.lasers:
			laser.move(vel)
			if laser.off_screen(HEIGHT):
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

class Enemy(Ship):
	# Class variable that creates a dicti onary which assigns colored image values to keys as strings "red", "green", and "blue" 
	COLOR_MAP = { 
	"red": (RED_SPACE_SHIP, RED_LASER),
	"green": (GREEN_SPACE_SHIP, GREEN_LASER),
	"blue": (BLUE_SPACE_SHIP, BLUE_LASER)
	}

	def __init__(self, x, y, color, health=100):
		super().__init__(x,y,health)
		self.ship_img, self.laser_img = self.COLOR_MAP[color]
		self.mask = pygame.mask.from_surface(self.ship_img)

	def move(self, vel):
		# Moves the enemy ship down at the given velocity
		self.y += vel

	def shoot(self):
		if self.cool_down_counter == 0:
			laser = Laser(self.x-20, self.y, self.laser_img)
			self.lasers.append(laser)
			self.cool_down_counter = 1

def collide(obj1, obj2):
	offset_x = obj2.x - obj1.x
	offset_y = obj2.y - obj1.y
	return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None


def main ():
	run = True
	FPS = 60 
	level = 0
	lives = 5
	main_font = pygame.font.SysFont("comicsans", 50)
	lost_font = pygame.font.SysFont("comicsans", 60)

	# List to store and keep track of all the enemies
	enemies = []

	#This variable is the number of enemies in a given level 
	wave_length = 5
	enemy_vel = 1

	player_vel = 5
	laser_vel = 4

	player = Player(300, 650)

	#Create a clock in the game that ticks at FPS
	clock = pygame.time.Clock()

	lost = False
	lost_count = 0

# This takes care of all the rendering in the window. This function "redraws" the playing window at FPS times per second with any new changes or events. 
	def redraw_window():
		WIN.blit(BG, (0,0))

		# Draw text
		lives_label = main_font.render(f"Lives: {lives}", 1, (255,255,255))
		level_label = main_font.render(f"Level: {level}", 1, (255,255,255))

		WIN.blit(lives_label, (10,10))
		WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))
	

		# This draws the enemies on the screen	
		for enemy in enemies:
			enemy.draw(WIN)	

		player.draw(WIN)

		if lost:
			lost_label = lost_font.render("You lost!", 1, (255,255,255))
			WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 355))


	pygame.display.update() 


	#While the game is running
	while run:
		
		clock.tick(FPS)
		redraw_window() 

		#Conditional statement to check if the player has lost. If so: increment lost_count
		if lives <= 0 or player.health <= 0:
			lost = True
			lost_count += 1

		if lost: 
			if lost_count > FPS * 3:
				run = False
			else:
				continue  

		
		#Conditional statement to check if the enemies have all been destroyed. If so: increment the level and the wave_length
		if len(enemies) == 0:
			level += 1
			wave_length += 5

			#This for loop spawns the enemies off screen in a random way within a range and brings them down into screen view and adds them into the enemy list
			for i in range(wave_length):
				enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1500, -100), random.choice(["red", "blue", "green"]))
				enemies.append(enemy)


		# Iterate through all the events that pygame recognizes and checks for Quit event
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False  


		keys = pygame.key.get_pressed()
		if keys[pygame.K_a] and player.x - player_vel > 0: #left
			player.x -= player_vel
		if keys[pygame.K_d] and player.x + player_vel  + player.get_width() < WIDTH: #right
			player.x += player_vel
		if keys[pygame.K_s] and player.y + player_vel + player.get_height() < HEIGHT: #down
			player.y += player_vel
		if keys[pygame.K_w] and player.y - player_vel > 0: #up
			player.y -= player_vel  
		if keys[pygame.K_SPACE]:
			player.shoot()

		for enemy in enemies[:]:
			enemy.move(enemy_vel)
			enemy.move_lasers(laser_vel, player)
			# Check position of enemy, and if it's below the screen: remove from emeny list and decrement the lives
			if enemy.y + enemy.get_height() > HEIGHT:
				lives -= 1 
				enemies.remove(enemy)

		player.move_lasers(-laser_vel, enemies)

main()
