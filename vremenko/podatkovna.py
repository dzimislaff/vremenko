#!/usr/bin/env python
# -*- coding: 'UTF-8' -*-

import logging
import sqlite3
from sqlite3 import Error

import vremenko.vreme


# omogoči beleženje
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    filename="podatkovna.log",
                    # encoding="utf-8",  # python >= 3.9
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def poveži_podatkovno(lokacija: str):
    povezava = None
    try:
        povezava = sqlite3.connect(lokacija)
        logger.info("Povezava s podatkovno bazo je bila uspešno vzpostavljena.")
    except Error as e:
        logger.error(f"Prišlo je do napake: {e}")
    return povezava


def izvedi_ukaz(povezava,
                ukaz: str,
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
#                    ukaz
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
                        kraj: str = "Ljubljana"
                        ):
    povezava = poveži_podatkovno(podatkovna)

    vreme = vremenko.vreme.vremenko_podatki(kraj)[:3]
    vreme = vreme[0][:7] + vreme[1][:3] + vreme[2]

    izvedi_ukaz(povezava, ustvari_vremenko)
    izvedi_ukaz(povezava, vnesi_vremenko, *vreme)


if __name__ == '__main__':
    posodobi_podatkovno()
