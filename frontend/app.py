"""Streamlit Frontend for Deal Intelligence Agent.

Contract compliant UI providing:
- Pipeline overview & deal selector
- Side-by-side Memory ON vs OFF pre-call briefing demo
- Personalized follow-up email drafter
- Live call ingestion (with one-click Demo Call 5 loader)
- Deal outcome recorder & global playbook insights
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv
import requests
import streamlit as st

# Load frontend environment
_env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=_env_path)

API_BASE = os.getenv("API_BASE", "http://localhost:8000").rstrip("/")

st.set_page_config(
    page_title="Deal Intelligence Agent",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for polished enterprise look
st.markdown(
    """
    <style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
    .card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .badge-won {
        background-color: #DEF7EC;
        color: #03543F;
        padding: 4px 10px;
        border-radius: 12px;
        font-weight: 600;
        font-size: 0.8rem;
    }
    .badge-lost {
        background-color: #FDE8E8;
        color: #9B1C1C;
        padding: 4px 10px;
        border-radius: 12px;
        font-weight: 600;
        font-size: 0.8rem;
    }
    .badge-open {
        background-color: #E1EFFE;
        color: #1E429F;
        padding: 4px 10px;
        border-radius: 12px;
        font-weight: 600;
        font-size: 0.8rem;
    }
    .stance-champion { color: #057A55; font-weight: 600; }
    .stance-cautious { color: #D97706; font-weight: 600; }
    .stance-blocker { color: #E02424; font-weight: 600; }
    .stance-neutral { color: #4B5563; font-weight: 600; }
    </style>
    """,
    unsafe_allow_html=True,
)


def api_get(endpoint: str, params: Optional[Dict[str, Any]] = None) -> Optional[Any]:
    try:
        res = requests.get(f"{API_BASE}{endpoint}", params=params, timeout=30)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        st.error(f"API Error ({endpoint}): {e}")
        return None


def api_post(endpoint: str, json_data: Optional[Dict[str, Any]] = None) -> Optional[Any]:
    try:
        res = requests.post(f"{API_BASE}{endpoint}", json=json_data or {}, timeout=90)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        st.error(f"API Error ({endpoint}): {e}")
        return None


# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### 🧠 Deal Intelligence")
    st.caption("Powered by **Hindsight Cloud** & **Groq**")

    # Backend health check
    health_res = api_get("/health")
    if health_res and health_res.get("ok"):
        st.success("🟢 Backend Connected", icon="✅")
    else:
        st.error(f"🔴 Backend Offline ({API_BASE})", icon="⚠️")
        st.info("Make sure the backend is running at http://localhost:8000")

    st.markdown("---")
    st.markdown("#### ⚡ Quick Actions")
    if st.button("🌱 Seed Initial Deals & Memory", use_container_width=True):
        with st.spinner("Seeding deals and retaining memories in Hindsight..."):
            seed_res = api_post("/admin/seed")
            if seed_res:
                st.success(
                    f"Loaded {seed_res.get('deals_loaded', 0)} deals, "
                    f"retained {seed_res.get('calls_retained', 0)} calls!"
                )
                st.rerun()

    st.markdown("---")
    st.markdown("#### 📁 Active Deal Pipeline")

    deals = api_get("/deals") or []
    deal_options = {d["deal_id"]: f"{d['company']} (${d['value']:,})" for d in deals}

    selected_deal_id = None
    if deal_options:
        selected_deal_id = st.selectbox(
            "Select Deal",
            options=list(deal_options.keys()),
            format_func=lambda x: deal_options.get(x, x),
            index=0,
        )

    # Show active deal snapshot
    if selected_deal_id:
        active_deal = next((d for d in deals if d["deal_id"] == selected_deal_id), None)
        if active_deal:
            st.markdown(f"**Company:** {active_deal['company']}")
            st.markdown(f"**Value:** ${active_deal['value']:,}")
            st.markdown(f"**Stage:** `{active_deal['stage']}`")
            st.markdown(f"**Recorded Calls:** {active_deal['calls_count']}")

            outcome = active_deal.get("outcome")
            if outcome == "won":
                st.markdown('<span class="badge-won">WON</span>', unsafe_allow_html=True)
            elif outcome == "lost":
                st.markdown('<span class="badge-lost">LOST</span>', unsafe_allow_html=True)
            else:
                st.markdown('<span class="badge-open">ACTIVE / OPEN</span>', unsafe_allow_html=True)

    with st.expander("➕ Create New Deal"):
        with st.form("new_deal_form"):
            new_company = st.text_input("Company Name")
            new_value = st.number_input("Deal Value ($)", min_value=1000, value=100000, step=5000)
            submitted = st.form_submit_button("Create Deal")
            if submitted and new_company:
                res = api_post("/deals", {"company": new_company, "value": float(new_value)})
                if res and "deal_id" in res:
                    st.success(f"Deal created: {res['deal_id']}")
                    st.rerun()


# --- MAIN VIEW ---
st.markdown('<div class="main-header">Deal Intelligence Agent</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">Remembers every objection, stakeholder concern, and promise across sales calls. Briefs reps before meetings, drafts follow-up emails, and learns winning playbooks.</div>',
    unsafe_allow_html=True,
)

if not selected_deal_id:
    st.info("👈 Please select or seed a deal in the sidebar to begin.")
    st.stop()

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "📋 Pre-Call Briefing",
        "⚖️ Memory Comparison (Demo)",
        "✉️ Follow-Up Email",
        "🎙️ Ingest Call (Demo Call 5)",
        "🏆 Playbook & Insights",
    ]
)


# --- TAB 1: PRE-CALL BRIEFING ---
with tab1:
    st.subheader("🎯 Pre-Call Strategic Briefing")

    col_ctrl1, col_ctrl2 = st.columns([2, 1])
    with col_ctrl1:
        memory_mode = st.radio(
            "Memory Mode:",
            options=["on", "off"],
            format_func=lambda x: "🧠 Memory ON (Full Hindsight Long-Term Memory)" if x == "on" else "⚡ Memory OFF (Latest Call Only)",
            horizontal=True,
        )
    with col_ctrl2:
        st.caption("Toggle between using full multi-call memory vs. latest call only.")

    with st.spinner("Generating intelligence brief..."):
        brief_data = api_get(f"/deals/{selected_deal_id}/brief", params={"memory": memory_mode})

    if brief_data:
        # Memory indicator
        if brief_data.get("memory_used"):
            st.success(f"✅ Hindsight Memory Active: Recalled {len(brief_data.get('recalled_facts', []))} grounded facts from previous calls & cross-deal playbook reflection.")
        else:
            st.warning("⚠️ Memory OFF: Briefing is synthesized strictly from the latest call with zero historical memory.")

        # Brief text
        st.markdown("#### 📝 Executive Brief")
        st.info(brief_data.get("brief", "No briefing generated."))

        # Open Objections & Stakeholders
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### 🛡️ Open Objections")
            objections = brief_data.get("open_objections", [])
            if objections:
                for obj in objections:
                    st.markdown(
                        f"""
                        <div class="card">
                            <b>Objection:</b> {obj.get('text')}<br>
                            <small>Raised in <b>Call {obj.get('raised_in_call', 1)}</b> by <b>{obj.get('by', 'Stakeholder')}</b></small>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            else:
                st.caption("No open objections recorded.")

        with c2:
            st.markdown("#### 👥 Key Stakeholders & Stances")
            stakeholders = brief_data.get("stakeholders", [])
            if stakeholders:
                for sh in stakeholders:
                    stance = sh.get("stance", "Neutral")
                    stance_class = f"stance-{stance.lower()}"
                    st.markdown(
                        f"""
                        <div class="card">
                            <b>{sh.get('name')}</b> ({sh.get('role')}) - <span class="{stance_class}">{stance.upper()}</span><br>
                            <small><b>Concerns:</b> {sh.get('concerns')}</small>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            else:
                st.caption("No stakeholder stances identified.")

        # Promises and Recalled Facts
        c3, c4 = st.columns(2)
        with c3:
            st.markdown("#### 🤝 Rep Commitments & Promises")
            promises = brief_data.get("promises", [])
            if promises:
                for p in promises:
                    st.markdown(
                        f"""
                        <div class="card">
                            <b>Commitment:</b> {p.get('text')}<br>
                            <small>Promised by <b>{p.get('made_by', 'Rep')}</b> | Due: <b>{p.get('due', 'Upcoming')}</b></small>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            else:
                st.caption("No open promises recorded.")

        with c4:
            st.markdown("#### 💡 Playbook Recommendations")
            tips = brief_data.get("playbook_tips", [])
            if tips:
                for t in tips:
                    st.markdown(
                        f"""
                        <div class="card">
                            <b>Tip:</b> {t.get('tip')}<br>
                            <small><b>Evidence:</b> {t.get('evidence')}</small>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            else:
                st.caption("No playbook recommendations available.")

        # Recalled Facts list if memory ON
        if brief_data.get("memory_used") and brief_data.get("recalled_facts"):
            st.markdown("#### 📜 Grounded Facts Recalled from Past Calls")
            for rf in brief_data.get("recalled_facts", []):
                st.markdown(f"- **[Call {rf.get('source_call', 1)}]** {rf.get('fact')}")


# --- TAB 2: SIDE-BY-SIDE MEMORY COMPARISON (BEFORE / AFTER DEMO) ---
with tab2:
    st.subheader("⚖️ Before vs. After: Memory OFF vs. Memory ON")
    st.markdown(
        "Demonstrates how flat-context LLMs forget crucial details from past calls, "
        "while **Hindsight Cloud** retains objections, promises, and cross-deal patterns."
    )

    if st.button("🔄 Generate Live Side-by-Side Comparison", type="primary"):
        with st.spinner("Querying both Memory OFF and Memory ON states..."):
            b_off = api_get(f"/deals/{selected_deal_id}/brief", params={"memory": "off"})
            b_on = api_get(f"/deals/{selected_deal_id}/brief", params={"memory": "on"})

        col_left, col_right = st.columns(2)

        with col_left:
            st.markdown("### ⚡ Memory OFF (Latest Call Only)")
            st.caption("Flat context model without long-term memory")
            if b_off:
                st.error("❌ Forgets David's Call 2 ERP latency concerns\n❌ Forgets promised SOC2 report\n❌ Unaware of past price discussions")
                st.markdown("#### Brief:")
                st.write(b_off.get("brief"))
                st.markdown(f"**Open Objections Detected:** {len(b_off.get('open_objections', []))}")
                for o in b_off.get("open_objections", []):
                    st.markdown(f"- {o.get('text')} *(raised in Call {o.get('raised_in_call')})*")
                st.markdown(f"**Promises Tracked:** {len(b_off.get('promises', []))}")
                for p in b_off.get("promises", []):
                    st.markdown(f"- {p.get('text')} *(due {p.get('due')})*")

        with col_right:
            st.markdown("### 🧠 Memory ON (Hindsight Long-Term Memory)")
            st.caption("Active temporal recall, entity tracking, and cross-session reflection")
            if b_on:
                st.success("✅ Recalls David's SAP ERP latency objection from Call 2\n✅ Remembers promised SOC2 Type II audit report\n✅ Connects CFO Sarah's budget threshold to quarterly billing playbook")
                st.markdown("#### Brief:")
                st.write(b_on.get("brief"))
                st.markdown(f"**Open Objections Detected:** {len(b_on.get('open_objections', []))}")
                for o in b_on.get("open_objections", []):
                    st.markdown(f"- {o.get('text')} *(raised in Call {o.get('raised_in_call')} by {o.get('by')})*")
                st.markdown(f"**Promises Tracked:** {len(b_on.get('promises', []))}")
                for p in b_on.get("promises", []):
                    st.markdown(f"- {p.get('text')} *(due {p.get('due')})*")
                st.markdown(f"**Playbook Winning Tips:**")
                for t in b_on.get("playbook_tips", []):
                    st.markdown(f"- **Tip:** {t.get('tip')}\n  *Evidence:* {t.get('evidence')}")


# --- TAB 3: FOLLOW-UP EMAIL DRAFTER ---
with tab3:
    st.subheader("✉️ Personalized Follow-Up Email Drafter")
    st.caption("Drafts an executive follow-up email addressing all open objections and commitments.")

    email_mode = st.radio(
        "Email Generation Mode:",
        options=["on", "off"],
        format_func=lambda x: "🧠 Memory ON (Cites past promises, technical specs & quarterly amortization)" if x == "on" else "⚡ Memory OFF (Generic summary of latest call only)",
        horizontal=True,
    )

    if st.button("✍️ Draft Follow-Up Email", type="primary"):
        with st.spinner("Drafting personalized executive follow-up email..."):
            email_res = api_post(f"/deals/{selected_deal_id}/followup", {"memory": email_mode})
            if email_res and "email" in email_res:
                st.text_area("Generated Email Draft", value=email_res["email"], height=350)
                st.download_button(
                    label="📥 Download Email Draft",
                    data=email_res["email"],
                    file_name=f"followup_{selected_deal_id}_{email_mode}.txt",
                    mime="text/plain",
                )


# --- TAB 4: INGEST CALL TRANSCRIPT ---
with tab4:
    st.subheader("🎙️ Ingest New Call Transcript")
    st.caption("Ingests a new call transcript and retains memories into Hindsight in real time.")

    # Load Demo Call 5 helper
    demo_call_5_file = Path(__file__).resolve().parent.parent / "data" / "demo_call_5.json"
    demo_call_5_data = None
    if demo_call_5_file.exists():
        try:
            demo_call_5_data = json.loads(demo_call_5_file.read_text(encoding="utf-8"))
        except Exception:
            pass

    col_btn1, col_btn2 = st.columns([1, 2])
    with col_btn1:
        load_demo = st.button("📄 Pre-fill with Demo Call 5")

    default_call_no = 5
    default_date = "2026-11-20"
    default_participants = "Alex Rivera, David Chen, Sarah Jenkins, Tom Bradley"
    default_transcript = ""

    if load_demo and demo_call_5_data:
        default_call_no = demo_call_5_data.get("call_no", 5)
        default_date = demo_call_5_data.get("date", "2026-11-20")
        default_participants = ", ".join(demo_call_5_data.get("participants", []))
        default_transcript = demo_call_5_data.get("transcript", "")
        st.info("Loaded data from `data/demo_call_5.json`.")

    with st.form("ingest_call_form"):
        call_no = st.number_input("Call Number", min_value=1, value=default_call_no)
        call_date = st.text_input("Date (YYYY-MM-DD)", value=default_date)
        participants_str = st.text_input("Participants (comma-separated)", value=default_participants)
        transcript = st.text_area("Call Transcript", value=default_transcript, height=200)

        ingest_submitted = st.form_submit_button("Ingest & Retain in Memory Bank", type="primary")

        if ingest_submitted:
            if not transcript.strip():
                st.error("Please provide a call transcript.")
            else:
                participants = [p.strip() for p in participants_str.split(",") if p.strip()]
                payload = {
                    "call_no": int(call_no),
                    "date": call_date,
                    "participants": participants,
                    "transcript": transcript,
                }
                with st.spinner("Retaining call transcript and extracting entities in Hindsight..."):
                    res = api_post(f"/deals/{selected_deal_id}/calls", payload)
                    if res and res.get("retained"):
                        st.success(f"Call {call_no} retained successfully into memory bank deal-{selected_deal_id}!")
                        st.rerun()


# --- TAB 5: PLAYBOOK & CROSS-DEAL COACHING ---
with tab5:
    st.subheader("🏆 Global Playbook & Mental Models")
    st.caption("Insights, winning objection-handling strategies, and mental models synthesized across all closed deals.")

    with st.spinner("Reflecting on global playbook memory bank..."):
        playbook_data = api_get("/playbook/insights")

    if playbook_data:
        st.markdown("#### 🧠 Operating Mental Models")
        models = playbook_data.get("mental_models", [])
        if models:
            for m in models:
                st.markdown(
                    f"""
                    <div class="card">
                        <h4 style="margin: 0; color: #1E3A8A;">📌 {m.get('name')}</h4>
                        <p style="margin-top: 8px; color: #334155;">{m.get('summary')}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.info("No mental models registered.")

        st.markdown("#### 📊 Cross-Deal Empirical Insights")
        insights = playbook_data.get("insights", [])
        if insights:
            for ins in insights:
                conf = int(ins.get("confidence", 0.85) * 100)
                st.markdown(
                    f"""
                    <div class="card">
                        <b>Insight:</b> {ins.get('text')}<br>
                        <small>Confidence Score: <b>{conf}%</b></small>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.info("No empirical insights generated yet.")

    st.markdown("---")
    st.markdown("#### 🏁 Record Deal Outcome")
    st.caption("Record whether a deal was Won or Lost, feeding learnings into the global Playbook bank.")

    with st.form("outcome_form"):
        col_res1, col_res2 = st.columns(2)
        with col_res1:
            outcome_res = st.selectbox("Outcome Result", ["won", "lost"])
        with col_res2:
            objections_str = st.text_input("Objections Handled (comma-separated)", "Upfront fee budget, ERP latency SLA")

        notes = st.text_area("Strategic Notes & Winning Tactics", "Offered 60-day phased pilot tied to verified savings.")
        record_btn = st.form_submit_button("Record Outcome to Playbook")

        if record_btn:
            handled = [o.strip() for o in objections_str.split(",") if o.strip()]
            payload = {
                "result": outcome_res,
                "objections_handled": handled,
                "notes": notes,
            }
            with st.spinner("Retaining deal outcome into global playbook bank..."):
                out_res = api_post(f"/deals/{selected_deal_id}/outcome", payload)
                if out_res and out_res.get("ok"):
                    st.success(f"Deal {selected_deal_id} marked as {outcome_res.upper()} and retained into Playbook!")
                    st.rerun()
