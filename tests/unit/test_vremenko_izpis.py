#!/usr/bin/env python
# -*- coding: 'UTF-8' -*-

import pytest
import vremenko.vreme
import vremenko.nastavitve


@pytest.mark.parametrize('kraji', vremenko.nastavitve.KRAJI_URL.keys())
def test_vremenko_izpis(kraji):
    assert type(vremenko.vreme.vremenko_izpis(kraji)) == str
