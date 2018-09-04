import signal
import time
import argparse
import sys
import logging
import os
import re
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler
from watchdog.events import PatternMatchingEventHandler

exit_flag = False

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARN)
formatter = logging.Formatter('%(asctime)s - %(message)s')
file_handler = logging.StreamHandler()
file_handler.setFormatter(formatter)
logging.basicConfig(level=logging.INFO,
                    filename="watch.log",
                    format='%(asctime)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')


class MyHandler(PatternMatchingEventHandler):

    def on_modified(self, event):
        print 'cat'


def signal_handler(sig_num, frame):
    """
    This is a handler for SIGTERM and SIGINT.
    Other signals can be mapped here as well (SIGHUP?)
    Basically it just sets a global flag,
    and main() will exit it's loop if the signal is trapped.
    :param sig_num: The integer signal number that was trapped from the OS.
    :param frame: Not used
    :return None
    """

    # logger.warn('Received ' + signal.Signals(sig_num).name)
    logger.warn('Process terminated')

    global exit_flag
    exit_flag = True


def createParser():
    parser = argparse.ArgumentParser()
    parser.add_argument("filepath", help="where to look for file changes")
    return parser.parse_args()


def main(dirpath):
    # Hook these two signals from the OS ..
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    # Now my signal_handler will get called if OS sends either
    # of these to my process.

    event_handler = LoggingEventHandler()
    observer = Observer()

    # recursive=True will monitor sub-dirs and not just the specified dir
    observer.schedule(event_handler, dirpath, recursive=True)
    observer.schedule(MyHandler(), dirpath)
    observer.start()
    print 'Program is starting up'
    try:
        # Will keep track of what lines in what file the word 'magic' is in
        magic_dict = {}
        while not exit_flag:

            # Do my long-running stuff
            print 'searching'

            # I can set up a dictionary with the file and
            # what lines magic appears on
            for filename in os.listdir(dirpath):
                #  Making sure we do not replace the dictionary each loop check
                if filename not in magic_dict.keys():
                    magic_dict[filename] = list()

                file_object = open(dirpath + '/' + filename, "r")
                file_contents = file_object.readlines()
                for i, line in enumerate(file_contents):
                    print magic_dict
                    print i, line
                    magic_in_line = bool(re.search('magic', line))
                    if magic_in_line and (i not in magic_dict[filename]):
                        magic_dict[filename].append(i)
                        logger.warn('Magic keyword in file '
                                    + filename + ' line: ' + str(i))

            # put a sleep inside my while loop so I don't peg
            # the cpu usage at 100%
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
