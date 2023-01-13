
import os
import sys
import subprocess
import time
import signal

exit_flag = False
def signal_handler(signal, frame):
    global exit_flag
    if exit_flag:
        sys.exit(1)
    exit_flag = True
    print('In signal_handler')

def main(args=sys.argv):
    global exit_flag
    signal.signal(signal.SIGINT, signal_handler)
    print(f'args={args}')
    while not exit_flag:
        time.sleep(0.5)
        print('Doing work...')






