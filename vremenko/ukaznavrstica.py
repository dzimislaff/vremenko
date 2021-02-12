#!/usr/bin/env python
# -*- coding: 'UTF-8' -*-

import argparse
import logging
from __version__ import __version__
import vremenko.beleženje
from vremenko.vreme import vremenko_izpis
from vremenko.nastavitve import KRAJI_SKLONI, URL_VREME_KRAJ

opis_programa = ("Preprost program, ki trenutne vremenske razmere izpiše ali "
                 "shrani v podatkovno bazo. Podatke pridobi z ARSO-ve spletne "
                 "strani.")
ime_programa = "vremenko"
primer_rabe = "Primer rabe: vreme izpis novo-mesto"


def uporabnikovo_izbiranje_kraja(KRAJI: dict
                                 ) -> str:  # ime kraja, npr.: Krško
    """
    uporabniku ponudi seznam krajev
    """
    def neveljavna_izbira(e):
        logging.info(f"neveljavna izbira: {e}")
        print("\nNeveljavna izbira.")

    def izhod(e):
        logging.info(f"izhod: {e}")
        print("\nIzhod.")
        exit(0)

    def uvodno_sporočilo(možnosti: list
                         ) -> str:
        uvod = ["\nPodatki za kraje, ki so na voljo:"]
        [uvod.append(f"{i+1}.)  {možnosti[i]}") for i in range(len(možnosti))]
        return "\n\t".join(uvod)

    možnosti = list(KRAJI_SKLONI.keys())
    uvod = uvodno_sporočilo(možnosti)
    while True:
        print(uvod)
        try:
            vnos = int(input(f"Vnesi izbiro: (1–{str(len(možnosti))})\t"))
            assert not len(možnosti) < vnos and not vnos < 1
        except (ValueError, AssertionError) as e:
            neveljavna_izbira(e)
        except KeyboardInterrupt as e:
            izhod(e)
        else:
            break
    return možnosti[vnos - 1]


def ukazi():
    """
    razbere ukaz iz ukazne vrstice
    """
    parser = argparse.ArgumentParser(
        description=opis_programa,
        prog=ime_programa,
        epilog=primer_rabe
    )
    parser.add_argument("--log", type=int, default=4, choices=[1, 2, 3, 4, 5],
                        help="vrsta dnevniških vnosov")
    parser.add_argument("--dnevnik", type=str,
                        help="beleženje v datoteko")
    parser.add_argument("--kratko", action="store_true", default=False,
                        help="kratka oblika izpisa v alinejah")
    parser.add_argument("--verzija", action="version",
                        version="%(prog)s {version}".format(version=__version__))

    subparsers = parser.add_subparsers(dest="ukaz")
    parser_kraji = subparsers.add_parser("kraji")
    parser_izpis = subparsers.add_parser("izpis")
    parser_izpis.add_argument("kraj", nargs="?", default="Ljubljana")

    return (parser.parse_args(),  # ukaz
            parser)               # parser


def ukaznavrstica():
    izbrani_ukazi = ukazi()
    ukaz = izbrani_ukazi[0]
    parser = izbrani_ukazi[1]
    vremenko.beleženje.beleženje(ukaz.dnevnik, ukaz.log)

    if ukaz.ukaz == "kraji":
        naslov = uporabnikovo_izbiranje_kraja(URL_VREME_KRAJ)
        print("")
    elif ukaz.ukaz == "izpis":
        if ukaz.kraj.lower().replace("-", " ") in URL_VREME_KRAJ:
            naslov = ukaz.kraj.lower().replace("-", " ")
        else:
            parser.error("neveljavna izbira kraja")
    else:
        naslov = "Ljubljana"
    print(vremenko_izpis(naslov.lower(), ukaz.kratko))


if __name__ == "__main__":
    ukaznavrstica()
