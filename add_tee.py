import pickle
from sys import argv
from os import listdir, makedirs
from os.path import isfile, join
import king_classic_pkling
from king_classic_pkling import PlayGolf, Player


def add_tee():
    allfiles = [f for f in listdir('pkl_files/') if isfile(join('pkl_files/', f))]
    for pf in allfiles:
        with open('pkl_files/' + pf, 'rb') as f:
            golfer = pickle.load(f)
            if golfer.name == 'Alex King':
                golfer.tees['The National - Cove/Bluff'] = 'Two'
            elif golfer.name == 'Andy Tapper':
                golfer.tees['The National - Cove/Bluff'] = 'One'
            elif golfer.name == 'Bobby Jovanov':
                golfer.tees['The National - Cove/Bluff'] = 'Two'
            elif golfer.name == 'Colt Davis':
                golfer.tees['The National - Cove/Bluff'] = 'Tournament'
            elif golfer.name == 'Cooper Stainbrook':
                golfer.tees['The National - Cove/Bluff'] = 'One'
            elif golfer.name == 'Eric Laorr':
                golfer.tees['The National - Cove/Bluff'] = 'One'
            elif golfer.name == 'Jeff Veness':
                golfer.tees['The National - Cove/Bluff'] = 'Three'
            elif golfer.name == 'Jerry King':
                golfer.tees['The National - Cove/Bluff'] = 'Three'
            elif golfer.name == 'Josh Duckett':
                golfer.tees['The National - Cove/Bluff'] = 'Two'
            elif golfer.name == 'Justin Casson':
                golfer.tees['The National - Cove/Bluff'] = 'Two'
            elif golfer.name == 'Mathias Jackson':
                golfer.tees['The National - Cove/Bluff'] = 'Three'
            elif golfer.name == 'Reggie Sherrill':
                golfer.tees['The National - Cove/Bluff'] = 'Three'
            elif golfer.name == 'Scott Davis':
                golfer.tees['The National - Cove/Bluff'] = 'Tournament'
            elif golfer.name == 'Stuart King':
                golfer.tees['The National - Cove/Bluff'] = 'One'
            elif golfer.name == 'Zach Taylor':
                golfer.tees['The National - Cove/Bluff'] = 'Tournament'

            with open('pkl_files/' + pf, 'wb') as f:
                pickle.dump(golfer, f)


if __name__ == '__main__':
    add_tee()
    print('Successfully added new tee to all players')
