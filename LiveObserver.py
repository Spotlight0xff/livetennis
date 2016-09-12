import logging
import csv
import os.path
import pymysql

import Utils
import Crypt
import FeedUpdater
import DatabaseConnection

logger = logging.getLogger('root')

class LiveObserver:
    """An object of this class will handle the updating of live match records.
    This class roughly follows the observer pattern.
    """
    map_writer = {}
    last_update = {}
    counter = {}
    csvdir = 'data'

    def __init__(self, csvdir, db_host, db_port, db_user, db_password, db_name):
        self.csvdir = csvdir
        self.db_conn = DatabaseConnection.DatabaseConnection(db_host, db_port, db_user, db_password, db_name)


    def crossRefMatch(self, uniq_match, matches):
        """Match one record in the provided arguments
        Roughly tries to find (year, tournament_id, match_id) in matches
        """
        for u_m, m in matches:
            if u_m == uniq_match:
                return m
        return None

    def new(self, uniq_match, matches, tournaments):
        """gets called when a match goes live"""
        matchId = uniq_match.getMatch()
        tId = uniq_match.getTournament()
        logger.info('Match {} just went live.'.format(matchId))
        unique_name = uniq_match.getName()
        logger.debug('Unique name: ' + unique_name)

        self.map_writer[unique_name] = [self.csv_write, self.update_db]
        self.counter[unique_name] = 0
        self.createMatchRecord(uniq_match, matches, tournaments)


    def createMatchRecord(self, uniq_match, matches, tournaments):
        """Insert new row into database (match record)"""
        if not self.db_conn.success:
            return # no db support (failed to connect probably)

        match = self.crossRefMatch(uniq_match, matches)
        result = self.db_conn.selectRow('matches', {
                                            'year': uniq_match.getYear(),
                                            'match_id': matchId,
                                            'tournament_id': tId})
        if not result: # need to create new record
            logger.info('Create new match record for '+unique_name)
            t_name = ''
            t_cat = ''
            for t in tournaments:
                if t.get('year') == uniq_match.getYear() and t.get('id') == tId:
                    t_name = t.get('name')
                    t_cat = t.get('group')
                    break

            res_ins = self.db_conn.insertRow('matches', (
                0,
                uniq_match.getYear(),
                tId,
                matchId,
                unique_name,
                t_name, # tournament name
                t_cat, # tournament category
                match.get('state'), # status
                '0', # is doubles
                match.get('isQuals'),
                match.get('numSets'),
                '{} {}'.format(match.get('nAF'), match.get('nAL')),
                '{} {}'.format(match.get('nBF'), match.get('nBL')),
                match.get('rnd'), # round
                match.get('winner'), # not sure if this is correct...
                ''.join([match.get(s) for s in ['s{}{}'.format(num,side) for side in ['A','B'] for num in range(1,6)]]),
                '', # first server
                match.get('ts'), # start time
                match.get('mt'), # match time
                '', # retirement
                ))
            if not res_ins:
                logger.error('Could not create match record for '+unique_name)
        else: # already listed (maybe check if set to live..?)
            True




    def csv_write(self, uniq_match, match):
        """Write live match details into csv-file"""
        unique_name = uniq_match.getName()
        if not os.path.exists(self.csvdir):
            os.makedirs(self.csvdir)
        csv_file = os.path.join(self.csvdir,unique_name+'.csv')
        new = False # need to add header @ top
        if not os.path.isfile(csv_file):
            new = True
        with open(csv_file, 'a+', newline='') as f:
            writer = csv.writer(f)
            if new:
                writer.writerow(FeedUpdater.getMatchHeader())
            # TODO  read counter from csv-file and use it
            self.counter[unique_name] += 1
            writer.writerow(FeedUpdater.getMatchRow(match, self.counter[unique_name]))


    def update_db(self, uniq_match, match):
        """Update live match details in database"""
        if not self.db_conn.success:
            return # no db support (failed to connect probably)

        unique_name = uniq_match.getName()
        logger.debug('Write updates to database for \'{}\''.format(unique_name))
        if self.db_conn.existsTable(unique_name):
            result = self.db_conn.insertRow(unique_name, FeedUpdater.getMatchRow(match, 0))
            if not result or result < 1:
                logger.error('Failed to insert data into table {}'.format(unique_name))
                return
            logger.debug('Inserted data into ' + unique_name)
        else:
            result = self.db_conn.createTable(unique_name, FeedUpdater.getMatchHeader())
            self.db_conn.cache_tableexists[unique_name] = True # add table name to cache
            if not result:
                logger.error('Could not create new table for \'{}\''.format(unique_name))
                return # handle this case!
            else:
                result_ins = self.db_conn.insertRow(unique_name, FeedUpdater.getMatchRow(match, 0))
                if not result_ins or result_ins < 1:
                    logger.error('Failed to insert data into new table {}'.format(unique_name))
                    return
            logger.debug('Inserted data into new ' + unique_name)




    def completed(self, uniq_match, matches, tournaments):
        unique_name = uniq_match.getName()
        logger.info('{} got completed.'.format(unique_name))
        del self.counter[unique_name]
        del self.map_writer[unique_name]

    def update(self, uniq_match, match):
        unique_name = uniq_match.getName()
        row = FeedUpdater.getMatchRow(match,0)
        if unique_name in self.last_update:
            if row[:-1] == self.last_update[unique_name][:-1]:
                logger.debug('Match {} did not change!'.format(unique_name))
                return
            else:
                logger.debug('Match {} did change!'.format(unique_name))
        self.last_update[unique_name] = row
        funcs = self.map_writer[unique_name]
        for func in funcs:
            func(uniq_match, match)
        logger.info('Match {} got updated.'.format(match.get('mId')))
