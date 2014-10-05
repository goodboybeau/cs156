'''
@author 	Jeffery Aronhalt
@sjsu_id	007939971
'''

import sys, time, math
import Queue
from Queue import PriorityQueue

# represents a node
class Node:
	calc = None
	visited_cost = None
	def __init__(self, pos, val):
		self.x = pos[0]
		self.y = pos[1]
		self.val = val
		self.cost = Node.calc(self,self.x,self.y) if Node.calc else None
		self.visited = False
		self.dont_go_back = False

	def __str__(self):
		string = "(x,y): %d,%d" % (self.x, self.y)
		string += " val: %s" % self.val
		string += " cost: %d" % self.get_cost()
		return string

	# this node's coords
	def coords(self):
		return (self.x,self.y)

	# this node's calculated cost
	def get_cost(self):
		return self.calc(self.x, self.y)

# gets a maze from a file
def get_maze(filename):
		global FOOD_COORDS
		read_maze = open(filename, 'r').read().split('\n')
		maze = []
		for row in range(len(read_maze)):
			r = []
			for col in range(len(read_maze[row])):
				n = Node((col,row), read_maze[row][col])
				r.append(n)
				if n.val == '%':
					FOOD_COORDS = n.coords()
				elif n.val == '@':
					START_COORDS = n.coords()
			if len(r) is not 0: maze.append(r)
		return maze, START_COORDS, FOOD_COORDS

# represents a map
class Map:
	def __init__(self, filename):
		self.maze, self.start, self.goal = get_maze(filename)
		self.current = self.maze[self.start[1]][self.start[0]]
		self.visited = [self.current]
		self.solution = [("Initial",self.current, str(self))]
		self.step = 0

	def __len__(self):
		return len(self.maze[0]) * len(self.maze)

	def __str__(self):
		string = ''
		for row in self.maze:
			for n in row:
				string += n.val
			string += '\n'
		return string

	# prints the solution set
	def show_solution(self):
		for step, node, view in self.solution:
			print "Step %s:" % step
			#print node
			print view

	# changes the values of the map and checks for success
	def update(self):
		for row in self.maze:
			for col in row:
				col.val = '.' if col.val == '@' else col.val

		self.maze[self.current.y][self.current.x].val = '@'
		if self.current.coords() == self.goal:
				self.solution.append((self.step+1,self.current,str(self)))
				self.show_solution()
				print "Problem solved! I had some noodles!"
				exit(0)

	# solves the food maze
	def solve(self):
		nexts = PriorityQueue()
		while True:
			self.step += 1
			self.current.visited = True
			possibilities = visitable_points(self.current, self.maze)
			for node in possibilities:
				nexts.put((node.get_cost(), node))
			next = nexts.get()
			try:
				while next[1].visited or (not are_neighbors(next[1].coords(), self.current.coords())):
					next = nexts.get(False)
				self.current = next[1]
				self.solution.append((self.step,self.current, str(self)))

			except Queue.Empty:
				try:
					self.current = self.solution.pop()[1]
					self.step -= 1

				except IndexError:
					print "No solution"
					exit(1)

			self.update()
			#time.sleep(1)

# represents the manhattan hueristic 
def hueristic_manhattan(map):
	
	def c():
		return 1

	def f(n, x,y):
		return abs(x-map.goal[0]) + abs(y-map.goal[1]) + c()

	Node.calc = f
	map.solve()

# represents the euclidean hueristic 
def hueristic_euclidean(map):

	def c():
		return 1

	def f(n, x,y):
		return math.sqrt(pow(abs(x-map.goal[0]),2) + pow(abs(y-map.goal[1]),2)) + c()

	Node.calc = f
	map.solve()

# represents the made-up hueristic 
def hueristic_made_up(map):

	def c():
		return int(time.time()) % 3

	def f(n, x,y):
		h = abs(x-map.goal[0]) + abs(y-map.goal[1]) + c()

	Node.calc = f
	map.solve()

def valid_point(node):
	global food_maze
	m = food_maze.maze
	if node.y >= len(m):
		return False
	if node.x >= len(m[node.y]):
		return False
	if node.val is not '#' and node.val is not '@':
		return True

def visitable_points(node, nodes):
	x, y = node.coords()
	points = []
	for _x, _y in [(x,y+1),(x,y-1),(x+1,y),(x-1,y)]:
		try:
			if valid_point(nodes[_y][_x]):
				points.append(nodes[_y][_x])
		except IndexError:
			pass
	return points

def are_neighbors(P,Q):
	if P[0] == Q[0] and (abs(P[1]-Q[1]) == 1):
		return True
	if P[1] == Q[1] and (abs(P[0]-Q[0]) == 1):
		return True
	return False


if __name__ == '__main__':
	global FOOD_COORDS
	global food_maze
	hueristic_map = {'manhattan':hueristic_manhattan, 'euclidean':hueristic_euclidean, 'made_up':hueristic_made_up}

	file_name = None
	hueristic = None
	
	try:
		file_name = sys.argv[1]
		hueristic = sys.argv[2]
		if hueristic not in hueristic_map.keys():
			raise AttributeError
	except IndexError:
		print "filename or hueristic not entered. exiting."
		exit(1)
	except AttributeError:
		print "%s is not a valid hueristic" % hueristic

	food_maze = Map(file_name)
	Node.visited_cost = len(food_maze) 
	
	hueristic_map[hueristic](food_maze)