'''
@author			jaronhalt
@sjsuid			007939971
@descrption		hw2 cs156

1. pick a starting spot A in n-dimensions with n degrees of freedom:
	T(1) = the first step,...,T(i) = the ith step
	
	scenario a (hill w/ restart): T(1) is chosen from the successors of A 
		coming to A', with DeltaE(T(1)) < 0. The euclidean distance (minimum distance given complete relaxation) 
		to the goal E of A' is "E(A')_a1". Restart. E(A')_a2 is the result of the second T(1).

	scenario b (beam w/ 2 states): E(A')_b1, E(A')_b2 are the choices from T(1).

	conclusion: Totalling two successors from scenario a and two from scenario b, we have chosen 
		4 random successors. In scenario a, we have no choice on either E(A'). In scenario b, we chose the best. 
		E(A')_b1 != E(A')_b2 (is not the same element of the state space, but they could be equivalent); 
		E(A')_a1 == E(A')_a2 is possible. Therefore, even if E(A')_a1 == E(A')_b1, then only E(A')_b2 need be less 
		than E(A')_a1 (and equivalently E(A')_a2). 

2. If a queen is "stuck", meaning it can't pass a certain tile because there's always another queen
	attacking passing the threshold for the heuristic in every attemp to pass, then allowing MORE 
	queens to attack than the current threshold would render the queen "unstuck".

'''

#3.

# state = (deck, their_hand, partial_state)
# partial_state = (face_up_card, suit, my_hand, history)
# move = (player_num, face_up_card, suit, number_of_cards)

import random, math

class Deck(object):
	def __init__(self):
		self.deck = [x for x in range(52)]
		self.shuffle()

	def shuffle(self):
		self.deck = [0 for x in range(52)]
		for x in range(52):
			i = random.randint(0,51)
			while not (self.deck[i] is 0):
				i = (i+1) % 52
			self.deck[i] = x

	#add this to hand
	def deal_one(self):
		try:
			return [self.deck.pop(0)]
		except IndexError:
			return None

	#add this to hand
	def deal_many(self, count):
		if count == 0:
			raise RuntimeError("count is 0!")

		dealt = []

		if not self.deck.size():
			return None

		try:
			for x in range(count):
				dealt += self.deal_one()
		except IndexError:
			pass
		except TypeError:
			pass
		finally:
			return dealt
		
	def size(self):
		return self.deck.size()

def CARD_VAL(c):
	return c % 13

def CARD_SUIT(c):
	return int(math.floor(c / 13))

class CrazyEight(object):
	
	@staticmethod
	def MOVE(player_num, face_up_card, suit, number_of_cards):
		return (player_num, face_up_card, suit, number_of_cards)

	def __init__(self, deck, trials, me):
		self.deck = deck
		self.pile = []
		self.my_hand = []
		self.their_hand = []
		self.history = []
		self.current_face_up = None
		self.declared_suit = None
		self.trials = trials
		self.stats = {}
		self.depth = 16
		self.me = me
		self.them = (self.me + 1) % 2
		self._game_over = False
		self.turn = 0
		self.twos = 0
		self.last_player = None

	def ready(self):
		self.deck.shuffle()
		for x in range(8):
			self.my_hand += self.deck.deal_one()
			self.their_hand += self.deck.deal_one()
		self.current_face_up = self.deck.deal_one()
		
		print "My hand",str(self.my_hand)
		print "Their hand",str(self.their_hand)
		print "Me:",self.me

	def game_over(self):
		return self._game_over

	def max_depth(self):
		return min(self.depth, len(self.my_hand) + len(self.their_hand))

	############## Start: New Methods
	def current_face_val(self):
		return CARD_VAL(self.current_face_up)

	def current_face_suit(self):
		return CARD_SUIT(self.current_face_up)

	def card_is_jack(self, card):
		return CARD_VAL(card) == 10

	def card_is_queen_of_spades(self, card):
		return CARD_VAL(card) == 11 and CARD_SUIT(card) == 0

	def card_is_two(self, card):
		return CARD_VAL(card) == 1

	def card_is_eight(self, card):
		return CARD_VAL(card) == 7

	def hand_has_suit(self, hand, suit):
		return suit in [CARD_SUIT(x) for x in hand]

	def hand_has_val(self, hand, val):
		return val in [CARD_VAL(x) for x in hand]

	def hand_can_play_current(self, hand):
		return 	self.hand_has_val(hand, None if ( self.card_is_eight(self.current_face_up) and not self.turn_is(self.last_player) ) else self.current_face_val()) or \
				self.hand_has_suit(hand, CARD_SUIT(self.declared_suit or self.current_face_up))

	def can_play_card(self,card):
		return CARD_SUIT(card) == self.current_face_suit() or CARD_VAL(card) == self.current_face_val()

	def turn_is(self, t):
		return t == self.turn

	def get_current_hand(self):
		return self.my_hand if self.turn_is(self.me) else self.their_hand

	def get_suit_declaration(self):
		if self.turn_is(self.me):
			self.declared_suit = self.pick_suit()
		else:
			self.declared_suit = self.prompt_for_suit()

		print "SUIT DECLARED",self.declared_suit

	def depth_of_next_playable(self):
		for x in range(self.deck.size()):
			if self.can_play_card(self.deck.deck[x]):
				return x
		return None

	############## End: New Methods

	def must_pick_up(self, turn):
		hand = self.get_current_hand()

		if self.card_is_jack(self.current_face_up) and not (turn == self.last_player):
			return False, None

		if self.card_is_queen_of_spades(self.current_face_up) and not (turn == self.last_player):
			return True, 5

		elif self.card_is_two(self.current_face_up) and not self.turn_is(self.last_player):
			if not self.hand_has_val(hand,1):
				ret = True, self.twos
				self.twos = 0
				return ret
			else:
				return False, None

		elif self.card_is_eight(self.current_face_up) and not self.turn_is(self.last_player):
			if self.hand_has_val(hand, 7) or self.hand_has_suit(hand, self.current_face_suit()):
				return False, None
			else:
				return True, 1

		else:
			if self.hand_has_val(hand, self.current_face_val()) or self.hand_has_suit(hand, self.declared_suit or self.current_face_suit()):
				return False, None
			else:
				return True, 1

		raise Exception("Didn't mean this...")


	def can_play(self, turn):
		must, count = self.must_pick_up(turn)
		print turn,"must pick up:",must
		if must:
			return False, count
		else:
			return True, None


	def next(self):
		print "current val:\t",self.current_face_val()
		print "current suit:\t", self.declared_suit or self.current_face_suit()

		if not self.hand_can_play_current(self.get_current_hand()):


		can_play, pick_up_count = self.can_play(self.turn)

		card_val, card_suit = 0, 0

		if not can_play:
			print self.turn,"can't play",not can_play,", must pick up",pick_up_count
			if pick_up_count is None:
				#only jacks should produce this...
				self.last_player = self.turn
				self.turn = (self.turn + 1) % 2
				return None
			#just couldn't play a card so loop until you find one
			elif pick_up_count == 1:
				self.pick_up_cards(1)
				while not self.can_play(player)[0]:
					self.pick_up_cards(1)
					pick_up_count += 1

			#otherwise you pick up many and lose your turn 
			else:
				self.pick_up_cards(pick_up_count)
				self.last_player = self.turn
				self.turn = (self.turn + 1) % 2
				return (player, card_val, card_suit, pick_up_count)

		else:
			player = self.turn

		#if it's my turn, pick a move and do it
		if self.turn_is(self.me):
			my_move = self.pick_move()
			card_val, card_suit = self.do_move(my_move,self.my_hand)
		#otherwise, ask them
		else:
			their_move = self.get_their_move()
			card_val, card_suit = self.do_move(their_move, self.their_hand)

		self.last_player = self.turn
		self.turn = (self.turn + 1) % 2
		return (player, card_val, card_suit, pick_up_count or 0)

	def pick_up_cards(self, count):
		hand = self.get_current_hand()
		add = self.deck.deal_many(count)
		for c in add:
			print "%d picked up %d (%d,%d): " %(self.turn,c,CARD_VAL(c),CARD_SUIT(c))
		hand += add

	def do_move(self, card_idx, hand):
		self.current_face_up = hand.pop(card_idx)

		#change suit if necessary
		self.declared_suit = self.get_suit_declaration() if self.card_is_eight(self.current_face_up) else None

		if self.card_is_two(self.current_face_up):
			self.twos += 2

		return self.current_face_val(), self.current_face_suit()

	def pick_move(self):
		#print "picking move"
		card_val, card_suit = 52, 52
		while not(card_val == self.current_face_val()) and not(card_suit == self.current_face_suit()):
			idx = random.randint(0,len(self.my_hand)-1)
			card_val = self.my_hand[idx] % 13
			card_suit = int(math.floor(self.my_hand[idx]/13))
		return idx


	def pick_suit(self):
		return random.randint(0,3)

	def prompt_for_suit(self):
		s = 4
		while s not in range(4):
			s = input("Pick a new suit (0:spades, 1:hearts, 2:diamonds, 3:clubs): ")
		return s

	def card_match(self,card):
		return card % 13 == self.current_face_val() or int(math.floor(card/13)) == self.current_face_suit()

	def get_their_move(self):
		idx = len(self.their_hand)
		
		while idx >= len(self.their_hand):
			try:
				idx = input("Enter the index of the card you wish to play (ctrl-c to exit): ")
				idx = int(idx)

			except KeyboardInterrupt:
				print '\n'
				exit(1)
			except:
				pass
			else:
				if idx < len(self.their_hand):
					if not ( self.card_match(self.their_hand[idx]) ):
						print "Card is not a valid move"
						idx = 52

		print "they picked",idx
		return idx

	def move(self, (face_up_card, suit, my_hand, history)):
		for x in range(self.trials):
			m = movePerfectKnowledge(self.deck, self.their_hand, (face_up_card, suit, self.my_hand, self.history), self.max_depth(), True)
			self.stats[m] = self.stats[m] + 1 if m in self.stats.keys() else 0

		m = self.stats.keys()[0]
		for k in self.stats:
			if self.stats[k] > self.stats[m]:
				m = k

		return self.stats[m]

	def movePerfectKnowledge(self, (deck, their_hand, partial_state)):
		if self.win():
			self._game_over = True
			return (self.me,0,0,0)

		if self.lose():
			self._game_over = True
			return (self.them,0,0,0)

		outcomes = []
		hand = partial_state[2]
		for x in range(hand):
			outcomes.push(self.mini_max(list(hand), list(their_hand), deck, self.max_depth(), True))


	def win(self):
		if len(self.my_hand):# + len(self.deck) == 0:
			return True
		return False

	def lose(self):
		if len(self.their_hand):# + len(self.deck) == 0:
			return True
		return False

# state = (deck, their_hand, partial_state)
# partial_state = (face_up_card, suit, my_hand, history)
# move = (player_num, face_up_card, suit, number_of_cards)

	def mini_max(self, myhand, their_hand, deck, depth, _max):

		if depth == 0 or (len(myhand) == 0 and _max) or (len(their_hand) == 0 and not _max):
			if _max:
				return sum(myhand)
			else:
				return sum(state(1))

		def max_value(best, val):
			# here '<=' v. '<' matters
			#if sum(best) <= sum(val):
			if best <= val:
				return val
			return best

		def min_value(best, val):
			# here '>=' v. '>' matters
			#if sum(best) >= sum(val):
			if best >= val:
				return val
			return best

		if _max:
			#best = [-float('inf')]
			best = -float('inf')
			for x in myhand:
				temp_hand = list(myhand).remove(x)
				val = self.mini_max(temp_hand, their_hand, depth-1, not _max)
				best = max_value(best, val)
			return best
		else:
			#best = [float('inf')]
			best = float('inf')
			for x in their_hand:
				temp_hand = list(their_hand).remove(x)
				val = self.mini_max(myhand, temp_hand, state, depth-1, not _max)
				best = min_value(best, val)

	def play(self):
		count = 1
		while not self._game_over:
			print "------------------------------------------------"
			print "Faceup card:\t||%d||" % self.current_face_up,"(%d,%d)" % (self.current_face_val(),self.current_face_suit())
			print "my_hand:\t",self.my_hand
			print "\t\t",str([(x%13,int(math.floor(x/13))) for x in self.my_hand])
			print "their_hand:\t",self.their_hand
			print "\t\t",str([(x%13,int(math.floor(x/13))) for x in self.their_hand])
			move = self.next()
			if not (move is None):
				print "move #%d: %s" %(count, str(move))
				self.history.append(move)
				count += 1

		winner, loser = None, None
		if self.win():
			winner, loser = "I", "You"
		elif self.lose():
			winner, loser = "You", "I"
		else:
			raise Exception("Game over and nobody won!")

		print "%s win! %s lose! %s get %d points! Write it down!" % (winner, loser, winner, sum(self.their_hand))

if __name__ == '__main__':
	print Deck().deck