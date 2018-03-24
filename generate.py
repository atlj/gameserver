from database import *
from models import Camp
import random

def generate_map(count):
    """
        Generete Word Method
        @param count: add Bot Camp
        @param level: max level Bot Camp
    
    """
        

    print 'Generating Map...\nCamps: {}\n'.format(str(count))
    global liste
    for i in range(count):
        camp = Camp(random.choice(liste.split(" ")), 12)
            
        print 'Id: ' + str(camp.id)
        print 'Location: ' + str(camp.ords)
        print '\n'
