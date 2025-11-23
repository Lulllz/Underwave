import pygame
import os
import random
import math
import pygame.mixer

pygame.init()

# Globais do QT
KEY_MAP = {'W': pygame.K_w, 'A': pygame.K_a, 'S': pygame.K_s, 'D': pygame.K_d}
QTE_FONT = pygame.font.Font('Grand9K Pixel.ttf', 20)
QTE_DURATION_MS = 2000  #duração do QTE em milissegundos

# Game speed multiplier (used to implement slow motion during QTE)
GAME_SPEED_MULTIPLIER = 1

#Globals de música
MUSIC_END = pygame.USEREVENT + 1

# Hitbox debug
SHOW_HITBOX = True
HITBOX_COLOR_PLAYER = (0, 255, 0)
HITBOX_COLOR_OBSTACLE = (255, 0, 0)
HITBOX_COLOR_CORRIMAO = (0, 120, 255)

# Constantes Globais
SCREEN_HEIGHT = 600
SCREEN_WIDTH = 1100
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
def safe_load(path, fallback_size=(64, 64)):
    """Try to load an image and return a Surface. If loading fails, return
    a simple placeholder Surface so the game doesn't crash at import time.
    """
    try:
        return pygame.image.load(path)
    except Exception:
        surf = pygame.Surface(fallback_size, pygame.SRCALPHA)
        surf.fill((255, 0, 255, 128))
        return surf


RUNNING = [safe_load(os.path.join("Assets/Dino", "IMPULSO1.png")),
           safe_load(os.path.join("Assets/Dino", "IMPULSO2.png"))]
JUMPING = safe_load(os.path.join("Assets/Dino", "PRINCIPAL.png"))
DUCKING = [safe_load(os.path.join("Assets/Dino", "agaixado.png"))]

PARADO= safe_load(os.path.join("Assets/Dino", "SkateParado.png"))

# additional player run assets
PRINCIPAL_IMG = safe_load(os.path.join("Assets/Dino", "PRINCIPAL.png"))
IMPULSO1_IMG = safe_load(os.path.join("Assets/Dino", "IMPULSO1.png"))
IMPULSO2_IMG = safe_load(os.path.join("Assets/Dino", "IMPULSO2.png"))

SMALL_CACTUS = [safe_load(os.path.join("Assets/Cactus", "SmallCactus1.png")),
                safe_load(os.path.join("Assets/Cactus", "SmallCactus2.png")),
                safe_load(os.path.join("Assets/Cactus", "SmallCactus3.png"))]
LARGE_CACTUS = [safe_load(os.path.join("Assets/Cactus", "LargeCactus1.png")),
                safe_load(os.path.join("Assets/Cactus", "LargeCactus2.png")),
                safe_load(os.path.join("Assets/Cactus", "LargeCactus3.png"))]

# replaced Bird with fish asset 'Peixe 2'
BIRD = [safe_load(os.path.join("Assets/FISH", "Peixe 2.png"))]

CONE = safe_load(os.path.join("Assets/Obstaculos", "Cone.png"))

# spacing between cones when multiple are placed side-by-side (ratio of cone width)
CONE_SPACING_RATIO = 0.05


# load corrimão (railing) asset if present; accept accented or unaccented filename
def _try_load_corrimao():
    candidates = [
        os.path.join("Assets/Obstaculos", "Corrimão.png"),
        os.path.join("Assets/Obstaculos", "Corrimao.png"),
        os.path.join("Assets/Fundo", "Corrimao.png"),
    ]
    for p in candidates:
        try:
            return pygame.image.load(p)
        except Exception:
            continue
    # fallback placeholder surface (orange rectangle)
    surf = pygame.Surface((40, 120))
    surf.fill((255, 140, 0))
    return surf

CORRIMAO_IMG = _try_load_corrimao()
CORRIMAO = [CORRIMAO_IMG]

CLOUD = safe_load(os.path.join("Assets/Other", "Cloud.png"))
#-----------------------------------------------------------------------------------
# Use the street background from `Assets/Rua` instead of the old Track image
# Background frames from Rua (loop between these images)
# Load raw frames then scale them so each spans the full screen width
raw_bg = [
    safe_load(os.path.join("Assets/Rua", "Rua 1.png")),
    safe_load(os.path.join("Assets/Rua", "Rua 2.png")),
    safe_load(os.path.join("Assets/Rua", "Rua 3.png")),
]
BG_FRAMES = []
BG_SCALES = []
for img in raw_bg:
    try:
        w = img.get_width()
        h = img.get_height()
        # preserve aspect ratio: scale width to SCREEN_WIDTH and adjust height
        if w != 0:
            scale = SCREEN_WIDTH / float(w)
            new_h = max(1, int(h * scale))
            scaled = pygame.transform.scale(img, (SCREEN_WIDTH, new_h))
        else:
            scaled = img
        BG_SCALES.append(scale if w != 0 else 1.0)
    except Exception:
        scaled = img
    BG_FRAMES.append(scaled)
# milliseconds between background frame switches
BG_SWITCH_MS = 250
# current BG (kept for compatibility with existing code)
# current BG (kept for compatibility with existing code)
BG = BG_FRAMES[0]
# index of current background frame used for scrolling
BG_FRAME_INDEX = 0
# vertical offset to move the street up (negative moves up, positive moves down)
STREET_OFFSET = -383

# Scale player assets to match street proportions
try:
    STREET_SCALE = BG_SCALES[0] if BG_SCALES else 1.0
except Exception:
    STREET_SCALE = 1.0
#------------------------------------------------------------------------------------------------
# vertical shift (pixels) to move player and obstacles downwards
# increase this value to lower player/obstacles further
VERTICAL_SHIFT = 80

def _scale_surface_list(lst, scale):
    out = []
    for s in lst:
        try:
            w, h = s.get_size()
            out.append(pygame.transform.scale(s, (max(1, int(w * scale)), max(1, int(h * scale)))))
        except Exception:
            out.append(s)
    return out

# rescale running/ducking/jump surfaces to match street
RUNNING = _scale_surface_list(RUNNING, STREET_SCALE)
DUCKING = _scale_surface_list(DUCKING, STREET_SCALE)
try:
    JUMPING = pygame.transform.scale(JUMPING, (max(1, int(JUMPING.get_width() * STREET_SCALE)), max(1, int(JUMPING.get_height() * STREET_SCALE))))
except Exception:
    pass

# scale additional run assets
try:
    PRINCIPAL = pygame.transform.scale(PRINCIPAL_IMG, (max(1, int(PRINCIPAL_IMG.get_width() * STREET_SCALE)), max(1, int(PRINCIPAL_IMG.get_height() * STREET_SCALE))))
except Exception:
    PRINCIPAL = PRINCIPAL_IMG
try:
    IMPULSO1 = pygame.transform.scale(IMPULSO1_IMG, (max(1, int(IMPULSO1_IMG.get_width() * STREET_SCALE)), max(1, int(IMPULSO1_IMG.get_height() * STREET_SCALE))))
except Exception:
    IMPULSO1 = IMPULSO1_IMG
try:
    IMPULSO2 = pygame.transform.scale(IMPULSO2_IMG, (max(1, int(IMPULSO2_IMG.get_width() * STREET_SCALE)), max(1, int(IMPULSO2_IMG.get_height() * STREET_SCALE))))
except Exception:
    IMPULSO2 = IMPULSO2_IMG
IMPULSO_SEQ = [IMPULSO1, IMPULSO2]

# scale the idle ('parado') skate asset to match street/player scale
try:
    PARADO_SCALED = pygame.transform.scale(PARADO, (max(1, int(PARADO.get_width() * STREET_SCALE)), max(1, int(PARADO.get_height() * STREET_SCALE))))
except Exception:
    PARADO_SCALED = PARADO

# compute new desired Y positions (baseline around previous bottom ~404)
GROUND_BASE = 404
SCALED_Y_POS = GROUND_BASE - RUNNING[0].get_height() if RUNNING else 310
SCALED_Y_POS_DUCK = GROUND_BASE - DUCKING[0].get_height() if DUCKING else 340
# apply vertical shift so player appears lower (closer to street)
try:
    SCALED_Y_POS += VERTICAL_SHIFT
    SCALED_Y_POS_DUCK += VERTICAL_SHIFT
except Exception:
    pass

# prefer the earlier loaded CORRIMAO_IMG if available; otherwise load safely
CORRIMAO = [safe_load(os.path.join("Assets/Obstaculos", "Corrimão.png"))]

BOLHAS = safe_load(os.path.join("Assets/Fundo", "Fundo bolhas.png"))

# Scale the 'Fundo bolhas' bubbles so they are a reasonable size for clouds
try:
    bw, bh = BOLHAS.get_size()
    # limit bubble width to at most one third of the screen to avoid oversized clouds
    max_bubble_w = max(1, SCREEN_WIDTH // 3)
    if bw > max_bubble_w and bw != 0:
        scale = float(max_bubble_w) / float(bw)
        BOLHAS = pygame.transform.scale(BOLHAS, (max(1, int(bw * scale)), max(1, int(bh * scale))))
except Exception:
    # if scaling fails, keep original
    pass

# Use the 'Fundo bolhas' bubbles as the cloud image for a bubble effect
CLOUD = BOLHAS

# sky/background image for some screens — load safely to avoid crash if missing
FUNDO = safe_load(os.path.join("Assets/Fundo", "Fundo ceu.png"))

# Parallax sky: prepare a scaled fundo that fills the full screen and
# scrolls more slowly than the street for a parallax effect.
FUNDO_SCROLL_RATIO = 0.35
try:
    
    try:
        top = FUNDO.get_at((0, 0))
    except Exception:
        top = None
    if top and (top[0], top[1], top[2]) == (255, 0, 255):
        FUNDO_SCALED = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        FUNDO_SCALED.fill((135, 206, 235))
    else:
        FUNDO_SCALED = pygame.transform.scale(FUNDO, (SCREEN_WIDTH, SCREEN_HEIGHT))
except Exception:
    # final fallback: a plain sky blue surface
    FUNDO_SCALED = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    FUNDO_SCALED.fill((135, 206, 235))

#Música de fundo
def load_and_play_music(path, loop=False):
    """Carrega e toca a música, configurando o evento MUSIC_END.
    Se 'loop' for True, ela toca em loop infinito.
    """
    try:
        pygame.mixer.music.load(path)
        
        # -1 para loop infinito (quando loop=True) ou 0 para tocar uma vez
        loop_count = -1 if loop else 0
        pygame.mixer.music.play(loop_count)
        
        # Define o evento para ser disparado quando a música terminar
        if not loop:
             pygame.mixer.music.set_endevent(MUSIC_END)
        else:
             # Se for loop infinito, limpamos o evento de fim
             pygame.mixer.music.set_endevent(pygame.NOEVENT)

        print(f"Música '{path}' carregada e tocando. Loop: {loop}")
        return True
    except pygame.error as e:
        print(f"Erro ao carregar ou tocar a música: {e}")
        return False


class Dinosaur:
    X_POS = 140
    Y_POS = 380
    Y_POS_DUCK = 350
    JUMP_VEL = 8.5

    def __init__(self):
        self.duck_img = DUCKING
        self.run_img = RUNNING
        self.jump_img = JUMPING

        self.dino_duck = False
        self.dino_run = True
        self.dino_jump = False

        self.step_index = 0
        self.jump_vel = self.JUMP_VEL
        self.image = self.run_img[0]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS

        # QTE state
        self.qte_active = False
        self.qte_letter = None
        self.qte_start = 0
        self.qte_duration = QTE_DURATION_MS
        self.qte_succeeded = False
        self.qte_failed = False
        self.qte_message = None
        self.qte_message_time = 0

        # running impulse state: mostly PRINCIPAL, occasionally IMPULSO1->IMPULSO2
        try:
            self.run_base = PRINCIPAL
            self.impulse_seq = IMPULSO_SEQ
        except Exception:
            self.run_base = self.run_img[0] if isinstance(self.run_img, (list, tuple)) else self.run_img
            self.impulse_seq = [self.run_base]
        self.run_timer = 0
        self.in_impulse = False
        self.impulse_step = 0
        # make the impulse (pulse) quicker by reducing frames per impulse frame
        self.impulse_duration = 6  # frames per impulse frame (was 8)
        self.impulse_interval = 23  # frames between impulses (~1s at 30fps)

    def update(self, userInput):
        if self.dino_duck:
            self.duck()
        if self.dino_run:
            self.run()
        if self.dino_jump:
            self.jump()

        if self.step_index >= 10:
            self.step_index = 0

        if userInput[pygame.K_UP] and not self.dino_jump:
            self.dino_duck = False
            self.dino_run = False
            self.dino_jump = True
            # start a quick-time event when jump begins but only if an obstacle
            # is close in front of the player (within `proximity_px`).
            proximity_px = 300 #dinstancia em pixels para iniciar o QTE
            start_qte = False
            if 'obstacles' in globals() and obstacles:
                for obs in obstacles:
                    try:
                        dx = obs.rect.x - self.dino_rect.x
                    except Exception:
                        continue
                    if 0 < dx <= proximity_px:
                        start_qte = True
                        break

            if start_qte:
                self.qte_active = True
                self.qte_succeeded = False
                self.qte_failed = False
                self.qte_letter = random.choice(list(KEY_MAP.keys()))
                self.qte_start = pygame.time.get_ticks()
            else:
                # ensure QTE is not active when jumping without nearby obstacles
                self.qte_active = False
        elif userInput[pygame.K_DOWN] and not self.dino_jump:
            self.dino_duck = True
            self.dino_run = False
            self.dino_jump = False
        elif not (self.dino_jump or userInput[pygame.K_DOWN]):
            self.dino_duck = False
            self.dino_run = True
            self.dino_jump = False

    def duck(self):
        # choose duck frame safely (works if there's 1 or multiple duck sprites)
        if isinstance(self.duck_img, (list, tuple)) and len(self.duck_img) > 0:
            idx = (self.step_index // 5) % len(self.duck_img)
            self.image = self.duck_img[idx]
        else:
            self.image = self.duck_img
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS_DUCK
        self.step_index += 1

    def run(self):
        # Running: mostly use the base (PRINCIPAL), but occasionally play the impulse sequence
        if self.in_impulse:
            frame_idx = self.impulse_step // self.impulse_duration
            if frame_idx >= len(self.impulse_seq):
                # end impulse sequence
                self.in_impulse = False
                self.impulse_step = 0
                self.run_timer = 0
                self.image = self.run_base
            else:
                self.image = self.impulse_seq[frame_idx]
                self.impulse_step += 1
        else:
            # normal running image
            self.image = self.run_base
            self.run_timer += 1
            if self.run_timer >= self.impulse_interval:
                # start impulse sequence
                self.in_impulse = True
                self.impulse_step = 0

        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS
        self.step_index += 1

    def jump(self):
        self.image = self.jump_img
        # Iguala o tempo de pulo ao tempo do jogo
        try:
            mult = GAME_SPEED_MULTIPLIER
        except NameError:
            mult = 1.0

        if self.dino_jump:
            # scale displacement and gravity by multiplier
            self.dino_rect.y -= self.jump_vel * 4 * mult
            self.jump_vel -= 0.8 * mult
        if self.jump_vel < - self.JUMP_VEL:
            self.dino_jump = False
            self.jump_vel = self.JUMP_VEL
            # termina o QTE se ainda estiver ativo quando o pulo termina
            if self.qte_active and not self.qte_succeeded:
                self.qte_active = False
                self.qte_failed = True
                self.qte_message = "*sons tristes*"
                self.qte_message_time = pygame.time.get_ticks()

    def handle_qte_input(self, key):
        """Call when a KEYDOWN event happens. Returns 'success' or 'fail' or None."""
        if not self.qte_active:
            return None
        # check correct key
        correct_key = KEY_MAP.get(self.qte_letter)
        if key == correct_key:
            self.qte_succeeded = True
            self.qte_active = False
            self.qte_message = "Maneiro B)"
            self.qte_message_time = pygame.time.get_ticks()
            return 'success'
        else:
            # wrong key -> fail
            self.qte_failed = True
            self.qte_active = False
            self.qte_message = "*sons tristes*"
            self.qte_message_time = pygame.time.get_ticks()
            return 'fail'

    def draw(self, SCREEN):
        SCREEN.blit(self.image, (self.dino_rect.x, self.dino_rect.y))
        # draw QTE letter above dino while active
        if self.qte_active and self.qte_letter:
            # compute remaining time ratio for a small bar
            elapsed = pygame.time.get_ticks() - self.qte_start
            remaining = max(0, self.qte_duration - elapsed)
            letter_surf = QTE_FONT.render(self.qte_letter, True, (255, 0, 0))
            letter_rect = letter_surf.get_rect()
            # position the letter slightly above the dino
            letter_rect.center = (self.dino_rect.x + 40, self.dino_rect.y - 30)
            # draw circular progress indicator centered on the letter (under the letter)
            ratio = remaining / float(self.qte_duration) if self.qte_duration else 0
            # radius slightly larger than letter to surround it
            radius = 20
            center_x = letter_rect.centerx
            center_y = letter_rect.centery
            # outer background circle
            pygame.draw.circle(SCREEN, (200, 200, 200), (center_x, center_y), radius)
            # inner background (hole)
            pygame.draw.circle(SCREEN, (255, 255, 255), (center_x, center_y), radius - 6)
            # draw remaining arc (clockwise from top)
            if ratio > 0:
                start_angle = -math.pi / 2
                end_angle = start_angle + 2 * math.pi * ratio
                rect = (center_x - radius, center_y - radius, radius * 2, radius * 2)
                pygame.draw.arc(SCREEN, (0, 200, 0), rect, start_angle, end_angle, 5)
            # finally draw the letter on top so it's visible
            SCREEN.blit(letter_surf, letter_rect)
        # show a brief GOOD/MISS message
        if self.qte_message and (pygame.time.get_ticks() - self.qte_message_time) < 1000:
            msg_surf = QTE_FONT.render(self.qte_message, True, (0, 0, 0))
            msg_rect = msg_surf.get_rect()
            msg_rect.center = (self.dino_rect.x + 40, self.dino_rect.y - 60)
            SCREEN.blit(msg_surf, msg_rect)

# apply scaled Y positions computed earlier so the dinosaur's feet match the street baseline
try:
    Dinosaur.Y_POS = SCALED_Y_POS
    Dinosaur.Y_POS_DUCK = SCALED_Y_POS_DUCK
except Exception:
    pass


class Cloud:
    def __init__(self):
        # Manage many small bubble sprites that fill the screen.
        # We create a set of scaled bubble variants and spawn many instances
        # at random positions so the whole screen is filled with bubbles.
        try:
            base = CLOUD
        except NameError:
            base = pygame.Surface((16, 16), pygame.SRCALPHA)
            base.fill((200, 200, 255))

        # create scaled variants for performance
        self.variants = []
        try:
            bw, bh = base.get_size()
            # sizes in pixels for bubble variants
            # larger sizes so bubbles are more prominent
            sizes = [24, 36, 48, 72]
            for s in sizes:
                try:
                    self.variants.append(pygame.transform.smoothscale(base, (s, max(1, int(bh * (s / float(bw)))))))
                except Exception:
                    self.variants.append(pygame.transform.scale(base, (s, s)))
        except Exception:
            # fallback single variant
            self.variants = [base]

        # spawn many bubbles to visually fill the screen
        self.bubbles = []
        count = 100
        for i in range(count):
            var = random.randint(0, len(self.variants) - 1)
            surf = self.variants[var]
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            # small speed variation so bubbles drift at slightly different rates
            speed = random.uniform(0.2, 1.0)
            self.bubbles.append({'x': x, 'y': y, 'var': var, 'speed': speed, 'w': surf.get_width(), 'h': surf.get_height()})

    def update(self):
        # apply global multiplier so we can slow the game during QTE
        try:
            mult = GAME_SPEED_MULTIPLIER
        except NameError:
            mult = 1.0
        # move each bubble left according to its own speed modifier
        for b in self.bubbles:
            b['x'] -= (game_speed * mult) * (0.15 * b['speed'])
            if b['x'] < -b['w']:
                # wrap to right with some horizontal jitter
                b['x'] = SCREEN_WIDTH + random.randint(0, 200)
                b['y'] = random.randint(0, SCREEN_HEIGHT)

    def draw(self, SCREEN):
        # draw all bubble instances
        for b in self.bubbles:
            try:
                surf = self.variants[b['var']]
                SCREEN.blit(surf, (int(b['x']), int(b['y'])))
            except Exception:
                continue


class Obstacle:
    def __init__(self, image, type):
        # normalize image to a list and scale by STREET_SCALE so obstacles match street
        imgs = image if isinstance(image, list) else [image]
        scaled_imgs = []
        try:
            scale = STREET_SCALE
        except Exception:
            scale = 1.0
        for img in imgs:
            try:
                w, h = img.get_size()
                nw = max(1, int(w * scale))
                nh = max(1, int(h * scale))
                scaled_imgs.append(pygame.transform.scale(img, (nw, nh)))
            except Exception:
                scaled_imgs.append(img)

        self.image = scaled_imgs
        self.type = type
        self.rect = self.image[self.type].get_rect()
        self.rect.x = SCREEN_WIDTH

    def update(self):
        # apply global multiplier so obstacles slow down during QTE
        try:
            mult = GAME_SPEED_MULTIPLIER
        except NameError:
            mult = 1.0
        self.rect.x -= int(game_speed * mult)
        if self.rect.x < -self.rect.width:
            obstacles.pop()

    def draw(self, SCREEN):
        # ensure rect size matches the current image (some obstacles animate
        # with frames of different sizes). Preserve position when updating.
        img = self.image[self.type]
        try:
            x = self.rect.x
            y = self.rect.y
        except Exception:
            x, y = SCREEN_WIDTH, 0
        # if image size changed, recreate rect but keep position
        if img.get_size() != (self.rect.width, self.rect.height):
            self.rect = img.get_rect()
            self.rect.x = x
            self.rect.y = y
        SCREEN.blit(img, self.rect)


class SmallCactus(Obstacle):
    def __init__(self, image):
        self.type = random.randint(0, 2)
        super().__init__(image, self.type)
        self.rect.y = 325 + VERTICAL_SHIFT


class LargeCactus(Obstacle):
    def __init__(self, image):
        self.type = random.randint(0, 2)
        super().__init__(image, self.type)
        self.rect.y = 300 + VERTICAL_SHIFT


class Bird(Obstacle):
    def __init__(self, image):
        # accept either a single Surface or a list of Surfaces
        if isinstance(image, list):
            imgs = image
        else:
            imgs = [image]
        self.type = 0
        # let Obstacle initializer handle scaling and rect setup
        super().__init__(imgs, self.type)
        self.rect.y = 310 


class Corrimao(Obstacle):
    """Railing obstacle: touching the top is safe; colliding with the side facing
    the player causes death. Uses same image-list convention as other obstacles.
    """
    def __init__(self, image):
        # image may be a Surface or list
        if isinstance(image, list):
            imgs = image
        else:
            imgs = [image]
        self.type = 0
        # delegate to base class to scale and setup rect
        super().__init__(imgs, self.type)
        # place so bottom sits near ground similar to other obstacles
        self.rect.y = 320 + VERTICAL_SHIFT

    def side_collision_with_player(self, player_rect):
        """Return True if collision with the side facing the player should count as hit.
        We determine this by examining the intersection rectangle: if intersection
        width is greater than intersection height, it's primarily a side collision.
        """
        if not player_rect.colliderect(self.rect):
            return False
        inter = player_rect.clip(self.rect)
        # If width >= height -> side collision (player hitting the vertical face)
        return inter.width >= inter.height
class Cone(Obstacle):
    def __init__(self, image, count=1):
        """Create a cone obstacle consisting of `count` cones side-by-side.
        `image` may be a Surface or a list; we use the first surface as the cone sprite.
        """
        # normalize to a single surface
        if isinstance(image, list):
            base = image[0]
        else:
            base = image

        # clamp count to 1..3
        count = max(1, min(3, int(count)))

        # build composite surface with small spacing
        try:
            w, h = base.get_size()
            # spacing controlled by global ratio so it is easy to tweak
            spacing = max(0, int(w * CONE_SPACING_RATIO))
            total_w = w * count + spacing * (count - 1)
            surf = pygame.Surface((total_w, h), pygame.SRCALPHA)
            for i in range(count):
                surf.blit(base, (i * (w + spacing), 0))
        except Exception:
            # fallback: just use the base surface
            surf = base

        # delegate to Obstacle initializer to apply street scaling
        super().__init__([surf], 0)
        # place cones roughly on the ground (similar to small cactus)
        self.rect.y = 325 + VERTICAL_SHIFT



def main():
    global game_speed, x_pos_bg, y_pos_bg, points, obstacles, x_pos_fundo
    global GAME_SPEED_MULTIPLIER
    global SHOW_HITBOX
    run = True
    clock = pygame.time.Clock()
    player = Dinosaur()
    cloud = Cloud()
    game_speed = 20
    x_pos_bg = 0
    x_pos_fundo = 0
    y_pos_bg = 380
    points = 0
    font = pygame.font.Font('freesansbold.ttf', 20)
    obstacles = []
    death_count = 0

    def score():
        global points, game_speed
        points += 1
        if points % 100 == 0:
            game_speed += 1

        text = font.render("Points: " + str(points), True, (0, 0, 0))
        textRect = text.get_rect()
        textRect.center = (1000, 40)
        SCREEN.blit(text, textRect)

    def background():
        global x_pos_bg, y_pos_bg, BG_FRAME_INDEX, x_pos_fundo
        # draw distant sky (FUNDO) first with a slower parallax scroll
        try:
            mult = GAME_SPEED_MULTIPLIER
        except NameError:
            mult = 1.0
        try:
            fundo = FUNDO_SCALED
            f_w = fundo.get_width()
            # draw two copies of the sky for continuous scrolling
            SCREEN.blit(fundo, (x_pos_fundo, 0))
            SCREEN.blit(fundo, (x_pos_fundo + f_w, 0))
            # advance fundo scroll at a slower ratio
            x_pos_fundo -= int(game_speed * mult * FUNDO_SCROLL_RATIO)
            if x_pos_fundo <= -f_w:
                x_pos_fundo += f_w
        except Exception:
            # if anything fails just draw the single FUNDO at 0,0
            try:
                SCREEN.blit(FUNDO, (0, 0))
            except Exception:
                pass

        # now draw the street (BG frames) on top of the sky
        current = BG_FRAMES[BG_FRAME_INDEX]
        image_width = current.get_width()
        base_y = y_pos_bg + STREET_OFFSET
        SCREEN.blit(current, (x_pos_bg, base_y))
        next_idx = (BG_FRAME_INDEX + 1) % len(BG_FRAMES)
        next_img = BG_FRAMES[next_idx]
        SCREEN.blit(next_img, (x_pos_bg + image_width, base_y))
        # when the current image has fully scrolled off, advance frame index
        if x_pos_bg <= -image_width:
            x_pos_bg += image_width
            BG_FRAME_INDEX = next_idx
        # advance street scroll at game speed
        x_pos_bg -= int(game_speed * mult)

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            # handle QTE key presses on KEYDOWN
            if event.type == pygame.KEYDOWN:
                # toggle hitbox display
                if event.key == pygame.K_h:
                    SHOW_HITBOX = not SHOW_HITBOX
                # give the player a chance to answer the QTE
                result = player.handle_qte_input(event.key)
                if result == 'success':
                    # award a small bonus for hitting the QTE
                    points += 100
                # else: failure feedback handled inside player

        SCREEN.fill((255, 255, 255))
        userInput = pygame.key.get_pressed()

        # draw background and clouds first so the sky/street are behind sprites
        background()
        cloud.draw(SCREEN)
        cloud.update()

        player.draw(SCREEN)
        player.update(userInput)

        # check QTE timeout
        if player.qte_active:
            elapsed = pygame.time.get_ticks() - player.qte_start
            if elapsed > player.qte_duration:
                player.qte_active = False
                player.qte_failed = True
                player.qte_message = "MISS"
                player.qte_message_time = pygame.time.get_ticks()

        # set global speed multiplier when QTE is active (slow motion)
        if player.qte_active:
            GAME_SPEED_MULTIPLIER = 0.60
        else:
            GAME_SPEED_MULTIPLIER = 1.0

        

        if len(obstacles) == 0:
            r = random.randint(0, 4)
            if r == 0:
                # replace small cactus with 1-3 cones
                count = random.randint(1, 3)
                obstacles.append(Cone(CONE, count=count))
            elif r == 1:
                # replace large cactus with 1-3 cones (visually larger grouping)
                count = random.randint(1, 3)
                obstacles.append(Cone(CONE, count=count))
            elif r == 2:
                obstacles.append(Bird(BIRD))
            elif r == 3:
                obstacles.append(Cone(CONE))
            else:
                # spawn the Corrimão (railing)
                obstacles.append(Corrimao(CORRIMAO))

        for obstacle in obstacles:
            obstacle.draw(SCREEN)
            obstacle.update()
            if player.dino_rect.colliderect(obstacle.rect):
                # special handling for Corrimao: only side collisions kill
                if isinstance(obstacle, Corrimao):
                    if obstacle.side_collision_with_player(player.dino_rect):
                        pygame.time.delay(2000)
                        death_count += 1
                        menu(death_count)
                    else:
                        # top/bottom collision with corrimao is safe; ignore
                        pass
                else:
                    pygame.time.delay(2000)
                    death_count += 1
                    menu(death_count)

        # draw hitboxes if enabled (player and obstacles)
        if SHOW_HITBOX:
            # player
            try:
                pygame.draw.rect(SCREEN, HITBOX_COLOR_PLAYER, player.dino_rect, 1)
            except Exception:
                pass
            # obstacles
            for obs in obstacles:
                try:
                    color = HITBOX_COLOR_OBSTACLE
                    if isinstance(obs, Corrimao):
                        color = HITBOX_COLOR_CORRIMAO
                    # try to draw a tight hitbox around non-transparent pixels
                    img = None
                    if isinstance(obs.image, list):
                        img = obs.image[obs.type]
                    else:
                        img = obs.image
                    try:
                        bound = img.get_bounding_rect()
                        draw_rect = pygame.Rect(obs.rect.x + bound.x, obs.rect.y + bound.y, bound.width, bound.height)
                        pygame.draw.rect(SCREEN, color, draw_rect, 1)
                    except Exception:
                        # fallback to full rect
                        pygame.draw.rect(SCREEN, color, obs.rect, 1)
                except Exception:
                    continue

        # background and clouds are drawn earlier so obstacles and player
        # render in front of the street.

        score()

        clock.tick(30)
        pygame.display.update()

def menu(death_count):
    global points
    run = True
     # Adicione este caminho para o seu arquivo de música
     # Altere "music.mp3" para o nome do seu arquivo real
    MUSIC_LIST = ["Assets/Musgas/Musga.mp3", "Assets/Musgas/LoopMusga.mp3"]
    current_music_index = 0
    pygame.mixer.music.set_volume(0.15) 
        # Inicia a música de fundo apenas uma vez (no primeiro menu)
        # Se a música já estiver tocando, esta função não a reinicia.
     # 1. Toca a primeira música (não em loop)
    if not pygame.mixer.music.get_busy():
        load_and_play_music(MUSIC_LIST[current_music_index], loop=False)
   
    while run:
   
        SCREEN.fill((255, 255, 255))
        # titulo do jogo
        try:
            title_font = pygame.font.Font('Grand9K Pixel.ttf', 72)
            title_font.set_bold(True)
        except Exception:
            title_font = pygame.font.SysFont(None, 72)
        title_surf = title_font.render("Underwave", True, (0, 102, 204))
        title_rect = title_surf.get_rect()
        title_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 160)
        SCREEN.blit(title_surf, title_rect)

        font = pygame.font.Font('Grand9K Pixel.ttf', 30)

        if death_count == 0:
            text = font.render("Aperte qualquer tecla para começar", True, (0, 0, 0))
        elif death_count > 0:
            text = font.render("Aperte qualquer tecla para reiniciar", True, (0, 0, 0))
            score = font.render("Sua Pontuação: " + str(points), True, (0, 0, 0))
            scoreRect = score.get_rect()
            scoreRect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)
            SCREEN.blit(score, scoreRect)
        textRect = text.get_rect()
        textRect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        SCREEN.blit(text, textRect)
        # draw the idle skate sprite where the player would stand during gameplay
        try:
            # use the scaled parado asset and the dinosaur baseline
            SCREEN.blit(PARADO_SCALED, (Dinosaur.X_POS, Dinosaur.Y_POS))
        except Exception:
            # fallback to the running image if parado not available
            SCREEN.blit(RUNNING[0], (SCREEN_WIDTH // 2 - 20, SCREEN_HEIGHT // 2 - 140))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                run = False
            if event.type == pygame.KEYDOWN:
                main()
       
        # 2. Verifica se a música terminou
            if event.type == MUSIC_END:
                current_music_index += 1
                
                # 3. Se ainda há músicas na sequência
                if current_music_index < len(MUSIC_LIST):
                    # Toca a próxima. Se for a última (índice 1), seta loop=True
                    is_looping = (current_music_index == len(MUSIC_LIST) - 1)
                    load_and_play_music(MUSIC_LIST[current_music_index], loop=is_looping)
                # 4. Se a sequência acabou, mas a última música não estava em loop, 
                # podemos reiniciá-la aqui se for o caso. (Neste exemplo, ela entra em loop no passo 3)
        
        
        
        # draw controls in the lower-right corner
        try:
            controls_font = pygame.font.Font('Grand9K Pixel.ttf', 18)
        except Exception:
            controls_font = pygame.font.SysFont(None, 18)
        controls_lines = [
            "Controles:",
            "W/A/S/D  - Quick Time",
            "Up       - Pular",
            "Down     - Agachar",
        ]
        line_h = controls_font.get_linesize()
        n = len(controls_lines)
        top_start = SCREEN_HEIGHT - 20 - n * line_h
        for i, line in enumerate(controls_lines):
            surf = controls_font.render(line, True, (0, 0, 0))
            rect = surf.get_rect()
            rect.right = SCREEN_WIDTH - 20
            rect.top = top_start + i * line_h
            SCREEN.blit(surf, rect)

        pygame.display.update()


if __name__ == '__main__':
    try:
        menu(death_count=0)
    except Exception:
        # Print traceback to console and save to crash_log.txt for diagnosis
        import traceback, sys
        traceback.print_exc()
        try:
            with open('crash_log.txt', 'w', encoding='utf-8') as f:
                traceback.print_exc(file=f)
        except Exception:
            pass
        try:
            pygame.quit()
        except Exception:
            pass
        sys.exit(1)