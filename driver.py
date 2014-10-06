from crazy_eights import *

if __name__ == '__main__':
	fs = 2
	while not (fs in range(2)):
		try:
			fs = int(input("Enter 0 to go first, 1 to go second: "))
		except:
			pass
	
	deck = Deck()
	eights = CrazyEight(deck, 10, (fs + 1) % 2)
	eights.ready()

	def play(CE):
		count = 1
		while not CE._game_over:
			print "------------------------------------------------"
			print "history:\t",CE.history
			print "Faceup card:\t||%d||" % CE.current_face_up,"(%d,%d)" % (CE.current_face_val(),CARD_SUIT(CE.current_face_up))
			print "%d:\t\t"%CE.me,CE.my_hand
			print "\t\t",str([(x%13,int(math.floor(x/13))) for x in CE.my_hand])
			print "%d:\t\t" % ((CE.me + 1) % 2),CE.their_hand
			print "\t\t",str([(x%13,int(math.floor(x/13))) for x in CE.their_hand])
			move = CE.next()
			if not (move is None):
				print "move #%d: %s" %(count, str(move))
				CE.history.append(move)
				count += 1

		winner, loser = None, None
		if CE.win():
			winner, loser = "I", "You"
		elif CE.lose():
			winner, loser = "You", "I"
		else:
			raise Exception("Game over and nobody won!")

		print "%s win! %s lose! %s get %d points! Write it down!" % (winner, loser, winner, sum(CE.their_hand))

	play(eights)