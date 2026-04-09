"""Career Ops — Streamlit Web Dashboard."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

from utils import (
    load_applications, add_application, update_application,
    check_duplicate, get_next_id,
    load_pipeline, load_scan_history,
    get_active_countries,
    STATUSES, STATUS_COLORS, ARCHETYPES, COUNTRY_LABELS,
)

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Career Ops",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
/* Metric cards */
div[data-testid="metric-container"] {
    background: rgba(116,199,236,0.07);
    border: 1px solid rgba(116,199,236,0.18);
    border-radius: 10px;
    padding: 14px 18px;
}
/* Duplicate banners */
.dup-warn {
    background: rgba(243,139,168,0.12);
    border-left: 4px solid #f38ba8;
    border-radius: 4px;
    padding: 10px 14px;
    margin: 8px 0;
}
.dup-info {
    background: rgba(250,179,135,0.12);
    border-left: 4px solid #fab387;
    border-radius: 4px;
    padding: 10px 14px;
    margin: 8px 0;
}
.dup-ok {
    background: rgba(166,227,161,0.12);
    border-left: 4px solid #a6e3a1;
    border-radius: 4px;
    padding: 10px 14px;
    margin: 8px 0;
}
/* Sidebar tweaks */
section[data-testid="stSidebar"] { min-width: 220px; }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _df(apps: list[dict]) -> pd.DataFrame:
    if not apps:
        return pd.DataFrame(columns=[
            "id", "date", "company", "role", "url", "score",
            "status", "archetype", "cv_lang", "country", "pdf", "report", "notes",
            "comp_suggestion", "added_at",
        ])
    df = pd.DataFrame(apps)
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
    if "score" in df.columns:
        df["score"] = pd.to_numeric(df["score"], errors="coerce")
    return df


def score_badge(score):
    if score is None or (isinstance(score, float) and pd.isna(score)):
        return "—"
    s = float(score)
    if s >= 4.5:
        return f"🟢 {s:.1f}"
    if s >= 4.0:
        return f"🟡 {s:.1f}"
    if s >= 3.5:
        return f"🟠 {s:.1f}"
    return f"🔴 {s:.1f}"


# ---------------------------------------------------------------------------
# Sidebar navigation
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown("## 🎯 Career Ops")
    st.markdown("---")
    page = st.radio(
        "Navigate",
        ["📊 Overview", "📋 Applications", "➕ Add Job", "⏳ Pipeline", "🔍 Scan History"],
        label_visibility="collapsed",
    )
    st.markdown("---")

    # Active countries indicator
    active = get_active_countries()
    labels = [COUNTRY_LABELS.get(c, c) for c in active]
    st.markdown("**Scanning countries**")
    for lbl in labels:
        st.caption(lbl)
    st.caption("Edit `config/profile.yml` → `search.countries` to change")

    st.markdown("---")
    if st.button("🔄 Refresh data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()


# ---------------------------------------------------------------------------
# Data load (cached per session)
# ---------------------------------------------------------------------------

@st.cache_data(ttl=30)
def get_apps():
    return load_applications()


apps = get_apps()
df = _df(apps)


# ===========================================================================
# PAGE: Overview
# ===========================================================================

if page == "📊 Overview":
    st.title("📊 Overview")

    if df.empty:
        st.info("No applications yet. Use **➕ Add Job** to get started.")
        st.stop()

    # ---- KPI row ----------------------------------------------------------
    total = len(df)
    applied    = int((df["status"] == "Applied").sum())    if "status" in df.columns else 0
    interviews = int((df["status"] == "Interview").sum())  if "status" in df.columns else 0
    offers     = int((df["status"] == "Offer").sum())      if "status" in df.columns else 0
    avg_score  = df["score"].mean() if "score" in df.columns and df["score"].notna().any() else None

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total", total)
    c2.metric("Applied", applied)
    c3.metric("Interviews", interviews)
    c4.metric("Offers", offers)
    c5.metric("Avg Score", f"{avg_score:.1f}/5" if avg_score else "—")

    st.markdown("---")

    left, right = st.columns(2)

    # ---- Status donut -----------------------------------------------------
    with left:
        if "status" in df.columns:
            sc = df["status"].value_counts().reset_index()
            sc.columns = ["Status", "Count"]
            fig = px.pie(
                sc, values="Count", names="Status",
                title="Applications by Status",
                color="Status",
                color_discrete_map=STATUS_COLORS,
                hole=0.45,
            )
            fig.update_traces(textposition="inside", textinfo="percent+label")
            fig.update_layout(showlegend=False, height=340, margin=dict(t=40, b=0))
            st.plotly_chart(fig, use_container_width=True)

    # ---- Score histogram --------------------------------------------------
    with right:
        if "score" in df.columns and df["score"].notna().any():
            fig = px.histogram(
                df.dropna(subset=["score"]),
                x="score", nbins=20,
                title="Score Distribution",
                color_discrete_sequence=["#74c7ec"],
                labels={"score": "Score"},
            )
            fig.add_vline(
                x=4.0, line_dash="dash", line_color="#f38ba8",
                annotation_text="Apply threshold (4.0)",
                annotation_position="top right",
            )
            fig.update_layout(height=340, showlegend=False, margin=dict(t=40, b=0),
                              yaxis_title="Count")
            st.plotly_chart(fig, use_container_width=True)

    # ---- Timeline ---------------------------------------------------------
    if "date" in df.columns and df["date"].notna().any():
        daily = (
            df.dropna(subset=["date"])
            .groupby(df["date"].dt.date)
            .size()
            .reset_index(name="count")
            .rename(columns={"date": "Date"})
            .sort_values("Date")
        )
        daily["Cumulative"] = daily["count"].cumsum()

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=daily["Date"], y=daily["Cumulative"],
            mode="lines+markers", name="Total",
            line=dict(color="#74c7ec", width=2),
            fill="tozeroy", fillcolor="rgba(116,199,236,0.08)",
        ))
        fig.update_layout(
            title="Applications Over Time",
            height=280, margin=dict(t=40, b=0),
            xaxis_title="", yaxis_title="Cumulative",
        )
        st.plotly_chart(fig, use_container_width=True)

    # ---- Recent -----------------------------------------------------------
    st.subheader("Recent Applications")
    recent = df.sort_values("date", ascending=False).head(8) if "date" in df.columns else df.head(8)
    display_cols = [c for c in ["id", "date", "company", "role", "score", "status", "archetype"] if c in recent.columns]
    recent_display = recent[display_cols].copy()
    if "score" in recent_display.columns:
        recent_display["score"] = recent_display["score"].apply(score_badge)
    if "date" in recent_display.columns:
        recent_display["date"] = recent_display["date"].dt.strftime("%Y-%m-%d")
    st.dataframe(recent_display, use_container_width=True, hide_index=True)


# ===========================================================================
# PAGE: Applications
# ===========================================================================

elif page == "📋 Applications":
    st.title("📋 Applications")

    if df.empty:
        st.info("No applications yet.")
        st.stop()

    # ---- Sidebar filters --------------------------------------------------
    with st.sidebar:
        st.markdown("**Filters**")
        status_filter = st.multiselect("Status", STATUSES, default=STATUSES)
        search = st.text_input("Search company / role", "")
        if "score" in df.columns and df["score"].notna().any():
            score_min, score_max = st.slider("Score range", 0.0, 5.0, (0.0, 5.0), 0.1)
        else:
            score_min, score_max = 0.0, 5.0
        if "archetype" in df.columns:
            arch_opts = ["All"] + sorted(df["archetype"].dropna().unique().tolist())
            arch_filter = st.selectbox("Archetype", arch_opts)
        else:
            arch_filter = "All"
        if "country" in df.columns:
            country_vals = sorted(df["country"].dropna().unique().tolist())
            country_filter = st.multiselect(
                "Country", country_vals,
                format_func=lambda c: COUNTRY_LABELS.get(c, c),
            ) if country_vals else []
        else:
            country_filter = []

    # ---- Apply filters ----------------------------------------------------
    filtered = df.copy()
    if status_filter and "status" in filtered.columns:
        filtered = filtered[filtered["status"].isin(status_filter)]
    if search:
        mask = (
            filtered.get("company", pd.Series(dtype=str)).str.contains(search, case=False, na=False) |
            filtered.get("role",    pd.Series(dtype=str)).str.contains(search, case=False, na=False)
        )
        filtered = filtered[mask]
    if "score" in filtered.columns:
        filtered = filtered[
            (filtered["score"].isna()) |
            ((filtered["score"] >= score_min) & (filtered["score"] <= score_max))
        ]
    if arch_filter != "All" and "archetype" in filtered.columns:
        filtered = filtered[filtered["archetype"] == arch_filter]
    if country_filter and "country" in filtered.columns:
        filtered = filtered[filtered["country"].isin(country_filter)]

    # ---- Sort + display ---------------------------------------------------
    sort_col, sort_dir_col, export_col = st.columns([2, 1, 1])
    with sort_col:
        sort_by = st.selectbox("Sort by", ["date", "score", "company", "status", "id"], index=0)
    with sort_dir_col:
        asc = st.checkbox("Ascending", value=False)
    with export_col:
        csv_bytes = filtered.to_csv(index=False).encode()
        st.download_button("⬇ Export CSV", csv_bytes, "applications.csv", "text/csv", use_container_width=True)

    if sort_by in filtered.columns:
        filtered = filtered.sort_values(sort_by, ascending=asc, na_position="last")

    st.caption(f"Showing **{len(filtered)}** of {len(df)} applications")

    display_cols = [c for c in ["id", "date", "company", "role", "score", "status", "archetype", "cv_lang", "country", "pdf", "notes"] if c in filtered.columns]
    display_df = filtered[display_cols].copy()
    if "score" in display_df.columns:
        display_df["score"] = display_df["score"].apply(score_badge)
    if "date" in display_df.columns:
        display_df["date"] = display_df["date"].dt.strftime("%Y-%m-%d")
    if "pdf" in display_df.columns:
        display_df["pdf"] = display_df["pdf"].apply(lambda x: "✅" if x else "❌")

    table_col, detail_col = st.columns([3, 1])

    with table_col:
        selection = st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row",
            key="apps_table",
        )

    with detail_col:
        st.subheader("Quick Update")
        selected_rows = selection.selection.rows if selection else []
        if selected_rows:
            idx = selected_rows[0]
            row = filtered.iloc[idx]
            app_id = str(row.get("id", ""))
            st.markdown(f"**{row.get('company', '')}**")
            st.caption(str(row.get("role", "")))

            if row.get("url"):
                st.link_button("🔗 Open JD", str(row["url"]), use_container_width=True)

            report_path = row.get("report", "")
            if report_path:
                full_report = Path(__file__).parent.parent / str(report_path)
                if full_report.exists():
                    st.link_button("📄 View Report", f"file://{full_report}", use_container_width=True)

            new_status = st.selectbox(
                "Status",
                STATUSES,
                index=STATUSES.index(row.get("status")) if row.get("status") in STATUSES else 0,
                key="status_sel",
            )
            new_notes = st.text_input("Notes", str(row.get("notes") or ""), key="notes_inp")
            new_comp = st.text_input("Comp suggestion", str(row.get("comp_suggestion") or ""), key="comp_inp")

            if st.button("💾 Save", type="primary", use_container_width=True):
                update_application(app_id, {
                    "status": new_status,
                    "notes": new_notes,
                    "comp_suggestion": new_comp,
                })
                st.cache_data.clear()
                st.success("Saved!")
                st.rerun()
        else:
            st.info("← Select a row to update it")


# ===========================================================================
# PAGE: Add Job
# ===========================================================================

elif page == "➕ Add Job":
    st.title("➕ Add Job")
    st.caption("Duplicate detection runs automatically as you type.")

    col_form, col_check = st.columns([3, 2])

    with col_form:
        url     = st.text_input("Job URL", placeholder="https://boards.greenhouse.io/…")
        company = st.text_input("Company *", placeholder="Anthropic")
        role    = st.text_input("Role / Title", placeholder="Senior AI Architect")

        c1, c2 = st.columns(2)
        with c1:
            archetype = st.selectbox("Archetype", ARCHETYPES)
            status    = st.selectbox("Status", STATUSES, index=0)
            country_opts = list(COUNTRY_LABELS.keys())
            country = st.selectbox(
                "Country", country_opts,
                index=country_opts.index("DE") if "DE" in country_opts else 0,
                format_func=lambda c: COUNTRY_LABELS.get(c, c),
            )
            cv_lang = st.selectbox(
                "CV Language", ["EN", "DE"],
                help="EN = English CV template, DE = German CV template",
            )
        with c2:
            score = st.slider("Score (if evaluated)", 0.0, 5.0, 0.0, 0.1)
            comp_suggestion = st.text_input("Comp suggestion", placeholder="€120k-140k")

        notes = st.text_area("Notes", height=80)

    with col_check:
        st.subheader("Duplicate Check")

        dup_result = {"is_duplicate": False}
        if url or company:
            dup_result = check_duplicate(
                url=url.strip() or None,
                company=company.strip() or None,
                role=role.strip() or None,
            )

        if dup_result["is_duplicate"]:
            ex = dup_result["existing"]
            st.markdown(f"""
<div class="dup-warn">
⚠️ <strong>Duplicate detected</strong> ({dup_result['match_type']})<br>
<strong>{ex.get('company')}</strong> — {ex.get('role')}<br>
Status: {ex.get('status')} &nbsp;|&nbsp; Score: {ex.get('score', '—')}/5<br>
Added: {ex.get('date')}
</div>""", unsafe_allow_html=True)

        elif dup_result.get("match_type") == "company_exists":
            existing_list = dup_result.get("existing", [])
            rows = "".join(
                f"<li>{a.get('role', '?')} — {a.get('status')}</li>"
                for a in existing_list[:5]
            )
            st.markdown(f"""
<div class="dup-info">
ℹ️ <strong>{dup_result['warning']}</strong><br>
<ul style="margin:4px 0 0 16px;padding:0">{rows}</ul>
</div>""", unsafe_allow_html=True)

        elif url or company:
            st.markdown("""
<div class="dup-ok">
✅ <strong>No duplicate found</strong> — safe to add.
</div>""", unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("**Score guidance**")
        st.markdown("- 🟢 4.5+ → apply immediately\n- 🟡 4.0–4.4 → worth applying\n- 🟠 3.5–3.9 → specific reason needed\n- 🔴 < 3.5 → skip")

    st.markdown("---")
    if st.button("✅ Add Application", type="primary", use_container_width=True):
        if not company.strip():
            st.error("Company name is required.")
        elif dup_result["is_duplicate"]:
            st.error(f"Already tracked: {dup_result['existing'].get('company')} — {dup_result['existing'].get('role')}")
        else:
            fresh_apps = load_applications()
            new_app = {
                "id":             get_next_id(fresh_apps),
                "date":           datetime.now().strftime("%Y-%m-%d"),
                "company":        company.strip(),
                "role":           role.strip(),
                "url":            url.strip(),
                "score":          score if score > 0 else None,
                "status":         status,
                "archetype":      archetype,
                "cv_lang":        cv_lang,
                "country":        country,
                "pdf":            False,
                "report":         "",
                "notes":          notes.strip(),
                "comp_suggestion": comp_suggestion.strip(),
                "added_at":       datetime.now().isoformat(),
            }
            add_application(new_app)
            st.cache_data.clear()
            st.success(f"✅ Added #{new_app['id']}: **{company}** — {role}")
            st.balloons()


# ===========================================================================
# PAGE: Pipeline
# ===========================================================================

elif page == "⏳ Pipeline":
    st.title("⏳ Pipeline")
    st.caption("Pending jobs from your scanner inbox (`data/pipeline.md`).")

    pipeline = load_pipeline()
    pending = [j for j in pipeline if j["status"] == "pending"]
    done    = [j for j in pipeline if j["status"] == "done"]
    errors  = [j for j in pipeline if j["status"] == "error"]

    c1, c2, c3 = st.columns(3)
    c1.metric("Pending", len(pending))
    c2.metric("Done", len(done))
    c3.metric("Errors", len(errors))

    if not pending and not errors:
        st.info("Pipeline is empty. Run `/career-ops-reiterated scan` to find new jobs, or add URLs to `data/pipeline.md`.")
        if done:
            with st.expander(f"Completed jobs ({len(done)})"):
                for j in done:
                    st.markdown(f"✅ **{j.get('company','?')}** — {j.get('title','?')}")
        st.stop()

    # ---- Pending ----------------------------------------------------------
    st.subheader(f"To Evaluate ({len(pending)})")

    for job in pending:
        jurl    = job.get("url", "")
        company = job.get("company", "?")
        title   = job.get("title", "Unknown role")

        with st.container(border=True):
            row1, row2 = st.columns([5, 1])
            with row1:
                st.markdown(f"**{company}** — {title}")
                if jurl:
                    st.caption(jurl[:90] + ("…" if len(jurl) > 90 else ""))
            with row2:
                if jurl:
                    st.link_button("Open", jurl, use_container_width=True)

            # Inline dup check
            dup = check_duplicate(url=jurl, company=company)
            if dup["is_duplicate"]:
                ex = dup["existing"]
                st.caption(f"⚠️ Already tracked: {ex.get('company')} [{ex.get('status')}]")

    # ---- Errors -----------------------------------------------------------
    if errors:
        with st.expander(f"⚠️ Errors ({len(errors)})"):
            for j in errors:
                st.markdown(f"- `{j.get('url','')}` — {j.get('title','')}")

    # ---- Done -------------------------------------------------------------
    if done:
        with st.expander(f"Completed ({len(done)})"):
            for j in done:
                st.markdown(f"✅ **{j.get('company','?')}** — {j.get('title','?')}")


# ===========================================================================
# PAGE: Scan History
# ===========================================================================

elif page == "🔍 Scan History":
    st.title("🔍 Scan History")

    history = load_scan_history()

    if not history:
        st.info("No scan history yet. Run `/career-ops-reiterated scan` to populate.")
        st.stop()

    hdf = pd.DataFrame(history)

    if "status" in hdf.columns:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Seen",        len(hdf))
        c2.metric("Added to Pipeline", int((hdf["status"] == "added").sum()))
        c3.metric("Duplicates",        int((hdf["status"] == "skipped_dup").sum()))
        c4.metric("Expired",           int((hdf["status"] == "skipped_expired").sum()))

        with st.sidebar:
            st.markdown("---")
            st.markdown("**History Filters**")
            hist_status = st.multiselect(
                "Status", hdf["status"].unique().tolist(),
                default=hdf["status"].unique().tolist(),
            )
        if hist_status:
            hdf = hdf[hdf["status"].isin(hist_status)]

    search_h = st.text_input("Search company / title", "")
    if search_h:
        mask = (
            hdf.get("company", pd.Series(dtype=str)).str.contains(search_h, case=False, na=False) |
            hdf.get("title",   pd.Series(dtype=str)).str.contains(search_h, case=False, na=False)
        )
        hdf = hdf[mask]

    st.caption(f"Showing {len(hdf)} records")
    st.dataframe(hdf, use_container_width=True, hide_index=True)
