#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
logger = logging.getLogger(__name__)
from amon import push_amon_measures, push_contracts, setup_peek, Popper
import os
import sys
import time
from ooop import OOOP

logging.basicConfig(level=logging.INFO)

def setup_ooop():
    ooop_config = {}
    for key, value in os.environ.items():
        if key.startswith('OOOP_'):
            key = key.split('_')[1].lower()
            if key == 'port':
                value = int(value)
            ooop_config[key] = value
    logger.info("Using OOOP CONFIG: %s" % ooop_config)
    return OOOP(**ooop_config)


if __name__ == '__main__':
    O = setup_peek()
    if sys.argv[1] == 'push_amon_measures':
        serials = open('serials', 'r')
        for serial in serials:
            ini = 0
            page = 500
	    meter_name = serial.replace('\n', '').strip()
            if not meter_name.startswith('ZIV00'):
                continue
            search_params = [('name', '=', meter_name),
                             ('valid', '=', True),
                             ('timestamp', '>=', '2012-05-01'),
			    ]
            profiles_ids = O.TgProfile.search(search_params, ini, page)
            while profiles_ids:
                j = push_amon_measures.delay(profiles_ids)
                logger.info("Job id:%s | %s/%s/%s" % (j.id, meter_name,
                                                      ini, page))
                time.sleep(0.1)
                ini += page
                profiles_ids = O.TgProfile.search(search_params, ini, page)
    elif sys.argv[1] == 'push_contracts':
        cids = O.GiscedataLecturesComptador.search([('tg', '=', 1)], 0, 0, False, {'active_test': False})
        contracts_ids = [
            x['polissa'][0]
            for x in O.GiscedataLecturesComptador.read(cids, ['polissa'])
        ]
        contracts_ids = set(contracts_ids)
        popper = Popper(contracts_ids)
        bucket = 500
        pops = popper.pop(bucket)
        while pops:
            j = push_contracts.delay(pops)
            logger.info("Job id:%s" % j.id) 
            pops = popper.pop(bucket)
