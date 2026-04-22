from __future__ import annotations

from ..domain.models import CampaignKPI, DrilldownReport


ANOMALY_LABELS_ZH = {
    "ROAS<1": "ROAS<1（低于盈亏平衡）",
    "ACOS>1": "ACOS>100%",
    "Spend>100_and_Sales=0": "高花费零销售",
    "CVR_drop_30pct": "CVR较前段下降超30%",
    "CPC_rise_30pct": "CPC较前段上升超30%",
}

LAYER_LABELS_ZH = {
    "placement": "版位",
    "search_term": "搜索词",
    "targeting": "定向",
}

TRACE_STEP_LABELS_ZH = {
    "resolve_tables": "解析数据表",
    "campaign_screening": "Campaign 初筛",
    "campaign_filter": "Campaign 过滤",
    "abnormal_detection": "异常识别",
    "drilldown_layers": "下钻执行",
    "synthesis": "汇总结论",
}


def _is_zh(lang: str | None) -> bool:
    return (lang or "").lower().startswith("zh")


def _pick(lang: str | None, zh: str, en: str) -> str:
    return zh if _is_zh(lang) else en


def _fmt_anomalies(anomalies: list[str] | tuple[str, ...], lang: str | None) -> str:
    if not anomalies:
        return "-"
    if not _is_zh(lang):
        return ", ".join(anomalies)
    return "；".join(ANOMALY_LABELS_ZH.get(a, a) for a in anomalies)


def _localize_layer(layer: str, lang: str | None) -> str:
    if not _is_zh(lang):
        return layer
    return LAYER_LABELS_ZH.get(layer, layer)


def _replace_many(text: str, replacements: dict[str, str]) -> str:
    out = text
    for old, new in replacements.items():
        out = out.replace(old, new)
    return out


def _localize_issue(text: str, lang: str | None) -> str:
    if not _is_zh(lang):
        return text
    return _replace_many(
        text,
        {
            "Low efficiency placement: ": "低效版位：",
            "Inefficient term: ": "低效搜索词：",
            "Inefficient target: ": "低效定向：",
        },
    )


def _localize_action(text: str, lang: str | None) -> str:
    if not _is_zh(lang):
        return text
    return _replace_many(
        text,
        {
            "Shift budget away from ": "从该版位转移预算：",
            "and lower bid modifier on this placement; re-allocate budget to higher-ROAS placements.": "下调该版位加价系数，并将预算重新分配到更高ROAS版位。",
            "Add negative keyword or reduce bid for this term; keep budget for terms with stable conversion.": "对该词执行否词或降价，预算优先保留给稳定转化词。",
            "Lower bid or narrow targeting expression; keep spend on targets with proven conversion.": "下调出价或收窄定向表达式，预算优先给已验证可转化定向。",
        },
    )


def _localize_evidence(text: str, lang: str | None) -> str:
    if not _is_zh(lang):
        return text
    return _replace_many(
        text,
        {
            "spend_share=": "花费占比=",
            "spend=$": "花费=$",
            "sales=$": "销售额=$",
            "match_type=": "匹配类型=",
            "ROAS=": "ROAS=",
            "ACOS=": "ACOS=",
            "CVR=": "CVR=",
        },
    )


def _localize_peer_evidence(text: str, lang: str | None) -> str:
    if not _is_zh(lang):
        return text
    return _replace_many(
        text,
        {
            "ROAS below peer median": "ROAS低于同批中位数",
            "ACOS above peer median": "ACOS高于同批中位数",
            "CVR below peer median": "CVR低于同批中位数",
            "CPC above peer median": "CPC高于同批中位数",
            "CTR below peer median": "CTR低于同批中位数",
        },
    )


def _localize_trace_step(step: dict, lang: str | None) -> str:
    if not _is_zh(lang):
        return str(step)

    key = str(step.get("step", ""))
    label = TRACE_STEP_LABELS_ZH.get(key, key)

    parts = [f"步骤={label}"]
    for k, v in step.items():
        if k == "step":
            continue
        parts.append(f"{k}={v}")
    return "；".join(parts)


def render_campaign_table(kpis: tuple[CampaignKPI, ...], lang: str = "zh") -> str:
    if not kpis:
        return _pick(lang, "无可用 Campaign 数据。", "No campaign data.")

    if _is_zh(lang):
        lines = [
            "| Campaign | 花费 | 销售额 | 订单 | 展现 | 点击 | CTR | CVR | ACOS | ROAS | 预算消耗率 | 异常标记 |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
        ]
    else:
        lines = [
            "| Campaign | Spend | Sales | Orders | Impr. | Clicks | CTR | CVR | ACOS | ROAS | Budget Util | Anomalies |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
        ]

    for item in kpis:
        lines.append(
            "| {campaign} | ${spend:.2f} | ${sales:.2f} | {orders:.0f} | {impressions:.0f} | "
            "{clicks:.0f} | {ctr:.2%} | {cvr:.2%} | {acos:.2%} | {roas:.2f} | {budget:.2%} | {anomalies} |".format(
                campaign=item.campaign_name,
                spend=item.spend,
                sales=item.sales,
                orders=item.orders,
                impressions=item.impressions,
                clicks=item.clicks,
                ctr=item.ctr,
                cvr=item.cvr,
                acos=item.acos,
                roas=item.roas,
                budget=item.budget_utilization,
                anomalies=_fmt_anomalies(item.anomalies, lang),
            )
        )

    return "\n".join(lines)


def render_drilldown_report(report: DrilldownReport, lang: str = "zh") -> str:
    none_text = _pick(lang, "- 无", "- None")

    lines: list[str] = []
    lines.append(_pick(lang, f"## 广告下钻分析报告（{report.date_range}）", f"## Drilldown Report ({report.date_range})"))
    lines.append("")
    lines.append(_pick(lang, "### 1) Campaign 总览", "### 1) Campaign KPI Overview"))
    lines.append(render_campaign_table(report.campaign_kpis, lang=lang))
    lines.append("")

    lines.append(_pick(lang, "### 2) Campaign 异常与同批对比", "### 2) Campaign Anomaly + Peer Comparison"))
    if report.campaign_comparison:
        lines.append(
            _pick(
                lang,
                "| Campaign | 花费排名 | ROAS较中位数差值 | ACOS较中位数差值 | CVR较中位数差值 | CTR较中位数差值 | CPC较中位数差值 | 异常 | 对比证据 |",
                "| Campaign | Spend Rank | ROAS Δvs Median | ACOS Δvs Median | CVR Δvs Median | CTR Δvs Median | CPC Δvs Median | Abnormal | Peer Evidence |",
            )
        )
        lines.append("|---|---:|---:|---:|---:|---:|---:|---|---|")
        for row in report.campaign_comparison:
            lines.append(
                "| {campaign} | {rank} | {roas_delta:+.2f} | {acos_delta:+.2%} | {cvr_delta:+.2%} | {ctr_delta:+.2%} | {cpc_delta:+.2f} | {abnormal} | {evidence} |".format(
                    campaign=row["campaign"],
                    rank=row["spend_rank"],
                    roas_delta=row["roas_vs_median"],
                    acos_delta=row["acos_vs_median"],
                    cvr_delta=row["cvr_vs_median"],
                    ctr_delta=row["ctr_vs_median"],
                    cpc_delta=row["cpc_vs_median"],
                    abnormal=_fmt_anomalies(row["anomalies"], lang),
                    evidence=(
                        "；".join(_localize_peer_evidence(x, lang) for x in row["anomaly_reasons_vs_peers"])
                        if row["anomaly_reasons_vs_peers"]
                        else "-"
                    ),
                )
            )
    else:
        lines.append(none_text)
    lines.append("")

    lines.append(_pick(lang, "### 3) 异常 Campaign 列表", "### 3) Abnormal Campaigns"))
    if report.abnormal_campaigns:
        for campaign in report.abnormal_campaigns:
            lines.append(f"- {campaign}")
    else:
        lines.append(none_text)
    lines.append("")

    lines.append(_pick(lang, "### 4) 下钻发现", "### 4) Drilldown Findings"))
    if report.findings:
        for finding in report.findings:
            lines.append(
                f"- [{finding.priority}] {finding.campaign_name} / {_localize_layer(finding.layer, lang)}: "
                f"{_localize_issue(finding.issue, lang)}；证据={_localize_evidence(finding.evidence, lang)}"
                if _is_zh(lang)
                else f"- [{finding.priority}] {finding.campaign_name} / {finding.layer}: {finding.issue}; evidence={finding.evidence}"
            )
    else:
        lines.append(none_text)
    lines.append("")

    lines.append(_pick(lang, "### 5) 版位横向对比", "### 5) Placement Horizontal Comparison"))
    if report.placement_breakdown:
        for campaign, rows in report.placement_breakdown.items():
            lines.append(f"#### {campaign}")
            lines.append(
                _pick(
                    lang,
                    "| 版位 | 花费占比 | 花费 | 销售额 | ROAS | ACOS | CTR | CVR | ROAS较Campaign差值 |",
                    "| Placement | Spend Share | Spend | Sales | ROAS | ACOS | CTR | CVR | ROAS Δvs Campaign |",
                )
            )
            lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|")
            for row in rows:
                lines.append(
                    "| {placement} | {spend_share:.1%} | ${spend:.2f} | ${sales:.2f} | {roas:.2f} | {acos:.1%} | {ctr:.2%} | {cvr:.2%} | {roas_delta:+.2f} |".format(
                        placement=row["placement"],
                        spend_share=row["spend_share"],
                        spend=row["spend"],
                        sales=row["sales"],
                        roas=row["roas"],
                        acos=row["acos"],
                        ctr=row["ctr"],
                        cvr=row["cvr"],
                        roas_delta=row["roas_delta_vs_campaign"],
                    )
                )
            lines.append("")
    else:
        lines.append(none_text)
        lines.append("")

    lines.append(_pick(lang, "### 6) 搜索词横向对比（按花费Top）", "### 6) Search Term Horizontal Comparison (Top Spend)"))
    if report.search_term_breakdown:
        for campaign, rows in report.search_term_breakdown.items():
            lines.append(f"#### {campaign}")
            lines.append(
                _pick(
                    lang,
                    "| 搜索词 | 匹配类型 | 花费 | 销售额 | ROAS | ACOS | CVR | ROAS较Campaign差值 |",
                    "| Search Term | Match Type | Spend | Sales | ROAS | ACOS | CVR | ROAS Δvs Campaign |",
                )
            )
            lines.append("|---|---|---:|---:|---:|---:|---:|---:|")
            for row in rows:
                lines.append(
                    "| {term} | {match_type} | ${spend:.2f} | ${sales:.2f} | {roas:.2f} | {acos:.1%} | {cvr:.2%} | {roas_delta:+.2f} |".format(
                        term=row["search_term"],
                        match_type=row["match_type"],
                        spend=row["spend"],
                        sales=row["sales"],
                        roas=row["roas"],
                        acos=row["acos"],
                        cvr=row["cvr"],
                        roas_delta=row["roas_delta_vs_campaign"],
                    )
                )
            lines.append("")
    else:
        lines.append(none_text)
        lines.append("")

    lines.append(_pick(lang, "### 7) 定向横向对比（按花费Top）", "### 7) Targeting Horizontal Comparison (Top Spend)"))
    if report.targeting_breakdown:
        for campaign, rows in report.targeting_breakdown.items():
            lines.append(f"#### {campaign}")
            lines.append(
                _pick(
                    lang,
                    "| 定向 | 匹配类型 | 花费 | 销售额 | ROAS | ACOS | CVR | ROAS较Campaign差值 |",
                    "| Targeting | Match Type | Spend | Sales | ROAS | ACOS | CVR | ROAS Δvs Campaign |",
                )
            )
            lines.append("|---|---|---:|---:|---:|---:|---:|---:|")
            for row in rows:
                lines.append(
                    "| {targeting} | {match_type} | ${spend:.2f} | ${sales:.2f} | {roas:.2f} | {acos:.1%} | {cvr:.2%} | {roas_delta:+.2f} |".format(
                        targeting=row["targeting"],
                        match_type=row["match_type"],
                        spend=row["spend"],
                        sales=row["sales"],
                        roas=row["roas"],
                        acos=row["acos"],
                        cvr=row["cvr"],
                        roas_delta=row["roas_delta_vs_campaign"],
                    )
                )
            lines.append("")
    else:
        lines.append(none_text)
        lines.append("")

    lines.append(_pick(lang, "### 8) 建议动作", "### 8) Recommended Actions"))
    if report.actions:
        for action in report.actions:
            lines.append(f"- {_localize_action(action, lang)}")
    else:
        lines.append(none_text)

    lines.append("")
    lines.append(_pick(lang, "### 9) 分析步骤日志", "### 9) Analysis Trace"))
    if report.analysis_trace:
        for step in report.analysis_trace:
            lines.append(f"- {_localize_trace_step(step, lang)}")
    else:
        lines.append(none_text)

    if report.notes:
        lines.append("")
        lines.append(_pick(lang, "### 备注", "### Notes"))
        for note in report.notes:
            lines.append(f"- {note}")

    return "\n".join(lines)
