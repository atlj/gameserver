import time

class Timer(object):
    def __init__(self, second = 0, minute = 0, hour = 0):
       self.second = float(second + (minute * 60) + (hour * 60 * 60))
   
   
    def start(self):
        i = 0.0
        while i < self.second:
            time.sleep(0.1)
            i += 0.1
        

