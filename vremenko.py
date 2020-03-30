#!/usr/bin/env python
# -*- coding: 'UTF-8' -*-

import argparse
from nastavitve import *
from pamet import *


def izbira_kraja(KRAJI):
    '''
    Uporabnik izbere kraj.
    Funkcija vrne seznam:
    - s polno povezavo (osnova + končnica),
    - z imenom kraja (npr. 'Metlika').
    '''
    moznosti = list(KRAJI.keys())
    while True:
        print('\nPodatki za kraje, ki so na voljo:')
        for i in range(len(moznosti)):
            print(f'\t({str(i + 1)})  {moznosti[i]}')
        try:
            vnos = int(input(f'Vnesi izbiro: (1-{str(len(moznosti))})\t'))
            if vnos < 1:
                continue
        except (ValueError, IndexError):
            print('Neveljavna izbira.')
            continue
        except KeyboardInterrupt:
            print('\nIzhod.')
            exit(0)
        else:
            break
    return [KRAJI[(moznosti[vnos - 1])], moznosti[vnos - 1]]


def argumenti():
    '''
    Razbere ukaz iz ukazne vrstice.
    '''
    parser = argparse.ArgumentParser(
        description="Preprost program, ki izpiše trenutne vremenske razmere.\
                    Podatke pridobi z ARSO-ve spletne strani.",
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
    return parser.parse_args()


def main():
    args = argumenti()
    if args.izbira:
        naslov = izbira_kraja(KRAJI)[1]
        print('')
    elif args.novomesto:
        naslov = "Novo mesto"
    elif args.rogaska:
        naslov = 'Rogaška Slatina'
    else:
        naslov = 'Ljubljana'
    try:
        stran = pridobi_spletno_stran(KRAJI[naslov])
        izpis(stran, naslov)
    except requests.exceptions.ConnectionError:
        print("\nPodatki so trenutno nedosegljivi.\n")


if __name__ == '__main__':
    main()
