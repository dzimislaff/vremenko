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
    """
    preveri, če XML vsebuje podatke
    kličejo jo: vreme_podatki, veter_podatki, dan_podatki, onesnaženost_podatki
    """
    if stran is None:
        return False
    elif (not stran.xpath("/data/metData")) \
            and (not stran.xpath("/arsopodatki")):
        return False
    else:
        return True


def razberi_podatke(xpath: str,
                    stran  # lxml.etree._Element
                    ) -> str:
    """
    razbere podatke iz XML-ja s pomočjo xpatha
    kličejo jo: vreme_podatki, veter_podatki
    """
    try:
        return stran.xpath(xpath)[0].text
    except (ValueError, IndexError) as e:
        logging.warning(f"nisem uspel razbrati podatka: {xpath}; {e}")
        return None


def vreme_podatki(stran  # lxml.etree._Element
                  ) -> Vreme:
    """
    iz XML-ja razbere podatke o vremenu
    kliče jo: vremenko_podatki
    """
    if not preveri_dostopnost_podatkov(stran):
        return None

    vrednosti = [razberi_podatke(kategorija, stran)
                 for kategorija in n.XPATH_VREME]
    vrednosti[0] = čas_uredi(vrednosti[0])

    if not any(vrednosti):
        return None
    else:
        return Vreme(*vrednosti)


def opis_vremena_izpis(opis_vremena: str,
                       prevodi: dict
                       ) -> str:
    """
    prevede ang. kratko oznako za opis vremena (vremenski pojav): clear -> jasno
    če kombinacija ne obstaja, vrne primarni vremenski pojav:
        prevCloudy_lightRA -> lightRA -> šibek dež
    """
    try:
        return f"{prevodi[opis_vremena][1]}. "
    except KeyError as e:
        logging.warning(
            f"nisem uspel najti prevoda za {opis_vremena}; {e}")
        deljen_opis = opis_vremena.split("_")
        return (f"{prevodi[deljen_opis[0]][1]}, "
                f"{prevodi[deljen_opis[1]][1].lower()}. ")


def vreme_izpis(vreme: Vreme,
                kraj: str = "Ljubljana"
                ) -> str:
    """
    podatke o vremenu pretvori v besedilo
    """
    if vreme is None:
        return "Podatkov o vremenu trenutno ni. "

    if vreme.čas:
        izpis = f"Podatki za {n.KRAJI_SKLONI[kraj]} ob {ura_izpis(vreme.čas)}.\n"
    else:
        izpis = f"Podatki za {n.KRAJI_SKLONI[kraj]}.\n"

    if vreme.opis_vremena or vreme.opis_vremena == 0:
        izpis += opis_vremena_izpis(vreme.opis_vremena, n.OPIS_VREMENA)

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

    if vreme.vsota_padavin not in ("0", None):
        izpis += (f"Zapadlo je "
                  f"{vreme.vsota_padavin} "
                  f"{vreme.vsota_padavin_enota} padavin. ")
    return izpis


def veter_podatki(stran  # lxml.etree._Element
                  ) -> Veter:
    """
    iz XML-ja razbere podatke o vetru
    """
    if not preveri_dostopnost_podatkov(stran):
        return None

    vrednosti = [razberi_podatke(kategorija, stran)
                 for kategorija in n.XPATH_VETER]

    if not any(vrednosti):
        return None
    else:
        return Veter(*vrednosti)


def veter_izpis(veter: Veter
                ) -> str:
    """
    podatke o vetru pretvori v besedilo
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
    iz XML-ja razbere podatke o onesnaženosti zraka
    """
    if not preveri_dostopnost_podatkov(stran):
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
        xpath = f"/arsopodatki/postaja[@sifra='{šifra}']/datum_do"  # čas
        onesnaženost.insert(0, čas_uredi(razberi_podatke(xpath, stran)))
        return Onesnaženost(*onesnaženost)


def onesnaženost_izpis(onesnaženost: Onesnaženost,
                       enote: dict = n.ZRAK_KATEGORIJE
                       ) -> str:
    """
    podatke o onesnaženosti zraka pretvori v besedilo
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
    """
    pretvori datetime.datetime v uro, npr.: 12.30
    """
    ura = dtm.time().strftime("%H.%M").lstrip("0")
    if len(ura) == 3:  # ob polnoči: .30 -> 00.30
        return f"00{ura}"
    else:
        return ura


def datum_izpis(dtm):
    """
    pretvori datetime.datetime v datum, npr.: 24. 5. 2020
    """
    return dtm.date().strftime("%-d. %-m. %Y")


def čas_uredi(niz: str  # "06.04.2020 19:38 CEST"
              ) -> datetime.datetime:
    """
    niz pretvori v datetime.datetime
        onesnaženost = "2020-11-18 17:00"
        xml_pozimi = "19.11.2020 18:00 CET"
        xml_poleti = "06.04.2020 19:38 CEST"
    """

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
    iz XML-ja razbere podatke o dnevu
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
    podatke o dnevu pretvori v besedilo
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
    sporočilo, ko ni povezave
    """
    return "Podatki so trenutno nedosegljivi."


def vremenko_podatki(kraj: str = "Ljubljana"
                     ) -> tuple:
    """
    osrednja funkcija, ki zbere podatke o vremenu (vreme, veter, dan,
    onesnaženost)
    """
    stran_vreme = vremenko.poštar.pridobi_xml(n.URL_VREME_KRAJ[kraj])
    if kraj in n.ZRAK_ŠIFRE.keys():
        stran_onesnaženost = vremenko.poštar.pridobi_xml(n.URL_ZRAK)
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
        return eval(podatki)()  # kliče vreme_ni_podatkov() ali ni_povezave()

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


if __name__ == "__main__":
    print(vremenko_izpis())
