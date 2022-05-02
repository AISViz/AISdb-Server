''' merge track dictionaries with rasters or other data from the web '''

import numpy as np

from aisdb.wsa import wsa
from aisdb.webdata.bathymetry import Gebco
from aisdb.webdata.shore_dist import shore_dist_gfw
#from webdata import marinetraffic


def merge_tracks_shoredist(tracks):
    with shore_dist_gfw() as sdist:
        for track in tracks:
            track['km_from_shore'] = np.array([
                sdist.getdist(x, y) for x, y in zip(track['lon'], track['lat'])
            ])
            track['dynamic'] = set(track['dynamic']).union(
                set(['km_from_shore']))
            yield track


def merge_tracks_portdist(tracks):
    with shore_dist_gfw() as sdist:
        for track in tracks:
            track['km_from_port'] = np.array([
                sdist.getportdist(x, y)
                for x, y in zip(track['lon'], track['lat'])
            ])
            track['dynamic'] = set(track['dynamic']).union(
                set(['km_from_port']))
            yield track


def merge_tracks_bathymetry(tracks, context=None):
    if context is None:
        with Gebco() as bathymetry:
            for track in tracks:
                track['depth_metres'] = np.array([
                    bathymetry.getdepth(x, y)
                    for x, y in zip(track['lon'], track['lat'])
                ]) * -1
                track['dynamic'] = set(track['dynamic']).union(
                    set(['depth_metres']))
                yield track
    else:
        bathymetry = context
        for track in tracks:
            track['depth_metres'] = np.array([
                bathymetry.getdepth(x, y)
                for x, y in zip(track['lon'], track['lat'])
            ]) * -1
            track['dynamic'] = set(track['dynamic']).union(
                set(['depth_metres']))
            yield track


def _mergetrack(track, *, bathymetry, sdist, hullgeom, retry_zero,
                skip_missing):
    # vessel tonnage from marinetraffic.com
    track['deadweight_tonnage'] = hullgeom.get_tonnage_mmsi_imo(
        track['mmsi'],
        track['imo'],
        retry_zero=retry_zero,
        skip_missing=skip_missing)

    # hull submerged surface area regression on tonnage
    track['submerged_hull_m^2'] = wsa(track['deadweight_tonnage'],
                                      track['ship_type'] or 0)

    # shore, port distance from cell grid
    track['km_from_shore'] = np.array(
        [sdist.getdist(x, y) for x, y in zip(track['lon'], track['lat'])])
    track['km_from_port'] = np.array(
        [sdist.getportdist(x, y) for x, y in zip(track['lon'], track['lat'])])

    # seafloor depth from raster, and depths of surrounding grid cells
    track['depth_metres'] = np.array([
        bathymetry.getdepth(x, y) for x, y in zip(track['lon'], track['lat'])
    ])

    # update indices
    track['static'] = set(track['static']).union(
        set([
            'submerged_hull_m^2',
            'deadweight_tonnage',
        ]))

    track['dynamic'] = set(track['dynamic']).union(
        set([
            'km_from_shore',
            'km_from_port',
            'depth_metres',
        ]))

    return track


def merge_layers(
    tracks,
    *,
    retry_zero=False,
    skip_missing=True,
    bathymetry=None,
    hullgeom=None,
    sdist=None,
):
    ''' generator function to merge AIS row data with shore distance, bathymetry, geometry databases

        same as above functions, but all combined in one

        args:
            tracks: dictionary generator
                yields track dictionary objects

        yields:
            sets of rows grouped by MMSI sorted by time with additional columns appended

        # set start method in main script
        #import os; from multiprocessing import set_start_method
        #if os.name == 'posix' and __name__ == '__main__':
        #    set_start_method('forkserver')

    '''

    # read data layers from disk to merge with AIS
    # print('aggregating ais, shore distance, bathymetry, vessel geometry...')
    #with shore_dist_gfw() as sdist, Gebco(
    #) as bathymetry, marinetraffic.scrape_tonnage() as hullgeom:
    if bathymetry is None:
        bathymetry = Gebco()
    if sdist is None:
        sdist = shore_dist_gfw()

    for track in tracks:
        yield _mergetrack(
            track,
            bathymetry=bathymetry,
            sdist=sdist,
            hullgeom=hullgeom,
            retry_zero=retry_zero,
            skip_missing=skip_missing,
        )
