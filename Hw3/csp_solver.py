'''
@author Jeff Aronhalt
@date	Nov. 2, 2014

@assignment HW3
@class 		CS156
@professor	Pollett
'''
import sys, string, time
from Queue import PriorityQueue, Queue

use_forward_checking = 0
#a variable's key is it's str(value)
variables = {}

#Number of distinct variables in the file
D = 0
#Largest value of an integer in a constraint
V = 0

class Value(str):
	def __init__(self, val, relations=None, is_variable=False):
		if not is_variable:
			assert( type(val) == (int) )
			self._assigned_val = val
		else:
			self._assigned_val = None
		super(Value, self).__init__(val)
		self._domain = range(0, 4)
		self._relations = relations or []

	def __str__(self):
		return super(Value, self).__str__()

	def __repr__(self):
		return super(Value, self).__str__()

	def get_relations_to(self, val):
		rels = []
		for rel_val in self._relations:
			if rel_val[1] == val:
				rels.append(rel_val[0])
		return rels

	def assigned(self):
		return self._assigned_val

	def count_to_be_removed_if_assignment(self, var, val):
		print "%s.count_to_be_removed_if_assignment(var=%s, val=%s)" % (self, var, val), val
		assert( type(val) == int )
		for rel, v in self._relations:
			if str(v) == str(var):
				return len(self.inconsistent_vals_in_domain(rel,val))
		return 0

	def inconsistent_vals_in_domain(self, rel, val):
		rel = rel.inverse()
		if 'eq' == str(rel):
			return self.vals_from_domain_not_equal_to(val)
		if 'ne' == str(rel):
			return self.vals_from_domain_equal_to(val)
		if 'lt' == str(rel):
			return self.vals_from_domain_less_than(val)
		if 'gt' == str(rel):
			return self.vals_from_domain_greater_than(val)

	def vals_from_domain_less_than(self, val):
		assert( type(val) == int )
		return [(x for x in self._domain if x < val)]

	def vals_from_domain_greater_than(self, val):
		assert( type(val) == int )
		return [(x for x in self._domain if x > val)]

	def vals_from_domain_equal_to(self, val):
		assert( type(val) == int )
		return [(x for x in self._domain if x == val)]

	def vals_from_domain_not_equal_to(self, val):
		assert( type(val) == int )
		return [(x for x in self._domain if x != val)]


class Variable(Value):
	def __init__(self, var):
		if string.lower(var[0]) not in string.lowercase:
			raise AttributeError('Variable cannot start with %s' % var[0])
		super(Variable, self).__init__(var, is_variable=True)

	def add_relation(self, rel, val):
		rel_val = rel, val
		self._relations.append(rel_val)
		#this means that it's explicit in the relationship to val
		#so, assign it
		if str(rel) == 'eq' and val.assigned() is not None:
			print "%s.add_relation(%s, %s) assigning %s" % (str(self), str(rel), str(val), val.assigned())
			self._assigned_val = val
		elif str(rel) == 'ne' and val.assigned() is not None:
			self._domain.remove(val.assigned())
			print "%s.add_relation(%s, %s)  removed %s from %s's domain" % (str(self), str(rel), str(val), val.assigned(), str(self))
		else:
			print "%s.add_relation(%s, %s) didn't assign %s" % (str(self), str(rel), str(val), val.assigned())

	def assingment_is_consistent(self, val):
		
		####node consistency
		#must be in the domain, since it should be consistent already
		if val not in self._domain:
			return False

		#must not be an explicit 'ne' relation
		for v in [v for r,v in self._relations if str(r) == 'ne']:
			if v.assigned() == val:
				return False
				
		return True
		####arc consistency
		#for rel, var in [ r,v for r,v in self._relations.iteritems() if not (type(v) == Value) ]:



	# val is related to self
	#
	# val rel self
	def is_consistent(self, rel, val):
		for r, v in self._relations:
			if v == val:
				if rel == 'eq':
					if r != 'eq':
						return False
					else:
						continue
				
				if rel == 'lt':
					if r != 'gt':
						return False
					else:
						continue

				if rel == 'gt':
					if r != 'lt':
						return False
					else:
						continue

				if rel == 'ne':
					if r == 'eq':
						return False
					else:
						continue

	def long_repr(self):
		slf = super(Variable,self).__str__()
		return "[(%s), %s] = %s" % (slf, (', '.join('%s %s %s' % (slf, rel, val) for rel, val in self._relations)), str(self._assigned_val) or str(None))



class Relation(str):
	def __init__(self, rel):
		if rel not in ['eq','ne','lt','gt']:
			raise AttributeError('Relation cannot be %s' % rel)
		super(Relation, self).__init__(rel)

	def inverse(self):
		if self == 'eq':
			return Relation('eq')

		if self == 'ne':
			return Relation('ne')

		if self == 'lt':
			return Relation('gt')

		if self == 'gt':
			return Relation('lt')

		raise AttributeError('Relation was %s' % self)

	@staticmethod
	def assignment_consistent(x, rel, y):
		if rel == 'ne':
			return not (x == y)
		if rel == 'eq':
			return x == y
		if rel == 'lt':
			return x < y
		if rel == 'gt':
			return x > y

	@staticmethod
	def can_satisfy(vI, rels, vJ):
		for r in rels:
			if Relation.assignment_consistent(vI, r, vJ):
				return True
		return False


class CSP_solver:

	@staticmethod
	def Backtracking_Search(csp):
		print "Backtracking_Search", csp.variables
		def Backtrack(assignment, csp):
			#if set(assignment.keys()).difference(set(csp.variables)) == 0:
			if len(csp.variables) == 0:
				return assignment

			var = csp.MRV()
			print "Backtrack MRV", var
			q = csp.LCV(var, assignment)
			while not q.empty():
				val = q.get()
				#move this into LCV
				while val in assignment.values():
					print "skipping",str(val)
					val = q.get()
				if not (val in assignment.values()):
					print "Assigning %d to %s" % (val, var)
					var._assigned_val = val
					assignment[str(var)] = var
					inference = CSP_solver.AC3(csp)
					if inference:
						for k,v in csp.variables.iteritems():
							if len(v._domain) == 1:
								v._assigned_val = v._domain[0]
								assignment[k] = v
						result = Backtrack(assignment, csp)
						if result is not None:
							return result

				variables[str(var)] = assignment.pop(var) 
				var._assigned_val = None
				print "put %s back" % var

		return Backtrack({}, csp)

	@staticmethod
	def AC3(csp):
		def revise(varI, varJ):
			print "varI,varJ", varI, varJ
			relations = varI.get_relations_to(varJ)
			print "%s relations to %s: %s" % ( str(varI), str(varJ), str(relations))
			revised = False
			for x in varI._domain:
				must_pop = True
				for y in varJ._domain:
					if Relation.can_satisfy(x, relations, y):
						must_pop = False
						break
				if must_pop:
					varI._domain.remove(x)
					revised = True
			return revised

		q = Queue()
		for var in csp.variables.values():
			for rel, val in var._relations:
				tup = var, val
				q.put(tup)

		while not q.empty():
			varI, varJ = q.get()
			if revise(varI, varJ):
				if len(varI._domain) == 0: return False
				for varK in set([ v[1] for v in varI._relations ]).difference(set([varJ])):
					tup = varK, varI
					q.put(tup)
		return True

class CSP(object):
	def __init__(self, _vars):
		self.variables = _vars

	def __str__(self):
		return str(self.variables) + "hahaha"

	def __repr__(self):
		return repr(self.variables) + 'haha'

	# returns the MRV
	def MRV(self):
		# dummy value
		var, val = None, Value(0)
		for vr, vl in self.variables.iteritems():
			(var, val) = (vr, vl) if (len(vl._relations) >= len(val._relations) or vl.assigned() is not None) else (var, val)
		return self.variables.pop(str(var))

	def LCV(self, var, assigned):
		pq = PriorityQueue()
		print "var, var._domain", var, var._domain
		for d in var._domain:
			if d in assigned.values():
				continue
			count = 0
			for r, v in var._relations:
				count += v.count_to_be_removed_if_assignment(var, d)
			print "putting d, count", d, count
			pq.put(d, count)
		return pq

if __name__ == '__main__':
	start = time.time()
	with open(sys.argv[1], 'r') as f:
		try:
			while True:
				var, rel, val = f.readline().strip('\n').split(' ')
				var = Variable(var)
				rel = Relation(rel)
				try:
					val = Variable(val)
					if not (val in variables.keys()):
						D += 1
						variables[str(val)] = val
				except AttributeError:
					try: 
						ival = int(val)
					except:
						pass
					else:
						val = Value(ival)
				finally:
					if not (var in variables.keys()):
						D += 1
						var.add_relation(rel, val)
						print "initializing key %s with value %s" %( str(var), var.long_repr() )
						variables[str(var)] = var
					else:
						variables[str(var)].add_relation(rel, val)
		except ValueError as e: 
			print e

	if not (V == D):
		print "V: %d" % V
		print "D: %d" % D

	assert (V == D or V == 0)
	for var in variables.values():
		print "%s relations: %s current_value = %s" % (var, ', '.join( "(%s->%s)" % (rel, val) for rel, val in var._relations), str(var._assigned_val)), "domain:", var._domain

	csp = CSP(variables)
	solution = CSP_solver.Backtracking_Search(csp)
	print "CSP_solver.Backtracking_Search(csp)", solution
	for k,v in solution.iteritems():
		print "%s:%d" % (k, v.assigned())

	print "time to run:", time.time() - start




