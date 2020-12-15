#!/usr/bin/env python
# -*- coding: 'UTF-8' -*-

import argparse
import logging
import __version__
import vremenko.beleženje
from vremenko.vreme import vremenko_izpis
from vremenko.nastavitve import KRAJI_SKLONI, URL_VREME_KRAJ


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


def argumenti():
    """
    razbere ukaz iz ukazne vrstice
    """
    parser = argparse.ArgumentParser(
        description="Preprost program, ki izpiše trenutne vremenske razmere.\
                    Podatke pridobi z ARSO-ve spletne strani.",
        prog="vremenko",
        epilog="Primer rabe: vreme izpis novo-mesto"
    )
    parser.add_argument("-l", "--log", type=int, default=4,
                        help="vrsta dnevniških vnosov")
    parser.add_argument("--dnevnik", type=str,
                        help="beleženje v datoteko")
    parser.add_argument("--kratko", action="store_true", default=False,
                        help="kratka oblika izpisa v alinejah")
    parser.add_argument("-v", "--verzija", action="version",
                        version="%(prog)s {version}".format(
                            version=__version__.__version__))
    subparsers = parser.add_subparsers(dest="ukaz")
    parser_kraji = subparsers.add_parser("kraji")

    parser_izpis = subparsers.add_parser("izpis")
    parser_izpis.add_argument("kraj", nargs="?", default="Ljubljana")

    return parser.parse_args()


def ukaznavrstica():
    args = argumenti()
    vremenko.beleženje.beleženje(args.dnevnik, args.log)

    if args.ukaz == "kraji":
        naslov = uporabnikovo_izbiranje_kraja(URL_VREME_KRAJ)
        print("")
    elif args.ukaz == "izpis":
        if args.kraj.lower().replace("-", " ") in URL_VREME_KRAJ:
            naslov = args.kraj.lower().replace("-", " ")
        elif args.kraj:
            naslov = args.kraj
    else:
        naslov = "Ljubljana"
    print(vremenko_izpis(naslov.lower(), args.kratko))


if __name__ == "__main__":
    ukaznavrstica()
