#!/usr/bin/env python
# -*- coding: 'UTF-8' -*-

import datetime
import vremenko.poštar
import vremenko.vreme

stran_vode = vremenko.poštar.pridobi_xml(
    "https://www.arso.gov.si/xml/vode/hidro_podatki_zadnji.xml"
)

šifre = {
    "Metlika": "4860",
}

xpath = (
    "temp_vode",
    "datum",
)


def voda_podatki(kraj: str,
                 šifre: dict,
                 xpath: tuple,
                 stran  # lxml.etree._Element
                 ) -> list:
    šifra = šifre["Metlika"]
    vrednosti = []
    for i in xpath:
        vrednosti.append(stran.xpath(
            f"/arsopodatki/postaja[@sifra='{šifra}']/{i}")[0].text)
    vrednosti[1] = vremenko.vreme.čas_uredi(vrednosti[1])
    return vrednosti


def voda_izpis_glava(kraj: str,
                     čas: datetime.datetime
                     ) -> str:
    izpis = f"Podatki za {kraj}\n"
    if čas:
        izpis = f"{izpis.rstrip()} ob {vremenko.vreme.ura_izpis(čas)}.\n"
    return izpis


def izpis(kraj: str,
          podatki: list,
          ) -> str:
    if not any(podatki):
        return "Podatkov o vodah trenutno ni. "
    izpis = voda_izpis_glava(kraj, podatki[1])
    izpis += f"Temperatura vode je {podatki[0].replace('.', ',')} °C."
    return izpis


def vode():
    kraj = "Metlika"
    podatki = voda_podatki(kraj, šifre, xpath, stran_vode)
    besedilo = izpis(kraj, podatki)
    print(besedilo)


if __name__ == '__main__':
    vode()
