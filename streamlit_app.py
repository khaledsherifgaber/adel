import streamlit as st
import json
import uuid
import os
from datetime import datetime
from anthropic import Anthropic

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
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { border-radius: 8px; padding: 8px 20px; }

    div[data-testid="metric-container"] {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 14px 20px;
    }
    .match-card {
        background: #f0fdf4;
        border: 1px solid #bbf7d0;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
    }
    .score-badge {
        display: inline-block;
        background: #166534;
        color: white;
        border-radius: 50px;
        padding: 4px 16px;
        font-size: 14px;
        font-weight: 600;
        margin-bottom: 8px;
    }
    .startup-pill {
        display: inline-block;
        background: #e0f2fe;
        color: #0369a1;
        border-radius: 6px;
        padding: 2px 10px;
        font-size: 12px;
        margin: 2px;
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
        "full_description": "PayFlow Africa enables businesses and individuals to send money across 30+ African countries in seconds using stablecoin rails. Fees drop from 8% to under 1%, settlement from days to seconds.",
        "category": "FinTech",
        "target_funding": "$2M",
        "current_stage": "Seed",
        "team_size": 8,
        "target_market": "MENA, Sub-Saharan Africa",
        "competition_analysis": "Competing with M-Pesa, WorldRemit. Differentiated by stablecoin tech and 10x lower fees.",
        "revenue_model": "Transaction fee (0.5%) + enterprise API licensing",
        "current_customers": "1,200 SMEs, $400K monthly volume",
        "financial_projections": "$800K ARR by end of year 1",
        "website_url": "",
        "pitch_deck_url": "",
        "business_plan": "Expand to 10 corridors by Q3, targeting $5M monthly volume",
        "product_demo_url": "",
        "created_at": datetime.utcnow().isoformat(),
    },
    {
        "id": "s2",
        "project_name": "MediScan AI",
        "tagline": "AI radiology for underserved hospitals",
        "full_description": "MediScan AI provides hospitals in emerging markets with AI-powered radiology analysis. Our model detects 12 conditions from chest X-rays with 94% accuracy, working offline on low-cost hardware.",
        "category": "HealthTech",
        "target_funding": "$3M",
        "current_stage": "Series A",
        "team_size": 12,
        "target_market": "Middle East, Africa, Southeast Asia",
        "competition_analysis": "Global players like Aidoc focus on premium hospitals. We target tier-2/3 hospitals they ignore.",
        "revenue_model": "SaaS subscription $500/month per hospital + per-scan fee",
        "current_customers": "45 hospitals across Egypt, Nigeria, Kenya",
        "financial_projections": "$1.8M ARR, 65% gross margin",
        "website_url": "",
        "pitch_deck_url": "",
        "business_plan": "500 hospitals by 2026, entering India market",
        "product_demo_url": "",
        "created_at": datetime.utcnow().isoformat(),
    },
    {
        "id": "s3",
        "project_name": "FarmLink",
        "tagline": "Connecting smallholder farmers to premium markets",
        "full_description": "FarmLink is an AgriTech marketplace connecting 50,000+ smallholder farmers directly to supermarkets and exporters, eliminating 4-layer middlemen and increasing farmer income by 40%.",
        "category": "AgriTech",
        "target_funding": "$1.5M",
        "current_stage": "Pre-Seed",
        "team_size": 6,
        "target_market": "Egypt, Morocco, Kenya",
        "competition_analysis": "Traditional wholesale markets control 90% of trade. No direct digital competitor at our scale.",
        "revenue_model": "5% commission on transactions + logistics margin",
        "current_customers": "3,200 farmers, 15 supermarket chains",
        "financial_projections": "$200K GMV/month growing 20% MoM",
        "website_url": "",
        "pitch_deck_url": "",
        "business_plan": "Expand to 5 new crops, add financing product for farmers",
        "product_demo_url": "",
        "created_at": datetime.utcnow().isoformat(),
    },
    {
        "id": "s4",
        "project_name": "EduNest",
        "tagline": "Personalized Arabic-first learning for K-12",
        "full_description": "EduNest delivers adaptive, gamified learning in Arabic for students aged 6-18. Our AI tutor personalizes curriculum to each student's learning pace, covering Math, Science and English.",
        "category": "EdTech",
        "target_funding": "$2.5M",
        "current_stage": "Seed",
        "team_size": 15,
        "target_market": "MENA (Arabic-speaking)",
        "competition_analysis": "Khan Academy (English-first), Noon Academy (tutoring). We own the adaptive Arabic curriculum space.",
        "revenue_model": "B2C subscription $15/month + B2B school licenses",
        "current_customers": "18,000 active students, 30 schools",
        "financial_projections": "$450K ARR, targeting $2M by year 2",
        "website_url": "",
        "pitch_deck_url": "",
        "business_plan": "Launch in Saudi Arabia and UAE, add teacher tools",
        "product_demo_url": "",
        "created_at": datetime.utcnow().isoformat(),
    },
    {
        "id": "s5",
        "project_name": "GreenGrid",
        "tagline": "Modular solar microgrids for off-grid communities",
        "full_description": "GreenGrid deploys pre-financed solar microgrids in rural and off-grid communities. Pay-as-you-go electricity via lease-to-own model for communities with zero grid access.",
        "category": "CleanTech",
        "target_funding": "$5M",
        "current_stage": "Series A",
        "team_size": 20,
        "target_market": "Sub-Saharan Africa, Rural MENA",
        "competition_analysis": "M-KOPA (East Africa focus). GreenGrid targets MENA and West Africa with Arabic-language support.",
        "revenue_model": "PAYG energy subscription + carbon credits",
        "current_customers": "8,000 households, 12 communities powered",
        "financial_projections": "$1.2M ARR, eligible for $3M green bonds",
        "website_url": "",
        "pitch_deck_url": "",
        "business_plan": "50 communities by end of year, carbon credit revenue starting Q2",
        "product_demo_url": "",
        "created_at": datetime.utcnow().isoformat(),
    },
    {
        "id": "s6",
        "project_name": "LogiChain",
        "tagline": "Smart last-mile logistics for MENA e-commerce",
        "full_description": "LogiChain is a tech-enabled last-mile delivery platform. AI routing engine + 2,000+ gig couriers. 30% cheaper than incumbents with 98% on-time delivery rate.",
        "category": "Logistics",
        "target_funding": "$4M",
        "current_stage": "Series A",
        "team_size": 25,
        "target_market": "Egypt, KSA, UAE",
        "competition_analysis": "Aramex, Fetchr are expensive and slow. LogiChain is 30% cheaper with 98% on-time delivery rate.",
        "revenue_model": "Per-delivery fee + SaaS dashboard for merchants",
        "current_customers": "120 e-commerce brands, 50,000 deliveries/month",
        "financial_projections": "$2.5M ARR, path to profitability in 14 months",
        "website_url": "",
        "pitch_deck_url": "",
        "business_plan": "Enter KSA market, launch white-label returns management",
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
    st.session_state.api_key = os.environ.get("ANTHROPIC_API_KEY", "")

# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────
CATEGORY_COLORS = {
    "FinTech": "🟦", "HealthTech": "🟥", "EdTech": "🟨",
    "AgriTech": "🟩", "CleanTech": "🟦", "Logistics": "🟪",
    "SaaS": "🔵", "E-Commerce": "🟠", "AI/ML": "⚪", "Other": "⚫",
}
STAGE_ORDER = ["Idea", "Pre-Seed", "Seed", "Series A", "Series B", "Profitable"]


def get_categories():
    return sorted(set(s["category"] for s in st.session_state.startups))


def get_stages():
    return sorted(
        set(s["current_stage"] for s in st.session_state.startups),
        key=lambda x: STAGE_ORDER.index(x) if x in STAGE_ORDER else 99,
    )


def run_ai_match(investor: dict, top_k: int) -> dict:
    client = Anthropic(api_key=st.session_state.api_key)

    startup_summaries = []
    for i, s in enumerate(st.session_state.startups):
        startup_summaries.append(f"""
[{i+1}] ID:{s['id']} | Name:{s['project_name']} | Category:{s['category']} | Stage:{s['current_stage']}
Funding:{s['target_funding']} | Team:{s['team_size']} | Market:{s['target_market']}
Revenue:{s['revenue_model']} | Customers:{s.get('current_customers','n/a')}
Competition:{s.get('competition_analysis','n/a')} | Financials:{s.get('financial_projections','n/a')}
Description:{s['full_description'][:300]}...""")

    prompt = f"""You are a senior startup investment analyst. Analyze the startups and recommend the best {min(top_k, len(st.session_state.startups))} matches for this investor.

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

Return ONLY valid JSON (no markdown, no extra text):
{{"matches":[{{"startup_id":"<id>","startup_name":"<name>","match_score":<0-100>,"match_summary":"<2-3 sentence explanation>","key_strengths":["<s1>","<s2>","<s3>"],"key_risks":["<r1>","<r2>"],"recommendation":"<one clear action sentence>"}}],"overall_analysis":"<2-3 sentence strategy summary for this investor>"}}"""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = message.content[0].text.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(raw)


# ─────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🚀 VentureMatch")
    st.markdown("AI-powered startup–investor matching platform")
    st.divider()

    st.markdown("### 🔑 Anthropic API Key")
    api_input = st.text_input(
        "API Key",
        value=st.session_state.api_key,
        type="password",
        placeholder="sk-ant-...",
        label_visibility="collapsed",
    )
    if st.button("Save Key", use_container_width=True):
        st.session_state.api_key = api_input
        st.success("Key saved!")

    if st.session_state.api_key:
        st.success("✅ API key connected")
    else:
        st.warning("⚠️ Add your Anthropic API key to enable AI matching")

    st.divider()
    st.markdown("### 📊 Database Stats")
    startups = st.session_state.startups
    col1, col2 = st.columns(2)
    col1.metric("Startups", len(startups))
    col2.metric("Categories", len(get_categories()))
    col1.metric("Stages", len(get_stages()))
    col2.metric("Avg Team", f"{sum(s['team_size'] for s in startups) // max(len(startups),1)}")

    st.divider()
    if st.button("🔄 Reset to Demo Data", use_container_width=True):
        st.session_state.startups = DEMO_STARTUPS.copy()
        st.session_state.match_results = None
        st.success("Reset to demo data!")
        st.rerun()

# ─────────────────────────────────────────────
# Main tabs
# ─────────────────────────────────────────────
st.markdown("# 🚀 VentureMatch")
st.markdown("*AI-powered startup–investor matching · powered by Claude*")
st.markdown("")

tab_db, tab_add, tab_match = st.tabs(["📋 Startup Database", "➕ Add Startup", "🤖 AI Match"])

# ══════════════════════════════════════════════
# TAB 1 — DATABASE
# ══════════════════════════════════════════════
with tab_db:
    st.markdown("### All Startups")

    startups = st.session_state.startups

    if not startups:
        st.info("No startups yet. Add some or reset to demo data.")
    else:
        # Filters
        fcol1, fcol2, fcol3 = st.columns(3)
        with fcol1:
            filter_cat = st.multiselect("Filter by Category", get_categories(), placeholder="All categories")
        with fcol2:
            filter_stage = st.multiselect("Filter by Stage", get_stages(), placeholder="All stages")
        with fcol3:
            search = st.text_input("Search", placeholder="Search by name or keyword...")

        filtered = startups
        if filter_cat:
            filtered = [s for s in filtered if s["category"] in filter_cat]
        if filter_stage:
            filtered = [s for s in filtered if s["current_stage"] in filter_stage]
        if search:
            q = search.lower()
            filtered = [s for s in filtered if q in s["project_name"].lower()
                        or q in s["tagline"].lower() or q in s["full_description"].lower()]

        st.caption(f"Showing {len(filtered)} of {len(startups)} startups")
        st.markdown("")

        for s in filtered:
            icon = CATEGORY_COLORS.get(s["category"], "⚫")
            with st.expander(f"{icon} **{s['project_name']}** · {s['current_stage']} · {s['target_funding']} · _{s['tagline']}_"):
                col_a, col_b, col_c = st.columns(3)
                col_a.markdown(f"**Category:** {s['category']}")
                col_a.markdown(f"**Stage:** {s['current_stage']}")
                col_a.markdown(f"**Target Funding:** {s['target_funding']}")
                col_b.markdown(f"**Team Size:** {s['team_size']} people")
                col_b.markdown(f"**Target Market:** {s['target_market']}")
                col_b.markdown(f"**Revenue Model:** {s['revenue_model']}")
                col_c.markdown(f"**Customers:** {s.get('current_customers','—')}")
                col_c.markdown(f"**Financials:** {s.get('financial_projections','—')}")

                st.markdown(f"**Description:** {s['full_description']}")

                if s.get("competition_analysis"):
                    st.markdown(f"**Competition:** {s['competition_analysis']}")
                if s.get("business_plan"):
                    st.markdown(f"**Business Plan:** {s['business_plan']}")
                if s.get("website_url"):
                    st.markdown(f"🌐 [Website]({s['website_url']})")

                if st.button(f"🗑️ Delete {s['project_name']}", key=f"del_{s['id']}"):
                    st.session_state.startups = [x for x in st.session_state.startups if x["id"] != s["id"]]
                    st.success(f"Deleted {s['project_name']}")
                    st.rerun()

# ══════════════════════════════════════════════
# TAB 2 — ADD STARTUP
# ══════════════════════════════════════════════
with tab_add:
    st.markdown("### Add New Startup")
    st.markdown("Fill in the startup profile. Fields marked * are required.")
    st.markdown("")

    with st.form("add_startup_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        project_name = c1.text_input("Project Name *", placeholder="e.g. PayFlow Africa")
        category = c2.selectbox("Category *", [
            "", "FinTech", "HealthTech", "EdTech", "AgriTech",
            "CleanTech", "Logistics", "SaaS", "E-Commerce", "AI/ML", "Other"
        ])

        tagline = st.text_input("Tagline *", placeholder="One-line pitch that captures the essence")
        full_description = st.text_area("Full Description *", placeholder="What problem does it solve and how?", height=120)

        c3, c4 = st.columns(2)
        target_funding = c3.text_input("Target Funding *", placeholder="e.g. $2M")
        current_stage = c4.selectbox("Current Stage *", [
            "", "Idea", "Pre-Seed", "Seed", "Series A", "Series B", "Profitable"
        ])

        c5, c6 = st.columns(2)
        team_size = c5.number_input("Team Size", min_value=1, value=5)
        website_url = c6.text_input("Website URL", placeholder="https://...")

        target_market = st.text_input("Target Market *", placeholder="e.g. MENA, Sub-Saharan Africa")
        revenue_model = st.text_input("Revenue Model *", placeholder="e.g. SaaS subscription + transaction fee")
        competition_analysis = st.text_area("Competition Analysis", placeholder="Who are competitors and what's your edge?", height=80)
        current_customers = st.text_input("Current Customers", placeholder="e.g. 1,200 SMEs, $400K monthly volume")

        c7, c8 = st.columns(2)
        financial_projections = c7.text_input("Financial Projections", placeholder="e.g. $800K ARR by year 1")
        pitch_deck_url = c8.text_input("Pitch Deck URL", placeholder="https://drive.google.com/...")

        business_plan = st.text_area("Business Plan Summary", placeholder="Key milestones and growth strategy", height=80)
        product_demo_url = st.text_input("Product Demo URL", placeholder="https://youtube.com/...")

        submitted = st.form_submit_button("✅ Add Startup", use_container_width=True, type="primary")

        if submitted:
            if not project_name or not category or not tagline or not full_description or not target_funding or not current_stage or not target_market or not revenue_model:
                st.error("Please fill all required (*) fields.")
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
                    "website_url": website_url,
                    "target_market": target_market,
                    "revenue_model": revenue_model,
                    "competition_analysis": competition_analysis,
                    "current_customers": current_customers,
                    "financial_projections": financial_projections,
                    "pitch_deck_url": pitch_deck_url,
                    "business_plan": business_plan,
                    "product_demo_url": product_demo_url,
                    "created_at": datetime.utcnow().isoformat(),
                }
                st.session_state.startups.append(new_startup)
                st.success(f"🎉 **{project_name}** added to the database!")

# ══════════════════════════════════════════════
# TAB 3 — AI MATCH
# ══════════════════════════════════════════════
with tab_match:
    st.markdown("### 🤖 AI Investor Matching")
    st.markdown("Describe the investor and Claude will find the best matching startups from your database.")
    st.markdown("")

    if not st.session_state.api_key:
        st.warning("⚠️ Please add your Anthropic API key in the sidebar to use AI matching.")

    if not st.session_state.startups:
        st.warning("⚠️ No startups in the database. Add some first.")

    # Investor form
    with st.form("investor_form"):
        st.markdown("#### Investor Profile")

        ic1, ic2 = st.columns(2)
        investor_name = ic1.text_input("Investor / Fund Name *", placeholder="e.g. MENA Growth Fund II")
        investment_focus = ic2.text_input("Investment Focus *", placeholder="e.g. FinTech, HealthTech, SaaS")

        ic3, ic4 = st.columns(2)
        investment_stage = ic3.selectbox("Preferred Stage *", [
            "", "Pre-Seed", "Seed", "Series A", "Series B+", "Any Stage"
        ])
        ticket_size = ic4.text_input("Ticket Size *", placeholder="e.g. $100K – $2M")

        ic5, ic6 = st.columns(2)
        preferred_markets = ic5.text_input("Preferred Markets", placeholder="e.g. MENA, Africa, Southeast Asia")
        risk_appetite = ic6.selectbox("Risk Appetite", ["", "Low", "Medium", "High", "Very High"])

        ic7, ic8 = st.columns(2)
        avoid_sectors = ic7.text_input("Sectors to Avoid", placeholder="e.g. Crypto, Gambling")
        top_k = ic8.selectbox("Matches to Return", [3, 4, 5], index=2)

        additional_notes = st.text_area(
            "Additional Notes",
            placeholder="Impact focus, ESG criteria, co-investment interest, exit strategy preferences...",
            height=80,
        )

        # Quick-fill demo button note
        st.caption("💡 Tip: Try the demo — Investor: 'MENA Growth Fund II', Focus: 'FinTech, HealthTech', Stage: 'Seed', Ticket: '$500K–$2M'")

        submit_match = st.form_submit_button(
            "🤖 Find Best Matches",
            use_container_width=True,
            type="primary",
            disabled=not st.session_state.api_key or not st.session_state.startups,
        )

    if submit_match:
        if not investor_name or not investment_focus or not investment_stage or not ticket_size:
            st.error("Please fill all required (*) fields.")
        else:
            investor = {
                "name": investor_name,
                "focus": investment_focus,
                "stage": investment_stage,
                "ticket": ticket_size,
                "markets": preferred_markets,
                "risk": risk_appetite,
                "avoid": avoid_sectors,
                "notes": additional_notes,
            }
            with st.spinner(f"🤖 Analyzing {len(st.session_state.startups)} startups for {investor_name}…"):
                try:
                    result = run_ai_match(investor, top_k)
                    st.session_state.match_results = {
                        "investor": investor_name,
                        "data": result,
                        "total": len(st.session_state.startups),
                        "timestamp": datetime.utcnow().strftime("%H:%M · %d %b %Y"),
                    }
                except json.JSONDecodeError as e:
                    st.error(f"Could not parse AI response. Try again. ({e})")
                except Exception as e:
                    st.error(f"Error: {e}")

    # ── Results ──
    if st.session_state.match_results:
        res = st.session_state.match_results
        data = res["data"]

        st.divider()
        st.markdown(f"### Results for **{res['investor']}**")
        st.caption(f"{res['total']} startups analyzed · {res['timestamp']}")

        if data.get("overall_analysis"):
            st.info(f"**🧠 AI Strategy Note:** {data['overall_analysis']}")

        st.markdown("")

        matches = data.get("matches", [])
        if not matches:
            st.warning("No matches returned. Try adjusting the investor criteria.")
        else:
            for i, m in enumerate(matches):
                score = m.get("match_score", 0)
                startup = next((s for s in st.session_state.startups if s["id"] == m.get("startup_id")), None)

                # Score color
                if score >= 80:
                    score_color = "🟢"
                elif score >= 60:
                    score_color = "🟡"
                else:
                    score_color = "🔴"

                with st.expander(
                    f"#{i+1} · {score_color} **{m['startup_name']}** — Match Score: {score}/100",
                    expanded=(i == 0),
                ):
                    # Header row
                    hc1, hc2, hc3, hc4 = st.columns(4)
                    hc1.metric("Match Score", f"{score}%")
                    if startup:
                        hc2.metric("Stage", startup["current_stage"])
                        hc3.metric("Funding Ask", startup["target_funding"])
                        hc4.metric("Category", startup["category"])

                    st.markdown(f"**Summary:** {m.get('match_summary','')}")
                    st.markdown("")

                    col_str, col_risk = st.columns(2)

                    with col_str:
                        st.markdown("**✅ Key Strengths**")
                        for s in m.get("key_strengths", []):
                            st.markdown(f"• {s}")

                    with col_risk:
                        st.markdown("**⚠️ Key Risks**")
                        for r in m.get("key_risks", []):
                            st.markdown(f"• {r}")

                    st.markdown("")
                    st.markdown(
                        f"""<div class="rec-box">💡 <strong>Recommendation:</strong> {m.get('recommendation','')}</div>""",
                        unsafe_allow_html=True,
                    )

                    if startup:
                        st.markdown("")
                        with st.expander("📄 View full startup profile"):
                            pc1, pc2 = st.columns(2)
                            pc1.markdown(f"**Market:** {startup['target_market']}")
                            pc1.markdown(f"**Team:** {startup['team_size']} people")
                            pc1.markdown(f"**Revenue Model:** {startup['revenue_model']}")
                            pc2.markdown(f"**Customers:** {startup.get('current_customers','—')}")
                            pc2.markdown(f"**Financials:** {startup.get('financial_projections','—')}")
                            st.markdown(f"**Description:** {startup['full_description']}")

        # Export JSON
        st.markdown("")
        export_data = json.dumps(res["data"], indent=2)
        st.download_button(
            label="⬇️ Export results as JSON",
            data=export_data,
            file_name=f"matches_{res['investor'].replace(' ','_')}_{datetime.utcnow().strftime('%Y%m%d')}.json",
            mime="application/json",
        )
