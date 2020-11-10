#!/usr/bin/env python
# -*- coding: 'UTF-8' -*-

import pytest
import vremenko.vreme
import vremenko.nastavitve as n
import vremenko.poštar


kraji = vremenko.nastavitve.KRAJI_URL.keys()


@pytest.mark.parametrize('kraj', kraji)
def test_veter_podatki(kraj):
    stran = vremenko.poštar.pridobi_vremenske_podatke(n.KRAJI_URL[kraj])
    podatki = vremenko.vreme.veter_podatki(stran)

    assert type(podatki.smer_vetra) == str
    assert type(podatki.hitrost_vetra) == str
    assert type(podatki.sunki_vetra) == str
    assert podatki.hitrost_vetra_enota == "m/s"
    assert podatki.sunki_vetra_enota == "m/s"
