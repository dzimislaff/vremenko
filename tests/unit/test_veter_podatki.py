#!/usr/bin/env python
# -*- coding: 'UTF-8' -*-

import pytest
import vremenko.vreme
import vremenko.poštar
from vremenko.nastavitve import URL_VREME_KRAJ, XPATH_VETER


kraji = vremenko.nastavitve.URL_VREME_KRAJ.keys()


@pytest.mark.parametrize('kraj', kraji)
def test_veter_podatki(kraj):
    stran = vremenko.poštar.pridobi_xml(URL_VREME_KRAJ[kraj])
    podatki = vremenko.vreme.vreme_podatki(XPATH_VETER, stran)
    podatki = vremenko.vreme.Veter(*podatki)
    if podatki:
        assert (podatki.smer_vetra is None) or type(podatki.smer_vetra) == str
        assert (podatki.hitrost_vetra is None) or type(
            podatki.hitrost_vetra) == str
        assert (podatki.sunki_vetra is None) or type(
            podatki.sunki_vetra) == str
        assert (podatki.hitrost_vetra_enota is None) or (
            podatki.hitrost_vetra_enota == "m/s")
        assert (podatki.sunki_vetra_enota is None) or (
            podatki.sunki_vetra_enota == "m/s")
