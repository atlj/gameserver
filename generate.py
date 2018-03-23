from database import *
from models import Camp


def generate_map(count, level):
    """
        Generete Word Method
        @param count: add Bot Camp
        @param level: max level Bot Camp
    
    """
        
    print 'Generating Map...\nCamps: {}\n'.format(str(count))
    for i in range(count):
        camp = Camp(random.randrange(level + 1))
            
        print 'Id: ' + str(camp.id)
        print 'Level  ' + str(camp)
        print 'Army: ' + str(len(camp.army))
        print 'Location: ' + str(camp.ords)
        print '\n'
        db = DBCamp()
        db.connect()
        db.insert(camp)
        db.close()
