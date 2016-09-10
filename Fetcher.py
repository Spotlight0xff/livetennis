import datetime
import requests
from lxml import etree
from enum import Enum
import logging

import Utils
import Crypt
import UniqueMatch


logger = logging.getLogger('root')





class ContentType(Enum):
    plain = 1
    obfuscated = 2
    encrypted = 3




host = 'http://ws.protennislive.com/LiveScoreSystem'
URLS = {
        'tournaments': (ContentType.plain, host + '/M/Long/GetTournaments.aspx?lang={}', 1),
        'livematches_tournament': (ContentType.obfuscated, host + '/M/Short/GetLiveMatchesPerTournament.aspx?year={}&id={}', 2),
        'livematches': (ContentType.encrypted, host + '/F/Short/GetLiveMatchesCrypt.aspx?y={}&wkno={}&e={}', 3), 
        'matchstats': (ContentType.obfuscated, host + '/M/Short/GetMatchStats.aspx?year={}&id={}&mId={}', 3),
        'matchstats_crypt': (ContentType.encrypted, host + '/M/Short/GetMatchStats_VCrypt.aspx?year={}&id={}&mId={}', 3),
        }

YEAR = datetime.date.today().year
WEEKNR = datetime.date.today().isocalendar()[1]


def getContent(want, *args):
    req = URLS[want]
    if len(args) != req[2]:
        raise Exception('Provided arguments do not match!')

    url = req[1].format(*args) if len(args) > 0 else req[1]
    r = requests.get(url)

    if req[0] is ContentType.obfuscated:
        logger.debug('request obfuscated URL \'{}\''.format(url) )
        return Crypt.decrypt_apk(r.content)
    elif req[0] is ContentType.encrypted:
        logger.debug('request encrypted URL \'{}\''.format(url) )
        return Crypt.decrypt_flash(r.content)
    else:
        logger.debug('request plain URL \'{}\''.format(url) )
        return r.content



def getTournaments(lang = 'en'):
    """returns listed Tournaments (live or not)"""
    content = getContent('tournaments', 'en')
    logger.trace(content)
    tournaments = etree.XML(content)
    for t in tournaments:
        name = t.get('name')
        id = t.get('id')
        year = t.get('year')
        gender = t.get('gen') # M or F
        group = t.get('group') # ??
        begin_date = t.get('bDate')
        end_date = t.get('eDate')
        yield {
            'name': name,
            'id': id,
            'year': year,
            'gender': gender,
            'group': group,
            'begin_date': begin_date,
            'end_date': end_date}

def getLiveMatches(t_id):
    content = getContent('livematches', YEAR, WEEKNR, t_id)
    logger.trace(content)
    root = etree.XML(content)
    if not root.findall( 'Tournament' ):
        return None

    tournament = root.find( 'Tournament' )
    for match in tournament:
        match_id = match.get("mId")
        logger.debug('Found Live Match: ' + match_id)
        yield match

def getMatchStats(t_id, m_id):
    content = getContent('matchstats', YEAR, t_id, m_id)
    logger.trace(content)
    root = etree.XML(content.encode('utf-8'))
    match = root.find('Tournament').find('Match')
    model = MatchModel.MatchModel()
    model.fromCsv(match.get('csv'))

def getAllLiveMatches():
    tournaments = getTournaments()
    # iterate through all tournaments
    for tournament in tournaments:
        # and get the live matches
        for match in getLiveMatches(tournament['id']):
            yield (UniqueMatch.UniqueMatch(tournament['year'], tournament['id'], match.get('mId')), match)
