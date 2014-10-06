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
		return self.deck.pop(0)

	#add this to hand
	def deal_many(self, count):
		if count == 0:
			raise RuntimeError("count is 0!")

		dealt = []

		if not len(self.deck):
			return None

		try:
			for x in range(count):
				dealt.append(self.deal_one())
		except IndexError:
			pass
		except TypeError:
			pass
		finally:
			return dealt
		
	def count(self):
		return self.deck.count()

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
		self.last_player = 0

	def ready(self):
		self.deck.shuffle()
		for x in range(8):
			self.my_hand.append(self.deck.deal_one())
			self.their_hand.append(self.deck.deal_one())
		self.current_face_up = self.deck.deal_one()
		initial = (None, self.current_face_val(), self.current_face_suit(), 0)
		self.history.append(initial)

		print self.me,str(self.my_hand)
		print (self.me + 1) % 2,str(self.their_hand)

	def game_over(self):
		return self._game_over

	def max_depth(self):
		return min(self.depth, len(self.my_hand) + len(self.their_hand))

	############## Start: New Methods
	def current_face_val(self):
		return CARD_VAL(self.current_face_up)

	def current_face_suit(self):
		return self.declared_suit if self.declared_suit is not None else CARD_SUIT(self.current_face_up)

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

	def hand_can_play_current(self, hand, current=None,suit=None):
		c = current is not None
		s = suit is not None

		if c:
			temp = self.current_face_up
			self.current_face_up = current
			current = temp

		if s:
			temp = self.declared_suit
			self.declared_suit = suit
			suit = temp

		result = self.hand_has_val(hand, None if self.declared_suit else self.current_face_val()) or \
				 self.hand_has_suit(hand, self.declared_suit or self.current_face_suit())
		
		if c:
			temp = self.current_face_up
			self.current_face_up = current
			current = temp

		if s:
			temp = self.declared_suit
			self.declared_suit = suit
			suit = temp

		return result

	def can_play_card(self,card,current=None, suit=None):
		c = current is not None
		s = suit is not None

		if c:
			temp = self.current_face_up
			self.current_face_up = current
			current = temp

		if s:
			temp = self.declared_suit
			self.declared_suit = suit
			suit = temp

		result = CARD_SUIT(card) == (self.current_face_suit()) or \
			CARD_VAL(card) ==  self.current_face_val()

		if c:
			temp = self.current_face_up
			self.current_face_up = current
			current = temp

		if s:
			temp = self.declared_suit
			self.declared_suit = suit
			suit = temp

		return result

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
		for x in range(self.deck.count()):
			if self.can_play_card(self.deck.deck[x]):
				return x
		return None

	def playable_cards(self, hand, face_up_card, suit=None):
		playables = []
		for c in hand:
			if self.can_play_card(c,current=face_up_card,suit=suit):
				playables.append(c)

		return playables

	############## End: New Methods

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

	def pick_up_cards(self, count):
		hand = self.get_current_hand()
		add = self.deck.deal_many(count)
		for c in add:
			print "%d picked up %d (%d,%d): " %(self.turn,c,CARD_VAL(c),CARD_SUIT(c))
		hand += add

	def must_pick_up(self, turn):
		hand = self.get_current_hand()

		if self.card_is_queen_of_spades(self.current_face_up) and not (turn == self.last_player):
			return True, 5

		elif self.card_is_two(self.current_face_up) and not self.turn_is(self.last_player):
			if not self.hand_has_val(hand,1):
				return True, self.twos
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
		if self.card_is_jack(self.current_face_up) and not (turn == self.last_player):
			return False, None

		must, count = self.must_pick_up(turn)
		print turn,"must pick up:",must
		if must:
			return False, count
		else:
			return True, None


	def next(self):
		can_play, pick_up_count = self.can_play(self.turn)
		print self.turn,"can't play",not can_play,", must pick up",pick_up_count

		card_val, card_suit = 0, 0

		if can_play:
			#if it's my turn, pick a move and do it
			if self.turn_is(self.me):
				my_move = self.pick_move()
				card_val, card_suit = self.do_move(my_move,self.my_hand)
			#otherwise, ask them
			else:
				their_move = self.get_their_move()
				card_val, card_suit = self.do_move(their_move, self.their_hand)

		else:
			self.declared_suit = None
			#only jacks should produce this...
			if pick_up_count is None:
				#self.last_player = self.turn
				self.turn = (self.turn + 1) % 2
				return None
			#just couldn't play a card so loop until you find one
			elif pick_up_count == 1:
				self.pick_up_cards(1)
				while not self.can_play(self.turn)[0]:
					self.pick_up_cards(1)
					pick_up_count += 1
					#if it's my turn, pick a move and do it
				print "%d,%s" % (self.turn, str(self.get_current_hand()))
				if self.turn_is(self.me):
					my_move = self.pick_move()
					card_val, card_suit = self.do_move(my_move,self.my_hand)
				#otherwise, ask them
				else:
					their_move = self.get_their_move()
					card_val, card_suit = self.do_move(their_move, self.their_hand)

			#otherwise you pick up many and lose your turn 
			else:
				self.pick_up_cards(pick_up_count)
				if pick_up_count % 2 == 0:
					self.twos = 0
					player = self.turn
					self.turn = (self.turn + 1) % 2
					return (player, 0, 0, pick_up_count)

		self.last_player = self.turn
		self.turn = (self.turn + 1) % 2
		return (self.last_player, card_val, card_suit, pick_up_count or 0)


	def do_move(self, card_idx, hand):
		self.current_face_up = hand.pop(card_idx)

		#change suit if necessary
		if self.card_is_eight(self.current_face_up):
			self.get_suit_declaration()
		if self.card_is_two(self.current_face_up):
			self.twos += 2

		return self.current_face_val(), self.current_face_suit()

	def pick_move(self):
		print "picking move"
		
		partial_state = (self.current_face_up, self.current_face_suit(), self.my_hand, self.history)
		return self.move(partial_state)

		playable = lambda x : None
		if self.card_is_two(self.current_face_up) and self.turn_is(self.turn):
			playable = self.card_is_two
		else:
			playable = self.can_play_card

		for x in range(len(self.my_hand)):
			if playable(self.my_hand[x]):
				return x
		return None

	#state = (deck, other_hand, (face_up_card, suit, player_hand, history))
	def move(self, (face_up_card, suit, myhand, history)):
		cards_left = list( set([x for x in range(52)]).difference(set(myhand).union(set([ ((f+1)*(s+1) - 1) for p,f,s,c in history])) ))
		outcomes = {}
		for x in range(100):
			idx = random.randint(0,len(myhand)-1)
			theirhand = []
			for x in range(len(self.their_hand)):
				if len(cards_left):
					theirhand.append(cards_left.pop(0 if len(cards_left) == 1 else random.randint(0,len(cards_left)-1)))
			state = (cards_left, theirhand,(face_up_card, suit, myhand, history))
			value = self.movePerfectKnowledge(state)
			outcomes[idx] = outcomes[idx] + value if idx in outcomes else value

		k,v = 0,0
		for key, val in outcomes.iteritems():
			if val > v:
				k = key

		return k

	def movePerfectKnowledge(self, (deck, theirhand, (face_up_card, suit, myhand, history))):
		puc = 0 #number of cards to pick up...
		while not self.hand_can_play_current(myhand,current=face_up_card, suit=suit):
			puc += 1
			myhand.append(deck.pop(0))
		
		value = self.alpha_beta(deck, theirhand, face_up_card, suit, myhand, -(float('inf')),(float('inf')),True,self.max_depth())

		return value

	def alpha_beta(self, deck, my_hand, face_up_card, suit, their_hand, a, b, _max,depth ):
		if depth == 0 \
			or ( len(my_hand if _max else their_hand) == 0 and len(deck) == 0 ):
			#print "!!returning!!"
			return sum([CARD_VAL(x) for x in their_hand]) - sum([CARD_VAL(x) for x in my_hand])
		
		if _max:
			try:
				while not self.hand_can_play_current(my_hand,current=face_up_card, suit=suit):
					my_hand.append(deck.pop(0))
			except IndexError:
				return sum([CARD_VAL(x) for x in my_hand])

			for card in self.playable_cards(my_hand,face_up_card,suit):
				myhand=list(my_hand)
				myhand.remove(card)
				a = max(a, self.alpha_beta(deck, their_hand,card, suit, myhand, a, b, False, depth-1))
				if b <= a:
					break
			return a

		else:
			try:
				while not self.hand_can_play_current(their_hand,current=face_up_card, suit=suit):
					their_hand.append(deck.pop(0))
			except IndexError:
				return sum([CARD_VAL(x) for x in their_hand])

			for card in self.playable_cards(their_hand,face_up_card,suit):
				theirhand=list(their_hand)
				theirhand.remove(card)
				b = min(b, self.alpha_beta(deck, theirhand,card, suit, my_hand, a, b, True, depth-1))
				if b <= a:
					break
				return b

	def win(self):
		if len(self.my_hand):# + len(self.deck) == 0:
			return True
		return False

	def lose(self):
		if len(self.their_hand):# + len(self.deck) == 0:
			return True
		return False

if __name__ == '__main__':
	print Deck().deck