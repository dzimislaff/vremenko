#!/usr/bin/env python
# -*- coding: 'UTF-8' -*-

import requests
import lxml.etree


def pridobi_spletno_stran(naslov):
    try:
        return requests.get(naslov)
    except requests.exceptions.ConnectionError:
        return None


def pridobi_xml(naslov):
    r = pridobi_spletno_stran(naslov)
    if r:
        stran = lxml.etree.fromstring(bytes(r.text, encoding='utf8'))
        return stran
    else:
        return None
