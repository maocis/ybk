import pathlib
import yaml

SITES = [
    'zgqbyp',
    'jscaee',
    'shscce',
]

ABBRS = {
    yaml.load((pathlib.Path(__file__).parent
               / (site + '.yaml')).open())['abbr']: site
    for site in SITES
}

CONFS = [
    yaml.load((pathlib.Path(__file__).parent
               / (site + '.yaml')).open())
    for site in SITES
]
