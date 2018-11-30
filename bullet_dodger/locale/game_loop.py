def game_loop():
    pygame.mixer.music.play(-1)
    pygame.mouse.set_visible(False)

    square = Block()
    square.set_pos(*pygame.mouse.get_pos())
    bullets = pygame.sprite.Group()
    bonuses = pygame.sprite.Group()
    global score
    score = Score()
    min_bullet_speed = 1
    max_bullet_speed = 1
    bullets_per_gust = 1
    odds = 12
    paused = False

    while True:
        pygame.display.update()
        fps_clock.tick(FPS)

        if not paused:
            draw_repeating_background(background_img)

            if score.points >= 2000:
                bullets_per_gust = 3000
                max_bullet_speed = 80
            elif score.points >= 1000:
                bullets_per_gust = 3
                min_bullet_speed = 3
                max_bullet_speed = 15
            elif score.points >= 800:
                max_bullet_speed = 20
            elif score.points >= 600:
                bullets_per_gust = 2
                max_bullet_speed = 10
            elif score.points >= 500:
                min_bullet_speed = 2
            elif score.points >= 400:
                max_bullet_speed = 8
            elif score.points >= 200:
                # The smaller this number is, the probability for a bullet
                # to be shot is higher
                odds = 8
                max_bullet_speed = 5
            elif score.points >= 100:
                odds = 9
                max_bullet_speed = 4
            elif score.points >= 60:
                odds = 10
                max_bullet_speed = 3
            elif score.points >= 30:
                odds = 11
                max_bullet_speed = 2

            if random.randint(1, odds) == 1:
                if random.randint(1, odds * 10) == 1:
                    bonus = Bonus(random.randint(30, WIDTH - 30),
                                  random.randint(30, HEIGHT - 30))
                    bonuses.add(bonus)
                for i in range(bullets_per_gust):
                    bullets.add(random_bullet(random.randint(min_bullet_speed,
                                                             max_bullet_speed)))
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
                score.points += 10
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
