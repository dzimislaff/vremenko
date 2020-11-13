#!/usr/bin/env python
# -*- coding: "UTF-8" -*-

from typing import NamedTuple
import datetime
import vremenko.nastavitve as n
import vremenko.poštar


class Vreme(NamedTuple):
    ura: str
    opis_vremena: str
    temperatura: str
    relativna_vlaga: str
    tlak: str
    sončno_obsevanje: str
    vsota_padavin: str
    temperatura_enota: str = "°C"
    relativna_vlaga_enota: str = "%"
    tlak_enota: str = "hPa"
    sončno_obsevanje_enota: str = "W/m2"
    vsota_padavin_enota: str = "mm"


class Veter(NamedTuple):
    smer_vetra: str
    hitrost_vetra: str
    sunki_vetra: str
    hitrost_vetra_enota: str  # = "m/s"
    sunki_vetra_enota: str  # = "m/s"


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


class Izpis(NamedTuple):
    vreme: NamedTuple
    veter: NamedTuple
    dan: NamedTuple
    onesnaženost: tuple


class Onesnaženost(NamedTuple):
    pm10: str
    so2: str
    co: str
    o3: str
    no2: str
    opozorilo: bool


def preveri_dostopnost_podatkov(stran  # lxml.etree._Element
                                ) -> bool:
    if stran is False:
        return False
    elif len(stran.xpath('/data/metData')) == 0:
        return False
    else:
        return True


def vreme_podatki(stran  # lxml.etree._Element
                  ) -> Vreme:
    """
    zahteve: typing.NamedTuple, lxml.etree
    """
    if not preveri_dostopnost_podatkov(stran):
        return None

    # temperatura, rel. vlaga, tlak, povprečno sončno obsevanje, vsota padavin
    kategorije = tuple(n.VREME.keys())[1:]

    try:  # ura
        vrednosti = [čas_uredi(stran.xpath(
            "/data/metData/tsValid_issued")[0].text).ura]
    except KeyError:
        vrednosti = [None]

    try:  # opis vremena
        vrednosti.append(n.OPIS_BAZA[stran.xpath(
            n.VREME["Opis vremena"])[0].text])
    except KeyError:
        vrednosti.append(None)

    for kategorija in kategorije:  # temp., rel. vlaga, tlak, son. obs., pad.
        try:
            vrednosti.append(stran.xpath(n.VREME[kategorija][0])[0].text)
        except KeyError:
            vrednosti.append(None)

    if not any(vrednosti):
        return None
    else:
        return Vreme(*vrednosti)


def vreme_izpis(vreme: Vreme,
                kraj: str = "Ljubljana"
                ) -> str:
    """
    zahteve: typing.NamedTuple
    """
    if vreme is None:
        return "Podatkov o vremenu trenutno ni. "

    if vreme.ura:
        izpis = f"Podatki za {n.KRAJI_SKLONI[kraj]} ob {vreme.ura}.\n"
    else:
        izpis = f"Podatki za {n.KRAJI_SKLONI[kraj]}.\n"

    if vreme.opis_vremena:
        izpis += f"{n.OPIS_IZPIS[vreme.opis_vremena]}. "

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
    zahteve: typing.NamedTuple, lxml.etree
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
                 hitrost_vetra_enota=hitrost_vetra_enota,
                 sunki_vetra=sunki_vetra,
                 sunki_vetra_enota=sunki_vetra_enota,
                 )


def veter_izpis(veter: Veter
                ) -> str:
    """
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
                         ) -> Onesnaženost:
    """
    zahteve: lxml.etree, nastavitve
    """
    if stran is None:
        return None

    šifra = šifre[kraj]

    def vnesi(i):
        try:
            return stran.xpath(
                f"/arsopodatki/postaja[@sifra='{šifra}']/{i}")[0].text
        except IndexError:
            return None

    def čist_zrak(podatki):
        try:
            for i, j in zip(podatki, kategorije):
                if int(float(i.lstrip("<"))) >= int(kategorije[j][1]):
                    return True  # opozorilo, da je zrak onesnažen
        except AttributeError:
            pass
        return False

    onesnaženost = [vnesi(i) for i in kategorije]
    zrak = čist_zrak(onesnaženost)
    onesnaženost.append(zrak)

    return Onesnaženost(*onesnaženost)


def onesnaženost_izpis(onesnaženost: Onesnaženost,
                       enote: dict = n.ZRAK_KATEGORIJE
                       ) -> str:
    """
    zahteve: nastavitve
    """
    if onesnaženost is None:
        return "Podatkov o kakovosti zraka trenutno ni."

    izpis = ""
    if onesnaženost.opozorilo:
        izpis += "POZOR! Zrak je onesnažen.\n"

    for i in range(5):
        if not onesnaženost[i]:
            continue
        izpis += (f"{onesnaženost._fields[i].upper()}: "
                  f"{onesnaženost[i]} {enote[onesnaženost._fields[i]][0]} "
                  f"(mejna vrednost: {enote[onesnaženost._fields[i]][1]}) "
                  f"{enote[onesnaženost._fields[i]][0]}.\n")
    return izpis.rstrip()


def čas_uredi(niz: str  # "06.04.2020 19:38 CEST"
              ) -> Čas:
    """
    zahteve: typing.NamedTuple
    """
    if type(niz) != str:
        return Čas(None, None, None)
    elif not (19 <= len(niz) <= 21):
        return Čas(None, None, None)

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
               dtm=dtm,                 # datetime.datetime(2020, 4, 1, 6, 41)
               )


def dan_podatki(stran  # lxml.etree._Element
                ) -> Dan:
    """
    zahteve: typing.NamedTuple, lxml.etree
    """
    if not preveri_dostopnost_podatkov(stran):
        return None

    vzhod = čas_uredi(stran.xpath("/data/metData/sunrise")[0].text)
    zahod = čas_uredi(stran.xpath("/data/metData/sunset")[0].text)

    if vzhod and zahod == (None, None, None):
        return None

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
               zaporedni_v_letu=zaporedni_v_letu.days
               )


def dan_izpis(dan: Dan
              ) -> str:
    """
    zahteve: typing.NamedTuple
    """
    if dan is None:
        return None
    elif dan == (None, None, None):
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


def vremenko_podatki(kraj: str = "Ljubljana"
                     ) -> tuple:
    """
    osrednja funkcija, ki pridobi podatke o vremenu (vreme, veter, dan,
    onesnaženost)
    """
    stran_vreme = vremenko.poštar.pridobi_vremenske_podatke(
        n.KRAJI_URL[kraj])
    if kraj in ("Ljubljana", "Maribor", "Celje", "Murska Sobota", "Koper",
                "Nova Gorica", "Trbovlje", "Zagorje"):
        stran_onesnaženost = vremenko.poštar.pridobi_vremenske_podatke(n.ZRAK)
    else:
        stran_onesnaženost = None

    if (stran_vreme is None) and (stran_onesnaženost is None):
        return "ni_povezave"

    elif stran_vreme is None:
        return "vreme_ni_podatkov"

    else:
        return Izpis(vreme=vreme_podatki(stran_vreme),
                     veter=veter_podatki(stran_vreme),
                     dan=dan_podatki(stran_vreme),
                     onesnaženost=onesnaženost_podatki(stran_onesnaženost,
                                                       kraj),
                     )


def vremenko_izpis(kraj: str = "Ljubljana"
                   ) -> str:
    """
    osrednja funkcija, ki vrne izpis vremena (vreme, veter, dan, onesnaženost)
    """
    podatki = vremenko_podatki(kraj)

    if type(podatki) is not vremenko.vreme.Izpis:
        # kliče vreme_ni_podatkov() ali ni_povezave()
        return eval(podatki)()

    else:
        izpis = ""
        izpis_vreme = vreme_izpis(podatki.vreme, kraj)
        if izpis_vreme:
            izpis += izpis_vreme

        izpis_veter = veter_izpis(podatki.veter)
        if izpis_veter:
            izpis += izpis_veter

        izpis_dolžina_dneva = dan_izpis(podatki.dan)
        if izpis_dolžina_dneva:
            izpis += izpis_dolžina_dneva

        if podatki.onesnaženost:
            izpis += "\n" + onesnaženost_izpis(podatki.onesnaženost)
    return izpis


def main():
    print(vremenko_izpis())


if __name__ == "__main__":
    main()
