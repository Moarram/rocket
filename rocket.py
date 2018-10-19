import pygame
import random as r
from math import *

# This program requires the pygame module.
# To install it run "pip3 install pygame" or "pip install pygame" from the command line

# TODO
# make this into a game
# add hitbox
# add fuel resource
# add shield resource
# add boundary
# add objects (black holes, astroids, fuel supply)
# remove gravity options

# Layout
FRAMERATE = 160
FONT_SIZE = 16
WIDTH = 900
HEIGHT = 900
INFO = 350

# Vector Magnitudes
THRUSTER_FORCE = 0.03
THRUSTER_ADJUST_STEP = 0.01
STABILIZER_FORCE = 0.01
STABILIZER_ADJUST_STEP = 0.002

# Particles
PARTICLE_DECAY = 30
PARTICLE_STRAY = 5 # 1 in x chance of particle straying
PARTICLE_MAG_MULT = 30

# Colors
FONT_C = (255, 255, 255)
THRUST_V_C = (255, 255, 0)
VELOCITY_V_C = (127, 255, 127)
STABILIZE_V_C = (127, 127, 255)
BOOST_V_C = (255, 255, 255)
GRAVITY_V_C = (255, 127, 127)
WELL_V_C = (127, 127, 127)
TRUE_C = (0, 255, 0)
FALSE_C = (255, 0, 0)
BODY_C = (255, 255, 255)
WING_C = (255, 0, 0)
PLANET_C = (120, 80, 40)
PARTICLE_1P_C = (255, 255, 255)
PARTICLE_2P_C = (255, 255, 127)
PARTICLE_3P_C = (255, 255, 0)
PARTICLE_4P_C = (255, 0, 0)
PARTICLE_5P_C = (50, 50, 50)
PARTICLE_6P_C = (0, 0, 0)
PARTICLE_1S_C = (255, 255, 255)
PARTICLE_2S_C = (127, 255, 255)
PARTICLE_3S_C = (127, 127, 255)
PARTICLE_4S_C = (0, 0, 255)
PARTICLE_5S_C = (0, 0, 0)

width = WIDTH + INFO
height = HEIGHT

pygame.init()
pygame.display.set_caption("rocket.py")

screen = pygame.display.set_mode((width, height)) # initialize game window

font = pygame.font.SysFont("consolas", FONT_SIZE)
clock = pygame.time.Clock()

particles = True
detail = False
gravity = False
well = False
center = (WIDTH//2, HEIGHT//2)

def translate(point):
	# account for header and whatnot here
	return (int(point[0]), int(point[1]))

def line(point_1, point_2, color, width=1):
	pygame.draw.line(screen, color, translate(point_1), translate(point_2), width)

def vect_add(v_1, v_2):
	x = cos(v_1.angle)*v_1.magnitude + cos(v_2.angle)*v_2.magnitude
	y = sin(v_1.angle)*v_1.magnitude + sin(v_2.angle)*v_2.magnitude
	return Vector(atan2(y, x), sqrt(x*x + y*y))

def vect_scal(v, scalar):
	return Vector(v.angle, v.magnitude*scalar)

def vect_rev(v):
	return Vector(v.angle + pi, v.magnitude)


class Vector:
	angle = float
	magnitude = float

	def __init__(self, angle, magnitude):
		self.angle = angle
		self.magnitude = magnitude

	def add(self, vector):
		x = cos(self.angle)*self.magnitude + cos(vector.angle)*vector.magnitude
		y = sin(self.angle)*self.magnitude + sin(vector.angle)*vector.magnitude
		self.angle = atan2(y, x)
		self.magnitude = sqrt(x*x + y*y)

	def set_angle_by_coords(self, start, end):
		x = end[0] - start[0]
		y = end[1] - start[1]
		self.angle = atan2(y, x)
		
	def get_new_position(self, start):
		x = start[0] + cos(self.angle)*self.magnitude
		y = start[1] + sin(self.angle)*self.magnitude
		return (x, y)

	def draw(self, position, color, amplify=2000):
		x = position[0] + cos(self.angle)*self.magnitude*amplify
		y = position[1] + sin(self.angle)*self.magnitude*amplify
		line(position, (x, y), color, 2)


class Particle:
	def __init__(self, position, vector, color_list):
		self.position = position
		self.vector = vector
		self.color_list = color_list
		self.color = color_list[0]
		self.steps = len(color_list) - 1
		self.count = 0
		self.gravity_vector = Vector(0.5*pi, 0.015)
		self.well_vector = Vector(0.0, 0.0)

	def decay(self):
		index = self.count//PARTICLE_DECAY
		if index < self.steps:
			c = []
			for i in range(3):
				c.append(int(self.color_list[index][i] - (((self.color_list[index][i]) - self.color_list[index + 1][i])/PARTICLE_DECAY)*(self.count%PARTICLE_DECAY)))
				# print(self.color_list[index][i], "-", ((self.color_list[index][i]) - self.color_list[index + 1][i])/PARTICLE_DECAY, "*", self.count%PARTICLE_DECAY)
			self.color = (c[0], c[1], c[2])
			# print(self.color_list[index], self.color, self.color_list[index + 1])
	
	def move(self):
		if r.randint(1, PARTICLE_STRAY) == 1:
			x = r.randint(0, 2)
			y = r.randint(0, 2)
			self.position = (self.position[0] + x - 1, self.position[1] + y - 1)
		self.position = self.vector.get_new_position(self.position)

	def update(self):
		if well:
			distance = sqrt((self.position[0] - center[0])**2 + (self.position[1] - center[1])**2)
			self.well_vector.set_angle_by_coords(self.position, center)
			self.well_vector.magnitude = 2/distance
			self.vector.add(self.well_vector)
		if gravity:
			self.vector.add(self.gravity_vector)
		if self.count >= self.steps*PARTICLE_DECAY:
			return False
		self.decay()
		self.move()
		self.count += 1
		return True
	
	def draw(self):
		point = translate(self.position)
		pygame.draw.rect(screen, self.color, pygame.Rect(point[0], point[1], 1, 1))
	

class Rocket:
	body = [(30, 0), (0, -10), (-10, -6), (-10, 6), (0, 10)]
	wing_1 = [(-15, 15), (-5, 15), (0, 10), (-9, 6)]
	wing_2 = [(-15, -15), (-5, -15), (0, -10), (-9, -6)]
	part_1 = [(-9, 0), (-9, 0), (-9, 0)]
	part_2 = [(-9, -1), (-9, 1)]

	def __init__(self, position):
		self.position = position
		self.thrust_vector = Vector(0.0, THRUSTER_FORCE)
		self.velocity_vector = Vector(0.0, 0.0)
		self.stabilize_vector = Vector(0.0, STABILIZER_FORCE)
		self.boost_vector = Vector(0.0, THRUSTER_FORCE*3)
		self.gravity_vector = Vector(0.5*pi, 0.015)
		self.well_vector = Vector(0.0, 0.0)
		self.particle_list = []
		self.thrusting = False
		self.stabilize = False
		self.boost = False

	def rotate(self, point_list, rad):
		out = []
		for point in point_list:
			x = point[0]*cos(rad) - point[1]*sin(rad)
			y = point[0]*sin(rad) + point[1]*cos(rad)
			out.append((x + self.position[0], y + self.position[1]))
		return out

	def add_particles(self, position_list, vector, color_list):
		for i in range(len(position_list)):
			thrust = vect_rev(vector)
			thrust.magnitude *= PARTICLE_MAG_MULT
			direction = vect_add(thrust, self.velocity_vector)
			position = self.rotate(position_list, vector.angle)[i]
			self.particle_list.append(Particle(position, direction, color_list))
	
	def update(self, target, thrusting, stabilize, boost, pulse):
		self.thrusting = thrusting
		self.stabilize = stabilize
		self.boost = boost
		self.pulse = pulse
		self.thrust_vector.set_angle_by_coords(self.position, target)
		self.boost_vector.magnitude = self.thrust_vector.magnitude*3
		if well:
			distance = sqrt((self.position[0] - center[0])**2 + (self.position[1] - center[1])**2)
			self.well_vector.set_angle_by_coords(self.position, center)
			self.well_vector.magnitude = 2/distance
			self.velocity_vector.add(self.well_vector)
		if gravity:
			self.velocity_vector.add(self.gravity_vector)
		if thrusting:
			self.velocity_vector.add(self.thrust_vector)
		if stabilize:
			self.stabilize_vector.angle = self.velocity_vector.angle - pi
			self.velocity_vector.add(self.stabilize_vector)
		if boost:
			self.boost_vector.set_angle_by_coords(self.position, target)
			self.velocity_vector.add(self.boost_vector)
		self.position = self.velocity_vector.get_new_position(self.position)

		if particles:
			if self.boost:
				self.add_particles(self.part_1 + self.part_2, self.boost_vector, [PARTICLE_1P_C, PARTICLE_3P_C, PARTICLE_4P_C, PARTICLE_5P_C, PARTICLE_6P_C])
			if self.thrusting and not self.boost:
				self.add_particles(self.part_1, self.thrust_vector, [PARTICLE_1P_C, PARTICLE_3P_C, PARTICLE_4P_C, PARTICLE_5P_C, PARTICLE_6P_C])
				self.add_particles(self.part_2, self.thrust_vector, [PARTICLE_2P_C, PARTICLE_4P_C, PARTICLE_5P_C, PARTICLE_6P_C])
			if self.stabilize:
				self.add_particles([(0, 0), (0, 0), (0, 0)], self.stabilize_vector, [PARTICLE_1S_C, PARTICLE_2S_C, PARTICLE_3S_C, PARTICLE_4S_C, PARTICLE_5S_C])
			if self.pulse:
				for pair in [(0, 0.025), (0, 0.02), (-0.5, 0.01), (0.5, 0.01), (-0.5, 0.02), (0.5, 0.02), (-0.2, 0.015), (0.2, 0.015)]:
					self.add_particles(self.part_1 + self.part_1 + self.part_2, Vector(self.thrust_vector.angle + pair[0], pair[1]), [PARTICLE_1P_C, PARTICLE_1P_C, PARTICLE_5P_C, PARTICLE_6P_C])
			for particle in self.particle_list:
				if not particle.update():
					self.particle_list.remove(particle)
					continue

	def draw(self):
		if particles:
			for particle in self.particle_list:
				particle.draw()

		if well:
			pygame.draw.circle(screen, PLANET_C, center, 5)

		if detail:
			self.velocity_vector.draw(self.position, VELOCITY_V_C, 200)
			if well:
				self.well_vector.draw(self.position,WELL_V_C)
			if gravity:
				self.gravity_vector.draw(self.position, GRAVITY_V_C)
			if self.stabilize:
				self.stabilize_vector.draw(self.position, STABILIZE_V_C)
			if self.thrusting:
				self.thrust_vector.draw(self.position, THRUST_V_C)
			if self.boost:
				self.boost_vector.draw(self.position, BOOST_V_C)
			point = translate((self.position[0] - 2, self.position[1] - 2))
			pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(point[0], point[1], 4, 4))

		else:
			r_wing_1 = self.rotate(self.wing_1, self.thrust_vector.angle)
			pygame.draw.aalines(screen, WING_C, True, r_wing_1)
			pygame.draw.polygon(screen, WING_C, r_wing_1)

			r_wing_2 = self.rotate(self.wing_2, self.thrust_vector.angle)
			pygame.draw.aalines(screen, WING_C, True, r_wing_2)
			pygame.draw.polygon(screen, WING_C, r_wing_2)

			r_body = self.rotate(self.body, self.thrust_vector.angle)
			pygame.draw.aalines(screen, BODY_C, True, r_body)
			pygame.draw.polygon(screen, BODY_C, r_body)



def text_line(text_list, position):
	x_coord = position[0]
	for item in text_list:
		message = font.render(item[0], True, item[1])
		screen.blit(message, (x_coord, position[1]))
		x_coord += message.get_width()

def text_block(text_list_list, position):
	y_coord = position[1]
	for text_list in text_list_list:
		text_line(text_list, (position[0], y_coord))
		y_coord += FONT_SIZE
	
def play():
	thrusting = False
	stabilize = False
	boost = False
	pulse = False
	abort = False
	done = False
	global particles
	global detail
	global gravity
	global well
	well = False

	rocket = Rocket((WIDTH/2, HEIGHT/2))
	while not (done or abort): 
		for event in pygame.event.get():
			if event.type == pygame.QUIT: # clicking X on window or ctrl+C in cmd will exit loop
				abort = True

			if event.type == pygame.MOUSEBUTTONDOWN:
				if event.button == 1:
					thrusting = True
					pulse = True
				if event.button == 3:
					stabilize = True

			if event.type == pygame.MOUSEBUTTONUP:
				if event.button == 1:
					thrusting = False
				if event.button == 3:
					stabilize = False

			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					done = True
				if event.key == pygame.K_SPACE:
					boost = True
					pulse = True
				if event.key == pygame.K_EQUALS:
					rocket.thrust_vector.magnitude += THRUSTER_ADJUST_STEP
				if event.key == pygame.K_MINUS:
					rocket.thrust_vector.magnitude -= THRUSTER_ADJUST_STEP
					if rocket.thrust_vector.magnitude < THRUSTER_ADJUST_STEP:
						rocket.thrust_vector.magnitude = THRUSTER_ADJUST_STEP
				if event.key == pygame.K_PERIOD:
					rocket.stabilize_vector.magnitude += STABILIZER_ADJUST_STEP
				if event.key == pygame.K_COMMA:
					rocket.stabilize_vector.magnitude -= STABILIZER_ADJUST_STEP
					if rocket.stabilize_vector.magnitude < STABILIZER_ADJUST_STEP:
						rocket.stabilize_vector.magnitude = STABILIZER_ADJUST_STEP
				if event.key == pygame.K_1:
					detail = not detail
				if event.key == pygame.K_2:
					particles = not particles
				if event.key == pygame.K_3:
					gravity = not gravity
				if event.key == pygame.K_4:
					well = not well

			if event.type == pygame.KEYUP:
				if event.key == pygame.K_SPACE:
					boost = False

		mouse_pos = pygame.mouse.get_pos()

		text = [[("Rocket", FONT_C)],
				[("Velocity: ", FONT_C), ("{:.3f}".format(rocket.velocity_vector.magnitude), VELOCITY_V_C)],
				[("Thrusters [M1]: ", FONT_C), (("ON", TRUE_C) if thrusting else ("OFF", FALSE_C))],
				[("Thruster Power [+/-]: ", FONT_C), ("{:.3f}".format(rocket.thrust_vector.magnitude), THRUST_V_C)],
				[("Stabilizers [M2]: ", FONT_C), (("ON", TRUE_C) if stabilize else ("OFF", FALSE_C))],
				[("Stabilizer Power [</>]: ", FONT_C), ("{:.4f}".format(rocket.stabilize_vector.magnitude), STABILIZE_V_C)],
				[("Boost [Space]: ", FONT_C), (("ON", TRUE_C) if boost else ("OFF", FALSE_C))],
				[("Boost Power: ", FONT_C), ("{:.3f} ".format(rocket.thrust_vector.magnitude*3), THRUST_V_C), ("(Thrust x3)", FONT_C)],
				[(" ", FONT_C)],
				[("General", FONT_C)],
				[("Vector Mode [1]: ", FONT_C), (("ON", TRUE_C) if detail else ("OFF", FALSE_C))],
				[("Particles [2]: ", FONT_C), (("ON", TRUE_C) if particles else ("OFF", FALSE_C))],
				[("Linear Gravity [3]: ", FONT_C), (("ON", TRUE_C) if gravity else ("OFF", FALSE_C))],
				[("Radial Gravity [4]: ", FONT_C), (("ON", TRUE_C) if well else ("OFF", FALSE_C))]]

		screen.fill((0, 0, 0)) # fill screen with black so we can re-draw from scratch
		
		if detail:
			line(rocket.position, mouse_pos, (50, 50, 50))
		rocket.update(pygame.mouse.get_pos(), thrusting, stabilize, boost, pulse)
		rocket.draw()

		pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(WIDTH, 0, width, height))
		line((WIDTH, 0), (WIDTH, HEIGHT), (255, 255, 255))
		text_block(text, (WIDTH + 5, 5))

		pulse = False
		pygame.display.flip()
		clock.tick(FRAMERATE) # wait for 1/FRAMERATE seconds

	if abort:
		print("Exiting...")
		return False # we want to close window
	print("Returning...")
	return True # we want to return to menu
	
def main():
	done = False
	while not done:
		if not play():
			done = True
	print("Application closed.")
	
main()