#!/usr/bin/env python
# -*- coding: 'UTF-8' -*-

import pytest
import datetime
import vremenko.vreme
import vremenko.poštar
from vremenko.nastavitve import URL_VREME_KRAJ, XPATH_VREME


kraji = vremenko.nastavitve.URL_VREME_KRAJ.keys()


@pytest.mark.parametrize('kraj', kraji)
def test_vreme_podatki(kraj):
    stran = vremenko.poštar.pridobi_xml(URL_VREME_KRAJ[kraj])
    podatki = vremenko.vreme.vreme_podatki(XPATH_VREME, stran)
    podatki[1] = vremenko.vreme.čas_uredi(podatki[1])
    podatki = vremenko.vreme.Vreme(*podatki)
    assert type(podatki.čas) == datetime.datetime
    assert type(podatki.temperatura) == str
    assert type(podatki.relativna_vlaga) == str
    assert podatki.temperatura_enota == "°C"
    assert podatki.relativna_vlaga_enota == "%"
    assert podatki.tlak_enota == "hPa"
    assert podatki.sončno_obsevanje_enota == "W/m2"
    assert podatki.vsota_padavin_enota == "mm"
    assert (podatki.opis_vremena is None) or (
        type(podatki.opis_vremena) == str)
    assert (podatki.tlak is None) or type(podatki.tlak) == str
    assert (podatki.sončno_obsevanje is None) or (
        type(podatki.sončno_obsevanje) == str)
    assert (podatki.vsota_padavin is None) or (
        type(podatki.vsota_padavin) == str)
