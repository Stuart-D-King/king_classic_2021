import pickle
from sys import argv
from os import listdir, makedirs
from os.path import isfile, join
import king_classic_pkling
from king_classic_pkling import PlayGolf, Player


def course_update():
    allfiles = [f for f in listdir('pkl_files/') if isfile(join('pkl_files/', f))]
    for pf in allfiles:
        with open('pkl_files/' + pf, 'rb') as f:
            golfer = pickle.load(f)
            golfer.courses['The National - Cove/Bluff'] = {
                'par': [4,4,3,5,4,5,3,4,4,4,4,5,3,4,5,3,4,4],
                'hdcps': [6,2,9,5,4,7,8,1,3,8,3,7,9,6,5,4,1,2],
                'tees': {
                    'One': (74.4, 143),
                    'Two': (72.4, 141),
                    'Tournament': (71.5, 137),
                    'Three': (70.4, 134),
                    'Four': (69, 127),
                    'Four/Five': (67.7, 128)
                }
            }
            with open('pkl_files/' + pf, 'wb') as f:
                pickle.dump(golfer, f)


if __name__ == '__main__':
    course_update()
    print('Successfully added new course to all players')
