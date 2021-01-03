#!/usr/bin/env python
# -*- coding: "UTF-8" -*-

from typing import NamedTuple
from dateutil import tz
import datetime
import logging
import vremenko.nastavitve as n
import vremenko.poštar


class Vreme(NamedTuple):
    kraj: str
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
    dolžina_dneva: datetime.timedelta
    zaporedni_v_letu: int


class Podatki(NamedTuple):
    vreme: NamedTuple
    veter: NamedTuple
    dan: NamedTuple
    onesnaženost: NamedTuple


def preveri_dostopnost_podatkov(stran  # lxml.etree._Element
                                ) -> bool:
    """
    preveri, če XML vsebuje podatke
    kličejo jo: vreme_podatki, dan_podatki, onesnaženost_podatki
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
    kliče jo: vreme_podatki
    """
    try:
        return stran.xpath(xpath)[0].text
    except (ValueError, IndexError) as e:
        logging.warning(f"nisem uspel razbrati podatka: {xpath}; {e}")
        return None


def vreme_podatki(xpath: tuple,
                  stran  # lxml.etree._Element
                  ) -> list:
    """
    iz XML-ja razbere vremenske podatke (vreme, veter)
    """
    vrednosti = [razberi_podatke(kategorija, stran)
                 for kategorija in xpath]

    if not any(vrednosti):
        return [None, None, None]
    else:
        return vrednosti


def opis_vremena_izpis(opis_vremena: str,
                       prevodi: dict
                       ) -> str:
    """
    prevede ang. kratko oznako za opis vremena (vremenski pojav): clear -> jasno
    če kombinacija ne obstaja, vrne primarni vremenski pojav:
        prevCloudy_lightRA -> lightRA -> šibek dež
    kliče jo: vremenko_izpis
    """
    try:
        return f"{prevodi[opis_vremena][1]}. "
    except KeyError as e:
        logging.warning(
            f"nisem uspel najti prevoda za {opis_vremena}; {e}")
        deljen_opis = opis_vremena.split("_")
        return (f"{prevodi[deljen_opis[0]][1]}, "
                f"{prevodi[deljen_opis[1]][1].lower()}. ")


def vreme_izpis_glava(kraj: str,
                      čas: datetime.datetime
                      ) -> str:
    izpis = f"Podatki za {kraj}\n"
    if čas:
        izpis = f"{izpis.rstrip()} ob {ura_izpis(čas)}.\n"
    return izpis


def vreme_izpis(vreme: Vreme,
                ) -> str:
    """
    podatke o vremenu pretvori v besedilo
    """
    if vreme is None:
        return "Podatkov o vremenu trenutno ni. "

    izpis = vreme_izpis_glava(n.KRAJI_SKLONI[vreme.kraj], vreme.čas)

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


def veter_izpis(veter: Veter
                ) -> str:
    """
    podatke o vetru pretvori v besedilo
    """
    if not any(veter[:3]):
        return None
    else:
        izpis = (f"Piha {veter.smer_vetra} "
                 f"s hitrostjo {veter.hitrost_vetra.replace('.', ',')} "
                 f"{veter.hitrost_vetra_enota} "
                 f"in sunki do {veter.sunki_vetra.replace('.', ',')} "
                 f"{veter.sunki_vetra_enota}. ")
        return izpis


def alineje_izpis(kategorije: list,
                  vrednosti: list,
                  izpis: str = ""
                  ) -> str:
    """
    izpis podatkov v alinejah, npr.: Temperatura zraka: 2,6 °C.
    """
    for i, j in zip(kategorije, vrednosti):
        izpis += f"{i}: {j}.\n"
    return izpis


def kategorije_izpis(podatki: tuple,
                     ) -> list:
    """
    ustvari seznam s kategorijami: ['Opis vremena', 'Temperatura' ...]
    """
    return [kategorija.capitalize().replace("_", " ") for kategorija in podatki]


def vrednosti_izpis(vrednosti: tuple,
                    enote: tuple
                    ) -> list:
    """
    ustvari seznam z vrednostmi z enotami: ['Ni podatka', '2.4 °C' ...]
    """
    return [f"{str(i).replace('.',',').replace('None', '0')} {j}" for i, j in zip(vrednosti, enote)]


def vreme_izpis_kratko(vreme: Vreme,
                       ) -> str:
    """
    podatke o vremenu pretvori v kratko besedilo v alinejah
    """
    kategorije = kategorije_izpis(vreme._fields[2:7])
    vrednosti = vrednosti_izpis(vreme[2:7], vreme[7:])
    # "partCloudy 0" -> "delno oblačno"
    vrednosti[0] = n.OPIS_VREMENA[str(vreme.opis_vremena)][0]
    izpis = vreme_izpis_glava(n.KRAJI_SKLONI[vreme.kraj], vreme.čas)
    return alineje_izpis(kategorije, vrednosti, izpis)


def veter_izpis_kratko(veter: Veter
                       ) -> str:
    """
    podatke o vetru pretvori v kratko besedilo v alinejah
    """
    if not any(veter[:3]):
        return None
    else:
        kategorije = kategorije_izpis(veter._fields[:3])
        vrednosti = vrednosti_izpis(veter[1:3], veter[3:])
        vrednosti.insert(0, veter[0])
        return alineje_izpis(kategorije, vrednosti)


def onesnaženost_podatki(stran,  # lxml.etree._Element
                         kraj: str,  # "Ljubljana",
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

    šifra = šifre[kraj.lower()]
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

    izpis = "\n"
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


def onesnaženost_izpis_kratko(onesnaženost: Onesnaženost,
                              enote: dict = n.ZRAK_KATEGORIJE
                              ) -> str:
    return onesnaženost_izpis(onesnaženost, enote)


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
    try:
        return dtm.date().strftime("%-d. %-m. %Y")
    except ValueError as e:
        logging.info(f"Windows ne podpira izpisa v obliki %-d -> %d; {e}")
        return dtm.date().strftime("%d. %m. %Y")


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
    # TODO test za Dobliče Črnomelj in Koper Kapitanija
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
    else:
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
    izpis = (f"Danes je {datum_izpis(dan.vzhod)}, tj. {dan.zaporedni_v_letu}. "
             f"dan v letu. Sončni vzhod je ob {ura_izpis(dan.vzhod)}, "
             f"zahod ob {ura_izpis(dan.zahod)}, dan traja "
             f"{str(dan.dolžina_dneva)[:-3].replace(':', '.')}. ")
    return izpis


def dan_izpis_kratko(dan: Dan
                     ) -> str:
    """
    podatke o dnevu pretvori v kratko besedilo v alinejah
    """
    izpis = (f"Datum: {datum_izpis(dan.vzhod)}.\n"
             f"Zaporedni dan v letu: {dan.zaporedni_v_letu}.\n"
             f"Vzhod: {ura_izpis(dan.vzhod)}.\n"
             f"Zahod: {ura_izpis(dan.zahod)}.\n"
             f"Dolžina dneva: {str(dan.dolžina_dneva)[:-3].replace(':', '.')}.\n")
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


def vremenko_podatki(kraj: str  # "Ljubljana"
                     ) -> Podatki:
    """
    osrednja funkcija, ki zbere podatke o vremenu (vreme, veter, dan,
    onesnaženost)
    """
    stran_vreme = vremenko.poštar.pridobi_xml(n.URL_VREME_KRAJ[kraj.lower()])
    if kraj.lower() in n.ZRAK_ŠIFRE.keys():
        stran_onesnaženost = vremenko.poštar.pridobi_xml(n.URL_ZRAK)
    else:
        stran_onesnaženost = None

    if (stran_vreme is None) and (stran_onesnaženost is None):
        return "ni_povezave"

    elif stran_vreme is None:
        return "vreme_ni_podatkov"

    else:
        vreme = vreme_podatki(n.XPATH_VREME, stran_vreme)
        vreme[1] = čas_uredi(vreme[1])
        return Podatki(vreme=Vreme(*vreme),
                       veter=Veter(*vreme_podatki(n.XPATH_VETER, stran_vreme)),
                       dan=dan_podatki(stran_vreme),
                       onesnaženost=onesnaženost_podatki(stran_onesnaženost,
                                                         kraj),
                       )


def izpisnik(podatki: Podatki,
             alineje: bool
             ) -> str:
    """
    kliče funkcije vreme_izpis oz. vreme_izpis_kratko itd.
    """
    ukazi = [vreme_izpis, veter_izpis, dan_izpis, onesnaženost_izpis]
    if alineje:
        ukazi = [i + "_kratko" for i in ukazi]
    izpis = ""
    for ukaz, podatek in zip(ukazi, podatki):
        odgovor = ukaz(podatek)
        if odgovor:
            izpis += ukaz(podatek)
    return izpis


def vremenko_izpis(kraj: str,  # "Ljubljana"
                   alineje: bool = False
                   ) -> str:
    """
    osrednja funkcija, ki vrne izpis vremena (vreme, veter, dan, onesnaženost)
    """
    podatki = vremenko_podatki(kraj)

    if type(podatki) is not vremenko.vreme.Podatki:
        return eval(podatki)()  # kliče vreme_ni_podatkov() ali ni_povezave()
    else:
        return izpisnik(podatki, alineje)


if __name__ == "__main__":
    print(vremenko_izpis())
