import pymysql
import logging

logger = logging.getLogger('root')

class DatabaseConnection:
    connection = None
    success = True # optimism
    cache_tableexists = {}
    def __init__(self, db_host, db_port, db_user, db_password, db_name):
        logger.debug('Trying to connect to {}@{}:{}/{}'.format(db_user, db_host, db_port, db_name))
        self.connection = pymysql.connect(host=db_host,
                                     port=db_port,
                                     user=db_user,
                                     password=db_password,
                                     db=db_name,
                                     charset='utf8mb4',
                                     cursorclass=pymysql.cursors.DictCursor)
        if not self.connection:
            logger.error('Failed to connect to database')
            self.success = False
        else:
            logger.debug('Connection to database successful')
            self.success = True

    def insertRow(self, table_name, data):
        """Insert a row into table `table_name` with `data` as values.
        Return True on success and False on failure."""
        cursor = self.connection.cursor()
        sql = 'INSERT INTO `{}` VALUES('.format(table_name)
        sql += ','.join("%s" for i in range(0,len(data)))
        sql += ')'
        logger.trace(sql)
        params = data
        num_affected_rows = 0

        try:
            num_affected_rows = cursor.execute(sql, data)
            self.connection.commit()
        except pymysql.Error as e:
            # show exact error iff debug level is set
            if logger.getEffectiveLevel() <= logging.DEBUG:
                logger.error('inserting into db failed: '.format(table_name) + str(e))
            return False
        return num_affected_rows == 1

    def existsTable(self, table_name):
        """Check if a table exists in the database.
        Use basic caching, invalidate using accessing self.cache_tableexists[table_name]"""
        if table_name in self.cache_tableexists:
            logger.debug('cache hit for '+table_name)
            return self.cache_tableexists[table_name]
        cursor = self.connection.cursor()
        logger.debug('cache miss for '+table_name)
        sql = 'SHOW TABLES LIKE %s'
        num_affected_rows = 0
        try:
            num_affected_rows = cursor.execute(sql, (table_name,))
        except pymysql.Error as e:
            if logger.getEffectiveLevel() <= logging.DEBUG:
                logger.error('check if table exists failed: '.format(table_name) + str(e))
            return False
        self.cache_tableexists[table_name] = num_affected_rows == 1
        return self.cache_tableexists[table_name]


    def createTable(self, table_name, names):
        """Create a new table called `table_name` with the provided names as columns.
        The first name is asumed to be a primary auto incremented key (integer therefore)."""
        schema = []
        # first name is primary key (integer) and auto incremented
        schema.append('`{}` INT(11) PRIMARY KEY AUTO_INCREMENT'.format(names[0]))
        schema.extend(['`{}` VARCHAR(30)'.format(name) for name in names[1:]])
        sql = "CREATE TABLE " + table_name + " ("
        sql += ", ".join(schema)
        sql += ")"
        with self.connection.cursor() as cursor:
            try:
                rows = cursor.execute(sql)
            except pymysql.Error as e:
                # show exact error iff debug level is set
                if logger.getEffectiveLevel() <= logging.DEBUG:
                    logger.error('creating table {} failed: '.format(table_name) + str(e))
                return False
            return True
