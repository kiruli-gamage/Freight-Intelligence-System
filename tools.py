import pandas as pd
from langchain.tools import tool
from datetime import datetime


def calculate_risk_score(row, days_since_inspection):
    score = 0
    util = (row["Current_Load"] / row["Max_Capacity"]) * 100
    if util > 90: score += 4
    elif util > 70: score += 2
    elif util > 50: score += 1

    if days_since_inspection > 30: score += 3
    elif days_since_inspection > 20: score += 2
    elif days_since_inspection > 10: score += 1

    priority_scores = {"Critical": 3, "High": 2, "Medium": 1, "Low": 0}
    score += priority_scores.get(row["Priority_Level"], 0)

    if row["Category"] == "Hazardous Materials": score += 2
    elif row["Category"] == "Cold Chain": score += 1

    return min(round(score, 1), 10)


@tool
def scan_cargo(query: str) -> str:
    """Scans all cargo containers and returns those below 40% capacity utilization."""
    df = pd.read_csv("inventory.csv")
    df["Utilization_Pct"] = (df["Current_Load"] / df["Max_Capacity"]) * 100
    low = df[df["Utilization_Pct"] < 40].copy()

    if low.empty:
        return "All containers are operating at sufficient capacity. No alerts."

    result = "CAPACITY ALERT — CONTAINERS BELOW 40%:\n\n"
    for _, row in low.iterrows():
        result += (
            f"- {row['Cargo_ID']} | {row['Description']}\n"
            f"  Location  : {row['Location']}\n"
            f"  Load      : {row['Current_Load']}/{row['Max_Capacity']} "
            f"({row['Utilization_Pct']:.1f}%)\n"
            f"  Priority  : {row['Priority_Level']}\n"
            f"  Cost      : ${row['Freight_Cost_USD']:,}\n\n"
        )
    return result


@tool
def forecast_capacity(cargo_id: str) -> str:
    """Forecasts days until a container reaches full capacity. Use container name like MAERSK-COLD-01 or keywords like 'vaccine', 'diamonds', 'singapore'."""
    df = pd.read_csv("inventory.csv")

    item = df[df["Cargo_ID"].str.upper() == cargo_id.upper()]

    if item.empty:
        item = df[
            df["Description"].str.lower().str.contains(cargo_id.lower()) |
            df["Location"].str.lower().str.contains(cargo_id.lower()) |
            df["Category"].str.lower().str.contains(cargo_id.lower()) |
            df["Cargo_ID"].str.lower().str.contains(cargo_id.lower())
        ]

    if item.empty:
        return f"No container found matching '{cargo_id}'."

    results = ""
    for _, row in item.head(3).iterrows():
        remaining = row["Max_Capacity"] - row["Current_Load"]
        days_to_full = remaining / row["Daily_Throughput"] if row["Daily_Throughput"] > 0 else 999
        utilization = (row["Current_Load"] / row["Max_Capacity"]) * 100

        try:
            inspected = datetime.strptime(str(row["Last_Inspected"]), "%Y-%m-%d")
            days_since = (datetime.now() - inspected).days
        except:
            days_since = 0

        risk = calculate_risk_score(row, days_since)

        if utilization > 90: status = "CRITICAL"
        elif utilization > 70: status = "WARNING"
        else: status = "NORMAL"

        results += (
            f"FORECAST — {row['Cargo_ID']}\n"
            f"{'=' * 35}\n"
            f"Description : {row['Description']}\n"
            f"Location    : {row['Location']}\n"
            f"Load        : {row['Current_Load']}/{row['Max_Capacity']} units\n"
            f"Utilization : {utilization:.1f}%\n"
            f"Throughput  : {row['Daily_Throughput']} units/day\n"
            f"Days to Full: {days_to_full:.1f} days\n"
            f"Cost        : ${row['Freight_Cost_USD']:,}\n"
            f"Priority    : {row['Priority_Level']}\n"
            f"Inspected   : {row['Last_Inspected']} ({days_since} days ago)\n"
            f"Risk Score  : {risk}/10\n"
            f"Status      : {status}\n\n"
        )
    return results


@tool
def prioritize_operations(query: str) -> str:
    """Prioritizes containers by urgency. Can filter by shipping line (MAERSK, COSCO, MSC etc), location, or category."""
    df = pd.read_csv("inventory.csv")
    df["Utilization_Pct"] = (df["Current_Load"] / df["Max_Capacity"]) * 100
    df["Days_To_Full"] = (df["Max_Capacity"] - df["Current_Load"]) / df["Daily_Throughput"]

    keywords = query.lower()
    for line in ["maersk", "evergreen", "cosco", "msc", "hapag", "cma", "one"]:
        if line in keywords:
            df = df[df["Cargo_ID"].str.lower().str.startswith(line)]
            break
    else:
        for cat in ["cold chain", "hazardous", "heavy goods", "high value", "general"]:
            if cat in keywords:
                df = df[df["Category"].str.lower().str.contains(cat)]
                break
        else:
            for loc in ["singapore", "rotterdam", "hamburg", "dubai", "shanghai", "los angeles", "felixstowe"]:
                if loc in keywords:
                    df = df[df["Location"].str.lower().str.contains(loc)]
                    break

    critical = df[df["Utilization_Pct"] > 90].sort_values("Utilization_Pct", ascending=False).head(5)
    warning = df[(df["Utilization_Pct"] > 70) & (df["Utilization_Pct"] <= 90)].sort_values("Utilization_Pct", ascending=False).head(5)
    normal = df[df["Utilization_Pct"] <= 70].sort_values("Utilization_Pct", ascending=False).head(5)

    result = "OPERATIONAL PRIORITY REPORT\n"
    result += "=" * 40 + "\n\n"

    if not critical.empty:
        result += "CRITICAL — IMMEDIATE ACTION\n"
        result += "-" * 30 + "\n"
        for _, row in critical.iterrows():
            result += (
                f"  {row['Cargo_ID']} | {row['Description']}\n"
                f"  {row['Utilization_Pct']:.1f}% full | "
                f"Full in {row['Days_To_Full']:.1f} days | "
                f"Priority: {row['Priority_Level']}\n\n"
            )

    if not warning.empty:
        result += "WARNING — MONITOR CLOSELY\n"
        result += "-" * 30 + "\n"
        for _, row in warning.iterrows():
            result += (
                f"  {row['Cargo_ID']} | {row['Description']}\n"
                f"  {row['Utilization_Pct']:.1f}% full | "
                f"Full in {row['Days_To_Full']:.1f} days\n\n"
            )

    if not normal.empty:
        result += "NORMAL — NO ACTION NEEDED\n"
        result += "-" * 30 + "\n"
        for _, row in normal.iterrows():
            result += f"  {row['Cargo_ID']} | {row['Utilization_Pct']:.1f}% full\n"

    return result


@tool
def assess_risk(query: str) -> str:
    """Calculates risk scores for all containers based on utilization, inspection date, priority and category."""
    df = pd.read_csv("inventory.csv")
    df["Utilization_Pct"] = (df["Current_Load"] / df["Max_Capacity"]) * 100

    risk_data = []
    for _, row in df.iterrows():
        try:
            inspected = datetime.strptime(str(row["Last_Inspected"]), "%Y-%m-%d")
            days_since = (datetime.now() - inspected).days
        except:
            days_since = 0

        risk = calculate_risk_score(row, days_since)
        risk_data.append({
            "Cargo_ID": row["Cargo_ID"],
            "Description": row["Description"],
            "Risk_Score": risk,
            "Utilization": row["Utilization_Pct"],
            "Days_Since": days_since,
            "Priority": row["Priority_Level"],
            "Cost": row["Freight_Cost_USD"]
        })

    risk_df = pd.DataFrame(risk_data).sort_values("Risk_Score", ascending=False)
    high = risk_df[risk_df["Risk_Score"] >= 7].head(5)
    med = risk_df[(risk_df["Risk_Score"] >= 4) & (risk_df["Risk_Score"] < 7)].head(5)

    result = "RISK ASSESSMENT REPORT\n"
    result += "=" * 40 + "\n\n"

    if not high.empty:
        result += "HIGH RISK — IMMEDIATE ATTENTION\n"
        result += "-" * 30 + "\n"
        for _, row in high.iterrows():
            result += (
                f"  {row['Cargo_ID']} | {row['Description']}\n"
                f"  Risk: {row['Risk_Score']}/10 | "
                f"Util: {row['Utilization']:.1f}% | "
                f"Inspected: {row['Days_Since']} days ago\n"
                f"  Freight at Risk: ${row['Cost']:,}\n\n"
            )

    if not med.empty:
        result += "MEDIUM RISK — MONITOR\n"
        result += "-" * 30 + "\n"
        for _, row in med.iterrows():
            result += (
                f"  {row['Cargo_ID']} | Risk: {row['Risk_Score']}/10 | "
                f"Util: {row['Utilization']:.1f}%\n"
            )

    return result


@tool
def fleet_efficiency(query: str) -> str:
    """Calculates overall fleet efficiency, total freight value, inspection compliance and operational summary."""
    df = pd.read_csv("inventory.csv")
    df["Utilization_Pct"] = (df["Current_Load"] / df["Max_Capacity"]) * 100

    avg_util = df["Utilization_Pct"].mean()
    total = len(df)
    critical = len(df[df["Utilization_Pct"] > 90])
    warning = len(df[(df["Utilization_Pct"] > 70) & (df["Utilization_Pct"] <= 90)])
    normal = len(df[df["Utilization_Pct"] <= 70])
    total_cost = df["Freight_Cost_USD"].sum()
    critical_cost = df[df["Utilization_Pct"] > 90]["Freight_Cost_USD"].sum()

    overdue = []
    for _, row in df.iterrows():
        try:
            inspected = datetime.strptime(str(row["Last_Inspected"]), "%Y-%m-%d")
            days_since = (datetime.now() - inspected).days
            if days_since > 20:
                overdue.append(f"{row['Cargo_ID']} ({days_since}d ago)")
        except:
            pass

    if avg_util < 60: rating = "POOR"
    elif avg_util < 70: rating = "BELOW OPTIMAL"
    elif avg_util <= 85: rating = "OPTIMAL"
    else: rating = "OVERLOADED"

    result = (
        f"FLEET EFFICIENCY REPORT\n"
        f"{'=' * 40}\n\n"
        f"Avg Utilization : {avg_util:.1f}% — {rating}\n"
        f"Critical        : {critical}/{total} containers\n"
        f"Warning         : {warning}/{total} containers\n"
        f"Normal          : {normal}/{total} containers\n\n"
        f"Total Fleet Value   : ${total_cost:,}\n"
        f"Value at Risk       : ${critical_cost:,}\n\n"
        f"Overdue Inspections : {len(overdue)}\n"
    )

    if overdue:
        for c in overdue[:5]:
            result += f"  - {c}\n"

    return result


@tool
def inspection_alerts(query: str) -> str:
    """Returns all containers overdue for inspection based on last inspection date."""
    df = pd.read_csv("inventory.csv")

    alerts = []
    for _, row in df.iterrows():
        try:
            inspected = datetime.strptime(str(row["Last_Inspected"]), "%Y-%m-%d")
            days_since = (datetime.now() - inspected).days
            alerts.append({
                "Cargo_ID": row["Cargo_ID"],
                "Description": row["Description"],
                "Days_Since": days_since,
                "Priority": row["Priority_Level"],
                "Location": row["Location"]
            })
        except:
            pass

    alerts_df = pd.DataFrame(alerts).sort_values("Days_Since", ascending=False)
    overdue = alerts_df[alerts_df["Days_Since"] > 20]

    if overdue.empty:
        return "All containers inspected within 20 days. Compliance is good."

    result = f"INSPECTION ALERTS — {len(overdue)} overdue\n"
    result += "=" * 40 + "\n\n"

    for _, row in overdue.iterrows():
        if row["Days_Since"] > 30: urgency = "CRITICAL OVERDUE"
        elif row["Days_Since"] > 25: urgency = "HIGH OVERDUE"
        else: urgency = "OVERDUE"

        result += (
            f"  {urgency} — {row['Cargo_ID']}\n"
            f"  {row['Description']}\n"
            f"  {row['Days_Since']} days since inspection | "
            f"Priority: {row['Priority']}\n\n"
        )

    return result