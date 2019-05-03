#!/usr/bin env python

import sys
from controller import Controller
from flask import (
    Flask,
    render_template
)


# Create the application instance
app = Flask(__name__, template_folder="templates")

# Create a URL route in our application for "/trigger"
@app.route('/trigger')
def trigger():
    controller.trigger(2, 3)
    return 'OK'

# If we're running in stand alone mode, run the application
if __name__ == '__main__':
    #board = 'tty.usbserial-A4001JNj'
    board = sys.argv[1]
    controller = Controller(board)
    app.run(debug=True)