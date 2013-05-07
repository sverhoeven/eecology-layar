import os
import sys
import transaction
from lxml import etree
from sqlalchemy import engine_from_config

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from eecology_layar.models import (
    DBSession,
    Track,
    Base,
    )

import logging
logger = logging.getLogger()

color2class = {
               "ff01baf8": "soaring",
               "ff04ffe0": "sitting",
               "ff00daf9": "flapping",
               "ff2bf4ff": "floating",
               }


def importkml(node):
    model = Track()
    coord = node[6][3].text.strip().split(',')
    model.lat = float(coord[0])
    model.long = float(coord[1])
    model.alt = float(coord[2])

    hex_color = node[4][0].text  # abgr
    model.classifier = color2class[hex_color]

    table = etree.fromstring(node[3].text)
    model.tid = table[2][1].text
    model.utm_time = table[1][1].text
    speeds = table[5][1].text.split()
    model.speed = speeds[0]
    model.speed3d = speeds[1]

    model.id = "{} {}".format(model.tid, model.utm_time)

    # TODO make name dynamic
    model.name = "female gull FAKV"

    DBSession.add(model)


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> <kml_uri>\n'
          '(example: "%s development.ini S355_museumplein.kml")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) != 3:
        usage(argv)
    config_uri = argv[1]
    kml_uri = argv[2]

    print "parsing kml\n"
    t = etree.parse(kml_uri)
    r = t.getroot()

    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)

    print "Create db\n"

    with transaction.manager:
        for p in r[0][2:]:  # skip linestring
            importkml(p)

if __name__ == '__main__':
    main()
