#!/usr/bin/env python
# -*- coding: 'UTF-8' -*-

import requests
from lxml import etree
import datetime
from nastavitve import *


def pridobi_spletno_stran(naslov=KRAJI["Ljubljana"],
                          kraj="Ljubljana"):
    r = requests.get(naslov)
    stran = etree.fromstring(bytes(r.text, encoding='utf8'))
    return stran


def onesnaženost_zraka(kraj='Ljubljana',
                       naslov=ONESNAŽENOST,
                       šifre=ŠIFRE_ONESNAŽENOSTI,
                       kategorije=KATEGORIJE_ONESNAŽENOSTI):
    šifra = šifre[kraj]
    stran = pridobi_spletno_stran(naslov)
    rezultat = {}
    čist_zrak = True
    for i in kategorije:
        try:
            rezultat[i] = stran.xpath(
                f'/arsopodatki/postaja[@sifra="{šifra}"]/{i}')[0].text
        except IndexError:
            pass
        else:
            if rezultat[i]:
                if int(float(rezultat[i])) >= int(kategorije[i][1]):
                    čist_zrak = False
    return (rezultat, čist_zrak)


def izpis(stran, kraj):
    print(vreme(stran, kraj))
    print(veter(stran))
    print(izpis_dolžine_dneva(dolžina_dneva(stran)))
    if kraj in ('Ljubljana', 'Maribor', 'Celje', 'Murska Sobota', 'Koper'
                'Nova Gorica', 'Trbovlje', 'Zagorje'):
        print(izpis_onesnaženosti(onesnaženost_zraka(kraj)))


def izpis_onesnaženosti(rezultat, enote=KATEGORIJE_ONESNAŽENOSTI):
    izpis = ''
    if not rezultat[1]:
        izpis += 'POZOR! Zrak je onesnažen.\n'
    for kategorija, vrednost in rezultat[0].items():
        if vrednost:
            izpis += (f'{kategorija.upper()}: {vrednost} {enote[kategorija][0]} '
                      f'(mejna vrednost: {enote[kategorija][1]} '
                      f'{enote[kategorija][0]}).\n')
    return izpis.rstrip()


def veter(stran):
    izpis = (f'Piha {stran.xpath(VETER["Smer vetra"])[0].text} s hitrostjo '
             f'{stran.xpath(VETER["Hitrost vetra"][0])[0].text.replace(".", ",")} '
             f'{VETER["Hitrost vetra"][1]} '
             f'in sunki do '
             f'{stran.xpath(VETER["Sunki vetra"][0])[0].text.replace(".", ",")} '
             f'{VETER["Sunki vetra"][1]}.')
    return izpis


def vreme(stran, kraj='Ljubljana'):
    izpis = f'Podatki za mesto {kraj}.\n'
    # opis vremena
    if stran.xpath(VREME["Opis vremena"])[0].text:
        izpis += f'{OPIS[stran.xpath(VREME["Opis vremena"])[0].text]}. '

    # temperatura in vlažnost
    izpis += (f'Temperatura zraka je '
              f'{stran.xpath(VREME["Temperatura"][0])[0].text.replace(".", ",")} '
              f'{VREME["Temperatura"][1]}')

    # vlažnost
    izpis += (f', relativna vlažnost znaša '
              f'{stran.xpath(VREME["Relativna vlažnost"][0])[0].text} '
              f'{VREME["Relativna vlažnost"][1]}')

    # tlak
    if stran.xpath(VREME["Tlak"][0])[0].text:
        izpis += (f', zračni tlak je '
                  f'{stran.xpath(VREME["Tlak"][0])[0].text.replace(".", ",")} '
                  f'{VREME["Tlak"][1]}. ')
    else:
        izpis += '. '

    # padavine
    if stran.xpath(VREME["Vsota padavin v časovnem intervalu"][0])[0].text != '0':
        izpis += (f'Zapadlo je {stran.xpath(VREME["Vsota padavin v časovnem intervalu"][0])[0].text} '
                  f'{VREME["Vsota padavin v časovnem intervalu"][1]} padavin.')
    return izpis


def popravi_datum_uro(niz):
    x = niz.split(' ')[:-1]
    # ura
    ura = x[1].replace(':', '.')

    # datum
    datum = x[0].split('.')
    for i in range(len(datum)):
        datum[i] = datum[i].lstrip('0')

    # datetime.time
    cifre_datum = [int(i) for i in datum]
    cifre_ura = x[1].split(':')
    izr_ura = datetime.datetime(cifre_datum[2], cifre_datum[1], cifre_datum[0], int(
        cifre_ura[0]), int(cifre_ura[1]))

    return ('. '.join(datum), ura, izr_ura)


def dolžina_dneva(stran):
    vzhod = popravi_datum_uro(stran.xpath('/data/metData/sunrise')[0].text)
    zahod = popravi_datum_uro(stran.xpath('/data/metData/sunset')[0].text)
    d1 = stran.xpath(
        '/data/metData/sunrise')[0].text.split(' ')[0].split('.')[::-1]
    datum = datetime.date(int(d1[0]), int(d1[1]), int(d1[2]))
    dni_od_začetka_leta = datum - datetime.date(int(d1[0]), 1, 1)
    dolžina_dneva = zahod[2] - vzhod[2]
    dolžina_dneva_ure = dolžina_dneva.total_seconds() // 3660
    dolžina_dneva_minute = (dolžina_dneva.total_seconds() % 3600) // 60
    dolžina_dneva = f'{str(int(dolžina_dneva_ure))}.{str(int((dolžina_dneva_minute)))}'
    return (vzhod[1], zahod[1], dni_od_začetka_leta.days, dolžina_dneva)


def izpis_dolžine_dneva(podatki):
    izpis = (f'Sončni vzhod je ob {podatki[0]}, zahod ob {podatki[1]}, dan '
             f'traja {podatki[3]}. Danes je {podatki[2]}. dan v letu.')
    return izpis
