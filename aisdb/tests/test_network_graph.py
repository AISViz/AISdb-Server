'''
from multiprocessing import set_start_method
set_start_method('forkserver')
from multiprocessing import Pool, Queue
'''
import os
from datetime import datetime
from functools import partial

from shapely.geometry import Polygon

from aisdb.database.dbqry import DBQuery, DBConn
from aisdb.database.sqlfcn_callbacks import (
    in_bbox_time, )
from aisdb.gis import Domain
from aisdb.track_gen import (
    fence_tracks,
    encode_greatcircledistance,
    TrackGen,
)
from aisdb.network_graph import _serialize_network_edge
from aisdb.webdata.merge_data import (
    merge_tracks_bathymetry,
    merge_tracks_portdist,
    merge_tracks_shoredist,
    # merge_tracks_hullgeom,
)
from aisdb.tests.create_testing_data import (
    sample_dynamictable_insertdata,
    sample_gulfstlawrence_bbox,
)
from aisdb.database.create_tables import (
    sqlite_createtable_dynamicreport,
    sqlite_createtable_staticreport,
)


def test_network_graph_geofencing(tmpdir):
    testdbpath = os.path.join(tmpdir, 'test_network_graph.db')
    #aisdatabase = DBConn(dbpath=testdbpath)
    with DBConn(dbpath=testdbpath) as aisdatabase:
        sqlite_createtable_staticreport(aisdatabase,
                                        month="200001",
                                        dbpath=testdbpath)
        sqlite_createtable_dynamicreport(aisdatabase,
                                         month="200001",
                                         dbpath=testdbpath)

        # query configs
        start = datetime(2000, 1, 1)
        end = datetime(2000, 2, 1)

        z1 = Polygon(zip(*sample_gulfstlawrence_bbox()))
        domain = Domain('gulf domain', zones=[{'name': 'z1', 'geometry': z1}])

        args = DBQuery(
            db=aisdatabase,
            start=start,
            end=end,
            xmin=domain.minX,
            xmax=domain.maxX,
            ymin=domain.minY,
            ymax=domain.maxY,
            callback=in_bbox_time,
        )

        sample_dynamictable_insertdata(db=aisdatabase, dbpath=testdbpath)
        # processing configs
        distsplit = partial(
            encode_greatcircledistance,
            distance_threshold=250000,
            speed_threshold=45,
            minscore=5e-07,
        )
        geofenced = partial(fence_tracks, domain=domain)

        # query db for points in domain bounding box
        try:
            _test = next(TrackGen(args.gen_qry(dbpath=testdbpath)))
            _test2 = next(
                geofenced(distsplit(TrackGen(
                    args.gen_qry(dbpath=testdbpath)))))
        except SyntaxError as err:
            print(f'suppressed error :\t{err.with_traceback(None)}')
        except Exception as err:
            raise err
