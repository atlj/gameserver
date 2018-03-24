import os, time
cdir = os.path.dirname(os.path.realpath(__file__))
__author__ = "atlj"
class log(object):
    def __init__(self, name, directory = cdir):
        self.logtype = name
        self.logname = name+" " + time.ctime()+".log"
        self.log_directory = os.path.join(directory, "logs")
    
    def write(self, data):
        if not os.path.exists(self.log_directory):
            os.makedirs(self.log_directory)
        
        if not os.path.exists(os.path.join(self.log_directory, self.logname)) :
            self.logfile = open(os.path.join(self.log_directory, self.logname), "w")
         
        self.logfile.write(time.ctime().split(" ")[3]+" >> "+"["+self.logtype+"]"+" >> "+data+"\n"), 
        self.logfile.flush()
        os.fsync(self.logfile.fileno())
