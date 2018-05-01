#!/usr/bin/env python
# -*- coding: 'UTF-8' -*-

import requests
import argparse
from lxml import etree
# from datetime import datetime


BASE = ('http://meteo.arso.gov.si/uploads/probase/www/observ/surface/text/sl/'
        'observationAms_')

# slovar s kombinacijo povezav: osnova + končnica
KRAJI = {
    'Ljubljana': (BASE + 'LJUBL-ANA_BEZIGRAD_latest.xml'),
    'Novo mesto': (BASE + 'NOVO-MES_latest.xml'),
    'Rogaška Slatina': (BASE + 'ROGAS-SLA_latest.xml'),
    'Metlika': (BASE + 'METLIKA_latest.xml'),
    'Črnomelj': (BASE + 'CRNOMELJ_latest.xml'),
    'Metlika': (BASE + 'METLIKA_latest.xml'),
    'Koper': (BASE + 'KOPER_KAPET-IJA_latest.xml'),
    'Celje': (BASE + 'CELJE_MEDLOG_latest.xml'),
    'Kočevje': (BASE + 'KOCEVJE_latest.xml'),
    'Maribor': (BASE + 'MARIBOR_VRBAN-PLA_latest.xml'),
    'Podčetrtek': (BASE + 'PODCE-TEK_ATOMS-TOP_latest.xml'),
    'Bilje pri Novi Gorici': (BASE + 'NOVA-GOR_BILJE_latest.xml'),
    'Marinča vas': (BASE + 'MARIN-VAS_latest.xml'),
    'Nanos (1242 m)': (BASE + 'NANOS_latest.xml'),
    'Rogla (1494 m)': (BASE + 'ROGLA_latest.xml'),
    'Kredarica (2514 m)': (BASE + 'KREDA-ICA_latest.xml'),
}

# seznam s potjo do podatka (xpath) v XML-datoteki in imenom kategorije
# prenos v ločeno datoteko?
KATEGORIJE = [
    ['/data/metData/nn_icon-wwsyn_icon', 'Opis vremena'],
    ['/data/metData/t', 'Temperatura', '°C'],
    ['/data/metData/rhavg', 'Relativna vlažnost', '%'],
    ['/data/metData/rr_val', 'Vsota padavin v časovnem intervalu', 'mm'],
    ['/data/metData/mslavg', 'Tlak', 'hPa'],
    ['/data/metData/ddavg_longText', 'Smer vetra'],
    ['/data/metData/ffavg_val', 'Hitrost vetra', 'm/s'],
    ['/data/metData/sunrise', 'Sončni vzhod'],
    ['/data/metData/sunset', 'Sončni zahod'],
    ['/data/metData/gSunRadavg', 'Povprečno sončno obsevanje', 'W/m2'],
]

# prevod oznak za vremenske razmere
# prenos v ločeno datoteko?
OPIS = {
    'clear': 'jasno',
    'mostClear': 'pretežno jasno',
    'partCloudy': 'delno oblačno',
    'modCloudy': 'zmerno oblačno',
    'prevCloudy': 'pretežno oblačno',
    'overcast': 'oblačno',
    'FG': 'megla',
    'RA': 'rosenje',
    'RASN': 'dež s snegom',
    'SN': 'sneženje',
    'TS': 'nevihte',
    'TSGR': 'nevihta s točo',
    'lightRA': 'manjše padavine',
    'modRA': 'zmerne padavine',
    'overcast_lightRA': 'oblačno z manjšimi padavinami',
    'overcast_modRA': 'oblačno z zmernimi padavinami',
    'overcast_heavyRA': 'oblačno z močnimi padavinami',
    'prevCloudy_lightRA': 'pretežno oblačno z manjšimi padavinami',
    'overcast_lightSN': 'oblačno z manjšim sneženjem'
}


def pridobi_spletno_stran(naslov=KRAJI["Ljubljana"], kraj="Ljubljana"):
    r = requests.get(naslov)
    '''
    [38:] zaradi konflikta med deklaracijo kodiranja in znaki

    ValueError: Unicode strings with encoding declaration are not supported.\
    Please use bytes input or XML fragments without declaration.
    '''
    stran = etree.fromstring(r.text[38:])

    # zdaj = datetime.now()
    # # TODO absolute path
    # datoteka = "data/vremenko_%(k)s_%(d)s.xml"\
    #             % { "k": kraj, "d": zdaj.strftime('%d-%m-%Y_%H-%M')}
    # with open(datoteka, "w") as f:
    #     f.write(r.text[38:])

    return stran


def izpis(root, kraj, opis=OPIS):
    print(f'Podatki za mesto {kraj}.')
    for i in KATEGORIJE:
        try:
            p = root.xpath(i[0])[0].text
            # opis vremena
            if i == KATEGORIJE[0]:
                print(f'\t{i[1]}: {opis[p]}.')
            # z enoto
            elif len(i) == 3:
                print(f'\t{i[1]}: {p} {i[2]}.')
            # brez enote
            else:
                print(f'\t{i[1]}: {p}.')
        except TypeError:
            print(f'\t{i[1]}: Ni podatka. (TypeError)')
        except KeyError:
            print(f'\t{i[1]}: Ni podatka. (KeyError)')
        except IndexError:
            print('Podatkov za ta kraj trenutno žal ni.')
            break


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
        root = pridobi_spletno_stran(KRAJI[naslov])
        izpis(root, naslov)
    except requests.exceptions.ConnectionError:
        print("\nPodatki so trenutno nedosegljivi.\n")


if __name__ == '__main__':
    main()
