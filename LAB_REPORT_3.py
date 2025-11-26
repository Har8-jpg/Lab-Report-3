import json
from typing import List, Dict, Any
import operator
import streamlit as st

# --- RULE ENGINE -----------------------------------------------------
OPS = {
    "==": operator.eq,
    "!=": operator.ne,
    ">": operator.gt,
    ">=": operator.ge,
    "<": operator.lt,
    "<=": operator.le,
    "in": lambda a, b: a in b,
    "not_in": lambda a, b: a not in b,
}

DEFAULT_RULES = [
    {
        "name": "Top merit candidate",
        "priority": 100,
        "conditions": [
            ["cgpa", ">=", 3.7],
            ["co_curricular_score", ">=", 80],
            ["family_income", "<=", 8000],
            ["disciplinary_actions", "==", 0]
        ],
        "action": {"decision": "AWARD_FULL",
                   "reason": "Excellent academic & co-curricular performance with acceptable need"}
    },
    {
        "name": "Good candidate - partial scholarship",
        "priority": 80,
        "conditions": [
            ["cgpa", ">=", 3.3],
            ["co_curricular_score", ">=", 60],
            ["family_income", "<=", 12000],
            ["disciplinary_actions", "<=", 1]
        ],
        "action": {"decision": "AWARD_PARTIAL",
                   "reason": "Good academic & involvement record with moderate need"}
    },
    {
        "name": "Need-based review",
        "priority": 70,
        "conditions": [
            ["cgpa", ">=", 2.5],
            ["family_income", "<=", 4000]
        ],
        "action": {"decision": "REVIEW",
                   "reason": "High need but borderline academic score"}
    },
    {
        "name": "Low CGPA – not eligible",
        "priority": 95,
        "conditions": [["cgpa", "<", 2.5]],
        "action": {"decision": "REJECT",
                   "reason": "CGPA below minimum scholarship requirement"}
    },
    {
        "name": "Serious disciplinary record",
        "priority": 90,
        "conditions": [["disciplinary_actions", ">=", 2]],
        "action": {"decision": "REJECT",
                   "reason": "Too many disciplinary records"}
    }
]

def evaluate_condition(facts, cond):
    field, op, value = cond
    return field in facts and op in OPS and OPS[op](facts[field], value)

def rule_matches(facts, rule):
    return all(evaluate_condition(facts, c) for c in rule["conditions"])

def run_rules(facts, rules):
    matched = [r for r in rules if rule_matches(facts, r)]
    if not matched:
        return {"decision": "REVIEW", "reason": "No rule matched"}, []
    matched_sorted = sorted(matched, key=lambda r: r["priority"], reverse=True)
    return matched_sorted[0]["action"], matched_sorted

# --- PAGE CONFIG -----------------------------------------------------
st.set_page_config(page_title="Scholarship Eligibility System",
                   layout="wide")

# --- PAGE HEADER -----------------------------------------------------
st.markdown("""
<h1 style='text-align:center; color:#2c3e50;'>
🎓 Scholarship Eligibility Rule-Based System
</h1>
<p style='text-align:center; font-size:17px; color:gray;'>
A decision support tool powered by rule-based reasoning.
</p>
""", unsafe_allow_html=True)

st.write("")

# --- SIDEBAR ---------------------------------------------------------
with st.sidebar:
    st.markdown("### 📝 Applicant Information")
    st.caption("Fill in the details below.")

    cgpa = st.number_input("CGPA", 0.0, 4.0, step=0.01, value=3.5)
    income = st.number_input("Family Income (RM)", 0, step=100, value=6000)
    co_curricular = st.number_input("Co-curricular Score (0–100)", 0, 100, step=1, value=70)
    service_hours = st.number_input("Community Service Hours", 0, step=1, value=30)
    semester = st.number_input("Current Semester", 1, 10, step=1, value=4)
    disciplinary = st.number_input("Disciplinary Actions", 0, step=1, value=0)

    st.markdown("---")
    st.markdown("### ⚙ Rule Editor (JSON)")
    rules_json = st.text_area(
        "Modify the rules if needed:",
        value=json.dumps(DEFAULT_RULES, indent=2),
        height=350
    )
    run = st.button("🚀 Evaluate Applicant", type="primary")

# --- FACTS -----------------------------------------------------------
facts = {
    "cgpa": float(cgpa),
    "family_income": float(income),
    "co_curricular_score": int(co_curricular),
    "community_service_hours": int(service_hours),
    "semester": int(semester),
    "disciplinary_actions": int(disciplinary),
}

st.markdown("## 📌 Applicant Data Summary")
st.json(facts)

st.markdown("---")

# --- EVALUATION ------------------------------------------------------
try:
    rules = json.loads(rules_json)
except:
    st.error("Invalid JSON. Reverted to default rules.")
    rules = DEFAULT_RULES

if run:
    action, matched_rules = run_rules(facts, rules)

    # --- DECISION CARD ------------------------------------------------
    decision_color = {
        "AWARD_FULL": "#27ae60",
        "AWARD_PARTIAL": "#2980b9",
        "REJECT": "#c0392b",
        "REVIEW": "#f39c12"
    }

    col1, col2 = st.columns([1.1, 1])

    with col1:
        st.markdown(f"""
        <div style="
            padding:25px;
            border-radius:15px;
            background:{decision_color[action['decision']]};
            color:white;
            font-size:20px;">
            <b>Decision:</b> {action['decision']}<br>
            <span style="font-size:16px;">{action['reason']}</span>
        </div>
        """, unsafe_allow_html=True)

    # --- MATCHED RULES ------------------------------------------------
    with col2:
        st.markdown("### 🔍 Matched Rules (by priority)")
        if matched_rules:
            for r in matched_rules:
                with st.expander(f"📘 {r['name']}  — priority {r['priority']}"):
                    st.markdown("**Action:**")
                    st.code(json.dumps(r["action"], indent=2))

                    st.markdown("**Conditions:**")
                    st.table({"Field": [c[0] for c in r["conditions"]],
                              "Operator": [c[1] for c in r["conditions"]],
                              "Value": [c[2] for c in r["conditions"]]})
        else:
            st.info("No rules matched.")

else:
    st.info("Enter applicant details and click **Evaluate** to begin.")