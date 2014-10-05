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
	eights.play()