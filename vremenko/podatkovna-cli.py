#!/usr/bin/env python
# -*- coding: 'UTF-8' -*-

import argparse
import vremenko.podatkovna


def argumenti():
    '''
    Razbere ukaz iz ukazne vrstice.
    '''
    parser = argparse.ArgumentParser(
        description="Preprost program, ki zapiše trenutne vremenske razmere \
                     v podatkovno bazo. Podatke pridobi z ARSO-ve spletne \
                     strani.",
        epilog="Primer rabe: \
                python podatkovna-cli.py novo-mesto-20-11.db 'Novo mesto'"
    )
    parser.add_argument("podatkovna", help="podatkovna baza")
    parser.add_argument("kraj", help="kraj")
    parser.add_argument("dnevnik", help="dnevnik")
    return parser.parse_args()


def main():
    args = argumenti()
    vremenko.podatkovna.posodobi_podatkovno(args.podatkovna,
                                            args.kraj,
                                            args.dnevnik
                                            )


if __name__ == '__main__':
    main()
