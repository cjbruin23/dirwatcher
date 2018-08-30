import signal
import time
import argparse
import sys
import logging
from watchdog.observers import Observer 
from watchdog.events import LoggingEventHandler
from watchdog.events import PatternMatchingEventHandler

exit_flag = False

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARN)

formatter = logging.Formatter('%(asctime)s - %(message)s')
logger.setFormatter(formatter)

logging.basicConfig(level=logging.INFO,
                    filename="watch.log",
                    format='%(asctime)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')


def signal_handler(sig_num, frame):
    """
    This is a handler for SIGTERM and SIGINT. Other signals can be mapped here as well (SIGHUP?)
    Basically it just sets a global flag, and main() will exit it's loop if the signal is trapped.
    :param sig_num: The integer signal number that was trapped from the OS.
    :param frame: Not used
    :return None
    """

    logger.warn('Received ' + signal.Signals(sig_num).name)
    global exit_flag
    exit_flag = True

def createParser():
    parser = argparse.ArgumentParser()
    parser.add_argument("filepath", help="where to look for file changes")
    return parser.parse_args()

class MyHandler(PatternMatchingEventHandler):

    def process(self, event):
        print "hello there!"

    def on_modified(self, event):
        print 'cat'

def main(dirpath):
    print dirpath
    # Hook these two signals from the OS .. 
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    # Now my signal_handler will get called if OS sends either of these to my process.

    event_handler = LoggingEventHandler()
    observer = Observer()

    #recursive=True will monitor sub-dirs and not just the specified dir
    observer.schedule(event_handler, dirpath, recursive=True)
    observer.schedule(MyHandler(), dirpath)
    observer.start()
    print 'Program is starting up'
    try:
        while not exit_flag:

            # Do my long-running stuff
            print 'yes'
            # put a sleep inside my while loop so I don't peg the cpu usage at 100%
            time.sleep(5)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
    print 'Program is done'


if __name__ == '__main__':
    args = createParser()
    if len(sys.argv) == 0:
        sys.exit()
    main(args.filepath)