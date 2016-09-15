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
    old_match = {}
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
        self.updateMatchRecord(uniq_match, matches, tournaments, True)


    def updateMatchRecord(self, uniq_match, matches, tournaments, initial = True):
        """Insert/Update match record in the db"""
        if not self.db_conn.success:
            return # no db support (failed to connect probably)

        unique_name = uniq_match.getName()
        match = self.crossRefMatch(uniq_match, matches)
        select_cond = {
                        'year': uniq_match.getYear(),
                        'match_id': uniq_match.getMatch(),
                        'tournament_id': uniq_match.getTournament()
                      }
        result = self.db_conn.selectRow('matches', select_cond)
        if not result: # need to create new record
            match_record = FeedUpdater.getMatchRecord(uniq_match, match, tournaments, True)
            logger.info('Create new match record for '+unique_name)
            res_ins = self.db_conn.insertRow('matches', tuple(match_record.values()))
            if not res_ins:
                logger.error('Could not create match record for '+unique_name)
        else: # already listed (maybe check if set to live..?)
            match_record = FeedUpdater.getMatchRecord(uniq_match, match, tournaments, False)
            res_update = self.db_conn.updateRow('matches', select_cond, match_record)
            if not res_update:
                logger.error('Could not update match record for ' + unique_name)




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
            old_match = self.old_match[unique_name] if unique_name in self.old_match else None
            writer.writerow(FeedUpdater.getMatchRow(match, old_match, self.counter[unique_name]))


    def update_db(self, uniq_match, match):
        """Update live match details in database"""
        if not self.db_conn.success:
            return # no db support (failed to connect probably)

        unique_name = uniq_match.getName()
        old_match = self.old_match[unique_name] if unique_name in self.old_match else None

        logger.debug('Write updates to database for \'{}\''.format(unique_name))
        if self.db_conn.existsTable(unique_name):
            result = self.db_conn.insertRow(unique_name, FeedUpdater.getMatchRow(match, old_match, 0))
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
                result_ins = self.db_conn.insertRow(unique_name, FeedUpdater.getMatchRow(match, old_match, 0))
                if not result_ins or result_ins < 1:
                    logger.error('Failed to insert data into new table {}'.format(unique_name))
                    return
            logger.debug('Inserted data into new ' + unique_name)




    def completed(self, uniq_match, matches, tournaments):
        unique_name = uniq_match.getName()

        # update match record (final update)
        match = self.crossRefMatch(uniq_match, matches)
        match_record = FeedUpdater.getMatchRecord(uniq_match, match, tournaments, False)
        select_cond = {
                        'year': uniq_match.getYear(),
                        'match_id': uniq_match.getMatch(),
                        'tournament_id': uniq_match.getTournament()
                      }
        result = self.db_conn.updateRow('matches', select_cond, match_record)
        if not result:
            logger.error('Error updating final match record for {}'.format(uniq_name))

        logger.info('{} got completed.'.format(unique_name))
        del self.counter[unique_name]
        del self.map_writer[unique_name]

    def update(self, uniq_match, match):
        unique_name = uniq_match.getName()
        if unique_name in self.last_update:
            if row[:-1] == self.last_update[unique_name][:-1]:
                logger.debug('Match {} did not change!'.format(unique_name))
                return
            else:
                logger.debug('Match {} did change!'.format(unique_name))
                if unique_name in self.old_match:
                    # logger.warn("ptA:{} -> ptA:{}".format(self.old_match[unique_name].get('ptA'), match.get('ptA')))
                    # logger.warn("ptB:{} -> ptB:{}".format(self.old_match[unique_name].get('ptA'), match.get('ptB')))
                    # winner = FeedUpdater.calculateWinner(self.old_match[unique_name], match)

        old_match = self.old_match[unique_name] if unique_name in self.old_match else None
        row = FeedUpdater.getMatchRow(match, old_match, 0)


        self.last_update[unique_name] = row
        self.old_match[unique_name] = match
        funcs = self.map_writer[unique_name]
        for func in funcs:
            func(uniq_match, match)
        logger.info('Match {} got updated.'.format(match.get('mId')))
