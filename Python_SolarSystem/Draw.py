import pygame
from pygame import Color
import numpy as np

from VerletPython import PythonSolver

WIDTH = 800
HEIGHT = 600
DISPLAY = (WIDTH, HEIGHT)

PLANET_RADIUS = [2, 5, 5, 2, 15, 15, 7, 7]
SUN_RADIUS = 10
X0 = WIDTH // 2
Y0 = HEIGHT // 2
BG = pygame.image.load("bg.jpg")
SUN_COLOR = Color("darkgoldenrod1")
PLANET_COLOR = [
    Color("snow2"),
    Color("firebrick3"),
    Color("skyblue1"),
    Color("bisque3"),
    Color("slategray2"),
    Color("sienna"),
    Color("steelblue2"),
    Color("steelblue4")
]

weight = np.array([1989000, 0.33, 4.9, 0.6, 6, 1900, 570, 87, 103]) * 1e24
distanceR = np.array([0, 58, 108, 152, 228, 778, 1433, 2877, 4437]) * 1e9
speed = np.array([0, 48, 35, 30, 24, 13, 10, 7, 5]) * 1e3

N = weight.shape[0]
T = 1e8
k = 1000

r0 = np.zeros((N, 2))
r0[:, 0] = distanceR
v0 = np.zeros((N, 2))
v0[:, 1] = speed
r, v = PythonSolver(weight, r0, v0, T, k)
distanceXY = np.zeros((N-1, 2))


def main():
    cur_t = 0
    
    pygame.init()
    screen = pygame.display.set_mode(DISPLAY)
    pygame.display.set_caption('Solar System')
    fps = pygame.time.Clock()
        
    done = False
    while not done:
        screen.blit(BG, (0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
                break 
        # distance updating
        if cur_t < k:
            distanceXY[:, 0] = np.sign(r[1:, 0, cur_t]) * abs(r[1:, 0, cur_t] / 1e9) ** 0.7
            distanceXY[:, 1]  = np.sign(r[1:, 1, cur_t]) * abs(r[1:, 1, cur_t] / 1e9) ** 0.7
            cur_t += 1
        # screen updating
        pygame.draw.circle(screen, SUN_COLOR, (X0, Y0), SUN_RADIUS, 0)
        for i in range(N - 1):
            pygame.draw.circle(screen, PLANET_COLOR[i], \
                (X0 + distanceXY[i, 0], Y0 + distanceXY[i, 1]), \
                PLANET_RADIUS[i], 0)
        pygame.display.update()
        fps.tick(100)

if __name__ == "__main__":
    main()