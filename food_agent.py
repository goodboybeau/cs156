import sys

START_COORDS = (0,0)
FOOD_COORDS = (0,0)

def hueristic_manhattan():
	pass

def hueristic_euclidean():
	pass

def hueristic_made_up():
	pass

def get_map(filename):
	read_map = open(filename, 'r').read().split('\n')
	cols = len(read_map[0])
	rows = len(read_map)
	food_maze = [[0 for x in xrange(rows)] for x in xrange(cols)]

	for x in range(cols):
		for y in range(rows):
			next = read_map[x][y]
			food_maze[x][y] = next
			if next == '@':
				START_COORDS = (x,y)
			elif next == '%':
				FOOD_COORDS = (x,y)

	return food_maze

def print_map(map):
	for x in map:
		print x

if __name__ == '__main__':
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

	food_maze = get_map(file_name)
	print_map(food_maze)