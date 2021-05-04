#micro:bit code for the AccelerEQ system - click Flash after connecting the micro:bit via USB

from microbit import *
import math #imports the microbit math module from the native library

#function definitions
def midiControlChange(chan, n, value): #defines the midi control change message
    MIDI_CC = 0xB0
    if chan > 15: #if statements check for values outside of the scope of the MIDI standard
        return #return ends the function call and returns the value outside of scope
    if n > 127:
        return
    if value > 127:
        return
    msg = bytes([MIDI_CC | chan, n, value]) #sets the format of the MIDI message
    uart.write(msg) #message is sent via UART whenever midiControlChange is called

#defines Start() which initiates the UART in order to transfer MIDI messages. Start() is called on the next line.
def Start():
    uart.init(baudrate=31250, bits=8, parity=None, stop=1, tx=pin0)
Start()

#defines variables which store the last registered state of a control. These are updated after each midiControlChange call.
lastA = False
lastB = False
lastC = False
lastPot = 0
lastx = 0
lasty = 0
lastz = 0

while True: #always runs and checks the conditional statements below

    # Variable definitions for each component/parameter - buttons return 0 or 1 depending on if they are pressed or not.
    # The potentiometer and accelerometer return analog data. Potentiometer returns numbers from 0 to 1023, while the accelerometer
    # returns numbers from -1024 to +1024 for the xyz axes when static, but can reach values up to +-2048 when shaken.
    a = button_a.is_pressed()
    b = button_b.is_pressed()
    c = pin2.is_touched()
    pot = pin1.read_analog()
    x = accelerometer.get_x()
    y = accelerometer.get_y()
    z = accelerometer.get_z()

    # Button behaviour definitions:
    # Send a 1 if respective button is pressed, and a 0 if it isn't.
    # This is done by comparing the current state of the button to its previous checked state.
    # MIDI CC#: A - 20, B - 21, C - 22
    if a is True and lastA is False:
        midiControlChange(0, 20, 1)
    elif a is False and lastA is True:
        midiControlChange(0, 20, 0)
    lastA = a

    if b is True and lastB is False:
        midiControlChange(0, 21, 1)
    elif b is False and lastB is True:
        midiControlChange(0, 21, 0)
    lastB = b

    if c is True and lastC is False:
        midiControlChange(0, 22, 1)
    elif c is False and lastC is True:
        midiControlChange(0, 22, 0)
    lastC = c

    # Potentiometer behaviour definitions:
    # Pot value is checked against last registered value (and the last value is updated after), with the
    # if statement running only if the two values are not equal.
    # The pot value is scaled from 0 to 1023 to 0 to 127 so that it can be sent as a MIDI CC message.
    # To ensure that the final value is an integer, the result is floored.
    # MIDI CC#: 23
    if pot != lastPot:
        potValue = math.floor(pot / 1024 * 127)
        midiControlChange(0, 23, potValue)
    lastPot = pot

    # Accelerometer behaviour definitions:
    # Same principle as previous two controls.
    # Value is scaled from -2048 to 2048 to 0 to 127.
    # First, the +1024 is added to account for movement.
    # The modulus of the result is taken to get a positive number using math.fabs, and the final result is floored.
    # MIDI CC#: x - 24, y - 25, z - 26(not used)
    if x != lastx:
        mod_x = math.floor(math.fabs(((x + 1024) / 2048 * 127)))
        midiControlChange(0, 24, mod_x)
        lastx = x
    if y != lasty:
        mod_y = math.floor(math.fabs(((y +  1024) / 2048 * 127)))
        midiControlChange(0, 25, mod_y)
        lasty = y
    if z != lastz:
        mod_z = math.floor(math.fabs(((z + 1024) / 2048 * 127)))
        midiControlChange(0, 26, mod_z)
        lastz = z
    sleep(10) # causes the microbit to sleep for 10 milliseconds and loop through the 'while' statement on wake