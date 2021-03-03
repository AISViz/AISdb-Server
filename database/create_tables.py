import sqlite3
import os
from os.path import sep

newdb = not os.path.isfile(f'database{sep}ais.db')
conn = sqlite3.connect(f'database{sep}ais.db')
cur = conn.cursor()

conn.enable_load_extension(True)
cur.execute('SELECT load_extension("mod_spatialite.so")')
if newdb: 
    cur.execute('SELECT InitSpatialMetaData(1)')

    cur.execute(''' CREATE TABLE coarsetype_ref (
            coarse_type integer,
            coarse_type_txt character varying(75)
        ); ''')
    cur.executemany (''' INSERT INTO coarsetype_ref (coarse_type, coarse_type_txt) VALUES (?,?) ''', (
        (20,	'Wing in ground craft'),
        (30,	'Fishing'),
        (31,	'Towing'),
        (32,	'Towing - length >200m or breadth >25m'),
        (33,	'Engaged in dredging or underwater operations'),
        (34,	'Engaged in diving operations'),
        (35,	'Engaged in military operations'),
        (36,	'Sailing'),
        (37,	'Pleasure craft'),
        (38,	'Reserved for future use'),
        (39,	'Reserved for future use'),
        (40,	'High speed craft'),
        (50,	'Pilot vessel'),
        (51,	'Search and rescue vessels'),
        (52,	'Tugs'),
        (53,	'Port tenders'),
        (54,	'Vessels with anti-pollution facilities or equipment'),
        (55,	'Law enforcement vessels'),
        (56,	'Spare for assignments to local vessels'),
        (57,	'Spare for assignments to local vessels'),
        (58,	'Medical transports (1949 Geneva convention)'),
        (59,	'Ships and aircraft of States not parties to an armed conflict'),
        (60,	'Passenger ships'),
        (70,	'Cargo ships'),
        (80,	'Tankers'),
        (90,	'Other types of ship'),
        (100,	'Unknown'),
        )
    )


def create_table_msg123(cur, month):
    cur.execute(f'''
            CREATE TABLE ais_s_{month}_msg_1_2_3 (
                unq_id_prefix character varying(11),
                lineno integer,
                errorflag boolean,
                mmsi integer,
                message_id smallint,
                repeat_indicator "char",
                "time" timestamp without time zone,
                millisecond smallint,
                region smallint,
                country smallint,
                base_station integer,
                online_data character varying(6),
                group_code character varying(4),
                sequence_id smallint,
                channel character varying(3),
                data_length character varying(20),
                navigational_status smallint,
                rot double precision,
                sog real,
                accuracy boolean,
                longitude double precision,
                latitude double precision,
                cog real,
                heading real,
                maneuver "char",
                raim_flag boolean,
                communication_state integer,
                utc_second smallint,
                spare character varying(4)
            );
        ''')
    cur.execute(f''' SELECT AddGeometryColumn('ais_s_{month}_msg_1_2_3', 'ais_geom', 4326, 'POINT', 'XY') ''')
    cur.execute(f''' SELECT CreateSpatialIndex('ais_s_{month}_msg_1_2_3', 'ais_geom') ''')
    #cur.execute(f''' CREATE UNIQUE INDEX idx_msg123_mmsi_time ON 'ais_s_{month}_msg_1_2_3' (mmsi, time) ''')  # redundant?
    cur.execute(f''' CREATE UNIQUE INDEX idx_{month}_msg123_mmsi_time_lat_lon ON 'ais_s_{month}_msg_1_2_3' (mmsi, time, longitude, latitude)''')


def create_table_msg5(cur, month):
    cur.execute(f'''
            CREATE TABLE ais_s_{month}_msg_5 (
                unq_id_prefix character varying(11),
                lineno integer,
                errorflag boolean,
                mmsi integer,
                message_id smallint,
                repeat_indicator "char",
                "time" timestamp without time zone,
                millisecond smallint,
                region smallint,
                country smallint,
                base_station integer,
                online_data character varying(6),
                group_code character varying(4),
                sequence_id smallint,
                channel character varying(3),
                data_length character varying(20),
                vessel_name character varying(20),
                call_sign character varying(7),
                imo integer,
                ship_type smallint,
                dim_bow smallint,
                dim_stern smallint,
                dim_port smallint,
                dim_star smallint,
                draught smallint,
                destination character varying(20),
                ais_version "char",
                fixing_device smallint,
                trans_control smallint,
                eta_month smallint,
                eta_day smallint,
                eta_hour smallint,
                eta_minute smallint,
                sequence smallint,
                dte boolean,
                mode smallint,
                spare character varying(4),
                spare2 character varying(4)
            );
        ''')
    cur.execute(f''' CREATE UNIQUE INDEX idx_{month}_msg5_mmsi_time ON 'ais_s_{month}_msg_5' (mmsi, time)''')


def create_table_msg18(cur, month):
    cur.execute(f'''
            CREATE TABLE ais_s_{month}_msg_18 (
                unq_id_prefix character varying(11),
                lineno integer,
                errorflag boolean,
                mmsi integer,
                message_id smallint,
                repeat_indicator "char",
                "time" timestamp without time zone,
                millisecond smallint,
                region smallint,
                country smallint,
                base_station integer,
                online_data character varying(6),
                group_code character varying(4),
                sequence_id smallint,
                channel character varying(3),
                data_length character varying(20),
                sog real,
                accuracy boolean,
                longitude double precision,
                latitude double precision,
                cog real,
                heading real,
                utc_second smallint,
                unit_flag boolean,
                display boolean,
                dsc boolean,
                band boolean,
                msg22 boolean,
                mode smallint,
                raim_flag boolean,
                communication_flag boolean,
                communication_state integer,
                spare character varying(4),
                spare2 character varying(4)
            )
        ''')
    cur.execute(f''' SELECT AddGeometryColumn('ais_s_{month}_msg_18', 'ais_geom', 4326, 'POINT', 'XY') ''')
    cur.execute(f''' SELECT CreateSpatialIndex('ais_s_{month}_msg_18', 'ais_geom') ''')
    #cur.execute(f''' CREATE UNIQUE INDEX idx_msg18_mmsi_time ON 'ais_s_{month}_msg_18' (mmsi, time) ''')
    cur.execute(f''' CREATE UNIQUE INDEX idx_{month}_msg18_mmsi_time_lat_lon ON 'ais_s_{month}_msg_18' (mmsi, time, longitude, latitude)''')


def create_table_msg24(cur, month):
    cur.execute(f'''
            CREATE TABLE ais_s_{month}_msg_24 (
                --unq_id_prefix character varying(11),
                --lineno integer,
                --errorflag boolean,
                mmsi integer,
                message_id smallint,
                repeat_indicator "char",
                "time" timestamp without time zone,
                --millisecond smallint,
                --region smallint,
                --country smallint,
                --base_station integer,
                --online_data character varying(6),
                --group_code character varying(4),
                sequence_id smallint,
                --channel character varying(3),
                --data_length character varying(20),
                vessel_name character varying(20),
                call_sign character varying(7),
                --imo integer,
                ship_type smallint,
                dim_bow smallint,
                dim_stern smallint,
                dim_port smallint,
                dim_star smallint,
                --fixing_device smallint,
                part_number boolean,
                vendor_id character varying(8),
                mother_ship_mmsi integer,
                --spare character varying(4), 
                model smallint, 
                serial integer
            );
        ''')
    cur.execute(f''' CREATE UNIQUE INDEX idx_{month}_msg24_mmsi_time ON 'ais_s_{month}_msg_24' (mmsi, time)''')
    #cur.execute(f''' CREATE INDEX idx_msg24_imo_time ON 'ais_s_{month}_msg_24' (imo, time)''')


def create_table_msg27(cur, month):
    cur.execute(f'''
            CREATE TABLE ais_s_{month}_msg_27 (
                unq_id_prefix character varying(11),
                lineno integer,
                errorflag boolean,
                mmsi integer,
                message_id smallint,
                repeat_indicator "char",
                "time" timestamp without time zone,
                millisecond smallint,
                region smallint,
                country smallint,
                base_station integer,
                online_data character varying(6),
                group_code character varying(4),
                sequence_id smallint,
                channel character varying(3),
                data_length character varying(20),
                navigational_status smallint,
                sog real,
                accuracy boolean,
                longitude double precision,
                latitude double precision,
                cog real,
                raim_flag boolean,
                gnss_status boolean,
                spare character varying(4)
            );
        ''')
    cur.execute(f''' SELECT AddGeometryColumn('ais_s_{month}_msg_27', 'ais_geom', 4326, 'POINT', 'XY') ''')
    cur.execute(f''' SELECT CreateSpatialIndex('ais_s_{month}_msg_27', 'ais_geom') ''')
    cur.execute(f''' CREATE UNIQUE INDEX idx_{month}_msg27_mmsi_time_lat_lon ON 'ais_s_{month}_msg_27' (mmsi, time, longitude, latitude)''')


def create_table_msg_other(cur, month):
    cur.execute(f'''
            CREATE TABLE ais_s_{month}_msg_other (
                unq_id_prefix character varying(11),
                lineno integer,
                parseerror character varying(1),
                mmsi integer,
                datetime timestamp without time zone,
                message_id smallint,
                ais_msg_eecsv text
            );
        ''')
    cur.execute(f''' CREATE INDEX idx_{month}_msg_other_mmsi_time ON 'ais_s_{month}_msg_other' (mmsi, datetime) ''')


'''
create_table_msg24('202101')
'''
