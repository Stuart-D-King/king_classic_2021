import pandas as pd
import numpy as np
import sys
import pickle
import pdb
from collections import defaultdict
from scipy.stats import rankdata
import folium
from os import listdir, makedirs
from os.path import isfile, join, exists
import boto3


def past_locations_map():
    m = folium.Map(location=[40, -98], zoom_start=5)

    folium.Marker([28.554899, -82.387863], popup='2020 - Brooksville, FL - Josh Duckett').add_to(m)
    folium.Marker([33.494171, -111.926048], popup='2018 & 2019 - Scottsdale, AZ - Alex King').add_to(m)
    folium.Marker([36.805531, -114.06719], popup='2017 - Mesquite, NV - Alex King').add_to(m)
    folium.Marker([41.878114, -87.629798], popup='2016 - Chicago, IL - Jerry King').add_to(m)
    folium.Marker([34.502587, -84.951054], popup='2015 - Calhoun, GA - Stuart King').add_to(m)
    folium.Marker([42.331427, -83.045754], popup='2014 - Detroit, MI - Reggie Sherrill').add_to(m)
    folium.Marker([39.739236, -104.990251], popup='2013 - Denver, CO - Stuart King').add_to(m)
    folium.Marker([47.677683, -116.780466], popup="2012 - Coeur d'Alene, ID - Jerry King").add_to(m)
    folium.Marker([37.096528, -113.568416], popup='2011 - St. George, UT - Reggie Sherrill').add_to(m)
    folium.Marker([38.291859, -122.458036], popup='2010 - Northern California - Alex King').add_to(m)
    folium.Marker([39.237685, -120.02658], popup='2009 - Lake Tahoe, CA - Alex King').add_to(m)
    folium.Marker([47.606209, -122.332071], popup='2008 - Seattle, WA - Alex King').add_to(m)
    folium.Marker([35.960638, -83.920739], popup='2007 - Knoxville, TN - Stuart King').add_to(m)
    folium.Marker([33.520661, -86.80249], popup='2006 - RTJ, Alabama - Gary Olson').add_to(m)
    folium.Marker([32.366805, -86.299969], popup='2005 - RTJ, Alabama - Stuart King').add_to(m)

    m.save('templates/past_locations.html')


class Player(object):

    def __init__(self, name, hdcp, courses, tees, skins=True):
        self.name = name
        self.skins = skins
        self.hdcp = hdcp
        self.scores = dict()
        self.net_scores = dict()
        self.skins_scores = dict()
        self.courses = courses
        self.tees = tees

        for course in self.courses.keys():
            self.create_scorecard(course)


    def create_scorecard(self, course):
        self.scores[course] = dict((x,0) for x in range(1,19))
        self.net_scores[course] = dict((x,0) for x in range(1,19))
        self.skins_scores[course] = dict((x,0) for x in range(1,19))


    def post_score(self, course, hole, score, hdcp):
        self.scores[course][hole] = score

        course_dct = self.courses[course]
        par = course_dct['par']
        hdcps = course_dct['hdcps']
        hole_hdcp = hdcps[hole - 1]

        if 'The National' in course:
            hdcp = round(hdcp / 2)

        if hole_hdcp <= hdcp:
            self.skins_scores[course][hole] = score - 1
        elif hdcp < 0 and hole_hdcp <= abs(hdcp):
            self.skins_scores[course][hole] = score + 1
        else:
            self.skins_scores[course][hole] = score

        if hdcp > 18:
            super_hdcp = hdcp - 18
            if hole_hdcp <= super_hdcp:
                self.net_scores[course][hole] = score - 2
            else:
                self.net_scores[course][hole] = score - 1
        elif hole_hdcp <= hdcp:
            self.net_scores[course][hole] = score - 1
        elif hdcp < 0 and hole_hdcp <= abs(hdcp):
            self.net_scores[course][hole] = score + 1
        else:
            self.net_scores[course][hole] = score


    def show_scorecard(self, course, net=False):
        if net:
            return self.net_scores[course]

        return self.scores[course]


    def front_nine(self, course, net=False, skins=False):
        if net:
            front = [v for k, v in self.net_scores[course].items()][:9]
            return front

        if skins:
            front = [v for k, v in self.skins_scores[course].items()][:9]
            return front

        front = [v for k, v in self.scores[course].items()][:9]
        return front


    def back_nine(self, course, net=False, skins=False):
        if net:
            back = [v for k,v in self.net_scores[course].items()][9:]
            return back

        if skins:
            back = [v for k,v in self.skins_scores[course].items()][9:]
            return back

        back = [v for k, v in self.scores[course].items()][9:]
        return back


    def calc_course_score(self, course, net=False, skins=False):
        if net:
            net_score = sum(self.net_scores[course].values())
            return net_score

        if skins:
            net_score = sum(self.skins_scores[course].values())
            return net_score

        score = sum(self.scores[course].values())
        return score


    def calc_total_score(self, net=False):
        if net:
            total = 0
            for course in self.scores.keys():
                net_total += sum(self.net_scores[course].values())
            return net_total

        total = 0
        for course in self.scores.keys():
            total += sum(self.scores[course].values())
        return total


class PlayGolf(object):

    def __init__(self):
        self.courses = {
            'The Oconee' : {
                'par': [5,4,4,4,3,4,5,3,4,5,4,4,3,4,3,4,5,4],
                'hdcps': [9,11,1,17,15,7,5,13,3,14,8,10,12,6,18,2,16,4],
                'tees': {
                    'One': (73.8, 139),
                    'Two': (72.8, 136),
                    'Tournament': (71.4, 134),
                    'Three': (70.5, 130),
                    'Three/Four': (68.8, 126),
                    'Four': (67.5, 121),
                    'Four/Five': (65.9, 118)
                }
            },
            'The Preserve' : {
                'par': [4,4,3,4,5,4,5,3,5,4,3,4,4,4,3,5,3,5],
                'hdcps': [1,9,17,3,11,5,13,15,7,4,8,6,16,2,10,18,12,14],
                'tees': {
                    'One': (72.2, 133),
                    'Two': (70.4, 126),
                    'Tournament': (69.5, 126),
                    'Three': (68.4, 122),
                    'Three/Four': (66.4, 117)
                }
            },
            'The National - Ridge/Bluff' : {
                'par': [4,4,3,4,3,5,4,5,4,4,4,5,3,4,5,3,4,4],
                'hdcps': [5,7,9,2,4,3,6,8,1,8,3,7,9,6,5,4,1,2],
                'tees': {
                    'One': (74.2, 143),
                    'Two': (72.5, 141),
                    'Tournament': (71.4, 136),
                    'Three': (70.4, 133),
                    'Four': (68.8, 128),
                    'Four/Five': (67.6, 127),
                    'Five': (66.9, 122)
                }
            },
            'The National - Bluff/Cove' : {
                'par': [4,4,5,3,4,5,3,4,4,4,4,3,5,4,5,3,4,4],
                'hdcps': [8,3,7,9,6,5,4,1,2,6,2,9,5,4,7,8,1,3],
                'tees': {
                    'One': (74.4, 143),
                    'Two': (72.4, 141),
                    'Tournament': (71.5, 137),
                    'Three': (70.4, 134),
                    'Four': (69, 127),
                    'Four/Five': (67.7, 128)
                }
            },
            'The National - Cove/Ridge' : {
                'par': [4,4,3,5,4,5,3,4,4,4,4,3,4,3,5,4,5,4],
                'hdcps': [6,2,9,5,4,7,8,1,3,5,7,9,2,4,3,6,8,1],
                'tees': {
                    'One': (74.6, 143),
                    'Two': (72.5, 141),
                    'Tournament': (71.7, 136),
                    'Three': (70.4, 132),
                    'Four': (68.8, 127),
                    'Four/Five': (67.3, 125)
                }
            },
            'The Landing' : {
                'par': [4,5,3,4,4,5,3,4,4,4,3,4,4,5,4,5,3,4],
                'hdcps': [3,13,15,1,11,9,17,5,7,6,8,2,10,12,4,14,18,16],
                'tees': {
                    'One': (74.5, 138),
                    'Two': (71.7, 131),
                    'Tournament': (70.6, 129),
                    'Three': (69.9, 127),
                    'Three/Four': (68.6, 124),
                    'Four': (67.3, 121)
                }
            },
            'Great Waters' : {
                'par': [4,5,4,3,4,5,4,3,4,4,4,5,4,3,4,4,3,5],
                'hdcps': [11,17,3,13,1,9,7,15,5,4,16,10,6,18,8,2,14,12],
                'tees': {
                    'Golden Bear': (75.7, 143),
                    'One': (73.3, 138),
                    'One/Two': (72, 135),
                    'Two': (70.8, 132),
                    'Two/Three': (69.6, 128),
                    'Three': (68.1, 125),
                    'Three/Four': (66.5, 121)
                }
            }
        }
        self.pkl_path = 'pkl_files/'


    def to_bucket(self, f_name):
        '''
        Write file to s3 bucket

        INPUT: f - file to write
        '''
        # Specify the service
        s3 = boto3.resource('s3')
        write_name = f_name.replace('_','-')
        s3.Bucket('king-classic-2021').upload_file(f_name, write_name)


    def add_player(self, name, hdcp, tees, skins=True):
        if not exists(self.pkl_path):
            makedirs(self.pkl_path)

        if not isfile(self.pkl_path + name.strip().lower().replace(' ','_')):
            golfer = Player(name, hdcp, self.courses, tees, skins)
            f_name = '{}{}.pkl'.format(self.pkl_path, name.strip().lower().replace(' ','_'))
            with open(f_name, 'wb') as f:
                pickle.dump(golfer, f)

            self.to_bucket(f_name)


    def add_score(self, player, course, hole, score):
        hdcp = self.calc_handicap(player, course)
        f_name = '{}{}.pkl'.format(self.pkl_path, player.strip().lower().replace(' ','_'))
        with open(f_name, 'rb') as f:
            golfer = pickle.load(f)

        golfer.post_score(course, hole, score, hdcp)

        with open(f_name, 'wb') as f:
            pickle.dump(golfer, f)

        self.to_bucket(f_name)


    def show_player_course_score(self, player, course, net=False):
        with open('{}{}.pkl'.format(self.pkl_path, player.strip().lower().replace(' ','_')), 'rb') as f:
            golfer = pickle.load(f)
        score = golfer.calc_course_score(course, net)
        return score


    def show_player_total_score(self, player, net=False):
        with open('{}{}.pkl'.format(self.pkl_path, player.strip().lower().replace(' ','_')), 'rb') as f:
            golfer = pickle.load(f)
        total_score = golfer.calc_total_score(net)
        return total_score


    def leaderboard(self, net=True):
        allfiles = [f for f in listdir(self.pkl_path) if isfile(join(self.pkl_path, f))]

        golfers = []
        for pf in allfiles:
            with open('{}'.format(self.pkl_path) + pf, 'rb') as f:
                golfers.append(pickle.load(f))

        names = []
        scores = []
        for golfer in golfers:
            names.append(golfer.name)
            total = 0
            for course in golfer.scores.keys():
                if golfer.calc_course_score(course, net) > 0:
                    total += golfer.calc_course_score(course, net)
            scores.append(total)

        rank = list(rankdata(scores, method='min'))
        # rank = list(np.unique(scores, return_inverse=True)[1])
        results = list(zip(rank, names, scores))
        sorted_results = sorted(results, key=lambda x: x[0])

        df = pd.DataFrame(sorted_results, columns=['Position', 'Name', 'Net Total'])
        # df.set_index('Position', inplace=True)

        return df


    def calc_skins(self, course, net=True):
        allfiles = [f for f in listdir(self.pkl_path) if isfile(join(self.pkl_path, f))]
        golfers = []
        for pf in allfiles:
            with open('{}'.format(self.pkl_path) + pf, 'rb') as f:
                golfers.append(pickle.load(f))

        players = [golfer for golfer in golfers if golfer.skins == True]
        names = [golfer.name for golfer in golfers]

        pot = len(names) * 5
        cols = [str(x) for x in range(1, 19)]

        scores = []
        if net:
            for player in players:
                scores.append(list(player.skins_scores[course].values()))
        else:
            for player in players:
                scores.append(list(player.scores[course].values()))

        df = pd.DataFrame(data=scores, index=names, columns=cols)
        low_scores = df.min(axis=0)
        # skins = []
        skins_dct = defaultdict(list)
        for hole, low_score in zip(range(1, 19), low_scores):
            if low_score == 0:
                continue
            scores = list(df[str(hole)].values)
            if scores.count(low_score) == 1:
                # skins.append((hole, df[str(hole)].idxmin()))
                skins_dct[df[str(hole)].idxmin()].append(str(hole))

        results = []
        for name in names:
            results.append((name, skins_dct[name], len(skins_dct[name])))
            # results.append((name, skins.count(name)))

        results = [(name, ', '.join(holes), n_skins) for name, holes, n_skins in results]
        sorted_results = sorted(results, key=lambda x: x[2], reverse=True)

        total_skins = sum(n for _, _, n in sorted_results)
        skin_value = pot / total_skins

        final_results = [(name, holes, skins * skin_value) for name, holes, skins in sorted_results]

        df_results = [(name, holes, round(winnings/skin_value), float(winnings)) for name, holes, winnings in final_results]

        df_skins = pd.DataFrame(df_results, columns=['Player', 'Holes Won', 'Skins', 'Winnings'])
        df_skins['Winnings'] = df_skins['Winnings'].map('${:,.2f}'.format)

        return df_skins


    def calc_teams(self, teams, course):
        allfiles = [f for f in listdir(self.pkl_path) if isfile(join(self.pkl_path, f))]
        golfers = []
        for pf in allfiles:
            with open('{}'.format(self.pkl_path) + pf, 'rb') as f:
                golfers.append(pickle.load(f))

        names = [golfer.name for golfer in golfers]
        dct = dict(zip(names, golfers))
        # pot = len(teams) * 20
        team_scores = []
        for (p1, p2) in teams:
            g1 = dct[p1]
            g2 = dct[p2]
            s1 = g1.calc_course_score(course, net=True)
            s2 = g2.calc_course_score(course, net=True)
            team_score = s1 + s2
            team_scores.append(team_score)

        team_nums = [idx+1 for idx, _ in enumerate(range(len(teams)))]
        rank = list(rankdata(team_scores, method='min'))
        results = list(zip(rank, team_nums, team_scores))
        sorted_results = sorted(results, key=lambda x: x[0])

        clean_teams = [p1 + ' / ' + p2 for p1, p2 in teams]
        final_results = [(r, clean_teams[i-1], s) for r,i,s in sorted_results]

        df = pd.DataFrame(final_results, columns=['Position', 'Team', 'Score'])
        df['Winnings'] = 0

        first = [t for r,t,s in final_results if r == 1]
        second = [t for r,t,s in final_results if r == 2]
        third = [t for r,t,s in final_results if r == 3]

        if len(first) == 1 and len(second) == 1:
            f_winnings = 80
            s_winnings = 50
            t_winnings = 30 / len(third)
            df['Winnings'] = np.where(df['Position'] == 1, f_winnings, df['Winnings'])
            df['Winnings'] = np.where(df['Position'] == 2, s_winnings, df['Winnings'])
            df['Winnings'] = np.where(df['Position'] == 3, t_winnings, df['Winnings'])
        elif len(first) == 2:
            f_winnings = (80 + 50) / 2
            s_winnings = 30 / len(third)
            df['Winnings'] = np.where(df['Position'] == 1, f_winnings, df['Winnings'])
            df['Winnings'] = np.where(df['Position'] == 3, s_winnings, df['Winnings'])
        elif len(first) == 1  and len(second) > 1:
            f_winnings = 80
            s_winnings = (50 + 30) / len(second)
            df['Winnings'] = np.where(df['Position'] == 1, f_winnings, df['Winnings'])
            df['Winnings'] = np.where(df['Position'] == 2, s_winnings, df['Winnings'])
        elif len(first) > 2:
            f_winnings = (80 + 50 + 30) / len(first)
            df['Winnings'] = np.where(df['Position'] == 1, f_winnings, df['Winnings'])

        df['Winnings'] = df['Winnings'].map('${:,.2f}'.format)

        return df


    def player_scorecards(self, players, course, net=False, skins=False):
        course_dct = self.courses[course]
        course_par = course_dct['par']
        course_hdcps = course_dct['hdcps']

        front_par = sum(course_par[:9])
        back_par = sum(course_par[9:])
        total_par = sum(course_par)
        par = course_par[:9] + [front_par] + course_par[9:] + [back_par, total_par, 0, 0]
        hdcp = course_hdcps[:9] + [0] + course_hdcps[9:] + [0,0,0,0]
        scores = [par, hdcp]

        allfiles = [f for f in listdir(self.pkl_path) if isfile(join(self.pkl_path, f))]
        golfers = []
        for pf in allfiles:
            with open('{}'.format(self.pkl_path) + pf, 'rb') as f:
                golfers.append(pickle.load(f))

        names = [golfer.name for golfer in golfers]
        dct = dict(zip(names, golfers))

        for player in players:
            golfer = dct[player]

            if net:
                front = golfer.front_nine(course, net=True)
                front_tot = sum(front)
                back = golfer.back_nine(course, net=True)
                back_tot = sum(back)
                total = golfer.calc_course_score(course, net=True)
                net_total = golfer.calc_course_score(course, net=True)
            elif skins:
                front = golfer.front_nine(course, skins=True)
                front_tot = sum(front)
                back = golfer.back_nine(course, skins=True)
                back_tot = sum(back)
                total = golfer.calc_course_score(course, skins=True)
                net_total = golfer.calc_course_score(course, skins=True)
            else:
                front = golfer.front_nine(course)
                front_tot = sum(front)
                back = golfer.back_nine(course)
                back_tot = sum(back)
                total = golfer.calc_course_score(course)
                net_total = golfer.calc_course_score(course, net=True)
            hdcp = self.calc_handicap(player, course)
            score = front + [front_tot] + back + [back_tot, total, hdcp, net_total]
            scores.append(score)

        idx = ['Par', 'Hdcp'] + players.copy()

        cols = [str(x) for x in range(1, 19)]
        all_cols = cols[:9] + ['Front'] + cols[9:] + ['Back', 'Total', 'Hdcp', 'Net']

        df = pd.DataFrame(data=scores, index=idx, columns=all_cols)
        for col in df.columns:
            df[col] = df[col].astype(str)
        df.loc['Par'] = df.loc['Par'].replace(['0'],'')
        df.loc['Hdcp'] = df.loc['Hdcp'].replace(['0'],'')
        return df


    def calc_handicap(self, player, course):
        allfiles = [f for f in listdir(self.pkl_path) if isfile(join(self.pkl_path, f))]
        golfers = []
        for pf in allfiles:
            with open('{}'.format(self.pkl_path) + pf, 'rb') as f:
                golfers.append(pickle.load(f))

        names = [golfer.name for golfer in golfers]
        dct = dict(zip(names, golfers))

        golfer = dct[player]

        course_dct = self.courses[course]
        course_par = sum(course_dct['par'])
        golfer_tees = golfer.tees[course]
        rating, slope = course_dct['tees'][golfer_tees]
        calc_hdcp = round((golfer.hdcp * (slope / 113)) + (rating - course_par))

        return calc_hdcp


    def show_handicaps(self, course):
        allfiles = [f for f in listdir(self.pkl_path) if isfile(join(self.pkl_path, f))]
        golfers = []
        for pf in allfiles:
            with open('{}'.format(self.pkl_path) + pf, 'rb') as f:
                golfers.append(pickle.load(f))

        names = [golfer.name for golfer in golfers]
        hdcps = [golfer.hdcp for golfer in golfers]
        tees = [golfer.tees[course] for golfer in golfers]
        course_hdcps = [self.calc_handicap(name, course) for name in names]
        results = list(zip(names, tees, hdcps, course_hdcps))
        sorted_results = sorted(results, key=lambda x: x[0])

        df_hdcps = pd.DataFrame(sorted_results, columns=['Player', 'Tee', 'Handicap', 'Course Handicap'])

        return df_hdcps


if __name__ == '__main__':
    # past_locations_map()
    golf = PlayGolf()

    print('Adding players...')
    tees = {
        'The Oconee': 'Two',
        'The National - Ridge/Bluff': 'One',
        'The National - Bluff/Cove': 'Two',
        'The National - Cove/Ridge': 'One',
        'The Preserve': 'One',
        'The Landing': 'One',
        'Great Waters': 'One'
    }

    golf.add_player('Stuart King', 3, tees, True)

    print("Adding Stuart's scores...")
    for idx, _ in enumerate(range(18)):
        golf.add_score('Stuart King', 'The Oconee', idx+1, np.random.randint(3,7))
    for idx, _ in enumerate(range(18)):
        golf.add_score('Stuart King', 'The Preserve', idx+1, np.random.randint(3,7))
