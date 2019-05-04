#! /usr/bin/env python

import sys
#from pyfirmata import Arduino, util
from gpiozero import LED
from gpiozero.pins.pigpio import PiGPIOFactory
from signal import pause
from time import sleep

class Controller:
    def __init__(self, board):
        #self.board = Arduino('/dev/{}'.format(board))
        factory = PiGPIOFactory(host='otc-alarm.local')
        self.alarm = LED(6, pin_factory=factory)
    
    def trigger(self, pin, delay):
       self.alarm.on()
       sleep(delay)
       self.alarm.off()

    def test(self):
        n = 0
        led = LED(17)
        while n < 3:
        #    self.board.digital[13].write(1)
        #    print('ON')
        #    sleep(1)
        #    self.board.digital[13].write(0)
        #    print('OFF')
            for i in range(4,8):
                print('Pin {}'.format(i))
                #self.board.digital[i].write(1)
                led.on
                print('ON')
                sleep(1)
                #self.board.digital[i].write(0)
                led.off
                print('OFF')
            n += 1


if __name__ == '__main__':
    board = sys.argv[1]
    c=Controller(board)
    c.test()
