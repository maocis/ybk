from collections import defaultdict

from flask import render_template
from flask.ext.login import login_required

from ybk.settings import CONFS
from ybk.models import Quote

from .views import frontend


@frontend.route('/walkthrough/')
@login_required
def walkthrough():
    def open_at(exchange):
        q = Quote.query_one({'exchange': exchange},
                            sort=[('quote_at', 1)])
        d = q.quote_at if q else None
        return d.strftime('%Y年%m月') if d else '尚未'

    def get_bes(CONFS):
        bes = defaultdict(list)
        for c in CONFS:
            for bank in c['opening']['bank']:
                bes[bank].append(c['abbr'])
        return bes

    nav = 'walkthrough'
    oas = [[c['abbr'], c['opening']['url'],
            open_at(c['abbr']), c['opening']['guide']]
           for c in CONFS]
    oas = sorted(oas, key=lambda x: x[2])
    downloads = [[c['abbr'], c['opening']['download']]
                 for c in CONFS]
    bes = get_bes(CONFS)

    return render_template('frontend/walkthrough.html', **locals())
