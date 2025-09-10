import pygame
from collections import deque
import numpy as np

FPS = 10000000
MAX_LINES = 100000
MAX_LINE_DELTA = 1000
MAX_LINE_COEF = 1.5

class Line:
    def __init__(self, start, end, color, screen, fade_coef=1.01):
        self.start = start
        self.end = end
        self.color = color
        self.screen = screen
        self.fade_coef = fade_coef

    def draw(self):
        pygame.draw.line(self.screen, self.color.astype(int).tolist(), self.start, self.end)

    def fade(self):
        self.color = self.fade_coef * self.color
        self.color = self.color.clip(0, 255)

def get_color_gradient_generator(grain=100):
    EPS=1e-9
    red = np.array([0xFF, EPS, EPS])
    green = np.array([EPS, 0xFF, EPS])
    blue = np.array([EPS, EPS, 0xFF])

    color_order = (red, green, blue)
    base_color_idx = 0
    cur_step = 0
    color_count = len(color_order)
    while True:
        next_frac = cur_step / grain
        base_frac = 1 - next_frac
        base_color = color_order[base_color_idx]
        next_color = color_order[(base_color_idx + 1) % color_count]
        cur_color = base_frac * base_color + next_frac * next_color
        cur_color *= 255 / np.sqrt(cur_color.dot(cur_color))
        cur_color = cur_color.clip(0, 255)

        cur_step += 1
        if cur_step >= grain:
            cur_step = 0
            base_color_idx += 1
            base_color_idx = base_color_idx % (color_count)

        yield cur_color

def get_solid_color_generator(color=None):
    if color is None:
        color = [0xFF, 0xFF, 0xFF] 

    while True:
        yield color 

def get_angle_generator(delta=1):
    cur_angle = 0
    while True:
        yield cur_angle
        cur_angle += delta
        if cur_angle >= 360:
            cur_angle -= 360

def get_offset_vector(angle, norm_square):
    coord = np.sqrt(norm_square / 2) / 2
    dx = (np.cos(angle) + np.sin(angle)) * coord
    dy = (np.cos(angle) - np.sin(angle)) * coord
    return np.array([dx, dy])

class LineMaker:
    def __init__(self, screen, norm_square=100000, color_generator=get_solid_color_generator()):
        self.angle_generator = get_angle_generator(0.1)
        self.color_generator = color_generator
        self.screen = screen
        self.norm_square = norm_square

    def get_line(self, pos):
        offset_vector = get_offset_vector(next(self.angle_generator), self.norm_square)
        line_start = pos - offset_vector
        line_end = pos + offset_vector
        color = next(self.color_generator)
        return Line(line_start, line_end, color, self.screen)


def is_quit(event):
    if event.type == pygame.QUIT:
        return True

    return False

def is_switch_lines(event):
    if not event.type == pygame.KEYDOWN:
        return False

    if event.key == pygame.K_SPACE:
        return True

    return False

def is_increase_max_lines(event):
    if not event.type == pygame.KEYDOWN:
        return False

    if event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
        return True

    return False

def is_clear_lines(event):
    if not event.type == pygame.KEYDOWN:
        return False

    if event.key == pygame.K_c:
        return True

    return False

def is_decrease_max_lines(event):
    if not event.type == pygame.KEYDOWN:
        return False

    if event.key == pygame.K_MINUS:
        return True

    return False


def main():
    bg_color = (0xFF, 0xFF, 0xFF)
    bg_color = (0x00, 0x00, 0x00)
    screen = pygame.display.set_mode((1800, 900))
    clock = pygame.time.Clock()
    pygame.display.set_caption('Draw lines')
    cur_max_lines = 100

    lines = deque([])
    line_maker = LineMaker(screen, color_generator=get_color_gradient_generator())
    # line_maker = LineMaker(screen, color_generator=get_solid_color_generator())

    running = True
    lines_on = False
    while running:
        for event in pygame.event.get():
            if is_quit(event):
                running = False
                continue
            elif is_switch_lines(event):
                lines_on = not lines_on 
            elif is_increase_max_lines(event):
                if cur_max_lines < 2:
                    cur_max_lines = 2
                else:
                    cur_max_lines = min(MAX_LINES, int(cur_max_lines * MAX_LINE_COEF))
                print("MAX LINE:", cur_max_lines)
            elif is_decrease_max_lines(event):
                cur_max_lines = max(1, int(cur_max_lines / MAX_LINE_COEF))
                print("MAX LINE:", cur_max_lines)
            elif is_clear_lines(event):
                lines = deque([])

        dt = clock.tick(FPS)

        mouse_pos = np.array(pygame.mouse.get_pos())
        # mouse_pos_scaled = tuple(2 * coord for coord in mouse_pos)
        # lines.append(Line(mouse_pos, mouse_pos_scaled, next(gradient_generator), screen))
        if lines_on:
            new_line = line_maker.get_line(mouse_pos)
            lines.append(new_line)
        while len(lines) > cur_max_lines:
            lines.popleft()

        screen.fill(bg_color)
        for line in lines:
            line.fade()
            line.draw()
        pygame.display.flip()
        print(clock.get_fps())



if __name__ == "__main__":
    main()
