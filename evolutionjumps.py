import pygame
import sys
import random
import numpy as np
import copy
import pygame.gfxdraw

# Initialize Pygame
pygame.init()

# Set up the game window
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))

# Set up colors (R, G, B)
white = (255, 255, 255)  
black = (30, 30, 60)
red = (255, 0, 0)

# Set up the game clock
clock = pygame.time.Clock()
FPS = 60

#State variables:
generationExists = False #if a generation exists, meaning if balls[] is not empty
trainingIsRunning = False #if the process of training should be running right now
winnerIsFound = False
numberOfGenerations = 0

#Configuration:
NumberOfSurvivors = 10
NumberOfCopies = 50
StrenfthOfMutation = 50


class ball:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = (random.randint(100, 200), random.randint(100, 200), random.randint(100, 200))
        self.jumps = [random.randint(0,80) * 10, random.randint(0,80) * 10, random.randint(0,80) * 10]
        self.isAlive = True
        self.score = 0

    def draw(self):
        pygame.gfxdraw.aacircle(screen, self.x, self.y, self.radius, self.color)
        pygame.gfxdraw.filled_circle(screen, self.x, self.y, self.radius, self.color)

    def jump(self):
        if self.x in self.jumps:
            self.y -= 100

    def move(self):
        global winnerIsFound
        if self.x < screen_width-self.radius:
            self.x += 10   #move the ball forward if not reached the wall yet.
        else:
            print(self.jumps) #these will be the winning set of jumps
            winnerIsFound = True
        if self.y < (screen_height-self.radius):
            self.y += 10   #if the ball is in air, move it down
        if self.y > (screen_height-self.radius):
            self.y = screen_height-self.radius    #if it somehow below ground, get it on the ground.

    def is_collided(self, obstacle):
        global numberOfCollisions
        if self.x + self.radius >= obstacle.x and self.y + self.radius >= obstacle.y and self.x - self.radius <= obstacle.x + obstacle.width and self.y - self.radius <= obstacle.y + obstacle.height:
            isAlive = False
            return True
        else:
            return False
            

        


class obstacle:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = (255, 0, 0)

    def draw(self):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))


def draw_obstacles():
    for obstacle in obstacles:
        obstacle.draw()

def create_first_generation(n):
    global numberOfGenerations
    numberOfGenerations += 1
    print("number of generations: ", numberOfGenerations)
    for i in range(n):
        balls.append(ball(0, screen_height-20, 20))

def count_alive_balls():
    number = 0
    for ball in balls:
        if ball.isAlive == True:
            number += 1
    return number


def select_n_best_by_score(n, balls):
    balls.sort(key=lambda ball: ball.score, reverse=True)
    return balls[:n]


def duplicate_balls_for_new_generation(m, balls):
    newBalls = []
    for i in balls:
        for j in range(m):
            newBalls.append(copy.deepcopy(i))
    return newBalls

#modifies position of jumps for all balls with a normal distribution with standard deviation s
def mutate_jumps(balls,s):
    for ball in balls:
        ball.jumps = [abs(int(round(np.random.normal(ball.jumps[0], s)/10)*10)), 
                    abs(int(round(np.random.normal(ball.jumps[1], s)/10)*10)), 
                    abs(int(round(np.random.normal(ball.jumps[2], s)/10)*10)),]

def reset (balls):
    for ball in balls:
        ball.score = 0
        ball.isAlive = True
        ball.x = 0
        ball.y = screen_height-ball.radius

def create_next_generation(balls, nOfSurvivors, nOfCopies, mutationStrength):
    bestBalls = select_n_best_by_score(nOfSurvivors, balls)
    newBalls = duplicate_balls_for_new_generation(nOfCopies, bestBalls)
    mutate_jumps(newBalls, mutationStrength)
    new_generation = bestBalls + newBalls
    for ball in new_generation:
        print("all jumps: ", ball.jumps)
    reset(new_generation)
    return new_generation




balls = []
obstacles = [obstacle(200,580,10,20), 
            obstacle(400,580,10,20), 
            obstacle(600,580,10,20)]


# Game loop
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False





    screen.fill(black)  

    draw_obstacles()

    if not generationExists:
        create_first_generation(10)
        #balls.append(ball(0, screen_height-20, 20))
        #balls[0].jumps = (170,370,570)
        generationExists = True
        trainingIsRunning = True


    if generationExists and trainingIsRunning and not winnerIsFound:
        for ball in balls:
            if ball.isAlive:
                if ball.x in ball.jumps:
                    ball.jump()
                ball.move()
                ball.draw()
                ball.score += 1
                stillAlive = True
                for obstacle in obstacles:
                    if ball.is_collided(obstacle):
                        stillAlive = False
                ball.isAlive = stillAlive
        if count_alive_balls() == 0:
            trainingIsRunning = False


    if generationExists and not trainingIsRunning and not winnerIsFound:
        balls = create_next_generation(balls, NumberOfSurvivors, NumberOfCopies, StrenfthOfMutation)
        numberOfGenerations += 1
        print("number of generations: ", numberOfGenerations)
        trainingIsRunning = True
    


      

    pygame.display.flip()

    clock.tick(FPS)

pygame.quit()
sys.exit()
