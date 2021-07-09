import pickle
from sys import argv
from os import listdir, makedirs
from os.path import isfile, join
import king_classic_pkling
from king_classic_pkling import PlayGolf, Player


def tee_update(player, course, new_tee):
    allfiles = [f for f in listdir('pkl_files/') if isfile(join('pkl_files/', f))]
    for pf in allfiles:
        with open('pkl_files/' + pf, 'rb') as f:
            golfer = pickle.load(f)
            if golfer.name == player:
                golfer.tees[course] = new_tee
                with open('pkl_files/' + pf, 'wb') as f:
                    pickle.dump(golfer, f)


if __name__ == '__main__':
    _, str(p), str(c), str(nt) = argv
    tee_update(p, c, nt)
