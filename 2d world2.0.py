import pygame, sys, random, math

# ─── Constants ──────────────────────────────────────────────────────────────────
SCREEN_W, SCREEN_H = 800, 600
TILE   = 32
MAP_W, MAP_H   = 100, 100
FPS     = 60

INV_SLOTS   = 5
REACH_PIX   = 208
MINIMAP_W   = 200
MINIMAP_H   = 200
MINIMAP_POS = (10, 10)

BREAKABLE = {'rock', 'log', 'leaf', 'sand'}

# ─── Init ───────────────────────────────────────────────────────────────────────
pygame.init()
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
clock  = pygame.time.Clock()
font   = pygame.font.SysFont(None, 24)

# ─── Procedural tile textures ─────────────────────────────────────────────────
def make_grass():
    s = pygame.Surface((TILE,TILE)); s.fill((50,160,50))
    for _ in range(30):
        x,y = random.randrange(TILE), random.randrange(TILE)
        s.set_at((x,y),(30,100,30))
    return s

def make_sand():
    s = pygame.Surface((TILE,TILE)); s.fill((194,178,128))
    for _ in range(40):
        x,y = random.randrange(TILE), random.randrange(TILE)
        s.set_at((x,y),(170,150,100))
    return s

def make_water():
    s = pygame.Surface((TILE,TILE)); s.fill((50,50,200))
    for y in range(0,TILE,6):
        for x in range(-2,TILE+2,8):
            start = (x, y+random.randint(-1,1))
            end   = (x+6, y+random.randint(-1,1))
            pygame.draw.line(s,(80,80,230),start,end,2)
    return s

def make_rock():
    s = pygame.Surface((TILE,TILE)); s.fill((100,100,100))
    for _ in range(6):
        x1,y1 = random.randrange(TILE), random.randrange(TILE)
        x2,y2 = x1+random.randint(-8,8), y1+random.randint(-8,8)
        pygame.draw.line(s,(70,70,70),(x1,y1),(x2,y2),2)
    return s

def make_log():
    s = pygame.Surface((TILE,TILE)); s.fill((80,50,20))
    for _ in range(10):
        x1,y1 = random.randrange(TILE), random.randrange(TILE)
        x2,y2 = x1+random.randint(-5,5), y1+random.randint(-5,5)
        pygame.draw.line(s,(100,70,30),(x1,y1),(x2,y2),2)
    return s

def make_leaves():
    s = pygame.Surface((TILE,TILE), pygame.SRCALPHA)
    for gy in range(4):
        for gx in range(4):
            if random.random() < 0.7:
                pygame.draw.rect(s, (20,120,20), (gx*8, gy*8, 8, 8))
    return s

TEX = {
    'grass': make_grass(),
    'sand' : make_sand(),
    'water': make_water(),
    'rock' : make_rock(),
    'log'  : make_log(),
    'leaf' : make_leaves(),
}

# ─── World gen ─────────────────────────────────────────────────────────────────
world = [['grass']*MAP_W for _ in range(MAP_H)]
# lakes
for _ in range(5):
    cx,cy = random.uniform(10,MAP_W-10), random.uniform(10,MAP_H-10)
    rx,ry = random.uniform(5,12), random.uniform(3,8)
    for y in range(MAP_H):
        for x in range(MAP_W):
            if ((x-cx)/rx)**2 + ((y-cy)/ry)**2 < 1:
                world[y][x] = 'water'
# river
ry = random.randint(20, MAP_H-20)
for x in range(MAP_W):
    w = 2 + int(2*math.sin(x/5))
    for dy in range(-w,w+1):
        yy = ry+dy
        if 0<=yy<MAP_H:
            world[yy][x] = 'water'
    ry += random.randint(-1,1)
# shore sand
for y in range(MAP_H):
    for x in range(MAP_W):
        if world[y][x]=='grass':
            for dy in (-1,0,1):
                for dx in (-1,0,1):
                    ny,nx = y+dy, x+dx
                    if 0<=ny<MAP_H and 0<=nx<MAP_W and world[ny][nx]=='water':
                        world[y][x] = 'sand'
# rocks
for _ in range(int(MAP_W*MAP_H*0.02)):
    x,y = random.randrange(MAP_W), random.randrange(MAP_H)
    if world[y][x]=='grass':
        world[y][x] = 'rock'
# trees
for _ in range(80):
    tx,ty = random.randrange(5,MAP_W-5), random.randrange(5,MAP_H-5)
    if world[ty][tx]=='grass':
        world[ty][tx] = 'log'
        for dy in range(-2,3):
            for dx in range(-2,3):
                lx,ly = tx+dx, ty+dy
                if (dx,dy)!=(0,0) and 0<=lx<MAP_W and 0<=ly<MAP_H:
                    if world[ly][lx]=='grass' and random.random()<0.6:
                        world[ly][lx] = 'leaf'

# ─── Player & Inventory ───────────────────────────────────────────────────────
px, py    = MAP_W/2, MAP_H/2
dir_vec   = pygame.math.Vector2(0,1)
swim_time = 0

inventory = {'rock':0,'log':0,'leaf':0,'sand':0}
slots     = ['rock','log','leaf','sand','grass']
sel_slot  = 0

# ─── Collision helper ──────────────────────────────────────────────────────────
def collides(rect):
    left   = rect.left  // TILE
    right  = rect.right // TILE
    top    = rect.top   // TILE
    bottom = rect.bottom// TILE
    for ty in range(top,bottom+1):
        for tx in range(left,right+1):
            if 0<=tx<MAP_W and 0<=ty<MAP_H:
                if world[ty][tx] in ('rock','log'):
                    if rect.colliderect(pygame.Rect(tx*TILE,ty*TILE,TILE,TILE)):
                        return True
    return False

# ─── Main loop ────────────────────────────────────────────────────────────────
while True:
    dt = clock.tick(FPS)/1000
    for e in pygame.event.get():
        if e.type==pygame.QUIT:
            pygame.quit(); sys.exit()
        elif e.type==pygame.KEYDOWN and pygame.K_1<=e.key<=pygame.K_5:
            sel_slot = e.key - pygame.K_1
        elif e.type==pygame.MOUSEBUTTONDOWN:
            mx,my = pygame.mouse.get_pos()
            cam_x = px*TILE - SCREEN_W/2
            cam_y = py*TILE - SCREEN_H/2
            wx = int((mx+cam_x)/TILE)
            wy = int((my+cam_y)/TILE)
            dist = math.hypot(mx-(px*TILE-cam_x), my-(py*TILE-cam_y))
            if dist<=REACH_PIX and 0<=wx<MAP_W and 0<=wy<MAP_H:
                if e.button==1 and world[wy][wx] in BREAKABLE:
                    # Left-click: break
                    inventory[world[wy][wx]] += 1
                    world[wy][wx] = 'grass'
                elif e.button==3:
                    # Right-click: place
                    typ = slots[sel_slot]
                    if inventory.get(typ,0)>0 and world[wy][wx]=='grass':
                        world[wy][wx] = typ
                        inventory[typ] -= 1

    # movement & sliding collision
    keys = pygame.key.get_pressed()
    mv   = pygame.math.Vector2(
        keys[pygame.K_d]-keys[pygame.K_a],
        keys[pygame.K_s]-keys[pygame.K_w]
    )
    moving = mv.length_squared()>0
    if moving:
        mv = mv.normalize()*5*dt*60
        dir_vec = mv.normalize()

    # X axis
    new_px = px*TILE + mv.x
    rect_x = pygame.Rect(new_px-TILE/2, py*TILE-TILE/2, TILE, TILE)
    if not collides(rect_x):
        px = new_px/TILE
    # Y axis
    new_py = py*TILE + mv.y
    rect_y = pygame.Rect(px*TILE-TILE/2, new_py-TILE/2, TILE, TILE)
    if not collides(rect_y):
        py = new_py/TILE

    # swimming bob
    under = world[int(py)][int(px)]
    if under=='water':
        swim_time += dt
        ybob = math.sin(swim_time*4)*5
    else:
        swim_time = 0; ybob = 0

    # camera
    cam_x = px*TILE - SCREEN_W/2
    cam_y = py*TILE - SCREEN_H/2 + ybob

    # ─── Draw base (skip leaves) ────────────────────────────────────────────────
    screen.fill((0,0,0))
    sx,sy = int(cam_x//TILE), int(cam_y//TILE)
    cols,rows = SCREEN_W//TILE+2, SCREEN_H//TILE+2
    for ry in range(rows):
        for rx in range(cols):
            wx,wy = sx+rx, sy+ry
            if 0<=wx<MAP_W and 0<=wy<MAP_H:
                t = world[wy][wx]
                if t!='leaf':
                    screen.blit(TEX[t],
                        (rx*TILE-(cam_x%TILE),
                         ry*TILE-(cam_y%TILE)))

    # draw player
    ps = pygame.Surface((TILE,TILE), pygame.SRCALPHA)
    ps.fill((200,50,50))
    eye_off,eye_r=6,5
    pupil = dir_vec if moving else pygame.math.Vector2(0,0)
    for ex in(-eye_off,eye_off):
        pygame.draw.circle(ps,(255,255,255),
            (TILE//2+ex,TILE//2-eye_off), eye_r)
        pygame.draw.circle(ps,(0,0,0),
            (int(TILE//2+ex+pupil.x),int(TILE//2-eye_off+pupil.y)),
            eye_r//2)
    screen.blit(ps,(
        px*TILE-cam_x-TILE/2,
        py*TILE-cam_y-TILE/2+ybob))

    # draw leaves
    for ry in range(rows):
        for rx in range(cols):
            wx,wy = sx+rx, sy+ry
            if 0<=wx<MAP_W and 0<=wy<MAP_H and world[wy][wx]=='leaf':
                screen.blit(TEX['leaf'],
                    (rx*TILE-(cam_x%TILE),
                     ry*TILE-(cam_y%TILE)))

    # ─── Highlight block under mouse last ──────────────────────────────────────
    mx,my = pygame.mouse.get_pos()
    wx = int((mx+cam_x)/TILE); wy = int((my+cam_y)/TILE)
    if 0<=wx<MAP_W and 0<=wy<MAP_H and world[wy][wx] in BREAKABLE:
        if math.hypot(mx-(px*TILE-cam_x), my-(py*TILE-cam_y)) <= REACH_PIX:
            hx = wx*TILE - cam_x
            hy = wy*TILE - cam_y
            pygame.draw.rect(screen,(255,255,0),(hx,hy,TILE,TILE),2)

    # ─── Minimap ────────────────────────────────────────────────────────────────
    mm = pygame.Surface((MINIMAP_W,MINIMAP_H))
    for y in range(MAP_H):
        for x in range(MAP_W):
            c = {
                'grass':(50,200,50),'sand':(194,178,128),
                'water':(50,50,200),'rock':(100,100,100),
                'log':(120,70,20),'leaf':(20,150,20)
            }[world[y][x]]
            mm.set_at((int(x/MAP_W*MINIMAP_W),
                       int(y/MAP_H*MINIMAP_H)), c)
    pygame.draw.circle(mm,(255,0,0),
        (int(px/MAP_W*MINIMAP_W),int(py/MAP_H*MINIMAP_H)),3)
    screen.blit(mm, MINIMAP_POS)

    # ─── Inventory Bar ─────────────────────────────────────────────────────────
    bar_h=48; bar_y=SCREEN_H-bar_h
    pygame.draw.rect(screen,(30,30,30),(0,bar_y,SCREEN_W,bar_h))
    for i in range(INV_SLOTS):
        sx_i = 10 + i*(TILE+10)
        r = pygame.Rect(sx_i, bar_y+8, TILE, TILE)
        if i==sel_slot:
            pygame.draw.rect(screen,(255,255,0),r.inflate(4,4),2)
        t = slots[i]
        screen.blit(TEX[t], r.topleft)
        cnt = inventory.get(t,0)
        if cnt>0:
            txt = font.render(str(cnt),True,(255,255,255))
            screen.blit(txt,(sx_i+TILE-txt.get_width(),
                             bar_y+8+TILE-txt.get_height()))

    pygame.display.flip()
