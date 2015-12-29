#!/usr/bin/python
from hueHandler import HueHandler
from peakMonitor import PeakMonitor
from ConfigParser import ConfigParser


def main():
    settings = ConfigParser()
    settings.read('settings.config')
    hue = HueHandler(settings.get('hue','bridge_ip'),
                     settings.get('hue', 'username'))
    if hue.connected:
        monitor = PeakMonitor(settings.get('pulseaudio','sink_name'),
                              settings.getint('pulseaudio', 'meter_rate'),
                              settings.getint('pulseaudio', 'max_sample_value'),
                              settings.getint('pulseaudio', 'display_scale'),
                              hue)
        for sample in monitor:
            pass

if __name__ == '__main__':
    main()