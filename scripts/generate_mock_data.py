#!/usr/bin/env python3
"""
Generate mock data for agent distribution system testing.
Adds ~10 records per table across all agent levels.
"""

import pymysql
import random
import uuid
from datetime import datetime, timedelta

DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 13306,
    "user": "root",
    "password": "root",
    "database": "ruoyi-fastapi",
    "cursorclass": pymysql.cursors.DictCursor,
    "autocommit": False,
}

conn = pymysql.connect(**DB_CONFIG)
cur = conn.cursor()


ID_COLUMNS = {
    "agent_info": "agent_id",
    "bet_link": "link_id",
    "bet_record": "record_id",
    "user_earnings": "earning_id",
    "agent_earnings": "earning_id",
}


def next_id(table):
    id_col = ID_COLUMNS.get(table, f"{table}_id")
    cur.execute(f"SELECT COALESCE(MAX({id_col}), 0) + 1 AS nid FROM {table}")
    return cur.fetchone()["nid"]


# ─── Helper: get max user_id ───
def max_user_id():
    cur.execute("SELECT COALESCE(MAX(user_id), 0) AS mid FROM sys_user")
    return cur.fetchone()["mid"]


now = datetime.now()
uid = max_user_id() + 1  # start user_id

# ═══════════════════════════════════════════════════════════
# 1. Add more AGENTS (fill out the tree)
# ═══════════════════════════════════════════════════════════
print("=== Adding agents ===")

# Existing agents: 1(L1), 2-3(L2 under 1), 4(L3 under 2), 5(L4 under 4), 6-7(L2 under 1)
# We need: more L2, L3, L4 agents under different branches

agents_to_add = [
    # (agent_level, parent_agent_id, agent_code, user_name, nick_name, phone, commission_rate, can_create_sub, remark)
    # L2 agents under AGL1DEMO01 (agent_id=1)
    (
        2,
        1,
        "AGL2BETA01",
        "agent_l2_beta_01",
        "高级代理Beta01",
        "13900000010",
        0.0200,
        1,
        "Beta测试高级代理",
    ),
    (
        2,
        1,
        "AGL2BETA02",
        "agent_l2_beta_02",
        "高级代理Beta02",
        "13900000011",
        0.0200,
        0,
        "Beta测试高级代理",
    ),
    (
        2,
        1,
        "AGL2GAMMA01",
        "agent_l2_gamma_01",
        "高级代理Gamma01",
        "13900000012",
        0.0250,
        1,
        "Gamma测试高级代理",
    ),
    # L3 agents under AGL2BETA01 (will get agent_id after insert)
    (
        3,
        None,
        "AGL3BETA01",
        "agent_l3_beta_01",
        "中级代理Beta01",
        "13900000020",
        0.0150,
        1,
        "Beta测试中级代理",
    ),
    (
        3,
        None,
        "AGL3GAMMA01",
        "agent_l3_gamma_01",
        "中级代理Gamma01",
        "13900000021",
        0.0150,
        0,
        "Gamma测试中级代理",
    ),
    # L4 agents
    (
        4,
        None,
        "AGL4BETA01",
        "agent_l4_beta_01",
        "初级代理Beta01",
        "13900000030",
        0.0100,
        0,
        "Beta测试初级代理",
    ),
]


def agent_exists(code):
    cur.execute("SELECT agent_id FROM agent_info WHERE agent_code = %s", (code,))
    return cur.fetchone() is not None


agent_id_map = {}  # maps code -> agent_id for linking parent

# Load existing agents into map
cur.execute("SELECT agent_id, agent_code FROM agent_info")
for row in cur.fetchall():
    agent_id_map[row["agent_code"]] = row["agent_id"]

# First pass: create L2 agents (parent=1, known)
for level, parent_id, code, uname, nick, phone, rate, can_sub, remark in agents_to_add:
    if level == 2:
        if agent_exists(code):
            aid = agent_id_map[code]
            print(f"  L2 agent exists: {code} (agent_id={aid})")
            continue
        aid = next_id("agent_info")
        cur.execute(
            """
            INSERT INTO agent_info (agent_id, user_id, parent_agent_id, agent_code, agent_level, 
                                    bet_commission_rate, can_create_sub, status, remark, create_time, update_time)
            VALUES (%s, %s, %s, %s, %s, %s, %s, '0', %s, NOW(), NOW())
        """,
            (aid, uid, parent_id, code, level, rate, can_sub, remark),
        )

        cur.execute(
            """
            INSERT INTO sys_user (user_id, user_name, nick_name, phonenumber, password, agent_level, 
                                  belong_agent_id, can_create_sub_agent, status, del_flag, create_time, update_time)
            VALUES (%s, %s, %s, %s, '$2a$10$7JB720yubVSZvUI0rEqK/.VqGOZTH.ulu33dHOiBE8ByOhJIrdAu2', 
                    %s, %s, 0, '0', '0', NOW(), NOW())
        """,
            (uid, uname, nick, phone, level, parent_id),
        )

        agent_id_map[code] = aid
        print(f"  Created L{level} agent: {code} (agent_id={aid}, user_id={uid})")
        uid += 1

# Second pass: create L3 agents (need to find parent L2 agent_id)
l2_agents = [code for code in agent_id_map if code.startswith("AGL2")]
for level, _, code, uname, nick, phone, rate, can_sub, remark in agents_to_add:
    if level == 3:
        if agent_exists(code):
            aid = agent_id_map[code]
            print(f"  L3 agent exists: {code} (agent_id={aid})")
            continue
        parent_code = l2_agents[0] if l2_agents else "AGL2BETA01"
        parent_aid = agent_id_map[parent_code]

        aid = next_id("agent_info")
        cur.execute(
            """
            INSERT INTO agent_info (agent_id, user_id, parent_agent_id, agent_code, agent_level,
                                    bet_commission_rate, can_create_sub, status, remark, create_time, update_time)
            VALUES (%s, %s, %s, %s, %s, %s, %s, '0', %s, NOW(), NOW())
        """,
            (aid, uid, parent_aid, code, level, rate, can_sub, remark),
        )

        cur.execute(
            """
            INSERT INTO sys_user (user_id, user_name, nick_name, phonenumber, password, agent_level,
                                  belong_agent_id, can_create_sub_agent, status, del_flag, create_time, update_time)
            VALUES (%s, %s, %s, %s, '$2a$10$7JB720yubVSZvUI0rEqK/.VqGOZTH.ulu33dHOiBE8ByOhJIrdAu2',
                    %s, %s, 0, '0', '0', NOW(), NOW())
        """,
            (uid, uname, nick, phone, level, parent_aid),
        )

        agent_id_map[code] = aid
        print(
            f"  Created L{level} agent: {code} (agent_id={aid}, user_id={uid}, parent={parent_code})"
        )
        uid += 1

# Third pass: create L4 agents
l3_agents = [code for code in agent_id_map if code.startswith("AGL3")]
for level, _, code, uname, nick, phone, rate, can_sub, remark in agents_to_add:
    if level == 4:
        if agent_exists(code):
            aid = agent_id_map[code]
            print(f"  L4 agent exists: {code} (agent_id={aid})")
            continue
        parent_code = l3_agents[0] if l3_agents else "AGL3BETA01"
        parent_aid = agent_id_map[parent_code]

        aid = next_id("agent_info")
        cur.execute(
            """
            INSERT INTO agent_info (agent_id, user_id, parent_agent_id, agent_code, agent_level,
                                    bet_commission_rate, can_create_sub, status, remark, create_time, update_time)
            VALUES (%s, %s, %s, %s, %s, %s, %s, '0', %s, NOW(), NOW())
        """,
            (aid, uid, parent_aid, code, level, rate, can_sub, remark),
        )

        cur.execute(
            """
            INSERT INTO sys_user (user_id, user_name, nick_name, phonenumber, password, agent_level,
                                  belong_agent_id, can_create_sub_agent, status, del_flag, create_time, update_time)
            VALUES (%s, %s, %s, %s, '$2a$10$7JB720yubVSZvUI0rEqK/.VqGOZTH.ulu33dHOiBE8ByOhJIrdAu2',
                    %s, %s, 0, '0', '0', NOW(), NOW())
        """,
            (uid, uname, nick, phone, level, parent_aid),
        )

        agent_id_map[code] = aid
        print(
            f"  Created L{level} agent: {code} (agent_id={aid}, user_id={uid}, parent={parent_code})"
        )
        uid += 1

conn.commit()

# Refresh all agent info
cur.execute(
    "SELECT agent_id, agent_code, agent_level, user_id FROM agent_info ORDER BY agent_id"
)
all_agents = cur.fetchall()
print(f"\nTotal agents: {len(all_agents)}")
for a in all_agents:
    print(
        f"  agent_id={a['agent_id']}, code={a['agent_code']}, level={a['agent_level']}, user_id={a['user_id']}"
    )

# Build lookup maps
agent_by_id = {a["agent_id"]: a for a in all_agents}
agent_by_code = {a["agent_code"]: a for a in all_agents}

# Get all user_ids for customers
all_user_ids = [a["user_id"] for a in all_agents]

# ═══════════════════════════════════════════════════════════
# 2. Add CUSTOMER users (~10 customers distributed across agents)
# ═══════════════════════════════════════════════════════════
print("\n=== Adding customers ===")

customer_names = [
    ("cust_bj_001", "北京客户01", "13800001001"),
    ("cust_bj_002", "北京客户02", "13800001002"),
    ("cust_sh_001", "上海客户01", "13800002001"),
    ("cust_sh_002", "上海客户02", "13800002002"),
    ("cust_gz_001", "广州客户01", "13800003001"),
    ("cust_gz_002", "广州客户02", "13800003002"),
    ("cust_sz_001", "深圳客户01", "13800004001"),
    ("cust_hz_001", "杭州客户01", "13800005001"),
    ("cust_cd_001", "成都客户01", "13800006001"),
    ("cust_wh_001", "武汉客户01", "13800007001"),
    ("cust_nj_001", "南京客户01", "13800008001"),
    ("cust_cs_001", "长沙客户01", "13800009001"),
]

# Distribute customers across different agents
customer_agent_assignments = [
    # (customer_index, belong_agent_id)
    (0, 1),  # -> L1 总代理
    (1, 2),  # -> L2 高级代理01
    (2, 3),  # -> L2 高级代理02
    (3, 4),  # -> L3 中级代理01
    (4, 5),  # -> L4 初级代理
    (5, 1),  # -> L1 总代理
    (6, 2),  # -> L2 高级代理01
    (7, 6),  # -> L2 最终验收代理
    (8, 7),  # -> L2 验收代理559868
    (9, 3),  # -> L2 高级代理02
    (10, 4),  # -> L3 中级代理01
    (11, 5),  # -> L4 初级代理
]

for cust_idx, belong_aid in customer_agent_assignments:
    uname, nick, phone = customer_names[cust_idx]
    cur.execute(
        """
        INSERT INTO sys_user (user_id, user_name, nick_name, phonenumber, password, agent_level,
                              belong_agent_id, can_create_sub_agent, status, del_flag, create_time, update_time)
        VALUES (%s, %s, %s, %s, '$2a$10$7JB720yubVSZvUI0rEqK/.VqGOZTH.ulu33dHOiBE8ByOhJIrdAu2',
                0, %s, 0, '0', '0', NOW(), NOW())
    """,
        (uid, uname, nick, phone, belong_aid),
    )
    print(f"  Created customer: {uname} (user_id={uid}, belong_agent_id={belong_aid})")
    all_user_ids.append(uid)
    uid += 1

conn.commit()
print(f"Total customers added: {len(customer_agent_assignments)}")

# ═══════════════════════════════════════════════════════════
# 3. Add BET LINKS (~10 links with various statuses)
# ═══════════════════════════════════════════════════════════
print("\n=== Adding bet links ===")

link_id = next_id("bet_link")
link_configs = [
    # (link_name, bet_desc, odds, days_offset, max_users, status, confirm_result)
    # status: 0=待投注, 1=投注中, 2=已截止, 3=已确认
    ("2026年4月第1期", "本期投注：足球世界杯预选赛", 2.50, -5, 50, 3, 1),  # 已确认-中奖
    ("2026年4月第2期", "本期投注：NBA季后赛", 3.00, -4, 30, 3, 0),  # 已确认-未中
    ("2026年4月第3期", "本期投注：英超联赛", 1.80, -3, 100, 3, 1),  # 已确认-中奖
    ("2026年4月第4期", "本期投注：欧冠半决赛", 4.50, -2, 20, 3, 0),  # 已确认-未中
    ("2026年4月第5期", "本期投注：网球大满贯", 2.20, -1, 40, 3, 1),  # 已确认-中奖
    ("2026年4月第6期", "本期投注：F1赛车", 3.50, 0, 60, 1, None),  # 投注中
    ("2026年4月第7期", "本期投注：乒乓球世锦赛", 1.90, 1, 80, 0, None),  # 待投注
    ("2026年4月第8期", "本期投注：游泳锦标赛", 2.80, 2, 25, 0, None),  # 待投注
    ("2026年4月第9期", "本期投注：羽毛球公开赛", 3.20, -6, 35, 2, None),  # 已截止
    ("2026年4月第10期", "本期投注：篮球全明星赛", 2.00, -7, 45, 3, 1),  # 已确认-中奖
]

link_ids = []
for (
    link_name,
    bet_desc,
    odds,
    days_offset,
    max_users,
    status,
    confirm_result,
) in link_configs:
    token = uuid.uuid4().hex
    create_time = now + timedelta(days=days_offset - 1)
    expire_time = now + timedelta(days=days_offset, hours=2)
    confirm_time = (now + timedelta(days=days_offset, hours=3)) if status == 3 else None

    cur.execute(
        """
        INSERT INTO bet_link (link_id, link_token, agent_id, link_name, bet_desc, odds,
                              expire_at, max_users, status, confirm_result, confirm_time, create_time)
        VALUES (%s, %s, 1, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """,
        (
            link_id,
            token,
            link_name,
            bet_desc,
            odds,
            expire_time,
            max_users,
            status,
            confirm_result,
            confirm_time,
            create_time,
        ),
    )

    link_ids.append(link_id)
    status_name = {0: "待投注", 1: "投注中", 2: "已截止", 3: "已确认"}
    print(f"  Link {link_id}: {link_name} (status={status_name[status]}, odds={odds})")
    link_id += 1

conn.commit()
print(f"Total bet links: {len(link_configs)}")

# ═══════════════════════════════════════════════════════════
# 4. Add BET RECORDS (~15 records across different links/users)
# ═══════════════════════════════════════════════════════════
print("\n=== Adding bet records ===")

record_id = next_id("bet_record")

# Get customer user_ids (agent_level=0 and belong_agent_id is not null)
cur.execute("""
    SELECT u.user_id, u.belong_agent_id
    FROM sys_user u
    WHERE u.agent_level = 0 AND u.belong_agent_id IS NOT NULL
    ORDER BY u.user_id
""")
customers = cur.fetchall()
customer_user_ids = [(c["user_id"], c["belong_agent_id"]) for c in customers]

cur.execute("""
    SELECT u.user_id, ai.agent_id as belong_agent_id
    FROM sys_user u
    JOIN agent_info ai ON u.user_id = ai.user_id
    WHERE ai.agent_level > 1
    ORDER BY u.user_id
""")
agent_bettors = [(r["user_id"], r["belong_agent_id"]) for r in cur.fetchall()]

all_bettors = customer_user_ids + agent_bettors
n_cust = len(customer_user_ids)

record_configs = [
    (0, 0, 500.00, 1, 1),
    (0, 1, 300.00, 1, 1),
    (0, 2, 200.00, 1, 0),
    (1, 0, 1000.00, 1, 0),
    (1, 3, 800.00, 1, 0),
    (2, 4, 1500.00, 1, 1),
    (2, 5, 600.00, 1, 1),
    (2, 6, 400.00, 1, 0),
    (3, 0, 2000.00, 1, 0),
    (3, 7, 350.00, 1, 0),
    (4, 1, 750.00, 1, 1),
    (4, 8, 900.00, 1, 1),
    (5, 2, 450.00, 1, None),
    (5, 9, 550.00, 1, None),
    (9, 3, 1200.00, 1, 1),
    (0, n_cust, 300.00, 1, 1),
    (2, n_cust + 1, 500.00, 1, 1),
    (4, n_cust + 2, 200.00, 1, 0),
    (9, n_cust + 3, 800.00, 1, 1),
]

for link_idx, bettor_idx, bet_amount, is_confirmed, is_win in record_configs:
    if bettor_idx >= len(all_bettors):
        continue

    lid = link_ids[link_idx]
    bettor_uid, belong_aid = all_bettors[bettor_idx]

    # Get link odds
    cur.execute("SELECT odds FROM bet_link WHERE link_id = %s", (lid,))
    link_odds = cur.fetchone()["odds"]

    win_amount = round(bet_amount * float(link_odds), 2) if is_win == 1 else 0
    round_profit = round(win_amount - bet_amount, 2) if is_win is not None else 0

    confirm_time = (now + timedelta(days=-2, hours=1)) if is_confirmed else None

    cur.execute(
        """
        INSERT INTO bet_record (record_id, link_id, user_id, belong_agent_id, bet_amount, odds,
                                is_confirmed, confirm_time, is_win, create_time)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
    """,
        (
            record_id,
            lid,
            bettor_uid,
            belong_aid,
            bet_amount,
            float(link_odds),
            is_confirmed,
            confirm_time,
            is_win,
        ),
    )

    status_text = {1: "已确认", 0: "未确认"}
    win_text = {1: "中奖", 0: "未中", None: "待确认"}
    print(
        f"  Record {record_id}: Link{lid} User{bettor_uid} ¥{bet_amount} ({status_text[is_confirmed]}, {win_text[is_win]})"
    )
    record_id += 1

conn.commit()
print(f"Total bet records: {len(record_configs)}")

# ═══════════════════════════════════════════════════════════
# 5. Add USER EARNINGS (for confirmed links)
# ═══════════════════════════════════════════════════════════
print("\n=== Adding user earnings ===")

earning_id = next_id("user_earnings")

# Get confirmed bet records with wins
cur.execute("""
    SELECT br.record_id, br.link_id, br.user_id, br.belong_agent_id, br.bet_amount, 
           br.win_amount, br.round_profit, bl.confirm_time
    FROM bet_record br
    JOIN bet_link bl ON br.link_id = bl.link_id
    WHERE br.is_confirmed = 1 AND bl.status = 3
""")
confirmed_records = cur.fetchall()

for rec in confirmed_records:
    cur.execute(
        "SELECT COUNT(*) as cnt FROM user_earnings WHERE user_id = %s AND link_id = %s",
        (rec["user_id"], rec["link_id"]),
    )
    if cur.fetchone()["cnt"] > 0:
        continue

    cur.execute(
        """
        INSERT INTO user_earnings (earning_id, user_id, belong_agent_id, link_id, bet_amount,
                                   win_amount, profit, confirm_time, create_time)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
    """,
        (
            earning_id,
            rec["user_id"],
            rec["belong_agent_id"],
            rec["link_id"],
            rec["bet_amount"],
            rec["win_amount"],
            rec["round_profit"],
            rec["confirm_time"],
        ),
    )
    earning_id += 1

conn.commit()
cur.execute("SELECT COUNT(*) as cnt FROM user_earnings")
print(f"Total user earnings: {cur.fetchone()['cnt']}")

# ═══════════════════════════════════════════════════════════
# 6. Add AGENT EARNINGS (for confirmed links)
# ═══════════════════════════════════════════════════════════
print("\n=== Adding agent earnings ===")

agent_earning_id = next_id("agent_earnings")

# For each confirmed bet record, calculate agent commissions
cur.execute("""
    SELECT br.record_id, br.link_id, br.user_id, br.belong_agent_id, br.bet_amount,
           br.round_profit as user_profit, bl.confirm_time
    FROM bet_record br
    JOIN bet_link bl ON br.link_id = bl.link_id
    WHERE br.is_confirmed = 1 AND bl.status = 3
""")
confirmed_recs = cur.fetchall()

for rec in confirmed_recs:
    belong_aid = rec["belong_agent_id"]
    bet_amount = float(rec["bet_amount"])
    user_profit = float(rec["user_profit"])

    # Get agent's commission rate
    cur.execute(
        "SELECT bet_commission_rate, parent_agent_id FROM agent_info WHERE agent_id = %s",
        (belong_aid,),
    )
    agent_info = cur.fetchone()
    if not agent_info:
        continue

    bet_commission = round(bet_amount * float(agent_info["bet_commission_rate"]), 2)

    # Profit commission (from commission_config)
    profit_commission = 0
    if user_profit > 0:
        cur.execute(
            """
            SELECT commission_amt, split_ratio FROM commission_config 
            WHERE agent_id IS NULL AND %s BETWEEN profit_min AND profit_max
            ORDER BY sort_order LIMIT 1
        """,
            (user_profit,),
        )
        config = cur.fetchone()
        if config:
            profit_commission = round(
                float(config["commission_amt"]) * float(config["split_ratio"]), 2
            )

    total_commission = round(bet_commission + profit_commission, 2)

    cur.execute(
        "SELECT COUNT(*) as cnt FROM agent_earnings WHERE agent_id = %s AND source_user_id = %s AND link_id = %s AND earn_type = 'direct'",
        (belong_aid, rec["user_id"], rec["link_id"]),
    )
    if cur.fetchone()["cnt"] == 0:
        cur.execute(
            """
            INSERT INTO agent_earnings (earning_id, agent_id, source_user_id, link_id, total_bet_amt,
                                        user_profit, earn_type, bet_commission, profit_commission,
                                        total_commission, create_time)
            VALUES (%s, %s, %s, %s, %s, %s, 'direct', %s, %s, %s, NOW())
        """,
            (
                agent_earning_id,
                belong_aid,
                rec["user_id"],
                rec["link_id"],
                bet_amount,
                user_profit,
                bet_commission,
                profit_commission,
                total_commission,
            ),
        )
        agent_earning_id += 1

    # Parent agent split (if exists)
    if agent_info["parent_agent_id"] and profit_commission > 0:
        cur.execute(
            "SELECT COUNT(*) as cnt FROM agent_earnings WHERE agent_id = %s AND source_user_id = %s AND link_id = %s AND earn_type = 'inherit'",
            (agent_info["parent_agent_id"], rec["user_id"], rec["link_id"]),
        )
        if cur.fetchone()["cnt"] == 0:
            cur.execute(
                """
                SELECT commission_amt, split_ratio FROM commission_config 
                WHERE agent_id IS NULL AND %s BETWEEN profit_min AND profit_max
                ORDER BY sort_order LIMIT 1
            """,
                (user_profit,),
            )
            config = cur.fetchone()
            if config:
                parent_commission = round(
                    float(config["commission_amt"])
                    * (1 - float(config["split_ratio"])),
                    2,
                )
                cur.execute(
                    """
                    INSERT INTO agent_earnings (earning_id, agent_id, source_user_id, link_id, total_bet_amt,
                                                user_profit, earn_type, bet_commission, profit_commission,
                                                total_commission, create_time)
                    VALUES (%s, %s, %s, %s, %s, %s, 'inherit', 0, %s, %s, NOW())
                """,
                    (
                        agent_earning_id,
                        agent_info["parent_agent_id"],
                        rec["user_id"],
                        rec["link_id"],
                        bet_amount,
                        user_profit,
                        parent_commission,
                        parent_commission,
                    ),
                )
                agent_earning_id += 1

conn.commit()
cur.execute("SELECT COUNT(*) as cnt FROM agent_earnings")
print(f"Total agent earnings: {cur.fetchone()['cnt']}")

# ═══════════════════════════════════════════════════════════
# Summary
# ═══════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("MOCK DATA GENERATION COMPLETE")
print("=" * 60)

for table in [
    "sys_user",
    "agent_info",
    "bet_link",
    "bet_record",
    "user_earnings",
    "agent_earnings",
    "commission_config",
]:
    cur.execute(f"SELECT COUNT(*) as cnt FROM {table}")
    print(f"  {table}: {cur.fetchone()['cnt']} rows")

conn.close()
print("\nDone!")
