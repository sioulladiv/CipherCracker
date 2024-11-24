"""
@author: Noe
@Nono5000
"""

import sys

def update_gui(pygame, agg, plt, gui_height, pkey, nkey, iteration, fitness_score, previous_fscore, pText, pText1, screen, font, fitness_scores):
    if not pygame.get_init():
        return pText, pkey, previous_fscore
        
    if isinstance(pkey, dict):
        previous_key = "".join(pkey.values())
        newkey = "".join(nkey.values())
    else:
        previous_key = "".join(map(str, pkey))
        newkey  = "".join(map(str, nkey))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.display.quit()
            pygame.quit()
            return {
                'text': pText,
                'key': pkey,
                'score': previous_fscore,
                'iterations': iteration
            }

    screen.fill((255, 255, 255))
    text_surface = font.render(previous_key, False, (0, 0, 0))
    text_surface_1 = font.render(newkey, False, (0, 0, 0))
    text_surface_2 = font.render(str(iteration), False, (0, 0, 0))
    text_surface_3 = font.render(str(fitness_score), False, (0, 0, 0))
    text_surface_4 = font.render(str(previous_fscore), False, (0, 0, 0))
    text_surface_5 = font.render(str(pText), False, (0, 0, 0))
    text_surface_6 = font.render(str(pText1), False, (0, 0, 0))
    label1 = font.render('Best Key :', False, (66, 135, 245))
    label2 = font.render('Crnt Key :', False, (66, 135, 245))
    label3 = font.render('Iteration :', False, (255, 0, 0))
    label4 = font.render('Best Score :', False, (66, 135, 245))
    label5 = font.render('Crnt Score :', False, (66, 135, 245))
    label6 = font.render('Best Decrypt :', False, (66, 135, 245))
    label7 = font.render('Crnt Decrypt :', False, (66, 135, 245))

    screen.blit(label1, (10,0))
    screen.blit(label2, (10,20))
    screen.blit(label4, (500,0))
    screen.blit(label5, (500,20))
    screen.blit(label6, (10,50))
    screen.blit(label7, (10,70))
    screen.blit(label3, (10,110))
    screen.blit(text_surface, (170,0))
    screen.blit(text_surface_1, (170,20))
    screen.blit(text_surface_2, (170,110))
    screen.blit(text_surface_3, (650,20))
    screen.blit(text_surface_4, (650,0))
    screen.blit(text_surface_6, (170, 50))
    screen.blit(text_surface_5, (170, 70))
    
    pygame.draw.rect(screen, (0, 255, 0), pygame.Rect(370, 110, 350, 20), 2)
    pygame.draw.rect(screen, (0, 255, 0), pygame.Rect(374, 114, ((previous_fscore-1.6)*342)/-1.2, 12))

    fitness_scores.append(previous_fscore)

    fig = plt.figure(figsize=[7, 3])
    ax = fig.add_subplot(111)
    ax.plot(fitness_scores, color='blue')
    ax.set_ylabel('Fitness Score')
    ax.set_xlabel('Iteration')
    plt.tight_layout(pad=0)
    canvas = agg.FigureCanvasAgg(fig)
    canvas.draw()
    renderer = canvas.get_renderer()
    raw_data = renderer.tostring_rgb()

    size = canvas.get_width_height()
    surf = pygame.image.fromstring(raw_data, size, "RGB")

    screen.blit(surf, (0, gui_height))
    pygame.display.flip()
    plt.close(fig)    
    pygame.display.flip()
