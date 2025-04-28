from bs4 import BeautifulSoup


def parse_html(response):
    result = {}
    page = response.text

    soup = BeautifulSoup(page, 'html.parser')

    h1 = soup.find('h1')
    title = soup.find('title')
    descr = soup.find('meta', attrs={'name': 'description'})

    result['status_code'] = response.status_code
    result['h1'] = h1.get_text().strip() if h1 else ''
    result['title'] = title.get_text().strip() if title else ''
    result['description'] = descr.get('content', '').strip() if descr else ''

    return result
