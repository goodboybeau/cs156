'''
@author		Jeff Aronhalt
@sjsuid		007939971
'''

'''

function Decision-Tree-Learning(examples, attributes, parent_examples) returns a tree
    if examples is empty then return Plurality-Value(parent_examples)
    else if all examples have the same classification then return the classification
    else if attributes is empty then return Plurality-Value(examples)
    else
        A := argmax_(a in attributes)Importance(a, examples)
        tree :=  a new decision tree with root test A
        for each value v_k of A do
            exs := {e : e in examples and e.A = v_k}
            subtree := Decision-Tree-Learning(exs, attributes -  A, examples)
            add a branch to tree with label (A=v_k) and subtree subtree
        return tree

'''

import sys, random
from math import log10, floor

class Tree(object):
	class Branch(object):
		def __init__(self, val, subtree):
			self.val = val
			self.subtree = subtree

		def get_str(self, indent):
			s = ('\t' * indent) + 'val:%f\n' % self.val
			if not (type(self.subtree) == type(False)):
				s += ('\t' * indent) + ('subtree:\n%s' % self.subtree.get_str(indent+1)) 
			else:
				s += ('\t' * indent) + ('leaf:%s\n' % str(self.subtree))
			return s

	def __init__(self, attr, branches=None, parent_branch=None):
		#root is str rep of attr function of ExMap
		self.root = attr
		self.branches = branches or []
		self.parent_branch = parent_branch

	def add_branch(self, label, subtree):
		self.branches.append( Tree.Branch(label, subtree) )

	def get_str(self, indent):
		s = ('\t' * indent) + 'root:%s\n' % str(self.root)
		for b in self.branches:
			s += ('\t' * indent) + 'branch:\n%s' % b.get_str(indent+1)
		return s

	def __str__(self):
		return self.get_str(0) 

	def determine_connectedness(self, _map, indent=0):
		print '\t'*indent, self.root
		v = _map.get_attr(self.root)
		for b in self.branches:
			if v == b.val:
				if type(b.subtree) == type(True):
					return b.subtree
				else:
					return b.subtree.determine_connectedness(_map, indent+1) 

def DecisionTreeLearning(examples, attributes, parent_examples):

	def Classification(ex):
		return ex.lame_check_connectedness()

	def PluralityValue(exs):
		c = 0
		for ex in exs:
			if ex.lame_check_connectedness():
				c += 1

		return c >= (len(exs) / 2)

	def Importance(attr, exs):
		return sum(e.get_attr(attr) for e in exs)
	
	if len(examples) == 0: 
		return PluralityValue(parent_examples)

	elif all(Classification(e) == Classification(examples[0]) for e in examples):
		return Classification(examples[0])

	elif len(attributes) == 0:
		return PluralityValue(examples)
	
	else:
		A = None
		for a in attributes:
			A = a if Importance(a, examples) >= ( Importance(A, examples) if A is not None else 0 ) else A 
		tree = Tree(A)
		for val in set([e.get_attr(A) for e in examples]):
			exs = [ ex for ex in examples if ex.get_attr(A) == val]
			attrs = list(attributes)
			attrs.remove(A)
			subtree = DecisionTreeLearning(exs, attrs, examples)
			tree.add_branch(val, subtree)
		return tree

def bucketize(val):
	if val >= 0 and val < .1:
		return 0
	if val >= .1 and val < .3:
		return .2
	if val >= .3 and val < .5:
		return .4
	if val >= .5 and val < .7:
		return .6
	if val >= .7 and val <= 1:
		return .9

	print val

	raise Exception

class ExMap(list):

	Attributes = ['count_ratio', 'lower_tri_ratio', 'upper_tri_ratio', 'diag_ratio']#, 'horizontal_change', 'vertical_change']

	def __init__(self, entries):
		self._connected = entries.pop(len(entries) - 1) if 'C' in entries[len(entries) - 1] else 'UNKNOWN'

		self._count = 0
		for x in range(5):
			for y in range(5):
				if entries[y][x] == 'O':
					if not self._count:
						self.first_coord = (x,y)
					self._count += 1 

		super(ExMap, self).__init__(entries)

		self.attr_map = {
			'count_ratio': self.attr_count_ratio,
			'lower_tri_ratio': self.attr_lower_ratio,
			'upper_tri_ratio': self.attr_upper_ratio,
			'diag_ratio': self.attr_diag_ratio,
			'horizontal_change': self.attr_horizontal_change,
			'vertical_change': self.attr_vertical_change
		}

	def __str__(self):
		s = ''
		for x in self:
			s += ' '.join(x) + '\n'
		s += self._connected + '\n'

		for k, v in self.attr_map.iteritems():
			s += '%s:%f\n' % (k, v())
		# s += 'count_ratio:%f\n' % self.attr_count_ratio()
		# s += 'upper_ratio:%f\n' % self.attr_upper_ratio()
		# s += 'lower_ratio:%f\n' % self.attr_lower_ratio()
		# s += 'diag_ratio:%f\n' % self.attr_diag_ratio()
		return s

	def __repr__(self):
		s = ''
		for x in self:
			s += ' '.join(x) + '\n'
		s += self._connected + '\n'
		return s

	def get_attr(self, attr):
		if type(attr) == str:
			return self.attr_map[attr]()
		else:
			return 1 if self.get(attr[0], attr[1]) == 'O' else 0

	def get(self, x, y):
		return self.__getitem__(y)[x]

	def attr_count_ratio(self):
		c = float(self._count) / float(25)
		return bucketize(c)

	def attr_pos_occupied(self, x, y):
		return self.__getitem__(y)[x] == 'O'

	def attr_lower_ratio(self):
		c = 0
		for x in range(5):
			for y in range(x,5):
				if self.get(x,y) == 'O':
					c += 1

		c = float(c) / float(self._count)

		return bucketize(c)

	def attr_upper_ratio(self):
		c = 0
		for y in range(5):
			for x in range(y,5):
				if self.get(x,y) == 'O':
					c += 1

		c = float(c) / float(self._count)
		return bucketize(c)

	def attr_diag_ratio(self):
		c = 0
		for i in range(5):
			if self.get(i,i) == 'O':
				c += 1

		c = float(c) / float(self._count)
		return bucketize(c)

	def attr_vertical_change(self):
		c = 0
		s = 0
		last = self.get(0,0)
		for x in range(5):
			for y in range(5):
				if x == y == 0:
					continue

				n = self.get(x,y)
				if not (last == n):
					c += 1
				else:
					s += 1
				last = n

		c = float(c) / float(25)
		return bucketize(1 - c)

	def attr_horizontal_change(self):
		c = 0
		s = 0
		last = self.get(0,0)
		for y in range(5):
			for x in range(5):
				if x == y == 0:
					continue

				n = self.get(x,y)
				if not (last == n):
					c += 1
				else:
					s += 1
				last = n

		c = float(c) / float(25)
		return bucketize(1 - c)

	def get_neighbors(self, x, y):
		l, r, u, d = True, True, True, True
		if x == 0: l = False
		if x == 4: r = False
		if y == 0: u = False
		if y == 4: d = False

		neighs = []

		if l:
			if self.__getitem__(y)[x-1] == 'O':
				neighs.append( (x-1, y) )
		if r:
			if self.__getitem__(y)[x+1] == 'O':
				neighs.append( (x+1, y) )
		if u:
			if self.__getitem__(y-1)[x] == 'O':
				neighs.append( (x, y-1) )
		if d:
			if self.__getitem__(y+1)[x] == 'O':
				neighs.append( (x, y+1) )

		return neighs

	def lame_check_connectedness(self):

		if self._connected == 'DISCONNECTED':
			return False
		if self._connected == 'CONNECTED':
			return True

		self._connected = 'DISCONNECTED'
		if self._count == 1:
			self._connected = 'CONNECTED'
			return True

		def check_connected(_x, _y, left_to_check, count_left, checked):

			for x, y in self.get_neighbors(_x, _y):
				if (x, y) not in left_to_check and (x, y) not in checked:
					left_to_check.append( (x,y) )
			checked.append( (_x, _y) )
			count_left -= 1
			if len(left_to_check) is 0:
				return count_left
			x, y = left_to_check.pop()
			return check_connected(x, y, left_to_check, count_left, checked)



		#where we are in the graph
		pos_x, pos_y = self.first_coord
		#how many 'O's left to find
		count_left = self._count
		#DFS nodes to check for neighbors
		to_check = []
		#nodes checked
		checked = []

		if check_connected(pos_x, pos_y, to_check, count_left, checked) == 0:
			self._connected = 'CONNECTED'
			return True
		else:
			self._connected = 'DISCONNECTED'
			return False

def read_examples(filename):
	maps = []
	with open(filename,'r') as f:
		for m in [ e.split('\n') for e in f.read().split('\n\n') ]:
			if len(m) > 1:
				maps.append(ExMap( [ l.split() if 'C' not in l else l for l in m ]))

	return maps

def read_test_map(filename):
	with open(filename, 'r') as f:
		s = f.read().split('\n')
		if len(s) > len(s[0]):
			s.remove(len(s) - 1)

		m = ExMap( [l.split() for l in s ])
		print m 
		return m


'''
This creates a random grid.

it creates :count: random maps and writes each of them
 to a file called :filename: using random choices from the 
 lambda function defined inside the definition.

'''
def make_training_set(filename, count):
	random.seed(10)
	rand_map_entry = lambda : random.choice(['O', 'O', 'O',  'X'])

	def generate_random_map():
		rows = []
		for x in range(5):
			cols = []
			for y in range(5):
				cols.append(rand_map_entry())
			rows.append(cols)
		rando_map = ExMap(rows)
		return rando_map

	with open(filename, 'w') as f:
		for x in range(count):
			m = generate_random_map()
			m.lame_check_connectedness()
			f.write(repr(m) + '\n')

if __name__ == '__main__':

	for x in range(5):
		for y in range(5):
			ExMap.Attributes.append( (x,y) )

	print ExMap.Attributes

	make_training_set('some',20000)
	attributes = ExMap.Attributes

	dtree = DecisionTreeLearning(read_examples('some'), attributes, [])
	#print dtree
	if dtree.determine_connectedness(read_test_map(sys.argv[2])):
		print 'CONNECTED'
	else:
		print 'DISCONNECTED'