#!/usr/bin/env python
# -*- coding: 'UTF-8' -*-

BASE = ('http://meteo.arso.gov.si/uploads/probase/www/observ/surface/text/sl/'
        'observationAms_')
ONESNAŽENOST = 'http://www.arso.gov.si/xml/zrak/ones_zrak_urni_podatki_zadnji.xml'


# slovar s kombinacijo povezav: osnova + končnica
KRAJI = {
    'Ljubljana': (BASE + 'LJUBL-ANA_BEZIGRAD_latest.xml'),
    'Novo mesto': (BASE + 'NOVO-MES_latest.xml'),
    'Rogaška Slatina': (BASE + 'ROGAS-SLA_latest.xml'),
    'Metlika': (BASE + 'METLIKA_latest.xml'),
    'Črnomelj': (BASE + 'CRNOMELJ_latest.xml'),
    'Metlika': (BASE + 'METLIKA_latest.xml'),
    'Koper': (BASE + 'KOPER_KAPET-IJA_latest.xml'),
    'Celje': (BASE + 'CELJE_MEDLOG_latest.xml'),
    'Kočevje': (BASE + 'KOCEVJE_latest.xml'),
    'Maribor': (BASE + 'MARIBOR_VRBAN-PLA_latest.xml'),
    'Podčetrtek': (BASE + 'PODCE-TEK_ATOMS-TOP_latest.xml'),
    'Bilje pri Novi Gorici': (BASE + 'NOVA-GOR_BILJE_latest.xml'),
    'Marinča vas': (BASE + 'MARIN-VAS_latest.xml'),
    'Nanos (1242 m)': (BASE + 'NANOS_latest.xml'),
    'Rogla (1494 m)': (BASE + 'ROGLA_latest.xml'),
    'Kredarica (2514 m)': (BASE + 'KREDA-ICA_latest.xml'),
}

# seznam s potjo do podatka (xpath) v XML-datoteki in imenom kategorije
KATEGORIJE = (
    ('/data/metData/nn_icon-wwsyn_icon', 'Opis vremena'),
    ('/data/metData/t', 'Temperatura', '°C'),
    ('/data/metData/rhavg', 'Relativna vlažnost', '%'),
    ('/data/metData/rr_val', 'Vsota padavin v časovnem intervalu', 'mm'),
    ('/data/metData/mslavg', 'Tlak', 'hPa'),
    ('/data/metData/ddavg_longText', 'Smer vetra'),
    ('/data/metData/ffavg_val', 'Hitrost vetra', 'm/s'),
    ('/data/metData/sunrise', 'Sončni vzhod'),
    ('/data/metData/sunset', 'Sončni zahod'),
    ('/data/metData/gSunRadavg', 'Povprečno sončno obsevanje', 'W/m2'),
)

VETER = {
    'Smer vetra': ('/data/metData/ddavg_longText'),
    'Hitrost vetra': ('/data/metData/ffavg_val', 'm/s'),
    'Sunki vetra': ('/data/metData/ffmax_val_kmh', 'm/s'),
}

VREME = {
    'Opis vremena': ('/data/metData/nn_icon-wwsyn_icon'),
    'Temperatura': ('/data/metData/t', '°C'),
    'Relativna vlažnost': ('/data/metData/rhavg', '%'),
    'Tlak': ('/data/metData/mslavg', 'hPa'),
    'Vsota padavin v časovnem intervalu': ('/data/metData/rr_val', 'mm')
}


OPIS = {
    'clear': 'Jasno je',
    'mostClear': 'Pretežno jasno je',
    'partCloudy': 'Delno oblačno je',
    'modCloudy': 'Zmerno oblačno je',
    'prevCloudy': 'Pretežno oblačno je',
    'overcast': 'Oblačno je',
    'FG': 'Megla je',
    'RA': 'Rosi',
    'RASN': 'Dež s snegom je',
    'SN': 'Sneži',
    'TS': 'Nevihta je',
    'TSGR': 'Nevihta s točo je',
    'lightRA': 'Rahlo dežuje',
    'modRA': 'Dežuje',
    'overcast_lightRA': 'Oblačno je z manjšimi padavinami',
    'overcast_modRA': 'Oblačno je z zmernimi padavinami',
    'overcast_heavyRA': 'Oblačno je z močnimi padavinami',
    'prevCloudy_lightRA': 'Pretežno oblačno je z manjšimi padavinami',
    'overcast_lightSN': 'Oblačno z manjšim sneženjem',
}


ŠIFRE_ONESNAŽENOSTI = {
    "Ljubljana": "E21",
    "Maribor": "E22",
    "Celje": "E23",
    "Nova Gorica": "E25",
    "Koper": "E30",
}

KATEGORIJE_ONESNAŽENOSTI = {
    'pm10': ('µg/m³', 50),
    'so2': ('µg/m³', 350),
    'co': ('mg/m³', 10),
    'o3': ('µg/m³', 180),
    'no2': ('µg/m³', 200),
}
