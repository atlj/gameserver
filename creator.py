import models
import os
from log import log
import cPickle as pickle

_author = "atlj"

cdir = os.path.dirname(os.path.realpath(__file__))

class creator(object):
    def __init__(self):
        self.log = log("Creator")

    def save(self, data, filename=False):
        if not os.path.exists(os.path.join(cdir, "Creator Models")):
            os.makedirs(os.path.join(cdir, "Creator Models"))

        if not filename:
            filename = "Creator Dumps"

        loaded = load(filename)
        if not loaded:
            todump = [data]
        else:
            todump = loaded.append(data)

        with open(os.path.join(cdir, filename), "wb") as dosya:
            pickle.dump(todump, dosya)

    def load(self, filename):
        if not os.path.exists(os.path.join(cdir, "Creator Models", filename)):
            return False
        with open(os.path.join(cdir, "Creator Models", filename), "rb") as dosya:
            return pickle.load(dosya)
    def menu(self, text, count):
        print text
        while 1:
            feedback = raw_input(">>")
            try:
                feedback = int(feedback)
            except ValueError:
                continue

            if not feedback in xrange(count):
                continue
            return feedback

    def main(self):
        main_menu_text = "arrays start at 0\n0)Olusturucular\n1)Siege Test\n"
        fb = self.menu(main_menu_text, 2)

        if fb == 0:
            fb = self.menu("\n0)Ordu Olustur", 1)
            if fb == 0:
                army_name = raw_input("Ordu Adi >>")
                general_name = raw_input("General Adi >>")
                while 1:
                    print "\nlutfen pozisyonu ornek verilen sekilde giriniz\nornek: 17, 20"
                    pozisyon = raw_input("x, y >> ")
                    pozisyon = pozisyon.split(",")
                    if not len(pozisyon) == 2:
                        continue
                    try:
                        pozisyon[0] = int(pozisyon[0])
                        pozisyon[1] = int(pozisyon[1])
                        break
                    except ValueError:
                        continue
                print "Ordu Basariyla Olusturuldu"

if __name__ == "__main__":
    creator_obj = creator()
    creator_obj.main()




