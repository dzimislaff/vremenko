#!/usr/bin/env python
# -*- coding: 'UTF-8' -*-

BAZA = ('http://meteo.arso.gov.si/uploads/probase/www/observ/surface/text/sl/'
        'observationAms_')
ZRAK = 'http://www.arso.gov.si/xml/zrak/ones_zrak_urni_podatki_zadnji.xml'


# slovar s kombinacijo povezav: osnova + končnica
KRAJI_URL = {
    'Ljubljana': (BAZA + 'LJUBL-ANA_BEZIGRAD_latest.xml'),
    'Novo mesto': (BAZA + 'NOVO-MES_latest.xml'),
    'Rogaška Slatina': (BAZA + 'ROGAS-SLA_latest.xml'),
    'Metlika': (BAZA + 'METLIKA_latest.xml'),
    'Črnomelj': (BAZA + 'CRNOMELJ_latest.xml'),
    'Koper': (BAZA + 'KOPER_KAPET-IJA_latest.xml'),
    'Celje': (BAZA + 'CELJE_MEDLOG_latest.xml'),
    'Kočevje': (BAZA + 'KOCEVJE_latest.xml'),
    'Maribor': (BAZA + 'MARIBOR_VRBAN-PLA_latest.xml'),
    'Podčetrtek': (BAZA + 'PODCE-TEK_ATOMS-TOP_latest.xml'),
    'Bilje pri Novi Gorici': (BAZA + 'NOVA-GOR_BILJE_latest.xml'),
    'Marinča vas': (BAZA + 'MARIN-VAS_latest.xml'),
    'Murska Sobota': (BAZA + 'MURSK-SOB_latest.xml'),
    'Trbovlje': (BAZA + 'TRBOVLJE_latest.xml'),
    'Krško': (BAZA + 'KRSKO_NEK_latest.xml'),
    'Nanos (1242 m)': (BAZA + 'NANOS_latest.xml'),
    'Rogla (1494 m)': (BAZA + 'ROGLA_latest.xml'),
    'Kredarica (2514 m)': (BAZA + 'KREDA-ICA_latest.xml'),
}

KRAJI_SKLONI = {
    'Ljubljana': 'Ljubljano',
    'Novo mesto': 'Novo mesto',
    'Rogaška Slatina': 'Rogaško Slatino',
    'Metlika': 'Metliko',
    'Črnomelj': 'Črnomelj',
    'Koper': 'Koper',
    'Celje': 'Celje',
    'Kočevje': 'Kočevje',
    'Maribor': 'Maribor',
    'Podčetrtek': 'Podčetrtek',
    'Bilje pri Novi Gorici': 'Bilje pri Novi Gorici',
    'Marinča vas': 'Marinčo vas',
    'Murska Sobota': 'Mursko Soboto',
    'Trbovlje': 'Trbovlje',
    'Krško': 'Krško',
    'Nanos (1242 m)': 'Nanos (1242 m)',
    'Rogla (1494 m)': 'Roglo (1494 m)',
    'Kredarica (2514 m)': 'Kredarico',
}

# slovar z imenom kategorije in xpathom do podatka v XML-datoteki in enoto
VETER = {
    'Smer vetra': ('/data/metData/ddavg_longText'),
    'Hitrost vetra': ('/data/metData/ffavg_val', 'm/s'),
    'Sunki vetra': ('/data/metData/ffmax_val_kmh', 'm/s'),
}


# slovar z imenom kategorije in xpathom do podatka v XML-datoteki in enoto
VREME = {
    'Opis vremena': ('/data/metData/nn_icon-wwsyn_icon'),
    'Temperatura': ('/data/metData/t', '°C'),
    'Relativna vlaga': ('/data/metData/rh', '%'),
    'Tlak': ('/data/metData/mslavg', 'hPa'),
    'Vsota padavin': ('/data/metData/rr_val', 'mm'),
    'Povprečno sončno obsevanje': ('/data/metData/gSunRadavg', 'W/m2'),
}


# slovar s prevodom vremenskih oznak
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


# slovar z imenom kraja in šifro
ZRAK_ŠIFRE = {
    'Ljubljana': 'E21',
    'Maribor': 'E22',
    'Celje': 'E23',
    'Nova Gorica': 'E25',
    'Koper': 'E30',
    'Murska Sobota': 'E24',
    'Murska Sobota': 'E24',
    'Trbovlje': 'E26',
}


# slovar z z vrsto onesnaženja, enoto in mejno vrednostjo
ZRAK_KATEGORIJE = {
    'pm10': ('µg/m³', 50),
    'so2': ('µg/m³', 350),
    'co': ('mg/m³', 10),
    'o3': ('µg/m³', 180),
    'no2': ('µg/m³', 200),
}
