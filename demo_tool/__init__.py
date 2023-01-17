
from inspect import trace
import os
import sys
import subprocess
import time
import signal
import threading
import traceback
import shutil
import queue


# https://github.com/PyAV-Org/PyAV
try:
    import av
except:
    traceback.print_exc()
    subprocess.run([
        sys.executable, *('-m pip install --user av'.split())
    ], check=False)
    import av


SHARED_DEMO_FOLDER = r'S:\Support\IT\IT Shared Documents\SharedDemos'
if not 'win' in str(sys.platform).lower():
    SHARED_DEMO_FOLDER = '/tmp/SharedDemos'


exit_flag = False
def signal_handler(signal, frame):
    global exit_flag
    if exit_flag:
        sys.exit(1)
    exit_flag = True
    print('In signal_handler')


desktop_frames_in_queue = queue.Queue()
desktop_video_out_size = (0, 0)
def fill_desktop_frames_in_queue_thread():
    global desktop_frames_in_queue, desktop_video_out_size

    if 'win' in str(sys.platform).lower():
        desktop_container = av.open('desktop', format='gdigrab')
    else:
        desktop_container = av.open(os.environ.get('DISPLAY', ':0'), format='x11grab')

    # desktop_stream = desktop_container.streams.video[0]
    # print(f'desktop_stream={desktop_stream}')

    video_out_fps = desktop_container.streams.video[0].codec_context.framerate
    desktop_video_out_size = (
        desktop_container.streams.video[0].codec_context.width,
        desktop_container.streams.video[0].codec_context.height
    )
    print(f'desktop_video_out_size={desktop_video_out_size} video_out_fps={video_out_fps}')

    for frame in desktop_container.decode(video=0):
        desktop_frames_in_queue.put(frame)

mic_audio_frames_in_queue = queue.Queue()
def fill_mic_audio_frames_in_queue_thread():
    global mic_audio_frames_in_queue

    mic_container = av.open('none:0',format='avfoundation')
    for frame in mic_container.decode(audio=0):
        mic_audio_frames_in_queue.put(frame)




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

    choice = 'r'
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

    desktop_in_t = threading.Thread(target=fill_desktop_frames_in_queue_thread, args=())
    desktop_in_t.start()

    if not os.path.exists(demo_video_f):
        video_out_container = av.open(demo_video_f, 'w')
        video_out_stream = video_out_container.add_stream(
            'libx264', rate=video_out_fps,
            options={"crf":"23", }
        )
        video_out_stream.codec_context.width = video_out_size[0]
        video_out_stream.codec_context.height = video_out_size[1]
    else:
        # Move old file -> demo_video_f.old.mp4, open it, copy old video frames into new video file.
        # Sucks for efficiency but needs to happen to keep dts numbers valid.
        old_demo_video_f = demo_video_f.replace('.mp4', '.old.mp4')
        if os.path.exists(old_demo_video_f):
            os.remove(old_demo_video_f)
        shutil.move(demo_video_f, old_demo_video_f)

        video_out_container = av.open(demo_video_f, 'w')
        video_out_stream = video_out_container.add_stream(
            'libx264', rate=video_out_fps,
            options={"crf":"23", }
        )
        video_out_stream.codec_context.width = video_out_size[0]
        video_out_stream.codec_context.height = video_out_size[1]

        # Copy in frames
        try:
            old_video_container = av.open(old_demo_video_f, 'r')
            for frame in old_video_container.decode(video=0):
                print(f'old frame={frame}')
                video_out_container.mux(video_out_stream.encode(frame))
                if exit_flag:
                    break # This also halts timestamps, apparently.
        except:
            traceback.print_exc()

    print(f'video_out_container={video_out_container} video_out_stream={video_out_stream}')

    print('')
    print('Ready to record!')
    print('')
    if 'a' in choice:
        _ = input('Press enter to begin recording')
    
    while not exit_flag:
        # Process like one frame
        print(f'while not {exit_flag}')
        try:
            for frame in desktop_container.decode(video=0):
                print(f'frame={frame}')
                video_out_container.mux(video_out_stream.encode(frame))
                if exit_flag:
                    break # This also halts timestamps, apparently.

        except:
            traceback.print_exc()
            time.sleep(1.5)

    try:
        video_out_container.close()
    except:
        traceback.print_exc()
    
    print(f'Opening {demo_dir}')
    print(f'Play {demo_video_f}')
    try:
        os.startfile(os.path.realpath(demo_dir))
    except:
        pass





