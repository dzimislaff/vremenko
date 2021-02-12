#!/usr/bin/env python
# -*- coding: 'UTF-8' -*-

import argparse
import vremenko.beleženje
import vremenko.baza

opis_programa = ("Preprost program, ki zapiše trenutne vremenske razmere "
                 "v podatkovno bazo. Podatke pridobi z ARSO-ve spletne "
                 "strani.")
ime_programa = "podatkovna"
primer_rabe = ("Primer rabe:"
               "python podatkovna-cli.py novo-mesto-20-11.db 'Novo mesto'")


def argumenti():
    """
    razbere ukaz iz ukazne vrstice
    """
    parser = argparse.ArgumentParser(
        description=opis_programa,
        prog=ime_programa,
        epilog=primer_rabe)
    parser.add_argument("podatkovna", help="podatkovna baza")
    parser.add_argument("kraj", help="kraj")
    parser.add_argument("dnevnik", help="dnevnik")
    parser.add_argument("-l", "--log", type=int, default=4,
                        help="vrsta dnevniških vnosov")
    return parser.parse_args()


def main():
    args = argumenti()
    vremenko.beleženje.beleženje(args.dnevnik, args.log)
    vremenko.baza.posodobi_podatkovno(args.podatkovna,
                                      args.kraj.lower(),
                                      )


if __name__ == '__main__':
    main()
