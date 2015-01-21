__author__ = 'quentin'

import numpy as np
import multiprocessing
from subprocess import call
from math import sqrt

from pysolovideo.hardware_control.arduino_api import SleepDepriverInterface

class BaseInteractorSync(object):
    _tracker = None


    def __call__(self):
        if self._tracker is None:
            raise ValueError("No tracker bound to this interactor. Use `bind_tracker()` methods")

        interact, result  = self._run()
        if interact:
            self._interact(**result)

        result["interact"] = interact

        return result


    def bind_tracker(self, tracker):
        self._tracker = tracker


    def _run(self):
        raise NotImplementedError

    def _interact(self, kwargs):
        raise NotImplementedError

class SleepDepInteractor(BaseInteractorSync):
    def __init__(self, channel, sd_interface ):
        self._sleep_dep_interface = sd_interface
        self._t0 = None
        self._channel = channel

        self._distance_threshold = 1e-2
        self._inactivity_time_threshold = 90 # s

    def _interact(self, **kwargs):
        print "c=",self._channel
        self._sleep_dep_interface.deprive(**kwargs)

    def _run(self):
        positions = self._tracker.positions
        t = self._tracker.times

        if len(positions ) <2 :
            return False, {"channel":self._channel}
        tail_m = positions[-1]
        xy_m = complex(tail_m["x"] + 1j * tail_m["y"])

        tail_mm = positions[-2]

        xy_mm =complex(tail_mm["x"] + 1j * tail_mm["y"])

        if np.abs(xy_m - xy_mm) < self._distance_threshold:

            now = t[-1]
            if self._t0 is None:
                self._t0 = now

            else:
                if(now - self._t0) > self._inactivity_time_threshold:

                    self._t0 = None
                    return True, {"channel":self._channel}

        else:
            self._t0 = None

        return False, {"channel":self._channel}



###Prototyping below ###########################
class BaseInteractor(object):
    _tracker = None
    # this is not v elegant
    _subprocess = multiprocessing.Process()

    _target = None

    def __call__(self):
        if self._tracker is None:
            raise ValueError("No tracker bound to this interactor. Use `bind_tracker()` methods")

        interact, result  = self._run()
        if interact:
            self._interact_async(result)

        result["interact"] = interact

        return result


    def bind_tracker(self, tracker):
        self._tracker = tracker


    def _run(self):
        raise NotImplementedError

    def _interact_async(self, kwargs):

        # If the target is being run, we wait
        if self._subprocess.is_alive():
            return

        if self._target is None:
            raise NotImplementedError("_target must ba a defined function")

        self._subprocess = multiprocessing.Process(target=self._target, kwargs = kwargs)

        self._subprocess.start()

class DefaultInteractor(BaseInteractor):

    def _run(self):
       return False, {}


def beep(freq):
    from scikits.audiolab import play
    length = 0.5
    rate = 10000.
    length = int(length * rate)
    factor = float(freq) * (3.14 * 2) / rate
    s = np.sin(np.arange(length) * factor)
    s *= np.linspace(1,0.3,len(s))
    play(s, 10000)

class SystemPlaySoundOnStop(BaseInteractor):

    def __init__(self, freq):
        self._t0 = None
        self._target = beep
        self._freq = freq
        self._distance_threshold = 0.2
        self._inactivity_time_threshold = 30# * 4 # s
        self._rest_time = 60 # how long should we wait before restimulating (s)

    def _cumulative_dist(self, times, positions):
        now = times[-1]
        cum_dist = 0
        px_lag = None
        py_lag = None
        for t, p in reversed(zip(times, positions)):
            if px_lag is None:
                px_lag, py_lag = p["x"],  p["y"]
                continue
            cum_dist += sqrt((px_lag - p["x"]) ** 2 + (py_lag - p["y"]) ** 2)

            if (now - t) > self._inactivity_time_threshold:
                break

            px_lag, py_lag = p["x"],  p["y"]
        return cum_dist

    def _run(self):
        positions = self._tracker.positions
        times = self._tracker.times
        now = times[-1]

        if len(times) <2 or (now - times[0]) < self._inactivity_time_threshold :
            return False, {"freq":self._freq}

        cum_dist = self._cumulative_dist(times, positions)
        print positions[-1]["roi_idx"], cum_dist
        if cum_dist > self._distance_threshold:
            return False, {"freq":self._freq}

        if self._t0 is None:
            self._t0 = now
            return True, {"freq":self._freq}

        if now - self._t0 < self._rest_time:
            return False, {"freq":self._freq}

        self._t0 = now
        return True, {"freq":self._freq}

        #
        # tail_m = positions[-1]
        # xy_m = complex(tail_m["x"] + 1j * tail_m["y"])
        #
        # tail_mm = positions[-2]
        #
        # xy_mm =complex(tail_mm["x"] + 1j * tail_mm["y"])
        #
        # if np.abs(xy_m - xy_mm) < self._distance_threshold:
        #     now = time[-1]
        #     if self._t0 is None:
        #         self._t0 = now
        #     else:
        #         if(now - self._t0) > self._inactivity_time_threshold:
        #             self._t0 = None
        #             return True, {"freq":self._freq}
        # else:
        #     self._t0 = None
        #
        # return False, {"freq":self._freq}




