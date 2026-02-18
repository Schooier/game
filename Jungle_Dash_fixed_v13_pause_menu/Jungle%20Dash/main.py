import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))  # ensure relative asset paths work
import random
import pygame
from pygame.locals import *

from objects import World, Player, Button, draw_lines, load_level, draw_text, sounds

# Window setup
SIZE = WIDTH , HEIGHT= 1000, 650
tile_size = 50

pygame.init()
win = pygame.display.set_mode(SIZE)
pygame.display.set_caption('DASH')
clock = pygame.time.Clock()
FPS = 30

# menu label font (for mode select buttons)
menu_font = pygame.font.SysFont('Bauhaus 93', 34)

def draw_button_label(btn, label):
	"""Covers default text on a button image and draws a custom centered label."""
	inner = btn.image.get_at((btn.rect.width//2, btn.rect.height//2))
	pad_x = 40
	pad_y = 16
	mask = pygame.Rect(btn.rect.x + pad_x, btn.rect.y + pad_y, btn.rect.width - 2*pad_x, btn.rect.height - 2*pad_y)
	pygame.draw.rect(win, inner, mask, border_radius=14)
	text_surf = menu_font.render(label, True, (255,255,255))
	text_rect = text_surf.get_rect(center=btn.rect.center)
	win.blit(text_surf, text_rect)


def draw_mode_button_label(btn, label):
	draw_button_label(btn, label)


# background images
bg1 = pygame.image.load('assets/BG1.png')
bg2 = pygame.image.load('assets/BG2.png')
bg = bg1
sun = pygame.image.load('assets/sun.png')
jungle_dash = pygame.image.load('assets/jungle dash.png')
you_won = pygame.image.load('assets/won.png')


# loading level 1
level = 1
max_level = len(os.listdir('levels/'))
data = load_level(level)

player_pos = (10, 340)


# creating world & objects
water_group = pygame.sprite.Group()
lava_group = pygame.sprite.Group()
forest_group = pygame.sprite.Group()
diamond_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()
enemies_group = pygame.sprite.Group()
platform_group = pygame.sprite.Group()
bridge_group = pygame.sprite.Group()
groups = [water_group, lava_group, forest_group, diamond_group, enemies_group, exit_group, platform_group,
			bridge_group]
world = World(win, data, groups)
player = Player(win, player_pos, world, groups)
level_diamond_total = 0


# creating buttons
play= pygame.image.load('assets/play.png')
replay = pygame.image.load('assets/replay.png')
home = pygame.image.load('assets/home.png')
exit = pygame.image.load('assets/exit.png')
setting = pygame.image.load('assets/setting.png')

normal_btn = Button(play, (220, 70), WIDTH//2 - 110, HEIGHT//2 - 60)
hard_btn   = Button(play, (220, 70), WIDTH//2 - 110, HEIGHT//2 + 20)
speed_btn  = Button(play, (220, 70), WIDTH//2 - 110, HEIGHT//2 + 100)
replay_btn  = Button(replay, (45,42), WIDTH//2 - 110, HEIGHT//2 + 20)
home_btn  = Button(home, (45,42), WIDTH//2 - 20, HEIGHT//2 + 20)
exit_btn  = Button(exit, (45,42), WIDTH//2 + 70, HEIGHT//2 + 20)

# pause button (bottom-right)
pause_btn  = Button(setting, (45,42), WIDTH - 55, HEIGHT - 55)
# pause menu buttons (center)
pause_resume_btn = Button(play, (220, 70), WIDTH//2 - 110, HEIGHT//2 - 80)
pause_menu_btn   = Button(play, (220, 70), WIDTH//2 - 110, HEIGHT//2 + 10)
pause_quit_btn   = Button(play, (220, 70), WIDTH//2 - 110, HEIGHT//2 + 100)




# function to reset a level
def reset_level(level):
	global cur_score
	cur_score = 0

	data = load_level(level)
	if data:
		for group in groups:
			group.empty()
		world = World(win, data, groups)
		player.reset(win, player_pos, world, groups)
		global level_diamond_total
		level_diamond_total = sum(1 for r in data for c in r if c == 17)
# 10, 340
	return world

score = 0
cur_score = 0

main_menu = True
game_over = False
level_won = False
game_won = False
show_progress = True

# extra modes
hard_mode = False           # Hard Mode: collect ALL diamonds to finish a level
speedrun_mode = False       # Speedrun Mode: show timer
speedrun_start_ms = 0
speedrun_pause_ms = 0
speedrun_pause_start = None
speedrun_final_ms = None
level_diamond_total = 0
hard_notice_until = 0



def draw_progress_bar(win, overall_progress):
	"""Draws a simple progress bar (0.0 - 1.0) at top-center."""
	overall_progress = max(0.0, min(1.0, float(overall_progress)))
	bar_w = 320
	bar_h = 16
	x = WIDTH//2 - bar_w//2
	y = 10
	# outline
	pygame.draw.rect(win, (255,255,255), (x, y, bar_w, bar_h), width=2, border_radius=6)
	# fill
	fill_w = int((bar_w-4) * overall_progress)
	pygame.draw.rect(win, (30, 144, 255), (x+2, y+2, fill_w, bar_h-4), border_radius=6)
	percent = int(overall_progress * 100)
	draw_text(win, f'{percent}%', (WIDTH//2 - 20, y + bar_h + 4))


def format_time_ms(ms: int) -> str:
	ms = max(0, int(ms))
	minutes = ms // 60000
	seconds = (ms % 60000) // 1000
	millis = ms % 1000
	return f'{minutes:02d}:{seconds:02d}.{millis:03d}'


def draw_advanced_win_screen():
	"""A nicer end screen with stats + buttons."""
	# dark overlay
	overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
	overlay.fill((0, 0, 0, 140))
	win.blit(overlay, (0, 0))

	# panel
	panel_w, panel_h = 520, 360
	px = WIDTH//2 - panel_w//2
	py = HEIGHT//2 - panel_h//2
	panel = pygame.Rect(px, py, panel_w, panel_h)
	pygame.draw.rect(win, (255, 255, 255), panel, border_radius=18)
	pygame.draw.rect(win, (30, 144, 255), panel, width=4, border_radius=18)

	# title + trophy image
	win.blit(you_won, (WIDTH//2 - you_won.get_width()//2, py - 40))

	# stats
	line_y = py + 140
	mode_txt = 'NORMAL'
	if hard_mode:
		mode_txt = 'HARD'
	elif speedrun_mode:
		mode_txt = 'SPEEDRUN'

	draw_text(win, f'Mode: {mode_txt}', (px + 40, line_y))
	line_y += 40
	draw_text(win, f'Totaal diamanten: {score}', (px + 40, line_y))
	line_y += 40
	if speedrun_mode and speedrun_final_ms is not None:
		draw_text(win, f'Eindtijd: {format_time_ms(speedrun_final_ms)}', (px + 40, line_y))
		line_y += 40

	# hint
	draw_text(win, 'Wat wil je doen?', (px + 40, py + panel_h - 110))

	# buttons (reuse existing icons)
	replay_btn.rect.topleft = (WIDTH//2 - 95, py + panel_h - 75)
	home_btn.rect.topleft = (WIDTH//2 - 20, py + panel_h - 75)
	exit_btn.rect.topleft = (WIDTH//2 + 55, py + panel_h - 75)

	replay_click = replay_btn.draw(win)
	home_click = home_btn.draw(win)
	exit_click = exit_btn.draw(win)

	return replay_click, home_click, exit_click

running = True
paused = False
while running:
	for event in pygame.event.get():
		if event.type == QUIT:
			running = False
		if event.type == KEYDOWN:
			# toggle UI
			if event.key == K_h:
				show_progress = not show_progress
			# pause
			if event.key in (K_p, K_ESCAPE):
				paused = not paused
				if paused:
					pygame.mixer.music.pause()
					pygame.mixer.pause()
					if speedrun_mode and speedrun_pause_start is None and not main_menu and not game_won:
						speedrun_pause_start = pygame.time.get_ticks()
				else:
					pygame.mixer.music.unpause()
					pygame.mixer.unpause()
					if speedrun_mode and speedrun_pause_start is not None:
						speedrun_pause_ms += pygame.time.get_ticks() - speedrun_pause_start
						speedrun_pause_start = None

	pressed_keys = pygame.key.get_pressed()

	# displaying background & sun image
	win.blit(bg, (0,0))
	win.blit(sun, (40,40))
	world.draw()
	for group in groups:
		group.draw(win)

	# drawing grid
	# draw_lines(win)

	if main_menu:
		win.blit(jungle_dash, (WIDTH//2 - WIDTH//8, HEIGHT//4))

		# Choose mode
		normal_click = normal_btn.draw(win)
		hard_click   = hard_btn.draw(win)
		speed_click  = speed_btn.draw(win)
		# replace default PLAY text with mode labels
		draw_mode_button_label(normal_btn, 'NORMAL')
		draw_mode_button_label(hard_btn, 'HARD')
		draw_mode_button_label(speed_btn, 'SPEEDRUN')
		if normal_click or hard_click or speed_click:
			hard_mode = bool(hard_click)
			speedrun_mode = bool(speed_click)
			main_menu = False
			game_over = False
			game_won = False
			score = 0
			speedrun_start_ms = pygame.time.get_ticks() if speedrun_mode else 0
			speedrun_pause_ms = 0
			speedrun_pause_start = None
			paused = False
			pygame.mixer.music.unpause()
			pygame.mixer.unpause()

	else:
		# pause button (click or press P / ESC)
		if not game_over and not game_won:
			if pause_btn.draw(win):
				paused = not paused
				if paused:
					pygame.mixer.music.pause()
					pygame.mixer.pause()
					if speedrun_mode and speedrun_pause_start is None and not game_over and not game_won:
						speedrun_pause_start = pygame.time.get_ticks()
				else:
					pygame.mixer.music.unpause()
					pygame.mixer.unpause()
					if speedrun_mode and speedrun_pause_start is not None:
						speedrun_pause_ms += pygame.time.get_ticks() - speedrun_pause_start
						speedrun_pause_start = None


		# pause overlay menu
		if paused and not game_over and not game_won:
			overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
			overlay.fill((0, 0, 0, 140))
			win.blit(overlay, (0, 0))
			# buttons
			res_click = pause_resume_btn.draw(win)
			menu_click = pause_menu_btn.draw(win)
			quit_click = pause_quit_btn.draw(win)
			draw_button_label(pause_resume_btn, 'RESUME')
			draw_button_label(pause_menu_btn, 'MENU')
			draw_button_label(pause_quit_btn, 'QUIT')
			if res_click:
				paused = False
				pygame.mixer.music.unpause()
				pygame.mixer.unpause()
				if speedrun_mode and speedrun_pause_start is not None:
					speedrun_pause_ms += pygame.time.get_ticks() - speedrun_pause_start
					speedrun_pause_start = None
			if menu_click:
				# back to mode select and restart
				paused = False
				pygame.mixer.music.unpause()
				pygame.mixer.unpause()
				if speedrun_mode and speedrun_pause_start is not None:
					speedrun_pause_ms += pygame.time.get_ticks() - speedrun_pause_start
					speedrun_pause_start = None
				main_menu = True
				game_over = False
				game_won = False
				level_won = False
				level = 1
				hard_mode = False
				speedrun_mode = False
				speedrun_start_ms = 0
				speedrun_pause_ms = 0
				speedrun_pause_start = None
				speedrun_final_ms = None
				score = 0
				cur_score = 0
				world = reset_level(level)
			if quit_click:
				running = False

		# progress bar (top-center) - toggle with H
		if show_progress:
			exit_sprites = exit_group.sprites()
			if exit_sprites:
				exit_x = max(s.rect.centerx for s in exit_sprites)
			else:
				exit_x = getattr(world, 'level_width', WIDTH)
			if exit_x <= 0:
				level_progress = 1.0
			else:
				level_progress = max(0.0, min(1.0, player.rect.centerx / exit_x))
			overall_progress = ((level - 1) + level_progress) / max_level
			draw_progress_bar(win, overall_progress)


		# mode indicators + speedrun timer (top area)
		if hard_mode:
			draw_text(win, 'HARD', (10, 10))
		if speedrun_mode:
			# timer pauses while paused or after you win
			if speedrun_start_ms == 0 and not main_menu:
				speedrun_start_ms = pygame.time.get_ticks()
			current_ms = pygame.time.get_ticks()
			paused_extra = 0
			if speedrun_pause_start is not None:
				paused_extra = current_ms - speedrun_pause_start
			run_ms = current_ms - speedrun_start_ms - speedrun_pause_ms - paused_extra
			draw_text(win, f'Time {format_time_ms(run_ms)}', (10, HEIGHT - 40))

		# Hard Mode notice if you try to exit too early
		if hard_notice_until and pygame.time.get_ticks() < hard_notice_until:
			# show remaining diamonds
			remaining = max(0, level_diamond_total - cur_score)
			draw_text(win, f'Pak nog {remaining} diamant(en)!', (WIDTH//2 - 140, HEIGHT//2 - 80))

		if not game_over and not game_won and not paused:
			
			enemies_group.update(player)
			platform_group.update()
			exit_group.update(player)
			if pygame.sprite.spritecollide(player, diamond_group, True):
				sounds[0].play()
				cur_score += 1
				score += 1	
			draw_text(win, f'{score}', ((WIDTH//tile_size - 2) * tile_size, tile_size//2 + 10))
			
		if not paused:
			game_over, level_won = player.update(pressed_keys, game_over, level_won, game_won)
			# Hard Mode: you can only finish if you collected ALL diamonds
			if hard_mode and level_won and cur_score < level_diamond_total:
				level_won = False
				hard_notice_until = pygame.time.get_ticks() + 1500
		else:
			draw_text(win, 'PAUZE', (WIDTH//2 - 50, HEIGHT//2 - 20))
			draw_text(win, 'druk P of ESC', (WIDTH//2 - 90, HEIGHT//2 + 20))


		if game_over and not game_won:
			replay = replay_btn.draw(win)
			home = home_btn.draw(win)
			exit = exit_btn.draw(win)

			if replay:
				score -= cur_score
				world = reset_level(level)
				game_over = False
				paused = False
				pygame.mixer.music.unpause()
				pygame.mixer.unpause()
			if home:
				game_over = True
				main_menu = True
				paused = False
				pygame.mixer.music.unpause()
				pygame.mixer.unpause()
				speedrun_start_ms = 0
				speedrun_pause_ms = 0
				speedrun_pause_start = None
				bg = bg1
				level = 1
				world = reset_level(level)
			if exit:
				running = False

		if level_won:
			if level <= max_level:
				level += 1
				game_level = f'levels/level{level}_data'
				if os.path.exists(game_level):
					data = []
					world = reset_level(level)
					level_won = False
					score += cur_score

				bg = random.choice([bg1, bg2])
			else:
				game_won = True
				# lock final speedrun time once
				if speedrun_mode and speedrun_final_ms is None:
					current_ms = pygame.time.get_ticks()
					paused_extra = 0
					if speedrun_pause_start is not None:
						paused_extra = current_ms - speedrun_pause_start
					speedrun_final_ms = current_ms - speedrun_start_ms - speedrun_pause_ms - paused_extra
				bg = bg1
				replay_click, home_click, exit_click = draw_advanced_win_screen()

				if replay_click:
					# restart from level 1 (same chosen mode)
					game_over = False
					game_won = False
					level_won = False
					level = 1
					score = 0
					speedrun_start_ms = pygame.time.get_ticks() if speedrun_mode else 0
					speedrun_pause_ms = 0
					speedrun_pause_start = None
					speedrun_final_ms = None
					paused = False
					world = reset_level(level)
					pygame.mixer.music.unpause()
					pygame.mixer.unpause()

				if home_click:
					game_over = True
					main_menu = True
					paused = False
					pygame.mixer.music.unpause()
					pygame.mixer.unpause()
					speedrun_start_ms = 0
					speedrun_pause_ms = 0
					speedrun_pause_start = None
					speedrun_final_ms = None
					level_won = False
					level = 1
					world = reset_level(level)

				if exit_click:
					running = False

	pygame.display.flip()
	clock.tick(FPS)

pygame.quit()