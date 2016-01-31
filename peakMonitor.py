import sys
from Queue import Queue
from ctypes import POINTER, c_ubyte, c_void_p, c_ulong, cast
# from colorama import Fore, Back, Style
import datetime

# From https://github.com/Valodim/python-pulseaudio
from pulseaudio.lib_pulseaudio import *


class PeakMonitor(object):

    def __init__(self, sink_name, rate, max_sample_values, display_scale, hue):
        self.sink_name = sink_name
        self.hue = hue
        self.rate = rate
        self.max_spaces = max_sample_values * display_scale
        self.last = 0
        self.last_ts = datetime.datetime.utcnow()

        # Wrap callback methods in appropriate ctypefunc instances so
        # that the Pulseaudio C API can call them
        self._context_notify_cb = pa_context_notify_cb_t(
                self.context_notify_cb)
        self._sink_info_cb = pa_sink_info_cb_t(self.sink_info_cb)
        self._stream_read_cb = pa_stream_request_cb_t(self.stream_read_cb)

        # stream_read_cb() puts peak samples into this Queue instance
        self._samples = Queue()

        # Create the mainloop thread and set our context_notify_cb
        # method to be called when there's updates relating to the
        # connection to Pulseaudio
        _mainloop = pa_threaded_mainloop_new()
        _mainloop_api = pa_threaded_mainloop_get_api(_mainloop)
        context = pa_context_new(_mainloop_api, 'peak_demo')
        pa_context_set_state_callback(context, self._context_notify_cb, None)
        pa_context_connect(context, None, 0, None)
        pa_threaded_mainloop_start(_mainloop)

    def __iter__(self):
        while True:
            yield self._samples.get()

    def context_notify_cb(self, context, _):
        state = pa_context_get_state(context)

        if state == PA_CONTEXT_READY:
            print "Pulseaudio connection ready..."
            # Connected to Pulseaudio. Now request that sink_info_cb
            # be called with information about the available sinks.
            o = pa_context_get_sink_info_list(context,
                                              self._sink_info_cb, None)
            pa_operation_unref(o)

        elif state == PA_CONTEXT_FAILED:
            print "Connection failed"

        elif state == PA_CONTEXT_TERMINATED:
            print "Connection terminated"

    def sink_info_cb(self, context, sink_info_p, _, __):
        if not sink_info_p:
            return

        sink_info = sink_info_p.contents
        print '-' * 60
        print 'index:', sink_info.index
        print 'name:', sink_info.name
        print 'description:', sink_info.description

        if sink_info.name == self.sink_name:
            # Found the sink we want to monitor for peak levels.
            # Tell PA to call stream_read_cb with peak samples.
            print
            print 'setting up peak recording: ', sink_info.monitor_source_name
            print
            samplespec = pa_sample_spec()
            samplespec.channels = 1
            samplespec.format = PA_SAMPLE_U8
            samplespec.rate = self.rate

            pa_stream = pa_stream_new(context,
                                      "peak detect demo",
                                      samplespec, None)
            pa_stream_set_read_callback(pa_stream,
                                        self._stream_read_cb,
                                        sink_info.index)
            pa_stream_connect_record(pa_stream,
                                     sink_info.monitor_source_name,
                                     None,
                                     PA_STREAM_PEAK_DETECT)

    def stream_read_cb(self, stream, length, index_incr):
        data = c_void_p()
        pa_stream_peek(stream, data, c_ulong(length))
        data = cast(data, POINTER(c_ubyte))
        for i in xrange(length):
            # When PA_SAMPLE_U8 is used, samples values range from 128
            # to 255 because the underlying audio data is signed but
            # it doesn't make sense to return signed peaks.
            self.analyze_samples(data[i] - 128)
            self._samples.put(data[i] - 128)
        pa_stream_drop(stream)

    def analyze_samples(self, sample):
        bar = '>' * sample
        spaces = ' ' * (self.max_spaces - sample)
        if self.last == 0:
            diff = 0.0
        else:
            diff = abs((sample * 1.0/self.last) - 1)

        diff1 = abs(sample - self.last)
        self.heartbeat(sample)
        self.last = sample
        if diff1 > 20:
            print('| %.2f %3d %3d %s%s\n' % (diff, diff1, sample, bar, spaces))
        else:
            print('| %.2f %3d %3d %s%s\n' % (diff, diff1, sample, bar, spaces))
        return

    def heartbeat(self, sample):
        value = int(sample * 255 * 1.0/128)
        time_delta = (datetime.datetime.utcnow() - self.last_ts)\
            .total_seconds()
        # Check if cache expired
        if time_delta < .1:
            return
        self.hue.update_brightness(1, value)
        self.hue.update_brightness(2, value)
        self.hue.update_brightness(3, value)
        self.hue.update_brightness(4, value)
        self.last_ts = datetime.datetime.utcnow()
