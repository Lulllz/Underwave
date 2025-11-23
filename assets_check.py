import os
import sys

BASE = os.path.join(os.path.dirname(__file__), 'Assets')
paths = [
    ('DinoRun1', os.path.join(BASE, 'Dino', 'DinoRun1.png')),
    ('DinoRun2', os.path.join(BASE, 'Dino', 'DinoRun2.png')),
    ('DinoJump', os.path.join(BASE, 'Dino', 'DinoJump.png')),
    ('DinoDuck1', os.path.join(BASE, 'Dino', 'DinoDuck1.png')),
    ('DinoDuck2', os.path.join(BASE, 'Dino', 'DinoDuck2.png')),
    ('SmallCactus1', os.path.join(BASE, 'Cactus', 'SmallCactus1.png')),
    ('SmallCactus2', os.path.join(BASE, 'Cactus', 'SmallCactus2.png')),
    ('SmallCactus3', os.path.join(BASE, 'Cactus', 'SmallCactus3.png')),
    ('LargeCactus1', os.path.join(BASE, 'Cactus', 'LargeCactus1.png')),
    ('LargeCactus2', os.path.join(BASE, 'Cactus', 'LargeCactus2.png')),
    ('LargeCactus3', os.path.join(BASE, 'Cactus', 'LargeCactus3.png')),
    ('Bird1', os.path.join(BASE, 'Bird', 'Bird1.png')),
    ('Bird2', os.path.join(BASE, 'Bird', 'Bird2.png')),
    ('Cone', os.path.join(BASE, 'Obstaculos', 'Cone.png')),
    ('Corrimao-accent', os.path.join(BASE, 'Obstaculos', 'Corrimão.png')),
    ('Corrimao-noaccent', os.path.join(BASE, 'Obstaculos', 'Corrimao.png')),
    ('Cloud', os.path.join(BASE, 'Other', 'Cloud.png')),
    ('Track', os.path.join(BASE, 'Other', 'Track.png')),
    ('FundoBolhas', os.path.join(BASE, 'Fundo', 'Fundo bolhas.png')),
]

missing = []
print('Asset check - existence:')
for name, p in paths:
    ok = os.path.exists(p)
    print(f" - {name}: {'FOUND' if ok else 'MISSING'} -> {p}")
    if not ok:
        missing.append((name, p))

# Try to load with pygame if available
try:
    import pygame
    pygame.init()
    print('\nAttempting to load images with pygame:')
    load_errors = []
    for name, p in paths:
        if not os.path.exists(p):
            continue
        try:
            img = pygame.image.load(p)
            print(f" - {name}: loaded (size={img.get_size()})")
        except Exception as e:
            print(f" - {name}: FAILED to load -> {e}")
            load_errors.append((name, str(e)))
    if load_errors:
        print('\nSome images failed to load via pygame:')
        for n, e in load_errors:
            print(f" - {n}: {e}")
except Exception as e:
    print('\npygame not available or failed to init; skipping load tests:', e)

if missing:
    print('\nSummary: MISSING FILES')
    for n, p in missing:
        print(' -', n, p)
    sys.exit(2)
else:
    print('\nSummary: all listed files exist (load errors may still occur).')
    sys.exit(0)
