import pygame
from pygame.locals import *
import sys
import time
import os
import random
pygame.init()
pygame.font.init()

WIN_WIDTH = 500
WIN_HEIGHT = 800

BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png")))]
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))
START_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "message.png")))
GAME_OVER_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "gameover.png")))

STAT_FONT = pygame.font.SysFont("consolas", 40)
SMALLER_FONT = pygame.font.SysFont("consolas", 25)

class Bird:
	IMGS = BIRD_IMGS
	MAX_ROTATION = 25
	ROT_VEL = 20
	ANIMATION_TIME = 5

	def __init__(self, x, y):
		self.x = x
		self.y = y 
		self.tilt = 0 
		self.tick_count = 0 
		self.vel = 0
		self.height = self.y
		self.img_count = 0
		self.img = self.IMGS[0]

	def jump(self):
		self.vel = -10.5
		self.tick_count = 0
		self.height = self.y

	def move(self):
		self.tick_count += 1

		d = self.vel*self.tick_count + 1.5*self.tick_count**2

		if d >= 16:
			d = 16

		if d < 0:
			d -= 2 #changes jump val, can mess w

		self.y = self.y + d #change to += d ?

		if d < 0 or self.y < self.height + 50:
			if self.tilt < self.MAX_ROTATION:
				self.tilt = self.MAX_ROTATION
		else:
			if self.tilt > -90:
				self.tilt -= self.ROT_VEL

	def draw(self, win):
		self.img_count += 1

		if self.img_count < self.ANIMATION_TIME:
			self.img = self.IMGS[0]
		elif self.img_count < self.ANIMATION_TIME*2:
			self.img = self.IMGS[1]
		elif self.img_count < self.ANIMATION_TIME*3:
			self.img = self.IMGS[2]
		elif self.img_count < self.ANIMATION_TIME*4:
			self.img = self.IMGS[1]
		elif self.img_count == self.ANIMATION_TIME*4 + 1:
			self.img = self.IMGS[0]
			self.img_count = 0

		if self.tilt <= -80:
			self.img = self.IMGS[1]
			self.img_count = self.ANIMATION_TIME*2

		rotated_image = pygame.transform.rotate(self.img, self.tilt)
		new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft = (self.x, self.y)).center)
		win.blit(rotated_image, new_rect.topleft)

	def get_mask(self):
		return pygame.mask.from_surface(self.img)


class Pipe:
	GAP = 200
	VEL = 5

	def __init__(self, x):
		self.x = x
		self.height = 0

		self.top = 0
		self.bottom = 0 
		self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)
		self.PIPE_BOTTOM = PIPE_IMG

		self.passed = False
		self.set_height()

	def set_height(self):
		self.height = random.randrange(50, 450)
		self.top = self.height - self.PIPE_TOP.get_height()
		self.bottom = self.height + self.GAP

	def move(self):
		self.x -= self.VEL

	def draw (self, win):
		win.blit(self.PIPE_TOP, (self.x, self.top))
		win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

	def collide(self, bird):
		bird_mask = bird.get_mask()
		top_mask = pygame.mask.from_surface(self.PIPE_TOP)
		bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

		top_offset = (self.x - bird.x, self.top - round(bird.y))
		bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

		b_point = bird_mask.overlap(bottom_mask, bottom_offset)
		t_point = bird_mask.overlap(top_mask, top_offset)

		if t_point or b_point:
			return True

		return False


class Base:
	VEL = 5
	WIDTH = BASE_IMG.get_width()
	IMG = BASE_IMG

	def __init__(self, y):
		self.y = y 
		self.x1 = 0 
		self.x2 = self.WIDTH 

	def move(self):
		self.x1 -= self.VEL
		self.x2 -= self.VEL

		if self.x1 + self.WIDTH < 0:
			self.x1 = self.x2 + self.WIDTH

		if self.x2 + self.WIDTH < 0:
			self.x2 = self.x1 + self.WIDTH

	def draw(self, win):
		win.blit(self.IMG, (self.x1, self.y))
		win.blit(self.IMG, (self.x2, self.y))


def draw_window(win, bird, pipes, base, score):
	win.blit(BG_IMG, (0,0))

	for pipe in pipes:
		pipe.draw(win)

	text = STAT_FONT.render("Score: " + str(score), 1, (255,255,255))
	win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))

	base.draw(win)

	bird.draw(win)
	pygame.display.update()


def gameOver(score):
	SCREEN = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
	SCREEN.blit(BG_IMG, (0,0))
	SCREEN.blit(BASE_IMG, (0,730))
	SCREEN.blit(GAME_OVER_IMG, ((WIN_WIDTH - GAME_OVER_IMG.get_width()) / 2,(WIN_HEIGHT - GAME_OVER_IMG.get_height()) / 3))
	scorem = STAT_FONT.render("Your Score Is: " + str(score), 1, (255,255,255))
	SCREEN.blit(scorem, (((WIN_WIDTH - scorem.get_width()) / 2), ((WIN_HEIGHT - GAME_OVER_IMG.get_height()) / 3) + GAME_OVER_IMG.get_height() + 30))
	restartm = SMALLER_FONT.render("Press Space to Restart", 1, (255,255,255))
	SCREEN.blit(restartm, (((WIN_WIDTH - restartm.get_width()) / 2), ((WIN_HEIGHT - GAME_OVER_IMG.get_height()) / 3) + GAME_OVER_IMG.get_height() + 180))

	pygame.display.update()

	while True:
		for event in pygame.event.get():
			if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
				pygame.quit()
				sys.exit()

			if event.type == KEYDOWN and event.key == K_SPACE:
				main()

def startScreen():
	START = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
	START.blit(BG_IMG, (0,0))
	START.blit(BASE_IMG, (0,730))
	START.blit(START_IMG, ((WIN_WIDTH - START_IMG.get_width()) / 2, 80))

	pygame.display.update()

	while True:
		for event in pygame.event.get():
			if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
				pygame.quit()
				sys.exit()

			if event.type == KEYDOWN and event.key == K_SPACE:
				main()


def main():
	bird = Bird(230,350)
	base = Base(730)
	pipes = [Pipe(600)]
	win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
	clock = pygame.time.Clock()

	score = 0 

	run = True
	while run:
		clock.tick(30)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				gameOver(score)
				#run = False
				#pygame.quit()
				#quit()
			#elif event.type == pygame.K_SPACE:
				#bird.jump()

		bird.move()

		pressed_keys = pygame.key.get_pressed()

		if pressed_keys[K_SPACE]:
			bird.jump()

		#for event in pygame.event.get():
		#	if event.type == pygame.KEYDOWN:
		#		if event.key == pygame.K_SPACE:
		#			bird.jump()

		if bird.y > base.y - 60:
			gameOver(score)
			#run = False

		add_pipe = False
		rem = []
		for pipe in pipes:
			if pipe.collide(bird):
				gameOver(score)
				#run = False
				#pygame.quit()
				#quit() 

			if pipe.x + pipe.PIPE_TOP.get_width() < 0:
				rem.append(pipe)

			if not pipe.passed and pipe.x < bird.x:
				pipe.passed = True
				add_pipe = True

			pipe.move()

		if add_pipe:
			score += 1
			pipes.append(Pipe(600))

		for r in rem:
			pipes.remove(r)

		#look up how to make user control game

		if bird.y + bird.img.get_height() >= 730:
			gameOver(score)

		base.move()
		draw_window(win, bird, pipes, base, score)

	pygame.quit()
	quit()

count = 0
if count == 0:
	startScreen()
	count = count + 1





