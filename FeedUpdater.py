#!/usr/bin/env python3

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
    return ('Counter', 'Server', 'Scored', 'Game score', 'Set', 'Set score', 'State', 'Timestamp')
