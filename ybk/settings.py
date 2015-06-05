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
