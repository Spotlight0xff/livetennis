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

def calculateWinner(old_match, match):
    if match.get('ptA') == 'A': # player a has advantage
        return 'A'
    if match.get('ptB') == 'A': # player b has advantage
        return 'B'

    # player A: 40 -> 40
    # player B: A -> 40
    if old_match.get('ptA') == '40' and match.get('ptA') == '40' and old_match.get('ptB') == 'A' and match.get('ptB') == '40':
        return 'A'

    # player A: A -> 40
    # player B: 40 -> 40
    if old_match.get('ptA') == 'A' and match.get('ptA') == '40' and old_match.get('ptB') == '40' and match.get('ptB') == '40':
        return 'B'

    if match.get('ptA') == '' or match.get('ptB') == '':
        return '0'

    old_ptA = int(old_match.get('ptA'))
    old_ptB = int(old_match.get('ptB'))
    new_ptA = int(match.get('ptA'))
    new_ptB = int(match.get('ptB'))
    if new_ptA > old_ptA:
        return 'A'

    if new_ptB > old_ptB:
        return 'B'

    if new_ptA == 0 and new_ptB == 0:
        return '0'

    # should not happen
    logger.warn('Both scores increased??: A: {} -> {}, B: {} -> {}'.format(old_match.get('ptA'), match.get('ptA'), old_match.get('ptB'), match.get('ptB')))
    return '?'

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
    record['id1'] = match.get('idA')
    record['id2'] = match.get('idB')
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

def getMatchRow(match, old_match, counter):
    set = getMatchSet(match)
    return (
            counter,
            match.get('serve'),
            calculateWinner(match, old_match) if old_match is not None else '',
            match.get('ptA')+match.get('ptB'),
            set,
            match.get('s{}A'.format(set)) + match.get('s{}B'.format(set)),
            match.get('state'),
            match.get('mt'),
            )

def getMatchHeader():
    return ("Counter", "Server", "Scored", "Gamescore", "Set", "Setscore", "State", "Timestamp")
