#!/usr/bin/env python
# -*- coding: 'UTF-8' -*-

import pytest
import datetime
import vremenko.vreme
import vremenko.poštar
from vremenko.nastavitve import URL_VREME, URL_VREME_KRAJ


kraji = vremenko.nastavitve.URL_VREME_KRAJ.keys()


@pytest.mark.parametrize('kraj', kraji)
def test_dan_podatki(kraj):
    stran = vremenko.poštar.pridobi_xml(
        URL_VREME[0] + URL_VREME_KRAJ[kraj.lower()] + URL_VREME[1])
    podatki = vremenko.vreme.dan_podatki(stran)

    assert type(podatki.vzhod) == datetime.datetime
    assert type(podatki.zahod) == datetime.datetime

    assert type(podatki.dolžina_dneva) == datetime.timedelta

    assert type(podatki.zaporedni_v_letu) == int
    assert 1 <= podatki.zaporedni_v_letu <= 366
