import math, pygame, sys
from constantes import *
from clases import *
from funciones import *


# funciones para la segunda ley
def crear_particula_heladera(masa_actual, min, max):
    # Mapea la masa actual al nivel Y superior del agua
    nivel_superior_y = map_value(masa_actual, MASA_MIN, MASA_MAX, NIVEL_FONDO_HELADERA, NIVEL_TOPE_HELADERA)
    y_start = int(nivel_superior_y)
    y_end = NIVEL_FONDO_HELADERA
    if y_start > y_end:
        y_start = y_end
    # El spawn ocurre entre el nuevo nivel superior y el fondo
    px = random.randint(min, max)
    py = random.randint(y_start, y_end)
    return Particula(px, py, RADIO_PARTICULA, COLOR_FRIO, VELOCIDAD_MAX_INICIAL, TEMP_AMBIENTE, TEMP_EBULLICION)

def crear_particula_freezer(masa_actual, min, max):
    # Mapea la masa actual al nivel Y superior del agua
    nivel_superior_y = map_value(masa_actual, MASA_MIN, MASA_MAX, NIVEL_FONDO_FREEZER, NIVEL_TOPE_FREEZER)
    y_start = int(nivel_superior_y)
    y_end = NIVEL_FONDO_FREEZER
    if y_start > y_end:
        y_start = y_end
    # El spawn ocurre entre el nuevo nivel superior y el fondo
    px = random.randint(min, max)
    py = random.randint(y_start, y_end)
    return Particula(px, py, RADIO_PARTICULA, COLOR_FRIO, VELOCIDAD_MAX_INICIAL, TEMP_AMBIENTE, TEMP_EBULLICION)

# Aca si arranca la cuestion
def segunda_ley(clock):

    heladera_encendida = True
    masa_actual = 1.5
    tiempo_simulado = 0.0
    potencia_heladera = 500
    potencia_max_heladera = 2500
    potencia_min_heladera = 500
    
    heladera_encendida = True
    paredes_heladera = [((268, 254), (573, 254)), ((573, 254), (573, 589)), ((573, 589), (268, 589)), ((268, 589), (268, 254))]
    particulas_heladera = []

    potencia_freezer = 1000
    potencia_max_freezer = 5000
    potencia_min_freezer = 1000
    paredes_freezer = [((268 , 80), (573, 80)), ((573, 80), (573, 220)), ((573, 220), (268, 220)), ((268, 220), (268, 80))]
    particulas_freezer = []

    color_estado = (0, 150, 0) if heladera_encendida else (200, 0, 0)

    # botones
    pot_down_rect_heladera = pygame.Rect(X_MENU_ANCLA, 100, 25, 25)
    pot_up_rect_heladera = pygame.Rect(X_MENU_ANCLA + 30, 100, 25, 25)
    pot_down_rect_freezer = pygame.Rect(X_MENU_ANCLA, 130, 25, 25)
    pot_up_rect_freezer = pygame.Rect(X_MENU_ANCLA + 30, 130, 25, 25)
    masa_down_rect = pygame.Rect(X_MENU_ANCLA, 160, 25, 25)
    masa_up_rect = pygame.Rect(X_MENU_ANCLA + 30, 160, 25, 25)
    texto_plus = FONT_HUD.render("+", True, COLOR_TEXTO_BOTON)
    texto_minus = FONT_HUD.render("-", True, COLOR_TEXTO_BOTON)

    # creo las particulas de la heladera
    cantidad_inicial = int(10)
    for _ in range(cantidad_inicial):
        particulas_heladera.append(crear_particula_heladera(masa_actual, MIN_SPAWN, MAX_SPAWN))

    # Creo tambien las del freezer
    for _ in range(cantidad_inicial):
        particulas_freezer.append(crear_particula_freezer(masa_actual, MIN_SPAWN, MAX_SPAWN))

    particulas_combinadas = particulas_heladera + particulas_freezer

    while True:
        pygame.display.set_caption("Segunda ley - Refrigerador")

        keys = pygame.key.get_pressed()
        dt = clock.tick(120) / 1000.0
    
        # Eventos

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if evento.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()

                    if pot_up_rect_heladera.collidepoint(mouse_pos):
                        if (potencia_heladera < potencia_max_heladera):
                            potencia_heladera += 100
                    elif pot_down_rect_heladera.collidepoint(mouse_pos):
                        if (potencia_heladera > potencia_min_heladera):
                            potencia_heladera -= 100 

                    if pot_up_rect_freezer.collidepoint(mouse_pos):
                        if (potencia_freezer < potencia_max_freezer):
                            potencia_freezer += 100
                    elif pot_down_rect_freezer.collidepoint(mouse_pos):
                        if (potencia_freezer > potencia_min_freezer):
                            potencia_freezer -= 100

                    elif masa_up_rect.collidepoint(mouse_pos):
                        if masa_actual < MASA_MAX:
                            masa_actual += 0.1
                    elif masa_down_rect.collidepoint(mouse_pos):
                        if masa_actual > MASA_MIN + 0.05: 
                            masa_actual -= 0.1

            if keys[pygame.K_q]:
                return

            #if evento.type == pygame.KEYDOWN:
            #    if evento.key == pygame.K_r:
            #        masa_actual = 1.5
            #        tiempo_simulado = 0.0
            #        potencia_heladera = 500
            #        potencia_freezer = 1000
            #        temperatura_actual = TEMP_AMBIENTE # Reinicia el promedio
            #        heladera_encendida = True 
            #        # Resetear partículas (y sus temperaturas individuales)
            #        particulas_heladera.clear() 
            #        particulas_freezer.clear()
            #        for _ in range(cantidad_inicial):
            #            particulas_heladera.append(crear_particula(masa_actual, MIN_SPAWN, MAX_SPAWN))
            #            particulas_freezer.append(crear_particula(masa_actual, MIN_SPAWN, MAX_SPAWN)) 

                #elif evento.key == pygame.K_SPACE:
                #    pava_encendida = not pava_encendida 
                #    if not pava_encendida: # <<<--- DETENER SONIDO AL APAGAR
                #        if SONIDO_HERVIR:
                #            SONIDO_HERVIR.stop()
                #        sonido_hervir_reproduciendose = False


        if heladera_encendida:
            temperatura_actual = actualizar_frio(dt, particulas_combinadas, potencia_heladera, potencia_freezer, masa_actual, heladera_encendida)
            tiempo_simulado += dt
        
        # Manejo de las fisicas de las particulas de la heladera
        for p in particulas_heladera:

            # Mapear la temperatura individual de la partícula a empuje y velocidad máxima
            temp_ratio_individual = (TEMP_AMBIENTE - p.temperatura_individual) / TEMP_AMBIENTE
            temp_ratio_individual = max(0, min(1, temp_ratio_individual))

            max_vel_individual = MAX_VELOCIDAD_TOPE - (temp_ratio_individual * (MAX_VELOCIDAD_TOPE - MAX_VELOCIDAD_BASE))

            for _ in range(SUB_STEPS):
                p.mover(SUB_STEPS) 

                for pared_p1, pared_p2 in paredes_heladera:
                    detectar_y_rebotar_circulo_linea(p, pared_p1, pared_p2)

                p.vy += GRAVEDAD_HELADERA_FREEZER / SUB_STEPS

                velocidad_actual = math.sqrt(p.vx**2 + p.vy**2)
                if velocidad_actual > max_vel_individual:
                    factor = max_vel_individual / velocidad_actual
                    p.vx *= factor
                    p.vy *= factor

            p.update_color(COLOR_CONGELADO, COLOR_FRIO, TEM_MIN_HELADERA, TEMP_AMBIENTE)


        # Manejo de fisicas de las particulas del freezer
        for p in particulas_freezer:

            # Mapear la temperatura individual de la partícula a empuje y velocidad máxima
            temp_ratio_individual = (TEMP_AMBIENTE - p.temperatura_individual) / TEMP_AMBIENTE
            temp_ratio_individual = max(0, min(1, temp_ratio_individual))

            max_vel_individual = MAX_VELOCIDAD_TOPE - (temp_ratio_individual * (MAX_VELOCIDAD_TOPE - MAX_VELOCIDAD_BASE))

            for _ in range(SUB_STEPS):
                p.mover(SUB_STEPS) 

                for pared_p1, pared_p2 in paredes_freezer:
                    detectar_y_rebotar_circulo_linea(p, pared_p1, pared_p2)

                p.vy += GRAVEDAD_HELADERA_FREEZER / SUB_STEPS

                velocidad_actual = math.sqrt(p.vx**2 + p.vy**2)
                if velocidad_actual > max_vel_individual:
                    factor = max_vel_individual / velocidad_actual
                    p.vx *= factor
                    p.vy *= factor

            p.update_color(COLOR_CONGELADO, COLOR_FRIO, TEM_MIN_FREEZER, TEMP_AMBIENTE)

        # Dibujo las cuestiones
        SCREEN.blit(FONDO_IMG, (0, 0))
        SCREEN.blit(pygame.transform.scale(MESA_IMG, (1500, 1200)), (-600, 400))

        # dibujo los botones
        pygame.draw.rect(SCREEN, COLOR_BOTON, pot_up_rect_heladera)
        pygame.draw.rect(SCREEN, COLOR_BOTON, pot_down_rect_heladera)
        pygame.draw.rect(SCREEN, COLOR_BOTON, pot_up_rect_freezer)
        pygame.draw.rect(SCREEN, COLOR_BOTON, pot_down_rect_freezer)
        pygame.draw.rect(SCREEN, COLOR_BOTON, masa_up_rect)
        pygame.draw.rect(SCREEN, COLOR_BOTON, masa_down_rect)

        # texto 
        SCREEN.blit(texto_plus, (pot_up_rect_heladera.x + 7, pot_up_rect_heladera.y + 2))
        SCREEN.blit(texto_minus, (pot_down_rect_heladera.x + 8, pot_down_rect_heladera.y + 2))
        SCREEN.blit(texto_plus, (pot_up_rect_freezer.x + 7, pot_up_rect_freezer.y + 2))
        SCREEN.blit(texto_minus, (pot_down_rect_freezer.x + 8, pot_down_rect_freezer.y + 2))
        SCREEN.blit(texto_plus, (masa_up_rect.x + 7, masa_up_rect.y + 2))
        SCREEN.blit(texto_minus, (masa_down_rect.x + 8, masa_down_rect.y + 2))

        texto_temp = FONT_HUD.render(f"Temp Prom: {temperatura_actual:.1f}°C", True, COLOR_TEXTO_1)
        texto_tiempo = FONT_HUD.render(f"Tiempo: {tiempo_simulado:.1f} s", True, COLOR_TEXTO_1)
        texto_potencia_heladera = FONT_HUD.render(f"Potencia Heladera: {potencia_heladera:.0f} W", True, COLOR_TEXTO_1)
        texto_potencia_freezer = FONT_HUD.render(f"Potencia Freezer: {potencia_freezer:.0f} W", True, COLOR_TEXTO_1)
        texto_masa = FONT_HUD.render(f"Masa: {masa_actual:.1f} kg", True, COLOR_TEXTO_1)
        #texto_estado = FONT_HUD.render(f"Estado: {'ENCENDIDA' if heladera_encendida else 'APAGADA'}", True, color_estado)
        #texto_reset = FONT_HUD.render("Presiona 'R' para reiniciar", True, COLOR_TEXTO_2)
        #texto_toggle = FONT_HUD.render("[ESPACIO] para On/Off", True, COLOR_TEXTO_2)
        texto_salir = FONT_HUD.render("'Q' para salir", True, COLOR_TEXTO_2)
        texto_ambiente = FONT_HUD.render(f"T. Ambiente: {TEMP_AMBIENTE:.1f}°C", True, COLOR_TEXTO_3)
        texto_linea = FONT_HUD.render("--------------------------------------------------------", True, COLOR_TEXTO_3)
        texto_calculo_deltaU_heladera = FONT_HUD.render(f"Energia Heladera ---> ΔU = {(potencia_heladera * tiempo_simulado):.1f} J", True, COLOR_TEXTO_1)
        texto_calculo_deltaU_freezer = FONT_HUD.render(f"Energia Freezer ---> ΔU = {(potencia_freezer * tiempo_simulado):.1f} J", True, COLOR_TEXTO_1)

        SCREEN.blit(HELADERA_IMG_ESCALADA, (200, 0))
        SCREEN.blit(texto_temp, (X_MENU_ANCLA, 40))
        SCREEN.blit(texto_tiempo, (X_MENU_ANCLA, 70))
        SCREEN.blit(texto_potencia_heladera, (X_MENU_ANCLA + 65, 105))
        SCREEN.blit(texto_potencia_freezer, (X_MENU_ANCLA + 65, 135))
        SCREEN.blit(texto_masa, (X_MENU_ANCLA + 65, 165))   
        #SCREEN.blit(texto_estado, (X_MENU_ANCLA, 195))
        #SCREEN.blit(texto_reset, (X_MENU_ANCLA, 225))
        #SCREEN.blit(texto_toggle, (X_MENU_ANCLA, 255))
        SCREEN.blit(texto_salir, (X_MENU_ANCLA, 195))
        SCREEN.blit(texto_ambiente, (X_MENU_ANCLA, 225))
        SCREEN.blit(texto_linea, (X_MENU_ANCLA, 255))
        SCREEN.blit(texto_calculo_deltaU_heladera, (X_MENU_ANCLA, 285))
        SCREEN.blit(texto_calculo_deltaU_freezer, (X_MENU_ANCLA, 315))

        for i, j in paredes_heladera:
            pygame.draw.line(SCREEN, (255, 255, 255), i, j, 3)

        for i, j in paredes_freezer:
            pygame.draw.line(SCREEN, (255, 255, 255), i, j, 3)

        for p in particulas_heladera:
            p.dibujar(SCREEN)

        for p in particulas_freezer:
            p.dibujar(SCREEN)

        pygame.display.update()