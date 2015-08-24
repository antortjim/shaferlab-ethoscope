__author__ = 'quentin'

from ethoscope.tracking.cameras import OurPiCameraAsync

# Build ROIs from greyscale image
from ethoscope.tracking.roi_builders import SleepMonitorWithTargetROIBuilder

# the robust self learning tracker
from ethoscope.tracking.trackers import AdaptiveBGModel

# the standard monitor
from ethoscope.tracking.monitor import Monitor
from ethoscope.utils.io import SQLiteResultWriter

import pkg_resources
import optparse
import logging




# _result_dir = "/psv_data/results/"
# _last_img_file = "/tmp/psv/last_img.jpg"
# _dbg_img_file = "/tmp/psv/dbg_img.png"
# _log_file = "/tmp/psv/psv.log"

if __name__ == "__main__":

    parser = optparse.OptionParser()
    parser.add_option("-o", "--output", dest="out", help="the output file (eg out.db   )", type="str",default=None)
        #
    parser.add_option("-r", "--result-video", dest="result_video", help="the path to an optional annotated video file."
                                                                "This is     useful to show the result on a video.",
                                                                type="str", default=None)

    parser.add_option("-d", "--draw-every",dest="draw_every", help="how_often to draw frames", default=0, type="int")

    (options, args) = parser.parse_args()

    option_dict = vars(options)

    # logging.basicConfig(filename=_log_file, level=logging.INFO)



    logging.info("Starting Monitor thread")

    cam = OurPiCameraAsync(target_fps=20, target_resolution=(1280,960))

    roi_builder = SleepMonitorWithTargetROIBuilder()
    rois = roi_builder(cam)

    logging.info("Initialising monitor")
    cam.restart()

    metadata = {
                             "machine_id": "None",
                             "machine_name": "None",
                             "date_time": cam.start_time, #the camera start time is the reference 0
                             "frame_width":cam.width,
                             "frame_height":cam.height,
                             "version": "whatever"
                              }
    draw_frames = False
    if option_dict["draw_every"] > 0:
        draw_frames = True


    monit = Monitor(cam, AdaptiveBGModel, rois,
                    draw_every_n=option_dict["draw_every"],
                    draw_results=draw_frames,
                    video_out=option_dict["result_video"])


    try:
        if option_dict["out"] is None:
            monit.run(None)
        else:
            with SQLiteResultWriter(option_dict["out"],rois, metadata) as rw:
                logging.info("Running monitor" )
                monit.run(rw)
    except KeyboardInterrupt:
        logging.info("Keyboard Exception, stopping monitor")
        monit.stop()


    logging.info("Stopping Monitor")
