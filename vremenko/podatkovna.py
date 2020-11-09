#!/usr/bin/env python
# -*- coding: 'UTF-8' -*-

import logging
import sqlite3
from sqlite3 import Error

import vremenko.vreme


def beleženje(dnevnik: str = "podatkovna.log",
              nivo_beleženja: int = 3,
              ):
    nivoji = {
        5: logging.CRITICAL,
        4: logging.ERROR,
        3: logging.WARNING,
        2: logging.INFO,
        1: logging.DEBUG
    }
    logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                        filename=dnevnik,
                        # encoding="utf-8",  # python >= 3.9
                        level=nivoji[nivo_beleženja])
                        # level = logging.INFO)
                        # level = logging.INFO)
    logger = logging.getLogger(__name__)
    return logger


def poveži_podatkovno(lokacija: str,
                      logger,
                      ):
    povezava = None
    try:
        povezava = sqlite3.connect(lokacija)
        logger.info("Povezava s podatkovno bazo je bila uspešno vzpostavljena.")
    except Error as e:
        logger.error(f"Prišlo je do napake: {e}")
    return povezava


def izvedi_ukaz(povezava,
                ukaz: str,
                logger,
                *vnos: str
                ):
    kazalec = povezava.cursor()
    try:
        if vnos:
            kazalec.execute(ukaz, vnos)
        else:
            kazalec.execute(ukaz)
        povezava.commit()
        logger.info("Uspešno izveden vnos v podatkovno bazo.")
    except sqlite3.IntegrityError as e:
        logger.warning(f"Opozorilo: {e}")
    except Error as e:
        logger.error(f"Prišlo je do napake: {e}")

# TODO
# def preberi_tabelo(povezava,
#                    ukaz,
#                    logger,
#                    ):
#     kazalec = povezava.cursor()
#     podatki = None
#     try:
#         kazalec.execute(ukaz)
#         podatki = kazalec.fetchall()
#         logger.info("Uspešno pridobljeni podatki iz podatkovne baze.")
#     except Error as e:
#         logger.error(f"Prišlo je do napake: {e}")
#     return podatki


ustvari_vremenko = """
    CREATE TABLE IF NOT EXISTS vreme (id INTEGER PRIMARY KEY,
        ura TEXT,
        opis_vremena TEXT,
        temperatura INTEGER,  -- °C
        relativna_vlaga INTEGER,  -- %
        tlak INTEGER,  -- hPa
        sončno_obsevanje INTEGER,  -- W/m2
        vsota_padavin INTEGER,  -- mm
        smer_vetra TEXT,
        hitrost_vetra INTEGER,  -- m/s
        sunki_vetra INTEGER,  -- m/s
        datum TEXT,
        vzhod TEXT,
        zahod TEXT,
        dolžina_dneva TEXT,
        zaporedni_v_letu INTEGER,
        unique (ura, datum)
    )
"""


vnesi_vremenko = """
    INSERT INTO
        vreme (
            ura,
            opis_vremena,
            temperatura,
            relativna_vlaga,
            tlak,
            sončno_obsevanje,
            vsota_padavin,
            smer_vetra,
            hitrost_vetra,
            sunki_vetra,
            datum,
            vzhod,
            zahod,
            dolžina_dneva,
            zaporedni_v_letu
        )
    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
"""


def posodobi_podatkovno(podatkovna: str = "ljubljana-2020-11.db",
                        kraj: str = "Ljubljana",
                        dnevnik: str = "ljubljana-2020-11.log",
                        nivo_beleženja: int = 3,
                        ):
    logger = beleženje(dnevnik, nivo_beleženja)

    povezava = poveži_podatkovno(podatkovna, logger)

    vreme = vremenko.vreme.vremenko_podatki(kraj)[:3]
    vreme = vreme[0][:7] + vreme[1][:3] + vreme[2]

    izvedi_ukaz(povezava, ustvari_vremenko, logger)
    izvedi_ukaz(povezava, vnesi_vremenko, logger, *vreme)


if __name__ == '__main__':
    posodobi_podatkovno()
