#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import signal
import sys
from time import sleep
import Utils
import argparse
import logging


import log
logger = log.setup_custom_logger('root')
logger.debug('main message')


import Fetcher
import Crypt
import LiveObserver


interval = 10


def main():
    global interval
    logger.info('Starting program')
    live_matches = []
    old_live_matches = []
    observer = LiveObserver.LiveObserver()
    while True:
        old_live_matches = live_matches
        logger.info('Retrieve list of live matches')
        live_matches = list(Fetcher.getAllLiveMatches())
        logger.debug('Found {} live matches'.format(len(live_matches)))
        old_matches_id = [uniq_match for uniq_match, match in old_live_matches]
        matches_id = [uniq_match for uniq_match, match in live_matches]
        # print('Old Live Matches: {}'.format(','.join(old_matches_id)))
        # print('Live Matches: {}'.format(','.join(live_matches)))

        # iterate through now-completed matches
        # completed = set(old_matches_id) - set(matches_id)
        completed = [x for x in old_matches_id if x not in matches_id] #set(matches_id) - set(old_matches_id)
        for uniq_match in completed:
            observer.completed(uniq_match, old_live_matches) # id

        # iterate through matches which went live just now
        new_live = [x for x in matches_id if x not in old_matches_id] #set(matches_id) - set(old_matches_id)
        if len(new_live):
            logger.info('{} match{} just went live.'.format(len(new_live), 'es' if len(new_live)>1 else ''))
        for uniq_match in new_live:
            observer.new(uniq_match, live_matches)

        # iterate through all live matches
        for uniq_match, match in live_matches:
            observer.update(uniq_match, match)

        logger.debug('Wait {} seconds until next run.'.format(interval))
        # sleep(interval)


def parseArgs():
    global verbose
    parser = argparse.ArgumentParser(description = 'Export Live Tennis Data')
    parser.add_argument('-d', '--csvdir', action='store',
            help='Path to output directory (.csv files)')
    parser.add_argument('-c', '--config', action='store',
            help='Path to configuration file')
    parser.add_argument("-v", "--verbose", action="count",
            help='Increase output verbosity (up to -vv)')
    parser.add_argument('-i', '--interval', action='store',
            help='Interval to request live updates')

    args = parser.parse_args()
    if args.verbose == 0:
        logger.setLevel(logging.INFO)
    elif args.verbose == 1:
        logger.setLevel(logging.DEBUG)
    elif args.verbose == 2:
        logger.setLevel(5) # TRACE

    

if __name__ == '__main__':
    parseArgs()
    main()

