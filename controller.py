#! /usr/bin/env python

import sys
from pyfirmata import Arduino, util
from time import sleep

class Controller:
    def __init__(self, board):
        self.board = Arduino('/dev/{}'.format(board))
    
    def trigger(self, pin, delay):
       self.board.digital[pin].write(1) 
       sleep(delay)
       self.board.digital[pin].write(0) 

    def test(self):
        n = 0
        while n < 3:
            self.board.digital[13].write(1)
            print('ON')
            sleep(1)
            self.board.digital[13].write(0)
            print('OFF')
            n+= 1


if __name__ == "__main__":
    board = sys.argv[1]
    c=Controller(board)
    c.test()