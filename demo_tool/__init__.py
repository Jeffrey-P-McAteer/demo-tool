
import os
import sys
import subprocess
import time
import signal

def signal_handler(signal, frame):
    print('In signal_handler')
    sys.exit(0)

def main(args=sys.argv):
    signal.signal(signal.SIGINT, signal_handler)
    print(f'args={args}')
    while True:
        time.sleep(0.5)
        print('Doing work...')






