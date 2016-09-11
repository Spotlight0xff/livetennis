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
    counter = {}
    csvdir = 'data'

    def __init__(self, csvdir, db_host, db_port, db_user, db_password, db_name):
        self.csvdir = csvdir
        self.db_conn = DatabaseConnection.DatabaseConnection(db_host, db_port, db_user, db_password, db_name)


    def crossRefMatch(self, uniq_match, matches):
        """Match one record in the provided arguments
        Roughly tries to find (year, tournament_id, match_id) in matches
        """
        for t_id, m in matches:
            if m.get('mId') == uniq_match.match() and t_id == uniq_match.tournament():
                return (t_id, m)
        return (0, None)

    def new(self, uniq_match, matches):
        """gets called when a match goes live"""
        matchId = uniq_match.getMatch()
        tId = uniq_match.getTournament()
        logger.info('Match {} just went live.'.format(matchId))
        unique_name = uniq_match.getName()
        logger.debug('Unique name: ' + unique_name)

        self.map_writer[unique_name] = [self.csv_write, self.update_db]
        self.counter[unique_name] = 0


    def csv_write(self, uniq_match, match):
        """Write live match details into csv-file"""
        unique_name = uniq_match.getName()
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
            logger.error('fail')
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




    def completed(self, uniq_match, matches):
        unique_name = uniq_match.getName()
        logger.info('{} got completed.'.format(unique_name))
        del self.counter[unique_name]
        del self.map_writer[unique_name]

    def update(self, uniq_match, match):
        logger.info('Match {} got updated.'.format(match.get('mId')))
        unique_name = uniq_match.getName()
        funcs = self.map_writer[unique_name]
        for func in funcs:
            func(uniq_match, match)
