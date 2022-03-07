#!/usr/bin/env python
# -*- coding: 'UTF-8' -*-

import datetime
from dateutil import tz
import logging
import vremenko.beleženje
import vremenko.altnastavitve as n
import requests
import lxml.etree
from dataclasses import dataclass


class Pošta:
    def __init__(self,
                 naslov: str,
                 r: requests.models.Response = None,
                 stran: lxml.etree._Element = None,
                 ):
        self.naslov = naslov
        self.r = r
        self.stran = stran

    @staticmethod
    def pridobi_spletno_stran(naslov: str
                              ) -> requests.models.Response:
        try:
            return requests.get(naslov)
        except requests.exceptions.ConnectionError:
            return  # TODO logging; ni povezave
        except requests.exceptions.MissingSchema:
            return  # TODO logging; neustrezna povezava

    @staticmethod
    def preveri_dostopnost_podatkov(stran: lxml.etree._Element,
                                    *args: str
                                    ) -> bool:
        for i in args:
            if not stran.xpath(i):
                return
        if stran is None:
            return
        else:
            return True

    def pretvori_v_xml(self,
                       ):
        try:
            self.stran = lxml.etree.fromstring(
                bytes(self.r.text, encoding='utf8'))
        except lxml.etree.XMLSyntaxError:
            pass  # TODO logging; neustrezen XML

    def pridobi_xml(self,
                    ):
        self.r = self.pridobi_spletno_stran(self.naslov)
        self.pretvori_v_xml()


class Poštar(Pošta):
    def __init__(self,
                 naslov):
        super().__init__(naslov)
        super().pridobi_xml()


class Kraj:
    def __init__(self,
                 kraj: str,
                 seznam_krajev: tuple = None,
                 ):
        if kraj.lower() not in n.KRAJI_URL.keys():
            raise ValueError("neznan kraj")
        self.kraj = kraj


class Arso(Kraj):
    def __init__(self,
                 kraj: str,
                 naslov: str,
                 seznam_krajev: tuple = tuple(n.KRAJI_URL.keys()),
                 stran: lxml.etree._Element = None,
                 ):
        super().__init__(kraj, seznam_krajev)
        self.naslov = naslov
        p = Poštar(self.naslov)
        self.stran = p.stran

    @staticmethod
    def preveri_prisotnost_podatkov(podatki: tuple
                                    ) -> bool:
        if any(podatki):
            return True

    @staticmethod
    def čas_uredi(niz: str  # "06.04.2020 19:38 CEST"
                  ) -> datetime.datetime:
        """
        niz pretvori v datetime.datetime
            onesnaženost = "2020-11-18 17:00"
            xml_pozimi = "19.11.2020 18:00 CET"
            xml_poleti = "06.04.2020 19:38 CEST"
        """
        if type(niz) != str:
            return
        elif not (16 <= len(niz) <= 21):
            return

        slo_časovni_pas = tz.gettz("Europe/Ljubljana")
        niz = niz.rstrip(" CEST").rstrip(" CET")
        if "." in niz:
            dtm = datetime.datetime.strptime(niz, "%d.%m.%Y %H:%M")
        else:
            dtm = datetime.datetime.strptime(niz, "%Y-%m-%d %H:%M")
        return dtm.replace(tzinfo=slo_časovni_pas)

    @staticmethod
    def razberi_podatke(stran: lxml.etree._Element,
                        xpath: str,
                        ) -> str:
        """
        razbere podatke iz XML-ja s pomočjo xpatha
        """
        try:
            return stran.xpath(xpath)[0].text
        except (ValueError, IndexError) as e:
            logging.warning(f"nisem uspel razbrati vrednosti: {xpath}; {e}")
            return

    def zberi_podatke(self,
                      xpath: tuple = n.XPATH_VREME,
                      ):
        """
        iz XML-ja razbere vremenske podatke (vreme, veter)
        """
        return [self.razberi_podatke(self.stran, kategorija)
                for kategorija in xpath]


class VremenskiPodatki(Arso):
    def __init__(self,
                 kraj: str,
                 naslov: str = None,
                 seznam_krajev: tuple = tuple(n.KRAJI_URL.keys()),
                 stran: lxml.etree._Element = None,
                 vrednosti: list = None,
                 ):
        self.naslov = (n.URL_VREME[0] +
                       n.KRAJI_URL[kraj.lower()] + n.URL_VREME[1])
        super().__init__(kraj, self.naslov, seznam_krajev, stran)
        self.vrednosti = super().zberi_podatke()

    @staticmethod
    def preveri_prisotnost_podatkov(podatki: tuple
                                    ) -> bool:
        if any(podatki):
            return True

    def obdelaj_podatke(self,
                        ):
        for i in range(3):
            self.vrednosti[i] = self.čas_uredi(self.vrednosti[i])
        self.vrednosti.insert(3, self.vrednosti[2] - self.vrednosti[1])
        self.vrednosti.insert(4, self.vrednosti[1].timetuple().tm_yday)


class OnesnaženostPodatki(Arso):
    def __init__(self,
                 kraj,
                 naslov: str = n.URL_ONESNAŽENOST,
                 seznam_krajev: tuple = tuple(n.ZRAK_ŠIFRE.keys()),
                 kategorije: dict = n.ZRAK_KATEGORIJE,
                 stran: lxml.etree._Element = None,
                 šifra: str = None,
                 vrednosti: list = None,
                 ):
        super().__init__(kraj, naslov, seznam_krajev, stran)
        self.kategorije = kategorije
        self.šifra = n.ZRAK_ŠIFRE[kraj.lower()]
        self.vrednosti = super().zberi_podatke(self.ustvari_xpath_seznam())

    def ustvari_xpath_seznam(self,
                             kategorije: dict = n.ZRAK_KATEGORIJE
                             ) -> list:
        seznam = [
            f"/arsopodatki/postaja[@sifra='{self.šifra}']/{i}" for i in kategorije]
        seznam.insert(
            0, f"/arsopodatki/postaja[@sifra='{self.šifra}']/datum_do")
        return tuple(seznam)

    def čist_zrak(self):
        for i, j in zip(self.vrednosti, self.kategorije):
            try:
                if int(float(i.lstrip("<"))) >= int(self.kategorije[j][1]):
                    # opozorilo, da je zrak onesnažen
                    self.vrednosti.append(True)
            except AttributeError:
                pass
            except ValueError:
                pass  # TODO logging
        self.vrednosti.append(False)


@dataclass
class Onesnaženost:
    kraj: str
    čas: datetime.datetime
    pm10: str
    pm2_5: str
    so2: str
    co: str
    o3: str
    no2: str
    opozorilo: bool

    def onesnaženost_izpis(self,
                           enote: dict = n.ZRAK_KATEGORIJE
                           ) -> str:
        """
        podatke o onesnaženosti zraka pretvori v besedilo
        """
        if not Arso.preveri_prisotnost_podatkov((self.pm10,
                                                 self.pm2_5,
                                                 self.so2,
                                                 self.co,
                                                 self.o3,
                                                 self.no2)):
            return "Podatkov o kakovosti zraka trenutno ni."

        izpis = "\n"
        if self.opozorilo:
            izpis += "POZOR! Zrak je onesnažen.\n"

        for i in self.__dict__:
            if not self.__dict__[i]:
                continue
            elif i in ("kraj", "čas"):
                continue
            izpis += (f"{i.upper().replace('_', '.')}: "
                      f"{self.__dict__[i]} "
                      f"{enote[i.replace('_', '.')][0]} "
                      f"(mejna vrednost: "
                      f"{enote[i.replace('_', '.')][1]}) "
                      f"{enote[i.replace('_', '.')][0]}.\n")
        return izpis.rstrip()


@dataclass
class Vreme:
    kraj: str
    čas: datetime.date
    sončni_vzhod: datetime.date
    sončni_zahod: datetime.date
    dolžina_dneva: datetime.date
    zaporedni_v_letu: int
    opis_vremena: str
    temperatura: str
    relativna_vlaga: str
    tlak: str
    sončno_obsevanje: str
    vsota_padavin: str
    smer_vetra: str
    hitrost_vetra: str
    sunki_vetra: str
    temperatura_enota: str = "°C"
    relativna_vlaga_enota: str = "%"
    tlak_enota: str = "hPa"
    sončno_obsevanje_enota: str = "W/m2"
    vsota_padavin_enota: str = "mm"
    hitrost_vetra_enota: str = "m/s"
    sunki_vetra_enota: str = "m/s"

    @staticmethod
    def ura_izpis(dtm):
        """
        pretvori datetime.datetime v uro, npr.: 12.30
        """
        ura = dtm.time().strftime("%H.%M").lstrip("0")
        if len(ura) == 3:  # ob polnoči: .30 -> 00.30
            return f"00{ura}"
        else:
            return ura

    @staticmethod
    def datum_izpis(dtm):
        """
        pretvori datetime.datetime v datum, npr.: 24. 5. 2020
        """
        try:
            return dtm.date().strftime("%-d. %-m. %Y")
        except ValueError as e:
            logging.info(f"Windows ne podpira izpisa v obliki %-d -> %d; {e}")
            return dtm.date().strftime("%d. %m. %Y")

    @staticmethod
    def decimalna_vejica(niz: str
                         ) -> str:
        return niz.replace('.', ',')

    # vreme
    def vreme_izpis_glava(self,
                          ) -> str:
        izpis = f"Podatki za {self.kraj}\n"
        if self.čas:
            izpis = f"{izpis.rstrip()} ob {self.ura_izpis(self.čas)}.\n"
        return izpis

    def opis_vremena_izpis(self,
                           prevodi: dict
                           ) -> str:
        """
        prevede ang. kratko oznako za opis vremena (vremenski pojav): clear -> jasno
        če kombinacija ne obstaja, vrne primarni vremenski pojav:
            prevCloudy_lightRA -> lightRA -> šibek dež
        kliče jo: vremenko_izpis
        """
        try:
            return f"{prevodi[self.opis_vremena][1]}. "
        except KeyError as e:
            logging.warning(
                f"nisem uspel najti prevoda za {self.opis_vremena}; {e}")
            deljen_opis = self.opis_vremena.split("_")
            return (f"{prevodi[deljen_opis[0]][1]}, "
                    f"{prevodi[deljen_opis[1]][1].lower()}. ")

    def vreme_izpis(self
                    ) -> str:
        """
        podatke o vremenu pretvori v besedilo
        """
        if not Arso.preveri_prisotnost_podatkov((self.opis_vremena,
                                                 self.temperatura,
                                                 self.relativna_vlaga,
                                                 self.tlak,
                                                 self.sončno_obsevanje,
                                                 self.vsota_padavin
                                                 )):
            return "Podatkov o vremenu trenutno ni. "

        izpis = self.vreme_izpis_glava()

        if self.opis_vremena or self.opis_vremena == 0:
            izpis += self.opis_vremena_izpis(n.OPIS_VREMENA)

        if self.temperatura:
            izpis += (f"Temperatura zraka je "
                      f"{self.decimalna_vejica(self.temperatura)} "
                      f"{self.temperatura_enota}")

        if self.relativna_vlaga:
            izpis += (f", relativna vlažnost znaša "
                      f"{self.relativna_vlaga} "
                      f"{self.relativna_vlaga_enota}")

        if self.tlak:
            izpis += (f", zračni tlak je "
                      f"{self.decimalna_vejica(self.tlak)} "
                      f"{self.tlak_enota}. ")
        else:
            izpis += ". "

        if self.sončno_obsevanje not in ("0", None):
            izpis += (f"Sončno obsevanje znaša {self.sončno_obsevanje} "
                      f"{self.sončno_obsevanje_enota}. ")

        if self.vsota_padavin not in ("0", None):
            izpis += (f"Zapadlo je "
                      f"{self.decimalna_vejica(self.vsota_padavin)} "
                      f"{self.vsota_padavin_enota} padavin. ")
        return izpis

    # veter
    def veter_izpis(self
                    ) -> str:
        """
        podatke o vetru pretvori v besedilo
        """

        if not Arso.preveri_prisotnost_podatkov((self.smer_vetra,
                                                 self.hitrost_vetra,
                                                 self.sunki_vetra)):
            return
        else:
            izpis = (f"Piha {self.smer_vetra} "
                     f"s hitrostjo {self.decimalna_vejica(self.hitrost_vetra)} "
                     f"{self.hitrost_vetra_enota} "
                     f"in sunki do {self.decimalna_vejica(self.sunki_vetra)} "
                     f"{self.sunki_vetra_enota}. ")
            return izpis

    def dan_izpis(self
                  ) -> str:
        """
        podatke o dnevu pretvori v besedilo
        """
        if not Arso.preveri_prisotnost_podatkov((self.sončni_vzhod,
                                                 self.sončni_zahod,
                                                 self.dolžina_dneva,
                                                 self.zaporedni_v_letu)):
            return

        izpis = (f"Danes je {self.datum_izpis(self.sončni_vzhod)}, tj. "
                 f"{self.zaporedni_v_letu}. dan v letu. Sončni vzhod je ob "
                 f"{self.ura_izpis(self.sončni_vzhod)}, zahod ob "
                 f"{self.ura_izpis(self.sončni_zahod)}, dan traja "
                 f"{str(self.dolžina_dneva)[:-3].replace(':', '.')}. ")
        return izpis


vremenko.beleženje.beleženje(None)
y = VremenskiPodatki("Ljubljana")
y.zberi_podatke()
y.obdelaj_podatke()
v = Vreme(y.kraj, *y.vrednosti)
print(v.vreme_izpis() + v.veter_izpis() + v.dan_izpis())
z = OnesnaženostPodatki("ljubljana")
z.čist_zrak()
o = Onesnaženost(z.kraj, *z.vrednosti)
print(o.onesnaženost_izpis())

pass
