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
            golfer.courses['The National - Bluff/Ridge'] = {
                'par': [4,4,5,3,4,5,3,4,4,4,4,3,4,3,5,4,5,4],
                'hdcps': [8,3,7,9,6,5,4,1,2,5,7,9,2,4,3,6,8,1],
                'tees': {
                    'One': (74.2, 143),
                    'Two': (72.5, 141),
                    'Tournament': (71.4, 136),
                    'Three': (70.4, 133),
                    'Four': (68.8, 128),
                    'Four/Five': (67.6, 127),
                    'Five': (66.9, 122)
                }
            }
            with open('pkl_files/' + pf, 'wb') as f:
                pickle.dump(golfer, f)


if __name__ == '__main__':
    course_update()
    print('Successfully added new course to all players')
