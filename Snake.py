from random import randrange
from os import environ, path
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
from pygame import *

RESOLUTION = 800 #800 by 800 pixels. Must be a multiple of the grid size
GRID_SIZE = 16 #16 x 16 grid
GRID_RESOLUTION = RESOLUTION/GRID_SIZE
FPS = 15 #Speed of the game

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

class Grid:
    def __init__(self, screen):
        self.screen = screen

    def random_pos(self, collision = None) -> list:
        if collision != None:
            while True:
                valid = True
                temp = (randrange(0, GRID_SIZE), randrange(0, GRID_SIZE))
                for pos in collision:
                    if pos == temp:
                        valid = False
                if valid:
                    return temp
        return (randrange(0, GRID_SIZE), randrange(0, GRID_SIZE))

    def out_of_bounds(self, pos: list) -> bool:
        if pos[0] < 0 or pos[0] > GRID_SIZE - 1 or pos[1] < 0 or pos[1] > GRID_SIZE - 1:
            return True

    def draw_square(self, screen, colour, pos):
        draw.rect(screen, colour, Rect(pos[0] * GRID_RESOLUTION, pos[1] * GRID_RESOLUTION + GRID_RESOLUTION, GRID_RESOLUTION, GRID_RESOLUTION))

    def draw(self):
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                draw.rect(self.screen, WHITE, Rect(x * GRID_RESOLUTION, y * GRID_RESOLUTION + GRID_RESOLUTION, GRID_RESOLUTION, GRID_RESOLUTION), 1)

class Snake(Grid):
    def __init__(self, screen):
        self.screen = screen
        self.body = [self.random_pos()]
        self.head_pos = self.body[0]
        self.length = 1

    def move(self, direction: str) -> None:
        match direction:
            case "up":
                self.body.insert(0, (self.head_pos[0], self.head_pos[1] - 1))
            case "down":
                self.body.insert(0, (self.head_pos[0], self.head_pos[1] + 1))
            case "right":
                self.body.insert(0, (self.head_pos[0] + 1, self.head_pos[1]))
            case "left":
                self.body.insert(0, (self.head_pos[0] - 1, self.head_pos[1]))

        if self.length < len(self.body):
            del self.body[-1]

    def tail_collision(self) -> bool:
        for idx, pos in enumerate(self.body):
            if idx > 0 and pos == self.head_pos:
                return True

    def draw(self):
        self.head_pos = self.body[0]
        for pos in self.body:
            colour = GREEN
            if pos == self.head_pos:
                colour = BLUE
            if not self.out_of_bounds(pos):
                self.draw_square(self.screen, colour, pos)

class Apple(Grid):
    def __init__(self, screen, snake: Snake):
        self.screen = screen
        self.pos = self.random_pos(snake.body)

    def draw(self):
        self.draw_square(self.screen, RED, self.pos)

class SnakeGame:
    def __init__(self):
        self.screen = display.set_mode((RESOLUTION, RESOLUTION + GRID_RESOLUTION))
        display.set_caption("Snake")
        display.set_icon(image.load(path.dirname(__file__) + "\Icon.png").convert())
        self.background = Surface((RESOLUTION, RESOLUTION + GRID_RESOLUTION))
        
        self.clock = time.Clock()
        self.grid = Grid(self.screen)
        self.impact = font.SysFont("impact", int(GRID_RESOLUTION))

        with open(path.dirname(__file__) + "\Highscore.txt", "r") as file:
            self.highscore = int(file.read())

        self.start()

    def start(self):
        self.snake = Snake(self.screen)
        self.apple = Apple(self.screen, self.snake)
        self.start_time = time.get_ticks()

    def play(self):
        running = True
        pause = False
        restart = False
        direction = ""

        while running:
            for events in event.get():
                if events.type == KEYDOWN:
                    if events.key == K_ESCAPE and not restart:
                        if pause == True:
                            pause = False
                        else:
                            pause = True
                    elif (events.key == K_r or events.key == K_RCTRL) and restart:
                        restart = False
                        self.start()
                    elif events.key == K_q or events.key == K_RETURN:
                        running = False
                    elif not pause and not restart:
                        if events.key == K_w and direction != "down":
                            direction = "up"
                        elif events.key == K_s and direction != "up":
                            direction = "down"
                        elif events.key == K_a and direction != "right":
                            direction = "left"
                        elif events.key == K_d and direction != "left":
                            direction = "right"
                elif events.type == QUIT:
                    running = False

            if not pause and not restart:
                if self.snake.tail_collision() or self.grid.out_of_bounds(self.snake.head_pos):
                    direction = ""
                    restart = True

                self.clock.tick(FPS)
                self.snake.move(direction)

                if self.snake.head_pos == self.apple.pos:
                    self.snake.length += 1
                    if self.snake.length > self.highscore:
                        self.highscore = self.snake.length
                        with open(path.dirname(__file__) + "\Highscore.txt", "w") as file:
                            file.write(str(self.snake.length))
                            file.close()
                    self.apple.pos = self.grid.random_pos(self.snake.body)

                self.draw()

    def draw_ui(self):
        score = self.impact.render(f"Score: {self.snake.length}", True, WHITE)
        highscore_font = self.impact.render(f"Highscore: {self.highscore}", True, WHITE)
        rect = highscore_font.get_rect()
        rect.topright = (RESOLUTION, -RESOLUTION/100)
        
        current_time = time.get_ticks() - self.start_time
        time_minutes = int(current_time/60000)
        time_seconds = int((current_time%60000)/1000)
        if time_seconds < 10:
            timer = f"{time_minutes}:0{time_seconds}"
        else:
            timer = f"{time_minutes}:{time_seconds}"
        clock = self.impact.render(f"{timer}", True, WHITE)

        self.screen.blit(score, (0, -RESOLUTION/100))
        self.screen.blit(highscore_font, rect)
        self.screen.blit(clock, (RESOLUTION/2 - RESOLUTION/6, -RESOLUTION/100))

    def draw(self):
        self.screen.blit(self.background, (0, 0))
        self.apple.draw() 
        self.snake.draw()
        self.grid.draw()
        self.draw_ui()
        display.update()

if __name__ == "__main__":
    init()
    game = SnakeGame()
    game.play()