from txros import util
from twisted.internet import defer

def MakeWait(base):
    class Wait(base):
        DEFAULT_SECONDS = 1.0
        @util.cancellableInlineCallbacks
        def run(self, parameters):
            time = self.DEFAULT_SECONDS
            if type(parameters) == int or type(parameters) == float:
                time = float(parameters)
            elif type(parameters) == dict and 'time' in parameters:
                time = parameters['time']
            self.send_feedback('waiting for {} seconds'.format(time))
            yield self.nh.sleep(time)
            defer.returnValue('Done waiting.')
    return Wait
