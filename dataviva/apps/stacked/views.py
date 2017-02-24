# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, g, request, abort
from dataviva.apps.general.views import get_locale
from dataviva.translations.dictionary import dictionary
from dataviva.apps.title.views import get_title
from dataviva.utils.graphs_services import *
import urllib
import json

mod = Blueprint('stacked', __name__,
				template_folder='templates',
				url_prefix='/<lang_code>/stacked',
				static_folder='static')


@mod.url_value_preprocessor
def pull_lang_code(endpoint, values):
	g.locale = values.pop('lang_code')


@mod.url_defaults
def add_language_code(endpoint, values):
	values.setdefault('lang_code', get_locale())


@mod.before_request
def before_request():
    g.page_type = mod.name


@mod.route('/<dataset>/<area>/<size>')
def index(dataset, area, size):
    filters = []
    title_attrs = {}

    services = {'product': product_service, 'id_ibge': location_service, 'wld':
                wld_service, 'occupation': occupation_service, 'industry': industry_service}

    for key, value in request.args.items():
        if key == 'type':
            title_attrs['type'] = value

    if value:
        if key in services:
            filters.append(services[key](value))
            if key == 'id_ibge':
                title_attrs['location'] = value
            elif key == 'wld':
                title_attrs['partner'] = value
            else:
                title_attrs[key] = value
        else:
            filters.append((key, value))

    filters = urllib.urlencode(filters)

    title, subtitle = get_title(dataset, area, 'stacked', title_attrs)

    return render_template('stacked/index.html',
                           dataset=dataset,
                           area=area,
                           size=size,
                           filters=filters,
                           title=title or 'Title',
                           subtitle=subtitle or '',
                           dictionary=json.dumps(dictionary()))