import pytest
from playwright.async_api import async_playwright

from common.base_page_test import BasePageTest
from common.config import Config


class DistributionPageTest(BasePageTest):
    """代理分销页面基础测试"""

    async def test_assign_agent_page(self) -> None:
        await self.goto_page(Config.frontend_url + '/admin-agent/assign')
        await self.page.wait_for_timeout(1500)
        assert await self.page.get_by_text('分配总代理').count() > 0

    async def test_agent_tree_page(self) -> None:
        await self.goto_page(Config.frontend_url + '/admin-agent/tree')
        await self.page.wait_for_timeout(1500)
        assert await self.page.get_by_text('代理树管理').count() > 0

    async def test_agent_list_page(self) -> None:
        await self.goto_page(Config.frontend_url + '/agent/list')
        await self.page.wait_for_timeout(1500)
        assert await self.page.get_by_text('直属代理').count() > 0

    async def test_bet_manage_page(self) -> None:
        await self.goto_page(Config.frontend_url + '/bet/link-manage')
        await self.page.wait_for_timeout(1500)
        assert await self.page.get_by_text('创建链接').count() > 0

    async def test_report_dashboard_page(self) -> None:
        await self.goto_page(Config.frontend_url + '/report/dashboard')
        await self.page.wait_for_timeout(1500)
        assert await self.page.get_by_text('收益明细').count() > 0


@pytest.mark.asyncio
async def test_distribution_pages() -> None:
    async with async_playwright() as p:
        test_instance = DistributionPageTest()
        await test_instance.setup(p)
        try:
            await test_instance.test_assign_agent_page()
            await test_instance.test_agent_tree_page()
            await test_instance.test_agent_list_page()
            await test_instance.test_bet_manage_page()
            await test_instance.test_report_dashboard_page()
        finally:
            await test_instance.teardown()
