import requests

from common.config import Config
from common.login_helper import LoginHelper

HTTP_OK = 200
HTTP_FORBIDDEN = 403
HTTP_CONFLICT = 409
HTTP_NOT_FOUND = 404
HTTP_METHOD_NOT_ALLOWED = 405
ALLOWED_STATUS_CODES = {200, 400, 401, 403, 500}


def auth_headers() -> dict[str, str]:
    token = LoginHelper().login(username='admin', password='admin123')
    assert token, '登录失败，无法执行代理分销接口测试'
    return {'Authorization': f'Bearer {token}'}


def auth_headers_for_user(username: str, password: str = 'admin123') -> dict[str, str]:
    token = LoginHelper().login(username=username, password=password)
    assert token, f'账号 {username} 登录失败，无法执行代理分销接口测试'
    return {'Authorization': f'Bearer {token}'}


def test_distribution_core_routes_exist() -> None:
    headers = auth_headers()
    routes = [
        ('GET', f'{Config.backend_url}/admin/agent-tree'),
        ('GET', f'{Config.backend_url}/admin/agent-detail/1'),
        ('GET', f'{Config.backend_url}/agent/direct-agents'),
        ('GET', f'{Config.backend_url}/bet/link/list'),
        ('GET', f'{Config.backend_url}/bet/my-bets'),
        ('GET', f'{Config.backend_url}/report/dashboard'),
        ('GET', f'{Config.backend_url}/report/my-earnings'),
        ('GET', f'{Config.backend_url}/commission/config'),
    ]
    session = requests.Session()
    for method, url in routes:
        response = session.request(method, url, headers=headers)
        assert response.status_code != HTTP_NOT_FOUND, f'路由 {url} 不存在'
        assert response.status_code != HTTP_METHOD_NOT_ALLOWED, f'路由 {url} 请求方法不匹配'
        assert response.status_code in ALLOWED_STATUS_CODES, f'路由 {url} 返回状态异常: {response.status_code}'
        body = response.json()
        assert 'code' in body, f'路由 {url} 响应结构异常: {body}'


def test_distribution_conflict_and_forbidden_status_codes() -> None:
    session = requests.Session()
    l1_headers = auth_headers_for_user('agent_l1_demo_01')
    l2_headers = auth_headers_for_user('agent_l2_demo_01')
    customer_headers = auth_headers_for_user('customer_l1_demo_01')

    create_response = session.post(
        f'{Config.backend_url}/bet/link/create',
        json={
            'linkName': 'api-status-smoke',
            'betDesc': 'status smoke',
            'odds': 2.0,
            'expireAt': '2099-01-01 12:00:00',
            'maxUsers': 5,
        },
        headers=l1_headers,
    )
    assert create_response.status_code == HTTP_OK, create_response.text
    create_payload = create_response.json()
    link_id = create_payload['data']['linkId']
    token = create_payload['data']['token']

    first_confirm = session.post(
        f'{Config.backend_url}/bet/open/{token}/confirm',
        json={'betAmount': 100},
        headers=customer_headers,
    )
    assert first_confirm.status_code == HTTP_OK, first_confirm.text

    second_confirm = session.post(
        f'{Config.backend_url}/bet/open/{token}/confirm',
        json={'betAmount': 100},
        headers=customer_headers,
    )
    assert second_confirm.status_code == HTTP_CONFLICT, second_confirm.text

    forbidden_response = session.put(
        f'{Config.backend_url}/bet/link/{link_id}/confirm-result',
        json={'isWin': 1},
        headers=l2_headers,
    )
    assert forbidden_response.status_code == HTTP_FORBIDDEN, forbidden_response.text
