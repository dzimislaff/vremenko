#!/usr/bin/env python
# -*- coding: 'UTF-8' -*-

import argparse
import logging
import __version__
import vremenko.beleženje
import vremenko.vreme
from vremenko.nastavitve import URL_VREME_KRAJ


def izbira_kraja(KRAJI):
    '''
    Uporabnik izbere kraj.
    Funkcija vrne seznam:
    - s polno povezavo (osnova + končnica),
    - z imenom kraja (npr. 'Metlika').
    '''
    moznosti = list(URL_VREME_KRAJ.keys())
    while True:
        print('\nPodatki za kraje, ki so na voljo:')
        for i in range(len(moznosti)):
            print(f'\t({str(i + 1)})  {moznosti[i]}')
        try:
            vnos = int(input(f'Vnesi izbiro: (1-{str(len(moznosti))})\t'))
            if vnos < 1:
                continue
        except (ValueError, IndexError) as e:
            logging.info(f"neveljavna izbira: {e}")
            print('Neveljavna izbira.')
            continue
        except KeyboardInterrupt as e:
            logging.info(f"izhod: {e}")
            print('\nIzhod.')
            exit(0)
        else:
            break
    return [URL_VREME_KRAJ[(moznosti[vnos - 1])], moznosti[vnos - 1]]


def argumenti():
    '''
    Razbere ukaz iz ukazne vrstice.
    '''
    parser = argparse.ArgumentParser(
        description="Preprost program, ki izpiše trenutne vremenske razmere.\
                    Podatke pridobi z ARSO-ve spletne strani.",
        prog="vremenko",
        # epilog="Primer rabe:"
    )
    parser.add_argument("-i", "--izbira", action="store_true",
                        help="prikaže izbire", default=False)
    parser.add_argument("-lj", "--ljubljana", action="store_true",
                        help="prikaže podatke za Ljubljano", default=False)
    parser.add_argument("-nm", "--novomesto", action="store_true",
                        help="podatki za Novo mesto", default=False)
    parser.add_argument("-rs", "--rogaska", action="store_true",
                        help="podatki za Rogaško Slatino", default=False)
    parser.add_argument("-l", "--log", type=int, default=4,
                        help="vrsta dnevniških vnosov")
    parser.add_argument("--dnevnik", type=str,
                        help="vrsta dnevniških vnosov")
    parser.add_argument("--kratko", action="store_true", default=False,
                        help="kratka oblika izpisa v alinejah")
    parser.add_argument("-v", "--verzija", action="version",
                        version='%(prog)s {version}'.format(
                            version=__version__.__version__))
    return parser.parse_args()


def ukaznavrstica():
    args = argumenti()
    vremenko.beleženje.beleženje(args.dnevnik, args.log)

    if args.izbira:
        naslov = izbira_kraja(URL_VREME_KRAJ)[1]
        print('')
    elif args.novomesto:
        naslov = "Novo mesto"
    elif args.rogaska:
        naslov = 'Rogaška Slatina'
    else:
        naslov = 'Ljubljana'
    print(vremenko.vreme.vremenko_izpis(naslov, args.kratko))


if __name__ == '__main__':
    ukaznavrstica()
