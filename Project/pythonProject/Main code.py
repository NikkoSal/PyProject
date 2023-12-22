import pygame
from pygame.locals import *

pygame.init()

clock = pygame.time.Clock()
fps = 60

screen_width = 1280
screen_height = 720

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Flt')

#def определения
tile_size = 40
game_over = 0
main_menu = True

#Спрайты
sun_img = pygame.image.load('Assets/sun.png')
sun = pygame.transform.scale(sun_img, (tile_size, tile_size))
bg_img = pygame.image.load('Assets/darkmood.jpg')
bg_img = pygame.transform.scale(bg_img, (screen_width, screen_height))
restart_img = pygame.image.load('Assets/RESTART.png')
restart_img = pygame.transform.scale(restart_img, (tile_size * 8, tile_size * 4))
start_img = pygame.image.load('Assets/START.png')
start_img = pygame.transform.scale(start_img, (tile_size * 8, tile_size * 6))
exit_img = pygame.image.load('Assets/EXIT.png')
exit_img = pygame.transform.scale(exit_img, (tile_size * 8, tile_size * 6))
mainmenu_img = pygame.image.load('Assets/mainmenu.jpg')
mainmenu_img = pygame.transform.scale(mainmenu_img, (screen_width, screen_height))
exit_ingame_img = pygame.image.load('Assets/EXIT1.png')
exit_ingame_img = pygame.transform.scale(exit_ingame_img, (tile_size *2, tile_size))


def draw_grid():
	for line in range(0, 40):
		pygame.draw.line(screen, (255, 255, 255), (0, line * tile_size), (screen_width, line * tile_size))
		pygame.draw.line(screen, (255, 255, 255), (line * tile_size, 0), (line * tile_size, screen_height))

class Button():
	def __init__(self, x, y, image):
		self.image = image
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
	def draw(self):
		action = False
		#Положение мышки
		pos = pygame.mouse.get_pos()

		if self.rect.collidepoint(pos):
			if pygame.mouse.get_pressed()[0] == 1:
				action = True
				self.clicked = True

		if pygame.mouse.get_pressed()[0] == 0:
			self.clicked = False


		#Рисуем кнопку на жкране
		screen.blit(self.image, self.rect)

		return action

class Player():
	def __init__(self, x, y):
		self.reset(x, y)

	def update(self, game_over):
		dx = 0
		dy = 0
		walk_cooldown = 5

		if game_over == 0:
			# Управление
			key = pygame.key.get_pressed()
			if key[pygame.K_SPACE] and self.jumped == False and self.in_air == False:
				self.vel_y = -15
				self.jumped = True
			if key[pygame.K_SPACE] == False:
				self.jumped = False
			if key[pygame.K_a]:
				dx -= 5
				self.counter += 1
				self.direction = -1
			if key[pygame.K_d]:
				dx += 5
				self.counter += 1
				self.direction = 1
			if key[pygame.K_a] == False and key[pygame.K_d] == False:
				self.counter = 0
				self.index = 0
				if self.direction == 1:
					self.image = self.images_right[self.index]
				if self.direction == -1:
					self.image = self.images_left[self.index]

			#Настройка анимации
			if self.counter > walk_cooldown:
				self.counter = 0
				self.index += 1
				if self.index >= len(self.images_right):
					self.index = 0
				if self.direction == 1:
					self.image = self.images_right[self.index]
				if self.direction == -1:
					self.image = self.images_left[self.index]

			#Гравитация
			self.vel_y += 1
			if self.vel_y > 10:
				self.vel_y = 10
			dy += self.vel_y

			#Коллизия
			self.in_air = True
			for tile in world.tile_list:
				#Коллизия по x
				if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.hight):
					dx = 0

				#Коллизия по y
				if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.hight):
					#Прыжки
					if self.vel_y < 0:
						dy = tile[1].bottom - self.rect.top
						self.vel_y = 0
					#Падение
					elif self.vel_y >= 0:
						dy = tile[1].top - self.rect.bottom
						self.vel_y = 0
						self.in_air = False



			#коллиия с классом Enemy
			if pygame.sprite.spritecollide(self, frame_group, False):
				game_over = -1
			# коллиия с классом Lava
			if pygame.sprite.spritecollide(self, lava_group, False):
				game_over = -1

			#Обновление координат
			self.rect.x += dx
			self.rect.y += dy


		elif game_over == -1:
			self.image = self.dead_image
			if self.rect.y > -200:
				self.rect.y -= 5

		# Сетка персонажа
		screen.blit(self.image, self.rect)
		pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)

		return game_over

	def reset(self, x, y):
		self.images_right = []
		self.images_left = []
		self.index = 0
		self.counter = 0
		for num in range (2, 12):
			img_right = pygame.image.load(f'Assets/guy{num}.png')
			img_right = pygame.transform.scale(img_right, (40, 80))
			img_left = pygame.transform.flip(img_right, True, False)
			self.images_right.append(img_right)
			self.images_left.append(img_left)
		self.dead_image = pygame.image.load('Assets/ghost.png')
		self.dead_image = pygame.transform.scale(self.dead_image,(50,60))
		self.image = self.images_right[self.index]
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.width = self.image.get_width()
		self.hight = self.image.get_height()
		self.vel_y = 0
		self.jumped = False
		self.direction = 0
		self.in_air = True

# Иниализация атрибута
class World():
	def __init__(self, data):
		self.tile_list = []

		#Спрайты
		dirt_img = pygame.image.load('Assets/block1.png')
		grass_img = pygame.image.load('Assets/grass1.png')

		row_count = 0
		for row in data:
			col_count = 0
			for tile in row:
#Создание тайлов и добавление их в tile_list
				if tile == 1:
					img = pygame.transform.scale(dirt_img, (tile_size, tile_size))
					img_rect = img.get_rect()
					img_rect.x = col_count * tile_size
					img_rect.y = row_count * tile_size
					tile = (img, img_rect)
					self.tile_list.append(tile)
				if tile == 2:
					img = pygame.transform.scale(grass_img, (tile_size, tile_size))
					img_rect = img.get_rect()
					img_rect.x = col_count * tile_size
					img_rect.y = row_count * tile_size
					tile = (img, img_rect)
					self.tile_list.append(tile)
				if tile == 3:
					frame = Enemy(col_count * tile_size, row_count * tile_size + 10)
					frame_group.add(frame)
				if tile == 6:
					lava = Lava(col_count * tile_size, row_count * tile_size + (tile_size // 2))
					lava_group.add(lava)
				col_count += 1
			row_count += 1

	#Сетка мира
	def draw(self):
		for tile in self.tile_list:
			screen.blit(tile[0], tile[1])
			pygame.draw.rect(screen, (255, 255, 255), tile[1], 2)


class Enemy(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load(('Assets/frame.png'))
		self.image = pygame.transform.scale(self.image, (40, 40))
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.move_direction = 1
		self.move_counter = 0

	def update(self):
		self.rect.x += self.move_direction
		self.move_counter += 1
		if abs(self.move_counter) > 50:
			self.move_direction *= -1
			self.move_counter *= -1

class Lava(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load(('Assets/lava.png'))
		self.image = pygame.transform.scale(self.image, (tile_size, tile_size // 2))
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y



world_data = [
[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,6, 6, 6, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0,0, 0, 0, 0, 0, 0, 3, 0, 3, 0, 0, 0, 0, 0, 0, 0, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0,0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1],
[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
]


player = Player(100,screen_height - 130)

frame_group = pygame.sprite.Group()

lava_group = pygame.sprite.Group()

world = World(world_data)

#Создаём кнопки
restart_button = Button(screen_width // 2 - 150, screen_height // 2 - 50 , restart_img)
start_img = Button(screen_width // 2 - 150 , screen_height // 2 - 210 , start_img)
exit_img = Button(screen_width // 2 - 150 , screen_height // 2 - 50 , exit_img)
exit_ingame_img = Button(600, 680, exit_ingame_img)

run = True
while run:
	if main_menu == True:
		screen.blit(mainmenu_img,(0,0))
		if exit_img.draw():
			run = False
		if start_img.draw():
			main_menu = False

	else:
		clock.tick(fps)
		screen.blit(bg_img, (0, 0))
		screen.blit(sun_img, (700, 100))

		world.draw()

		if game_over == 0:
			frame_group.update()


		frame_group.draw(screen)

		lava_group.draw(screen)

		game_over = player.update(game_over)


		#Если игрок мертв

		if game_over == -1:
			if restart_button.draw():
				player.reset(100,screen_height - 130)
				game_over = 0
			if exit_ingame_img.draw():
				run = False

	#draw_grid()

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False

	pygame.display.update()

pygame.quit()