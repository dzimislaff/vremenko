#!/usr/bin/env python
# -*- coding: 'UTF-8' -*-

# https://github.com/navdeep-G/setup.py
# https://github.com/navdeep-G/setup.py/blob/master/setup.py

from setuptools import setup

različica_programa = "0.2.5.4"
ime_programa = 'vremenko'
opis_programa = "Preprost program, ki trenutne vremenske razmere izpiše ali \
                 shrani v podatkovno bazo. Podatke pridobi z ARSO-ve spletne \
                 strani."
spletna_povezava = 'https://github.com/dzimislaff/vremenko'
email = 'nejc.mobilc@gmail.com'
avtor = 'nejc'
različica_pythona = "!=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, !=3.5.*, >=3.6.0"
zahtevani_moduli = [
    "click", "lxml", "python-dateutil", "requests"
]
dodatni_moduli = {
    "testiranje": ["pytest"],
}


setup(
    name=ime_programa,
    version=različica_programa,
    description=opis_programa,
    author=avtor,
    author_email=email,
    python_requires=različica_pythona,
    install_requires=zahtevani_moduli,
    entry_points="""
        [console_scripts]
        # vremenko=ukaznavrstica:ukaznavrstica
        vremenko=vremenko.ukaznavrstica:ukaznavrstica
    """,
    classifiers=[
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Natural Language :: Slovenian,'
    ],
)