import asyncio
import os
import json
from json import JSONDecodeError
from datetime import datetime, timedelta

import topojson as tp
import websockets
from shapely.geometry import Point, LineString

from aisdb import zones_dir, DomainFromTxts
from aisdb import sqlfcn_callbacks, DBQuery
from aisdb import (
    TrackGen,
    encode_greatcircledistance,
    split_timedelta,
    max_tracklength,
)
from aisdb.network_graph import colorhash

host = os.environ.get('AISDBHOSTALLOW', '*')
port = os.environ.get('AISDBPORT', 9924)
port = int(port)

print(f"starting server on {host}:{port}")

domain = DomainFromTxts(zones_dir.rsplit(os.path.sep, 1)[1], zones_dir)


def trajectories_json(tracks, ident=lambda track: str(track['mmsi'])):
    for track in tracks:
        if track['time'].size <= 1:
            geom = Point(track['lon'][0], track['lat'][0])
        else:
            geom = LineString(zip(track['lon'], track['lat']))

        topo = tp.Topology(geom).toposimplify(.001, prevent_oversimplify=True)

        yield (topo.output, {"color": colorhash(ident(track))})

    return


class SocketServ():

    async def handler(self, websocket):
        enabled = True
        while enabled:
            try:
                clientmsg = await websocket.recv()
            except websockets.ConnectionClosedOK:
                continue
            except websockets.ConnectionClosed:
                print('closing...')
                await websocket.close()
                break
            except KeyboardInterrupt:
                print('exiting...')
                enabled = False
                exit(0)
                break
            except Exception as err:
                print('error awaiting client: ', end='')
                if hasattr(err, '__module__'):
                    print(err.__module__, end=': ')
                print(err.with_traceback(None))
                continue

            print(f'{websocket.remote_address} ' + clientmsg)

            try:
                req = json.loads(clientmsg)
                assert 'type' in req.keys()
            except JSONDecodeError:
                print('not json', clientmsg)
                continue
            except websockets.ConnectionClosed:
                print('closing...')
                enabled = False
                await websocket.close()
                break
            except Exception as err:
                print(f'error parsing client response:\n{clientmsg}\n', end='')
                if hasattr(err, '__module__'):
                    print(err.__module__, end=': ')
                print(err.with_traceback(None))
                continue

            if req['type'] == 'zones':
                await self.req_zones(req, websocket)
            '''
            elif req['type'] == 'tracks_month':
                y, m = req['month'][:4], req['month'][4:]
                year, month = int(y), int(m)
                start = datetime(year, month, 1)
                end = datetime(year + int(month == 12), month % 12 + 1, 1)
                await self.req_tracks(
                    req,
                    websocket,
                    start=start,
                    end=end,
                )
            '''

            if req['type'] == 'tracks_week':
                year, month, day = map(int, req['date'].split('-'))
                start = datetime(year, month, day)
                end = start + timedelta(days=7)
                await self.req_tracks(
                    req,
                    websocket,
                    start=start,
                    end=end,
                )

            elif req['type'] == 'tracks_day':
                year, month, day = map(int, req['date'].split('-'))
                start = datetime(year, month, day)
                end = start + timedelta(days=1)
                await self.req_tracks(
                    req,
                    websocket,
                    start=start,
                    end=end,
                )

    async def req_zones(self, req, websocket):
        zones = {'type': 'WKBHex', 'geometries': []}
        for zone in domain.zones:
            event = {
                'geometry': zone['geometry'].wkb_hex,
                'opts': {
                    'label': zone['name'],
                },
            }
            zones['geometries'].append(event)
        await websocket.send(json.dumps(zones).replace(' ', ''))
        await websocket.send(json.dumps({'type': 'done'}))

    async def req_tracks(self, req, websocket, *, start, end):
        qry = DBQuery(
            start=start,
            end=end,
            callback=sqlfcn_callbacks.in_bbox_time_validmmsi,
            xmin=domain.minX,
            xmax=domain.maxX,
            ymin=domain.minY,
            ymax=domain.maxY,
        )
        qrygen = qry.gen_qry(printqry=os.environ.get('DEBUG', False))
        pipeline = trajectories_json(
            encode_greatcircledistance(
                split_timedelta(
                    max_tracklength(TrackGen(qrygen)),
                    maxdelta=timedelta(weeks=1),
                ),
                distance_threshold=500000,
                minscore=0,
                speed_threshold=70,
            ))
        eventbatch = {'type': 'topology', 'geometries': []}
        count = 0
        for topology, opts in pipeline:
            count += 1
            event = {'topology': topology, 'opts': opts}
            eventbatch['geometries'].append(event)
            #if False:
            if count % 50 != 0 and count > 50:
                continue
            try:
                await websocket.send(json.dumps(eventbatch).replace(' ', ''))
                clientresponse = await websocket.recv()
                response = json.loads(clientresponse)
            except websockets.ConnectionClosed:
                print('closing...')
                await websocket.close()
                break
            except Exception as err:
                print('error sending topology: ', end='')
                if hasattr(err, '__module__'):
                    print(err.__module__, end=': ')
                raise err.with_traceback(None)
            status = 0
            if response['type'] == 'ack':
                pass
            elif response['type'] == 'stop':
                status = 1
                break
            else:
                raise ValueError(f'unhandled response type: {response}')
            eventbatch = {'type': 'topology', 'geometries': []}
        await websocket.send(json.dumps({'type': 'done', 'status': status}))

    async def main(self):
        async with websockets.serve(self.handler, host=host, port=port):
            await asyncio.Future()


serv = SocketServ()
asyncio.run(serv.main())
