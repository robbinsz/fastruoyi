-- 代理分销系统初始化脚本（MySQL）
-- 执行前请先在测试环境验证，并根据现网 menu_id / role_id 实际情况复核。

SET @current_db = DATABASE();

SET @stmt = IF(
  EXISTS (
    SELECT 1
    FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = @current_db
      AND TABLE_NAME = 'sys_user'
      AND COLUMN_NAME = 'agent_level'
  ),
  'SELECT 1',
  "ALTER TABLE `sys_user` ADD COLUMN `agent_level` TINYINT DEFAULT 0 COMMENT '代理层级：0=客户/普通用户 1=总代理 2=高级代理 3=中级代理 4=初级代理'"
);
PREPARE stmt FROM @stmt;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @stmt = IF(
  EXISTS (
    SELECT 1
    FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = @current_db
      AND TABLE_NAME = 'sys_user'
      AND COLUMN_NAME = 'belong_agent_id'
  ),
  'SELECT 1',
  "ALTER TABLE `sys_user` ADD COLUMN `belong_agent_id` BIGINT DEFAULT NULL COMMENT '归属代理商agent_id，顶级代理和超管为空'"
);
PREPARE stmt FROM @stmt;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @stmt = IF(
  EXISTS (
    SELECT 1
    FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = @current_db
      AND TABLE_NAME = 'sys_user'
      AND COLUMN_NAME = 'can_create_sub_agent'
  ),
  'SELECT 1',
  "ALTER TABLE `sys_user` ADD COLUMN `can_create_sub_agent` TINYINT DEFAULT 0 COMMENT '是否可创建次级代理：0=否 1=是'"
);
PREPARE stmt FROM @stmt;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

CREATE TABLE IF NOT EXISTS `agent_info` (
  `agent_id` BIGINT NOT NULL AUTO_INCREMENT,
  `user_id` BIGINT NOT NULL,
  `parent_agent_id` BIGINT DEFAULT NULL,
  `agent_code` VARCHAR(50) NOT NULL,
  `agent_level` TINYINT NOT NULL DEFAULT 1,
  `bet_commission_rate` DECIMAL(5, 4) NOT NULL DEFAULT 0.0250,
  `can_create_sub` TINYINT NOT NULL DEFAULT 0,
  `status` CHAR(1) NOT NULL DEFAULT '0',
  `remark` VARCHAR(500) DEFAULT NULL,
  `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`agent_id`),
  UNIQUE KEY `uk_agent_user_id` (`user_id`),
  UNIQUE KEY `uk_agent_code` (`agent_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='代理商扩展信息表';

CREATE TABLE IF NOT EXISTS `bet_link` (
  `link_id` BIGINT NOT NULL AUTO_INCREMENT,
  `link_token` VARCHAR(64) NOT NULL,
  `agent_id` BIGINT NOT NULL,
  `link_name` VARCHAR(100) DEFAULT NULL,
  `bet_desc` TEXT DEFAULT NULL,
  `odds` DECIMAL(6, 2) DEFAULT NULL,
  `expire_at` DATETIME NOT NULL,
  `max_users` INT DEFAULT NULL,
  `status` TINYINT NOT NULL DEFAULT 0,
  `confirm_result` TINYINT DEFAULT NULL,
  `confirm_time` DATETIME DEFAULT NULL,
  `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `remark` VARCHAR(500) DEFAULT NULL,
  PRIMARY KEY (`link_id`),
  UNIQUE KEY `uk_link_token` (`link_token`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='投注链接表';

SET @stmt = IF(
  EXISTS (
    SELECT 1
    FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = @current_db
      AND TABLE_NAME = 'bet_link'
      AND COLUMN_NAME = 'remark'
  ),
  'SELECT 1',
  "ALTER TABLE `bet_link` ADD COLUMN `remark` VARCHAR(500) DEFAULT NULL AFTER `create_time`"
);
PREPARE stmt FROM @stmt;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

CREATE TABLE IF NOT EXISTS `bet_record` (
  `record_id` BIGINT NOT NULL AUTO_INCREMENT,
  `link_id` BIGINT NOT NULL,
  `user_id` BIGINT NOT NULL,
  `belong_agent_id` BIGINT NOT NULL,
  `bet_amount` DECIMAL(12, 2) NOT NULL,
  `odds` DECIMAL(6, 2) NOT NULL,
  `is_confirmed` TINYINT NOT NULL DEFAULT 0,
  `confirm_time` DATETIME DEFAULT NULL,
  `is_win` TINYINT DEFAULT NULL,
  `win_amount` DECIMAL(12, 2) NOT NULL DEFAULT 0,
  `round_profit` DECIMAL(12, 2) NOT NULL DEFAULT 0,
  `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`record_id`),
  UNIQUE KEY `uk_link_user` (`link_id`, `user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='投注记录表';

CREATE TABLE IF NOT EXISTS `user_earnings` (
  `earning_id` BIGINT NOT NULL AUTO_INCREMENT,
  `user_id` BIGINT NOT NULL,
  `belong_agent_id` BIGINT NOT NULL,
  `link_id` BIGINT NOT NULL,
  `bet_amount` DECIMAL(12, 2) NOT NULL DEFAULT 0,
  `win_amount` DECIMAL(12, 2) NOT NULL DEFAULT 0,
  `profit` DECIMAL(12, 2) NOT NULL DEFAULT 0,
  `confirm_time` DATETIME DEFAULT NULL,
  `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`earning_id`),
  UNIQUE KEY `uk_user_link` (`user_id`, `link_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户收益快照表';

CREATE TABLE IF NOT EXISTS `agent_earnings` (
  `earning_id` BIGINT NOT NULL AUTO_INCREMENT,
  `agent_id` BIGINT NOT NULL,
  `source_user_id` BIGINT NOT NULL,
  `link_id` BIGINT NOT NULL,
  `total_bet_amt` DECIMAL(12, 2) NOT NULL DEFAULT 0,
  `user_profit` DECIMAL(12, 2) NOT NULL DEFAULT 0,
  `earn_type` VARCHAR(20) NOT NULL,
  `bet_commission` DECIMAL(12, 2) NOT NULL DEFAULT 0,
  `profit_commission` DECIMAL(12, 2) NOT NULL DEFAULT 0,
  `total_commission` DECIMAL(12, 2) NOT NULL DEFAULT 0,
  `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`earning_id`),
  UNIQUE KEY `uk_agent_user_link` (`agent_id`, `source_user_id`, `link_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='代理收益记录表';

CREATE TABLE IF NOT EXISTS `commission_config` (
  `config_id` BIGINT NOT NULL AUTO_INCREMENT,
  `agent_id` BIGINT DEFAULT NULL,
  `profit_min` DECIMAL(12, 2) NOT NULL,
  `profit_max` DECIMAL(12, 2) NOT NULL,
  `commission_amt` DECIMAL(12, 2) NOT NULL,
  `split_ratio` DECIMAL(5, 4) NOT NULL,
  `sort_order` INT NOT NULL DEFAULT 1,
  `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`config_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='梯度提成配置表';

SET @stmt = IF(
  EXISTS (
    SELECT 1
    FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = @current_db
      AND TABLE_NAME = 'commission_config'
      AND COLUMN_NAME = 'min_profit'
  ),
  "ALTER TABLE `commission_config` CHANGE COLUMN `min_profit` `profit_min` DECIMAL(12, 2) NOT NULL",
  'SELECT 1'
);
PREPARE stmt FROM @stmt;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @stmt = IF(
  EXISTS (
    SELECT 1
    FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = @current_db
      AND TABLE_NAME = 'commission_config'
      AND COLUMN_NAME = 'max_profit'
  ),
  "ALTER TABLE `commission_config` CHANGE COLUMN `max_profit` `profit_max` DECIMAL(12, 2) NOT NULL",
  'SELECT 1'
);
PREPARE stmt FROM @stmt;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @stmt = IF(
  EXISTS (
    SELECT 1
    FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = @current_db
      AND TABLE_NAME = 'commission_config'
      AND COLUMN_NAME = 'commission_amt'
  ),
  'SELECT 1',
  "ALTER TABLE `commission_config` ADD COLUMN `commission_amt` DECIMAL(12, 2) NOT NULL DEFAULT 0 AFTER `profit_max`"
);
PREPARE stmt FROM @stmt;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @stmt = IF(
  EXISTS (
    SELECT 1
    FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = @current_db
      AND TABLE_NAME = 'commission_config'
      AND COLUMN_NAME = 'sort_order'
  ),
  'SELECT 1',
  "ALTER TABLE `commission_config` ADD COLUMN `sort_order` INT NOT NULL DEFAULT 1 AFTER `split_ratio`"
);
PREPARE stmt FROM @stmt;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @stmt = IF(
  EXISTS (
    SELECT 1
    FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = @current_db
      AND TABLE_NAME = 'commission_config'
      AND COLUMN_NAME = 'update_time'
  ),
  'SELECT 1',
  "ALTER TABLE `commission_config` ADD COLUMN `update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP AFTER `create_time`"
);
PREPARE stmt FROM @stmt;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

INSERT INTO `sys_role` (`role_name`, `role_key`, `role_sort`, `data_scope`, `menu_check_strictly`, `dept_check_strictly`, `status`, `create_by`, `create_time`, `remark`)
SELECT '总代理', 'agent_l1', 101, '5', 1, 1, '0', 'system', NOW(), '代理分销角色-L1'
WHERE NOT EXISTS (SELECT 1 FROM `sys_role` WHERE `role_key` = 'agent_l1');

INSERT INTO `sys_role` (`role_name`, `role_key`, `role_sort`, `data_scope`, `menu_check_strictly`, `dept_check_strictly`, `status`, `create_by`, `create_time`, `remark`)
SELECT '高级代理', 'agent_l2', 102, '5', 1, 1, '0', 'system', NOW(), '代理分销角色-L2'
WHERE NOT EXISTS (SELECT 1 FROM `sys_role` WHERE `role_key` = 'agent_l2');

INSERT INTO `sys_role` (`role_name`, `role_key`, `role_sort`, `data_scope`, `menu_check_strictly`, `dept_check_strictly`, `status`, `create_by`, `create_time`, `remark`)
SELECT '中级代理', 'agent_l3', 103, '5', 1, 1, '0', 'system', NOW(), '代理分销角色-L3'
WHERE NOT EXISTS (SELECT 1 FROM `sys_role` WHERE `role_key` = 'agent_l3');

INSERT INTO `sys_role` (`role_name`, `role_key`, `role_sort`, `data_scope`, `menu_check_strictly`, `dept_check_strictly`, `status`, `create_by`, `create_time`, `remark`)
SELECT '初级代理', 'agent_l4', 104, '5', 1, 1, '0', 'system', NOW(), '代理分销角色-L4'
WHERE NOT EXISTS (SELECT 1 FROM `sys_role` WHERE `role_key` = 'agent_l4');

INSERT INTO `sys_role` (`role_name`, `role_key`, `role_sort`, `data_scope`, `menu_check_strictly`, `dept_check_strictly`, `status`, `create_by`, `create_time`, `remark`)
SELECT '普通客户', 'customer', 105, '5', 1, 1, '0', 'system', NOW(), '代理分销角色-customer'
WHERE NOT EXISTS (SELECT 1 FROM `sys_role` WHERE `role_key` = 'customer');

INSERT INTO `commission_config` (`agent_id`, `profit_min`, `profit_max`, `commission_amt`, `split_ratio`, `sort_order`)
SELECT NULL, 100.00, 1500.00, 100.00, 0.5000, 1
WHERE NOT EXISTS (
  SELECT 1 FROM `commission_config` WHERE `agent_id` IS NULL AND `profit_min` = 100.00 AND `profit_max` = 1500.00
);

INSERT INTO `commission_config` (`agent_id`, `profit_min`, `profit_max`, `commission_amt`, `split_ratio`, `sort_order`)
SELECT NULL, 1500.01, 2500.00, 200.00, 0.5000, 2
WHERE NOT EXISTS (
  SELECT 1 FROM `commission_config` WHERE `agent_id` IS NULL AND `profit_min` = 1500.01 AND `profit_max` = 2500.00
);

INSERT INTO `commission_config` (`agent_id`, `profit_min`, `profit_max`, `commission_amt`, `split_ratio`, `sort_order`)
SELECT NULL, 2500.01, 3500.00, 300.00, 0.5000, 3
WHERE NOT EXISTS (
  SELECT 1 FROM `commission_config` WHERE `agent_id` IS NULL AND `profit_min` = 2500.01
);

INSERT INTO `sys_menu` (`menu_name`, `parent_id`, `order_num`, `path`, `component`, `menu_type`, `visible`, `status`, `perms`, `icon`, `create_by`, `create_time`, `remark`)
SELECT '系统管理（代理）', 0, 5, 'admin-agent', NULL, 'M', '0', '0', '', 'people', 'system', NOW(), '代理分销超管目录'
WHERE NOT EXISTS (SELECT 1 FROM `sys_menu` WHERE `path` = 'admin-agent');

INSERT INTO `sys_menu` (`menu_name`, `parent_id`, `order_num`, `path`, `component`, `menu_type`, `visible`, `status`, `perms`, `icon`, `create_by`, `create_time`, `remark`)
SELECT '代理管理', 0, 10, 'agent', NULL, 'M', '0', '0', '', 'tree-table', 'system', NOW(), '代理分销目录'
WHERE NOT EXISTS (SELECT 1 FROM `sys_menu` WHERE `path` = 'agent');

INSERT INTO `sys_menu` (`menu_name`, `parent_id`, `order_num`, `path`, `component`, `menu_type`, `visible`, `status`, `perms`, `icon`, `create_by`, `create_time`, `remark`)
SELECT '投注管理', 0, 20, 'bet', NULL, 'M', '0', '0', '', 'link', 'system', NOW(), '投注管理目录'
WHERE NOT EXISTS (SELECT 1 FROM `sys_menu` WHERE `path` = 'bet');

INSERT INTO `sys_menu` (`menu_name`, `parent_id`, `order_num`, `path`, `component`, `menu_type`, `visible`, `status`, `perms`, `icon`, `create_by`, `create_time`, `remark`)
SELECT '收益报表', 0, 30, 'report', NULL, 'M', '0', '0', '', 'chart', 'system', NOW(), '收益报表目录'
WHERE NOT EXISTS (SELECT 1 FROM `sys_menu` WHERE `path` = 'report');

SET @admin_agent_menu_id = (SELECT `menu_id` FROM `sys_menu` WHERE `path` = 'admin-agent' LIMIT 1);
SET @agent_menu_id = (SELECT `menu_id` FROM `sys_menu` WHERE `path` = 'agent' LIMIT 1);
SET @bet_menu_id = (SELECT `menu_id` FROM `sys_menu` WHERE `path` = 'bet' LIMIT 1);
SET @report_menu_id = (SELECT `menu_id` FROM `sys_menu` WHERE `path` = 'report' LIMIT 1);
SET @role_l1_id = (SELECT `role_id` FROM `sys_role` WHERE `role_key` = 'agent_l1' LIMIT 1);
SET @role_l2_id = (SELECT `role_id` FROM `sys_role` WHERE `role_key` = 'agent_l2' LIMIT 1);
SET @role_l3_id = (SELECT `role_id` FROM `sys_role` WHERE `role_key` = 'agent_l3' LIMIT 1);
SET @role_l4_id = (SELECT `role_id` FROM `sys_role` WHERE `role_key` = 'agent_l4' LIMIT 1);
SET @role_customer_id = (SELECT `role_id` FROM `sys_role` WHERE `role_key` = 'customer' LIMIT 1);
SET @role_admin_id = (SELECT `role_id` FROM `sys_role` WHERE `role_key` = 'admin' LIMIT 1);

INSERT INTO `sys_menu` (`menu_name`, `parent_id`, `order_num`, `path`, `component`, `menu_type`, `visible`, `status`, `perms`, `icon`, `create_by`, `create_time`, `remark`)
SELECT '分配总代理', @admin_agent_menu_id, 1, 'assign', 'admin/assign-agent', 'C', '0', '0', 'admin:assign:agent', '#', 'system', NOW(), '分配总代理'
WHERE NOT EXISTS (SELECT 1 FROM `sys_menu` WHERE `perms` = 'admin:assign:agent');

INSERT INTO `sys_menu` (`menu_name`, `parent_id`, `order_num`, `path`, `component`, `menu_type`, `visible`, `status`, `perms`, `icon`, `create_by`, `create_time`, `remark`)
SELECT '代理树管理', @admin_agent_menu_id, 2, 'tree', 'admin/agent-tree', 'C', '0', '0', 'admin:agent:tree', '#', 'system', NOW(), '代理树管理'
WHERE NOT EXISTS (SELECT 1 FROM `sys_menu` WHERE `perms` = 'admin:agent:tree');

INSERT INTO `sys_menu` (`menu_name`, `parent_id`, `order_num`, `path`, `component`, `menu_type`, `visible`, `status`, `perms`, `icon`, `create_by`, `create_time`, `remark`)
SELECT '代理授权', @admin_agent_menu_id, 3, 'grant', 'admin/agent-tree', 'F', '0', '0', 'admin:agent:grant', '#', 'system', NOW(), '授权和撤销次级代理权限'
WHERE NOT EXISTS (SELECT 1 FROM `sys_menu` WHERE `perms` = 'admin:agent:grant');

INSERT INTO `sys_menu` (`menu_name`, `parent_id`, `order_num`, `path`, `component`, `menu_type`, `visible`, `status`, `perms`, `icon`, `create_by`, `create_time`, `remark`)
SELECT '代理编辑', @admin_agent_menu_id, 4, 'edit', 'admin/agent-tree', 'F', '0', '0', 'admin:agent:edit', '#', 'system', NOW(), '代理启停、详情与提成系数维护'
WHERE NOT EXISTS (SELECT 1 FROM `sys_menu` WHERE `perms` = 'admin:agent:edit');

INSERT INTO `sys_menu` (`menu_name`, `parent_id`, `order_num`, `path`, `component`, `menu_type`, `visible`, `status`, `perms`, `icon`, `create_by`, `create_time`, `remark`)
SELECT '代理商列表', @agent_menu_id, 1, 'list', 'agent/list', 'C', '0', '0', 'agent:list', '#', 'system', NOW(), '直属代理和客户列表'
WHERE NOT EXISTS (SELECT 1 FROM `sys_menu` WHERE `perms` = 'agent:list');

INSERT INTO `sys_menu` (`menu_name`, `parent_id`, `order_num`, `path`, `component`, `menu_type`, `visible`, `status`, `perms`, `icon`, `create_by`, `create_time`, `remark`)
SELECT '创建下级代理', @agent_menu_id, 2, 'create-sub', 'agent/create-sub', 'C', '0', '0', 'agent:create:sub', '#', 'system', NOW(), '创建直属下级代理'
WHERE NOT EXISTS (SELECT 1 FROM `sys_menu` WHERE `perms` = 'agent:create:sub');

INSERT INTO `sys_menu` (`menu_name`, `parent_id`, `order_num`, `path`, `component`, `menu_type`, `visible`, `status`, `perms`, `icon`, `create_by`, `create_time`, `remark`)
SELECT '客户管理', @agent_menu_id, 3, 'customer', 'agent/create-customer', 'C', '0', '0', 'agent:customer:manage', '#', 'system', NOW(), '创建直属客户'
WHERE NOT EXISTS (SELECT 1 FROM `sys_menu` WHERE `perms` = 'agent:customer:manage');

INSERT INTO `sys_menu` (`menu_name`, `parent_id`, `order_num`, `path`, `component`, `menu_type`, `visible`, `status`, `perms`, `icon`, `create_by`, `create_time`, `remark`)
SELECT '提成配置', @agent_menu_id, 4, 'commission', 'commission/config', 'C', '0', '0', 'commission:config', '#', 'system', NOW(), '代理提成梯度配置'
WHERE NOT EXISTS (SELECT 1 FROM `sys_menu` WHERE `perms` = 'commission:config');

INSERT INTO `sys_menu` (`menu_name`, `parent_id`, `order_num`, `path`, `component`, `menu_type`, `visible`, `status`, `perms`, `icon`, `create_by`, `create_time`, `remark`)
SELECT '平台默认提成', @agent_menu_id, 5, 'commission-default', 'commission/config', 'F', '0', '0', 'commission:default', '#', 'system', NOW(), '平台默认提成配置'
WHERE NOT EXISTS (SELECT 1 FROM `sys_menu` WHERE `perms` = 'commission:default');

INSERT INTO `sys_menu` (`menu_name`, `parent_id`, `order_num`, `path`, `component`, `menu_type`, `visible`, `status`, `perms`, `icon`, `create_by`, `create_time`, `remark`)
SELECT '链接管理', @bet_menu_id, 1, 'link', 'bet/link-manage', 'C', '0', '0', 'bet:link:manage', '#', 'system', NOW(), '投注链接管理'
WHERE NOT EXISTS (SELECT 1 FROM `sys_menu` WHERE `perms` = 'bet:link:manage');

INSERT INTO `sys_menu` (`menu_name`, `parent_id`, `order_num`, `path`, `component`, `menu_type`, `visible`, `status`, `perms`, `icon`, `create_by`, `create_time`, `remark`)
SELECT '我的投注', @bet_menu_id, 2, 'my-bets', 'bet/my-bets', 'C', '0', '0', 'bet:my:view', '#', 'system', NOW(), '我的投注记录'
WHERE NOT EXISTS (SELECT 1 FROM `sys_menu` WHERE `perms` = 'bet:my:view');

INSERT INTO `sys_menu` (`menu_name`, `parent_id`, `order_num`, `path`, `component`, `menu_type`, `visible`, `status`, `perms`, `icon`, `create_by`, `create_time`, `remark`)
SELECT '代理看板', @report_menu_id, 1, 'dashboard', 'report/dashboard', 'C', '0', '0', 'earnings:view', '#', 'system', NOW(), '代理收益看板'
WHERE NOT EXISTS (SELECT 1 FROM `sys_menu` WHERE `perms` = 'earnings:view');

INSERT INTO `sys_menu` (`menu_name`, `parent_id`, `order_num`, `path`, `component`, `menu_type`, `visible`, `status`, `perms`, `icon`, `create_by`, `create_time`, `remark`)
SELECT '我的收益', @report_menu_id, 2, 'my-earnings', 'report/my-earnings', 'C', '0', '0', 'earnings:my', '#', 'system', NOW(), '客户我的收益'
WHERE NOT EXISTS (SELECT 1 FROM `sys_menu` WHERE `perms` = 'earnings:my');

INSERT INTO `sys_role_menu` (`role_id`, `menu_id`)
SELECT @role_l1_id, `menu_id` FROM `sys_menu`
WHERE `path` IN ('agent', 'bet', 'report')
AND @role_l1_id IS NOT NULL
AND NOT EXISTS (
  SELECT 1 FROM `sys_role_menu` rm WHERE rm.`role_id` = @role_l1_id AND rm.`menu_id` = `sys_menu`.`menu_id`
);

INSERT INTO `sys_role_menu` (`role_id`, `menu_id`)
SELECT @role_l2_id, `menu_id` FROM `sys_menu`
WHERE `path` IN ('agent', 'bet', 'report')
AND @role_l2_id IS NOT NULL
AND NOT EXISTS (
  SELECT 1 FROM `sys_role_menu` rm WHERE rm.`role_id` = @role_l2_id AND rm.`menu_id` = `sys_menu`.`menu_id`
);

INSERT INTO `sys_role_menu` (`role_id`, `menu_id`)
SELECT @role_l3_id, `menu_id` FROM `sys_menu`
WHERE `path` IN ('agent', 'bet', 'report')
AND @role_l3_id IS NOT NULL
AND NOT EXISTS (
  SELECT 1 FROM `sys_role_menu` rm WHERE rm.`role_id` = @role_l3_id AND rm.`menu_id` = `sys_menu`.`menu_id`
);

INSERT INTO `sys_role_menu` (`role_id`, `menu_id`)
SELECT @role_l4_id, `menu_id` FROM `sys_menu`
WHERE `path` IN ('agent', 'bet', 'report')
AND @role_l4_id IS NOT NULL
AND NOT EXISTS (
  SELECT 1 FROM `sys_role_menu` rm WHERE rm.`role_id` = @role_l4_id AND rm.`menu_id` = `sys_menu`.`menu_id`
);

INSERT INTO `sys_role_menu` (`role_id`, `menu_id`)
SELECT @role_customer_id, `menu_id` FROM `sys_menu`
WHERE `path` IN ('bet', 'report')
AND @role_customer_id IS NOT NULL
AND NOT EXISTS (
  SELECT 1 FROM `sys_role_menu` rm WHERE rm.`role_id` = @role_customer_id AND rm.`menu_id` = `sys_menu`.`menu_id`
);

INSERT INTO `sys_role_menu` (`role_id`, `menu_id`)
SELECT @role_admin_id, `menu_id` FROM `sys_menu`
WHERE `path` IN ('admin-agent', 'agent', 'bet', 'report')
AND @role_admin_id IS NOT NULL
AND NOT EXISTS (
  SELECT 1 FROM `sys_role_menu` rm WHERE rm.`role_id` = @role_admin_id AND rm.`menu_id` = `sys_menu`.`menu_id`
);

INSERT INTO `sys_role_menu` (`role_id`, `menu_id`)
SELECT @role_admin_id, `menu_id` FROM `sys_menu`
WHERE `perms` IN (
  'admin:assign:agent',
  'admin:agent:tree',
  'admin:agent:grant',
  'admin:agent:edit',
  'agent:list',
  'agent:create:sub',
  'agent:customer:manage',
  'commission:config',
  'commission:default',
  'bet:link:manage',
  'bet:my:view',
  'earnings:view',
  'earnings:my'
)
AND @role_admin_id IS NOT NULL
AND NOT EXISTS (
  SELECT 1 FROM `sys_role_menu` rm WHERE rm.`role_id` = @role_admin_id AND rm.`menu_id` = `sys_menu`.`menu_id`
);

INSERT INTO `sys_role_menu` (`role_id`, `menu_id`)
SELECT @role_l1_id, `menu_id` FROM `sys_menu`
WHERE `perms` IN ('agent:list', 'agent:create:sub', 'agent:customer:manage', 'commission:config')
AND @role_l1_id IS NOT NULL
AND NOT EXISTS (
  SELECT 1 FROM `sys_role_menu` rm WHERE rm.`role_id` = @role_l1_id AND rm.`menu_id` = `sys_menu`.`menu_id`
);

INSERT INTO `sys_role_menu` (`role_id`, `menu_id`)
SELECT @role_l2_id, `menu_id` FROM `sys_menu`
WHERE `perms` IN ('agent:list', 'agent:create:sub', 'agent:customer:manage', 'commission:config')
AND @role_l2_id IS NOT NULL
AND NOT EXISTS (
  SELECT 1 FROM `sys_role_menu` rm WHERE rm.`role_id` = @role_l2_id AND rm.`menu_id` = `sys_menu`.`menu_id`
);

INSERT INTO `sys_role_menu` (`role_id`, `menu_id`)
SELECT @role_l3_id, `menu_id` FROM `sys_menu`
WHERE `perms` IN ('agent:list', 'agent:create:sub', 'agent:customer:manage', 'commission:config')
AND @role_l3_id IS NOT NULL
AND NOT EXISTS (
  SELECT 1 FROM `sys_role_menu` rm WHERE rm.`role_id` = @role_l3_id AND rm.`menu_id` = `sys_menu`.`menu_id`
);

INSERT INTO `sys_role_menu` (`role_id`, `menu_id`)
SELECT @role_l4_id, `menu_id` FROM `sys_menu`
WHERE `perms` IN ('agent:list', 'agent:customer:manage', 'bet:my:view', 'commission:config')
AND @role_l4_id IS NOT NULL
AND NOT EXISTS (
  SELECT 1 FROM `sys_role_menu` rm WHERE rm.`role_id` = @role_l4_id AND rm.`menu_id` = `sys_menu`.`menu_id`
);

INSERT INTO `sys_role_menu` (`role_id`, `menu_id`)
SELECT @role_l1_id, `menu_id` FROM `sys_menu`
WHERE `perms` IN ('bet:link:manage', 'bet:my:view')
AND @role_l1_id IS NOT NULL
AND NOT EXISTS (
  SELECT 1 FROM `sys_role_menu` rm WHERE rm.`role_id` = @role_l1_id AND rm.`menu_id` = `sys_menu`.`menu_id`
);

INSERT INTO `sys_role_menu` (`role_id`, `menu_id`)
SELECT @role_l2_id, `menu_id` FROM `sys_menu`
WHERE `perms` IN ('bet:my:view')
AND @role_l2_id IS NOT NULL
AND NOT EXISTS (
  SELECT 1 FROM `sys_role_menu` rm WHERE rm.`role_id` = @role_l2_id AND rm.`menu_id` = `sys_menu`.`menu_id`
);

INSERT INTO `sys_role_menu` (`role_id`, `menu_id`)
SELECT @role_l3_id, `menu_id` FROM `sys_menu`
WHERE `perms` IN ('bet:my:view')
AND @role_l3_id IS NOT NULL
AND NOT EXISTS (
  SELECT 1 FROM `sys_role_menu` rm WHERE rm.`role_id` = @role_l3_id AND rm.`menu_id` = `sys_menu`.`menu_id`
);

INSERT INTO `sys_role_menu` (`role_id`, `menu_id`)
SELECT @role_customer_id, `menu_id` FROM `sys_menu`
WHERE `perms` IN ('bet:my:view')
AND @role_customer_id IS NOT NULL
AND NOT EXISTS (
  SELECT 1 FROM `sys_role_menu` rm WHERE rm.`role_id` = @role_customer_id AND rm.`menu_id` = `sys_menu`.`menu_id`
);

INSERT INTO `sys_role_menu` (`role_id`, `menu_id`)
SELECT @role_customer_id, `menu_id` FROM `sys_menu`
WHERE `perms` IN ('earnings:my')
AND @role_customer_id IS NOT NULL
AND NOT EXISTS (
  SELECT 1 FROM `sys_role_menu` rm WHERE rm.`role_id` = @role_customer_id AND rm.`menu_id` = `sys_menu`.`menu_id`
);

INSERT INTO `sys_role_menu` (`role_id`, `menu_id`)
SELECT @role_l1_id, `menu_id` FROM `sys_menu`
WHERE `perms` IN ('earnings:view')
AND @role_l1_id IS NOT NULL
AND NOT EXISTS (
  SELECT 1 FROM `sys_role_menu` rm WHERE rm.`role_id` = @role_l1_id AND rm.`menu_id` = `sys_menu`.`menu_id`
);

INSERT INTO `sys_role_menu` (`role_id`, `menu_id`)
SELECT @role_l2_id, `menu_id` FROM `sys_menu`
WHERE `perms` IN ('earnings:view')
AND @role_l2_id IS NOT NULL
AND NOT EXISTS (
  SELECT 1 FROM `sys_role_menu` rm WHERE rm.`role_id` = @role_l2_id AND rm.`menu_id` = `sys_menu`.`menu_id`
);

INSERT INTO `sys_role_menu` (`role_id`, `menu_id`)
SELECT @role_l3_id, `menu_id` FROM `sys_menu`
WHERE `perms` IN ('earnings:view')
AND @role_l3_id IS NOT NULL
AND NOT EXISTS (
  SELECT 1 FROM `sys_role_menu` rm WHERE rm.`role_id` = @role_l3_id AND rm.`menu_id` = `sys_menu`.`menu_id`
);

INSERT INTO `sys_role_menu` (`role_id`, `menu_id`)
SELECT @role_l4_id, `menu_id` FROM `sys_menu`
WHERE `perms` IN ('earnings:view')
AND @role_l4_id IS NOT NULL
AND NOT EXISTS (
  SELECT 1 FROM `sys_role_menu` rm WHERE rm.`role_id` = @role_l4_id AND rm.`menu_id` = `sys_menu`.`menu_id`
);
