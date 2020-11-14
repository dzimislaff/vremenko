#!/usr/bin/env python
# -*- coding: 'UTF-8' -*-

import pytest
import datetime
from dateutil import tz
import vremenko.vreme


slo_časovni_pas = tz.gettz("Europe/Ljubljana")
časi = [
    ("07.07.2020 21:00 CEST", '7. 7. 2020', '21.00', datetime.datetime(2020, 7, 7, 21, 0, tzinfo=slo_časovni_pas)),
    ("06.04.2020 19:38 CEST", '6. 4. 2020', '19.38', datetime.datetime(2020, 4, 6, 19, 38, tzinfo=slo_časovni_pas)),
    (1, None, None, None),
    (True, None, None, None),
    (False, None, None, None),
    (1.5, None, None, None),
    ([], None, None, None),
    ({}, None, None, None),
    ((), None, None, None),
    (None, None, None, None),
]

@pytest.mark.parametrize('čas, datum, ura, dtm', časi)
def test_čas_uredi(čas, datum, ura, dtm):
    polica = vremenko.vreme.čas_uredi(čas)
    assert polica.datum == datum
    assert polica.ura == ura
    assert polica.dtm == dtm
