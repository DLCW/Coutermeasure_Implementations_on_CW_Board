from subprocess import call
import chipwhisperer.capture.ChipWhispererCapture as cwc

import sys
import time
from Crypto.Cipher import AES
import csv
import binascii
import random
import numpy
try:
    from PySide.QtCore import *
    from PySide.QtGui import *
except ImportError:
    print "ERROR: PySide is required for this program"
    sys.exit()

def hexStrToByteArray(hexStr):
    ba = bytearray()
    for s in hexStr.split():
        ba.append(int(s, 16))
    return ba
	
def pe():
    QCoreApplication.processEvents()

def resetAVR():
    call(["C:\\Program Files (x86)\\Atmel\\AVR Tools\\STK500\\Stk500.exe",
          "-dATMega328p", "-s", "-cUSB"])


AES_INV_SBOX = [0x52, 0x9 , 0x6a, 0xd5, 0x30, 0x36, 0xa5, 0x38, 0xbf, 0x40, 0xa3, 0x9e, 0x81, 0xf3, 0xd7, 0xfb,
                0x7c, 0xe3, 0x39, 0x82, 0x9b, 0x2f, 0xff, 0x87, 0x34, 0x8e, 0x43, 0x44, 0xc4, 0xde, 0xe9, 0xcb,
                0x54, 0x7b, 0x94, 0x32, 0xa6, 0xc2, 0x23, 0x3d, 0xee, 0x4c, 0x95, 0xb , 0x42, 0xfa, 0xc3, 0x4e,
                0x8 , 0x2e, 0xa1, 0x66, 0x28, 0xd9, 0x24, 0xb2, 0x76, 0x5b, 0xa2, 0x49, 0x6d, 0x8b, 0xd1, 0x25,
                0x72, 0xf8, 0xf6, 0x64, 0x86, 0x68, 0x98, 0x16, 0xd4, 0xa4, 0x5c, 0xcc, 0x5d, 0x65, 0xb6, 0x92,
                0x6c, 0x70, 0x48, 0x50, 0xfd, 0xed, 0xb9, 0xda, 0x5e, 0x15, 0x46, 0x57, 0xa7, 0x8d, 0x9d, 0x84,
                0x90, 0xd8, 0xab, 0x0 , 0x8c, 0xbc, 0xd3, 0xa , 0xf7, 0xe4, 0x58, 0x5 , 0xb8, 0xb3, 0x45, 0x6 ,
                0xd0, 0x2c, 0x1e, 0x8f, 0xca, 0x3f, 0xf , 0x2 , 0xc1, 0xaf, 0xbd, 0x3 , 0x1 , 0x13, 0x8a, 0x6b,
                0x3a, 0x91, 0x11, 0x41, 0x4f, 0x67, 0xdc, 0xea, 0x97, 0xf2, 0xcf, 0xce, 0xf0, 0xb4, 0xe6, 0x73,
                0x96, 0xac, 0x74, 0x22, 0xe7, 0xad, 0x35, 0x85, 0xe2, 0xf9, 0x37, 0xe8, 0x1c, 0x75, 0xdf, 0x6e,
                0x47, 0xf1, 0x1a, 0x71, 0x1d, 0x29, 0xc5, 0x89, 0x6f, 0xb7, 0x62, 0xe , 0xaa, 0x18, 0xbe, 0x1b,
                0xfc, 0x56, 0x3e, 0x4b, 0xc6, 0xd2, 0x79, 0x20, 0x9a, 0xdb, 0xc0, 0xfe, 0x78, 0xcd, 0x5a, 0xf4,
                0x1f, 0xdd, 0xa8, 0x33, 0x88, 0x7 , 0xc7, 0x31, 0xb1, 0x12, 0x10, 0x59, 0x27, 0x80, 0xec, 0x5f,
                0x60, 0x51, 0x7f, 0xa9, 0x19, 0xb5, 0x4a, 0xd , 0x2d, 0xe5, 0x7a, 0x9f, 0x93, 0xc9, 0x9c, 0xef,
                0xa0, 0xe0, 0x3b, 0x4d, 0xae, 0x2a, 0xf5, 0xb0, 0xc8, 0xeb, 0xbb, 0x3c, 0x83, 0x53, 0x99, 0x61,
                0x17, 0x2b, 0x4 , 0x7e, 0xba, 0x77, 0xd6, 0x26, 0xe1, 0x69, 0x14, 0x63, 0x55, 0x21, 0xc , 0x7d]
                
#Make the application
app = cwc.makeApplication()

#If you DO NOT want to overwrite/use settings from the GUI version including
#the recent files list, uncomment the following:
#app.setApplicationName("Capture V2 Scripted")

#Get main module
cap = cwc.ChipWhispererCapture()

#Show window - even if not used
cap.show()

#NB: Must call processEvents since we aren't using proper event loop
pe()

cap.setParameter(['Generic Settings', 'Scope Module', 'ChipWhisperer/OpenADC'])
cap.setParameter(['Generic Settings', 'Target Module', 'Simple Serial'])
cap.setParameter(['Generic Settings', 'Trace Format', 'ChipWhisperer/Native'])
cap.setParameter(['OpenADC Interface', 'connection', 'ChipWhisperer Lite'])
cap.setParameter(['Target Connection', 'connection', 'ChipWhisperer-Lite'])

#Load FW (must be configured in GUI first)
cap.FWLoaderGo()

#NOTE: You MUST add this call to pe() to process events. This is done automatically
#for setParameter() calls, but everything else REQUIRES this, since if you don't
#signals will NOT be processed correctly
pe()

#Connect to scope
cap.doConDisScope(True)
pe()

cmds = [  ['CW Extra', 'CW Extra Settings', 'Trigger Pins', 'Target IO4 (Trigger Line)', True],
      ['CW Extra', 'CW Extra Settings', 'Target IOn Pins', 'Target IO1', 'Serial RXD'],
      ['CW Extra', 'CW Extra Settings', 'Target IOn Pins', 'Target IO2', 'Serial TXD'],
	  ['OpenADC', 'Clock Setup', 'CLKGEN Settings', 'Desired Frequency', 7370000.0],
      ['CW Extra', 'CW Extra Settings', 'Target HS IO-Out', 'CLKGEN'],
      ['OpenADC', 'Clock Setup', 'ADC Clock', 'Source', 'CLKGEN x4 via DCM'],
	  ['OpenADC', 'Trigger Setup', 'Total Samples', 3000],
	  ['OpenADC', 'Trigger Setup', 'Offset', 0],
	  ['OpenADC', 'Gain Setting', 'Setting', 45],
	  ['OpenADC', 'Trigger Setup', 'Mode', 'rising edge'],
	  #Final step: make DCMs relock in case they are lost
	  ['OpenADC', 'Clock Setup', 'ADC Clock', 'Reset ADC DCM', None],
	]

for cmd in cmds: cap.setParameter(cmd)

#Connect to serial port
ser = cap.target.driver.ser
ser.con()

#Set baud rate
#cap.setParameter(['Serial Port Settings', 'TX Baud', 38400])
#cap.setParameter(['Serial Port Settings', 'RX Baud', 38400])

#Attach special method so we can call from GUI if wanted
cap.resetAVR = resetAVR

#Some useful commands to play with from GUI
#cap.resetAVR
#ser.write("x")
#ser.write("k00112233445566778899AABBCCDDEEFF\n")
#ser.write("pAABBCCDDEEFF00112233445566778899\n")
#print ser.read(255)

#Run Application
#app.exec_()

#cap.resetAVR()

# Create a pointer on a csv file

'''''''''''''''''''''''''''
Traces for Template building  
'''''''''''''''''''''''''''
nbSamples = 1900
trace = csv.writer(open("template_building.csv", "wb"))
plain = csv.writer(open("template_plain.csv", "wb"))
key = csv.writer(open("template_key.csv", "wb"))
myaes_input = bytearray(16)
myaes_key = bytearray(16)

nbtraces = 500
for k in range(16):
	myaes_key [k]   = random.randint(0, 255)
key.writerow(myaes_key)
for value in range (256):
	myaes_input [0]  = AES_INV_SBOX [value] ^ myaes_key[0]  
	myaes_input [15] = AES_INV_SBOX [value] ^ myaes_key[15]
	for j in range(nbtraces):
		for k in range(1,15):
			myaes_input [k] = random.randint(0, 255)
		time.sleep(0.1)
		ser.write("k" + binascii.hexlify(myaes_key) + "\n")
		time.sleep(0.1)
		cap.scope.arm()
		pe()
		ser.write("p" + binascii.hexlify(myaes_input) + "\n")
		if cap.scope.capture(update=True, NumberPoints=None, waitingCallback=pe):
			print "Timeout"
		else:
			print "Capture OK"
		
		print "p" + binascii.hexlify(myaes_input)
		print "k" + binascii.hexlify(myaes_key)
				

		respdata = ser.read()
		print respdata
		
		trace.writerow(cap.scope.datapoints[0:nbSamples])
		plain.writerow(myaes_input)
		print "capture template building trace number :" + str (value) + " : " + str (j)
		print  "\\\\\\\\\\\\\\\\\\"

'''''''''''''''''''''''''''
Traces for validation processing  
'''''''''''''''''''''''''''	
trace  = csv.writer(open("validation_processing.csv", "wb"))
plain  = csv.writer(open("validation_plain.csv", "wb"))
myaes_key   = hexStrToByteArray("38 11 22 33 44 55 66 77 88 99 AA BB CC DD EE FF")


nbtraces = 1000
for j in range(nbtraces):
	for i in range(16):
		myaes_input [i] = random.randint(0, 255)
	time.sleep(0.1)

	ser.write("k" + binascii.hexlify(myaes_key) + "\n")
	time.sleep(0.1)
	cap.scope.arm()
	pe()
	ser.write("p" + binascii.hexlify(myaes_input) + "\n")
	if cap.scope.capture(update=True, NumberPoints=None, waitingCallback=pe):
		print "Timeout"
	else:
		print "Capture OK"
	
	print "p" + binascii.hexlify(myaes_input)
	print "k" + binascii.hexlify(myaes_key)
	#Read response, which is 33 bytes long. Specifying length avoids waiting for
	#timeout to occur.
	respdata = ser.read()
	print respdata


	trace.writerow(cap.scope.datapoints[0:nbSamples])

	plain.writerow(myaes_input)
	print "capture validation processing trace number : " + str (j) 
	
'''''''''''''''''''''''''''
Traces for attack processing  
'''''''''''''''''''''''''''	
trace  = csv.writer(open("attack_processing.csv", "wb"))
plain  = csv.writer(open("attack_plain.csv", "wb"))

myaes_key   = hexStrToByteArray("2B 7E 15 16 28 AE D2 A6 AB F7 15 88 09 CF 4F 3C")


nbtraces = 5000
for j in range(nbtraces):
	for i in range(16):
		myaes_input [i] = random.randint(0, 255)
	time.sleep(0.1)
	#Flush clears input buffer
	#ser.flush()
	ser.write("k" + binascii.hexlify(myaes_key) + "\n")
	time.sleep(0.1)
	cap.scope.arm()
	pe()
	ser.write("p" + binascii.hexlify(myaes_input) + "\n")
	if cap.scope.capture(update=True, NumberPoints=None, waitingCallback=pe):
		print "Timeout"
	else:
		print "Capture OK"
	
	print "p" + binascii.hexlify(myaes_input)
	print "k" + binascii.hexlify(myaes_key)
	#Read response, which is 33 bytes long. Specifying length avoids waiting for
	#timeout to occur.
	respdata = ser.read()
	print respdata

	trace.writerow(cap.scope.datapoints[0:nbSamples])

	plain.writerow(myaes_input)

	print "capture attack processing trace number : " + str (j) 

#The following should delete the CWC Main window and disconnect
#where appropriate
cap.deleteLater()
sys.exit(app.exec_())

