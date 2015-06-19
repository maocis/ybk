import pathlib
import yaml


SITES = [p.parts[-1].split('.')[0]
         for p in filter(lambda x: x.match('*.yaml'),
                         (pathlib.Path(__file__).parent / 'conf.d').iterdir())]

ABBRS = {
    yaml.load((pathlib.Path(__file__).parent / 'conf.d'
               / (site + '.yaml')).open())['abbr']: site
    for site in SITES
}

CONFS = [
    yaml.load((pathlib.Path(__file__).parent / 'conf.d'
               / (site + '.yaml')).open())
    for site in SITES
]


def get_conf(abbr_or_site):
    if abbr_or_site in ABBRS:
        site = ABBRS[abbr_or_site]
    else:
        site = abbr_or_site

    return CONFS[SITES.index(site)]
