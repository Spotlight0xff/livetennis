#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import signal
import sys
from time import sleep
import argparse
import logging
import configparser
import os.path


import log
logger = log.setup_custom_logger('root')
logger.debug('main message')


import Utils
import Fetcher
import Crypt
import LiveObserver


interval = 10
db_host = ''
db_port = ''
db_user = ''
db_password = ''
db_name = ''
filter = []


def main():
    global interval, csvdir, db_host, db_port, db_user, db_password, db_name, filter
    logger.info('Starting program')
    live_matches = []
    old_live_matches = []
    observer = LiveObserver.LiveObserver(csvdir, db_host, db_port, db_user, db_password, db_name)
    while True:
        old_live_matches = live_matches
        logger.info('Retrieve list of live matches')
        tournaments = list(Fetcher.getTournaments(filter=filter))
        live_matches = list(Fetcher.getAllLiveMatches(tournaments))
        logger.debug('Found {} live matches'.format(len(live_matches)))
        old_matches_id = [uniq_match for uniq_match, match in old_live_matches]
        matches_id = [uniq_match for uniq_match, match in live_matches]
        # print('Old Live Matches: {}'.format(','.join(old_matches_id)))
        # print('Live Matches: {}'.format(','.join(live_matches)))

        # iterate through now-completed matches
        # completed = set(old_matches_id) - set(matches_id)
        completed = [x for x in old_matches_id if x not in matches_id] #set(matches_id) - set(old_matches_id)
        for uniq_match in completed:
            observer.completed(uniq_match, old_live_matches, tournaments) # id

        # iterate through matches which went live just now
        new_live = [x for x in matches_id if x not in old_matches_id] #set(matches_id) - set(old_matches_id)
        if len(new_live):
            logger.info('{} match{} just went live.'.format(len(new_live), 'es' if len(new_live)>1 else ''))
        for uniq_match in new_live:
            observer.new(uniq_match, live_matches, tournaments)

        # iterate through all live matches
        for uniq_match, match in live_matches:
            observer.update(uniq_match, match)

        logger.debug('Wait {} seconds until next run.'.format(interval))
        sleep(interval)



def printTournaments():
    tournaments = list(Fetcher.getTournaments(filter=None))
    t2 = tournaments
    max_len_id = 0
    max_len_name = 0
    max_len_cat = 0
    max_len_date1 = 0
    max_len_date2 = 0
    for t in tournaments:
        max_len_id = max(max_len_id, len(t['id']))
        max_len_name = max(max_len_name, len(t['name']))
        max_len_cat = max(max_len_cat, len(t['group']))
        max_len_date1 = max(max_len_date1, len(t['begin_date']))
        max_len_date2 = max(max_len_date2, len(t['end_date']))

    for t in tournaments:
        print("ID: {0:>{f_max}} ".format(t['id'], f_max = max_len_id) +
                "Name: {:<{f_max}} ".format(t['name'], f_max=max_len_name) +
                "Category: {:>{f_max}} ".format(t['group'], f_max=max_len_cat) +
                'Gender: {}, '.format(t['gender'])+
                'Year: {}, '.format(t['year'])+
                'Date: {:>{f_max1}} to {:>{f_max2}}'.format( t['begin_date'], t['end_date'], f_max1 = max_len_date1, f_max2 = max_len_date2))

def parseArgs():
    global interval, csvdir, db_host, db_port, db_user, db_password, db_name, filter
    parser = argparse.ArgumentParser(description = 'Export Live Tennis Data')
    parser.add_argument('-d', '--csvdir', action='store',
            help='Path to output directory (.csv files)', default='data')
    parser.add_argument('-c', '--config', action='store',
            help='Path to configuration file', default='config.ini')
    parser.add_argument("-v", "--verbose", action="count",
            help='Increase output verbosity (up to -vv)')
    parser.add_argument('-i', '--interval', action='store',
            help='Interval to request live updates', default=10)
    parser.add_argument('-l', '--list-tournaments', action='store_true',
            help='List available tournaments', default=False)

    args  = parser.parse_args()
    if not args.verbose:
        logger.setLevel(logging.INFO)
    elif args.verbose == 1:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(5) # TRACE

    if args.list_tournaments:
        printTournaments()
        sys.exit(0)

    csvdir = args.csvdir
    interval = args.interval

    logger.debug('Trying to read configfile \'{}\''.format(args.config))
    if os.path.isfile(args.config):
        config = configparser.ConfigParser()
        config.read(args.config)
        if 'Database' in config.sections():
            db_cfg = config['Database']
            db_host = db_cfg.get('Host', 'localhost')
            db_port = int(db_cfg.get('Port', '3306'))
            db_user = db_cfg.get('User', Utils.getDefaultUser())
            db_password = db_cfg.get('Password', '')
            db_name = db_cfg.get('Name', 'livetennis')
        else:
            logger.error('Specify an section called \'Database\'')

        if 'Filter' in config.sections():
            cfg_filter = config['Filter']
            whitelist = cfg_filter.get('Whitelist', '')
            if not whitelist:
                logger.warn('No whitelist specified, fetching matches from all tournaments')
            else:
                filter = whitelist.split(',')
                logger.info("Whitelisted following tournaments:\n{}".format("\n".join(filter)))

            doubles = int(cfg_filter.get('Doubles', '0'))
            # TODO make this happen
            if doubles:
                logger.info('Fetch doubles matches also')
            else:
                logger.info('Fetch only single matches')
        else:
            logger.warn('No filter specified, fetching all matches from all tournaments.')


    else:
        logger.error('You need to provide an configfile for database connection')
    

if __name__ == '__main__':
    parseArgs()
    main()

