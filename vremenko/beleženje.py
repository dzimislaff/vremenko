#!/usr/bin/env python
# -*- coding: 'UTF-8' -*-

import logging


def beleženje(dnevnik: str,
              nivo_beleženja: int = 4,
              ):
    nivoji = {
        5: logging.CRITICAL,
        4: logging.ERROR,
        3: logging.WARNING,
        2: logging.INFO,
        1: logging.DEBUG
    }
    logging.basicConfig(format="%(asctime)s %(levelname)s: %(name)s, %(funcName)s: %(message)s",
                        filename=dnevnik,
                        # encoding="utf-8",  # python >= 3.9
                        level=nivoji[nivo_beleženja])
    logger = logging.getLogger(__name__)
    return logger
