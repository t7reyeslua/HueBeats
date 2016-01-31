#!/usr/bin/python
import sys
import ast
from hueHandler import HueHandler
from peakMonitor import PeakMonitor
from ConfigParser import ConfigParser
from daemon import Daemon
import os
from time import sleep
import signal


class GracefulExit(Exception):
    pass


def signal_handler(signum, frame):
    raise GracefulExit


class HueBeats():
    '''
    Single instance
    '''

    def run(self):
        try:
            self.settings = ConfigParser()
            self.settings.read('settings.config')
            self.hue = HueHandler(self.settings.get('hue', 'bridge_ip'),
                             self.settings.get('hue', 'username'),
                             ast.literal_eval(self.settings.get('hue', 'lights_ids')))
            if self.hue.connected:
                self.start_spotify()
                self.set_lights('dancing_state')
                monitor = PeakMonitor(
                        self.settings.get('pulseaudio', 'sink_name'),
                        self.settings.getint('pulseaudio', 'meter_rate'),
                        self.settings.getint('pulseaudio', 'max_sample_value'),
                        self.settings.getint('pulseaudio', 'display_scale'),
                        self.hue)
                for sample in monitor:
                    pass
        except GracefulExit:
            self.stop_dancing()
        return

    def start_spotify(self):
        spotify_playlist = self.settings.get('spotify', 'playlist_uri')
        command = '(spotify 1>/dev/null 2>&1 &) && ' + \
                  'sleep 3 && ' + \
                  'qdbus org.mpris.MediaPlayer2.spotify / ' + \
                  'org.freedesktop.MediaPlayer2.OpenUri ' +\
                  spotify_playlist
        os.system(command)
        return

    def stop_spotify(self):
        command = 'qdbus org.mpris.MediaPlayer2.spotify / ' + \
                  'org.freedesktop.MediaPlayer2.Stop'
        os.system(command)
        return

    def set_lights(self, state):
        states = []
        for light in self.hue.lights_ids:
            states.append(
                    ast.literal_eval(
                            self.settings.get('hue', state + '_' + str(light))))
        self.hue.set_state(states)
        return

    def set_group(self, state):
        states = ast.literal_eval(self.settings.get('hue', state + '_0'))
        self.hue.set_state_group(states)
        return

    def stop_dancing(self):
        self.set_group('initial_state')
        self.stop_spotify()
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

    signal.signal(signal.SIGTERM, signal_handler)
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
