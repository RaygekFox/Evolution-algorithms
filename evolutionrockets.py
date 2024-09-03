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
screen_width = 1200
screen_height = 800
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
NumberOfCopies = 10
StrenfthOfMutation = 1
CurrentBestScore = 0

planetRadius = 150
gravityStrength = 10
initialFuel = 25

class rocket:
	def __init__(self):
		self.x = screen_width / 2
		self.y = screen_height / 2 + planetRadius + 10
		self.color = white
		self.angle = math.pi / 2
		self.velocityX = 0
		self.velocityY = 0
		self.fuel = initialFuel
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
				self.color = (0,255,0)


		self.velocityX *= 0.99
		self.velocityY *= 0.99

		self.x += self.velocityX
		self.y += self.velocityY

		self.neuralNetworkValues[0][0] = self.height
		self.neuralNetworkValues[0][1] = self.angle
		self.neuralNetworkValues[0][2] = self.velocityX
		self.neuralNetworkValues[0][3] = self.velocityY

		if self.isAlive:
			self.score += 1

		self.calculateNeuralNetwork()

		# Increase fuel by 0.1
		self.fuel += 0.01



	def calculateNeuralNetwork(self): #calculates the neural network and decides if the engine should be on and the angle changed
		for i in range(1, len(self.neuralNetworkValues)):
			for j in range(len(self.neuralNetworkValues[i])):
				sum = 0
				for k in range(len(self.neuralNetworkValues[i-1])):
					sum += self.neuralNetworkValues[i-1][k] * self.neuralNetworkWeights[i-1][j][k]
				self.neuralNetworkValues[i][j] = self.activate(sum)
		
		if self.neuralNetworkValues[3][0] > 0.5:
			self.engineOn = True
			#self.color = orange
		else:
			self.engineOn = False
			#self.color = white

		self.angle += (self.neuralNetworkValues[3][1]-0.5) * 2 * math.pi
			

		
	def activate(self, x):
		try:
			return 1 / (1 + math.exp(-x))  # Sigmoid activation function
		except OverflowError:
			return 0  # Return 0 for very large negative inputs
	
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

def chooseSurvivors(rockets):
	survivors = []
	rockets.sort(key=lambda x: x.score, reverse=True)
	for i in range(NumberOfSurvivors):
		survivors.append(rockets[i])
	return survivors

def createCopies(survivors):
	global NumberOfCopies
	nextGeneration = []
	for i in range(len(survivors)):
		for j in range(NumberOfCopies):
			nextGeneration.append(copy.deepcopy(survivors[i]))
	return nextGeneration

def mutateWeights(mutatingRockets):
	for rocket in mutatingRockets:
		for i in range(len(rocket.neuralNetworkWeights)):
			for j in range(len(rocket.neuralNetworkWeights[i])):
				for k in range(len(rocket.neuralNetworkWeights[i][j])):
					rocket.neuralNetworkWeights[i][j][k] += random.uniform(-1, 1) * StrenfthOfMutation
	return mutatingRockets

def resetRockets(rockets):
	for rocket in rockets:
		rocket.score = 0
		rocket.isAlive = True
		rocket.engineOn = True
		rocket.fuel = initialFuel
		rocket.x = screen_width / 2
		rocket.y = screen_height / 2 + planetRadius + 10
		rocket.angle = math.pi / 2
		rocket.velocityX = 0
		rocket.velocityY = 0
		rocket.color = white
	return rockets
	

		

def createNewGeneration(rockets):
	global CurrentBestScore
	survivors = chooseSurvivors(rockets)
	print("Best score: ",survivors[0].score)
	CurrentBestScore = survivors[0].score
	copies = createCopies(survivors)
	mutatedRockets = mutateWeights(copies)
	rockets = survivors + mutatedRockets
	rockets = resetRockets(rockets)
	return rockets

def changeFPS(newFPS):
	global FPS
	FPS = newFPS

def changeSOM(newSOM):
	global StrenfthOfMutation
	StrenfthOfMutation += newSOM




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
		numberOfGenerations += 1

	if generationExists and trainingIsRunning:
		for rocket in rockets:
			rocket.update()
		if not aliveRocketsExist():
			rockets = createNewGeneration(rockets)
			numberOfGenerations += 1
			print("Generation: ", numberOfGenerations)
	
	
	
	screen.fill(blue)

	pygame.draw.circle(screen, (255, 255, 255), (screen_width // 2, screen_height // 2), planetRadius, 0)

	# Draw all rockets
	for rocket in rockets:
		if rocket.isAlive:
			rocket.draw()

	# Create buttons for FPS settings
	button_width, button_height = 80, 30
	button_y = screen_height - 40
	button_colors = [(200, 200, 200), (180, 180, 180), (160, 160, 160)]
	button_texts = ["3 FPS", "15 FPS", "60 FPS"]
	button_fps = [3, 15, 60]

	for i, (text, fps) in enumerate(zip(button_texts, button_fps)):
		if i >= len(button_colors):
			print(f"Warning: i ({i}) is out of range for button_colors")
			break
		button_x = 20 + i * (button_width + 10)
		button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
		pygame.draw.rect(screen, button_colors[i], button_rect)

		font = pygame.font.Font(None, 24)
		text_surface = font.render(text, True, (0, 0, 0))
		text_rect = text_surface.get_rect(center=button_rect.center)
		screen.blit(text_surface, text_rect)	

		mouse_pos = pygame.mouse.get_pos()
		click = pygame.mouse.get_pressed()
		if button_rect.collidepoint(mouse_pos) and click[0] == 1:
			changeFPS(fps)			
		
		# Add debug print
		print(f"Drawing button {i}: color={button_colors[i]}, text={text}, fps={fps}")

	# After the loop, print the lengths of all lists
	print(f"Lengths: colors={len(button_colors)}, texts={len(button_texts)}, fps={len(button_fps)}")

	button_y = screen_height - 80
	button_texts = ["SOM -", "SOM +"]
	button_colors = [(200, 200, 200), (180, 180, 180)]
	button_som = [-0.1, 0.1]

	for i, (text, som) in enumerate(zip(button_texts, button_som)):
		button_x = 20 + i * (button_width + 10)
		button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
		pygame.draw.rect(screen, button_colors[i], button_rect)
		
		font = pygame.font.Font(None, 24)
		text_surface = font.render(text, True, (0, 0, 0))
		text_rect = text_surface.get_rect(center=button_rect.center)
		screen.blit(text_surface, text_rect)
		
		# Check for button clicks
		mouse_pos = pygame.mouse.get_pos()
		click = pygame.mouse.get_pressed()
		if button_rect.collidepoint(mouse_pos) and click[0] == 1:
			changeSOM(som)
	
	# Draw text for generation, best score, and strength of mutation
	font = pygame.font.Font(None, 24)
	text_color = (255, 255, 255)  # White color for text
	
	# Number of generations
	gen_text = f"Generation: {numberOfGenerations}"
	gen_surface = font.render(gen_text, True, text_color)
	screen.blit(gen_surface, (20, 20))
	
	# Best score
	best_score = CurrentBestScore
	score_text = f"Best Score: {best_score}"
	score_surface = font.render(score_text, True, text_color)
	screen.blit(score_surface, (20, 50))
	
	# Strength of mutation
	som_text = f"Strength of Mutation: {StrenfthOfMutation:.1f}"
	som_surface = font.render(som_text, True, text_color)
	screen.blit(som_surface, (20, 80))
		
	# Draw neural network visualization for rockets[0]
	if rockets:
		nn_width, nn_height = 300, 200
		nn_x, nn_y = screen_width - nn_width - 20, 20
		layer_sizes = [4, 4, 4, 2]
		max_layer_size = max(layer_sizes)
		
		# Calculate positions for nodes
		positions = []
		for i, layer_size in enumerate(layer_sizes):
			layer_x = nn_x + i * (nn_width / (len(layer_sizes) - 1))
			for j in range(layer_size):
				y_offset = (max_layer_size - layer_size) / 2
				node_y = nn_y + (y_offset + j) * (nn_height / (max_layer_size - 1))
				value = (math.log(math.log(abs(rockets[0].neuralNetworkValues[i][j])+1)+1))
				positions.append((layer_x, node_y, value))
				
				
		
		# Draw connections (weights)
		node_index = 0
		for layer, next_layer in zip(layer_sizes[:-1], layer_sizes[1:]):
			for i in range(layer):
				for j in range(next_layer):
					start = (positions[node_index + i][0],positions[node_index + i][1])
					end = (positions[node_index + layer + j][0],positions[node_index + layer + j][1])
					weight = rockets[0].neuralNetworkWeights[len(positions) // 4 - 1][i][j]
					color = (0, 255, 0) if weight > 0 else (255, 0, 0)
					thickness = int(math.log(abs(weight) + 1) * 2) + 1
					pygame.draw.line(screen, color, start, end, thickness)
			node_index += layer
		
		# Draw nodes
		for pos in positions:
			pygame.draw.circle(screen, white, (int(pos[0]), int(pos[1])), pos[2]*10)

		

	pygame.display.flip()
	clock.tick(FPS) 

# Quit Pygame
pygame.quit()
sys.exit()  # Add this line to ensure the program exits cleanly


