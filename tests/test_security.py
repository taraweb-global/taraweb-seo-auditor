import requests

import app as crawler


def csrf_headers():
    return {'X-TaraWeb-CSRF': crawler.CSRF_TOKEN}


def test_homepage_is_taraweb_branded_and_hardened():
    response = crawler.app.test_client().get('/')

    assert response.status_code == 200
    assert b'TaraWeb SEO Auditor' in response.data
    assert b'Open-source attribution' in response.data
    assert b'https://taraweb.tech/' in response.data
    assert b'https://github.com/taraweb-global/taraweb-seo-auditor' in response.data
    assert b'noindex,nofollow,noarchive' in response.data
    assert b'/static/favicon.ico' in response.data
    assert b'Configure your crawl' in response.data
    assert b'class="settings-group advanced-settings"' in response.data
    assert b'id="crawler-live-status"' in response.data
    assert response.headers['X-Content-Type-Options'] == 'nosniff'
    assert response.headers['X-Frame-Options'] == 'DENY'
    assert response.headers['Referrer-Policy'] == 'no-referrer'


def test_state_change_requires_csrf_token():
    response = crawler.app.test_client().post('/detect-cms', json={'url': 'https://example.com'})

    assert response.status_code == 403
    assert response.get_json()['error'] == 'Invalid or missing request token.'


def test_private_target_is_blocked_by_default():
    response = crawler.app.test_client().post(
        '/detect-cms',
        json={'url': 'http://127.0.0.1:8080'},
        headers=csrf_headers(),
    )

    assert response.status_code == 400
    assert 'blocked by default' in response.get_json()['error']


def test_credentialed_target_is_rejected():
    error = crawler._target_url_error('https://user:password@example.com/')

    assert error == 'Credentials embedded in URLs are not allowed.'


def test_public_target_validation(monkeypatch):
    monkeypatch.setattr(
        crawler.socket,
        'getaddrinfo',
        lambda host, *args, **kwargs: [(
            crawler.socket.AF_INET,
            crawler.socket.SOCK_STREAM,
            6,
            '',
            ('127.0.0.1' if host == '127.0.0.1' else '93.184.216.34', 443),
        )],
    )

    assert crawler._target_url_error('https://example.com/') is None


def test_browser_triggered_source_mutation_is_unavailable():
    response = crawler.app.test_client().post('/update', headers=csrf_headers())

    assert response.status_code == 410
    assert response.get_json()['ok'] is False

    restart = crawler.app.test_client().post('/restart', headers=csrf_headers())
    assert restart.status_code == 410
    assert restart.get_json()['ok'] is False


def test_safe_session_blocks_private_redirect_before_second_request(monkeypatch):
    calls = []

    def fake_request(_session, method, url, **kwargs):
        calls.append(url)
        response = requests.Response()
        response.status_code = 302
        response.url = url
        response.headers['Location'] = 'http://127.0.0.1/admin'
        response._content = b''
        response._content_consumed = True
        return response

    monkeypatch.setattr(
        crawler.socket,
        'getaddrinfo',
        lambda host, *args, **kwargs: [(
            crawler.socket.AF_INET,
            crawler.socket.SOCK_STREAM,
            6,
            '',
            ('127.0.0.1' if host == '127.0.0.1' else '93.184.216.34', 443),
        )],
    )
    monkeypatch.setattr(requests.Session, 'request', fake_request)

    with crawler.SafeSession() as session:
        try:
            session.get('https://example.com/', allow_redirects=True)
            assert False, 'private redirect should be rejected'
        except crawler.UnsafeTargetError as exc:
            assert 'Blocked redirect target' in str(exc)

    assert calls == ['https://example.com/']


def test_safe_session_does_not_inherit_proxy_or_netrc_environment():
    with crawler.SafeSession() as session:
        assert session.trust_env is False


def test_safe_session_rejects_oversized_response_before_reading(monkeypatch):
    response = requests.Response()
    response.status_code = 200
    response.url = 'https://example.com/'
    response.headers['Content-Length'] = str(crawler.MAX_FETCH_BYTES + 1)
    response._content = b''
    response._content_consumed = True

    monkeypatch.setattr(crawler, '_target_url_error', lambda _value: None)
    monkeypatch.setattr(requests.Session, 'request', lambda *args, **kwargs: response)

    with crawler.SafeSession() as session:
        try:
            session.get('https://example.com/')
            assert False, 'oversized response should be rejected'
        except crawler.ResponseTooLargeError:
            pass


def test_default_bind_address_is_loopback():
    assert crawler.APP_HOST == '127.0.0.1'


def test_robots_pattern_matching_regression():
    assert crawler._robots_pattern_match('/private/*', 'https://example.com/private/report')
    assert not crawler._robots_pattern_match('/private/*', 'https://example.com/public/report')


def test_invalid_crawl_limits_return_clear_client_error():
    response = crawler.app.test_client().post(
        '/crawl',
        json={'url': 'https://example.com', 'max_pages': 'many'},
        headers=csrf_headers(),
    )

    assert response.status_code == 400
    assert response.get_json()['error'] == 'Max pages must be a whole number.'


def test_out_of_range_worker_count_is_rejected(monkeypatch):
    monkeypatch.setattr(crawler, '_target_url_error', lambda value: None)
    response = crawler.app.test_client().post(
        '/crawl',
        json={'url': 'https://example.com', 'max_workers': 21},
        headers=csrf_headers(),
    )

    assert response.status_code == 400
    assert response.get_json()['error'] == 'Workers must be between 1 and 20.'


def test_missing_crawl_url_uses_json_error_response():
    response = crawler.app.test_client().post('/crawl', json={}, headers=csrf_headers())

    assert response.status_code == 400
    assert response.is_json
    assert response.get_json()['error'] == 'URL is required'


def test_invalid_saved_crawl_name_is_rejected():
    response = crawler.app.test_client().get('/crawl/load?file=..%2Fsecret.json')

    assert response.status_code == 400
    assert response.get_json()['error'] == 'Invalid file'


def test_security_headers_disable_dynamic_response_caching():
    response = crawler.app.test_client().get('/')

    assert response.headers['Cross-Origin-Opener-Policy'] == 'same-origin'
    assert response.headers['Cross-Origin-Resource-Policy'] == 'same-origin'
    assert response.headers['Cache-Control'] == 'no-store'
