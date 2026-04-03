from __future__ import annotations

from datetime import datetime, timedelta
from typing import TypedDict
from uuid import uuid4

import pytest
import requests

from common.config import Config
from common.login_helper import LoginHelper

HTTP_OK = 200
HTTP_CONFLICT = 409
BET_AMOUNT = 100
WIN_AMOUNT = 200
WIN_PROFIT = 100
MIN_DIRECT_BET_COMMISSION = 2.5
MIN_DIRECT_PROFIT_COMMISSION = 50
MIN_TOKEN_LENGTH = 16
DEFAULT_TEST_PASSWORD = 'admin123'
L1_BATCH_CUSTOMERS = [
    'customer_l1_demo_01',
    'customer_l1_demo_02',
    'customer_l1_demo_03',
    'customer_l1_demo_04',
]
L2_AGENT_BATCH_USERS = ['agent_l2_demo_01', 'agent_l2_demo_02']
L2A_BATCH_CUSTOMERS = [
    'customer_l2a_demo_01',
    'customer_l2a_demo_02',
    'customer_l2a_demo_03',
    'customer_l2a_demo_04',
]


class DistributionContext(TypedDict):
    session: requests.Session
    agent_headers: dict[str, str]
    customer_headers: dict[str, str]
    agent_username: str
    customer_username: str


class WorkflowContext(TypedDict):
    link_id: int
    token: str
    link_name: str


def auth_headers(username: str, password: str) -> dict[str, str]:
    token = LoginHelper().login(username=username, password=password)
    assert token, f'账号 {username} 登录失败，无法执行分销流程测试'
    return {'Authorization': f'Bearer {token}'}


def auth_headers_or_skip(username: str, password: str = DEFAULT_TEST_PASSWORD) -> dict[str, str]:
    token = LoginHelper().login(username=username, password=password)
    if not token:
        pytest.skip(f'测试账号 {username} 不存在或密码不匹配，请先导入分销测试账号 SQL')
    return {'Authorization': f'Bearer {token}'}


def assert_json_response(response: requests.Response) -> dict:
    assert response.status_code == HTTP_OK, f'接口调用失败: {response.status_code}, body={response.text}'
    payload = response.json()
    assert payload.get('code') == HTTP_OK, f'业务响应失败: {payload}'
    return payload


def create_bet_link(context: DistributionContext, *, prefix: str) -> WorkflowContext:
    link_name = f'{prefix}-{uuid4().hex[:8]}'
    create_payload = {
        'linkName': link_name,
        'betDesc': 'pytest distribution workflow',
        'odds': 2.0,
        'expireAt': (datetime.now() + timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S'),
        'maxUsers': 10,
        'remark': 'created by integration test',
    }
    create_response = context['session'].post(
        f'{Config.backend_url}/bet/link/create',
        json=create_payload,
        headers=context['agent_headers'],
    )
    create_data = assert_json_response(create_response)
    return WorkflowContext(
        link_id=create_data['data']['linkId'],
        token=create_data['data']['token'],
        link_name=link_name,
    )


def confirm_and_settle_workflow(context: DistributionContext, workflow: WorkflowContext, *, is_win: int = 1) -> None:
    confirm_response = context['session'].post(
        f'{Config.backend_url}/bet/open/{workflow["token"]}/confirm',
        json={'betAmount': BET_AMOUNT},
        headers=context['customer_headers'],
    )
    confirm_data = assert_json_response(confirm_response)
    assert confirm_data['data']['linkId'] == workflow['link_id']

    settle_response = context['session'].put(
        f'{Config.backend_url}/bet/link/{workflow["link_id"]}/confirm-result',
        json={'isWin': is_win},
        headers=context['agent_headers'],
    )
    assert_json_response(settle_response)


def create_and_settle_workflow(
    context: DistributionContext,
    *,
    prefix: str,
    is_win: int,
    bet_amount: float = BET_AMOUNT,
    odds: float = 2.0,
) -> WorkflowContext:
    link_name = f'{prefix}-{uuid4().hex[:8]}'
    create_payload = {
        'linkName': link_name,
        'betDesc': 'pytest acceptance workflow',
        'odds': odds,
        'expireAt': (datetime.now() + timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S'),
        'maxUsers': 10,
    }
    create_response = context['session'].post(
        f'{Config.backend_url}/bet/link/create',
        json=create_payload,
        headers=context['agent_headers'],
    )
    create_data = assert_json_response(create_response)
    workflow = WorkflowContext(
        link_id=create_data['data']['linkId'],
        token=create_data['data']['token'],
        link_name=link_name,
    )
    confirm_response = context['session'].post(
        f'{Config.backend_url}/bet/open/{workflow["token"]}/confirm',
        json={'betAmount': bet_amount},
        headers=context['customer_headers'],
    )
    assert_json_response(confirm_response)
    settle_response = context['session'].put(
        f'{Config.backend_url}/bet/link/{workflow["link_id"]}/confirm-result',
        json={'isWin': is_win},
        headers=context['agent_headers'],
    )
    assert_json_response(settle_response)
    return workflow


@pytest.fixture(scope='module')
def distribution_context() -> DistributionContext:
    agent_username = Config.distribution_agent_username
    agent_password = Config.distribution_agent_password
    customer_username = Config.distribution_customer_username
    customer_password = Config.distribution_customer_password
    if not all([agent_username, agent_password, customer_username, customer_password]):
        pytest.skip(
            '未配置分销集成测试账号，请设置 DIST_TEST_AGENT_USERNAME、DIST_TEST_AGENT_PASSWORD、'
            'DIST_TEST_CUSTOMER_USERNAME、DIST_TEST_CUSTOMER_PASSWORD'
        )
    return DistributionContext(
        session=requests.Session(),
        agent_headers=auth_headers(agent_username, agent_password),
        customer_headers=auth_headers(customer_username, customer_password),
        agent_username=agent_username,
        customer_username=customer_username,
    )


@pytest.fixture(scope='module')
def l1_batch_customer_headers() -> dict[str, dict[str, str]]:
    return {username: auth_headers_or_skip(username) for username in L1_BATCH_CUSTOMERS}


@pytest.fixture(scope='module')
def l2_agent_headers() -> dict[str, dict[str, str]]:
    return {username: auth_headers_or_skip(username) for username in L2_AGENT_BATCH_USERS}


@pytest.fixture(scope='module')
def created_workflow(distribution_context: DistributionContext) -> WorkflowContext:
    return create_bet_link(distribution_context, prefix='created-link')


@pytest.fixture(scope='module')
def settled_workflow(distribution_context: DistributionContext) -> WorkflowContext:
    workflow = create_bet_link(distribution_context, prefix='settled-link')
    confirm_and_settle_workflow(distribution_context, workflow)
    return workflow


@pytest.mark.integration
def test_create_bet_link_returns_token(created_workflow: WorkflowContext) -> None:
    assert created_workflow['link_id'] > 0
    assert len(created_workflow['token']) >= MIN_TOKEN_LENGTH
    assert created_workflow['link_name'].startswith('created-link-')


@pytest.mark.integration
def test_bet_link_list_contains_created_link(
    distribution_context: DistributionContext, created_workflow: WorkflowContext
) -> None:
    response = distribution_context['session'].get(
        f'{Config.backend_url}/bet/link/list',
        params={'pageNum': 1, 'pageSize': 20, 'linkName': created_workflow['link_name']},
        headers=distribution_context['agent_headers'],
    )
    payload = assert_json_response(response)
    assert any(row['linkId'] == created_workflow['link_id'] for row in payload['rows']), payload


@pytest.mark.integration
def test_open_bet_link_preview_matches_created_link(
    distribution_context: DistributionContext, created_workflow: WorkflowContext
) -> None:
    response = distribution_context['session'].get(
        f'{Config.backend_url}/bet/open/{created_workflow["token"]}',
        headers=distribution_context['customer_headers'],
    )
    payload = assert_json_response(response)
    assert payload['data']['linkId'] == created_workflow['link_id']
    assert payload['data']['linkName'] == created_workflow['link_name']
    assert payload['data']['alreadyConfirmed'] is False


@pytest.mark.integration
def test_agent_direct_customers_route_returns_expected_customer(distribution_context: DistributionContext) -> None:
    response = distribution_context['session'].get(
        f'{Config.backend_url}/agent/direct-customers',
        params={'pageNum': 1, 'pageSize': 50},
        headers=distribution_context['agent_headers'],
    )
    payload = assert_json_response(response)
    assert 'rows' in payload and 'total' in payload
    assert any(row['userName'] == distribution_context['customer_username'] for row in payload['rows']), payload


@pytest.mark.integration
def test_agent_direct_customers_route_contains_batch_customers(distribution_context: DistributionContext) -> None:
    response = distribution_context['session'].get(
        f'{Config.backend_url}/agent/direct-customers',
        params={'pageNum': 1, 'pageSize': 50},
        headers=distribution_context['agent_headers'],
    )
    payload = assert_json_response(response)
    row_user_names = {row['userName'] for row in payload['rows']}
    assert set(L1_BATCH_CUSTOMERS).issubset(row_user_names), payload


@pytest.mark.integration
def test_agent_direct_agents_route_returns_valid_page(distribution_context: DistributionContext) -> None:
    response = distribution_context['session'].get(
        f'{Config.backend_url}/agent/direct-agents',
        params={'pageNum': 1, 'pageSize': 50},
        headers=distribution_context['agent_headers'],
    )
    payload = assert_json_response(response)
    assert 'rows' in payload and 'total' in payload
    assert isinstance(payload['rows'], list)


@pytest.mark.integration
def test_customer_my_bets_contains_settled_link(
    distribution_context: DistributionContext, settled_workflow: WorkflowContext
) -> None:
    response = distribution_context['session'].get(
        f'{Config.backend_url}/bet/my-bets',
        headers=distribution_context['customer_headers'],
    )
    payload = assert_json_response(response)
    target_row = next((row for row in payload['data'] if row['linkId'] == settled_workflow['link_id']), None)
    assert target_row is not None, payload
    assert target_row['betAmount'] == BET_AMOUNT


@pytest.mark.integration
def test_customer_my_earnings_contains_settled_link(
    distribution_context: DistributionContext, settled_workflow: WorkflowContext
) -> None:
    response = distribution_context['session'].get(
        f'{Config.backend_url}/report/my-earnings',
        headers=distribution_context['customer_headers'],
    )
    payload = assert_json_response(response)
    target_row = next((row for row in payload['data']['rows'] if row['linkId'] == settled_workflow['link_id']), None)
    assert target_row is not None, payload
    assert target_row['betAmount'] == BET_AMOUNT


@pytest.mark.integration
def test_duplicate_confirm_returns_conflict(distribution_context: DistributionContext) -> None:
    workflow = create_bet_link(distribution_context, prefix='dup-confirm')
    first_response = distribution_context['session'].post(
        f'{Config.backend_url}/bet/open/{workflow["token"]}/confirm',
        json={'betAmount': BET_AMOUNT},
        headers=distribution_context['customer_headers'],
    )
    assert_json_response(first_response)

    second_response = distribution_context['session'].post(
        f'{Config.backend_url}/bet/open/{workflow["token"]}/confirm',
        json={'betAmount': BET_AMOUNT},
        headers=distribution_context['customer_headers'],
    )
    assert second_response.status_code == HTTP_CONFLICT, second_response.text
    payload = second_response.json()
    assert payload.get('code') == HTTP_CONFLICT, payload


@pytest.mark.integration
def test_duplicate_settle_returns_conflict(distribution_context: DistributionContext) -> None:
    workflow = create_bet_link(distribution_context, prefix='dup-settle')
    confirm_and_settle_workflow(distribution_context, workflow, is_win=1)
    second_response = distribution_context['session'].put(
        f'{Config.backend_url}/bet/link/{workflow["link_id"]}/confirm-result',
        json={'isWin': 1},
        headers=distribution_context['agent_headers'],
    )
    assert second_response.status_code == HTTP_CONFLICT, second_response.text
    payload = second_response.json()
    assert payload.get('code') == HTTP_CONFLICT, payload


@pytest.mark.integration
def test_l2_scope_only_contains_direct_members() -> None:
    headers = auth_headers_or_skip('agent_l2_demo_01')
    session = requests.Session()

    agent_response = session.get(
        f'{Config.backend_url}/agent/direct-agents',
        params={'pageNum': 1, 'pageSize': 20},
        headers=headers,
    )
    agent_payload = assert_json_response(agent_response)
    agent_user_names = {row['userName'] for row in agent_payload['rows']}
    assert agent_user_names == {'agent_l3_demo_01'}, agent_payload

    customer_response = session.get(
        f'{Config.backend_url}/agent/direct-customers',
        params={'pageNum': 1, 'pageSize': 20},
        headers=headers,
    )
    customer_payload = assert_json_response(customer_response)
    customer_user_names = {row['userName'] for row in customer_payload['rows']}
    assert customer_user_names == set(L2A_BATCH_CUSTOMERS), customer_payload


@pytest.mark.integration
def test_settled_win_formula_matches_expected_values(distribution_context: DistributionContext) -> None:
    workflow = create_and_settle_workflow(distribution_context, prefix='formula-win', is_win=1)

    my_earnings_response = distribution_context['session'].get(
        f'{Config.backend_url}/report/my-earnings',
        headers=distribution_context['customer_headers'],
    )
    my_earnings_payload = assert_json_response(my_earnings_response)
    target_row = next((row for row in my_earnings_payload['data']['rows'] if row['linkId'] == workflow['link_id']), None)
    assert target_row is not None, my_earnings_payload
    assert target_row['betAmount'] == BET_AMOUNT
    assert target_row['winAmount'] == WIN_AMOUNT
    assert target_row['profit'] == WIN_PROFIT

    dashboard_response = distribution_context['session'].get(
        f'{Config.backend_url}/report/dashboard',
        params={'pageNum': 1, 'pageSize': 20, 'period': 'day'},
        headers=distribution_context['agent_headers'],
    )
    dashboard_payload = assert_json_response(dashboard_response)
    assert dashboard_payload['data']['totalBetCommission'] >= MIN_DIRECT_BET_COMMISSION
    assert dashboard_payload['data']['totalProfitCommission'] >= MIN_DIRECT_PROFIT_COMMISSION


@pytest.mark.integration
def test_settled_loss_formula_matches_expected_values(distribution_context: DistributionContext) -> None:
    workflow = create_and_settle_workflow(distribution_context, prefix='formula-loss', is_win=0)

    my_earnings_response = distribution_context['session'].get(
        f'{Config.backend_url}/report/my-earnings',
        headers=distribution_context['customer_headers'],
    )
    my_earnings_payload = assert_json_response(my_earnings_response)
    target_row = next((row for row in my_earnings_payload['data']['rows'] if row['linkId'] == workflow['link_id']), None)
    assert target_row is not None, my_earnings_payload
    assert target_row['betAmount'] == BET_AMOUNT
    assert target_row['winAmount'] == 0
    assert target_row['profit'] == -BET_AMOUNT


@pytest.mark.integration
@pytest.mark.parametrize('username', L1_BATCH_CUSTOMERS)
def test_batch_l1_customers_can_access_my_bets(
    distribution_context: DistributionContext,
    l1_batch_customer_headers: dict[str, dict[str, str]],
    username: str,
) -> None:
    response = distribution_context['session'].get(
        f'{Config.backend_url}/bet/my-bets',
        headers=l1_batch_customer_headers[username],
    )
    payload = assert_json_response(response)
    assert isinstance(payload['data'], list)


@pytest.mark.integration
@pytest.mark.parametrize('username', L1_BATCH_CUSTOMERS)
def test_batch_l1_customers_can_access_my_earnings(
    distribution_context: DistributionContext,
    l1_batch_customer_headers: dict[str, dict[str, str]],
    username: str,
) -> None:
    response = distribution_context['session'].get(
        f'{Config.backend_url}/report/my-earnings',
        headers=l1_batch_customer_headers[username],
    )
    payload = assert_json_response(response)
    assert 'summary' in payload['data']
    assert 'rows' in payload['data']


@pytest.mark.integration
def test_agent_dashboard_contains_total_commission(distribution_context: DistributionContext) -> None:
    response = distribution_context['session'].get(
        f'{Config.backend_url}/report/dashboard',
        headers=distribution_context['agent_headers'],
    )
    payload = assert_json_response(response)
    assert 'totalCommission' in payload['data']
    assert 'totalBetAmount' in payload['data']


@pytest.mark.integration
def test_agent_earnings_list_route_returns_page(distribution_context: DistributionContext) -> None:
    response = distribution_context['session'].get(
        f'{Config.backend_url}/report/earnings/list',
        params={'pageNum': 1, 'pageSize': 20},
        headers=distribution_context['agent_headers'],
    )
    payload = assert_json_response(response)
    assert 'rows' in payload and 'total' in payload


@pytest.mark.integration
def test_agent_earnings_trend_route_returns_list(distribution_context: DistributionContext) -> None:
    response = distribution_context['session'].get(
        f'{Config.backend_url}/report/earnings/trend',
        headers=distribution_context['agent_headers'],
    )
    payload = assert_json_response(response)
    assert isinstance(payload['data'], list)


@pytest.mark.integration
def test_agent_sub_agents_route_returns_list(distribution_context: DistributionContext) -> None:
    response = distribution_context['session'].get(
        f'{Config.backend_url}/report/sub-agents',
        headers=distribution_context['agent_headers'],
    )
    payload = assert_json_response(response)
    assert isinstance(payload['data'], list)


@pytest.mark.integration
def test_l1_agent_direct_agents_contains_expected_l2_agents(distribution_context: DistributionContext) -> None:
    response = distribution_context['session'].get(
        f'{Config.backend_url}/agent/direct-agents',
        params={'pageNum': 1, 'pageSize': 50},
        headers=distribution_context['agent_headers'],
    )
    payload = assert_json_response(response)
    row_user_names = {row['userName'] for row in payload['rows']}
    assert set(L2_AGENT_BATCH_USERS).issubset(row_user_names), payload


@pytest.mark.integration
def test_l2_agent_direct_customers_contains_expected_members(
    distribution_context: DistributionContext,
    l2_agent_headers: dict[str, dict[str, str]],
) -> None:
    response = distribution_context['session'].get(
        f'{Config.backend_url}/agent/direct-customers',
        params={'pageNum': 1, 'pageSize': 50},
        headers=l2_agent_headers['agent_l2_demo_01'],
    )
    payload = assert_json_response(response)
    row_user_names = {row['userName'] for row in payload['rows']}
    assert set(L2A_BATCH_CUSTOMERS).issubset(row_user_names), payload


@pytest.mark.integration
def test_l2_agent_dashboard_route_returns_summary(
    distribution_context: DistributionContext,
    l2_agent_headers: dict[str, dict[str, str]],
) -> None:
    response = distribution_context['session'].get(
        f'{Config.backend_url}/report/dashboard',
        headers=l2_agent_headers['agent_l2_demo_01'],
    )
    payload = assert_json_response(response)
    assert 'totalCommission' in payload['data']
    assert 'totalBetAmount' in payload['data']


@pytest.mark.integration
def test_agent_export_earnings_returns_excel_stream(distribution_context: DistributionContext) -> None:
    response = distribution_context['session'].get(
        f'{Config.backend_url}/report/earnings/export',
        params={'pageNum': 1, 'pageSize': 20},
        headers=distribution_context['agent_headers'],
    )
    assert response.status_code == HTTP_OK, f'导出接口调用失败: {response.status_code}, body={response.text}'
    content_type = response.headers.get('Content-Type', '')
    disposition = response.headers.get('Content-Disposition', '')
    assert 'spreadsheetml.sheet' in content_type
    assert 'earnings.xlsx' in disposition
    assert len(response.content) > 0
