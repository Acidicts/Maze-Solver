import pygame
import random
from collections import deque

pygame.init()
width, height = 480, 750
win = pygame.display.set_mode((width, height))
pygame.display.set_caption("Maze Generator")
clock = pygame.time.Clock()


class Cell:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size
        self.visited = False
        self.walls = {'top': True, 'right': True, 'bottom': True, 'left': True}

    def draw(self, win):
        if self.walls['top']:
            pygame.draw.line(win, (255, 255, 255), (self.x, self.y), (self.x + self.size, self.y))
        if self.walls['right']:
            pygame.draw.line(win, (255, 255, 255), (self.x + self.size, self.y),
                             (self.x + self.size, self.y + self.size))
        if self.walls['bottom']:
            pygame.draw.line(win, (255, 255, 255), (self.x, self.y + self.size),
                             (self.x + self.size, self.y + self.size))
        if self.walls['left']:
            pygame.draw.line(win, (255, 255, 255), (self.x, self.y), (self.x, self.y + self.size))


def solve_maze(grid, start, end):
    queue = deque([start])
    came_from = {start: None}
    while queue:
        current = queue.popleft()
        if current == end:
            break
        neighbors = get_neighbors(current, grid)
        for neighbor in neighbors:
            if neighbor not in came_from:
                queue.append(neighbor)
                came_from[neighbor] = current
                yield came_from, current, neighbor
    if end not in came_from:
        print("End cell is not reachable from the start cell.")
    yield came_from, None, None


def get_neighbors(cell, grid):
    neighbors = []
    directions = [
        ('top', 0, -20),
        ('right', 20, 0),
        ('bottom', 0, 20),
        ('left', -20, 0)
    ]
    for direction, dx, dy in directions:
        nx, ny = cell.x + dx, cell.y + dy
        for neighbor in grid:
            if neighbor.x == nx and neighbor.y == ny and not cell.walls[direction]:
                neighbors.append(neighbor)
    return neighbors


def draw_solution(win, came_from, start, end, current, next_cell):
    for cell in came_from:
        if came_from[cell] is not None:
            pygame.draw.line(win, (0, 255, 0), (cell.x + 10, cell.y + 10),
                             (came_from[cell].x + 10, came_from[cell].y + 10), 3)
    if current and next_cell:
        pygame.draw.line(win, (255, 0, 0), (current.x + 10, current.y + 10), (next_cell.x + 10, next_cell.y + 10), 3)


def remove_walls(current, next_cell):
    dx = current.x - next_cell.x
    dy = current.y - next_cell.y
    if dx == 20:
        current.walls['left'] = False
        next_cell.walls['right'] = False
    elif dx == -20:
        current.walls['right'] = False
        next_cell.walls['left'] = False
    if dy == 20:
        current.walls['top'] = False
        next_cell.walls['bottom'] = False
    elif dy == -20:
        current.walls['bottom'] = False
        next_cell.walls['top'] = False


cols, rows = width // 20, height // 20
grid = [Cell(x * 20, y * 20, 20) for y in range(rows) for x in range(cols)]


def get_neighbors_for_generation(cell):
    neighbors = []
    for neighbor in grid:
        if not neighbor.visited and (
                (neighbor.x == cell.x and abs(neighbor.y - cell.y) == 20) or
                (neighbor.y == cell.y and abs(neighbor.x - cell.x) == 20)
        ):
            neighbors.append(neighbor)
    return neighbors


stack = []
current = grid[0]
current.visited = True

wait = True
while wait:
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                wait = False

while True:
    neighbors = get_neighbors_for_generation(current)
    if neighbors:
        next_cell = random.choice(neighbors)
        stack.append(current)
        remove_walls(current, next_cell)
        current = next_cell
        current.visited = True
    elif stack:
        current = stack.pop()
    else:
        break

start = grid[0]
end = grid[-1]
solver = solve_maze(grid, start, end)


def blink_cell(win, cell, color1, color2, blink_rate):
    ellipse_size = cell.size // 2
    ellipse_x = cell.x + (cell.size - ellipse_size) // 2
    ellipse_y = cell.y + (cell.size - ellipse_size) // 2
    if pygame.time.get_ticks() // blink_rate % 2 == 0:
        pygame.draw.ellipse(win, color1, (ellipse_x, ellipse_y, ellipse_size, ellipse_size))


run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    win.fill((0, 0, 0))
    for cell in grid:
        cell.draw(win)
    try:
        came_from, current, next_cell = next(solver)
        draw_solution(win, came_from, start, end, current, next_cell)
    except StopIteration:
        draw_solution(win, came_from, start, end, None, None)

    blink_cell(win, start, (0, 0, 255), (0, 0, 0), 500)
    blink_cell(win, end, (255, 0, 0), (0, 0, 0), 500)

    pygame.display.flip()
    clock.tick(30)

pygame.quit()