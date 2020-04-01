#!/usr/bin/env python
# -*- coding: 'UTF-8' -*-

from typing import NamedTuple
import requests
from lxml import etree
import datetime
import nastavitve as n

# TODO komentarji, decimalna števila


class Vreme(NamedTuple):
    opis_vremena: str
    temperatura: str  # zaenkrat
    relativna_vlaga: int
    tlak: str  # zaenkrat
    vsota_padavin: str  # zaenkrat
    temperatura_enota: str = '°C'
    relativna_vlaga_enota: str = '%'
    tlak_enota: str = 'hPa'
    vsota_padavin_enota: str = 'mm'


class Veter(NamedTuple):
    smer_vetra: str
    hitrost_vetra: str  # zaenkrat
    sunki_vetra: str  # zaenkrat
    hitrost_vetra_enota: str = 'm/s'
    sunki_vetra_enota: str = 'm/s'


class Dan(NamedTuple):
    datum: str
    vzhod: str
    zahod: str
    dolžina_dneva: str
    zaporedni_v_letu: str


def pridobi_spletno_stran(naslov=n.KRAJI["Ljubljana"],
                          kraj="Ljubljana"):
    r = requests.get(naslov)
    stran = etree.fromstring(bytes(r.text, encoding='utf8'))
    return stran


def vreme(stran):
    try:
        opis_vremena = n.OPIS[stran.xpath(n.VREME["Opis vremena"])[0].text]
    except KeyError:
        opis_vremena = None

    try:
        temperatura = stran.xpath(n.VREME["Temperatura"][0])[0].text
    except KeyError:
        temperatura = None
    else:
        temperatura_enota = n.VREME["Temperatura"][1]

    try:
        relativna_vlaga = int(stran.xpath(
            n.VREME["Relativna vlaga"][0])[0].text)
    except KeyError:
        relativna_vlaga = None
    else:
        relativna_vlaga_enota = n.VREME["Relativna vlaga"][1]

    try:
        # TODO decimalno število
        tlak = stran.xpath(n.VREME["Tlak"][0])[0].text
    except KeyError:
        tlak = None
    else:
        tlak_enota = n.VREME["Tlak"][1]

    try:
        # TODO decimalno število
        vsota_padavin = stran.xpath(n.VREME["Vsota padavin"][0])[0].text
    except KeyError:
        vsota_padavin = None
    else:
        vsota_padavin_enota = n.VREME["Vsota padavin"][1]

    return Vreme(opis_vremena=opis_vremena,
                 temperatura=temperatura,
                 relativna_vlaga=relativna_vlaga,
                 tlak=tlak,
                 vsota_padavin=vsota_padavin,
                 temperatura_enota=temperatura_enota,
                 relativna_vlaga_enota=relativna_vlaga_enota,
                 tlak_enota=tlak_enota,
                 vsota_padavin_enota=vsota_padavin_enota,
                 )


def izpis_vremena(vreme, kraj='Ljubljana'):
    if not any(vreme):
        return "Podatkov o vremenu trenutno ni."

    izpis = f'Podatki za mesto {kraj}.\n'
    # opis vremena
    if vreme.opis_vremena:
        izpis += f'{vreme.opis_vremena}. '

    # temperatura in vlažnost
    izpis += (f'Temperatura zraka je '
              f'{vreme.temperatura.replace(".", ",")} '
              f'{vreme.temperatura_enota}')

    # vlažnost
    izpis += (f', relativna vlažnost znaša '
              f'{vreme.relativna_vlaga} '
              f'{vreme.relativna_vlaga_enota}')

    # tlak
    if vreme.tlak:
        izpis += (f', zračni tlak je '
                  f'{vreme.tlak.replace(".", ",")} '
                  f'{vreme.tlak_enota}. ')
    else:
        izpis += '. '

    # padavine
    if vreme.vsota_padavin != '0':
        izpis += (f'Zapadlo je '
                  f'{vreme.vsota_padavin} '
                  f'{vreme.vsota_padavin_enota} padavin.')
    return izpis


def veter(stran):
    try:
        smer_vetra = stran.xpath(n.VETER["Smer vetra"])[0].text
    except KeyError:
        smer_vetra = None
    try:
        hitrost_vetra = stran.xpath(n.VETER["Hitrost vetra"][0])[
            0].text.replace(".", ",")
    except KeyError:
        hitrost_vetra = None
    else:
        hitrost_vetra_enota = n.VETER["Hitrost vetra"][1]

    try:
        sunki_vetra = stran.xpath(n.VETER["Sunki vetra"][0])[
            0].text.replace(".", ",")
    except KeyError:
        sunki_vetra = None
    else:
        sunki_vetra_enota = n.VETER["Sunki vetra"][1]

    return Veter(smer_vetra=smer_vetra,
                 hitrost_vetra=hitrost_vetra,
                 sunki_vetra=sunki_vetra,
                 hitrost_vetra_enota=hitrost_vetra_enota,
                 sunki_vetra_enota=sunki_vetra_enota,
                 )


def izpis_vetra(veter):
    if not any(veter):
        return

    izpis = (f'Piha {veter.smer_vetra} '
             f's hitrostjo '
             f'{veter.hitrost_vetra} {veter.hitrost_vetra_enota} '
             f'in sunki do {veter.sunki_vetra} {veter.sunki_vetra_enota}.')
    return izpis


def onesnaženost_zraka(kraj='Ljubljana',
                       naslov=n.ONESNAŽENOST,
                       šifre=n.ŠIFRE_ONESNAŽENOSTI,
                       kategorije=n.KATEGORIJE_ONESNAŽENOSTI):
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


def izpis_onesnaženosti(rezultat,
                        enote=n.KATEGORIJE_ONESNAŽENOSTI):
    izpis = ''
    if not rezultat[1]:
        izpis += 'POZOR! Zrak je onesnažen.\n'
    for kategorija, vrednost in rezultat[0].items():
        if vrednost:
            izpis += (f'{kategorija.upper()}: '
                      f'{vrednost} {enote[kategorija][0]} '
                      f'(mejna vrednost: {enote[kategorija][1]} '
                      f'{enote[kategorija][0]}).\n')
    return izpis.rstrip()


def popravi_datum_uro(niz):
    x = niz.split(' ')[:-1]
    ura = x[1].replace(':', '.')
    datum = x[0].split('.')
    for i in range(len(datum)):
        datum[i] = datum[i].lstrip('0')
    # datetime.time
    cifre_datum = [int(i) for i in datum]
    cifre_ura = x[1].split(':')
    izr_ura = (datetime.datetime(cifre_datum[2],
                                 cifre_datum[1],
                                 cifre_datum[0],
                                 int(cifre_ura[0]),
                                 int(cifre_ura[1])))
    return ('. '.join(datum), ura, izr_ura)


def dolžina_dneva(stran):
    # <class 'tuple'>: ('1. 4. 2020',
    #                   '6.41',
    #                   datetime.datetime(2020, 4, 1, 6, 41))
    vzhod = popravi_datum_uro(stran.xpath('/data/metData/sunrise')[0].text)
    zahod = popravi_datum_uro(stran.xpath('/data/metData/sunset')[0].text)

    # <class 'list'>: ['2020', '04', '01']
    d = stran.xpath(
        '/data/metData/sunrise')[0].text.split(' ')[0].split('.')[::-1]
    datum = datetime.date(int(d[0]), int(d[1]), int(d[2]))
    zaporedni_v_letu = datum - datetime.date(int(d[0]), 1, 1)
    datum = '. '.join(i.lstrip('0') for i in d[::-1])
    dolžina_dneva = zahod[2] - vzhod[2]
    dolž_dneva_ure = dolžina_dneva.total_seconds() // 3660
    dolž_dneva_min = (dolžina_dneva.total_seconds() % 3600) // 60
    dolžina_dneva = f'{str(int(dolž_dneva_ure))}.{str(int((dolž_dneva_min)))}'
    return Dan(datum=datum,
               vzhod=vzhod[1],
               zahod=zahod[1],
               dolžina_dneva=dolžina_dneva,
               zaporedni_v_letu=zaporedni_v_letu.days,)


def izpis_dolžine_dneva(dan):
    izpis = (f'Sončni vzhod je ob {dan.vzhod}, zahod ob {dan.zahod}, dan '
             f'traja {dan.dolžina_dneva}. Danes je {dan.datum}, tj. '
             f'{dan.zaporedni_v_letu}. dan v letu.')
    return izpis


def izpis(stran,
          kraj):
    izpis_vreme = izpis_vremena(vreme(stran), kraj)
    if izpis_vreme:
        print(izpis_vreme)

    izpis_veter = izpis_vetra(veter(stran))
    if izpis_veter:
        print(izpis_veter)

    izpis_dolžina_dneva = izpis_dolžine_dneva(dolžina_dneva(stran))
    if izpis_dolžina_dneva:
        print(izpis_dolžina_dneva)

    if kraj in ('Ljubljana', 'Maribor', 'Celje', 'Murska Sobota', 'Koper'
                'Nova Gorica', 'Trbovlje', 'Zagorje'):
        print(izpis_onesnaženosti(onesnaženost_zraka(kraj)))
