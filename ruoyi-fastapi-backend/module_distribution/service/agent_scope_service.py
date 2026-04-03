from sqlalchemy.ext.asyncio import AsyncSession

from module_admin.entity.vo.user_vo import CurrentUserModel
from module_distribution.dao.agent_admin_dao import AgentAdminDao
from module_distribution.entity.vo.agent_admin_vo import VisibleScopeModel


class AgentScopeService:
    """
    代理数据可见范围服务
    """

    @classmethod
    async def collect_descendant_scope(
        cls, query_db: AsyncSession, root_agent_id: int
    ) -> tuple[list[int], list[int], list[int]]:
        descendant_agent_ids: list[int] = []
        descendant_agent_user_ids: list[int] = []
        queue = [root_agent_id]
        while queue:
            current_agent_id = queue.pop(0)
            child_agents = await AgentAdminDao.get_direct_child_agents(query_db, current_agent_id)
            for child_agent in child_agents:
                descendant_agent_ids.append(child_agent.agent_id)
                descendant_agent_user_ids.append(child_agent.user_id)
                queue.append(child_agent.agent_id)
        customer_rows = await AgentAdminDao.get_customers_by_agent_ids(query_db, [root_agent_id, *descendant_agent_ids])
        customer_user_ids = [row.user_id for row in customer_rows]
        return descendant_agent_ids, descendant_agent_user_ids, customer_user_ids

    @classmethod
    async def get_visible_scope(cls, query_db: AsyncSession, current_user: CurrentUserModel) -> VisibleScopeModel:
        if current_user.user.admin:
            return VisibleScopeModel(
                is_admin=True,
                self_user_id=current_user.user.user_id,
                self_agent_id=None,
                agent_level=0,
                direct_agent_ids=[],
                visible_agent_ids=[],
                direct_customer_user_ids=[],
                visible_user_ids=[],
            )

        self_agent_id = None
        direct_agent_ids: list[int] = []
        visible_agent_ids: list[int] = []
        direct_customer_user_ids: list[int] = []
        visible_user_ids = [current_user.user.user_id]

        if current_user.user.agent_level and current_user.user.agent_level > 0:
            current_agent = await AgentAdminDao.get_agent_info_by_user_id(query_db, current_user.user.user_id)
            if current_agent:
                self_agent_id = current_agent.agent_id
                child_agents = await AgentAdminDao.get_direct_child_agents(query_db, current_agent.agent_id)
                direct_agent_ids = [row.agent_id for row in child_agents]
                visible_agent_ids = [current_agent.agent_id, *direct_agent_ids]
                customers = await AgentAdminDao.get_direct_customers(query_db, current_agent.agent_id)
                direct_customer_user_ids = [row.user_id for row in customers]
                visible_user_ids.extend([row.user_id for row in child_agents])
                visible_user_ids.extend(direct_customer_user_ids)

        return VisibleScopeModel(
            is_admin=False,
            self_user_id=current_user.user.user_id,
            self_agent_id=self_agent_id,
            agent_level=current_user.user.agent_level or 0,
            direct_agent_ids=direct_agent_ids,
            visible_agent_ids=list(dict.fromkeys(visible_agent_ids)),
            direct_customer_user_ids=direct_customer_user_ids,
            visible_user_ids=list(dict.fromkeys(visible_user_ids)),
        )
