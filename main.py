import pygame
import sys
import math

pygame.init()
clock = pygame.time.Clock()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

screen_size = 70
screen_width = screen_size * 16
screen_height = screen_size * 9
screen = pygame.display.set_mode((screen_width, screen_height))

map_display = False
map_img = pygame.image.load("sample.png")
img_width, img_height = map_img.get_size()

class visionCone:
    def __init__(self):
        self.direction = 0
        self.angle_span = 90
        self.length = 100

    def tick(self, pos):
        self.cone_pos = [pos]
        start_angle = math.radians(self.direction - self.angle_span // 2)
        end_angle = math.radians(self.direction + self.angle_span // 2)
        num_rays = 60

        for i in range(num_rays + 1):
            angle = start_angle + (end_angle - start_angle) * (i / num_rays)
            dx = math.cos(angle)
            dy = math.sin(angle)

            for dist in range(self.length):
                x = int(pos[0] + dx * dist)
                y = int(pos[1] + dy * dist)
                if 0 <= x < img_width and 0 <= y < img_height:
                    if map_img.get_at((x, y))[:3] == BLACK:
                        break
            hit_x = pos[0] + dx * dist
            hit_y = pos[1] + dy * dist
            self.cone_pos.append((hit_x, hit_y))

    def render(self, screen):
        if len(self.cone_pos) > 2:
            pygame.draw.polygon(screen, (255, 255, 0), self.cone_pos, 0)

    def render_3d(self, screen, pos):
        fov = math.radians(self.angle_span)
        num_rays = screen_width
        angle_step = fov / num_rays
        ray_angle = math.radians(self.direction) - fov / 2

        for col in range(num_rays):
            dx = math.cos(ray_angle)
            dy = math.sin(ray_angle)

            for dist in range(1, self.length * 5):
                x = int(pos[0] + dx * dist)
                y = int(pos[1] + dy * dist)
                if 0 <= x < img_width and 0 <= y < img_height:
                    if map_img.get_at((x, y))[:3] == BLACK:
                        corrected_dist = dist * math.cos(ray_angle - math.radians(self.direction))
                        if corrected_dist == 0:
                            corrected_dist = 0.0001
                        wall_height = int((screen_height * 16) / corrected_dist)
                        wall_height = min(wall_height, screen_height)
                        shade = max(0, 255 - int(corrected_dist * 2))
                        color = (shade, shade, shade)
                        y_start = screen_height // 2 - wall_height // 2
                        pygame.draw.line(screen, color, (col, y_start), (col, y_start + wall_height))
                        break
            ray_angle += angle_step

class Player:
    def __init__(self, pos, displaySize):
        self.x, self.y = pos
        self.displaySize = displaySize
        self.vel = [0, 0]
        self.vis = visionCone()

    def tick(self):
        speed = 1
        move_x, move_y = 0, 0

        if self.vel != [0, 0]:
            angle_rad = math.radians(self.vis.direction)
            dx = math.cos(angle_rad)
            dy = math.sin(angle_rad)
            move_x += -dx * self.vel[1]
            move_y += -dy * self.vel[1]
            strafe_angle = math.radians(self.vis.direction + 90)
            sx = math.cos(strafe_angle)
            sy = math.sin(strafe_angle)
            move_x += sx * self.vel[0]
            move_y += sy * self.vel[0]

            if map_img.get_at((int(self.x + move_x * speed), int(self.y)))[:3] != BLACK:
                self.x += move_x * speed
            if map_img.get_at((int(self.x), int(self.y + move_y * speed)))[:3] != BLACK:
                self.y += move_y * speed

        self.vel = [0, 0]
        self.vis.tick((self.x, self.y))

    def render(self, screen):
        rect = pygame.Rect(self.x - self.displaySize // 2, self.y - self.displaySize // 2, self.displaySize, self.displaySize)
        pygame.draw.rect(screen, RED, rect)
        self.vis.render(screen)

def getStart():
    for x in range(img_width):
        for y in range(img_height):
            if map_img.get_at((x, y))[:3] == WHITE:
                temp_x = x
                while map_img.get_at((temp_x, y))[:3] == WHITE:
                    temp_x += 1
                start_x = int((temp_x + x) / 2)
                temp_y = y
                while map_img.get_at((x, temp_y))[:3] == WHITE:
                    temp_y += 1
                start_y = int((temp_y + y) / 2)
                return start_x, start_y

player = Player(getStart(), 5)

while True:
    keys = pygame.key.get_pressed()
    if keys[pygame.K_a]: player.vel[0] = -1
    if keys[pygame.K_d]: player.vel[0] = 1
    if keys[pygame.K_w]: player.vel[1] = -1
    if keys[pygame.K_s]: player.vel[1] = 1
    if keys[pygame.K_LEFT]: player.vis.direction -= 3
    if keys[pygame.K_RIGHT]: player.vis.direction += 3

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:
                map_display = not map_display

    player.tick()

    if map_display:
        temp_map = map_img.copy()
        player.render(temp_map)
        screen.blit(temp_map, (0, 0))
    else:
        screen.fill((40, 40, 40))
        player.vis.render_3d(screen, (player.x, player.y))

    pygame.display.flip()
    clock.tick(60)
