import subprocess
import re
import os
import sys
import signal
import random

"""

ABOUT:
This is a simple script to run n games x times with both teams running our team class. At the end of each game of n rounds, the winners pickle file is written to table.pickle.
Each agent will load table.pickle at the start of a round and if no winner is determined (tie) no changes are saved to table.pickle.
This ensures we train our Qtable with the best weights. Kind of like generational learning.

USAGE:
Run this file with normal python usage.
ARGS:
    -n [int] - pass in -n followed by a number of matches to run per game. (Must be greater than 1)
    -g [int | inf] - pass in -g followed by the number of games to run. For an infinite loop of games pass inf.
    -r - when passed in will generate random maps each game.
    -vb - play blue = myTeam, red = baselineTeam
EXAMPLES:
    Run 2 games with 2 matches each:
        python3 trainer.py -n 2 -g 2
    Run infinite games with 51 rounds each:
        python3 trainer.py -n 51 -g inf

NOTE:
    To exit midway use CTRL+c if not be sure to delete the files named _red_table.pickle and _blue_table.pickle

"""

def runTournament(n, x, i, rand=False, vs_baseline=False):
    args = ['python3', 'capture.py', '-b', 'myTeam', '-n', str(n), '--delay-step=0.000001', '-Q', '-l', 'RANDOM6']
    if not vs_baseline:
        args.append('-r')
        args.append('myTeam')
    if rand:
        args.append('-l')
        args.append('RANDOM'+str(int(random.random()*100000)))

    proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    determine_winner(proc.stdout, x, i, vs_baseline)
    proc.stdout.close()
    proc.wait()

def determine_winner(output, xx, ii, vs_baseline=False):
    red = None; blue = None
    for i, s in enumerate(reversed(list(iter(output.readline, b'')))):
        if i==3:
            x=s.decode("utf-8")
            t = re.search('[\d]+/[\d]+', x)
            if t:
                blue = t.group(0).split('/')[0]
        elif i==4:
            x=s.decode("utf-8")
            t = re.search('[\d]+/[\d]+', x)
            if t:
                red = t.group(0).split('/')[0]
        elif i>4:
            break
    if blue is not None and red is not None:
        winner = "blue" if blue > red else "red" if red > blue else None
        print('Game '+str(ii)+'/'+str(xx)+' Winner: '+str(winner))
        if winner is not None and (not vs_baseline or winner == "blue"):
            os.replace("./"+winner+"_table.pickle", "./table.pickle")

def cleanUp():
    print("\nCleaning up...", end =" ")
    if os.path.isfile('_red_table.pickle'):
        os.remove('_red_table.pickle')
    if os.path.isfile('_blue_table.pickle'):
        os.remove('_blue_table.pickle')
    if os.path.isfile('red_table.pickle'):
        os.remove('red_table.pickle')
    if os.path.isfile('blue_table.pickle'):
        os.remove('blue_table.pickle')
    print('Done!')

def prepare():
    n=51; x=1; argc = len(sys.argv); rand=False; vs_baseline=False
    for i, arg in enumerate(sys.argv):
        if argc >= i+1:
            if arg == '-n': # number of rounds per game
                n = int(sys.argv[i+1])
            elif arg == '-g': # number of games to run
                if sys.argv[i+1] == 'inf':
                    x = float('inf')
                else:
                    x = int(sys.argv[i+1])
            elif arg == '-r': # randomly generate maps
                rand = True
            elif arg == '-vb': # play 1 team vs baseline
                vs_baseline = True
    i=0
    while x > i:
        runTournament(n, x, i+1, rand, vs_baseline)
        i+=1
    cleanUp()

def signal_handler(sig, frame):
    cleanUp()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)


prepare()