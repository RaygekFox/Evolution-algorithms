import pygame 
import sys # type: ignore
import random # type: ignore
import numpy as np # type: ignore
import copy
import pygame.gfxdraw # type: ignore
import math
# Initialize Pygame
pygame.init()

# Set up the game window
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))

# Set up colors (R, G, B)
white = (255, 255, 255)  
blue = (30, 30, 60)
orange = (255, 100, 0)

# Set up the game clock
clock = pygame.time.Clock()
FPS = 30

#State variables:
generationExists = False #if a generation exists, meaning if balls[] is not empty
trainingIsRunning = False #if the process of training should be running right now
winnerIsFound = False
numberOfGenerations = 0

#Configuration:
initialNumberOfRockets = 10
NumberOfSurvivors = 2
NumberOfCopies = 4
StrenfthOfMutation = 100

planetRadius = 50
gravityStrength = 10

class rocket:
	def __init__(self):
		self.x = screen_width / 2
		self.y = screen_height / 2 + planetRadius + 10
		self.color = white
		self.angle = math.pi / 2
		self.velocityX = 0
		self.velocityY = 0
		self.fuel = 10
		self.enginePower = 11
		self.isAlive = True
		self.engineOn = True
		self.height = 0
		self.vectorToPlanet = [self.x - screen_width / 2, self.y - screen_height / 2 ]
		self.distanceToPlanet = planetRadius
		self.angleToPlanet = math.atan2(self.vectorToPlanet[1], self.vectorToPlanet[0])
		self.score = 0
		self.neuralNetworkValues = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0]]
		self.neuralNetworkWeights = [
			[[0.0 for _ in range(4)] for _ in range(4)],  # Weights from input layer to first hidden layer
			[[0.0 for _ in range(4)] for _ in range(4)],  # Weights from first hidden layer to second hidden layer
			[[0.0 for _ in range(4)] for _ in range(4)],  # Weights from second hidden layer to third hidden layer
			[[0.0 for _ in range(2)] for _ in range(4)]   # Weights from third hidden layer to output layer
		]

	def update(self):
		
		
		self.vectorToPlanet = [self.x - screen_width / 2, self.y - screen_height / 2 ]
		self.distanceToPlanet = math.sqrt(self.vectorToPlanet[0]**2 + self.vectorToPlanet[1]**2)
		self.angleToPlanet = math.atan2(self.vectorToPlanet[1], self.vectorToPlanet[0])

		self.height = self.distanceToPlanet - planetRadius



		if self.height < 0:
			self.isAlive = False


		self.velocityX -= gravityStrength * math.cos(self.angleToPlanet)
		self.velocityY -= gravityStrength * math.sin(self.angleToPlanet)

		if self.engineOn:
			if self.fuel > 0:
				self.fuel -= 1
				self.velocityX += self.enginePower * math.cos(self.angle)
				self.velocityY += self.enginePower * math.sin(self.angle)
				self.color = orange
			else:
				self.engineOn = False

		self.x += self.velocityX
		self.y += self.velocityY

		self.neuralNetworkValues[0][0] = self.height
		self.neuralNetworkValues[0][1] = self.angle
		self.neuralNetworkValues[0][2] = self.velocityX
		self.neuralNetworkValues[0][3] = self.velocityY

		if self.isAlive:
			self.score += 1

		self.calculateNeuralNetwork()


	def calculateNeuralNetwork(self): #calculates the neural network and decides if the engine should be on and the angle changed
		for i in range(1, len(self.neuralNetworkValues)):
			for j in range(len(self.neuralNetworkValues[i])):
				sum = 0
				for k in range(len(self.neuralNetworkValues[i-1])):
					sum += self.neuralNetworkValues[i-1][k] * self.neuralNetworkWeights[i-1][j][k]
				self.neuralNetworkValues[i][j] = self.activate(sum)
		
		if self.neuralNetworkValues[3][0] > 0.5:
			self.engineOn = True
			self.color = orange
		else:
			self.engineOn = False
			self.color = white
		if self.neuralNetworkValues[3][1] > 0.5:
			self.angle += math.pi / 8

		
	def activate(self, x):
		return 1 / (1 + math.exp(-x))  # Sigmoid activation function
	
	def randomizeWeights(self):
		for i in range(len(self.neuralNetworkWeights)):
			for j in range(len(self.neuralNetworkWeights[i])):
				for k in range(len(self.neuralNetworkWeights[i][j])):
					self.neuralNetworkWeights[i][j][k] = random.uniform(-1, 1)

	
	def draw(self):
		# Calculate the points of the triangle
		base_center = (int(self.x), int(self.y))
		tip_x = int(self.x + 20 * math.cos(self.angle))
		tip_y = int(self.y + 20 * math.sin(self.angle))
		left_x = int(self.x + 10 * math.cos(self.angle + math.pi/2))
		left_y = int(self.y + 10 * math.sin(self.angle + math.pi/2))
		right_x = int(self.x + 10 * math.cos(self.angle - math.pi/2))
		right_y = int(self.y + 10 * math.sin(self.angle - math.pi/2))

		# Draw the triangle
		pygame.draw.polygon(screen, self.color, [(tip_x, tip_y), (left_x, left_y), (right_x, right_y)])





rockets = []

def aliveRocketsExist():
	for rocket in rockets:
		if rocket.isAlive:
			return True
	return False


# Main game loop
running = True
while running:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False

	if not generationExists:
		for i in range(initialNumberOfRockets):
			rockets.append(rocket())
			rockets[i].randomizeWeights()
		generationExists = True
		trainingIsRunning = True

	if generationExists and trainingIsRunning:
		for rocket in rockets:
			rocket.update()
		if not aliveRocketsExist():
			trainingIsRunning = False

	screen.fill(blue)

	pygame.draw.circle(screen, (255, 255, 255), (screen_width // 2, screen_height // 2), planetRadius, 0)

	# Draw all rockets
	for rocket in rockets:
		if rocket.isAlive:
			rocket.draw()

	pygame.display.flip()
	clock.tick(FPS) 

# Quit Pygame
pygame.quit()
sys.exit()  # Add this line to ensure the program exits cleanly


