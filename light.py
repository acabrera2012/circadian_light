import serial
import time
import signal
import sys
import subprocess

serial_port = '/dev/ttyUSB0'  # This may change if we plug the usb into a different port on the Pi
baud_rate = 9600

lightDuration = int(sys.argv[1])                # In minutes

# Function to send commands to the relay
def send_command(command):
    ser.write(command)
    time.sleep(0.1)  # Wait for the relay to respond

def exit_gracefully():
    # Send close command
    send_command(b'\xA0' + b'\x01' + b'\x00' +  b'\xA1')

    exit(0)

def keyboard_interrupt_handler(signal, frame):
    print("Exiting due to user request...")
    exit_gracefully()

# Open the serial connection
try:
    ser = serial.Serial(serial_port, baud_rate, timeout=1)

except:
    print("No USB detected...")
    exit_gracefully()

signal.signal(signal.SIGINT, keyboard_interrupt_handler)

while True:

    if lightDuration > 0:
        # Turn on screen
        print("Turning on screen")
        subprocess.run(["xset", "dpms", "force", "on"])

        # Send open command
        send_command(b'\xA0' + b'\x01' + b'\x01' + b'\xA2')

        # Sleep for the specified period
        print("Lighting for " + str(lightDuration) + " minute(s)")
        time.sleep(lightDuration * 60)                      # Multiply duration minutes arg by 60 for sleep seconds
    
        # Turn off screen
        print("Turning off screen")
        subprocess.run(["xset", "dpms", "force", "off"])

    exit_gracefully()