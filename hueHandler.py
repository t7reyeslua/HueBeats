import sys
from pprint import pprint as pp

# From https://github.com/allanbunch/beautifulhue
from beautifulhue.api import Bridge


class HueHandler(object):

    def __init__(self, ip, username):
        self.ip = ip
        self.username = username
        self.bridge = Bridge(device={'ip': ip}, user={'name': username})
        self.connected = False
        self.connect()

    def connect(self):
        response = self.getSystemData()
        pp(response)
        if 'lights' in response:
            self.connected = True
            print 'Connected to the Hub'
            pp(response['lights'])
        elif 'error' in response[0]:
            error = response[0]['error']
            if error['type'] == 1:
                self.createConfig()
                self.connect()

    def createConfig(self):
        self.created = False
        print 'Press the button on the Hue bridge'
        while not self.created:
            resource = {'user': {'devicetype': self.username,
                                 'name': self.username}}
            response = self.bridge.config.create(resource)['resource']
            if 'error' in response[0]:
                if response[0]['error']['type'] != 101:
                    print 'Unhandled error creating configuration on the Hue'
                    sys.exit(response)
            else:
                self.created = True

    def getSystemData(self):
        resource = {'which': 'system'}
        return self.bridge.config.get(resource)['resource']

    def update_hue(self, light, value):
        if light == 0:
            light = 'all'
        resource = {
            'which': light,
            'data': {
                'state': {'on': True,
                          'sat': 254, 'bri': 200,
                          'hue': value}
            }
        }
        res = self.bridge.light.update(resource)
        pp(res)
        return

    def update_brightness(self, light, value):
        if light == 0:
            light = 'all'
        resource = {
            'which': light,
            'data': {
                'state': {'on': True, 'bri': value}
            }
        }
        res = self.bridge.light.update(resource)
        pp(res)
        return
