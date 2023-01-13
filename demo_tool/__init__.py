
SHARED_DEMO_FOLDER = r'S:\Support\IT\IT Shared Documents\SharedDemos'

import os
import sys
import subprocess
import time
import signal
import threading

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
    args = [a for a in args if not ('__main__.py' in a and 'demo_tool' in a) and not ('python' in a) ]
    #print(f'args={args}')

    demo_name = '_'.join(args).replace(' ', '_')
    print(f'demo_name={demo_name}')
    if len(demo_name) < 3:
        raise Exception(f'Refusing to save demo files named {demo_name}, name too short!')
    
    if not os.path.exists(SHARED_DEMO_FOLDER):
        os.makedirs(SHARED_DEMO_FOLDER, exist_ok=True)

    demo_dir = os.path.join(SHARED_DEMO_FOLDER, demo_name)
    if os.path.exists(demo_dir):
        choice = input(f'{demo_dir} already exists, append (a) to existing demo, replace demo (r), or cancel (c) ?')
        choice = choice.lower().strip()
        if 'c' in choice:
            print('Cancelling...')
            return
    
    os.makedirs(demo_dir, exist_ok=True)
    
    while not exit_flag:
        time.sleep(0.5)
        print('Doing work...')


    print(f'Opening {SHARED_DEMO_FOLDER}')
    os.startfile(os.path.realpath(SHARED_DEMO_FOLDER))





