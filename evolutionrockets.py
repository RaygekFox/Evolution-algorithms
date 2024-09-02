import pygame # type: ignore
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
FPS = 60

#State variables:
generationExists = False #if a generation exists, meaning if balls[] is not empty
trainingIsRunning = False #if the process of training should be running right now
winnerIsFound = False
numberOfGenerations = 0

#Configuration:
NumberOfSurvivors = 2
NumberOfCopies = 4
StrenfthOfMutation = 100

planetRadius = 50
gravityStrength = 1

class rocket:
	def __init__(self, x, y):
		self.x = screen_width / 2
		self.y = screen_height / 2 + planetRadius
		self.angle = math.pi / 2
		self.velocityX = 0
		self.velocityY = 0
		self.fuel = 100
		self.isAlive = True
		self.engineOn = False
		self.height = 0
		self.vectorToPlanet = [self.x - screen_width / 2, self.y - screen_height / 2 ]
		self.distanceToPlanet = planetRadius
		self.angleToPlanet = math.atan2(self.vectorToPlanet[1], self.vectorToPlanet[0])
		self.hasLaunched = False
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

		self.velocityX += gravityStrength * math.cos(self.angleToPlanet)
		self.velocityY += gravityStrength * math.sin(self.angleToPlanet)

		self.x += self.velocityX
		self.y += self.velocityY

		self.neuralNetworkValues[0][0] = self.height
		self.neuralNetworkValues[0][1] = self.angle
		self.neuralNetworkValues[0][2] = self.velocityX
		self.neuralNetworkValues[0][3] = self.velocityY

	def calculateNeuralNetwork(self):
		for i in range(1, len(self.neuralNetworkValues)):
			for j in range(len(self.neuralNetworkValues[i])):
				sum = 0
				for k in range(len(self.neuralNetworkValues[i-1])):
					sum += self.neuralNetworkValues[i-1][k] * self.neuralNetworkWeights[i-1][j][k]
				self.neuralNetworkValues[i][j] = self.activate(sum)

	def activate(self, x):
		return 1 / (1 + math.exp(-x))  # Sigmoid activation function




