import random, argparse, gi, sys, logging, os, shutil


gi.require_version('Gst', '1.0')
from gi.repository import Gst, GObject, GstNet

# check min-version
minGst = (1, 0)
minPy = (3, 0)

Gst.init([])
if Gst.version() < minGst:
    raise Exception("GStreamer version", Gst.version(), 'is too old, at least', minGst, 'is required')

if sys.version_info < minPy:
    raise Exception("Python version", sys.version_info, 'is too old, at least', minPy, 'is required')

# init GObject & Co. before importing local classes
GObject.threads_init()

from lib.loghandler import LogHandler

def main():
    # configure logging
    docolor = sys.stderr.isatty()
    handler = LogHandler(docolor)
    logging.root.addHandler(handler)
    level = logging.DEBUG
    logging.root.setLevel(level)

    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=str, help="Path to video files")
    parser.add_argument("random", type=bool, action="store_true", help="randomly select a file. Default: true")
    parser.add_argument("loop", type=bool, action="store_true", help="run in a loop. Default: true")
    args = parser.parse_args()
    runloop = args["loop"]


    while runloop:
        dir = os.path.normpath(args["path"])
        files = os.scandir(path=dir)
        filenum = 0
        if args["random"]:
            filenum = random.randint(0, len(files))
        else:
            if filenum + 1 < len(files):
                filenum += 1
            else:
                filenum = 0
        file = files[filenum]
        pipelineTemplate = """"filesrc location={path} ! decodebin ! video/x-raw 
        ! videorate ! videoscale ! video/x-raw, format=I420, width=1920, height=1080, framerate=25/1 
        ! matroskamux ! tcpclientsink port={port} host={host}"""
        pipeline = Gst.parse_launch(pipelineTemplate.format(path=file.path, host='127.0.0.1', port='9999'))
        pipeline.set_state(Gst.State.PLAYING)


