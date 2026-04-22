# Campaign Analysis Skill 已迁移

该文件已迁移为 DeerFlow 标准 Skill 架构。

## Skill 入口与关系

主控编排入口：
- [amazon-ads-drilldown-analysis/SKILL.md](/Users/anker/Documents/ads_analyst/skills/custom/amazon-ads-drilldown-analysis/SKILL.md)

分层技能：
- [amazon-campaign-analysis/SKILL.md](/Users/anker/Documents/ads_analyst/skills/custom/amazon-campaign-analysis/SKILL.md)
- [amazon-placement-analysis/SKILL.md](/Users/anker/Documents/ads_analyst/skills/custom/amazon-placement-analysis/SKILL.md)
- [amazon-search-term-analysis/SKILL.md](/Users/anker/Documents/ads_analyst/skills/custom/amazon-search-term-analysis/SKILL.md)
- [amazon-targeting-analysis/SKILL.md](/Users/anker/Documents/ads_analyst/skills/custom/amazon-targeting-analysis/SKILL.md)

## 分析顺序（强制）

1. Campaign 诊断
2. 对异常 Campaign 触发 Placement 下钻
3. 对异常 Campaign 触发 Search Term 下钻
4. 对异常 Campaign 触发 Targeting 下钻
5. 合并根因并输出动作建议

## 字段 Mapping 与口径

- [field-mapping-campaign.md](/Users/anker/Documents/ads_analyst/skills/custom/amazon-campaign-analysis/references/field-mapping-campaign.md)
- [field-mapping-placement.md](/Users/anker/Documents/ads_analyst/skills/custom/amazon-campaign-analysis/references/field-mapping-placement.md)
- [field-mapping-search-term.md](/Users/anker/Documents/ads_analyst/skills/custom/amazon-campaign-analysis/references/field-mapping-search-term.md)
- [field-mapping-targeting.md](/Users/anker/Documents/ads_analyst/skills/custom/amazon-campaign-analysis/references/field-mapping-targeting.md)
- [metric-formulas.md](/Users/anker/Documents/ads_analyst/skills/custom/amazon-campaign-analysis/references/metric-formulas.md)
