import os
from psycopg2 import connect, extras
from dotenv import load_dotenv
from datetime import date

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')


def connect_db():
    return connect(DATABASE_URL)


def get_data_by_param(query, param):
    conn = connect_db()
    with conn.cursor(cursor_factory=extras.NamedTupleCursor) as curs:
        curs.execute(query, (param,))
        existing = curs.fetchone()
    conn.close()
    return existing


def get_data_by_name(url):
    return get_data_by_param('SELECT * FROM urls WHERE name=%s', url)


def get_data_by_id(id):
    return get_data_by_param('SELECT * FROM urls WHERE id=%s', id)


def get_checks_by_id(url_id):
    connect_ = connect_db()
    with connect_.cursor(cursor_factory=extras.NamedTupleCursor) as curs:
        query_select = """
            SELECT *
            FROM url_checks
            WHERE url_id=%s
            ORDER BY id DESC
        """
        curs.execute(query_select, (url_id,))
        existing = curs.fetchall()
    connect_.close()
    return existing


def get_all_urls():
    connect_ = connect_db()
    with connect_.cursor(cursor_factory=extras.NamedTupleCursor) as curs:
        query_select = """
            SELECT
                urls.id,
                urls.name,
                url_checks.status_code,
                MAX(url_checks.created_at) AS last_check
            FROM urls
            LEFT JOIN url_checks ON urls.id = url_checks.url_id
            GROUP BY urls.id, urls.name, url_checks.status_code
            ORDER BY urls.id DESC;
        """
        curs.execute(query_select)
        urls = curs.fetchall()
    connect_.close()
    return urls


def add_url(url):
    connect_ = connect_db()
    with connect_.cursor(cursor_factory=extras.NamedTupleCursor) as curs:
        curs.execute(
            'INSERT INTO urls (name, created_at) VALUES (%s, %s) RETURNING id',
            (url, date.today())
        )
        id = curs.fetchone().id
    connect_.commit()
    connect_.close()
    return id


def add_check(datas):
    connect_ = connect_db()
    with connect_.cursor(cursor_factory=extras.NamedTupleCursor) as curs:
        query_insert = """
            INSERT INTO url_checks (
                url_id,
                status_code,
                h1,
                title,
                description,
                created_at
            )
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        curs.execute(query_insert, (
            datas['id'],
            datas['status_code'],
            datas['h1'],
            datas['title'],
            datas['description'],
            date.today()
        ))
    connect_.commit()
    connect_.close()
