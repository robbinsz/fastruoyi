# Agent Distribution Design

## Domain Model
- `sys_user` 增加 `agent_level`、`belong_agent_id`、`can_create_sub_agent`，用于快速表达用户代理身份和直属归属。
- `agent_info` 存代理独有属性，如 `agent_code`、`bet_commission_rate`、`can_create_sub`。
- `bet_link`、`bet_record`、`user_earnings`、`agent_earnings`、`commission_config` 作为独立业务表，后续围绕它们实现投注与结算闭环。

## Service Boundaries
- `agent_admin_service` 负责超管分配 L1、授权/撤销创建次级权限、代理树查询。
- `agent_scope_service` 负责把当前登录用户映射为可见范围，供后续代理列表、客户列表、报表、投注查询复用。
- 投注和收益计算后续独立为 `bet_*` 与 `earnings_*` 服务，不和基础代理管理耦合。

## Delivery Strategy
1. Phase A: 数据结构、模型、初始化 SQL、超管基础 API。
2. Phase B: 代理/客户创建与可见范围查询。
3. Phase C: 投注链接、投注确认、结果确认、收益引擎。
4. Phase D: 报表接口与前端页面。
