__author__ = 'quentin'

from .tracking_unit import TrackingUnit
import logging
import traceback
import json

from ethoscope.utils.description import DescribedObject


class Monitor(DescribedObject):

    _description = {"overview":
    """
    A monitor orchestrates the different software modules
    and implements the logic to scale experiments to more than 1 animal
    """,
    
        "arguments": [
            {
                "type": "str", "name": "yoke",
                "description": "A mapping of yoke:focal animals",
                "default": ""}

        ]}
                                   
    def __init__(self, camera, tracker_class,
                 rois = None, stimulators=None,
                 yoke=None,
                 *args, **kwargs  # extra arguments for the tracker objects
                 ):
        r"""
        Class to orchestrate the tracking of multiple objects.
        It performs, in order, the following actions:

         * Requesting raw frames (delegated to :class:`~ethoscope.hardware.input.cameras.BaseCamera`)
         * Cutting frame portions according to the ROI layout (delegated to :class:`~ethoscope.core.tracking_unit.TrackingUnit`).
         * Detecting animals and computing their positions and other variables (delegated to :class:`~ethoscope.trackers.trackers.BaseTracker`).
         * Using computed variables to interact physically (i.e. feed-back) with the animals (delegated to :class:`~ethoscope.stimulators.stimulators.BaseStimulator`).
         * Drawing results on a frame, optionally saving video (delegated to :class:`~ethoscope.drawers.drawers.BaseDrawer`).
         * Saving the result of tracking in a database (delegated to :class:`~ethoscope.utils.io.ResultWriter`).

        :param camera: a camera object responsible of acquiring frames and associated time stamps
        :type camera: :class:`~ethoscope.hardware.input.cameras.BaseCamera`
        :param tracker_class: The algorithm that will be used for tracking. It must inherit from :class:`~ethoscope.trackers.trackers.BaseTracker`
        :type tracker_class: class
        :param rois: A list of region of interest.
        :type rois: list(:class:`~ethoscope.core.roi.ROI`)
        :param stimulators: The class that will be used to analyse the position of the object and interact with the system/hardware.
        :type stimulators: list(:class:`~ethoscope.stimulators.stimulators.BaseInteractor`
        :param yoke: Pairs of focal (key) and yoked (value) region_ids. An animal in a yoked region_id will be stimulated following its focal counterpart.
        :type yoke: dictionary 
        :param args: additional arguments passed to the tracking algorithm
        :param kwargs: additional keyword arguments passed to the tracking algorithm
        """

        self._camera = camera
        self._last_frame_idx =0
        self._force_stop = False
        self._last_positions = {}
        self._last_time_stamp = 0
        self._is_running = False


        if rois is None:
            raise NotImplementedError("rois must exist (cannot be None)")

        if stimulators is None:
            self._unit_trackers = [TrackingUnit(tracker_class, r, None, *args, **kwargs) for r in rois]

        elif len(stimulators) == len(rois):
            # if the user does not enter anything in yoke, yoke becomes "" (not None)
            if yoke is None or yoke == "":
                self._unit_trackers = [TrackingUnit(tracker_class, r, inter, *args, **kwargs) for r, inter in zip(rois, stimulators)]
            else:
                yoke = json.loads(yoke)
                self._unit_trackers = [None for r in rois]
                for f in yoke.values():
                    # check if the corresponding unit tracker
                    # is still None or not
                    # It wont be none if the same animal is followed
                    # by another yoke animal
                    # i.e. if the focal animal is not mapped to a single yoke 
                    ff = int(f)
                    if self._unit_trackers[ff-1] is None:
                        self._unit_trackers[ff-1] = TrackingUnit(tracker_class, rois[ff-1], stimulators[ff-1], *args, **kwargs)
                
                for y, f in yoke.items():
                    yy = int(y)
                    ff = int(f)
                    self._unit_trackers[yy-1] = TrackingUnit(
                        tracker_class, rois[yy-1], stimulators[yy-1], *args,
                        # assign to the stimulator the tracker of the focal animal
                        # instead of that of this animal.
                        # this causes this stimulator to obey the behavior of the other animal
                        tracker=self._unit_trackers[ff-1]._tracker,
                        **kwargs)
                
                # finally, if a region id is neither yoke nor focal, assume focal
                for i, ut in enumerate(self._unit_trackers):
                    if ut is None:
                        self._unit_trackers[i] = TrackingUnit(tracker_class, rois[i], stimulators[i], *args, **kwargs)

                assert all([not ut._tracker is None for ut in self._unit_trackers])

        else:
            raise ValueError("You should have one interactor per ROI")

    @property
    def last_positions(self):
        """
        :return: The last positions (and other recorded variables) of all detected animals
        :rtype: dict
        """
        return self._last_positions

    @property
    def last_time_stamp(self):
        """
        :return: The time, in seconds, since monitoring started running. It will be 0 if the monitor is not running yet.
        :rtype: float
        """
        time_from_start = self._last_time_stamp / 1e3
        return time_from_start

    @property
    def last_frame_idx(self):
        """
        :return: The number of the last acquired frame.
        :rtype: int
        """
        return self._last_frame_idx

    def stop(self):
        """
        Interrupts the `run` method. This is meant to be called by another thread to stop monitoring externally.
        """
        self._force_stop = True

    def run(self, result_writer = None, drawer = None):
        """
        Runs the monitor indefinitely.

        :param result_writer: A result writer used to control how data are saved. `None` means no results will be saved.
        :type result_writer: :class:`~ethoscope.utils.io.ResultWriter`
        :param drawer: A drawer to plot the data on frames, display frames and/or save videos. `None` means none of the aforementioned actions will performed.
        :type drawer: :class:`~ethoscope.drawers.drawers.BaseDrawer`
        """

        try:
            logging.info("Monitor starting a run")
            self._is_running = True

            for i,(t, frame) in enumerate(self._camera):

                if self._force_stop:
                    logging.info("Monitor object stopped from external request")
                    break

                self._last_frame_idx = i
                self._last_time_stamp = t
                self._frame_buffer = frame

                for j,track_u in enumerate(self._unit_trackers):
                    data_rows = track_u.track(t, frame)
                    if len(data_rows) == 0:
                        self._last_positions[track_u.roi.idx] = []
                        continue

                    abs_pos = track_u.get_last_positions(absolute=True)

                    # if abs_pos is not None:
                    self._last_positions[track_u.roi.idx] = abs_pos

                    if result_writer is not None:
                        result_writer.write(t, track_u.roi, data_rows)

                if result_writer is not None:
                    result_writer.flush(t, frame)

                if drawer is not None:
                    drawer.draw(frame, self._last_positions, self._unit_trackers)
                self._last_t = t

        except Exception as e:
            logging.error("Monitor closing with an exception: '%s'" % traceback.format_exc())
            raise e

        finally:
            self._is_running = False
            logging.info("Monitor closing")




