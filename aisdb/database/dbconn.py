''' exposes the SQLite DB connection. some postgres code is also included for legacy support '''

import os

import aiosqlite
import sqlite3
if (sqlite3.sqlite_version_info[0] < 3
        or (sqlite3.sqlite_version_info[0] <= 3
            and sqlite3.sqlite_version_info[1] < 35)):
    import pysqlite3 as sqlite3
import warnings

_coarsetype_rows = [
    (20, 'Wing in ground craft'),
    (21, 'Wing in ground craft, hazardous category A'),
    (22, 'Wing in ground craft, hazardous category B'),
    (23, 'Wing in ground craft, hazardous category C'),
    (24, 'Wing in ground craft, hazardous category D'),
    (25, 'Wing in ground craft'),
    (26, 'Wing in ground craft'),
    (27, 'Wing in ground craft'),
    (28, 'Wing in ground craft'),
    (29, 'Wing in ground craft'),
    (30, 'Fishing'),
    (31, 'Towing'),
    (32, 'Towing - length >200m or breadth >25m'),
    (33, 'Engaged in dredging or underwater operations'),
    (34, 'Engaged in diving operations'),
    (35, 'Engaged in military operations'),
    (36, 'Sailing'),
    (37, 'Pleasure craft'),
    (38, 'Reserved for future use'),
    (39, 'Reserved for future use'),
    (40, 'High speed craft'),
    (41, 'High speed craft, hazardous category A'),
    (42, 'High speed craft, hazardous category B'),
    (43, 'High speed craft, hazardous category C'),
    (44, 'High speed craft, hazardous category D'),
    (45, 'High speed craft'),
    (46, 'High speed craft'),
    (47, 'High speed craft'),
    (48, 'High speed craft'),
    (49, 'High speed craft'),
    (50, 'Pilot vessel'),
    (51, 'Search and rescue vessels'),
    (52, 'Tugs'),
    (53, 'Port tenders'),
    (54, 'Vessels with anti-pollution facilities or equipment'),
    (55, 'Law enforcement vessels'),
    (56, 'Spare for assignments to local vessels'),
    (57, 'Spare for assignments to local vessels'),
    (58, 'Medical transports (1949 Geneva convention)'),
    (59, 'Ships and aircraft of States not parties to an armed conflict'),
    (60, 'Passenger ships'),
    (61, 'Passenger ships, hazardous category A'),
    (62, 'Passenger ships, hazardous category B'),
    (63, 'Passenger ships, hazardous category C'),
    (64, 'Passenger ships, hazardous category D'),
    (65, 'Passenger ships'),
    (66, 'Passenger ships'),
    (67, 'Passenger ships'),
    (68, 'Passenger ships'),
    (69, 'Passenger ships'),
    (70, 'Cargo ships'),
    (71, 'Cargo ships, hazardous category A'),
    (72, 'Cargo ships, hazardous category B'),
    (73, 'Cargo ships, hazardous category C'),
    (74, 'Cargo ships, hazardous category D'),
    (75, 'Cargo ships'),
    (76, 'Cargo ships'),
    (77, 'Cargo ships'),
    (78, 'Cargo ships'),
    (79, 'Cargo ships'),
    (80, 'Tankers'),
    (81, 'Tankers, hazardous category A'),
    (82, 'Tankers, hazardous category B'),
    (83, 'Tankers, hazardous category C'),
    (84, 'Tankers, hazardous category D'),
    (85, 'Tankers'),
    (86, 'Tankers'),
    (87, 'Tankers'),
    (88, 'Tankers'),
    (89, 'Tankers'),
    (90, 'Other'),
    (91, 'Other, hazardous category A'),
    (92, 'Other, hazardous category B'),
    (93, 'Other, hazardous category C'),
    (94, 'Other, hazardous category D'),
    (95, 'Other'),
    (96, 'Other'),
    (97, 'Other'),
    (98, 'Other'),
    (99, 'Other'),
    (100, 'Unknown'),
]

_create_coarsetype_table = '''
CREATE TABLE IF NOT EXISTS coarsetype_ref (
    coarse_type integer,
    coarse_type_txt character varying(75)
);'''

_create_coarsetype_index = 'CREATE UNIQUE INDEX idx_coarsetype ON coarsetype_ref(coarse_type)'


def get_dbname(dbpath):
    if dbpath is None:
        raise ValueError('dbpath cannot be None')
    name_ext = os.path.split(dbpath)[1]
    name = name_ext.split('.')[0]
    return name


pragmas = [
    'PRAGMA temp_store=MEMORY',
    'PRAGMA journal_mode=TRUNCATE',
    'PRAGMA threads=6',
    'PRAGMA mmap_size=1000000000',  # 1GB
    'PRAGMA cache_size=-15625000',  # 16GB
    'PRAGMA cache_spill=0',
]


class DBConn():
    ''' SQLite3 database connection object

        by default this will create a new SQLite database if the dbpath does
        not yet exist

        args:
            dbpath (string)
                defaults to dbpath as configured in ~/.config/ais.cfg

        attributes:
            conn (sqlite3.Connection)
                database connection object
            cur (sqlite3.Cursor)
                database cursor object
    '''

    def __init__(self, *, dbpath=None, dbpaths=[]):

        if dbpath is not None:
            dbpaths.append(dbpath)

        if dbpaths == []:
            warnings.warn('No database arguments to DBConn()')

        # configs
        self.conn = sqlite3.connect(':memory:',
                                    timeout=5,
                                    detect_types=sqlite3.PARSE_DECLTYPES
                                    | sqlite3.PARSE_COLNAMES)
        self.conn.row_factory = sqlite3.Row
        for p in pragmas:
            self.conn.execute(p)
        self.conn.commit()
        self.cur = self.conn.cursor()

        # attach auxiliary databases
        self.dbpaths = dbpaths
        self.dbnames = []
        for dbp in dbpaths:
            # check that directory exists
            if not os.path.isdir(os.path.dirname(dbp)):
                print(f'creating directory path: {dbp}')
                os.mkdir(os.path.dirname(dbp))

            self.attach(dbp)

        self.cur.execute('SELECT name FROM sqlite_master '
                         'WHERE type="table" AND name="coarsetype_ref";')

        if not self.cur.fetchall():
            self.create_table_coarsetype()

        self.conn.commit()

    def __enter__(self):
        return self

    def __exit__(self, exc_class, exc, tb):
        while len(self.dbnames) > 0:
            self.dbpaths.pop()
            self.cur.execute('DETACH DATABASE ?', [self.dbnames.pop()])

        self.conn.commit()
        self.conn.close()

    def attach(self, dbpath):
        dbname = get_dbname(dbpath)
        self.cur.execute('PRAGMA database_list')
        res = self.cur.fetchall()
        #attached = dbpath in self.dbpaths
        attached = False
        for r in res:
            if r['name'] == dbname:
                attached = True
        if not attached:
            self.cur.execute('ATTACH DATABASE ? AS ?', [dbpath, dbname])

        if dbpath not in self.dbpaths:
            self.dbpaths.append(dbpath)

        if dbname not in self.dbnames:
            self.dbnames.append(dbname)
        return

    def create_table_coarsetype(self):
        ''' create a table to describe integer vessel type as a human-readable string
            included here instead of create_tables.py to prevent circular import error
        '''

        self.cur.execute(_create_coarsetype_table)

        self.cur.execute(_create_coarsetype_index)

        self.cur.executemany((
            'INSERT OR IGNORE INTO coarsetype_ref (coarse_type, coarse_type_txt) '
            'VALUES (?,?) '), _coarsetype_rows)


class DBConn_async():

    #def __init__(self, dbpath=None, dbpaths=[]):
    def __init__(self, dbpath=None):
        #self.dbpaths = []
        #self.dbnames = []
        #if dbpath is not None:
        #    dbpaths.append(dbpath)
        #if dbpaths == []:
        #    warnings.warn('No database arguments to DBConn()')
        self.dbpath = dbpath

    async def __aenter__(self):
        #self.conn = await aiosqlite.connect(':memory:')
        self.conn = await aiosqlite.connect(self.dbpath)
        self.conn.row_factory = sqlite3.Row

        for p in pragmas:
            _ = await self.conn.execute(p)

        #for dbpath in self.dbpaths:
        #    await self.attach(dbpath)

        coarsetype_cursor = await self.conn.execute(
            'SELECT name FROM sqlite_master '
            'WHERE type="table" AND name="coarsetype_ref";')
        coarsetype_result = await coarsetype_cursor.fetchall()

        if coarsetype_result == []:
            _ = await self.create_table_coarsetype()

        return self

    async def __aexit__(self, exc_class, exc, tb):
        await self.conn.close()
        return

    async def attach(self, dbpath):
        assert isinstance(self.conn, aiosqlite.core.Connection)
        dbname = get_dbname(dbpath)
        cursor = await self.conn.execute('PRAGMA database_list')
        res = await cursor.fetchall()

        attached = False
        for r in res:
            if r['name'] == dbname:
                attached = True

        if not attached:
            _ = await self.conn.execute('ATTACH DATABASE ? AS ?',
                                        [dbpath, dbname])

        if dbpath not in self.dbpaths:
            self.dbpaths.append(dbpath)

        if dbname not in self.dbnames:
            self.dbnames.append(dbname)
        return

    async def create_table_coarsetype(self):
        ''' create a table to describe integer vessel type as a human-readable string
            included here instead of create_tables.py to prevent circular import error
        '''

        _ = await self.conn.execute(_create_coarsetype_table)

        _ = await self.conn.execute(_create_coarsetype_index)

        _ = await self.conn.executemany((
            'INSERT OR IGNORE INTO coarsetype_ref (coarse_type, coarse_type_txt) '
            'VALUES (?,?) '), _coarsetype_rows)
