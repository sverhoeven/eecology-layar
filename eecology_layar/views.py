from pyramid.view import view_config
import logging
from geoalchemy.functions import functions
from .models import DBSession, Track

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

    4.887165,52.372402,1.000000
<TABLE border="1"><TR><TD><B>Variable</B></TD><TD><B>Value</B></TD></TR>
<TR><TD>UTM time</TD><TD>28-Jun-2010 09:11:33</TD>
</TR><TR><TD>sensor ID</TD><TD>355</TD></TR>
<TR><TD>sensor time</TD><TD>179.38302</TD></TR>
<TR><TD>record index</TD><TD>161</TD></TR>
<TR><TD>lat long</TD><TD>4.8859  52.3727</TD></TR>
<TR><TD>altitude [m]</TD><TD>163</TD></TR>
<TR><TD>T-P Speed [km/h]</TD><TD>19.1809  40.8701</TD></TR>
<TR><TD>Dist [km]</TD><TD>NaN</TD></TR>
<TR><TD>Class</TD><TD>NaN</TD></TR>
<TR><TD>record index</TD><TD>161</TD></TR></TABLE>
<color>ff01baf8</color>

SELECT "device_info_serial","date_time","latitude","longitude","altitude","pressure","temperature","h_accuracy","v_accuracy","x_speed","y_speed","z_speed","gps_fixtime","location","userflag","satellites_used","positiondop","speed_accuracy","vnorth","veast","vdown","speed_3d" FROM "gps"."uva_tracking_speed_3d" WHERE "device_info_serial" = '355' and altitude=163

device_info_serial    date_time    latitude    longitude    altitude    pressure    temperature    h_accuracy    v_accuracy    x_speed    y_speed    z_speed    gps_fixtime    location    userflag    satellites_used    positiondop    speed_accuracy    vnorth    veast    vdown    speed_3d
355
2010-06-28 09:11:33
52.3727456
4.8859403
163
NULL
24
3.9
3.6
9.91
-2.23
-5.07
9.7
0101000020E61000006ED51AEF338B13402CDDB820B62F4A40
0
7
1.7
2.96
-10.7651112008473
-3.06595545974304
-1.89689165538333
11.3527926079886


    """

    tracker_id = 355
    rows = [{
             "utm_time": "28-Jun-2010 09:11:33",
             "lat": 4.8859,
             "long": 52.3727,
             "alt": 163,
             "temperature": 24,
             "sensor_time": 179.38302,
             "tspeed": 19.1809,
             "pspeed": 40.8701,
             "class": "soar",
             }, {
             "utm_time": "28-Jun-2010 09:11:33",
             "lat": 4.8859,
             "long": 52.3727,
             "alt": 163,
             "temperature": 24,
             "sensor_time": 179.38302,
             "tspeed": 19.1809,
             "pspeed": 40.8701,
             "class": "soar",
             }]

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
#    p = request.params
#    mine = WKTSpatialElement("POINT({} {})".format(p['lat'], p['long']))
#    dist = functions.distance(Track.geom, mine)
#    within = functions.distance_within(Track.geom, mine, distance)
#    rows = DBSession().query(Track, dist).filter(within).order_by(dist)
    rows = DBSession().query(Track)

    spots = []
    max_hotspots = 200
    for row in rows[:max_hotspots]:
        spot = {
           "id": row.id,
           "anchor": {"geolocation": {"lat": row.lat,
                                      "lon": row.long,
                                      "alt": row.alt,
                                      }},
           "text": {
             "title": row.utm_time,
             "description": "{0}<br/>T: {1} km/h<br/>P: {2} km/h".format(row.name, row.speed, row.speed3d),
             "footnote": "www.uva-bits.nl",
           },
           "imageUrl": request.static_url('eecology_layar:static/class/{0}.png'.format(row.classifier)),
           "biwStyle": "collapsed",
         }
        spots.append(spot)

    return spots
