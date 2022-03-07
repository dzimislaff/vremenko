#!/usr/bin/env python
# -*- coding: 'UTF-8' -*-

import pytest
import vremenko.vreme
from vremenko.nastavitve import KRAJI_URL


@pytest.mark.parametrize('kraji', KRAJI_URL.keys())
def test_vremenko_izpis(kraji):
    assert type(vremenko.vreme.vremenko_izpis(kraji)) == str
