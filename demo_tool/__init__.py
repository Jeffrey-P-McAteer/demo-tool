
SHARED_DEMO_FOLDER = r'S:\Support\IT\IT Shared Documents\SharedDemos'

import os
import sys
import subprocess
import time
import signal
import threading
import traceback

# https://github.com/PyAV-Org/PyAV
try:
    import av
except:
    traceback.print_exc()
    subprocess.run([
        sys.executable, *('-m pip install --user av'.split())
    ], check=False)
    import av


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
    os.makedirs(demo_dir, exist_ok=True)

    demo_video_f = os.path.join(demo_dir, demo_name+'.mp4')
    print(f'Recording desktop to {demo_video_f}')

    if os.path.exists(demo_dir) and os.path.exists(demo_video_f):
        choice = input(f'{demo_dir} already exists, append (a) to existing demo, replace demo (r), or cancel (c) ?')
        choice = choice.lower().strip()
        if 'c' in choice:
            print('Cancelling...')
            return
        elif 'r' in choice:
            print('Replacing...')
            time.sleep(1)
            if exit_flag:
                return
            os.remove(demo_video_f)
        else:
            print('Appending...') # Default behavior

    
    while not exit_flag:
        time.sleep(0.5)
        print('Doing work...')


    print(f'Opening {demo_dir}')
    os.startfile(os.path.realpath(demo_dir))





