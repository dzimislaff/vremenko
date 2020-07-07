#!/usr/bin/env python
# -*- coding: "UTF-8" -*-

from typing import NamedTuple
import datetime
import vremenko.nastavitve as n
import vremenko.poštar


class Vreme(NamedTuple):
    opis_vremena: str
    ura: str
    temperatura: str  # zaenkrat
    relativna_vlaga: int
    tlak: str  # zaenkrat
    sončno_obsevanje: str  # zaenkrat
    vsota_padavin: str  # zaenkrat
    temperatura_enota: str = "°C"
    relativna_vlaga_enota: str = "%"
    tlak_enota: str = "hPa"
    sončno_obsevanje_enota: str = "W/m2"
    vsota_padavin_enota: str = "mm"


class Veter(NamedTuple):
    smer_vetra: str
    hitrost_vetra: str  # zaenkrat
    sunki_vetra: str  # zaenkrat
    hitrost_vetra_enota: str = "m/s"
    sunki_vetra_enota: str = "m/s"


class Dan(NamedTuple):
    datum: str
    vzhod: str
    zahod: str
    dolžina_dneva: str
    zaporedni_v_letu: int


class Čas(NamedTuple):
    datum: str
    ura: str
    dtm: datetime.datetime


def preveri_dostopnost_podatkov(stran):
    if stran is None:
        return None
    elif len(stran.xpath('/data/metData')) == 0:
        return None
    else:
        return True


def vreme_podatki(stran  # lxml.etree._Element
                  ) -> Vreme:
    """
    vhod: lxml.etree._Element
    izhod: namedtuple, npr.: Vreme(opis_vremena="Jasno je",
                                   ura="18.30",
                                   temperatura="18.3",
                                   relativna_vlaga=21,
                                   tlak="1026.3",
                                   sončno_obsevanje="191",
                                   vsota_padavin="0",
                                   temperatura_enota="°C",
                                   relativna_vlaga_enota="%",
                                   tlak_enota="hPa",
                                   sončno_obsevanje_enota="W/m2",
                                   vsota_padavin_enota="mm")
    zahteve: typing.NamedTuple, lxml.etree
    izlušči podatke iz zapisa .xml z ARSO-ve spletne strani v namedtuple:
    opis_vremena, ura, temperatura, relativna_vlaga, tlak, sončno_obsevanje,
    vsota_padavin, temperatura_enota, relativna_vlaga_enota, tlak_enota,
    sončno_obsevanje_enota, vsota_padavin_enota
    """
    if not preveri_dostopnost_podatkov(stran):
        return None

    try:
        opis_vremena = n.OPIS[stran.xpath(n.VREME["Opis vremena"])[0].text]
    except KeyError:
        opis_vremena = None

    try:
        ura = čas_uredi(stran.xpath(
            "/data/metData/tsValid_issued")[0].text).ura
    except KeyError:
        ura = None

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
        tlak = stran.xpath(n.VREME["Tlak"][0])[0].text
    except KeyError:
        tlak = None
        tlak_enota = None
    else:
        tlak_enota = n.VREME["Tlak"][1]

    try:
        sončno_obsevanje = stran.xpath(
            n.VREME["Povprečno sončno obsevanje"][0])[0].text
    except KeyError:
        sončno_obsevanje = None
        sončno_obsevanje_enota = None
    else:
        if sončno_obsevanje == "0":
            sončno_obsevanje = None
            sončno_obsevanje_enota = None
        else:
            sončno_obsevanje_enota = n.VREME["Povprečno sončno obsevanje"][1]

    try:
        vsota_padavin = stran.xpath(n.VREME["Vsota padavin"][0])[0].text
    except KeyError:
        vsota_padavin = None
        vsota_padavin_enota = None
    else:
        vsota_padavin_enota = n.VREME["Vsota padavin"][1]

    return Vreme(opis_vremena=opis_vremena,
                 ura=ura,
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


def vreme_izpis(vreme: Vreme,
                kraj: str = "Ljubljana"
                ) -> str:
    """
    vhod: namedtuple, npr.: Vreme(opis_vremena="Jasno je",
                                   ura="18.30",
                                   temperatura="18.3",
                                   relativna_vlaga=21,
                                   tlak="1026.3",
                                   sončno_obsevanje="191",
                                   vsota_padavin="0",
                                   temperatura_enota="°C",
                                   relativna_vlaga_enota="%",
                                   tlak_enota="hPa",
                                   sončno_obsevanje_enota="W/m2",
                                   vsota_padavin_enota="mm")
          niz, npr.: "Ljubljana"
    izhod: niz, npr.: "Podatki za Ljubljano ob 18.30. Jasno je. Temperatura
                       zraka je 18,3 °C, relativna vlažnost znaša 21 %, zračni
                       tlak je 1026,3 hPa. Sončno obsevanje znaša 191 W/m2. "
    zahteve: typing.NamedTuple
    pretvori podatke iz namedtupla v besedilo
    """
    if vreme is None:
        return "Podatkov o vremenu trenutno ni. "
    elif not any(vreme):
        return "Podatkov o vremenu trenutno ni. "

    if vreme.ura:
        izpis = f"Podatki za {n.KRAJI_SKLONI[kraj]} ob {vreme.ura}.\n"
    else:
        izpis = f"Podatki za {n.KRAJI_SKLONI[kraj]}.\n"

    if vreme.opis_vremena:
        izpis += f"{vreme.opis_vremena}. "

    if vreme.temperatura:
        izpis += (f"Temperatura zraka je "
                  f"{vreme.temperatura.replace('.', ',')} "
                  f"{vreme.temperatura_enota}")

    if vreme.relativna_vlaga:
        izpis += (f", relativna vlažnost znaša "
                  f"{vreme.relativna_vlaga} "
                  f"{vreme.relativna_vlaga_enota}")

    if vreme.tlak:
        izpis += (f", zračni tlak je "
                  f"{vreme.tlak.replace('.', ',')} "
                  f"{vreme.tlak_enota}. ")
    else:
        izpis += ". "

    if vreme.sončno_obsevanje:
        izpis += (f"Sončno obsevanje znaša {vreme.sončno_obsevanje} "
                  f"{vreme.sončno_obsevanje_enota}. ")

    if vreme.vsota_padavin != "0":
        izpis += (f"Zapadlo je "
                  f"{vreme.vsota_padavin} "
                  f"{vreme.vsota_padavin_enota} padavin.")
    return izpis


def veter_podatki(stran  # lxml.etree._Element
                  ) -> Veter:
    """
    izhod: namedtuple, npr.: Veter(smer_vetra="severovzhodnik",
                                  hitrost_vetra="3,5",
                                  sunki_vetra="27",
                                  hitrost_vetra_enota="m/s",
                                  sunki_vetra_enota="m/s")
    zahteve: typing.NamedTuple, lxml.etree
    izlušči podatke iz zapisa .xml z ARSO-ve spletne strani v namedtuple:
    smer_vetra, hitrost_vetra, sunki_vetra, hitrost_vetra_enota,
    sunki_vetra_enota
    """
    if not preveri_dostopnost_podatkov(stran):
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


def veter_izpis(veter: Veter
                ) -> str:
    """
    vhod: namedtuple, npr.: Veter(smer_vetra="severovzhodnik",
                                   hitrost_vetra="3,5",
                                   sunki_vetra="27",
                                   hitrost_vetra_enota="m/s",
                                   sunki_vetra_enota="m/s")
    izhod: niz, npr.: "Piha severovzhodnik s hitrostjo 3,5 m/s in sunki
                       do 27 m/s. "
    zahteve: typing.NamedTuple
    """
    if veter is None:
        return None

    elif not any(veter):
        return None

    izpis = (f"Piha {veter.smer_vetra} "
             f"s hitrostjo "
             f"{veter.hitrost_vetra} {veter.hitrost_vetra_enota} "
             f"in sunki do {veter.sunki_vetra} {veter.sunki_vetra_enota}. ")
    return izpis


def onesnaženost_podatki(stran,  # lxml.etree._Element
                         kraj: str = "Ljubljana",
                         šifre: dict = n.ZRAK_ŠIFRE,
                         kategorije: dict = n.ZRAK_KATEGORIJE
                         ) -> tuple:
    """
    vhod: slovar, npr.: {"Ljubljana": "E21"},
          slovar, npr.: {"pm10": ("µg/m³", 50)}
    izhod: tuple, npr.: (
            {"pm10": "43", "so2": "4", "co": "0.2", "o3": "114", "no2": "6"},
            True) – True označuje čist zrak, None nasprotno
    zahteve: lxml.etree, nastavitve
    izlušči podatke iz zapisa .xml z ARSO-ve spletne strani v tuple: s podatki
    o delcih v zraku, stikalo čistega zraka
    """
    if stran is None:
        return None

    šifra = šifre[kraj]
    rezultat = {}
    čist_zrak = True
    for i in kategorije:
        try:
            rezultat[i] = stran.xpath(
                f"/arsopodatki/postaja[@sifra='{šifra}']/{i}")[0].text
        except IndexError:
            pass
        else:
            if rezultat[i]:
                if int(float(rezultat[i].lstrip("<"))) >= int(kategorije[i][1]):
                    čist_zrak = False
    return rezultat, čist_zrak


def onesnaženost_izpis(rezultat: tuple,
                       enote: dict = n.ZRAK_KATEGORIJE
                       ) -> str:
    """
    vhod: tuple, npr.: (
            {"pm10": "43", "so2": "4", "co": "0.2", "o3": "114", "no2": "6"},
            True) – True označuje čist zrak, None nasprotno
    izhod: niz, npr.: "PM10: 43 µg/m³ (mejna vrednost: 50 µg/m³).
                       SO2: 4 µg/m³ (mejna vrednost: 350 µg/m³).
                       CO: 0.2 mg/m³ (mejna vrednost: 10 mg/m³).
                       O3: 114 µg/m³ (mejna vrednost: 180 µg/m³).
                       NO2: 6 µg/m³ (mejna vrednost: 200 µg/m³)."
    zahteve: nastavitve
    """
    if rezultat is None:
        return "Podatkov o kakovosti zraka trenutno ni."

    izpis = ""
    if not rezultat[1]:
        izpis += "POZOR! Zrak je onesnažen.\n"
    for kategorija, vrednost in rezultat[0].items():
        if vrednost:
            izpis += (f"{kategorija.upper()}: "
                      f"{vrednost} {enote[kategorija][0]} "
                      f"(mejna vrednost: {enote[kategorija][1]} "
                      f"{enote[kategorija][0]}).\n")
    return izpis.rstrip()


def čas_uredi(niz: str
              ) -> Čas:
    """
    vhod: niz, npr.: "06.04.2020 19:38 CEST"
    izhod: namedtuple, npr.: Čas(datum="6. 4. 2020",
                                 ura="6.32",
                                 dtm=datetime.datetime(2020, 4, 6, 6, 32))
    zahteve: typing.NamedTuple
    pretvori zapis časa (datum in ura) z ARSO-ve spletne strani v namedtuple:
    datum, ura, zapis v obliki datetime.datetime
    """
    x = niz.split(" ")[:-1]
    ura = x[1].replace(":", ".")
    datum = x[0].split(".")
    for i in range(len(datum)):
        datum[i] = datum[i].lstrip("0")
    # datetime.time
    cifre_datum = [int(i) for i in datum]
    cifre_ura = x[1].split(":")
    dtm = (datetime.datetime(cifre_datum[2],
                             cifre_datum[1],
                             cifre_datum[0],
                             int(cifre_ura[0]),
                             int(cifre_ura[1])))
    return Čas(datum=". ".join(datum),  # "1. 4. 2020"
               ura=ura,                 # "6.41"
               dtm=dtm,)                # datetime.datetime(2020, 4, 1, 6, 41)


def dan_podatki(stran  # lxml.etree._Element
                ) -> str:
    """
    izhod: namedtuple, npr.: Dan(datum="6. 4. 2020",
                                 vzhod="6.32", zahod="19.38",
                                 dolžina_dneva="13.06",
                                 zaporedni_v_letu=96)
    zahteve: typing.NamedTuple, lxml.etree
    izlušči podatke iz zapisa .xml z ARSO-ve spletne strani v namedtuple:
    datum, vzhod, zahod, dolžina_dneva, zaporedni_v_letu
    """
    if not preveri_dostopnost_podatkov(stran):
        return None

    vzhod = čas_uredi(stran.xpath("/data/metData/sunrise")[0].text)
    zahod = čas_uredi(stran.xpath("/data/metData/sunset")[0].text)

    # <class "list">: ["2020", "04", "01"]
    x = stran.xpath(
        "/data/metData/sunrise")[0].text.split(" ")[0].split(".")[::-1]
    datum = datetime.date(int(x[0]), int(x[1]), int(x[2]))
    zaporedni_v_letu = datum - datetime.date(int(x[0]), 1, 1)
    datum = ". ".join(i.lstrip("0") for i in x[::-1])
    dolžina_dneva = zahod.dtm - vzhod.dtm
    dolž_dneva_ure = str(int(dolžina_dneva.total_seconds() // 3600))
    dolž_dneva_min = str(int(dolžina_dneva.total_seconds() % 3600) // 60)
    if len(dolž_dneva_min) == 1:
        dolž_dneva_min = f"0{dolž_dneva_min}"
    dolžina_dneva = f"{dolž_dneva_ure}.{dolž_dneva_min}"
    return Dan(datum=datum,
               vzhod=vzhod.ura,
               zahod=zahod.ura,
               dolžina_dneva=dolžina_dneva,
               zaporedni_v_letu=zaporedni_v_letu.days,)


def dan_izpis(dan: Dan
              ) -> str:
    """
    vhod: namedtuple, npr.: Dan(datum="6. 4. 2020",
                                vzhod="6.32",
                                zahod="19.38",
                                dolžina_dneva="13.06",
                                zaporedni_v_letu=96)
    izhod: niz, npr.: "Danes je 6. 4. 2020, tj. 96. dan v letu. Sončni vzhod
                       je ob 6.32, zahod ob 19.38, dan traja 13.06."
    zahteve: typing.NamedTuple
    """
    if dan is None:
        return None

    izpis = (f"Danes je {dan.datum}, tj. {dan.zaporedni_v_letu}. dan v letu. "
             f"Sončni vzhod je ob {dan.vzhod}, zahod ob {dan.zahod}, "
             f"dan traja {dan.dolžina_dneva}.")
    return izpis


def vreme_ni_podatkov() -> str:
    """
    sporočilo, ko ni podatkov o vremenu
    """
    return "Podatkov o vremenu trenutno ni."


def ni_povezave() -> str:
    """
    sporočilo, ko ni povezvae
    """
    return "Podatki so trenutno nedosegljivi."


def vremenko_izpis(kraj: str = "Ljubljana"
                   ) -> str:
    """
    izhod: niz, npr.: "Podatki za Ljubljano ob 19.00.
           Temperatura zraka je 17,1 °C, relativna vlažnost znaša 26 %,
           zračni tlak je 1026,5 hPa. Sončno obsevanje znaša 102 W/m2. Piha
           severovzhodnik s hitrostjo 5,1 m/s in sunki do 35 m/s. Danes je
           6. 4. 2020, tj. 96. dan v letu. Sončni vzhod je ob 6.32, zahod ob
           19.38, dan traja 13.06.
           PM10: 43 µg/m³ (mejna vrednost: 50 µg/m³).
           SO2: 4 µg/m³ (mejna vrednost: 350 µg/m³).
           CO: 0.2 mg/m³ (mejna vrednost: 10 mg/m³).
           O3: 114 µg/m³ (mejna vrednost: 180 µg/m³).
           NO2: 6 µg/m³ (mejna vrednost: 200 µg/m³)."
    """
    stran_vreme = vremenko.poštar.pridobi_vremenske_podatke(
        n.KRAJI_URL[kraj], kraj)
    stran_onesnaženost = vremenko.poštar.pridobi_vremenske_podatke(n.ZRAK)

    if (stran_vreme is None) and (stran_onesnaženost is None):
        return ni_povezave()

    elif stran_vreme is None:
        return vreme_ni_podatkov()

    else:
        izpis = ""
        izpis_vreme = vreme_izpis(vreme_podatki(stran_vreme), kraj)
        if izpis_vreme:
            izpis += izpis_vreme

        izpis_veter = veter_izpis(veter_podatki(stran_vreme))
        if izpis_veter:
            izpis += izpis_veter

        izpis_dolžina_dneva = dan_izpis(dan_podatki(stran_vreme))
        if izpis_dolžina_dneva:
            izpis += izpis_dolžina_dneva

        if kraj in ("Ljubljana", "Maribor", "Celje", "Murska Sobota", "Koper",
                    "Nova Gorica", "Trbovlje", "Zagorje"):
            izpis += "\n" + onesnaženost_izpis(
                onesnaženost_podatki(stran_onesnaženost, kraj))
    return izpis


def main():
    print(vremenko_izpis())


if __name__ == "__main__":
    main()
