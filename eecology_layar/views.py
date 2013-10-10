import os
import shutil
import logging
from pyramid.view import view_config
from pyramid.response import Response
from geoalchemy.functions import functions
from geoalchemy import WKTSpatialElement
from .models import DBSession, Track, Individual, TrackSession, Device

logger = logging.getLogger()


@view_config(route_name='home', renderer='json')
def home(request):
    layer = request.params['layerName']
    hotspots = get_hotspots(request)
    if len(hotspots) > 0:
        result = {
          "hotspots": hotspots,
          "layer": layer,
          "errorString": "ok",
          "errorCode": 0,
        }
    else:
        error = "No POIs are returned. Please adjust the filter settings."
        result = {
          "hotspots": hotspots,
          "layer": layer,
          "errorString": error,
          "errorCode": 20,
        }

    return result


@view_config(route_name='screenshot')
def upload_screenshot(request):
    """

    POST params:
    screenshot: the image
    layer_name: the name of the layer
    message: a message from the user
    lat: latitude of the user
    lon: longitude of the user
    location_name: friendly location name
    """

    p = request.POST
    logger.info(p)
    input_file = p['screenshot'].file
    filename = "{0}-{1}.jpg".format(p['lat'], p['lon'])
    file_path = os.path.join('/tmp', filename)
    logger.warn("Storing screenshot at " + file_path + " with message: "+ p['message'])
    with open(file_path, 'wb') as output_file:
        shutil.copyfileobj(input_file, output_file)

    return Response("OK")


def get_hotspots(request):
    """

    Example request params:
    NestedMultiDict([
        (u'lang', u'en'),
        (u'countryCode', u'NL'),
        (u'userId', u'6f85d06929d160a7c8a3cc1ab4b54b87db99f74b'),
        (u'lon', u'4.88891601562'),
        (u'version', u'7.1'),
        (u'radius', u'90534'),
        (u'lat', u'52.37895253'),
        (u'layerName', u'eecology'),
        (u'accuracy', u'100')
    ])

     """

    """
      // Use PDO::prepare() to prepare SQL statement.
  // This statement is used due to security reasons and will help prevent general SQL injection attacks.
  // ":lat1", ":lat2", ":long" and ":radius" are named parameter markers for which real values
  // will be substituted when the statement is executed.
  // $sql is returned as a PDO statement object.
  $sql = $db->prepare( "
              SELECT id,
                     imageURL,
                     title,
                     description,
                     footnote,
                     lat,
                     lon,
                     (((acos(sin((:lat1 * pi() / 180)) * sin((lat * pi() / 180)) +
                        cos((:lat2 * pi() / 180)) * cos((lat * pi() / 180)) *
                        cos((:long  - lon) * pi() / 180))
                       ) * 180 / pi()
                      )* 60 * 1.1515 * 1.609344 * 1000
                     ) as distance
               FROM POI
              WHERE poiType = "geo"
             HAVING distance < :radius
           ORDER BY distance ASC
              LIMIT 0, 50 " );

  // PDOStatement::bindParam() binds the named parameter markers to the
  // specified parameter values.
  $sql->bindParam( ':lat1', $value['lat'], PDO::PARAM_STR );
  $sql->bindParam( ':lat2', $value['lat'], PDO::PARAM_STR );
  $sql->bindParam( ':long', $value['lon'], PDO::PARAM_STR );
  $sql->bindParam( ':radius', $value['radius'], PDO::PARAM_INT );
  // Use PDO::execute() to execute the prepared statement $sql.
  $sql->execute();
    """
    p = request.params

    if 'RADIOLIST' not in p:
        p['RADIOLIST'] = 355

    # predefined list of track+ranges
    tracks = {
              '355': [355, '2010-06-28T00:12:47Z', '2010-06-28T17:43:09Z'],
              '6014a': [6014, '2013-06-07 02:16:33', '2013-06-07 14:58:04'],
              '6014b': [6014, '2013-06-03 08:09:28', '2013-06-03 19:26:27'],
              '870': [870, '2013-06-18 05:40:37', '2013-06-18 15:40:38'],
              }

    device_info_serial = tracks[p['RADIOLIST']][0]
    start_time = tracks[p['RADIOLIST']][1]
    stop_time = tracks[p['RADIOLIST']][2]

    point = "POINT({0} {1})".format(p['lon'], p['lat'])
    mine = WKTSpatialElement(point)
    spheroid = 'SPHEROID["WGS 84",6378137,298.257223563]'
    #distc = functions.distance(Track.location, mine)
    distc = 'ST_Distance_Spheroid(location, ST_GeomFromText(:mine, 4326), :spheroid)'
    within = distc + ' < :radius'
    query = DBSession().query(Track, Individual)
    query = query.join(Device).join(TrackSession).join(Individual)
    query = query.filter(within).params(mine=point, spheroid=spheroid, radius=p['radius'])
    query = query.filter(Track.device_info_serial==device_info_serial)
    query = query.filter(Track.date_time.between(start_time, stop_time))
    query = query.order_by(distc)  # Closest spot first

    logger.info(query)

    spots = []
    # TODO implement paging, for now select hotspots in Amsterdam
    limit = 50 # for some reason limit must be x3 to get correct row count
    query = query.slice(0, limit)
    rows = query.all();
    logger.info(len(rows))
    for row, indi in rows:

        name = "{0} {1} {2}".format(indi.sex, indi.species, indi.color_ring)
        spot = {
           "id": str(row.device_info_serial) + " " + str(row.date_time),
           "anchor": {"geolocation": {"lat": row.latitude,
                                      "lon": row.longitude,
                                      }},
           "text": {
             "title": str(row.date_time),
             "description": u"{0}, {1} \u00B0C, T: {2} km/h, D: {3} &deg;".format(name, row.temperature, round(row.speed or 0, 2), round(row.direction or 0, 0)),
             "footnote": "http://www.uva-bits.nl",
           },
#            "imageURL": request.static_url('eecology_layar:static/class/{0}.jpg'.format(row.classifier)),
           "imageURL": "http://www.uva-bits.nl/wp-content/uploads/2011/01/N2_seagull-50x50.jpg",
           "biwStyle": "collapsed",
#           "object": {
#                      "contentType": "model/vnd.layar.l3d",
#                      "url": "http://testvm1.uva-bits.nl/layar/static/cheers.l3d",
#                       "url": "http://testvm1.uva-bits.nl/layar/static/bird.l3d",
#                      "url": request.static_url('eecology_layar:static/bird.l3d'),
#                      "size": 2,
#                      },
           "transform": {
#                         "rotate": {
#                                    "axis": {"z": 1},
#                                    "angle": row.direction,
#                                    },
                         "scale": p['CUSTOM_SLIDER']/100.0,
                         },
           "actions": [{
                        "label": "Share",
                        "uri": "layarshare://sharingapi/?title=Describe%20title&type=message&description=Describe%20location",
                        "contentType": "application/vnd.layar.internal",
                        "activityType": 13
                      }, {
                        "label": "Picture",
                        "uri": "layarshare://sharingapi/?type=screenshot",
                        "contentType": "application/vnd.layar.internal",
                        "params": ["lat", "lon", "alt"],
                        "activityType": 27
                      }, {
                        "label": "Movie",
                        "uri": "bits://movie",
                        "params": ["lat", "lon", "alt"],
                        "activityType": 3
                      }, {
                        "label": "Sound",
                        "uri": "bits://sound",
                        "params": ["lat", "lon", "alt"],
                        "activityType": 2
                      }]
         }
        if 'alt' in p:
            """Only show alt when gps fix"""
            alt = row.altitude - float(p['alt'])
            spot['transform']['translate'] = {'z': alt}


        spots.append(spot)

    return spots

