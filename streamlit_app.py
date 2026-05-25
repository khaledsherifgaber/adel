import streamlit as st
import json
import uuid
import os
import requests
from datetime import datetime

# ─────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="VentureMatch — AI Startup Matching",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# Custom CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    .main { padding-top: 1rem; }

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 20px;
    }

    div[data-testid="metric-container"] {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 14px 20px;
    }

    .rec-box {
        background: #eff6ff;
        border-left: 4px solid #3b82f6;
        border-radius: 0 8px 8px 0;
        padding: 12px 16px;
        margin-top: 12px;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Demo data
# ─────────────────────────────────────────────
DEMO_STARTUPS = [
    {
        "id": "s1",
        "project_name": "PayFlow Africa",
        "tagline": "Instant cross-border payments for Africa",
        "full_description": "PayFlow Africa enables businesses and individuals to send money across Africa using stablecoin rails.",
        "category": "FinTech",
        "target_funding": "$2M",
        "current_stage": "Seed",
        "team_size": 8,
        "target_market": "MENA, Africa",
        "competition_analysis": "Competing with M-Pesa and WorldRemit.",
        "revenue_model": "Transaction fees",
        "current_customers": "1,200 SMEs",
        "financial_projections": "$800K ARR",
        "website_url": "",
        "pitch_deck_url": "",
        "business_plan": "Expand to 10 corridors",
        "product_demo_url": "",
        "created_at": datetime.utcnow().isoformat(),
    },
    {
        "id": "s2",
        "project_name": "MediScan AI",
        "tagline": "AI radiology for underserved hospitals",
        "full_description": "AI-powered radiology analysis for hospitals in emerging markets.",
        "category": "HealthTech",
        "target_funding": "$3M",
        "current_stage": "Series A",
        "team_size": 12,
        "target_market": "Middle East, Africa",
        "competition_analysis": "Competing with Aidoc.",
        "revenue_model": "SaaS subscription",
        "current_customers": "45 hospitals",
        "financial_projections": "$1.8M ARR",
        "website_url": "",
        "pitch_deck_url": "",
        "business_plan": "Expand globally",
        "product_demo_url": "",
        "created_at": datetime.utcnow().isoformat(),
    },
]

# ─────────────────────────────────────────────
# Session state
# ─────────────────────────────────────────────
if "startups" not in st.session_state:
    st.session_state.startups = DEMO_STARTUPS.copy()

if "match_results" not in st.session_state:
    st.session_state.match_results = None

if "api_key" not in st.session_state:
    st.session_state.api_key = ""

# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────
CATEGORY_COLORS = {
    "FinTech": "🟦",
    "HealthTech": "🟥",
    "EdTech": "🟨",
    "AgriTech": "🟩",
    "CleanTech": "🟦",
    "Logistics": "🟪",
    "SaaS": "🔵",
    "E-Commerce": "🟠",
    "AI/ML": "⚪",
    "Other": "⚫",
}

STAGE_ORDER = [
    "Idea",
    "Pre-Seed",
    "Seed",
    "Series A",
    "Series B",
    "Profitable"
]

def get_categories():
    return sorted(set(s["category"] for s in st.session_state.startups))

def get_stages():
    return sorted(
        set(s["current_stage"] for s in st.session_state.startups),
        key=lambda x: STAGE_ORDER.index(x)
        if x in STAGE_ORDER else 99,
    )

# ─────────────────────────────────────────────
# Mistral AI Matching
# ─────────────────────────────────────────────
def run_ai_match(investor: dict, top_k: int):

    startup_summaries = []

    for i, s in enumerate(st.session_state.startups):
        startup_summaries.append(f"""
[{i+1}]
ID: {s['id']}
Name: {s['project_name']}
Category: {s['category']}
Stage: {s['current_stage']}
Funding: {s['target_funding']}
Team: {s['team_size']}
Market: {s['target_market']}
Revenue: {s['revenue_model']}
Customers: {s.get('current_customers', 'N/A')}
Competition: {s.get('competition_analysis', 'N/A')}
Financials: {s.get('financial_projections', 'N/A')}
Description: {s['full_description']}
""")

    prompt = f"""
You are a senior VC investment analyst.

Analyze the startups below and recommend the BEST {top_k} matches.

INVESTOR PROFILE:
Name: {investor['name']}
Investment Focus: {investor['focus']}
Preferred Stage: {investor['stage']}
Ticket Size: {investor['ticket']}
Preferred Markets: {investor.get('markets', 'Any')}
Risk Appetite: {investor.get('risk', 'Medium')}
Sectors to Avoid: {investor.get('avoid', 'None')}
Notes: {investor.get('notes', 'None')}

STARTUPS:
{''.join(startup_summaries)}

Return ONLY VALID JSON.

Format:
{{
  "matches": [
    {{
      "startup_id": "id",
      "startup_name": "name",
      "match_score": 90,
      "match_summary": "summary",
      "key_strengths": ["a", "b", "c"],
      "key_risks": ["a", "b"],
      "recommendation": "recommendation"
    }}
  ],
  "overall_analysis": "summary"
}}
"""

    headers = {
        "Authorization": f"Bearer {st.session_state.api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "mistral-large-latest",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.7,
        "max_tokens": 2000
    }

    response = requests.post(
        "https://api.mistral.ai/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=120
    )

    if response.status_code != 200:
        raise Exception(f"API Error: {response.text}")

    result = response.json()

    raw = result["choices"][0]["message"]["content"]

    raw = raw.replace("```json", "")
    raw = raw.replace("```", "")
    raw = raw.strip()

    return json.loads(raw)

# ─────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────
with st.sidebar:

    st.markdown("## 🚀 VentureMatch")
    st.markdown("AI startup-investor matching")

    st.divider()

    st.markdown("### 🔑 Mistral API Key")

    api_input = st.text_input(
        "API Key",
        value=st.session_state.api_key,
        type="password",
        placeholder="Enter Mistral API key",
        label_visibility="collapsed",
    )

    if st.button("Save API Key", use_container_width=True):
        st.session_state.api_key = api_input
        st.success("API Key saved!")

    if st.session_state.api_key:
        st.success("✅ API Connected")
    else:
        st.warning("⚠️ Add your Mistral API key")

    st.divider()

    startups = st.session_state.startups

    st.markdown("### 📊 Database Stats")

    c1, c2 = st.columns(2)

    c1.metric("Startups", len(startups))
    c2.metric("Categories", len(get_categories()))

    c1.metric("Stages", len(get_stages()))

    avg_team = (
        sum(s["team_size"] for s in startups)
        // max(len(startups), 1)
    )

    c2.metric("Avg Team", avg_team)

# ─────────────────────────────────────────────
# Main UI
# ─────────────────────────────────────────────
st.title("🚀 VentureMatch")
st.markdown("AI-powered startup-investor matching using Mistral AI")

tab1, tab2, tab3 = st.tabs([
    "📋 Database",
    "➕ Add Startup",
    "🤖 AI Match"
])

# ─────────────────────────────────────────────
# TAB 1
# ─────────────────────────────────────────────
with tab1:

    st.subheader("Startup Database")

    startups = st.session_state.startups

    for s in startups:

        icon = CATEGORY_COLORS.get(s["category"], "⚫")

        with st.expander(
            f"{icon} {s['project_name']} — {s['current_stage']}"
        ):

            c1, c2, c3 = st.columns(3)

            c1.markdown(f"**Category:** {s['category']}")
            c1.markdown(f"**Funding:** {s['target_funding']}")

            c2.markdown(f"**Stage:** {s['current_stage']}")
            c2.markdown(f"**Team:** {s['team_size']}")

            c3.markdown(f"**Market:** {s['target_market']}")

            st.markdown(f"### {s['tagline']}")
            st.write(s["full_description"])

            st.markdown("### Revenue Model")
            st.write(s["revenue_model"])

            st.markdown("### Competition")
            st.write(s["competition_analysis"])

# ─────────────────────────────────────────────
# TAB 2
# ─────────────────────────────────────────────
with tab2:

    st.subheader("Add Startup")

    with st.form("startup_form"):

        c1, c2 = st.columns(2)

        project_name = c1.text_input("Project Name *")

        category = c2.selectbox(
            "Category *",
            [
                "",
                "FinTech",
                "HealthTech",
                "EdTech",
                "AgriTech",
                "CleanTech",
                "Logistics",
                "SaaS",
                "E-Commerce",
                "AI/ML",
                "Other"
            ]
        )

        tagline = st.text_input("Tagline *")

        full_description = st.text_area(
            "Full Description *",
            height=120
        )

        c3, c4 = st.columns(2)

        target_funding = c3.text_input("Target Funding *")

        current_stage = c4.selectbox(
            "Current Stage *",
            [
                "",
                "Idea",
                "Pre-Seed",
                "Seed",
                "Series A",
                "Series B",
                "Profitable"
            ]
        )

        team_size = st.number_input(
            "Team Size",
            min_value=1,
            value=5
        )

        target_market = st.text_input("Target Market *")

        revenue_model = st.text_input("Revenue Model *")

        competition_analysis = st.text_area(
            "Competition Analysis",
            height=80
        )

        submitted = st.form_submit_button(
            "✅ Add Startup",
            use_container_width=True
        )

        if submitted:

            if (
                not project_name
                or not category
                or not tagline
                or not full_description
                or not target_funding
                or not current_stage
            ):
                st.error("Please fill all required fields.")
            else:

                new_startup = {
                    "id": str(uuid.uuid4()),
                    "project_name": project_name,
                    "tagline": tagline,
                    "full_description": full_description,
                    "category": category,
                    "target_funding": target_funding,
                    "current_stage": current_stage,
                    "team_size": int(team_size),
                    "target_market": target_market,
                    "revenue_model": revenue_model,
                    "competition_analysis": competition_analysis,
                    "current_customers": "",
                    "financial_projections": "",
                    "website_url": "",
                    "pitch_deck_url": "",
                    "business_plan": "",
                    "product_demo_url": "",
                    "created_at": datetime.utcnow().isoformat(),
                }

                st.session_state.startups.append(new_startup)

                st.success(f"{project_name} added successfully!")

# ─────────────────────────────────────────────
# TAB 3
# ─────────────────────────────────────────────
with tab3:

    st.subheader("🤖 AI Matching")

    with st.form("investor_form"):

        c1, c2 = st.columns(2)

        investor_name = c1.text_input("Investor Name *")

        investment_focus = c2.text_input(
            "Investment Focus *",
            placeholder="FinTech, AI, SaaS"
        )

        c3, c4 = st.columns(2)

        investment_stage = c3.selectbox(
            "Preferred Stage *",
            [
                "",
                "Pre-Seed",
                "Seed",
                "Series A",
                "Series B",
                "Any Stage"
            ]
        )

        ticket_size = c4.text_input(
            "Ticket Size *",
            placeholder="$100K - $2M"
        )

        c5, c6 = st.columns(2)

        preferred_markets = c5.text_input(
            "Preferred Markets"
        )

        risk_appetite = c6.selectbox(
            "Risk Appetite",
            ["Low", "Medium", "High"]
        )

        top_k = st.selectbox(
            "Number of Matches",
            [3, 4, 5],
            index=2
        )

        additional_notes = st.text_area(
            "Additional Notes"
        )

        submit_match = st.form_submit_button(
            "🚀 Find Matches",
            use_container_width=True,
            type="primary"
        )

    if submit_match:

        if not st.session_state.api_key:
            st.error("Please enter your Mistral API key.")
        else:

            investor = {
                "name": investor_name,
                "focus": investment_focus,
                "stage": investment_stage,
                "ticket": ticket_size,
                "markets": preferred_markets,
                "risk": risk_appetite,
                "notes": additional_notes,
            }

            with st.spinner("Analyzing startups..."):

                try:

                    result = run_ai_match(
                        investor,
                        top_k
                    )

                    st.session_state.match_results = result

                except Exception as e:
                    st.error(str(e))

    # Results
    if st.session_state.match_results:

        data = st.session_state.match_results

        st.divider()

        st.subheader("📈 Match Results")

        if data.get("overall_analysis"):
            st.info(data["overall_analysis"])

        matches = data.get("matches", [])

        for i, m in enumerate(matches):

            score = m.get("match_score", 0)

            with st.expander(
                f"#{i+1} {m['startup_name']} — {score}/100",
                expanded=(i == 0)
            ):

                c1, c2, c3 = st.columns(3)

                c1.metric("Match Score", score)

                st.markdown("### Summary")
                st.write(m.get("match_summary", ""))

                st.markdown("### ✅ Strengths")

                for s in m.get("key_strengths", []):
                    st.markdown(f"- {s}")

                st.markdown("### ⚠️ Risks")

                for r in m.get("key_risks", []):
                    st.markdown(f"- {r}")

                st.markdown(
                    f"""
                    <div class="rec-box">
                    💡 <strong>Recommendation:</strong>
                    {m.get('recommendation', '')}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        # Export
        st.download_button(
            label="⬇️ Export JSON",
            data=json.dumps(data, indent=2),
            file_name="venture_matches.json",
            mime="application/json",
            use_container_width=True
        )
