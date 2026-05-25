import streamlit as st
import json
import uuid
import os
from datetime import datetime
from mistralai import Mistral

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
        font-style: italic;
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
        "full_description": "PayFlow Africa enables businesses and individuals to send money across 30+ African countries in seconds using stablecoin rails.",
        "category": "FinTech",
        "target_funding": "$2M",
        "current_stage": "Seed",
        "team_size": 8,
        "target_market": "MENA, Sub-Saharan Africa",
        "competition_analysis": "Competing with M-Pesa and WorldRemit.",
        "revenue_model": "Transaction fee + API licensing",
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
        "competition_analysis": "Targets underserved hospitals.",
        "revenue_model": "SaaS subscription",
        "current_customers": "45 hospitals",
        "financial_projections": "$1.8M ARR",
        "website_url": "",
        "pitch_deck_url": "",
        "business_plan": "Expand to India",
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
    st.session_state.api_key = os.environ.get("l1H8pIdvNALk0aNxI1CP6SL0hwJHA1YK", "")

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
    "Profitable",
]


def get_categories():
    return sorted(set(s["category"] for s in st.session_state.startups))


def get_stages():
    return sorted(
        set(s["current_stage"] for s in st.session_state.startups),
        key=lambda x: STAGE_ORDER.index(x) if x in STAGE_ORDER else 99,
    )


# ─────────────────────────────────────────────
# AI Matching
# ─────────────────────────────────────────────
def run_ai_match(investor: dict, top_k: int) -> dict:

    client = Mistral(api_key=st.session_state.api_key)

    startup_summaries = []

    for i, s in enumerate(st.session_state.startups):
        startup_summaries.append(f"""
[{i+1}] ID:{s['id']}
Name:{s['project_name']}
Category:{s['category']}
Stage:{s['current_stage']}
Funding:{s['target_funding']}
Team:{s['team_size']}
Market:{s['target_market']}
Revenue:{s['revenue_model']}
Customers:{s.get('current_customers','n/a')}
Competition:{s.get('competition_analysis','n/a')}
Financials:{s.get('financial_projections','n/a')}
Description:{s['full_description']}
""")

    prompt = f"""
You are a senior startup investment analyst.

Analyze the startups and recommend the best
{min(top_k, len(st.session_state.startups))}
matches for this investor.

INVESTOR PROFILE:
Name: {investor['name']}
Investment Focus: {investor['focus']}
Preferred Stage: {investor['stage']}
Ticket Size: {investor['ticket']}
Preferred Markets: {investor.get('markets', 'Any')}
Risk Appetite: {investor.get('risk', 'Medium')}
Sectors to Avoid: {investor.get('avoid', 'None')}
Notes: {investor.get('notes', 'None')}

STARTUPS DATABASE:
{''.join(startup_summaries)}

Return ONLY valid JSON:

{{
  "matches":[
    {{
      "startup_id":"<id>",
      "startup_name":"<name>",
      "match_score":95,
      "match_summary":"summary",
      "key_strengths":["s1","s2"],
      "key_risks":["r1","r2"],
      "recommendation":"recommendation"
    }}
  ],
  "overall_analysis":"summary"
}}
"""

    response = client.chat.complete(
        model="mistral-large-latest",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3,
        max_tokens=2000,
    )

    raw = response.choices[0].message.content.strip()

    raw = raw.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(raw)

    except Exception:
        return {
            "matches": [],
            "overall_analysis": raw
        }


# ─────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────
with st.sidebar:

    st.markdown("## 🚀 VentureMatch")
    st.markdown("AI-powered startup–investor matching platform")

    st.divider()

    st.markdown("### 🔑 Mistral API Key")

    api_input = st.text_input(
        "API Key",
        value=st.session_state.api_key,
        type="password",
        placeholder="Your Mistral API key...",
        label_visibility="collapsed",
    )

    if st.button("Save Key", use_container_width=True):
        st.session_state.api_key = api_input
        st.success("Key saved!")

    if st.session_state.api_key:
        st.success("✅ API key connected")
    else:
        st.warning("⚠️ Add your Mistral API key")

    st.divider()

    startups = st.session_state.startups

    st.markdown("### 📊 Database Stats")

    col1, col2 = st.columns(2)

    col1.metric("Startups", len(startups))
    col2.metric("Categories", len(get_categories()))

    col1.metric("Stages", len(get_stages()))

    avg_team = (
        sum(s["team_size"] for s in startups)
        // max(len(startups), 1)
    )

    col2.metric("Avg Team", avg_team)

    st.divider()

    if st.button("🔄 Reset Demo Data", use_container_width=True):
        st.session_state.startups = DEMO_STARTUPS.copy()
        st.session_state.match_results = None
        st.success("Reset complete!")
        st.rerun()

# ─────────────────────────────────────────────
# Main UI
# ─────────────────────────────────────────────
st.markdown("# 🚀 VentureMatch")
st.markdown("*AI-powered startup–investor matching · powered by Mistral AI*")

tab_db, tab_add, tab_match = st.tabs([
    "📋 Startup Database",
    "➕ Add Startup",
    "🤖 AI Match"
])

# ─────────────────────────────────────────────
# TAB 1
# ─────────────────────────────────────────────
with tab_db:

    st.markdown("### All Startups")

    startups = st.session_state.startups

    if not startups:
        st.info("No startups available.")

    else:

        search = st.text_input(
            "Search",
            placeholder="Search startup..."
        )

        filtered = startups

        if search:
            q = search.lower()

            filtered = [
                s for s in filtered
                if q in s["project_name"].lower()
                or q in s["full_description"].lower()
            ]

        st.caption(f"Showing {len(filtered)} startups")

        for s in filtered:

            icon = CATEGORY_COLORS.get(s["category"], "⚫")

            with st.expander(
                f"{icon} {s['project_name']} · {s['current_stage']}"
            ):

                c1, c2 = st.columns(2)

                c1.markdown(f"**Category:** {s['category']}")
                c1.markdown(f"**Funding:** {s['target_funding']}")
                c1.markdown(f"**Market:** {s['target_market']}")

                c2.markdown(f"**Team Size:** {s['team_size']}")
                c2.markdown(f"**Revenue:** {s['revenue_model']}")
                c2.markdown(f"**Customers:** {s['current_customers']}")

                st.markdown(f"**Description:** {s['full_description']}")

# ─────────────────────────────────────────────
# TAB 2
# ─────────────────────────────────────────────
with tab_add:

    st.markdown("### Add Startup")

    with st.form("add_startup_form", clear_on_submit=True):

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
                or not target_market
                or not revenue_model
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
                    "competition_analysis": "",
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
with tab_match:

    st.markdown("### 🤖 AI Investor Matching")

    if not st.session_state.api_key:
        st.warning("Please add your Mistral API key.")

    with st.form("investor_form"):

        c1, c2 = st.columns(2)

        investor_name = c1.text_input("Investor Name *")

        investment_focus = c2.text_input(
            "Investment Focus *"
        )

        c3, c4 = st.columns(2)

        investment_stage = c3.selectbox(
            "Preferred Stage *",
            [
                "",
                "Pre-Seed",
                "Seed",
                "Series A",
                "Series B+",
                "Any Stage"
            ]
        )

        ticket_size = c4.text_input("Ticket Size *")

        preferred_markets = st.text_input(
            "Preferred Markets"
        )

        top_k = st.selectbox(
            "Matches to Return",
            [3, 4, 5],
            index=2
        )

        submit_match = st.form_submit_button(
            "🤖 Find Matches",
            use_container_width=True,
            disabled=not st.session_state.api_key
        )

    if submit_match:

        investor = {
            "name": investor_name,
            "focus": investment_focus,
            "stage": investment_stage,
            "ticket": ticket_size,
            "markets": preferred_markets,
        }

        with st.spinner("Analyzing startups..."):

            try:

                result = run_ai_match(
                    investor,
                    top_k
                )

                st.session_state.match_results = result

            except Exception as e:

                st.error(f"Error: {e}")

    # Results
    if st.session_state.match_results:

        data = st.session_state.match_results

        st.divider()

        st.markdown("## 🎯 Match Results")

        if data.get("overall_analysis"):

            st.info(data["overall_analysis"])

        matches = data.get("matches", [])

        for i, m in enumerate(matches):

            score = m.get("match_score", 0)

            with st.expander(
                f"#{i+1} — {m['startup_name']} ({score}/100)",
                expanded=(i == 0)
            ):

                st.metric("Match Score", f"{score}%")

                st.markdown(
                    f"**Summary:** {m.get('match_summary','')}"
                )

                col1, col2 = st.columns(2)

                with col1:

                    st.markdown("### ✅ Strengths")

                    for s in m.get("key_strengths", []):

                        st.markdown(f"- {s}")

                with col2:

                    st.markdown("### ⚠️ Risks")

                    for r in m.get("key_risks", []):

                        st.markdown(f"- {r}")

                st.markdown(
                    f"""
<div class="rec-box">
💡 <strong>Recommendation:</strong>
{m.get('recommendation','')}
</div>
""",
                    unsafe_allow_html=True,
                )

        st.download_button(
            label="⬇️ Export JSON",
            data=json.dumps(data, indent=2),
            file_name="venturematch_results.json",
            mime="application/json",
        )
