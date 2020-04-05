#!/usr/bin/env python
# -*- coding: 'UTF-8' -*-

from typing import NamedTuple
import datetime
import nastavitve as n
import poštar

# TODO komentarji, decimalna števila


class Vreme(NamedTuple):
    opis_vremena: str
    temperatura: str  # zaenkrat
    relativna_vlaga: int
    tlak: str  # zaenkrat
    sončno_obsevanje: str  # zaenkrat
    vsota_padavin: str  # zaenkrat
    temperatura_enota: str = '°C'
    relativna_vlaga_enota: str = '%'
    tlak_enota: str = 'hPa'
    sončno_obsevanje_enota: str = 'W/m2'
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


def vreme_podatki(stran):
    if stran is None:
        return None

    try:
        opis_vremena = n.OPIS[stran.xpath(n.VREME["Opis vremena"])[0].text]
    except KeyError:
        opis_vremena = None

    try:
        temperatura = stran.xpath(n.VREME["Temperatura"][0])[0].text
    except KeyError:
        temperatura = None
        temperatura_enota = None
    else:
        temperatura_enota = n.VREME["Temperatura"][1]

    try:
        relativna_vlaga = int(stran.xpath(
            n.VREME["Relativna vlaga"][0])[0].text)
    except KeyError:
        relativna_vlaga = None
        relativna_vlaga_enota = None
    else:
        relativna_vlaga_enota = n.VREME["Relativna vlaga"][1]

    try:
        # TODO decimalno število
        tlak = stran.xpath(n.VREME["Tlak"][0])[0].text
    except KeyError:
        tlak = None
        tlak_enota = None
    else:
        tlak_enota = n.VREME["Tlak"][1]

    try:
        sončno_obsevanje = stran.xpath(
            n.VREME['Povprečno sončno obsevanje'][0])[0].text
    except KeyError:
        sončno_obsevanje = None
        sončno_obsevanje_enota = None
    else:
        if sončno_obsevanje == '0':
            sončno_obsevanje = None
            sončno_obsevanje_enota = None
        else:
            sončno_obsevanje_enota = n.VREME['Povprečno sončno obsevanje'][1]

    try:
        # TODO decimalno število
        vsota_padavin = stran.xpath(n.VREME["Vsota padavin"][0])[0].text
    except KeyError:
        vsota_padavin = None
        vsota_padavin_enota = None
    else:
        vsota_padavin_enota = n.VREME["Vsota padavin"][1]

    return Vreme(opis_vremena=opis_vremena,
                 temperatura=temperatura,
                 relativna_vlaga=relativna_vlaga,
                 tlak=tlak,
                 sončno_obsevanje=sončno_obsevanje,
                 vsota_padavin=vsota_padavin,
                 temperatura_enota=temperatura_enota,
                 relativna_vlaga_enota=relativna_vlaga_enota,
                 tlak_enota=tlak_enota,
                 sončno_obsevanje_enota=sončno_obsevanje_enota,
                 vsota_padavin_enota=vsota_padavin_enota,
                 )


def vreme_izpis(vreme, kraj='Ljubljana'):
    if vreme is None:
        return "Podatkov o vremenu trenutno ni."
    elif not any(vreme):
        return "Podatkov o vremenu trenutno ni."

    izpis = f'Podatki za {n.KRAJI_SKLONI[kraj]}.\n'

    if vreme.opis_vremena:
        izpis += f'{vreme.opis_vremena}. '

    if vreme.temperatura:
        izpis += (f'Temperatura zraka je '
                  f'{vreme.temperatura.replace(".", ",")} '
                  f'{vreme.temperatura_enota}')

    if vreme.relativna_vlaga:
        izpis += (f', relativna vlažnost znaša '
                  f'{vreme.relativna_vlaga} '
                  f'{vreme.relativna_vlaga_enota}')

    if vreme.tlak:
        izpis += (f', zračni tlak je '
                  f'{vreme.tlak.replace(".", ",")} '
                  f'{vreme.tlak_enota}. ')
    else:
        izpis += '. '

    if vreme.sončno_obsevanje:
        izpis += (f'Sončno obsevanje znaša {vreme.sončno_obsevanje} '
                  f'{vreme.sončno_obsevanje_enota}. ')

    if vreme.vsota_padavin != '0':
        izpis += (f'Zapadlo je '
                  f'{vreme.vsota_padavin} '
                  f'{vreme.vsota_padavin_enota} padavin.')
    return izpis


def veter_podatki(stran):
    if stran is None:
        return None

    try:
        smer_vetra = stran.xpath(n.VETER["Smer vetra"])[0].text
    except KeyError:
        smer_vetra = None

    try:
        hitrost_vetra = stran.xpath(n.VETER["Hitrost vetra"][0])[
            0].text.replace(".", ",")
    except (KeyError, AttributeError):
        hitrost_vetra = None
        hitrost_vetra_enota = None
    else:
        hitrost_vetra_enota = n.VETER["Hitrost vetra"][1]

    try:
        sunki_vetra = stran.xpath(n.VETER["Sunki vetra"][0])[
            0].text.replace(".", ",")
    except (KeyError, AttributeError):
        sunki_vetra = None
        sunki_vetra_enota = None
    else:
        sunki_vetra_enota = n.VETER["Sunki vetra"][1]

    return Veter(smer_vetra=smer_vetra,
                 hitrost_vetra=hitrost_vetra,
                 sunki_vetra=sunki_vetra,
                 hitrost_vetra_enota=hitrost_vetra_enota,
                 sunki_vetra_enota=sunki_vetra_enota,
                 )


def veter_izpis(veter):
    if veter is None:
        return None

    elif not any(veter):
        return None

    izpis = (f'Piha {veter.smer_vetra} '
             f's hitrostjo '
             f'{veter.hitrost_vetra} {veter.hitrost_vetra_enota} '
             f'in sunki do {veter.sunki_vetra} {veter.sunki_vetra_enota}. ')
    return izpis


def onesnaženost_podatki(stran,
                         kraj='Ljubljana',
                         šifre=n.ZRAK_ŠIFRE,
                         kategorije=n.ZRAK_KATEGORIJE):
    if stran is None:
        return None

    šifra = šifre[kraj]
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


def onesnaženost_izpis(rezultat,
                       enote=n.ZRAK_KATEGORIJE):
    if rezultat is None:
        return "Podatkov o kakovosti zraka trenutno ni."

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


def dan_uredi_podatke(niz):
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


def dan_podatki(stran):
    # <class 'tuple'>: ('1. 4. 2020',
    #                   '6.41',
    #                   datetime.datetime(2020, 4, 1, 6, 41))
    vzhod = dan_uredi_podatke(stran.xpath('/data/metData/sunrise')[0].text)
    zahod = dan_uredi_podatke(stran.xpath('/data/metData/sunset')[0].text)

    # <class 'list'>: ['2020', '04', '01']
    x = stran.xpath(
        '/data/metData/sunrise')[0].text.split(' ')[0].split('.')[::-1]
    datum = datetime.date(int(x[0]), int(x[1]), int(x[2]))
    zaporedni_v_letu = datum - datetime.date(int(x[0]), 1, 1)
    datum = '. '.join(i.lstrip('0') for i in x[::-1])
    dolžina_dneva = zahod[2] - vzhod[2]
    dolž_dneva_ure = str(int(dolžina_dneva.total_seconds() // 3660))
    dolž_dneva_min = str(int(dolžina_dneva.total_seconds() % 3600) // 60)
    if len(dolž_dneva_min) == 1:
        dolž_dneva_min = f'0{dolž_dneva_min}'
    dolžina_dneva = f'{dolž_dneva_ure}.{dolž_dneva_min}'
    return Dan(datum=datum,
               vzhod=vzhod[1],
               zahod=zahod[1],
               dolžina_dneva=dolžina_dneva,
               zaporedni_v_letu=zaporedni_v_letu.days,)


def dan_izpis(dan):
    izpis = (f'Sončni vzhod je ob {dan.vzhod}, zahod ob {dan.zahod}, dan '
             f'traja {dan.dolžina_dneva}. Danes je {dan.datum}, tj. '
             f'{dan.zaporedni_v_letu}. dan v letu.')
    return izpis


def vreme_ni_podatkov():
    return 'Podatkov o vremenu trenutno ni.'


def ni_povezave():
    return 'Podatki so trenutno nedosegljivi.'


def vremenko_izpis(kraj='Ljubljana'):
    stran_vreme = poštar.pridobi_vremenske_podatke(n.KRAJI_URL[kraj], kraj)
    stran_onesnaženost = poštar.pridobi_vremenske_podatke(n.ZRAK)

    if (stran_vreme is None) and (stran_onesnaženost is None):
        return ni_povezave()

    elif stran_vreme is None:
        return vreme_ni_podatkov(kraj)

    else:
        izpis = ''
        izpis_vreme = vreme_izpis(vreme_podatki(stran_vreme), kraj)
        if izpis_vreme:
            izpis += izpis_vreme

        izpis_veter = veter_izpis(veter_podatki(stran_vreme))
        if izpis_veter:
            izpis += izpis_veter

        izpis_dolžina_dneva = dan_izpis(dan_podatki(stran_vreme))
        if izpis_dolžina_dneva:
            izpis += izpis_dolžina_dneva

        if kraj in ('Ljubljana', 'Maribor', 'Celje', 'Murska Sobota', 'Koper',
                    'Nova Gorica', 'Trbovlje', 'Zagorje'):
            izpis += '\n' + onesnaženost_izpis(
                onesnaženost_podatki(stran_onesnaženost, kraj))
    return izpis


def main():
    print(vremenko_izpis())


if __name__ == '__main__':
    main()
