#!/usr/bin/env python3

from collections import OrderedDict
import logging
logger = logging.getLogger('root')

def getMatchSet(match):
    set = 0
    if match.get('s5A') != '' or match.get('s5B') != '':
        set = 5
    elif match.get('s4A') != '' or match.get('s4B') != '':
        set = 4
    elif match.get('s3A') != '' or match.get('s3B') != '':
        set = 3
    elif match.get('s2A') != '' or match.get('s2B') != '':
        set = 2
    elif match.get('s1A') != '' or match.get('s1B') != '':
        set = 1
    return set


def getRetirement(match):
    msg = match.get('msg')
    # msg will look like this:
    # {11|player1} {20}
    # this means, that player 1 won (id 11) by retirement (20)
    # used IDs: see decompiled apk: Constants.java: matchMessages
    if '{20}' in msg:
        return True
    return False

def isDoubles(match):
    if match.get('nA2F') and match.get('nA2L') and match.get('nB2F') and match.get('nB2L'):
        return True
    else:
        return False

def getMatchRecord(uniq_match, match, tournaments, initial):
    unique_name = uniq_match.getName()
    t_name = ''
    t_cat = ''
    for t in tournaments:
        if t.get('year') == uniq_match.getYear() and t.get('id') == uniq_match.getTournament():
            t_name = t.get('name')
            t_cat = t.get('group')
            break
    record = OrderedDict()
    if initial:
        record['id'] = 0 # will get autoincremented anyway
    record['year'] = uniq_match.getYear()
    record['tournament_id'] = uniq_match.getTournament()
    record['match_id'] = uniq_match.getMatch()
    record['table_name'] = unique_name
    record['t_name'] = t_name
    record['t_category'] = t_cat
    record['status'] = match.get('state')
    record['is_doubles'] = '1' if isDoubles(match) else '0'
    record['is_quals'] = match.get('isQuals')
    record['num_sets'] = match.get('numSets')
    record['player1'] = '{} {}'.format(match.get('nAF'), match.get('nAL'))
    record['player2'] = '{} {}'.format(match.get('nBF'), match.get('nBL'))
    record['round'] = match.get('rnd')
    record['winner'] = match.get('winner')
    record['score'] = ''.join([match.get(s) for s in ['s{}{}'.format(num,side) for side in ['A','B'] for num in range(1,6)]])
    # this one is tricky:
    # we get this correct only if this method gets called directly at the first start
    if initial:
        record['first_server'] =  match.get('serve')
    record['start_ts'] = match.get('ts')
    record['matchtime'] = match.get('mt')
    record['retirement'] = '1' if getRetirement(match) else '0'
    return record

def getMatchRow(match, counter):
    set = getMatchSet(match)
    return (
            counter,
            match.get('serve'),
            match.get('winner'),
            match.get('ptA')+match.get('ptB'),
            set,
            match.get('s{}A'.format(set)) + match.get('s{}B'.format(set)),
            match.get('state'),
            match.get('mt'),
            )

def getMatchHeader():
    return ("Counter", "Server", "Scored", "Gamescore", "Set", "Setscore", "State", "Timestamp")
