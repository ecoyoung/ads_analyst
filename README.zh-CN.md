**简体中文** | [English](README.md)

# ads_analyst

用于 Amazon Ads 诊断的 DeerFlow 风格多智能体架构。

## 项目功能

- 检查 PostgreSQL 连接性和表可用性
- 运行以广告活动（campaign）为先的诊断
- 对异常广告活动强制执行下钻分析：
  - 展示位置（Placement）
  - 搜索词（Search Term）
  - 投放目标（Targeting）
- 输出与根因关联的行动建议

## 标准化架构

```text
src/ads_analyst
├── app/
│   └── cli.py                     # CLI entry and command routing
├── orchestrator/
│   └── drilldown_orchestrator.py  # campaign -> placement/search-term/targeting orchestration
├── agents/
│   ├── base.py                    # shared data-reading/filtering utilities
│   ├── campaign_agent.py          # campaign screening + anomaly detection
│   ├── placement_agent.py         # placement root-cause analysis
│   ├── search_term_agent.py       # term-level root-cause analysis
│   └── targeting_agent.py         # targeting-level root-cause analysis
├── domain/
│   └── models.py                  # report/kpi/finding data contracts
├── reporting/
│   └── markdown_renderer.py       # markdown output contract
├── shared/
│   ├── column_mapping.py          # unified field alias inference
│   └── metrics.py                 # safe metric formulas
├── infra/
│   └── database.py                # infrastructure compatibility exports
├── config.py                      # load database config (toml/env/legacy markdown + env override)
├── database.py                    # PostgreSQL client
├── campaign_service.py            # backward-compatible summary API
└── cli.py                         # backward-compatible module entry
```

## 安装

```bash
pip install -r requirements.txt
```

## 命令

1) 数据库检查

```bash
PYTHONPATH=src python3 -m ads_analyst.cli db-check
```

2) 广告活动 KPI 汇总

```bash
PYTHONPATH=src python3 -m ads_analyst.cli campaign-summary --start-date 2026-04-04 --end-date 2026-04-17
```

3) 下钻报告（推荐）

```bash
PYTHONPATH=src python3 -m ads_analyst.cli drilldown-report --start-date 2026-04-04 --end-date 2026-04-17
```

4) 按广告活动关键字过滤

```bash
PYTHONPATH=src python3 -m ads_analyst.cli drilldown-report --campaign-filter magnesium
```

5) 使用自定义阈值规则

```bash
PYTHONPATH=src python3 -m ads_analyst.cli drilldown-report --thresholds ./thresholds.toml
```

6) 为每次运行写出 markdown 和中间 JSON 产物

```bash
PYTHONPATH=src python3 -m ads_analyst.cli drilldown-report --output-root ./outputs
```

7) 生成中文/英文报告

```bash
PYTHONPATH=src python3 -m ads_analyst.cli drilldown-report --lang zh
PYTHONPATH=src python3 -m ads_analyst.cli drilldown-report --lang en
```

每次运行时，工具会写出：
- `report.md`
- `report.json`
- `campaign_kpis.json`
- `campaign_comparison.json`
- `placement_breakdown.json`
- `search_term_breakdown.json`
- `targeting_breakdown.json`
- `findings.json`
- `actions.json`
- `analysis_trace.json`（结构化审计日志，不是隐藏的模型思维链）
- `manifest.json`

## 配置优先级

推荐的配置文件：`database.toml`。

支持的配置格式：
- `.toml`（推荐，主流）
- `.env` 风格的键值文件
- 旧版 `database.md`（向后兼容）

环境变量会覆盖文件配置：

- `ADS_DB_HOST`
- `ADS_DB_PORT`
- `ADS_DB_NAME`
- `ADS_DB_USER`
- `ADS_DB_PASSWORD`
- `ADS_DB_CHARSET`

### `database.toml` 示例

```toml
[database]
host = "127.0.0.1"
port = 5432
database = "postgres"
user = "your_db_user"
password = "your_db_password"
charset = "utf8"

[tables]
names = ["amazon_ads_sp_campaigns_innerbrightness"]
```

## 说明

- 本仓库目前在 `skills/custom/*` 下包含技能文档，定义了分层下钻架构。
- 运行时代码现在遵循相同的分层标准，可以按技能层独立扩展。
- 阈值集中定义在 `thresholds.toml` 中（campaign/placement/search_term/targeting）。
