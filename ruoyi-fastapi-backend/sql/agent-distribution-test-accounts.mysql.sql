-- 代理分销测试账号初始化脚本（MySQL）
-- 依赖：请先执行 agent-distribution-init.mysql.sql
-- 默认密码：admin123
-- 账号规模：4 个代理账号 + 16 个客户账号，共 20 个测试账号

SET @pwd_hash = '$2a$10$7JB720yubVSZvUI0rEqK/.VqGOZTH.ulu33dHOiBE8ByOhJIrdAu2';
SET @default_dept_id = 103;
SET @role_l1_id = (SELECT role_id FROM sys_role WHERE role_key = 'agent_l1' LIMIT 1);
SET @role_l2_id = (SELECT role_id FROM sys_role WHERE role_key = 'agent_l2' LIMIT 1);
SET @role_l3_id = (SELECT role_id FROM sys_role WHERE role_key = 'agent_l3' LIMIT 1);
SET @role_customer_id = (SELECT role_id FROM sys_role WHERE role_key = 'customer' LIMIT 1);

-- ----------------------------
-- 1、总代理账号
-- ----------------------------
INSERT INTO sys_user (
  dept_id, user_name, nick_name, user_type, email, phonenumber, sex, avatar, password,
  status, del_flag, login_ip, login_date, pwd_update_date, create_by, create_time, update_by, update_time,
  remark, agent_level, belong_agent_id, can_create_sub_agent
)
SELECT
  @default_dept_id, 'agent_l1_demo_01', '总代理01', '00', 'agent_l1_demo_01@example.com', '13900000001', '1', '', @pwd_hash,
  '0', '0', '', NULL, NOW(), 'system', NOW(), 'system', NOW(),
  '分销测试总代理账号', 1, NULL, 1
WHERE NOT EXISTS (SELECT 1 FROM sys_user WHERE user_name = 'agent_l1_demo_01');

INSERT INTO agent_info (
  user_id, parent_agent_id, agent_code, agent_level, bet_commission_rate, can_create_sub, status, remark, create_time, update_time
)
SELECT
  su.user_id, NULL, 'AGL1DEMO01', 1, 0.0250, 1, '0', '分销测试总代理账号', NOW(), NOW()
FROM sys_user su
WHERE su.user_name = 'agent_l1_demo_01'
AND NOT EXISTS (SELECT 1 FROM agent_info ai WHERE ai.agent_code = 'AGL1DEMO01');

INSERT INTO sys_user_role (user_id, role_id)
SELECT su.user_id, @role_l1_id
FROM sys_user su
WHERE su.user_name = 'agent_l1_demo_01'
AND @role_l1_id IS NOT NULL
AND NOT EXISTS (
  SELECT 1 FROM sys_user_role ur WHERE ur.user_id = su.user_id AND ur.role_id = @role_l1_id
);

-- ----------------------------
-- 2、二级和三级代理账号
-- ----------------------------
INSERT INTO sys_user (
  dept_id, user_name, nick_name, user_type, email, phonenumber, sex, avatar, password,
  status, del_flag, login_ip, login_date, pwd_update_date, create_by, create_time, update_by, update_time,
  remark, agent_level, belong_agent_id, can_create_sub_agent
)
SELECT
  @default_dept_id, 'agent_l2_demo_01', '高级代理01', '00', 'agent_l2_demo_01@example.com', '13900000002', '1', '', @pwd_hash,
  '0', '0', '', NULL, NOW(), 'system', NOW(), 'system', NOW(),
  '分销测试高级代理账号', 2, (SELECT agent_id FROM agent_info WHERE agent_code = 'AGL1DEMO01' LIMIT 1), 1
WHERE NOT EXISTS (SELECT 1 FROM sys_user WHERE user_name = 'agent_l2_demo_01');

INSERT INTO sys_user (
  dept_id, user_name, nick_name, user_type, email, phonenumber, sex, avatar, password,
  status, del_flag, login_ip, login_date, pwd_update_date, create_by, create_time, update_by, update_time,
  remark, agent_level, belong_agent_id, can_create_sub_agent
)
SELECT
  @default_dept_id, 'agent_l2_demo_02', '高级代理02', '00', 'agent_l2_demo_02@example.com', '13900000003', '1', '', @pwd_hash,
  '0', '0', '', NULL, NOW(), 'system', NOW(), 'system', NOW(),
  '分销测试高级代理账号', 2, (SELECT agent_id FROM agent_info WHERE agent_code = 'AGL1DEMO01' LIMIT 1), 0
WHERE NOT EXISTS (SELECT 1 FROM sys_user WHERE user_name = 'agent_l2_demo_02');

INSERT INTO agent_info (
  user_id, parent_agent_id, agent_code, agent_level, bet_commission_rate, can_create_sub, status, remark, create_time, update_time
)
SELECT
  su.user_id, (SELECT agent_id FROM agent_info WHERE agent_code = 'AGL1DEMO01' LIMIT 1), 'AGL2DEMO01', 2, 0.0200, 1, '0',
  '分销测试高级代理账号', NOW(), NOW()
FROM sys_user su
WHERE su.user_name = 'agent_l2_demo_01'
AND NOT EXISTS (SELECT 1 FROM agent_info ai WHERE ai.agent_code = 'AGL2DEMO01');

INSERT INTO agent_info (
  user_id, parent_agent_id, agent_code, agent_level, bet_commission_rate, can_create_sub, status, remark, create_time, update_time
)
SELECT
  su.user_id, (SELECT agent_id FROM agent_info WHERE agent_code = 'AGL1DEMO01' LIMIT 1), 'AGL2DEMO02', 2, 0.0200, 0, '0',
  '分销测试高级代理账号', NOW(), NOW()
FROM sys_user su
WHERE su.user_name = 'agent_l2_demo_02'
AND NOT EXISTS (SELECT 1 FROM agent_info ai WHERE ai.agent_code = 'AGL2DEMO02');

INSERT INTO sys_user_role (user_id, role_id)
SELECT su.user_id, @role_l2_id
FROM sys_user su
WHERE su.user_name IN ('agent_l2_demo_01', 'agent_l2_demo_02')
AND @role_l2_id IS NOT NULL
AND NOT EXISTS (
  SELECT 1 FROM sys_user_role ur WHERE ur.user_id = su.user_id AND ur.role_id = @role_l2_id
);

INSERT INTO sys_user (
  dept_id, user_name, nick_name, user_type, email, phonenumber, sex, avatar, password,
  status, del_flag, login_ip, login_date, pwd_update_date, create_by, create_time, update_by, update_time,
  remark, agent_level, belong_agent_id, can_create_sub_agent
)
SELECT
  @default_dept_id, 'agent_l3_demo_01', '中级代理01', '00', 'agent_l3_demo_01@example.com', '13900000004', '1', '', @pwd_hash,
  '0', '0', '', NULL, NOW(), 'system', NOW(), 'system', NOW(),
  '分销测试中级代理账号', 3, (SELECT agent_id FROM agent_info WHERE agent_code = 'AGL2DEMO01' LIMIT 1), 0
WHERE NOT EXISTS (SELECT 1 FROM sys_user WHERE user_name = 'agent_l3_demo_01');

INSERT INTO agent_info (
  user_id, parent_agent_id, agent_code, agent_level, bet_commission_rate, can_create_sub, status, remark, create_time, update_time
)
SELECT
  su.user_id, (SELECT agent_id FROM agent_info WHERE agent_code = 'AGL2DEMO01' LIMIT 1), 'AGL3DEMO01', 3, 0.0150, 0, '0',
  '分销测试中级代理账号', NOW(), NOW()
FROM sys_user su
WHERE su.user_name = 'agent_l3_demo_01'
AND NOT EXISTS (SELECT 1 FROM agent_info ai WHERE ai.agent_code = 'AGL3DEMO01');

INSERT INTO sys_user_role (user_id, role_id)
SELECT su.user_id, @role_l3_id
FROM sys_user su
WHERE su.user_name = 'agent_l3_demo_01'
AND @role_l3_id IS NOT NULL
AND NOT EXISTS (
  SELECT 1 FROM sys_user_role ur WHERE ur.user_id = su.user_id AND ur.role_id = @role_l3_id
);

-- ----------------------------
-- 3、直属于总代理的 8 个客户账号
-- ----------------------------
INSERT INTO sys_user (
  dept_id, user_name, nick_name, user_type, email, phonenumber, sex, avatar, password,
  status, del_flag, login_ip, login_date, pwd_update_date, create_by, create_time, update_by, update_time,
  remark, agent_level, belong_agent_id, can_create_sub_agent
)
SELECT
  @default_dept_id, account.user_name, account.nick_name, '00', account.email, account.phonenumber, '1', '', @pwd_hash,
  '0', '0', '', NULL, NOW(), 'system', NOW(), 'system', NOW(),
  '分销测试客户账号-L1', 0, (SELECT agent_id FROM agent_info WHERE agent_code = 'AGL1DEMO01' LIMIT 1), 0
FROM (
  SELECT 'customer_l1_demo_01' AS user_name, 'L1客户01' AS nick_name, 'customer_l1_demo_01@example.com' AS email, '13900000101' AS phonenumber
  UNION ALL SELECT 'customer_l1_demo_02', 'L1客户02', 'customer_l1_demo_02@example.com', '13900000102'
  UNION ALL SELECT 'customer_l1_demo_03', 'L1客户03', 'customer_l1_demo_03@example.com', '13900000103'
  UNION ALL SELECT 'customer_l1_demo_04', 'L1客户04', 'customer_l1_demo_04@example.com', '13900000104'
  UNION ALL SELECT 'customer_l1_demo_05', 'L1客户05', 'customer_l1_demo_05@example.com', '13900000105'
  UNION ALL SELECT 'customer_l1_demo_06', 'L1客户06', 'customer_l1_demo_06@example.com', '13900000106'
  UNION ALL SELECT 'customer_l1_demo_07', 'L1客户07', 'customer_l1_demo_07@example.com', '13900000107'
  UNION ALL SELECT 'customer_l1_demo_08', 'L1客户08', 'customer_l1_demo_08@example.com', '13900000108'
) account
WHERE NOT EXISTS (SELECT 1 FROM sys_user su WHERE su.user_name = account.user_name);

-- ----------------------------
-- 4、直属于高级代理01的 4 个客户账号
-- ----------------------------
INSERT INTO sys_user (
  dept_id, user_name, nick_name, user_type, email, phonenumber, sex, avatar, password,
  status, del_flag, login_ip, login_date, pwd_update_date, create_by, create_time, update_by, update_time,
  remark, agent_level, belong_agent_id, can_create_sub_agent
)
SELECT
  @default_dept_id, account.user_name, account.nick_name, '00', account.email, account.phonenumber, '1', '', @pwd_hash,
  '0', '0', '', NULL, NOW(), 'system', NOW(), 'system', NOW(),
  '分销测试客户账号-L2A', 0, (SELECT agent_id FROM agent_info WHERE agent_code = 'AGL2DEMO01' LIMIT 1), 0
FROM (
  SELECT 'customer_l2a_demo_01' AS user_name, 'L2A客户01' AS nick_name, 'customer_l2a_demo_01@example.com' AS email, '13900000201' AS phonenumber
  UNION ALL SELECT 'customer_l2a_demo_02', 'L2A客户02', 'customer_l2a_demo_02@example.com', '13900000202'
  UNION ALL SELECT 'customer_l2a_demo_03', 'L2A客户03', 'customer_l2a_demo_03@example.com', '13900000203'
  UNION ALL SELECT 'customer_l2a_demo_04', 'L2A客户04', 'customer_l2a_demo_04@example.com', '13900000204'
) account
WHERE NOT EXISTS (SELECT 1 FROM sys_user su WHERE su.user_name = account.user_name);

-- ----------------------------
-- 5、直属于高级代理02的 4 个客户账号
-- ----------------------------
INSERT INTO sys_user (
  dept_id, user_name, nick_name, user_type, email, phonenumber, sex, avatar, password,
  status, del_flag, login_ip, login_date, pwd_update_date, create_by, create_time, update_by, update_time,
  remark, agent_level, belong_agent_id, can_create_sub_agent
)
SELECT
  @default_dept_id, account.user_name, account.nick_name, '00', account.email, account.phonenumber, '1', '', @pwd_hash,
  '0', '0', '', NULL, NOW(), 'system', NOW(), 'system', NOW(),
  '分销测试客户账号-L2B', 0, (SELECT agent_id FROM agent_info WHERE agent_code = 'AGL2DEMO02' LIMIT 1), 0
FROM (
  SELECT 'customer_l2b_demo_01' AS user_name, 'L2B客户01' AS nick_name, 'customer_l2b_demo_01@example.com' AS email, '13900000301' AS phonenumber
  UNION ALL SELECT 'customer_l2b_demo_02', 'L2B客户02', 'customer_l2b_demo_02@example.com', '13900000302'
  UNION ALL SELECT 'customer_l2b_demo_03', 'L2B客户03', 'customer_l2b_demo_03@example.com', '13900000303'
  UNION ALL SELECT 'customer_l2b_demo_04', 'L2B客户04', 'customer_l2b_demo_04@example.com', '13900000304'
) account
WHERE NOT EXISTS (SELECT 1 FROM sys_user su WHERE su.user_name = account.user_name);

-- ----------------------------
-- 6、为全部客户绑定 customer 角色
-- ----------------------------
INSERT INTO sys_user_role (user_id, role_id)
SELECT su.user_id, @role_customer_id
FROM sys_user su
WHERE su.user_name IN (
  'customer_l1_demo_01', 'customer_l1_demo_02', 'customer_l1_demo_03', 'customer_l1_demo_04',
  'customer_l1_demo_05', 'customer_l1_demo_06', 'customer_l1_demo_07', 'customer_l1_demo_08',
  'customer_l2a_demo_01', 'customer_l2a_demo_02', 'customer_l2a_demo_03', 'customer_l2a_demo_04',
  'customer_l2b_demo_01', 'customer_l2b_demo_02', 'customer_l2b_demo_03', 'customer_l2b_demo_04'
)
AND @role_customer_id IS NOT NULL
AND NOT EXISTS (
  SELECT 1 FROM sys_user_role ur WHERE ur.user_id = su.user_id AND ur.role_id = @role_customer_id
);

-- ----------------------------
-- 7、推荐给集成测试使用的账号
-- agent:    agent_l1_demo_01 / admin123
-- customer: customer_l1_demo_01 / admin123
-- ----------------------------
UPDATE `sys_config`
SET `config_value` = 'false', `update_by` = 'system', `update_time` = NOW()
WHERE `config_key` = 'sys.account.captchaEnabled';
