# -*- encoding: utf-8 -*-
from __future__ import division

import argparse
import gettext
import math
import os
import random
import sys

import pygame
from pygame.locals import *

from . import __version__, PROGRAM_DESCRIPTION

gettext.install("bullet_dodger", os.path.join(os.path.dirname(__file__), 'locale'))

"""Parse command line arguments."""
parser = argparse.ArgumentParser(description=PROGRAM_DESCRIPTION,
                                 prog=_('Hero Dodger'))
parser.add_argument('--version', action='version',
                    version='%(prog)s ' + __version__,
                    help=_('output version information and exit'))
parser.add_argument('-l', '--lang',
                    help=_('manually choose a different language to use.'))
args = parser.parse_args()

if args.lang:
    lang = gettext.translation('bullet_dodger',
                               os.path.join(os.path.dirname(__file__), 'locale'), [args.lang])
    if sys.version_info[:1] == (2,):
        lang.install(unicode=True)
    else:
        lang.install()

# Resolution
WIDTH = 800
HEIGHT = 600

# Colors
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
DARK_ALLOY_ORANGE = (196, 121, 67)
RED = (255, 0, 0)
YELLOW = (255, 255, 12)

MSWIN = os.name == 'nt'

ASSETS = os.path.join(os.path.dirname(__file__), 'assets')

pygame.init()
# Display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
fullscreen = False
# Window titlebar
pygame.display.set_caption(_('Hero Dodge'))
game_icon = os.path.join(ASSETS, 'bullet.png')
pygame.display.set_icon(pygame.image.load(game_icon))
# Timing
fps_clock = pygame.time.Clock()
FPS = 60
# Preload resources
default_font = pygame.font.Font(None, 28)
ground_texture = os.path.join(ASSETS, 'ground.gif')
background_img = pygame.image.load(ground_texture)
start_screen_background = os.path.join(ASSETS, 'ground.gif')
background_start_img =  pygame.image.load(start_screen_background)
bullet_fire_sound = os.path.join(ASSETS, 'gun_fire.ogg')
blip_star = os.path.join(ASSETS, 'blip_star.ogg')
game_music = os.path.join(ASSETS, 'Hitman.ogx')
pygame.mixer.music.load(game_music)

def get_config_dir():
    """Get user's configuration directory."""
    if MSWIN:
        confdir = os.environ["APPDATA"]

    elif 'XDG_CONFIG_HOME' in os.environ:
        confdir = os.environ['XDG_CONFIG_HOME']

    else:
        confdir = os.path.join(os.path.expanduser("~"), '.config')

    game_confdir = os.path.join(confdir, "bullet-dodger")

    try:  # Python 2 compatibility
        os.makedirs(game_confdir)
    except OSError as e:
        pass

    return game_confdir


class Score:
    # Highest score file
    def __init__(self):
        self.HIGHEST_SCORE_PATH = os.path.join(get_config_dir(), 'highest_score')
        if not os.path.exists(self.HIGHEST_SCORE_PATH):
            with open(self.HIGHEST_SCORE_PATH, 'w') as highest_score_file:
                highest_score_file.write('0')
        # Load highest score
        self.high_score = self.highest_score = self.load_highest_score()
        self.points = 0

    def load_highest_score(self):
        with open(self.HIGHEST_SCORE_PATH, 'r') as highest_score_file:
            highest_score = int(highest_score_file.readlines()[0])
        return highest_score

    def save_highest_score(self):
        with open(self.HIGHEST_SCORE_PATH, 'w') as highest_score_file:
            highest_score_file.write(str(self.high_score))

class Block(pygame.sprite.Sprite):
    def __init__(self):
        super(Block, self).__init__()
        self.img = pygame.image.load(os.path.join(ASSETS, 'hero.png'))
        self.rect = self.img.get_rect()
        self.centerx = self.rect.centerx
        self.centery = self.rect.centery

    def set_pos(self, x, y):
        'Positions the block center in x and y location'
        self.rect.x = x - self.centerx
        self.rect.y = y - self.centery

    def collide(self, sprites):
        for sprite in sprites:
            if pygame.sprite.collide_rect(self, sprite):
                return sprite


class Bonus(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super(Bonus, self).__init__()
        self.image = pygame.image.load(os.path.join(ASSETS, 'star.png'))
        self.rect = self.image.get_rect()
        self.rect.x = x - self.rect.centerx
        self.rect.y = y - self.rect.centery


def random_bullet(speed, score_points, direction):

    if (score_points >= 300):
        direction = random.randint(1, 4)
    elif (score_points >= 200) and (score_points < 300):
        direction = random.randint(1, 3)
    elif (score_points >= 100) and (score_points < 200):
        direction = random.randint(1, 2)
    elif (score_points < 100):
        direction = random.randint(1, 1)


    random_or = random.randint(1, direction) #directions
    if random_or == 1:  # Up -> Down
        return Bullet(random.randint(0, WIDTH), 0, 0, speed)
    elif random_or == 2:  # Right -> Left
        return Bullet(WIDTH, random.randint(0, HEIGHT), -speed, 0)
    elif random_or == 3:  # Down -> Up
        return Bullet(random.randint(0, WIDTH), HEIGHT, 0, -speed)
    elif random_or == 4:  # Left -> Right
        return Bullet(0, random.randint(0, HEIGHT), speed, 0)


class Bullet(pygame.sprite.Sprite):

    def __init__(self, xpos, ypos, hspeed, vspeed):
        super(Bullet, self).__init__()
        self.image = pygame.image.load(os.path.join(ASSETS, 'bullet.png'))
        self.rect = self.image.get_rect()
        self.rect.x = xpos
        self.rect.y = ypos
        self.hspeed = hspeed
        self.vspeed = vspeed

        self.set_direction()

    def update(self):
        self.rect.x += self.hspeed
        self.rect.y += self.vspeed
        if self.collide():
            self.kill()

    def collide(self):
        if self.rect.x < 0 - self.rect.height or self.rect.x > WIDTH:
            return True
        elif self.rect.y < 0 - self.rect.height or self.rect.y > HEIGHT:
            return True

    def set_direction(self):
        if self.hspeed > 0:
            self.image = pygame.transform.rotate(self.image, 270)
        elif self.hspeed < 0:
            self.image = pygame.transform.rotate(self.image, 90)
        elif self.vspeed > 0:
            self.image = pygame.transform.rotate(self.image, 180)


def draw_repeating_background(background_img):
    background_rect = background_img.get_rect()
    background_rect_width = background_rect.width
    background_rect_height = background_rect.height
    for i in range(int(math.ceil(WIDTH / background_rect.width))):
        for j in range(int(math.ceil(HEIGHT / background_rect.height))):
            screen.blit(background_img, Rect(i * background_rect_width,
                                             j * background_rect_height,
                                             background_rect_width,
                                             background_rect_height))


def draw_text(text, font, surface, x, y, main_color, background_color=None):
    textobj = font.render(text, True, main_color, background_color)
    textrect = textobj.get_rect()
    textrect.centerx = x
    textrect.centery = y
    surface.blit(textobj, textrect)


def toggle_fullscreen():
    if pygame.display.get_driver() == 'x11':
        pygame.display.toggle_fullscreen()
    else:
        global screen, fullscreen
        screen_copy = screen.copy()
        if fullscreen:
            screen = pygame.display.set_mode((WIDTH, HEIGHT))
        else:
            screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
        fullscreen = not fullscreen
        screen.blit(screen_copy, (0, 0))


def start_screen():
    pygame.mouse.set_cursor(*pygame.cursors.diamond)
    draw_repeating_background(background_start_img)
    title_font = pygame.font.Font('freesansbold.ttf', 65)
    big_font = pygame.font.Font(None, 36)
    default_font = pygame.font.Font(None, 28)
    draw_text(_('HERO DODGE'), title_font, screen,
              WIDTH / 2, HEIGHT / 3, RED, YELLOW)
    draw_text(_('Use o mouse para desviar dos tiros'), big_font, screen,
              WIDTH / 2, HEIGHT / 2, GREEN, BLACK)
    draw_text(_("Aperte qualquer tecla do mouse ou S para iniciar o jogo"),
              default_font, screen, WIDTH / 2, HEIGHT / 1.7, GREEN, BLACK)
    draw_text(_('Pressione F11 para mudar o tamanho da tela'), default_font, screen,
              WIDTH / 2, HEIGHT / 1.1, GREEN, BLACK)
    pygame.display.update()
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
            return 'play'
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:
                return 'play'
            if event.key == K_F11:
                toggle_fullscreen()
        if event.type == QUIT:
            return 'quit'
    return 'start_screen'


def game_loop():
    pygame.mixer.music.play(-1)
    pygame.mouse.set_visible(False)

    square = Block()
    square.set_pos(*pygame.mouse.get_pos())
    bullets = pygame.sprite.Group()
    bonuses = pygame.sprite.Group()
    global score
    global direction
    score = Score()
    min_bullet_speed = 1
    max_bullet_speed = 1
    bullets_per_gust = 1
    odds = 12
    paused = False
    direction = random.randint(1, 4)
    while True:
        pygame.display.update()
        fps_clock.tick(FPS)

        if not paused:
            draw_repeating_background(background_img)

            if score.points >= 1500:
                bullets_per_gust = 3000
                max_bullet_speed = 80
            elif score.points >= 1000:
                bullets_per_gust = 3
                min_bullet_speed = 3
                max_bullet_speed = 15
            elif score.points >= 800:
                max_bullet_speed = 7
            elif score.points >= 500:
                bullets_per_gust = 2
                max_bullet_speed = 6
            elif score.points >= 400:
                min_bullet_speed = 2
            elif score.points >= 300:
                max_bullet_speed = 5
            elif score.points >= 200:
                # The smaller this number is, the probability for a bullet
                # to be shot is higher
                max_bullet_speed = 4
            elif score.points >= 150:
                odds = 10
                max_bullet_speed = 3
            elif score.points >= 100:
                odds = 15
                max_bullet_speed = 2
            elif score.points >= 50:
                odds = 20
                max_bullet_speed = 1

            if random.randint(1, odds) == 1:
                if random.randint(1, odds * 10) == 1:
                    bonus = Bonus(random.randint(30, WIDTH - 30),
                                  random.randint(30, HEIGHT - 30))
                    bonuses.add(bonus)
                for i in range(bullets_per_gust):
                    bullets.add(random_bullet(random.randint(min_bullet_speed,
                                                             max_bullet_speed), score.points, direction))
                    score.points += 1
            draw_text(_('{}  points').format(score.points), default_font, screen,
                      100, 20, DARK_ALLOY_ORANGE)
            draw_text(_('Record: {}').format(score.high_score), default_font,
                      screen, WIDTH - 100, 20, DARK_ALLOY_ORANGE)
            bullets.update()
            bonuses.update()
            bullets.draw(screen)
            bonuses.draw(screen)

            bonus = square.collide(bonuses)
            if square.collide(bullets):
                sound = pygame.mixer.Sound(bullet_fire_sound)
                pygame.mixer.music.stop()
                sound.play()
                if score.high_score > score.highest_score:
                    score.save_highest_score()
                return 'game_over_screen'
            elif bonus:
                score.points += 50
                sound = pygame.mixer.Sound(blip_star)
                sound.play()
                bonus.kill()

            if score.points > score.high_score:
                score.high_score = score.points

            screen.blit(square.img, square.rect)

            for event in pygame.event.get():
                if event.type == pygame.MOUSEMOTION:
                    mouse_pos = pygame.mouse.get_pos()
                    if mouse_pos[0] <= 10:
                        pygame.mouse.set_pos(WIDTH - 10, mouse_pos[1])
                    elif mouse_pos[0] >= WIDTH - 10:
                        pygame.mouse.set_pos(0 + 10, mouse_pos[1])
                    elif mouse_pos[1] <= 10:
                        pygame.mouse.set_pos(mouse_pos[0], HEIGHT - 10)
                    elif mouse_pos[1] >= HEIGHT - 10:
                        pygame.mouse.set_pos(mouse_pos[0], 0 + 10)
                    square.set_pos(*mouse_pos)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    random_x = random.randint(0, WIDTH)
                    random_y = random.randint(0, HEIGHT)
                    square.set_pos(random_x, random_y)
                    pygame.mouse.set_pos([random_x, random_y])
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        paused = not paused
                        if paused:
                            transp_surf = pygame.Surface((WIDTH, HEIGHT))
                            transp_surf.set_alpha(150)
                            screen.blit(transp_surf, transp_surf.get_rect())
                            pygame.mouse.set_visible(True)
                            draw_text(_('Paused'), pygame.font.Font(None, 60), screen,
                                      WIDTH / 2, HEIGHT / 4, RED)
                if event.type == QUIT:
                    return 'quit'
        else:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        paused = not paused
                        pygame.mouse.set_visible(False)
                    elif event.key == pygame.K_F11:
                        toggle_fullscreen()
                if event.type == QUIT:
                    return 'quit'
    # When out of the main loop, the game is over
    return 'game_over_screen'


def game_over_screen():
    global score
    pygame.mouse.set_visible(True)
    draw_repeating_background(background_start_img)
    # Text
    draw_text(_('{}  points').format(score.points), default_font, screen,
              100, 20, GREEN)
    draw_text(_('Record: {}').format(score.high_score), default_font, screen,
              WIDTH - 100, 20, GREEN)
    # Transparent surface
    transp_surf = pygame.Surface((WIDTH, HEIGHT))
    transp_surf.set_alpha(200)
    screen.blit(transp_surf, transp_surf.get_rect())

    draw_text(_("Voce foi atingido :("), pygame.font.Font(None, 40), screen,
              WIDTH / 2, HEIGHT / 3, RED)
    draw_text(_('Aperte qualquer tecla para jogar novamente.'),
              default_font, screen, WIDTH / 2, HEIGHT / 2.1, GREEN)
    draw_text(_('Pressione Q para sair'), default_font, screen,
              WIDTH / 2, HEIGHT / 1.9, GREEN)
    draw_text(_('Pressione F11 para mudar o tamanho da tela'), default_font, screen,
              WIDTH / 2, HEIGHT / 1.1, GREEN, BLACK)

    pygame.display.update()

    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == K_F11:
                toggle_fullscreen()
            if event.key == pygame.K_q:
                return 'quit'
            elif event.key == pygame.K_c:
                return 'play'
        if event.type == pygame.MOUSEBUTTONDOWN:
            return 'play'
        if event.type == QUIT:
            return 'quit'
    return 'game_over_screen'


def main_loop():
    action = 'start_screen'
    score = Score()
    while action != 'quit':
        if action == 'start_screen':
            action = start_screen()
        elif action == 'play':
            action = game_loop()
        elif action == 'game_over_screen':
            action = game_over_screen()
