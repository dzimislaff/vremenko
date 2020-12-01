#!/usr/bin/env python
# -*- coding: 'UTF-8' -*-

import sqlite3
from sqlite3 import Error
import logging
import time
from vremenko.nastavitve import OPIS_VREMENA, VETER_IZPIS
from vremenko.vreme import vremenko_podatki


ustvari_dan = """
    CREATE TABLE IF NOT EXISTS dan (id INTEGER PRIMARY KEY,
        vzhod INTEGER,
        zahod INTEGER,
        dolžina_dneva INTEGER,
        zaporedni_v_letu INTEGER,
        unique (vzhod)
    )
"""

vnesi_dan = """
    INSERT INTO
        dan (
            vzhod,
            zahod,
            dolžina_dneva,
            zaporedni_v_letu
        )
    VALUES (?,?,?,?)
"""

ustvari_vreme = """
    CREATE TABLE IF NOT EXISTS vreme (id INTEGER PRIMARY KEY,
        čas INTEGER,
        opis_vremena INTEGER,
        temperatura INTEGER,  -- °C
        relativna_vlaga INTEGER,  -- %
        tlak INTEGER,  -- hPa
        sončno_obsevanje INTEGER,  -- W/m2
        vsota_padavin INTEGER,  -- mm
        smer_vetra INTEGER,
        hitrost_vetra INTEGER,  -- m/s
        sunki_vetra INTEGER,  -- m/s
        unique (čas)
    )
"""

vnesi_vreme = """
    INSERT INTO
        vreme (
            čas,
            opis_vremena,
            temperatura,
            relativna_vlaga,
            tlak,
            sončno_obsevanje,
            vsota_padavin,
            smer_vetra,
            hitrost_vetra,
            sunki_vetra
        )
    VALUES (?,?,?,?,?,?,?,?,?,?)
"""

ustvari_onesnaženost = """
    CREATE TABLE IF NOT EXISTS onesnaženost (id INTEGER PRIMARY KEY,
        čas INTEGER,
        pm10 INTEGER,  -- µg/m³
        pm2_5 INTEGER,  -- µg/m³
        so2 INTEGER,  -- µg/m³
        co INTEGER,  -- mg/m³
        o3 INTEGER,  -- µg/m³
        no2 INTEGER,  -- µg/m³
        opozorilo BOOLEAN NOT NULL CHECK (opozorilo IN (0,1)),
        unique (čas)
    )
"""

vnesi_onesnaženost = """
    INSERT INTO
        onesnaženost (
            čas,
            pm10,
            pm2_5,
            so2,
            co,
            o3,
            no2,
            opozorilo
        )
    VALUES (?,?,?,?,?,?,?,?)
"""

odstrani_znak_onesnaženost = """
    UPDATE onesnaženost
    SET pm10 = trim(pm10, '<'),
        pm2_5 = trim(pm2_5, '<'),
        so2 = trim(so2, '<'),
        co = trim(co, '<'),
        o3 = trim(o3, '<'),
        no2 = trim(no2, '<');
"""


def poveži_podatkovno(lokacija: str,
                      ):
    povezava = None
    try:
        povezava = sqlite3.connect(
            # detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
            lokacija)
        logging.info(
            "Povezava s podatkovno bazo je bila uspešno vzpostavljena.")
    except Error as e:
        logging.error(f"Prišlo je do napake: {e}")
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
        logging.info("Uspešno izveden vnos v podatkovno bazo.")
    except sqlite3.IntegrityError as e:
        logging.warning(f"Opozorilo: {e}")
    except Error as e:
        logging.error(f"Prišlo je do napake: {e}")


def pretvori_unixepoch(dtm):
    return time.mktime(dtm.timetuple())


def posodobi_podatkovno(podatkovna: str,  # "ljubljana-2020-11.db"
                        kraj: str  # "Ljubljana"
                        ):

    povezava = poveži_podatkovno(podatkovna)

    podatki = vremenko_podatki(kraj)

    # tabela dan
    if podatki.dan:
        dan = [pretvori_unixepoch(i) for i in podatki.dan[:2]]
        dan.append(podatki.dan.dolžina_dneva.total_seconds())
        dan.append(podatki.dan.zaporedni_v_letu)
        izvedi_ukaz(povezava, ustvari_dan)
        izvedi_ukaz(povezava, vnesi_dan, *dan)

    # tabela vreme
    if podatki.vreme:
        podatki_vreme = list(podatki.vreme[:7] + podatki.veter[:3])
        podatki_vreme[0] = time.mktime(podatki_vreme[0].timetuple())
        if podatki_vreme[1]:
            podatki_vreme[1] = list(OPIS_VREMENA.keys()).index(podatki_vreme[1])
        podatki_vreme[7] = VETER_IZPIS.index(podatki_vreme[7])
        izvedi_ukaz(povezava, ustvari_vreme)
        izvedi_ukaz(povezava, vnesi_vreme, *podatki_vreme)

    # tabela onesnaženost
    if podatki.onesnaženost:
        onesnaženost = list(podatki.onesnaženost)
        onesnaženost[0] = pretvori_unixepoch(onesnaženost[0])
        izvedi_ukaz(povezava, ustvari_onesnaženost)
        izvedi_ukaz(povezava, vnesi_onesnaženost, *onesnaženost)
        izvedi_ukaz(povezava, odstrani_znak_onesnaženost)


if __name__ == '__main__':
    posodobi_podatkovno()
