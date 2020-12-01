#!/usr/bin/env python
# -*- coding: "UTF-8" -*-

from typing import NamedTuple
from dateutil import tz
import datetime
import logging
import vremenko.nastavitve as n
import vremenko.poštar


class Vreme(NamedTuple):
    čas: datetime.date
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
    hitrost_vetra_enota: str = "m/s"
    sunki_vetra_enota: str = "m/s"


class Onesnaženost(NamedTuple):
    čas: datetime.datetime
    pm10: str
    pm2_5: str
    so2: str
    co: str
    o3: str
    no2: str
    opozorilo: bool


class Dan(NamedTuple):
    vzhod: datetime.date
    zahod: datetime.date
    dolžina_dneva: str
    zaporedni_v_letu: int


class Podatki(NamedTuple):
    vreme: NamedTuple
    veter: NamedTuple
    onesnaženost: NamedTuple
    dan: NamedTuple


def preveri_dostopnost_podatkov(stran  # lxml.etree._Element
                                ) -> bool:
    if not len(stran):
        return False
    elif not stran.xpath('/data/metData'):
        return False
    else:
        return True


def razberi_podatke(kategorija, xpath, stran):
    try:
        return stran.xpath(xpath[kategorija])[0].text
    except (ValueError, IndexError) as e:
        logging.warning(f"nisem uspel razbrati podatka: {kategorija}; {e}")
        return None


def razberi_čas(xpath, stran):
    try:
        return čas_uredi(stran.xpath(xpath)[0].text)
    except (KeyError, IndexError) as e:
        logging.warning(f"nisem uspel razbrati podatka o datumu in uri; {e}")
        return None


def vreme_podatki(stran  # lxml.etree._Element
                  ) -> Vreme:
    """
    zahteve: typing.NamedTuple, lxml.etree
    """
    if not preveri_dostopnost_podatkov(stran):
        return None

    kategorije = tuple(n.XPATH_VREME.keys())
    vrednosti = [razberi_podatke(kategorija, n.XPATH_VREME, stran)
                 for kategorija in kategorije]
    vrednosti.insert(0, razberi_čas(n.XPATH_ČAS, stran))

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

    if vreme.čas:
        izpis = f"Podatki za {n.KRAJI_SKLONI[kraj]} ob {ura_izpis(vreme.čas)}.\n"
    else:
        izpis = f"Podatki za {n.KRAJI_SKLONI[kraj]}.\n"

    if vreme.opis_vremena or vreme.opis_vremena == 0:
        izpis += f"{n.OPIS_VREMENA[vreme.opis_vremena][1]}. "

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

    kategorije = tuple(n.XPATH_VETER.keys())
    vrednosti = [razberi_podatke(kategorija, n.XPATH_VETER, stran)
                 for kategorija in kategorije]

    if not any(vrednosti):
        return None
    else:
        return Veter(*vrednosti)


def veter_izpis(veter: Veter
                ) -> str:
    """
    zahteve: typing.NamedTuple
    """
    if veter is None:
        return None

    elif not any(veter[:3]):
        return None

    izpis = (f"Piha {veter.smer_vetra} "
             f"s hitrostjo {veter.hitrost_vetra.replace('.', ',')} "
             f"{veter.hitrost_vetra_enota} "
             f"in sunki do {veter.sunki_vetra.replace('.', ',')} "
             f"{veter.sunki_vetra_enota}. ")
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

    def vnesi(i, šifra):
        try:
            return stran.xpath(
                f"/arsopodatki/postaja[@sifra='{šifra}']/{i}")[0].text
        except IndexError as e:
            logging.warning(
                f"nisem uspel razbrati podatka o onesnaženosti {i}; {e}")
            return None

    def čist_zrak(podatki):
        for i, j in zip(podatki, kategorije):
            try:
                if int(float(i.lstrip("<"))) >= int(kategorije[j][1]):
                    return True  # opozorilo, da je zrak onesnažen
            except AttributeError:
                pass
        return False

    šifra = šifre[kraj]
    onesnaženost = [vnesi(i, šifra) for i in kategorije]
    onesnaženost.append(čist_zrak(onesnaženost))

    if not any(onesnaženost):
        return None
    else:
        # štempljanje časa
        xpath = f"/arsopodatki/postaja[@sifra='{šifra}']/datum_do"
        onesnaženost.insert(0, razberi_čas(xpath, stran))
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

    for i in range(1, 7):
        if not onesnaženost[i]:
            continue
        izpis += (f"{onesnaženost._fields[i].upper().replace('_', '.')}: "
                  f"{onesnaženost[i]} "
                  f"{enote[onesnaženost._fields[i].replace('_', '.')][0]} "
                  f"(mejna vrednost: "
                  f"{enote[onesnaženost._fields[i].replace('_', '.')][1]}) "
                  f"{enote[onesnaženost._fields[i].replace('_', '.')][0]}.\n")
    return izpis.rstrip()


def ura_izpis(dtm):
    return dtm.time().strftime("%H.%M").lstrip("0")


def datum_izpis(dtm):
    return dtm.date().strftime("%-d. %-m. %Y")


def čas_uredi(niz: str  # "06.04.2020 19:38 CEST"
              ) -> datetime.datetime:
    # onesnaženost = "2020-11-18 17:00"
    # xml_pozimi = "19.11.2020 18:00 CET"
    # xml_poleti = "06.04.2020 19:38 CEST"

    if type(niz) != str:
        return None
    elif not (16 <= len(niz) <= 21):
        return None

    slo_časovni_pas = tz.gettz("Europe/Ljubljana")

    niz = niz.rstrip(" CEST").rstrip(" CET")
    if "." in niz:
        dtm = datetime.datetime.strptime(niz, "%d.%m.%Y %H:%M")
    else:
        dtm = datetime.datetime.strptime(niz, "%Y-%m-%d %H:%M")
    return dtm.replace(tzinfo=slo_časovni_pas)


def dan_podatki(stran  # lxml.etree._Element
                ) -> Dan:
    """
    zahteve: typing.NamedTuple, lxml.etree
    """
    if not preveri_dostopnost_podatkov(stran):
        return None

    vzhod = čas_uredi(stran.xpath("/data/metData/sunrise")[0].text)
    zahod = čas_uredi(stran.xpath("/data/metData/sunset")[0].text)

    if not vzhod:
        return None

    dolžina_dneva = zahod - vzhod
    zaporedni_v_letu = vzhod.timetuple().tm_yday

    return Dan(vzhod=vzhod,
               zahod=zahod,
               dolžina_dneva=dolžina_dneva,
               zaporedni_v_letu=zaporedni_v_letu
               )


def dan_izpis(dan: Dan
              ) -> str:
    """
    zahteve: typing.NamedTuple
    """
    if dan is None:
        return None

    izpis = (f"Danes je {datum_izpis(dan.vzhod)}, tj. {dan.zaporedni_v_letu}. "
             f"dan v letu. Sončni vzhod je ob {ura_izpis(dan.vzhod)}, "
             f"zahod ob {ura_izpis(dan.zahod)}, dan traja "
             f"{str(dan.dolžina_dneva)[:-3].replace(':', '.')}.")
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
    stran_vreme = vremenko.poštar.pridobi_xml(n.KRAJI_URL[kraj])
    if kraj in n.ZRAK_ŠIFRE.keys():
        stran_onesnaženost = vremenko.poštar.pridobi_xml(n.ZRAK)
    else:
        stran_onesnaženost = None

    if (stran_vreme is None) and (stran_onesnaženost is None):
        return "ni_povezave"

    elif stran_vreme is None:
        return "vreme_ni_podatkov"

    else:
        return Podatki(vreme=vreme_podatki(stran_vreme),
                       veter=veter_podatki(stran_vreme),
                       onesnaženost=onesnaženost_podatki(stran_onesnaženost,
                                                         kraj),
                       dan=dan_podatki(stran_vreme),
                       )


def vremenko_izpis(kraj: str = "Ljubljana"
                   ) -> str:
    """
    osrednja funkcija, ki vrne izpis vremena (vreme, veter, dan, onesnaženost)
    """
    podatki = vremenko_podatki(kraj)

    if type(podatki) is not vremenko.vreme.Podatki:
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
