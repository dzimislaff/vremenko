#!/usr/bin/env python
# -*- coding: 'UTF-8' -*-

import pytest
import vremenko.vreme
from vremenko.nastavitve import URL_VREME_KRAJ


@pytest.mark.parametrize('kraji', URL_VREME_KRAJ.keys())
def test_vremenko_izpis(kraji):
    assert type(vremenko.vreme.vremenko_izpis(kraji)) == str
