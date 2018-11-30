
def start_screen():
    pygame.mouse.set_cursor(*pygame.cursors.diamond)
    title_font = pygame.font.Font('freesansbold.ttf', 65)
    big_font = pygame.font.Font(None, 36)
    default_font = pygame.font.Font(None, 28)
    draw_text(_('BULLET DODGER'), title_font, screen,
              WIDTH / 2, HEIGHT / 3, RED, YELLOW)
    draw_text(_('Use the mouse to dodge the bullets'), big_font, screen,
              WIDTH / 2, HEIGHT / 2, GREEN, BLACK)
    draw_text(_("Press any mouse button or S when you're ready"),
              default_font, screen, WIDTH / 2, HEIGHT / 1.7, GREEN, BLACK)
    draw_text(_('Press F11 to toggle full screen'), default_font, screen,
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
