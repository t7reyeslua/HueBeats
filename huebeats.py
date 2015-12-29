#!/usr/bin/python
import sys
from hueHandler import HueHandler
from peakMonitor import PeakMonitor
from ConfigParser import ConfigParser
from daemon import Daemon


class HueBeats():
    '''
    Single instance
    '''

    def run(self):
        settings = ConfigParser()
        settings.read('settings.config')
        hue = HueHandler(settings.get('hue', 'bridge_ip'),
                         settings.get('hue', 'username'))
        if hue.connected:
            monitor = PeakMonitor(
                    settings.get('pulseaudio', 'sink_name'),
                    settings.getint('pulseaudio', 'meter_rate'),
                    settings.getint('pulseaudio', 'max_sample_value'),
                    settings.getint('pulseaudio', 'display_scale'),
                    hue)
            for sample in monitor:
                pass
        return


class HueBeats_Daemon(Daemon):
    '''
    Daemon wrapper around HueBeats. Using this allows us to also launch the
    app in non-daemon mode, which is useful during development.
    '''
    def run(self):
        hb = HueBeats()
        hb.run()


def main():
    if __file__ not in ('huebeats.py', './huebeats.py'):
        print("The app needs to be run from the root directory " +
              "(e.g. HueBeats/). It is\nadvisable to use the huebeats.sh " +
              "script that is provided there.")
        sys.exit(2)

    if len(sys.argv) == 2:
        daemon = HueBeats_Daemon('/tmp/hueBeats.pid')
        if 'start' == sys.argv[1]:
            print("Starting HueBeats")
            daemon.start()
        elif 'stop' == sys.argv[1]:
            print("Stopping HueBeats")
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            print("Restarting HueBeats")
            daemon.restart()
        else:
            print("Unknown command %s" % sys.argv[1])
            print("Usage: %s start|stop|restart" % sys.argv[0])
            sys.exit(2)
        sys.exit(0)
    else:
        hb = HueBeats()
        hb.run()

if __name__ == '__main__':
    main()
