#!/usr/bin/env python
# -*- coding: 'UTF-8' -*-

import argparse
import logging

import vremenko.podatkovna


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
    logger = logging.getLogger(__name__)
    return logger


def argumenti():
    """
    Razbere ukaz iz ukazne vrstice.
    """
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
    parser.add_argument("-l", "--log", action="store_true", default=3,
                        help="vrsta dnevniških vnosov")
    return parser.parse_args()


def main():
    args = argumenti()
    logger = beleženje(args.dnevnik, args.log)
    vremenko.podatkovna.posodobi_podatkovno(args.podatkovna,
                                            args.kraj,
                                            )
    logger.info("Program se je uspešno izvedel.")


if __name__ == '__main__':
    main()
