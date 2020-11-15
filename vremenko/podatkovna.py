#!/usr/bin/env python
# -*- coding: 'UTF-8' -*-

import sqlite3
from sqlite3 import Error
# import vremenko.beleženje
import logging
import vremenko.vreme


def poveži_podatkovno(lokacija: str,
                      ):
    povezava = None
    try:
        povezava = sqlite3.connect(
            lokacija, detect_types=sqlite3.PARSE_DECLTYPES)
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


ustvari_dan = """
    CREATE TABLE IF NOT EXISTS dan (id INTEGER PRIMARY KEY,
        datum DATE,
        vzhod TEXT,
        zahod TEXT,
        dolžina_dneva TEXT,
        zaporedni_v_letu INTEGER,
        unique (datum)
    )
"""

vnesi_dan = """
    INSERT INTO
        dan (
            datum,
            vzhod,
            zahod,
            dolžina_dneva,
            zaporedni_v_letu
        )
    VALUES (?,?,?,?,?)
"""

ustvari_vremenko = """
    CREATE TABLE IF NOT EXISTS vreme (id INTEGER PRIMARY KEY,
        ura TEXT,
        datum DATE,
        opis_vremena TEXT,
        temperatura INTEGER,  -- °C
        relativna_vlaga INTEGER,  -- %
        tlak INTEGER,  -- hPa
        sončno_obsevanje INTEGER,  -- W/m2
        vsota_padavin INTEGER,  -- mm
        smer_vetra TEXT,
        hitrost_vetra INTEGER,  -- m/s
        sunki_vetra INTEGER,  -- m/s
        pm10 INTEGER,  -- µg/m³
        so2 INTEGER,  -- µg/m³
        co INTEGER,  -- mg/m³
        o3 INTEGER,  -- µg/m³
        no2 INTEGER,  -- µg/m³
        opozorilo BOOLEAN NOT NULL CHECK (opozorilo IN (0,1)),
        unique (ura, datum),
        FOREIGN KEY (datum)
            REFERENCES dan (datum)
    )
"""

vnesi_vremenko = """
    INSERT INTO
        vreme (
            ura,
            datum,
            opis_vremena,
            temperatura,
            relativna_vlaga,
            tlak,
            sončno_obsevanje,
            vsota_padavin,
            smer_vetra,
            hitrost_vetra,
            sunki_vetra,
            pm10,
            so2,
            co,
            o3,
            no2,
            opozorilo
        )
    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
"""

odstrani_znak_onesnaženost = """
    UPDATE vreme
    SET pm10 = trim(pm10, '<'),
        so2 = trim(so2, '<'),
        co = trim(co, '<'),
        o3 = trim(o3, '<'),
        no2 = trim(no2, '<');
"""


def posodobi_podatkovno(podatkovna: str = "ljubljana-2020-11.db",
                        kraj: str = "Ljubljana",
                        ):

    povezava = poveži_podatkovno(podatkovna)

    podatki = vremenko.vreme.vremenko_podatki(kraj)

    if not podatki.onesnaženost:
        podatki_vreme = podatki.vreme[:8] + \
            podatki.veter[:3] + tuple([0 for i in range(6)])
    else:
        podatki_vreme = podatki.vreme[:8] + \
            podatki.veter[:3] + podatki.onesnaženost

    # tabela dan
    izvedi_ukaz(povezava, ustvari_dan)
    izvedi_ukaz(povezava, vnesi_dan, *podatki.dan[:5])

    # tabela vreme
    izvedi_ukaz(povezava, ustvari_vremenko)
    izvedi_ukaz(povezava, vnesi_vremenko, *podatki_vreme)
    izvedi_ukaz(povezava, odstrani_znak_onesnaženost)


if __name__ == '__main__':
    posodobi_podatkovno()
