#!/usr/bin/env python
# -*- coding: 'UTF-8' -*-

import pytest
import vremenko.vreme
import vremenko.nastavitve as n
import vremenko.poštar


kraji = vremenko.nastavitve.KRAJI_URL.keys()


@pytest.mark.parametrize('kraj', kraji)
def test_dan_podatki(kraj):
    stran = vremenko.poštar.pridobi_vremenske_podatke(n.KRAJI_URL[kraj])
    podatki = vremenko.vreme.dan_podatki(stran)

    assert type(podatki.datum_izpis) == str
    assert 10 <= len(podatki.datum_izpis) <= 12

    assert type(podatki.vzhod) == str
    assert len(podatki.vzhod) == 4

    assert type(podatki.zahod) == str
    assert len(podatki.zahod) == 5

    assert type(podatki.dolžina_dneva) == str
    assert 4 <= len(podatki.dolžina_dneva) <= 5

    assert type(podatki.zaporedni_v_letu) == int
    assert 1 <= podatki.zaporedni_v_letu <= 366
