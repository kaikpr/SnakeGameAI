import random
import pygame
from Game.food import Food
import Game.colors as color
import Game.config as cf
clock = pygame.time.Clock()
from queue import PriorityQueue
from Graphics.background import Background
bg = Background(cf.WIDTH, cf.HEIGHT)
import heapq
count = 0
class GameLogic:
    def __init__(self, snake, width, height):
        self.snake = snake
        self.width = width
        self.height = height
        self.food = Food(width, height, snake)
        self.game_over_flag = False
        self.score = 0
        self.path = []
        self.path_to_draw = []
        self.is_finding = False
        self.is_on_music = True
        self.is_paused = False
        self.is_simulated = False
    def toggle_pause(self):
        self.is_paused = not self.is_paused
        
    def update(self):
        if not self.snake.is_moving or self.is_paused:
            return
        head = self.snake.move()

        # self.visualize_bfs(cf.screen, cf.window)
        if head == self.food.food:
            self.food.is_eaten = True
            if self.food.is_eaten:
                print("is eaten")
            if self.is_on_music:
                self.snake.play_crunch_sound()
            self.food.spawn_food()
            self.score +=1
            # print(self.score)
        else:
            self.snake.body.pop(0)

        if self.snake.collides_with_wall(self.width, self.height) or self.snake.collides_with_self():
            self.game_over_flag = True

    def get_score(self):
        return self.score
            
    def game_over(self):
        return self.game_over_flag
    
    def restart_game(self):
        self.snake.__init__(self.width // 2, self.height // 2)
        self.food.spawn_food()
        self.game_over_flag = False
        self.score = 0

    def bfs(self, start, target, screen, window):
        print("CALLED")
        visited = set()
        queue = [(start, [])]
        self.is_finding = False
        while queue:
            self.is_finding = False
            current, path = queue.pop(0)

            if current and not self.food.is_eaten:
                node_rect = pygame.Rect(7 + current[0] * 20, 7 + current[1] * 20, 5, 5)
                # pygame.draw.rect(screen, color.GREEN, node_rect)
                # # pygame.display.update(node_rect)
                # window.blit(screen, (30, 30)) 
                self.path_to_draw.append((color.GREEN, node_rect))

            if current == target:
                for step in path:
                    node_rect = pygame.Rect(7 + step[0] * 20, 7 + step[1] * 20, 7, 7)
                    # pygame.draw.rect(screen, color.WHITE, node_rect)
                    # window.blit(screen, (30, 30)) 
                    self.path_to_draw.append((color.WHITE, node_rect))
                return path

            if target == self.snake.body[0]:
                    for neighbor in self.get_valid_neighbors_new(current):
                        if neighbor not in visited:
                            visited.add(neighbor)
                            queue.append((neighbor, path + [neighbor]))
            else:
                for neighbor in self.get_valid_neighbors(current):
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append((neighbor, path + [neighbor]))
        
        return None
    
    def ucs(self, start, target, screen, window):
        visited = set()
        queue = PriorityQueue()
        queue.put((0, start, []))  # (cost, current, path)
        
        while not queue.empty():
            cost, current, path = queue.get()
            
            if current:
                node_rect = pygame.Rect(7 + current[0] * 20, 7 + current[1] * 20, 5, 5)
                pygame.draw.rect(screen, color.GREEN, node_rect)

            if current == target:
                for step in path:
                    node_rect = pygame.Rect(7 + step[0] * 20, 7 + step[1] * 20, 7, 7)
                    pygame.draw.rect(screen, color.WHITE, node_rect)
                window.blit(screen, (30, 30))
                pygame.display.update(node_rect)
                return path

            if current not in visited:
                visited.add(current)
                if target == self.snake.body[0]:
                    for neighbor in self.get_valid_neighbors_new(current):
                        new_cost = cost + 1
                        queue.put((new_cost, neighbor, path + [neighbor]))
                else:
                    for neighbor in self.get_valid_neighbors(current):
                        new_cost = cost + 1  # Assuming all steps have equal cost
                        queue.put((new_cost, neighbor, path + [neighbor]))
        return None
    
    
    def a_star(self, start, target, screen, window):
        def heuristic(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])
            
        def cost(current, neighbor):
            return 1
        visited = set()
        queue = [(0, start, [])]  # (cost, current, path)
        
        while queue:
            cost, current, path = heapq.heappop(queue)
            
            if current:
                node_rect = pygame.Rect(7 + current[0] * 20, 7 + current[1] * 20, 5, 5)
                pygame.draw.rect(screen, color.BLUE, node_rect)

            if current == target:
                for step in path:
                    x, y = step
                    pygame.draw.rect(screen, color.WHITE, (7 + x * 20, 7 + y * 20, 10, 10))
                window.blit(screen, (30, 30))
                pygame.display.update(node_rect)
                return path

            if current not in visited:
                visited.add(current)
                for neighbor in self.get_valid_neighbors(current):
                    new_cost = cost + cost(current, neighbor) + heuristic(neighbor, target)
                    heapq.heappush(queue, (new_cost, neighbor, path + [neighbor]))

        return None

    def get_valid_neighbors(self, position):
        x, y = position
        valid_neighbors = []

        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            new_x, new_y = x + dx, y + dy
            if (0 <= new_x < self.width) and (0 <= new_y < self.height) and (new_x, new_y) not in self.snake.body:
                valid_neighbors.append((new_x, new_y))

        return valid_neighbors
    
    def get_valid_neighbors_new(self, position):
        x, y = position
        valid_neighbors = []

        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            new_x, new_y = x + dx, y + dy
            if (0 <= new_x < self.width) and (0 <= new_y < self.height) and (new_x, new_y) not in self.snake.body[1:-1]:
                valid_neighbors.append((new_x, new_y))

        return valid_neighbors

    def visualize_ucs(self, screen, window):
        if not self.game_over():
            start = self.snake.body[-1]
            target = self.food.food
            if not self.path:
                path = self.ucs(start, target, screen, window)
            
                if path:
                    print("default path")
                    self.path = [(path[0][0] - start[0], path[0][1] - start[1])]
                    self.path.extend((path[i][0] - path[i-1][0], path[i][1] - path[i-1][1]) for i in range(1, len(path)))
                    
            elif not self.is_finding:
                tail = self.snake.body[0]
                if not self.path:
                    path = self.ucs(start, tail, screen, window)
                    if path:
                        print("following tail")
                        self.path = [(path[0][0] - start[0], path[0][1] - start[1])]
                        self.path.extend((path[i][0] - path[i-1][0], path[i][1] - path[i-1][1]) for i in range(1, len(path)))       
                    else:
                        choose_longest_path = self.choose_longest_path(start)
                        if choose_longest_path:
                            print("choose_longest_path")
                            self.path = [choose_longest_path]    
                        else:
                            print("follow default head")
                            head_direction = (self.snake.body[-1][0] - self.snake.body[-2][0], self.snake.body[-1][1] - self.snake.body[-2][1])
                            self.path = [head_direction]
    
    def visualize_astar(self, screen, window):
        if not self.game_over():
            start = self.snake.body[-1]
            target = self.food.food
            path = self.a_star(start, target, screen, window)
            
            if path:
                print("default path")
                self.path = [(path[0][0] - start[0], path[0][1] - start[1])]
                self.path.extend((path[i][0] - path[i-1][0], path[i][1] - path[i-1][1]) for i in range(1, len(path)))
    def move_along_path(self):
        if self.path:
            direction = self.path.pop(0)
            # print(direction)
            self.snake.change_direction(direction)
            self.snake.set_moving(True)
            self.update()
    def visualize_bfs(self, screen, window):
        global count
        count += 1
        print(count)
        if not self.game_over():
            start = self.snake.body[-1]
            target = self.food.food
            path = self.bfs(start, target, screen, window)
            # print(self.path)
            if path:
                print("default path")
                self.path = [(path[0][0] - start[0], path[0][1] - start[1])]
                self.path.extend((path[i][0] - path[i-1][0], path[i][1] - path[i-1][1]) for i in range(1, len(path)))
                # for step in path:
                #     path_rect = pygame.Rect(7 + step[0] * 20, 7 + step[1] * 20, 7, 7)
                #     pygame.draw.rect(screen, color.WHITE, path_rect)
                #     pygame.display.update(path_rect)
            elif not self.is_finding:
                tail = self.snake.body[0]

                path = self.bfs(start, tail, screen, window)
                if path:
                    print("following tail")
                    self.path = [(path[0][0] - start[0], path[0][1] - start[1])]
                    self.path.extend((path[i][0] - path[i-1][0], path[i][1] - path[i-1][1]) for i in range(1, len(path)))         
                else:
                    choose_longest_path = self.choose_longest_path(start)
                    if choose_longest_path:
                        print("choose_longest_path")
                        self.path = [choose_longest_path]    
                    else:
                        print("follow default head")
                        head_direction = (self.snake.body[-1][0] - self.snake.body[-2][0], self.snake.body[-1][1] - self.snake.body[-2][1])
                        self.path = [head_direction]
    def choose_longest_path(self, start):
        best_direction = None
        max_distance = 0

        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            new_x, new_y = start[0] + dx, start[1] + dy
            distance = self.calculate_distance_to_tail((new_x, new_y))

            if (0 <= new_x < self.width) and (0 <= new_y < self.height) and (new_x, new_y) not in self.snake.body:
                if distance > max_distance:
                    max_distance = distance
                    best_direction = (dx, dy)

        return best_direction

    def calculate_distance_to_tail(self, position):
        tail = self.snake.body[0]
        return abs(position[0] - tail[0]) + abs(position[1] - tail[1])
