import os
import requests
from dotenv import load_dotenv
from flask import (
    Flask,
    render_template,
    request,
    flash,
    get_flashed_messages,
    url_for,
    redirect
)

from page_analyzer.parser import parse_html
from page_analyzer.utils import (
    validate,
    normalize_url,
)

from page_analyzer.db import (
    get_data_by_name,
    get_data_by_id,
    get_all_urls,
    get_checks_by_id,
    add_url,
    add_check,
)

load_dotenv()

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.route('/')
def index():
    return render_template(
        'index.html',
        url='',
        messages=[]
    )


@app.get('/urls')
def get_urls():
    urls = get_all_urls()
    return render_template(
        'urls.html',
        urls=urls
    )


@app.post('/urls')
def post_new_url():
    url = request.form.to_dict().get('url')
    errors = validate(url)
    if errors:
        for error in errors:
            flash(error, 'danger')
        messages = get_flashed_messages(with_categories=True)
        return render_template(
            'index.html',
            url=url,
            messages=messages
        ), 422

    url = normalize_url(url)
    existing = get_data_by_name(url)
    if existing:
        flash('Страница уже существует', 'info')
        id = existing.id
    else:
        flash('Страница успешно добавлена', 'success')
        id = add_url(url)
    return redirect(url_for('get_url_id', id=id), 302)


@app.get('/urls/<id>')
def get_url_id(id):
    url = get_data_by_id(id)
    checks = get_checks_by_id(id)
    messages = get_flashed_messages(with_categories=True)
    return render_template(
        'url.html',
        url=url,
        messages=messages,
        checks=checks
    )


@app.post('/urls/<id>/checks')
def post_checks(id):
    url = get_data_by_id(id)

    try:
        resp = requests.get(url.name)
        resp.raise_for_status()
    except requests.RequestException:
        flash('Произошла ошибка при проверке', 'danger')
        return redirect(url_for('get_url_id', id=id), 302)

    data = parse_html(resp)
    data['id'] = id
    flash('Страница успешно проверена', 'success')

    add_check(data)
    return redirect(url_for('get_url_id', id=id), 302)


@app.errorhandler(404)
def page_not_found(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500
