import math
import random
import sys

import pygame

import os
PAVA_IMG = pygame.image.load('Imagenes/pava.png')
MESA_IMG = pygame.image.load('Imagenes/mesa.png')
FONDO_IMG = pygame.image.load('Imagenes/pizarra_fondo.jpg')
PAVA_IMG_ESCALADA = pygame.transform.scale(PAVA_IMG, (500, 500))
# --- PANTALLA ---
ANCHO, ALTO = 1280, 720
FPS = 120
TITULO = "Simulación Termodinámica"

# --- RUTAS ---
RUTA_IMAGEN_PAVA = os.path.join('imagenes', 'pava.webp')
RUTA_SONIDO_HERVIR = os.path.join('sonidos', 'boiling.wav')

# --- COLORES ---
COLOR_FONDO = (255, 255, 255); COLOR_PAREDES = (0, 0, 0)
COLOR_FRIO = (0, 100, 255); COLOR_TIBIO = (255, 255, 0)
COLOR_CALIENTE = (255, 0, 0); COLOR_VAPOR = (210, 210, 210)
COLOR_BOTON = (220, 220, 220); COLOR_BOTON_ACTIVO = (100, 200, 100); COLOR_TEXTO_BOTON = (0, 0, 0)

# --- CONSTANTES TERMODINÁMICAS ---
CALOR_ESPECIFICO_AGUA = 4186
TEMP_AMBIENTE = 20.0; TEMP_MATE = 80.0; TEMP_HERVIR = 100.0
CALOR_LATENTE_VAPORIZACION = 2260000

# Aislamiento térmico realista (casi no pierde calor por las paredes)
K_ENFRIAMIENTO_PARTICULA = 0.0001 

# --- CONSTANTES FÍSICAS ---
GRAVEDAD = 0.015
SUB_STEPS = 8

# Margen de flotabilidad ajustado:

MAX_EMPUJE_CALOR_PARTICULA = 0.020

MAX_VELOCIDAD_BASE = 1.5; MAX_VELOCIDAD_TOPE = 5.0
POTENCIA_FIJA = 2500.0 

# --- PARÁMETROS DE SIMULACIÓN ---
MASA_MIN = 0.5; MASA_MAX = 2.0
PARTICULAS_POR_KG = 300 
RADIO_PARTICULA = 6
VIDA_PARTICULA_VAPOR = 2.5; PARTICULAS_VAPOR_POR_LIQUIDA = 3

# --- GEOMETRÍA ---
Y_NIVEL_FONDO = 445; Y_NIVEL_TOPE = 130
ZONA_CALOR_Y = 430
MIN_X_SPAWN = 265; MAX_X_SPAWN = 500

PAREDES_ESTATICAS = [
    ((260, 150), (505, 150)), ((505, 150), (520, 200)), ((520, 200), (535, 300)),
    ((535, 300), (550, 450)), ((230, 450), (245, 300)), ((245, 300), (260, 150)),
]
import random
import pygame
class Particula:
    def __init__(self, x, y, vel_max_ini):
        self.x = x
        self.y = y
        self.radio = RADIO_PARTICULA
        self.color = COLOR_FRIO
        # Velocidad inicial aleatoria
        self.vx = random.uniform(-vel_max_ini, vel_max_ini)
        self.vy = random.uniform(-vel_max_ini, vel_max_ini)
        
        self.temperatura = TEMP_AMBIENTE
        
    def mover(self, divisor_pasos):
        self.x += self.vx / divisor_pasos
        self.y += self.vy / divisor_pasos
        # Si la partícula está caliente, vibra un poco. 
        # Esto evita que se apilen estáticamente en el fondo.
        if self.temperatura > 60: # Solo si está algo caliente
            import random  # Asegurate de importar random arriba
            agitacion = 0.5 # Fuerza de la vibración
            self.x += random.uniform(-agitacion, agitacion)
            self.y += random.uniform(-agitacion, agitacion)
    def update_color(self):
        """Actualiza color basado en temperatura individual."""
        ratio = (self.temperatura - TEMP_AMBIENTE) / (TEMP_HERVIR - TEMP_AMBIENTE)
        ratio = max(0, min(1, ratio))
        
        r = int(COLOR_FRIO[0] + (COLOR_CALIENTE[0] - COLOR_FRIO[0]) * ratio)
        g = int(COLOR_FRIO[1] + (COLOR_CALIENTE[1] - COLOR_FRIO[1]) * ratio)
        b = int(COLOR_FRIO[2] + (COLOR_CALIENTE[2] - COLOR_FRIO[2]) * ratio)
        self.color = (r, g, b)

    def dibujar(self, superficie):
        pygame.draw.circle(superficie, self.color, (int(self.x), int(self.y)), self.radio)

class ParticulaVapor:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radio = random.randint(4, 7)
        self.color = COLOR_VAPOR
        self.vx = random.uniform(-0.4, 0.4)
        self.vy = random.uniform(-1.2, -0.7) # Hacia arriba
        
        self.vida_total = VIDA_PARTICULA_VAPOR + random.uniform(-0.5, 0.5)
        self.vida_restante = self.vida_total
        self.viva = True
        self.surface = pygame.Surface((self.radio * 2, self.radio * 2), pygame.SRCALPHA)

    def update(self, dt):
        self.vida_restante -= dt
        if self.vida_restante <= 0:
            self.viva = False
            return
        self.x += self.vx
        self.y += self.vy

    def dibujar(self, superficie):
        if not self.viva: return
        
        ratio = self.vida_restante / self.vida_total
        alpha = int(150 * ratio)
        alpha = max(0, min(alpha, 255))
        
        self.surface.fill((0, 0, 0, 0))
        pygame.draw.circle(self.surface, (*self.color, alpha), (self.radio, self.radio), self.radio)
        superficie.blit(self.surface, (int(self.x - self.radio), int(self.y - self.radio)))
import pygame




class Slider:
    def __init__(self, x, y, w, h, min_val, max_val, start_val, label):
        self.rect = pygame.Rect(x, y, w, h)
        self.min_val = min_val
        self.max_val = max_val
        self.val = start_val
        self.label = label
        self.dragging = False
        self.font = pygame.font.Font(None, 24)
        
        self.handle_rect = pygame.Rect(x, y - 5, 10, h + 10)
        self.update_handle_pos()

    def update_handle_pos(self):
        ratio = (self.val - self.min_val) / (self.max_val - self.min_val)
        self.handle_rect.centerx = self.rect.x + ratio * self.rect.width

    def manejar_evento(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.handle_rect.collidepoint(event.pos) or self.rect.collidepoint(event.pos):
                self.dragging = True
                self.update_val_from_mouse(event.pos[0])
                
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
            
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.update_val_from_mouse(event.pos[0])

    def update_val_from_mouse(self, mouse_x):
        x = max(self.rect.left, min(mouse_x, self.rect.right))
        ratio = (x - self.rect.left) / self.rect.width
        self.val = self.min_val + ratio * (self.max_val - self.min_val)
        self.update_handle_pos()

    def dibujar(self, screen):
        # Fondo
        pygame.draw.rect(screen, (180, 180, 180), self.rect, border_radius=5)
        # Relleno activo
        active_rect = pygame.Rect(self.rect.x, self.rect.y, self.handle_rect.centerx - self.rect.x, self.rect.height)
        pygame.draw.rect(screen, (100, 150, 255), active_rect, border_radius=5)
        
        # Mango
        color_handle = (50, 100, 200) if self.dragging else (100, 100, 100)
        pygame.draw.rect(screen, color_handle, self.handle_rect, border_radius=2)
        
        # --- FORMATEO DEL TEXTO ---
        val_str = f"{self.val:.1f}"
        if "Potencia" in self.label: 
            val_str = f"{self.val:.0f} W"
        elif "Ambiente" in self.label: 
            val_str = f"{self.val:.1f} °C"
        elif "Corte" in self.label: 
            val_str = f"{self.val:.0f} °C"
        elif "Aislamiento" in self.label: 
            val_str = f"k = {self.val:.5f}"
            
        lbl_surf = self.font.render(f"{self.label}: {val_str}", True, (255,255,255))
        screen.blit(lbl_surf, (self.rect.x, self.rect.y - 18))

class HUD:
    def __init__(self):
        self.font = pygame.font.Font(None, 30)
        self.font_small = pygame.font.Font(None, 24)
        self.font_formula = pygame.font.SysFont("arial", 20) 
        self.x_anchor = 750
        
        # Botones
        self.btn_mate = pygame.Rect(self.x_anchor, 80, 100, 30)
        self.btn_hervir = pygame.Rect(self.x_anchor + 110, 80, 100, 30)
        self.btn_manual = pygame.Rect(self.x_anchor + 220, 80, 100, 30)

    
        # 1. Temp. de Corte
        self.slider_target = Slider(self.x_anchor, 510, 200, 10, 20, 100, 80, "Temp. Corte")
        # 2. Potencia
        self.slider_potencia = Slider(self.x_anchor, 570, 200, 10, 0, 3000, POTENCIA_FIJA, "Potencia")
        # 3. Temp. Ambiente
        self.slider_ambiente = Slider(self.x_anchor, 630, 200, 10, 0, 40, TEMP_AMBIENTE, "Temp. Ambiente")
        # 4. Aislamiento
        self.slider_aislamiento = Slider(self.x_anchor, 690, 200, 10, 0.0, 0.02, K_ENFRIAMIENTO_PARTICULA, "Aislamiento")

    def manejar_eventos_input(self, event, modo_actual, modo_manual_activo):
        nuevo_modo = modo_actual
        nuevo_estado_manual = modo_manual_activo

        # Solo activar sliders en modo manual
        if modo_manual_activo:
            self.slider_target.manejar_evento(event)
            self.slider_potencia.manejar_evento(event)
            self.slider_ambiente.manejar_evento(event)
            self.slider_aislamiento.manejar_evento(event)

        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            if self.btn_mate.collidepoint(pos):
                nuevo_modo = TEMP_MATE
                nuevo_estado_manual = False
            elif self.btn_hervir.collidepoint(pos):
                nuevo_modo = TEMP_HERVIR
                nuevo_estado_manual = False
            elif self.btn_manual.collidepoint(pos):
                nuevo_estado_manual = True 
                
        return nuevo_modo, nuevo_estado_manual

    def dibujar(self, screen, data):
        
        mouse_pos = pygame.mouse.get_pos()
        tooltip_a_mostrar = None 
        
    
        # Colores botones
        color_mate = COLOR_BOTON_ACTIVO if (data['target_temp'] == TEMP_MATE and not data['modo_manual']) else COLOR_BOTON
        color_hervir = COLOR_BOTON_ACTIVO if (data['target_temp'] == TEMP_HERVIR and not data['modo_manual']) else COLOR_BOTON
        color_manual = COLOR_BOTON_ACTIVO if data['modo_manual'] else COLOR_BOTON
        
        pygame.draw.rect(screen, color_mate, self.btn_mate)
        pygame.draw.rect(screen, color_hervir, self.btn_hervir)
        pygame.draw.rect(screen, color_manual, self.btn_manual)
        
        txt_mate = self.font_small.render("MATE (80°)", True, (0,0,0))
        txt_hervir = self.font_small.render("HERVIR", True, (0,0,0))
        txt_manual = self.font_small.render("MANUAL", True, (0,0,0))
        
        screen.blit(txt_mate, (self.btn_mate.x + 5, self.btn_mate.y + 7))
        screen.blit(txt_hervir, (self.btn_hervir.x + 15, self.btn_hervir.y + 7))
        screen.blit(txt_manual, (self.btn_manual.x + 15, self.btn_manual.y + 7))

        # --- DIBUJAR SLIDERS ---
        if data['modo_manual']:
            self.slider_target.dibujar(screen)
            self.slider_potencia.dibujar(screen)
            self.slider_ambiente.dibujar(screen)
            self.slider_aislamiento.dibujar(screen)

        # --- DATOS ---
        color_estado = (0, 150, 0) if data['encendida'] else (200, 0, 0)
        estado_txt = "ENCENDIDA" if data['encendida'] else "APAGADA"
        
        if not data['encendida'] and data['temp'] >= data['target_temp'] - 2.0:
             estado_txt = "LISTO"
             color_estado = (0, 100, 200)

        if abs(data['delta_u']) < 10000: du_str = f"{data['delta_u']:.0f}"
        else: du_str = f"{data['delta_u']/1000:.1f}k"
        def fmt_j(valor): return f"{valor:.0f}" if valor < 10000 else f"{valor/1000:.1f}k"

        potencia_mostrar = data['potencia_actual']
        
        if data['modo_manual']:
            str_objetivo = f"MANUAL ({data['target_temp']:.0f}°C)"
        else:
            str_objetivo = f"{data['target_temp']:.0f}°C"

        info = [
            (f"Temp Agua: {data['temp']:.1f}°C", 20),
            (f"Objetivo: {str_objetivo}", 50),
            (f"Masa: {data['masa']:.2f} kg", 130),
            (f"Potencia: {potencia_mostrar:.0f} W", 155),

            (f"ΔU (1° Ley): {du_str} J", 190, 0, (0, 0, 150), "FORMULA_1"),
            (f"ΔS (2° Ley): {data['delta_s']:.1f} J/K", 220, 0, (100, 0, 100), "FORMULA_2"),

            (f"Q_p (Total): {fmt_j(data['q_p'])} J", 260, 0, (255,255,255), "FORMULA_QP"),
            (f"Q_a (Agua): {fmt_j(data['q_a'])} J", 285, 0, (255,255,255), "FORMULA_QA"),
            (f"Q_l (Vapor): {fmt_j(data['q_l'])} J", 310, 0, (255,255,255), "FORMULA_QL"),

            (f"Estado: {estado_txt}", 350, 0, color_estado),
            (f"Tiempo: {data['tiempo']:.1f} s", 380),
            
            ("Presiona 'R' para reiniciar", 410, 0, (50,50,50)),
            ("Presiona 'ESC' para menú", 430, 0, (50,50,50)),
            ("[ESPACIO] ON/OFF", 450, 0, (50,50,50)),
        
        
        ]
        
        for item in info:
            texto = item[0]
            y = item[1]
            offset_x = item[2] if len(item) > 2 else 0
            color = item[3] if len(item) > 3 else (255,255,255)
            
            surf = self.font.render(texto, True, color)
            rect_texto = screen.blit(surf, (self.x_anchor + offset_x, y))

            if len(item) > 4:
                tag = item[4]
                if rect_texto.collidepoint(mouse_pos):
                    if tag == "FORMULA_1": tooltip_a_mostrar = "ΔU = Q - W (Energía Interna)"
                    elif tag == "FORMULA_2": tooltip_a_mostrar = "ΔS = m · c · ln(Tf / Ti)"
                    elif tag == "FORMULA_QP": tooltip_a_mostrar = f"Qp = P({potencia_mostrar:.0f}W) * Tiempo"
                    elif tag == "FORMULA_QA": tooltip_a_mostrar = "Qa = m * c * ΔT"
                    elif tag == "FORMULA_QL": tooltip_a_mostrar = "Ql = m_vap * L_vap"

        if tooltip_a_mostrar:
            self.dibujar_tooltip(screen, tooltip_a_mostrar, mouse_pos)

    def dibujar_tooltip(self, screen, texto, pos):
        padding = 5
        surf_texto = self.font_formula.render(texto, True, (0, 0, 0))
        bg_rect = surf_texto.get_rect()
        bg_rect.topleft = (pos[0] + 15, pos[1] + 15)
        bg_rect.width += padding * 2; bg_rect.height += padding * 2
        pygame.draw.rect(screen, (255, 255, 220), bg_rect) 
        pygame.draw.rect(screen, (0, 0, 0), bg_rect, 1)
        screen.blit(surf_texto, (bg_rect.x + padding, bg_rect.y + padding))


class MenuPrincipal:
    def __init__(self):
        self.font_titulo = pygame.font.Font(None, 80)
        self.font_botones = pygame.font.Font(None, 50)
        self.font_footer = pygame.font.Font(None, 24) 
        center_x = ANCHO // 2; start_y = 300
        self.btn_iniciar = pygame.Rect(center_x - 100, start_y, 200, 50)
        self.btn_teoria = pygame.Rect(center_x - 100, start_y + 80, 200, 50)
        self.btn_salir = pygame.Rect(center_x - 100, start_y + 160, 200, 50)
        self.integrantes = ["Integrantes:", "Burgos Pablo", "Genaro de Boni", "Eula Maximiliano", "Sajnovsky Jose"]

    def dibujar(self, screen):
        screen.fill(COLOR_FONDO)
        titulo = self.font_titulo.render("Simulación Termodinámica", True, (0, 0, 0))
        rect_titulo = titulo.get_rect(center=(ANCHO//2, 150))
        screen.blit(titulo, rect_titulo)
        botones = [(self.btn_iniciar, "Iniciar", (100, 200, 100)), (self.btn_teoria, "Teoría", (100, 150, 255)), (self.btn_salir, "Salir", (255, 100, 100))]
        for rect, texto, color in botones:
            pygame.draw.rect(screen, color, rect, border_radius=10)
            pygame.draw.rect(screen, (255,255,255), rect, 2, border_radius=10)
            surf = self.font_botones.render(texto, True, (255, 255, 255))
            text_rect = surf.get_rect(center=rect.center)
            screen.blit(surf, text_rect)
        start_y_nombres = ALTO - 20 - (len(self.integrantes) * 20) 
        for i, linea in enumerate(self.integrantes):
            surf_nombre = self.font_footer.render(linea, True, (80, 80, 80)) 
            screen.blit(surf_nombre, (20, start_y_nombres + (i * 20)))

    def manejar_clic(self, pos):
        if self.btn_iniciar.collidepoint(pos): return "SIMULACION"
        if self.btn_teoria.collidepoint(pos): return "TEORIA"
        if self.btn_salir.collidepoint(pos): return "SALIR"
        return None

class PantallaTeoria:
    def __init__(self):
        self.font_titulo = pygame.font.Font(None, 60)
        self.font_texto = pygame.font.Font(None, 32)
        self.font_boton = pygame.font.Font(None, 40)
        self.btn_volver = pygame.Rect(50, ALTO - 80, 150, 50)
        self.textos = [
            "Primera Ley de la Termodinámica (Conservación de la Energía):",
            "La energía no se crea ni se destruye, solo se transforma.",
            "En esta simulación, la energía eléctrica de la pava se transforma en calor",
            "(Efecto Joule), aumentando la energía interna del agua (su temperatura).",
            "Al llegar a 100°C, la energía se usa para romper enlaces (Calor Latente),",
            "convirtiendo el líquido en vapor sin aumentar más la temperatura.",
            "",
            "Segunda Ley de la Termodinámica (Entropía):",
            "El calor fluye espontáneamente del cuerpo caliente (resistencia) al frío (agua).",
            "El proceso de ebullición aumenta el desorden molecular (Entropía).",
            "Es un proceso irreversible: no podemos juntar el vapor para recuperar",
            "la electricidad original fácilmente."
        ]
    def dibujar(self, screen):
        screen.fill((240, 240, 250)) 
        titulo = self.font_titulo.render("Teoría Aplicada", True, (0, 0, 0))
        screen.blit(titulo, (50, 50))
        y = 120
        for linea in self.textos:
            color = (0, 0, 150) if "Ley" in linea else (50, 50, 50)
            surf = self.font_texto.render(linea, True, color)
            screen.blit(surf, (50, y)); y += 35
        pygame.draw.rect(screen, (100, 100, 100), self.btn_volver, border_radius=10)
        txt = self.font_boton.render("Volver", True, (255, 255, 255))
        screen.blit(txt, txt.get_rect(center=self.btn_volver.center))
    def manejar_clic(self, pos):
        if self.btn_volver.collidepoint(pos): return "MENU"
        return None
import math




def map_value(value, from_low, from_high, to_low, to_high):
    """Mapea un valor de un rango a otro."""
    value = max(from_low, min(from_high, value))
    return to_low + (value - from_low) * (to_high - to_low) / (from_high - from_low)

def generar_paredes_pava():
    """Genera la lista completa de paredes incluyendo el arco inferior."""
    paredes = list(PAREDES_ESTATICAS) 
    puntos_del_arco = []
    num_segmentos = 10
    centro_x_arco = 390; centro_y_arco = 450; radio_x_arco = 165; radio_y_arco = 50
    
    for i in range(num_segmentos + 1):
        angulo = (i / num_segmentos) * math.pi
        x = centro_x_arco + radio_x_arco * math.cos(angulo + math.pi)
        y = centro_y_arco + radio_y_arco * math.sin(angulo)
        puntos_del_arco.append((int(x), int(y)))
        
    for i in range(num_segmentos):
        paredes.append((puntos_del_arco[i], puntos_del_arco[i+1]))
        
    paredes.append(((230, 450), puntos_del_arco[0]))
    paredes.append(((550, 450), puntos_del_arco[-1]))
    return paredes

def detectar_y_rebotar_circulo_linea(particula, p1, p2):
    """Lógica de colisión matemática."""
    dx_line = p2[0] - p1[0]
    dy_line = p2[1] - p1[1]
    longitud_cuadrada = dx_line**2 + dy_line**2
    
    if longitud_cuadrada == 0: return

    t = ((particula.x - p1[0]) * dx_line + (particula.y - p1[1]) * dy_line) / longitud_cuadrada
    t = max(0, min(1, t))
    
    punto_cercano_x = p1[0] + t * dx_line
    punto_cercano_y = p1[1] + t * dy_line
    
    dist_x = particula.x - punto_cercano_x
    dist_y = particula.y - punto_cercano_y
    distancia = math.sqrt(dist_x**2 + dist_y**2)
    
    if 0.001 < distancia < particula.radio:
        normal_x = dist_x / distancia
        normal_y = dist_y / distancia
        overlap = particula.radio - distancia
        
        particula.x += normal_x * overlap
        particula.y += normal_y * overlap
        
        dot_product = particula.vx * normal_x + particula.vy * normal_y
        particula.vx -= 2 * dot_product * normal_x
        particula.vy -= 2 * dot_product * normal_y
        particula.vx *= 0.99
        particula.vy *= 0.99

def pava_nueva(clock, SCREEN):
    print ("ENTRE a PRIMERA LEY")
    # Inicialización Global
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption(TITULO)
    clock = pygame.time.Clock()

    class SimulacionPava:
        def __init__(self, screen_ref):
            self.screen = screen_ref
            self.hud = HUD()
            
            try:
                img = pygame.image.load(RUTA_IMAGEN_PAVA)
                self.img_pava = pygame.transform.scale(img, (500, 500))
            except Exception as e:
                print(f"Advertencia: No se pudo cargar la imagen ({e})")
                self.img_pava = None

            try:
                self.snd_hervir = pygame.mixer.Sound(RUTA_SONIDO_HERVIR)
                self.snd_hervir.set_volume(0.5)
            except Exception as e:
                print(f"Advertencia: No se pudo cargar el sonido ({e})")
                self.snd_hervir = None

            self.paredes = generar_paredes_pava()
            self.resetear_simulacion()

        def resetear_simulacion(self):
            self.masa_agua = 1.0 # Valor fijo por defecto
            self.masa_inicial = self.masa_agua
            self.temperatura_promedio = TEMP_AMBIENTE
            self.tiempo_sim = 0.0
            self.encendida = True
            self.hirviendo = False
            self.snd_reproduciendo = False
            self.target_temp = TEMP_HERVIR 
            
            self.modo_manual = False
            self.potencia_actual = POTENCIA_FIJA
            self.temp_ambiente_actual = TEMP_AMBIENTE
            self.k_aislamiento_actual = K_ENFRIAMIENTO_PARTICULA
            
            self.particulas = []
            self.vapores = []
            self.masa_vaporizada_acum = 0.0

            self.delta_u = 0.0 
            self.delta_s = 0.0 
            
            if self.snd_hervir: self.snd_hervir.stop()
            self.ajustar_cantidad_particulas()
            
            # Resetear sliders
            self.hud.slider_target.val = 80 # Default manual objetivo
            self.hud.slider_potencia.val = POTENCIA_FIJA
            self.hud.slider_ambiente.val = TEMP_AMBIENTE
            self.hud.slider_aislamiento.val = K_ENFRIAMIENTO_PARTICULA
            
            self.hud.slider_target.update_handle_pos()
            self.hud.slider_potencia.update_handle_pos()
            self.hud.slider_ambiente.update_handle_pos()
            self.hud.slider_aislamiento.update_handle_pos()

        def ajustar_cantidad_particulas(self):
            target_count = int(self.masa_agua * PARTICULAS_POR_KG)
            diff = target_count - len(self.particulas)
            if diff > 0:
                for _ in range(diff): self.crear_particula()
            elif diff < 0:
                for _ in range(abs(diff)):
                    if self.particulas: self.particulas.pop()

        def crear_particula(self):
            lvl_top = map_value(self.masa_agua, MASA_MIN, MASA_MAX, Y_NIVEL_FONDO, Y_NIVEL_TOPE)
            y_start = int(lvl_top)
            y_end = Y_NIVEL_FONDO
            if y_start > y_end: y_start = y_end
            px = random.randint(MIN_X_SPAWN, MAX_X_SPAWN)
            py = random.randint(y_start, y_end)
            
            temp_ini = self.temperatura_promedio if self.particulas else self.temp_ambiente_actual
            self.particulas.append(Particula(px, py, 1.0))
            self.particulas[-1].temperatura = temp_ini

        def crear_vapor(self):
            lvl_top = map_value(self.masa_agua, MASA_MIN, MASA_MAX, Y_NIVEL_FONDO, Y_NIVEL_TOPE)
            px = random.randint(MIN_X_SPAWN + 20, MAX_X_SPAWN - 20)
            py = lvl_top + random.uniform(-5, 5)
            self.vapores.append(ParticulaVapor(px, py))

        def manejar_eventos(self, event):
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r: 
                    self.resetear_simulacion()
                elif event.key == pygame.K_SPACE:
                    self.encendida = not self.encendida
                    if not self.encendida and self.snd_hervir:
                        self.snd_hervir.stop()
                        self.snd_reproduciendo = False
                elif event.key == pygame.K_ESCAPE:
                    if self.snd_hervir: self.snd_hervir.stop()
                    return "MENU"

            nuevo_modo, nuevo_manual = self.hud.manejar_eventos_input(event, self.target_temp, self.modo_manual)
            
            if nuevo_modo != self.target_temp:
                self.target_temp = nuevo_modo
                if not self.encendida and self.temperatura_promedio < self.target_temp:
                    self.encendida = True
            
            self.modo_manual = nuevo_manual
            
            if self.modo_manual:
                # En modo manual, el "Target Temp" viene del slider
                self.target_temp = self.hud.slider_target.val
                
                self.potencia_actual = self.hud.slider_potencia.val
                self.temp_ambiente_actual = self.hud.slider_ambiente.val
                self.k_aislamiento_actual = self.hud.slider_aislamiento.val
            else:
                self.potencia_actual = POTENCIA_FIJA
                self.temp_ambiente_actual = TEMP_AMBIENTE
                self.k_aislamiento_actual = K_ENFRIAMIENTO_PARTICULA
                
            return None

        def update(self, dt):
            self.update_fisica(dt)

        def update_fisica(self, dt):
            if not self.particulas: return
            nivel_agua_y = map_value(self.masa_agua, MASA_MIN, MASA_MAX, Y_NIVEL_FONDO, Y_NIVEL_TOPE)

            # --- LÓGICA DE CORTE AUTOMÁTICO (TERMOSTATO) ---
            if self.encendida:
                # Si estamos en modo manual, usamos el target del slider
                if self.modo_manual:
                    if self.temperatura_promedio >= self.target_temp:
                        self.encendida = False
                # Si NO estamos en manual, usamos la lógica de los presets
                else:
                    if self.target_temp == TEMP_MATE and self.temperatura_promedio >= TEMP_MATE:
                        self.encendida = False
                    # (Nota: El modo HERVIR preset por defecto NO corta, sigue hirviendo como pava vieja)

            # --- A. TERMODINÁMICA ---
            potencia_aplicada = self.potencia_actual if self.encendida else 0
            perdida_total = 0
            masa_p = self.masa_agua / len(self.particulas)
            particulas_calor = [p for p in self.particulas if p.y > ZONA_CALOR_Y]
            
            pot_por_particula = 0
            if particulas_calor and self.encendida:
                pot_por_particula = potencia_aplicada / len(particulas_calor)

            temp_acum = 0
            for p in self.particulas:
                # Enfriamiento con aislamiento dinámico y temperatura ambiente dinámica
                if p.temperatura > self.temp_ambiente_actual:
                    p_perdida = self.k_aislamiento_actual * (p.temperatura - self.temp_ambiente_actual)
                    perdida_total += p_perdida
                    dT = (p_perdida * dt) / (masa_p * CALOR_ESPECIFICO_AGUA)
                    p.temperatura = max(self.temp_ambiente_actual, p.temperatura - dT)
                
                if self.encendida and p in particulas_calor:
                    dT = (pot_por_particula * dt) / (masa_p * CALOR_ESPECIFICO_AGUA)
                    p.temperatura = min(TEMP_HERVIR, p.temperatura + dT)
                
                if p.y < nivel_agua_y + 15:
                    p.temperatura -= 0.002 
                    p.temperatura = max(self.temp_ambiente_actual, p.temperatura)
                
                temp_acum += p.temperatura
                p.update_color()

            self.temperatura_promedio = temp_acum / len(self.particulas)
            
            potencia_neta = potencia_aplicada - perdida_total
            dq = potencia_neta * dt
            self.delta_u += dq
            
            temp_kelvin = self.temperatura_promedio + 273.15
            if temp_kelvin > 0:
                self.delta_s += dq / temp_kelvin

            self.hirviendo = self.temperatura_promedio >= (TEMP_HERVIR - 0.5)

            # --- B. VAPORIZACIÓN ---
            if self.hirviendo:
                if self.encendida and self.snd_hervir and not self.snd_reproduciendo:
                    self.snd_hervir.play(loops=-1)
                    self.snd_reproduciendo = True
                
                pot_neta = potencia_aplicada - perdida_total
                if pot_neta > 0 and self.masa_agua > 0 and self.encendida:
                    masa_vap = (pot_neta * dt) / CALOR_LATENTE_VAPORIZACION
                    self.masa_agua = max(0, self.masa_agua - masa_vap)
                    self.masa_vaporizada_acum += masa_vap
                    n_vap = int(self.masa_vaporizada_acum * PARTICULAS_POR_KG)
                    if n_vap > 0:
                        self.masa_vaporizada_acum -= n_vap / PARTICULAS_POR_KG
                        self.particulas.sort(key=lambda x: x.temperatura)
                        for _ in range(min(n_vap, len(self.particulas))):
                            self.particulas.pop()
                            for _ in range(PARTICULAS_VAPOR_POR_LIQUIDA): self.crear_vapor()
            else:
                if self.snd_reproduciendo and self.snd_hervir:
                    if not self.encendida or not self.hirviendo:
                        self.snd_hervir.stop()
                        self.snd_reproduciendo = False

            # --- C. MOVIMIENTO ---
            for p in self.particulas:
                rango_temp = TEMP_HERVIR - self.temp_ambiente_actual
                if rango_temp <= 0: rango_temp = 1 
                ratio_temp = (p.temperatura - self.temp_ambiente_actual) / rango_temp
                
                empuje = ratio_temp * MAX_EMPUJE_CALOR_PARTICULA
                v_max = MAX_VELOCIDAD_BASE + (ratio_temp * (MAX_VELOCIDAD_TOPE - MAX_VELOCIDAD_BASE))
                
                for _ in range(SUB_STEPS):
                    p.mover(SUB_STEPS)
                    for w1, w2 in self.paredes: detectar_y_rebotar_circulo_linea(p, w1, w2)
                    p.vy += GRAVEDAD / SUB_STEPS
                    if p.y > nivel_agua_y:
                        p.vy -= empuje / SUB_STEPS
                        if p.y < nivel_agua_y + 15:
                            p.vy += 0.08
                            p.vx += random.uniform(-0.15, 0.15)
                    else:
                        p.vy *= 0.98
                    
                    v_actual = math.sqrt(p.vx**2 + p.vy**2)
                    if v_actual > v_max:
                        factor = v_max / v_actual
                        p.vx *= factor; p.vy *= factor

            # --- D. VAPOR VISUAL ---
            for pv in self.vapores[:]:
                pv.update(dt)
                if not pv.viva: self.vapores.remove(pv)
                
            if self.encendida: self.tiempo_sim += dt

        def dibujar(self):
            
            if self.img_pava: screen.blit(FONDO_IMG, (0, 0)), screen.blit(pygame.transform.scale(MESA_IMG, (1500, 1200)), (50, 400)),screen.blit(PAVA_IMG_ESCALADA, (200, 100))
            for p in self.particulas: p.dibujar(self.screen)
            for pv in self.vapores: pv.dibujar(self.screen)
            
            q_entregado = self.potencia_actual * self.tiempo_sim if (self.encendida or self.tiempo_sim > 0) else 0
            q_sensible = self.masa_agua * CALOR_ESPECIFICO_AGUA * (self.temperatura_promedio - self.temp_ambiente_actual)
            masa_vaporizada = self.masa_inicial - self.masa_agua
            q_latente = masa_vaporizada * CALOR_LATENTE_VAPORIZACION

            data_hud = {
                'temp': self.temperatura_promedio,
                'target_temp': self.target_temp,
                'tiempo': self.tiempo_sim,
                'masa': self.masa_agua,
                'encendida': self.encendida,
                'delta_u': self.delta_u,
                'delta_s': self.delta_s,
                'q_p': q_entregado,
                'q_a': q_sensible,
                'q_l': q_latente,
                'modo_manual': self.modo_manual,
                'potencia_actual': self.potencia_actual
            }
            self.hud.dibujar(self.screen, data_hud)

    class MainApp:
        def __init__(self):
            self.estado = "SIMULACION" 
            
            self.teoria = PantallaTeoria()
            self.simulacion = SimulacionPava(screen)

        def run(self):
            while True:
                dt = clock.get_time() / 1000.0
                eventos = pygame.event.get()
                
                for event in eventos:
                    if event.type == pygame.QUIT:
                        pygame.quit(); sys.exit()
                    keys = pygame.key.get_pressed()
                    
                    if keys[pygame.K_q]:
                        return
                    if self.estado == "MENU":
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            accion = self.menu.manejar_clic(event.pos)
                            if accion == "SIMULACION":
                                self.simulacion.resetear_simulacion()
                                self.estado = "SIMULACION"
                            elif accion == "TEORIA": self.estado = "TEORIA"
                            elif accion == "SALIR": pygame.quit(); sys.exit()
                    
                    elif self.estado == "TEORIA":
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            accion = self.teoria.manejar_clic(event.pos)
                            if accion == "MENU": self.estado = "MENU"
                    
                    elif self.estado == "SIMULACION":
                        accion = self.simulacion.manejar_eventos(event)
                        if accion == "MENU": self.estado = "MENU"

                if self.estado == "MENU": self.menu.dibujar(screen)
                elif self.estado == "TEORIA": self.teoria.dibujar(screen)
                elif self.estado == "SIMULACION":
                    self.simulacion.update(dt)
                    self.simulacion.dibujar()

                pygame.display.flip()
                clock.tick(FPS)

    app = MainApp()
    app.run()

    if __name__ == "__main__":
        pygame.init()
        SCREEN = pygame.display.set_mode((1280, 720)) 
        clock = pygame.time.Clock()
        pava_nueva(clock,SCREEN)
        