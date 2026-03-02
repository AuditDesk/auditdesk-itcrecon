# ============================================================
# ITCRECON v3.0 — by Audit Desk
# ₹999/month | ₹8,999/year — Both Early Bird, locked forever
# Stack: Streamlit + Supabase + Razorpay
# Login: via itcrecon.in (passes ?email= param after auth)
# Deploy: Streamlit Cloud (free)
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np
from supabase import create_client
import razorpay
from io import BytesIO
from datetime import datetime, date, timedelta
import time
import uuid
import json
try:
    import anthropic as _anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle,
                                  Paragraph, Spacer, HRFlowable, Image as RLImage)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch

# ============================================================
# SECTION 1: PAGE CONFIG & GLOBAL STYLES
# ============================================================

st.set_page_config(
    page_title="Audit Desk™ — ITC Forensic Engine",
    page_icon="📐",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
/* ═══════════════════════════════════════════════════════════════
   AUDIT DESK — BLUE SPECTRUM THEME
   Midnight Navy. Electric Cyan. Precise. Trusted. Professional.
   ═══════════════════════════════════════════════════════════════ */
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600;700&family=DM+Sans:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

/* ── Base ─────────────────────────────────────────────────────── */
.stApp { background-color: #0A1B44 !important; color: #FFFFFF; }

/* Override Streamlit's default white/light backgrounds */
[data-testid="stAppViewContainer"] { background-color: #0A1B44 !important; }
[data-testid="stHeader"]           { background-color: #0A1B44 !important; }
[data-testid="stToolbar"]          { background-color: #0A1B44 !important; }
.main .block-container             { background-color: #0A1B44 !important; }

section[data-testid="stSidebar"] {
    background-color: #071233 !important;
    border-right: 1px solid #1A3A6E;
}
section[data-testid="stSidebar"] > div {
    background-color: #071233 !important;
}

/* ── Inputs ───────────────────────────────────────────────────── */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stTextArea textarea,
.stDateInput input {
    background-color: #0D2157 !important;
    color: #FFFFFF !important;
    border: 1px solid #1A3A6E !important;
    border-radius: 6px !important;
}
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus {
    border-color: #00CFFF !important;
    box-shadow: 0 0 0 2px rgba(0,207,255,0.18) !important;
}
.stSelectbox > div > div {
    background-color: #0D2157 !important;
    color: #FFFFFF !important;
    border: 1px solid #1A3A6E !important;
}
/* Dropdown options */
[data-baseweb="select"] { background: #0D2157 !important; }
[data-baseweb="popover"] ul { background: #0D2157 !important; }

/* ── Buttons ──────────────────────────────────────────────────── */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #0095BF 0%, #00CFFF 50%, #00CFFF 100%) !important;
    color: #0A1B44 !important;
    border: none !important;
    border-radius: 6px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: 0.5px !important;
    padding: 10px 20px !important;
    transition: all 0.2s !important;
    box-shadow: 0 2px 12px rgba(0,207,255,0.35) !important;
}
.stButton > button[kind="primary"]:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 24px rgba(0,207,255,0.55) !important;
    background: linear-gradient(135deg, #00CFFF 0%, #FFFFFF 100%) !important;
}
.stButton > button[kind="secondary"] {
    background: #0D2157 !important;
    color: #FFFFFF !important;
    border: 1px solid #1A3A6E !important;
    border-radius: 6px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    transition: all 0.2s !important;
}
.stButton > button[kind="secondary"]:hover {
    border-color: #00CFFF !important;
    color: #00CFFF !important;
    background: #0D2157 !important;
}

/* ── Tabs ─────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid #1A3A6E !important;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #FFFFFF !important;
    border-bottom: 2px solid transparent !important;
    font-weight: 500;
    padding: 8px 16px;
}
.stTabs [aria-selected="true"] {
    color: #00CFFF !important;
    border-bottom: 2px solid #00CFFF !important;
    background: transparent !important;
}

/* ── Sliders ──────────────────────────────────────────────────── */
[data-testid="stSlider"] > div > div > div > div {
    background: #00CFFF !important;
}

/* ── Metrics ──────────────────────────────────────────────────── */
[data-testid="stMetricValue"]     { color: #00CFFF !important; }
[data-testid="stMetricLabel"]     { color: #FFFFFF !important; }
[data-testid="stMetricDelta"]     { color: #00CFFF !important; }

/* ── Dataframes ───────────────────────────────────────────────── */
.stDataFrame iframe { background: #071233 !important; }
[data-testid="stDataFrameResizable"] {
    background: #071233 !important;
    border: 1px solid #1A3A6E !important;
}

/* ── Progress bars ────────────────────────────────────────────── */
.stProgress > div > div { background: #00CFFF !important; }

/* ── Spinners & alerts ────────────────────────────────────────── */
.stSpinner > div { border-top-color: #00CFFF !important; }
.stAlert         { background: #0D2157 !important; border-color: #1A3A6E !important; }
.stSuccess       { border-left-color: #00CFFF !important; }
.stError         { border-left-color: #e85d50 !important; }
.stWarning       { border-left-color: #00CFFF !important; }
.stInfo          { border-left-color: #00CFFF !important; }

/* ── Dividers ─────────────────────────────────────────────────── */
hr { border-color: #1A3A6E !important; }

/* ── Scrollbar ────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #0A1B44; }
::-webkit-scrollbar-thumb { background: #1A3A6E; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #00CFFF; }

/* ── File uploader — drag & drop visibility ───────────────────── */
[data-testid="stFileUploader"] {
    background: #0D2157 !important;
    border: 1.5px dashed #1A3A6E !important;
    border-radius: 8px !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: #00CFFF !important;
}
[data-testid="stFileUploader"] section {
    background: transparent !important;
}
[data-testid="stFileUploader"] section > button {
    background: #071233 !important;
    color: #00CFFF !important;
    border: 1px solid #1A3A6E !important;
    border-radius: 6px !important;
}
[data-testid="stFileUploader"] section p,
[data-testid="stFileUploader"] section span,
[data-testid="stFileUploaderDropzoneInstructions"] span,
[data-testid="stFileUploaderDropzoneInstructions"] small {
    color: #FFFFFF !important;
    opacity: .85 !important;
}
/* Download button visibility */
[data-testid="stDownloadButton"] > button {
    background: linear-gradient(135deg, #0095BF, #00CFFF) !important;
    color: #0A1B44 !important;
    border: none !important;
    border-radius: 6px !important;
    font-weight: 700 !important;
    box-shadow: 0 2px 12px rgba(0,207,255,0.35) !important;
}
[data-testid="stDownloadButton"] > button:hover {
    box-shadow: 0 6px 24px rgba(0,207,255,0.55) !important;
    transform: translateY(-1px) !important;
}

/* ── Cards ────────────────────────────────────────────────────── */
.card {
    background: #0D2157; border: 1px solid #1A3A6E;
    border-radius: 10px; padding: 20px; margin: 8px 0;
}
.card-blue  { border-left: 3px solid #00CFFF; }
.card-green { border-left: 3px solid #0080A8; }
.card-amber { border-left: 3px solid #00CFFF; }
.card-red   { border-left: 3px solid #e85d50; }

/* ── Wealth discovery ─────────────────────────────────────────── */
.wealth-card {
    background: linear-gradient(135deg, #071233 0%, #0D2157 50%, #1A3A6E 100%);
    border: 2px solid #00CFFF;
    border-radius: 12px; padding: 28px; margin: 16px 0;
    box-shadow: 0 4px 32px rgba(0,207,255,0.2),
                inset 0 1px 0 rgba(0,207,255,0.1);
}
.wealth-number {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 2.8rem; font-weight: 700;
    color: #00CFFF; margin: 0; line-height: 1;
    text-shadow: 0 0 30px rgba(0,207,255,0.5);
}
.wealth-label { color: #00CFFF; font-size: 0.9rem; margin: 6px 0 0 0; }

/* ── Stat boxes ───────────────────────────────────────────────── */
.stat-grid {
    display: grid; grid-template-columns: repeat(4, 1fr);
    gap: 12px; margin: 16px 0;
}
.stat-box {
    background: #071233; border: 1px solid #1A3A6E;
    border-top: 2px solid #00CFFF;
    border-radius: 8px; padding: 18px; text-align: center;
}
.stat-number {
    font-family: 'IBM Plex Mono', monospace;
    color: #00CFFF; font-size: 1.8rem; font-weight: 700; margin: 0;
}
.stat-label { color: #FFFFFF; font-size: 0.78rem; margin: 4px 0 0 0; }

/* ── Section headers ──────────────────────────────────────────── */
.section-hdr {
    color: #FFFFFF; font-size: 1.1rem; font-weight: 700;
    border-bottom: 1px solid #00CFFF; padding-bottom: 8px;
    margin: 28px 0 16px 0; letter-spacing: 0.5px;
}

/* ── Step badge ───────────────────────────────────────────────── */
.badge {
    background: #00CFFF; color: #0A1B44; border-radius: 50%;
    width: 26px; height: 26px; display: inline-flex;
    align-items: center; justify-content: center;
    font-weight: 700; font-size: 0.8rem; margin-right: 10px;
}

/* ── Early bird banner ────────────────────────────────────────── */
.eb-banner {
    background: linear-gradient(135deg, #071233 0%, #0D2157 100%);
    border: 1px solid #00CFFF; border-radius: 8px;
    padding: 16px 20px; margin: 16px 0;
    display: flex; align-items: center; gap: 16px;
    box-shadow: 0 0 20px rgba(0,207,255,0.1);
}
.eb-pill {
    background: linear-gradient(135deg, #071233 0%, #0D2157 100%);
    border: 1px solid #00CFFF;
    color: #00CFFF; border-radius: 20px;
    padding: 6px 16px; font-size: 0.82rem;
    font-weight: 600; display: inline-block;
    letter-spacing: 0.3px;
}

/* ── Blur gate ────────────────────────────────────────────────── */
.blur-content {
    filter: blur(6px); user-select: none; pointer-events: none;
    color: #FFFFFF; font-family: 'IBM Plex Mono', monospace;
    font-size: 0.85rem; line-height: 2;
}

/* ── Sovereign dashboard ──────────────────────────────────────── */
.sovereign-metric {
    background: #071233;
    border: 1px solid #00CFFF;
    border-top: 2px solid #00CFFF;
    border-radius: 8px; padding: 20px; text-align: center;
}
.sovereign-number {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 2rem; font-weight: 700; color: #00CFFF;
    text-shadow: 0 0 16px rgba(0,207,255,0.35);
}

/* ── Health indicators ────────────────────────────────────────── */
.health-green { color: #00CFFF; font-weight: 700; }
.health-amber { color: #00CFFF; font-weight: 700; }
.health-red   { color: #e85d50; font-weight: 700; }

/* ── Login page brand ─────────────────────────────────────────── */
.brand-mark {
    font-family: 'IBM Plex Mono', monospace;
    color: #00CFFF; font-size: 1.5rem; font-weight: 700;
    letter-spacing: 4px; margin: 0;
}
.login-panel-left {
    background: linear-gradient(160deg, #071233 0%, #0D2157 100%);
    border-right: 1px solid #1A3A6E;
    min-height: 100vh; padding: 48px 40px;
}

/* ── Pricing cards ────────────────────────────────────────────── */
.price-card {
    background: #071233; border: 1px solid #1A3A6E;
    border-radius: 12px; padding: 28px 22px; text-align: center;
    transition: all 0.25s; height: 100%;
}
.price-card:hover {
    transform: translateY(-4px);
    border-color: #00CFFF;
    box-shadow: 0 8px 40px rgba(0,207,255,0.2);
}
.price-card.featured {
    border-color: #00CFFF;
    box-shadow: 0 0 30px rgba(0,207,255,0.15);
    background: linear-gradient(160deg, #0D2157 0%, #071233 100%);
}
.price-amount {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 2.4rem; font-weight: 700; color: #00CFFF;
}
.price-period { color: #FFFFFF; font-size: 0.85rem; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# SECTION 2: CONSTANTS
# ============================================================

MONTHLY_PRICE      = 999
ANNUAL_PRICE       = 8999
EARLY_BIRD_LIMIT   = 5000
EARLY_BIRD_MONTHLY = 999      # locked forever for first 5000
FUTURE_MONTHLY     = 1499     # price after early bird closes
FUTURE_ANNUAL      = 13499
TRIAL_DAYS         = 14
DELTA_THRESHOLD    = 500.0
SITE_URL           = "https://auditdesk-itcrecon.streamlit.app"
LANDING_URL        = "https://itcrecon.in"

# AI NARRATIVE — free credits on signup at console.anthropic.com
# Add to secrets.toml: ANTHROPIC_API_KEY = "sk-ant-..."
# Leave blank to skip narrative (PDF still works perfectly without it)

# Loaded from secrets — never hardcoded in source
def _get_secret(key, fallback=""):
    try:    return st.secrets[key]
    except: return fallback

# Role identifiers (read at runtime, not module load)
def is_sovereign(email):
    return email == _get_secret("SOVEREIGN_EMAIL", "__nobody__")

def is_staff(email):
    return email == _get_secret("STAFF_EMAIL", "__nobody__")

def check_special_login(email, password):
    """
    Returns role string if credentials match a special account,
    None otherwise. Checked BEFORE database lookup.
    """
    sov_email = _get_secret("SOVEREIGN_EMAIL")
    sov_pass  = _get_secret("SOVEREIGN_PASSWORD")
    sta_email = _get_secret("STAFF_EMAIL")
    sta_pass  = _get_secret("STAFF_PASSWORD")
    if email == sov_email and password == sov_pass:
        return "sovereign"
    if email == sta_email and password == sta_pass:
        return "staff"
    return None

# ============================================================
# SECTION 3: DATABASE
# ============================================================

@st.cache_resource
def init_supabase():
    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_SERVICE_KEY"]
    )

@st.cache_resource
def init_razorpay():
    try:
        return razorpay.Client(auth=(
            st.secrets["RAZORPAY_KEY_ID"],
            st.secrets["RAZORPAY_KEY_SECRET"]
        ))
    except:
        return None

try:
    supabase      = init_supabase()
    razor_client  = init_razorpay()
    DB_LIVE       = True
except:
    DB_LIVE = False

# ---- DB helpers ----

def db(table):
    return supabase.table(table)

def now_iso():
    return datetime.now().isoformat()

def log_calculator_use(tool_name, session_id):
    """Track anonymous calculator usage."""
    try:
        db("calculator_events").insert({
            "tool"      : tool_name,
            "session_id": session_id,
            "timestamp" : now_iso()
        }).execute()
    except:
        pass

def get_subscriber_count():
    """How many paying subscribers exist right now."""
    try:
        res = db("subscriptions").select("id", count="exact")\
            .eq("status", "active").execute()
        return res.count or 0
    except:
        return 0

def get_free_user_count():
    try:
        res = db("free_users").select("id", count="exact").execute()
        return res.count or 0
    except:
        return 0

def is_early_bird_open():
    return get_subscriber_count() < EARLY_BIRD_LIMIT

def get_user_subscription(email):
    """Returns subscription row or None."""
    try:
        res = db("subscriptions").select("*")\
            .eq("email", email)\
            .eq("status", "active")\
            .maybe_single().execute()
        return res.data
    except:
        return None

def get_or_create_free_user(email, password):
    """Register or fetch a free user."""
    try:
        existing = db("free_users").select("*")\
            .eq("email", email).maybe_single().execute()
        if existing.data:
            if existing.data["password"] == password:
                return existing.data, None
            return None, "Wrong password."
        # Create new
        db("free_users").insert({
            "email"         : email,
            "password"      : password,
            "registered_at" : now_iso(),
            "trial_started" : None
        }).execute()
        row = db("free_users").select("*")\
            .eq("email", email).single().execute()
        return row.data, None
    except Exception as e:
        return None, str(e)

def start_trial(email):
    try:
        db("free_users").update({
            "trial_started": now_iso()
        }).eq("email", email).execute()
    except:
        pass

def is_trial_active(free_user_row):
    if not free_user_row:
        return False
    ts = free_user_row.get("trial_started")
    if not ts:
        return False
    started = datetime.fromisoformat(ts)
    return (datetime.now() - started).days < TRIAL_DAYS

def days_left_in_trial(free_user_row):
    if not free_user_row:
        return 0
    ts = free_user_row.get("trial_started")
    if not ts:
        return 0
    started = datetime.fromisoformat(ts)
    remaining = TRIAL_DAYS - (datetime.now() - started).days
    return max(0, remaining)

def save_recon_result(email, client_name, summary):
    """Save recon run and return the record id."""
    try:
        link_token = str(uuid.uuid4()).replace("-","")[:24]
        res = db("recon_results").insert({
            "email"         : email,
            "client_name"   : client_name,
            "period"        : summary.get("period",""),
            "itc_available" : summary["itc_available_2b"],
            "itc_claimed"   : summary["itc_claimed_3b"],
            "unclaimed_itc" : summary["unclaimed_itc"],
            "mismatch_count": summary["mismatch_count"],
            "wealth_found"  : summary["wealth_found"],
            "link_token"    : link_token,
            "unlocked"      : False,
            "timestamp"     : now_iso()
        }).execute()
        return res.data[0] if res.data else None
    except Exception as e:
        st.error(f"Save error: {e}")
        return None

def mark_result_unlocked(result_id):
    try:
        db("recon_results").update({"unlocked": True})\
            .eq("id", result_id).execute()
    except:
        pass

def get_client_roster(email):
    try:
        res = db("clients").select("*")\
            .eq("email", email)\
            .order("client_name").execute()
        return res.data or []
    except:
        return []

def add_client(email, name, gstin, entity_type):
    try:
        db("clients").insert({
            "email"      : email,
            "client_name": name,
            "gstin"      : gstin,
            "entity_type": entity_type,
            "added_at"   : now_iso()
        }).execute()
        return True
    except:
        return False

def get_recon_history(email):
    try:
        res = db("recon_results").select("*")\
            .eq("email", email)\
            .order("timestamp", desc=True)\
            .limit(100).execute()
        return res.data or []
    except:
        return []

def get_report_by_token(token):
    try:
        res = db("recon_results").select("*")\
            .eq("link_token", token)\
            .eq("unlocked", True)\
            .maybe_single().execute()
        if res.data:
            return res.data
        res2 = db("recon_results").select("*")\
            .eq("link_token", token)\
            .maybe_single().execute()
        if res2.data:
            try:
                db("recon_results").update({"unlocked": True})\
                    .eq("link_token", token).execute()
            except Exception:
                pass
            return res2.data
        return None
    except:
        return None

def snapshot_sovereign():
    """Save a daily snapshot for trend charts."""
    try:
        subs   = get_subscriber_count()
        frees  = get_free_user_count()
        mrr    = subs * MONTHLY_PRICE
        db("sovereign_snapshots").insert({
            "date"        : date.today().isoformat(),
            "subscribers" : subs,
            "free_users"  : frees,
            "mrr"         : mrr,
            "timestamp"   : now_iso()
        }).execute()
    except:
        pass

def get_sovereign_data():
    try:
        snaps = db("sovereign_snapshots").select("*")\
            .order("date", desc=False)\
            .limit(365).execute()
        recons = db("recon_results").select(
            "wealth_found, timestamp, email, client_name, unlocked"
        ).order("timestamp", desc=True).limit(500).execute()
        calc_events = db("calculator_events").select("tool, timestamp")\
            .order("timestamp", desc=True).limit(10000).execute()
        return {
            "snapshots"   : snaps.data or [],
            "recons"      : recons.data or [],
            "calc_events" : calc_events.data or []
        }
    except Exception as e:
        return {"snapshots": [], "recons": [], "calc_events": [], "error": str(e)}

# ============================================================
# SECTION 4: SESSION STATE
# ============================================================

def init_session():
    defaults = {
        "logged_in"      : False,
        "email"          : None,
        "is_subscriber"  : False,
        "is_trial"       : False,
        "free_user_row"  : None,
        "subscription"   : None,
        "page"           : "home",
        "session_id"     : str(uuid.uuid4())[:16],
        "recon_result"   : None,
        "recon_client"   : None,
        "recon_unlocked" : False,
        "recon_saved_id" : None,
        "calc_uses"      : 0,
        "show_reg_prompt": False,
        "public_token"   : None,
        "role"           : "user",
        "remembered_email": "",
        "session_token"  : "",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session()

# Shorthand
S = st.session_state

def has_full_access():
    return S.is_subscriber

def _save_session_token(email):
    try:
        token = uuid.uuid4().hex
        db("free_users").update({"session_token": token}).eq("email", email).execute()
        S.session_token    = token
        S.remembered_email = email
        return token
    except Exception:
        return ""

def _verify_session_token(email, token):
    if not email or not token:
        return False
    try:
        res = db("free_users").select("session_token").eq("email", email).execute()
        if res.data and len(res.data) > 0:
            return res.data[0].get("session_token", "") == token
    except Exception:
        pass
    return False

def nav(page):
    S.page = page
    S.recon_result   = None
    S.recon_unlocked = False
    S.recon_saved_id = None
    st.rerun()

# ============================================================
# SECTION 5: TRIANGLE RECON ENGINE — FUZZY COLUMN MATCHING
# ============================================================
# Understands any column naming convention automatically.
# "Inv Value", "Invoice Value", "inv_val", "InvValue" — all the same.
# No CA ever needs to reformat their GST export.

import re as _re

def _fuzzy_find_col(df_cols, concepts):
    """
    Fuzzy column resolver.
    Handles abbreviations, spacing, underscores, case differences.
    Works on GST Portal exports, Tally, Zoho, ClearTax, BUSY, etc.
    """
    def norm(s):
        return _re.sub(r"[^a-z0-9]", "", s.lower())

    norm_map = {norm(c): c for c in df_cols}

    # Pass 1: exact normalised match
    for c in concepts:
        if norm(c) in norm_map:
            return norm_map[norm(c)]

    # Pass 2: substring — concept inside column or column inside concept
    for c in concepts:
        k = norm(c)
        for nk, orig in norm_map.items():
            if k in nk or nk in k:
                return orig

    # Pass 3: token overlap scoring
    concept_tokens = set()
    for c in concepts:
        concept_tokens.update(norm(c).split())

    best, best_score = None, 0
    for nk, orig in norm_map.items():
        score = sum(1 for t in concept_tokens if t in nk or nk in t)
        if score > best_score:
            best_score, best = score, orig
    return best if best_score > 0 else None


def _resolve_numeric(df, *concept_groups):
    """Sum numeric values across concept groups (IGST + CGST + SGST)."""
    total = pd.Series(0.0, index=df.index)
    for concepts in concept_groups:
        col = _fuzzy_find_col(df.columns.tolist(), concepts)
        if col:
            total = total + pd.to_numeric(df[col], errors="coerce").fillna(0)
    return total


def _resolve_key_col(df, concepts):
    """Find and normalise the invoice number column."""
    col = _fuzzy_find_col(df.columns.tolist(), concepts)
    if col:
        return df[col].astype(str).str.strip().str.upper()\
                      .str.replace(r"[\s/\-]", "", regex=True)
    return pd.Series(df.index.astype(str), index=df.index)


def run_triangle_recon(gstr1_df, gstr2b_df, gstr3b_df,
                       threshold=DELTA_THRESHOLD, period=""):
    """
    Correct Triangle Recon — produces 5 distinct outputs:
    A. ITC Opportunity   = max(2B - 3B, 0)   — recoverable wealth
    B. ITC Overclaim Risk= max(3B - 2B, 0)   — compliance exposure
    C. Missing in 2B     = in GSTR-1 but not in 2B (supplier didn't upload)
    D. Missing in GSTR-1 = in 2B but not in GSTR-1 (sales mismatch)
    E. Value mismatches  = same invoice, different tax amount

    Composite key matching: Supplier GSTIN + Invoice No + Date
    GSTIN always string — never numeric.
    """
    IGST = ["itc_igst","igst","integrated_tax","integrated tax","igst_amount",
            "igst amt","itc igst","integrated tax amount","igst_itc",
            "igst_availed","igst availed","integrated gst"]
    CGST = ["itc_cgst","cgst","central_tax","central tax","cgst_amount",
            "cgst amt","itc cgst","central tax amount","cgst_itc",
            "cgst_availed","cgst availed","central gst"]
    SGST = ["itc_sgst","sgst","state_tax","state tax","sgst_amount",
            "sgst amt","itc sgst","state tax amount","sgst_itc",
            "sgst_availed","sgst availed","state gst",
            "utgst","ut tax","union territory tax","ut gst"]
    INV  = ["invoice_no","invoice_number","inv_no","inv no","bill_no",
            "bill no","invoice","voucher_no","document_no","doc_no",
            "inv","bill number","invoice no","invno","billno"]
    DATE = ["invoice_date","inv_date","bill_date","date","invoice date",
            "bill date","invdate","voucher_date","doc_date"]
    GST_NO = ["supplier_gstin","gstin","vendor_gstin","party_gstin",
              "gst_no","supplier gst","vendor gst","gstin_of_supplier",
              "suppliers gstin","ctin","counterparty gstin","gstn",
              "supplier gstin","gstin no"]
    IGST_3B = ["itc_claimed_igst","itc_availed_igst","itc_igst","igst",
               "integrated tax itc","itc integrated","igst itc","igst claimed",
               "igst_itc_claimed"]
    CGST_3B = ["itc_claimed_cgst","itc_availed_cgst","itc_cgst","cgst",
               "central tax itc","itc central","cgst itc","cgst claimed",
               "cgst_itc_claimed"]
    SGST_3B = ["itc_claimed_sgst","itc_availed_sgst","itc_sgst","sgst",
               "state tax itc","itc state","sgst itc","sgst claimed",
               "utgst","sgst_itc_claimed"]

    # ── Tax amounts ────────────────────────────────────────────────
    gstr2b_df = gstr2b_df.copy()
    gstr1_df  = gstr1_df.copy()
    gstr3b_df = gstr3b_df.copy()

    gstr2b_df["_itc"] = _resolve_numeric(gstr2b_df, IGST, CGST, SGST)
    gstr1_df["_tax"]  = _resolve_numeric(gstr1_df,  IGST, CGST, SGST)

    # ── Resolve column names ───────────────────────────────────────
    gstin_col_2b = _fuzzy_find_col(gstr2b_df.columns.tolist(), GST_NO)
    gstin_col_1  = _fuzzy_find_col(gstr1_df.columns.tolist(),  GST_NO)
    inv_col_2b   = _fuzzy_find_col(gstr2b_df.columns.tolist(), INV)
    inv_col_1    = _fuzzy_find_col(gstr1_df.columns.tolist(),  INV)
    date_col_2b  = _fuzzy_find_col(gstr2b_df.columns.tolist(), DATE)
    date_col_1   = _fuzzy_find_col(gstr1_df.columns.tolist(),  DATE)

    # ── Build composite key: GSTIN + InvNo + Date ─────────────────
    # GSTIN — always string, never numeric
    def clean_gstin(df, col):
        if col and col in df.columns:
            return df[col].astype(str).str.strip().str.upper()                          .str.replace(r"[^A-Z0-9]", "", regex=True)                          .replace("", "UNKNOWN").replace("NAN", "UNKNOWN")                          .replace("NONE", "UNKNOWN").replace("0", "UNKNOWN")
        return pd.Series(["UNKNOWN"] * len(df), index=df.index)

    def clean_inv(df, col):
        if col and col in df.columns:
            return df[col].astype(str).str.strip().str.upper()                          .str.replace(r"[\s/\-]", "", regex=True)
        return pd.Series(df.index.astype(str), index=df.index)

    def clean_date(df, col):
        if col and col in df.columns:
            # Normalise date to YYYY-MM-DD string — handles most formats
            try:
                return pd.to_datetime(df[col], errors="coerce")                         .dt.strftime("%Y-%m-%d").fillna("NODATE")
            except Exception:
                return df[col].astype(str).str.strip()
        return pd.Series(["NODATE"] * len(df), index=df.index)

    gstr2b_df["_gstin"] = clean_gstin(gstr2b_df, gstin_col_2b)
    gstr2b_df["_inv"]   = clean_inv(gstr2b_df,   inv_col_2b)
    gstr2b_df["_date"]  = clean_date(gstr2b_df,  date_col_2b)
    gstr2b_df["_ckey"]  = (gstr2b_df["_gstin"] + "||" +
                           gstr2b_df["_inv"]   + "||" +
                           gstr2b_df["_date"])

    gstr1_df["_gstin"]  = clean_gstin(gstr1_df, gstin_col_1)
    gstr1_df["_inv"]    = clean_inv(gstr1_df,   inv_col_1)
    gstr1_df["_date"]   = clean_date(gstr1_df,  date_col_1)
    gstr1_df["_ckey"]   = (gstr1_df["_gstin"] + "||" +
                           gstr1_df["_inv"]   + "||" +
                           gstr1_df["_date"])

    # ── Outer merge on composite key ───────────────────────────────
    merged = pd.merge(
        gstr2b_df[["_ckey","_gstin","_inv","_date","_itc"]],
        gstr1_df [["_ckey","_gstin","_inv","_date","_tax"]],
        on="_ckey", how="outer",
        suffixes=("_2b","_1")
    )

    # Fill numeric nulls with 0; keep GSTIN as string
    merged["_itc"]  = merged["_itc"].fillna(0.0)
    merged["_tax"]  = merged["_tax"].fillna(0.0)
    merged["_delta"]= merged["_itc"] - merged["_tax"]

    # Resolve GSTIN display (prefer 2B, fallback to 1)
    merged["_gstin_disp"] = merged["_gstin_2b"].combine_first(
                             merged["_gstin_1"]).fillna("UNKNOWN")
    merged["_inv_disp"]   = merged["_inv_2b"].combine_first(
                             merged["_inv_1"]).fillna("")
    merged["_date_disp"]  = merged["_date_2b"].combine_first(
                             merged["_date_1"]).fillna("")

    # ── Classify each row ──────────────────────────────────────────
    def classify(row):
        itc, tax = row["_itc"], row["_tax"]
        if tax > 0 and itc == 0:
            return "Missing in 2B"       # supplier filed 1 but not 2B
        if itc > 0 and tax == 0:
            return "Missing in GSTR-1"   # in 2B but no matching GSTR-1
        if abs(row["_delta"]) >= threshold:
            return "Value Mismatch"      # same invoice, different amount
        return "Matched"

    merged["_type"] = merged.apply(classify, axis=1)

    # ── Risk rating ────────────────────────────────────────────────
    def risk(delta):
        a = abs(delta)
        if a > 50000: return "🔴 Critical"
        if a > 10000: return "🟠 High"
        if a > 1000:  return "🟡 Medium"
        return "🟢 Low"

    merged["_risk"] = merged["_delta"].apply(risk)

    # ── 3B ITC claimed ─────────────────────────────────────────────
    itc_claimed   = float(_resolve_numeric(
        gstr3b_df, IGST_3B, CGST_3B, SGST_3B).sum())
    itc_available = float(gstr2b_df["_itc"].sum())

    # ── A. ITC Opportunity (recoverable wealth) ────────────────────
    itc_opportunity = round(max(0.0, itc_available - itc_claimed), 2)

    # ── B. ITC Overclaim Risk (compliance exposure) ────────────────
    itc_overclaim   = round(max(0.0, itc_claimed - itc_available), 2)

    # ── C/D/E. Invoice-level classification ───────────────────────
    missing_in_2b  = merged[merged["_type"] == "Missing in 2B"].copy()
    missing_in_1   = merged[merged["_type"] == "Missing in GSTR-1"].copy()
    value_mismatch = merged[merged["_type"] == "Value Mismatch"].copy()

    missing_2b_sum  = round(float(missing_in_2b["_tax"].sum()), 2)
    missing_1_sum   = round(float(missing_in_1["_itc"].sum()), 2)
    value_mm_sum    = round(float(value_mismatch["_delta"].abs().sum()), 2)

    # Total invoice gap
    invoice_gap = round(missing_2b_sum + missing_1_sum + value_mm_sum, 2)

    # ── Build display tables ───────────────────────────────────────
    def make_display(df, amount_col, label):
        if df.empty:
            return pd.DataFrame()
        out = pd.DataFrame()
        out["Invoice No."]    = df["_inv_disp"]
        out["Supplier GSTIN"] = df["_gstin_disp"]
        out["Date"]           = df["_date_disp"]
        out["ITC in 2B (₹)"]  = df["_itc"].round(2)
        out["Tax in 1 (₹)"]   = df["_tax"].round(2)
        out["Delta (₹)"]      = df["_delta"].round(2)
        out["Type"]           = df["_type"]
        out["Risk"]           = df["_risk"]
        try:
            return out.sort_values("Delta (₹)", key=lambda x: x.abs(), ascending=False)
        except Exception:
            return out

    disp_missing_2b  = make_display(missing_in_2b,  "_tax",   "Missing in 2B")
    disp_missing_1   = make_display(missing_in_1,   "_itc",   "Missing in GSTR-1")
    disp_value_mm    = make_display(value_mismatch, "_delta", "Value Mismatch")

    # Combined for PDF — all mismatches together
    all_mismatches = pd.concat(
        [disp_missing_2b, disp_missing_1, disp_value_mm],
        ignore_index=True
    ).sort_values("Delta (₹)", key=abs, ascending=False)

    # Total unique invoices = union of both files (not max of either)
    all_keys        = set(gstr2b_df["_ckey"].tolist()) | set(gstr1_df["_ckey"].tolist())
    total_invoices  = len(all_keys)
    mismatch_total  = len(missing_in_2b) + len(missing_in_1) + len(value_mismatch)
    matched_count   = total_invoices - mismatch_total
    recon_integrity = round(max(0, matched_count) / total_invoices * 100, 1) if total_invoices else 0
    overclaim_pct   = round(itc_overclaim   / itc_available * 100, 1) if itc_available else 0
    mismatch_pct    = round(mismatch_total  / total_invoices * 100, 1) if total_invoices else 0
    net_exposure    = round(itc_overclaim + value_mm_sum, 2)
    # Sec 50 interest estimate — 18% per annum on excess ITC (daily = 18/365)
    sec50_daily_rate = 18.0 / 365 / 100
    sec50_30d        = round(itc_overclaim * sec50_daily_rate * 30, 2)
    sec50_90d        = round(itc_overclaim * sec50_daily_rate * 90, 2)

    # ── Supplier Intelligence ─────────────────────────────────────
    # Derived entirely from existing merged data — no new uploads needed
    # Filing rate per supplier = how reliably they appear in GSTR-2B
    # Risk score = weighted: ITC at risk (60%) + filing failure rate (40%)

    def build_supplier_intelligence(merged_df, gstr1_df, gstr2b_df):
        """
        Per-supplier stats across the reconciliation universe.
        Every metric comes from data already in the engine.
        """
        # Total invoices per supplier in GSTR-1 (what they filed)
        filed_per_gstin = (gstr1_df.groupby("_gstin")
                           .size().reset_index(name="invoices_in_1"))

        # Missing in 2B per supplier (what didn't reach us)
        missing_grp = (merged_df[merged_df["_type"] == "Missing in 2B"]
                       .groupby("_gstin_disp")
                       .agg(
                           invoices_missing=("_ckey", "count"),
                           itc_at_risk=("_tax", "sum"),
                       ).reset_index()
                       .rename(columns={"_gstin_disp": "_gstin"}))

        if missing_grp.empty:
            return pd.DataFrame(), {}

        # Merge to get filing context
        si = pd.merge(missing_grp,
                      filed_per_gstin[["_gstin","invoices_in_1"]],
                      on="_gstin", how="left")
        si["invoices_in_1"] = si["invoices_in_1"].fillna(si["invoices_missing"])

        # Filing rate: what % of their invoices actually appeared in 2B
        si["invoices_total_for_gstin"] = si["invoices_in_1"]
        si["invoices_filed_in_2b"]  = (si["invoices_in_1"] - si["invoices_missing"]).clip(lower=0)
        si["filing_rate_pct"] = (
            si["invoices_filed_in_2b"] / si["invoices_in_1"] * 100
        ).clip(0, 100).round(1)

        # Risk score: 60% weight on ITC amount, 40% on filing failure rate
        max_itc   = si["itc_at_risk"].max() or 1
        si["_itc_norm"]  = si["itc_at_risk"] / max_itc          # 0–1
        si["_fail_norm"] = 1 - (si["filing_rate_pct"] / 100)    # 0–1 (higher = worse)
        si["risk_score"] = ((si["_itc_norm"] * 0.60) +
                            (si["_fail_norm"] * 0.40)) * 100
        si["risk_score"] = si["risk_score"].round(1)

        # Risk label
        def risk_label(row):
            if row["risk_score"] >= 70 or row["filing_rate_pct"] < 30:
                return "🔴 Critical"
            if row["risk_score"] >= 45 or row["filing_rate_pct"] < 60:
                return "🟠 High"
            if row["risk_score"] >= 20:
                return "🟡 Medium"
            return "🟢 Low"
        si["risk_label"] = si.apply(risk_label, axis=1)

        # Repeat defaulter flag: filed < 50% of their own invoices
        si["repeat_defaulter"] = si["filing_rate_pct"] < 50

        # Sort by ITC at risk descending — CA cares about money first
        si = si.sort_values("itc_at_risk", ascending=False).reset_index(drop=True)

        # Filter out NaN/UNKNOWN GSTIN rows — artifacts from outer merge with no GSTIN
        si["_gstin"] = si["_gstin"].astype(str).str.strip()
        si = si[~si["_gstin"].isin(["UNKNOWN","nan","NaN","","NONE","0","None"])].copy()
        si = si[si["invoices_missing"] > 0].copy()  # must have actual missed invoices
        si = si.reset_index(drop=True)
        si.index = si.index + 1  # 1-based rank

        # Concentration stats
        total_gap   = si["itc_at_risk"].sum() or 1
        top5_gap    = si.head(5)["itc_at_risk"].sum()
        top5_pct    = round(top5_gap / total_gap * 100, 1)
        top1_gstin  = si.iloc[0]["_gstin"]      if len(si) > 0 else ""
        top1_amount = si.iloc[0]["itc_at_risk"]  if len(si) > 0 else 0
        repeat_count= int(si["repeat_defaulter"].sum())

        intel_stats = {
            "supplier_count"        : len(si),
            "top5_concentration_pct": top5_pct,
            "top1_gstin"            : top1_gstin,
            "top1_amount"           : round(float(top1_amount), 2),
            "repeat_defaulter_count": repeat_count,
        }

        # Display table
        display = pd.DataFrame()
        display["Rank"]            = si.index
        display["Supplier GSTIN"]  = si["_gstin"]
        display["Invoices Missed"] = si["invoices_missing"].astype(int)
        display["ITC at Risk (₹)"] = si["itc_at_risk"].round(0).astype(int)
        display["Filing Rate"]     = si["filing_rate_pct"].apply(lambda x: f"{x:.0f}%")
        display["Risk Score"]      = si["risk_score"].apply(lambda x: f"{x:.0f}/100")
        display["Risk"]            = si["risk_label"]
        display["Repeat Defaulter"]= si["repeat_defaulter"].apply(
                                        lambda x: "⚠️ Yes" if x else "—")
        return display, intel_stats

    supplier_intel_df, intel_stats = build_supplier_intelligence(
        merged, gstr1_df, gstr2b_df
    )

    summary = {
        "period"            : period,
        "invoices_2b"       : len(gstr2b_df),
        "invoices_1"        : len(gstr1_df),
        "invoices_total"    : total_invoices,   # union of both files — correct denominator
        # A — opportunity
        "itc_available_2b"  : round(itc_available, 2),
        "itc_claimed_3b"    : round(itc_claimed, 2),
        "itc_opportunity"   : itc_opportunity,
        # B — risk
        "itc_overclaim"     : itc_overclaim,
        "overclaim_pct"     : overclaim_pct,
        # C/D/E — invoice level
        "missing_in_2b_count" : len(missing_in_2b),
        "missing_in_2b_sum"   : missing_2b_sum,
        "missing_in_1_count"  : len(missing_in_1),
        "missing_in_1_sum"    : missing_1_sum,
        "value_mm_count"      : len(value_mismatch),
        "value_mm_sum"        : value_mm_sum,
        "invoice_gap"         : invoice_gap,
        "mismatch_pct"        : mismatch_pct,
        # Composite scores
        "recon_integrity"   : recon_integrity,
        "net_exposure"      : net_exposure,
        "sec50_30d"         : sec50_30d,
        "sec50_90d"         : sec50_90d,
        # Legacy fields
        "mismatch_count"    : mismatch_total,
        "mismatch_sum"      : invoice_gap,
        "unclaimed_itc"     : itc_opportunity,
        "wealth_found"      : itc_opportunity,
        # Supplier intelligence
        "supplier_count"            : intel_stats.get("supplier_count", 0),
        "top5_concentration_pct"    : intel_stats.get("top5_concentration_pct", 0),
        "top1_gstin"                : intel_stats.get("top1_gstin", ""),
        "top1_amount"               : intel_stats.get("top1_amount", 0),
        "repeat_defaulter_count"    : intel_stats.get("repeat_defaulter_count", 0),
    }
    return {
        "summary"           : summary,
        "mismatches"        : all_mismatches,
        "missing_in_2b"     : disp_missing_2b,
        "missing_in_1"      : disp_missing_1,
        "value_mismatches"  : disp_value_mm,
        "supplier_intel"    : supplier_intel_df,   # NEW — ranked supplier table
    }


# ============================================================
# SECTION 6: PDF GENERATOR
# ============================================================



# ============================================================
# SECTION 5c: EMAIL SYSTEM
# Uses Gmail SMTP (free, 500 emails/day)
# Switch to domain email later — change secrets.toml only
# ============================================================

def _send_email(to_email: str, subject: str, html_body: str) -> bool:
    """Core email sender. Returns True if sent, False if skipped/failed."""
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    sender       = _get_secret("GMAIL_SENDER", "")
    app_password = _get_secret("GMAIL_APP_PASSWORD", "")

    if not sender or not app_password:
        return False  # Not configured — skip silently

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = f"Audit Desk <{sender}>"
        msg["To"]      = to_email
        msg.attach(MIMEText(html_body, "html", "utf-8"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(sender, app_password)
            smtp.sendmail(sender, to_email, msg.as_string())
        return True
    except Exception:
        return False  # Never crash the app over an email


def _email_html_wrapper(headline: str, body_html: str,
                         cta_text: str = "", cta_url: str = "") -> str:
    """Wraps content in a consistent dark-themed email template."""
    cta_block = f"""
        <div style="text-align:center; margin:28px 0;">
            <a href="{cta_url}"
               style="background:#00CFFF; color:white; text-decoration:none;
                      padding:14px 32px; border-radius:8px; font-weight:700;
                      font-size:15px; display:inline-block;">
            {cta_text}
            </a>
        </div>
    """ if cta_text and cta_url else ""

    return f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
</head>
<body style="margin:0;padding:0;background:#071233;
             font-family:'Segoe UI',Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0"
       style="background:#071233;padding:40px 16px;">
<tr><td align="center">
<table width="600" cellpadding="0" cellspacing="0"
       style="background:#071233;border:1px solid #1A3A6E;border-radius:12px;
              overflow:hidden;max-width:600px;width:100%;">

  <!-- Header -->
  <tr>
    <td style="background:linear-gradient(135deg,#071233 0%,#071233 100%);
               padding:28px 32px;border-bottom:2px solid #00CFFF;">
      <p style="color:#00CFFF;font-family:monospace;font-size:11px;
                letter-spacing:3px;margin:0 0 4px 0;">AUDIT DESK™</p>
      <h1 style="color:#FFFFFF;margin:0;font-size:22px;
                 font-weight:700;line-height:1.3;">{headline}</h1>
    </td>
  </tr>

  <!-- Body -->
  <tr>
    <td style="padding:28px 32px;">
      {body_html}
      {cta_block}
    </td>
  </tr>

  <!-- Footer -->
  <tr>
    <td style="padding:20px 32px;border-top:1px solid #1A3A6E;
               background:#071233;">
      <p style="color:#FFFFFF;font-size:12px;margin:0;line-height:1.6;
                text-align:center;">
        Audit Desk · ITC Forensic Engine for Practising CAs<br>
        itcrecon.in · support: auditdesk.hq@gmail.com<br>
        <span style="color:#444;">
        You received this because you created an account on Audit Desk.
        </span>
      </p>
    </td>
  </tr>

</table>
</td></tr>
</table>
</body>
</html>"""


def send_welcome_email_free_user(to_email: str):
    """
    Sent immediately when someone creates a free account.
    Goal: warm them up, explain Early Bird, make them want to subscribe.
    Designed to be forwarded to CA colleagues.
    """
    eb_open = is_early_bird_open()

    eb_block = """
        <div style="background:#071233;border:1px solid #00CFFF;
                    border-radius:8px;padding:18px 22px;margin:20px 0;">
          <p style="color:#00CFFF;font-weight:700;font-size:15px;
                    margin:0 0 10px 0;">🔥 Early Bird offer — both plans locked forever</p>
          <p style="color:#FFFFFF;font-size:14px;line-height:1.8;margin:0;">
            Subscribe during Early Bird and your price is locked permanently —
            whether you choose monthly (₹999) or annual (₹8,999).<br><br>
            This is not a introductory discount that expires.
            This is <strong>your price, forever</strong>, as long as your
            subscription stays active.<br><br>
            When Audit Desk raises prices for new subscribers,
            you keep paying what you pay today. No surprises. No renegotiation.
          </p>
        </div>
    """ if eb_open else ""

    body = f"""
        <p style="color:#FFFFFF;font-size:15px;line-height:1.8;margin:0 0 20px 0;">
          Welcome. Your Audit Desk account is ready.
        </p>

        <!-- What you have right now -->
        <div style="background:#0D2157;border-left:3px solid #00CFFF;
                    border-radius:0 8px 8px 0;padding:16px 20px;margin:0 0 16px 0;">
          <p style="color:#00CFFF;font-weight:700;margin:0 0 10px 0;">
            Free with your account — always:</p>
          <p style="color:#FFFFFF;font-size:14px;line-height:2;margin:0;">
            🧮 &nbsp;GST Calculator (exclusive + inclusive modes)<br>
            📅 &nbsp;MSME 45-Day Checker — Section 43B(h) compliance<br>
            💰 &nbsp;Section 50 GST Late Payment Interest Calculator<br>
            🔍 &nbsp;HSN / SAC Code Finder
          </p>
        </div>

        <!-- What the trial unlocks -->
        <div style="background:#0D2157;border-left:3px solid #00CFFF;
                    border-radius:0 8px 8px 0;padding:16px 20px;margin:0 0 16px 0;">
          <p style="color:#00CFFF;font-weight:700;margin:0 0 10px 0;">
            Your 14-day free trial — activate when ready:</p>
          <p style="color:#FFFFFF;font-size:14px;line-height:2;margin:0;">
            📐 &nbsp;Triangle Recon — GSTR-1 × GSTR-2B × GSTR-3B in 30 seconds<br>
            📄 &nbsp;Audit Desk Certified PDF — with your firm name<br>
            🔗 &nbsp;Shareable Client Link — send recovery proof directly to client<br>
            📊 &nbsp;Monthly ITC Health Dashboard — all clients at a glance
          </p>
        </div>

        <!-- What Triangle Recon actually finds -->
        <p style="color:#FFFFFF;font-size:14px;line-height:1.8;margin:0 0 16px 0;">
          Most CAs we work with find between ₹50,000 and ₹3,00,000 in unclaimed
          Input Tax Credit per client per quarter. That is money sitting in your
          client's GST account — not claimed, not recovered, not earning anything.
          Audit Desk finds it in under 30 seconds. You send them a link.
          They see the number. You look like the CA who pays attention.
        </p>

        {eb_block}

        <!-- Forward ask -->
        <div style="background:#0D2157;border:1px solid #1A3A6E;
                    border-radius:8px;padding:16px 20px;margin:20px 0;">
          <p style="color:#FFFFFF;font-size:13px;line-height:1.8;margin:0;">
            💬 &nbsp;<strong style="color:#FFFFFF;">Know another CA</strong>
            spending hours on manual reconciliation? Forward this email.
            They get the same free account, same calculators, same Early Bird
            offer — and you get the credit for introducing them to a better way
            of working.
          </p>
        </div>
    """

    html = _email_html_wrapper(
        headline = "Your Audit Desk account is ready",
        body_html = body,
        cta_text  = "Open Audit Desk →",
        cta_url   = SITE_URL
    )
    _send_email(to_email, "Welcome to Audit Desk — your account is ready", html)


def send_welcome_email_subscriber(to_email: str, plan: str,
                                   early_bird: bool, amount: int):
    """
    Sent when someone converts from free to paid.
    Confirms the Early Bird lock in writing — reduces cancellation anxiety,
    gives them something to forward to CA colleagues.
    """
    plan_label  = "Annual" if plan == "annual" else "Monthly"
    plan_price  = f"₹{amount:,}/{'year' if plan == 'annual' else 'month'}"
    next_charge = "in 12 months" if plan == "annual" else "next month"

    eb_block = f"""
        <div style="background:#071233;border:1px solid #00CFFF;
                    border-radius:8px;padding:18px 22px;margin:20px 0;">
          <p style="color:#00CFFF;font-weight:700;font-size:15px;
                    margin:0 0 10px 0;">🔥 Your Early Bird price is confirmed and locked</p>
          <p style="color:#FFFFFF;font-size:14px;line-height:1.8;margin:0;">
            You subscribed during the Early Bird period.
            Your {plan_label} price of <strong>{plan_price}</strong> is now
            <strong>locked permanently</strong> — this is our written commitment to you.<br><br>
            When Audit Desk raises prices for new subscribers, nothing changes
            for you. Your next charge ({next_charge}) will be exactly {plan_price}.<br><br>
            <strong>One thing to remember:</strong> The Early Bird rate stays
            as long as your subscription is continuous. If you cancel and
            rejoin later, you will be placed on the price applicable at that time.
            So stay subscribed — and keep winning for your clients.
          </p>
        </div>
    """ if early_bird else f"""
        <div style="background:#0D2157;border:1px solid #1A3A6E;
                    border-radius:8px;padding:16px 20px;margin:16px 0;">
          <p style="color:#FFFFFF;font-size:14px;margin:0;">
            <strong>Your plan:</strong> {plan_label} · {plan_price}<br>
            <strong>Next charge:</strong> {next_charge} · same amount
          </p>
        </div>
    """

    body = f"""
        <p style="color:#FFFFFF;font-size:15px;line-height:1.8;margin:0 0 20px 0;">
          Your Audit Desk subscription is now active. You have full access to
          everything on the platform.
        </p>

        {eb_block}

        <!-- First recon guide -->
        <div style="background:#0D2157;border-left:3px solid #00CFFF;
                    border-radius:0 8px 8px 0;padding:18px 22px;margin:20px 0;">
          <p style="color:#00CFFF;font-weight:700;margin:0 0 12px 0;">
            Run your first recon in 5 minutes:</p>
          <p style="color:#FFFFFF;font-size:14px;line-height:2.2;margin:0;">
            <span style="color:#00CFFF;">1.</span>
            &nbsp;Log in to Audit Desk<br>
            <span style="color:#00CFFF;">2.</span>
            &nbsp;Add your first client under Client Roster<br>
            <span style="color:#00CFFF;">3.</span>
            &nbsp;Download GSTR-1, GSTR-2B, GSTR-3B from GST Portal
            (Returns → Download)<br>
            <span style="color:#00CFFF;">4.</span>
            &nbsp;Upload all three under Triangle Recon<br>
            <span style="color:#00CFFF;">5.</span>
            &nbsp;See the unclaimed ITC in under 30 seconds<br>
            <span style="color:#00CFFF;">6.</span>
            &nbsp;Download the certified PDF · Send the client link
          </p>
        </div>

        <!-- What to expect -->
        <p style="color:#FFFFFF;font-size:14px;line-height:1.8;margin:0 0 16px 0;">
          CAs using Audit Desk typically find ₹50,000 to ₹3,00,000 in unclaimed
          ITC per client per quarter. At a standard 10% recovery fee, one scan
          more than pays for an entire year of Audit Desk. Run it for your ten
          largest clients this week.
        </p>

        <!-- Referral ask -->
        <div style="background:#0D2157;border:1px solid #1A3A6E;
                    border-radius:8px;padding:16px 20px;margin:20px 0;">
          <p style="color:#FFFFFF;font-size:13px;line-height:1.8;margin:0;">
            💬 &nbsp;<strong style="color:#FFFFFF;">Enjoying Audit Desk?</strong>
            Tell a CA colleague. They get the same Early Bird pricing you did —
            and the more CAs use the platform, the richer the benchmarks and
            intelligence it generates for everyone.
          </p>
        </div>
    """

    subject = (
        f"Your Audit Desk {'Early Bird ' if early_bird else ''}subscription is confirmed"
    )
    html = _email_html_wrapper(
        headline  = "You're subscribed. Let's find some money.",
        body_html = body,
        cta_text  = "Open Audit Desk →",
        cta_url   = SITE_URL
    )
    _send_email(to_email, subject, html)


# ============================================================
# SECTION 5b: AI NARRATIVE ENGINE
# Free tier: uses Anthropic API credits (no card until credits run out)
# Degrades gracefully — PDF still works if API unavailable
# ============================================================

def generate_ai_narrative(client_name, summary, mismatches_df):
    """
    Calls Claude API to write a professional audit narrative
    based on the recon numbers. Uses free API credits — zero cost
    until credits are exhausted, at which point it returns None
    and the PDF generates without the narrative section.

    Cost when paid: ~₹2–5 per narrative (tiny vs ₹999 subscription).
    """
    if not ANTHROPIC_AVAILABLE:
        return None

    try:
        api_key = _get_secret("ANTHROPIC_API_KEY", "")
        if not api_key:
            return None

        client = _anthropic.Anthropic(api_key=api_key)

        # Build top mismatches summary for context
        top_mismatches = ""
        if mismatches_df is not None and not mismatches_df.empty:
            top3 = mismatches_df.head(3)
            rows = []
            for _, row in top3.iterrows():
                inv  = row.get("Invoice No.", "—")
                mval = row.get("Mismatch (₹)", 0)
                gstin= row.get("Supplier GSTIN", "")
                rows.append(
                    f"Invoice {inv}"
                    + (f" from GSTIN {gstin}" if gstin else "")
                    + f": ₹{float(str(mval).replace('₹','').replace(',','') or 0):,.0f} mismatch"
                )
            top_mismatches = "; ".join(rows)

        period      = summary.get("period", "the period")
        unclaimed   = summary.get("unclaimed_itc", 0)
        available   = summary.get("itc_available_2b", 0)
        claimed     = summary.get("itc_claimed_3b", 0)
        mismatches  = summary.get("mismatch_count", 0)
        wealth      = summary.get("wealth_found", 0)

        prompt = f"""You are a senior Chartered Accountant writing a professional GST audit narrative for a client report. Write a clear, precise 3-paragraph audit finding in formal but readable English.

Client: {client_name}
Period: {period}
ITC Available in GSTR-2B: ₹{available:,.2f}
ITC Claimed in GSTR-3B: ₹{claimed:,.2f}
Unclaimed ITC: ₹{unclaimed:,.2f}
Invoice Mismatches Found: {mismatches}
Total Wealth Identified: ₹{wealth:,.2f}
Top Mismatches: {top_mismatches if top_mismatches else "Invoice-level data not available"}

Write exactly 3 paragraphs:
Paragraph 1: What was found (the numbers, what they mean for the client).
Paragraph 2: The likely cause (vendor filing delays, reconciliation gaps, clerical errors — infer from data).
Paragraph 3: Recommended action (specific GST filing steps the CA should take).

Write in third person. Be specific with rupee amounts. Do not use bullet points. Do not add any heading or label. Just the three paragraphs. Maximum 200 words total."""

        message = client.messages.create(
            model="claude-haiku-4-5-20251001",  # cheapest model — still excellent
            max_tokens=400,
            messages=[{"role": "user", "content": prompt}]
        )

        narrative = message.content[0].text.strip()
        return narrative if narrative else None

    except Exception:
        # API error, quota exceeded, key missing — silent fail
        # PDF generates normally without the narrative
        return None


def _get_unicode_fonts():
    """
    Register Unicode fonts that support ₹ symbol.
    Tries multiple locations — Windows, Linux, Mac.
    Falls back to Helvetica with ASCII rupee if no TTF found.
    """
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    import os

    candidates = [
        # Windows
        ("C:/Windows/Fonts/arial.ttf",     "C:/Windows/Fonts/arialbd.ttf"),
        ("C:/Windows/Fonts/calibri.ttf",   "C:/Windows/Fonts/calibrib.ttf"),
        ("C:/Windows/Fonts/verdana.ttf",   "C:/Windows/Fonts/verdanab.ttf"),
        # Linux
        ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
         "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
        ("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
         "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"),
        # Mac
        ("/Library/Fonts/Arial.ttf",       "/Library/Fonts/Arial Bold.ttf"),
        ("/System/Library/Fonts/Helvetica.ttc", None),
    ]
    for reg, bold in candidates:
        if os.path.exists(reg):
            try:
                pdfmetrics.registerFont(TTFont("UniFont",     reg))
                if bold and os.path.exists(bold):
                    pdfmetrics.registerFont(TTFont("UniFont-Bold", bold))
                else:
                    pdfmetrics.registerFont(TTFont("UniFont-Bold", reg))
                return "UniFont", "UniFont-Bold"
            except Exception:
                continue
    return "Helvetica", "Helvetica-Bold"  # fallback — ₹ shows as box but no crash


def _pdf_rupee(amount):
    """Format rupee amount — always ASCII Rs. for PDF safety."""
    return f"Rs.{amount:,.2f}"

def _pdf_rupee_int(amount):
    return f"Rs.{amount:,.0f}"

def _clean_risk(risk_str):
    """Strip emojis from risk label for PDF."""
    return (str(risk_str)
            .replace("🔴 ", "").replace("🟠 ", "")
            .replace("🟡 ", "").replace("🟢 ", "")
            .replace("🔴", "").replace("🟠", "")
            .replace("🟡", "").replace("🟢", ""))

def _risk_color(risk_str):
    """Return HEX color for risk label."""
    s = str(risk_str).lower()
    if "critical" in s: return colors.HexColor("#e85d50")
    if "high"     in s: return colors.HexColor("#00CFFF")
    if "medium"   in s: return colors.HexColor("#00CFFF")
    return colors.HexColor("#3fb950")


def generate_pdf(client_name, ca_name, summary, mismatches_df,
                 link_token="", ai_narrative=None, supplier_intel_df=None):
    buf  = BytesIO()
    doc  = SimpleDocTemplate(buf, pagesize=A4,
                             leftMargin=0.7*inch, rightMargin=0.7*inch,
                             topMargin=0.7*inch, bottomMargin=0.7*inch)

    # Register best available Unicode font
    FONT, FONT_BOLD = _get_unicode_fonts()

    styles = getSampleStyleSheet()
    # Blue Spectrum — readable on white PDF background
    NAVY         = colors.HexColor("#005DAA")    # Deep Azure — brand + HR
    GOLD         = colors.HexColor("#005DAA")    # HR line
    TBL_HDR      = colors.HexColor("#FFFFFF")    # Pale Sky — table header BG
    TBL_HDR_TEXT = colors.HexColor("#005DAA")    # Deep Azure — header text

    S_brand = ParagraphStyle("Brand", fontName=FONT_BOLD,
                              textColor=NAVY, fontSize=22,
                              leading=28, spaceAfter=2)
    S_sub  = ParagraphStyle("Sub",  fontName=FONT,
                             textColor=colors.HexColor("#005DAA"), fontSize=9,
                             leading=14, spaceBefore=0)
    S_body = ParagraphStyle("Body", fontName=FONT,
                             textColor=colors.HexColor("#1a1a2e"),
                             fontSize=10, leading=16)
    S_bold = ParagraphStyle("Bold", fontName=FONT_BOLD,
                             textColor=colors.HexColor("#0A1B44"),
                             fontSize=10, leading=16)
    S_cert = ParagraphStyle("Cert", fontName=FONT,
                             textColor=colors.HexColor("#334155"),
                             fontSize=8, alignment=1)
    PS_cell = ParagraphStyle("Cell",
                  fontName=FONT, fontSize=7.5, leading=10,
                  wordWrap="LTR", spaceAfter=0)
    PS_cell_b = ParagraphStyle("CellBold",
                  fontName=FONT_BOLD, fontSize=7.5, leading=10,
                  wordWrap="LTR", spaceAfter=0)
    S_h1 = S_brand

    story = []

    # ── Logo + brand name side by side in header ─────────────────
    import os as _os
    _logo_paths = [
        _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "logo_pdf.png"),
        "/mnt/user-data/outputs/logo_pdf.png",
        "logo_pdf.png",
        "logo.png",
    ]
    _logo_found = next((p for p in _logo_paths if _os.path.exists(p)), None)

    if _logo_found:
        # Side-by-side: logo left, brand text right — in a frameless table
        _logo_img = RLImage(_logo_found, width=0.72*inch, height=0.68*inch)
        _brand_cell = [
            Paragraph("Audit Desk™", S_brand),
            Paragraph("Triangle Recon  –  ITC Forensic Report", S_sub),
        ]
        _hdr_table = Table(
            [[_logo_img, _brand_cell]],
            colWidths=[0.9*inch, 6.4*inch]
        )
        _hdr_table.setStyle(TableStyle([
            ("VALIGN",  (0,0), (-1,-1), "MIDDLE"),
            ("LEFTPADDING",  (0,0), (0,0), 0),
            ("RIGHTPADDING", (0,0), (0,0), 8),
            ("TOPPADDING",   (0,0), (-1,-1), 0),
            ("BOTTOMPADDING",(0,0), (-1,-1), 0),
        ]))
        story.append(_hdr_table)
    else:
        # Fallback: no logo — just text
        story.append(Paragraph("Audit Desk™", S_brand))
        story.append(Paragraph("Triangle Recon  –  ITC Forensic Report", S_sub))

    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=2,
                             color=GOLD))
    story.append(Spacer(1, 12))

    story.append(Paragraph(f"<b>Client:</b> {client_name}", S_body))
    story.append(Paragraph(f"<b>Prepared by:</b> {ca_name}", S_body))
    story.append(Paragraph(f"<b>Period:</b> {summary.get('period','')}", S_body))
    story.append(Paragraph(
        f"<b>Date:</b> {datetime.now().strftime('%d %B %Y, %I:%M %p')}", S_body))
    story.append(Spacer(1, 16))

    # ── Section A: ITC Opportunity ───────────────────────────────
    story.append(Paragraph("A   ITC OPPORTUNITY — RECOVERABLE WEALTH", S_bold))
    story.append(Spacer(1, 6))
    opportunity = summary.get("itc_opportunity", 0)
    overclaim   = summary.get("itc_overclaim", 0)
    data_a = [
        ["Metric", "Amount"],
        ["Total ITC Available (GSTR-2B)", _pdf_rupee(summary["itc_available_2b"])],
        ["ITC Claimed (GSTR-3B)",         _pdf_rupee(summary["itc_claimed_3b"])],
        ["ITC OPPORTUNITY (Recoverable)", _pdf_rupee(opportunity)],
    ]
    t_a = Table(data_a, colWidths=[3.5*inch, 2.8*inch])
    t_a.setStyle(TableStyle([
        ("BACKGROUND", (0,0),(-1,0),  TBL_HDR),
        ("TEXTCOLOR",  (0,0),(-1,0),  TBL_HDR_TEXT),
        ("FONTNAME",   (0,0),(-1,0),  FONT_BOLD),
        ("BACKGROUND", (0,-1),(-1,-1),TBL_HDR),
        ("TEXTCOLOR",  (0,-1),(-1,-1),colors.HexColor("#005DAA")),
        ("FONTNAME",   (0,-1),(-1,-1),FONT_BOLD),
        ("FONTNAME",   (0,1),(-1,-2), FONT),
        ("FONTSIZE",   (0,0),(-1,-1), 10),
        ("ROWBACKGROUNDS",(0,1),(-1,-2),
         [colors.HexColor("#f6f8fa"), colors.white]),
        ("GRID",    (0,0),(-1,-1), 0.5, colors.HexColor("#d0d7de")),
        ("PADDING", (0,0),(-1,-1), 8),
    ]))
    story.append(t_a)
    story.append(Spacer(1, 14))

    # ── Section B: ITC Overclaim Risk ────────────────────────────
    if overclaim > 0:
        story.append(Paragraph("B   ITC OVERCLAIM RISK — COMPLIANCE EXPOSURE",
            ParagraphStyle("RiskHdr", fontName=FONT_BOLD,
                           textColor=colors.HexColor("#e85d50"), fontSize=10)))
        story.append(Spacer(1, 6))
        data_b = [
            ["Risk Metric", "Amount"],
            ["Excess ITC Claimed (3B > 2B)", _pdf_rupee(overclaim)],
        ]
        t_b = Table(data_b, colWidths=[3.5*inch, 2.8*inch])
        t_b.setStyle(TableStyle([
            ("BACKGROUND", (0,0),(-1,0),  TBL_HDR),
        ("TEXTCOLOR",  (0,0),(-1,0),  TBL_HDR_TEXT),
            ("TEXTCOLOR",  (0,0),(-1,0),  colors.white),
            ("FONTNAME",   (0,0),(-1,0),  FONT_BOLD),
            ("BACKGROUND", (0,1),(-1,1),  colors.HexColor("#fde8e8")),
            ("TEXTCOLOR",  (0,1),(-1,1),  colors.HexColor("#b91c1c")),
            ("FONTNAME",   (0,1),(-1,1),  FONT_BOLD),
            ("FONTSIZE",   (0,0),(-1,-1), 10),
            ("GRID",    (0,0),(-1,-1), 0.5, colors.HexColor("#d0d7de")),
            ("PADDING", (0,0),(-1,-1), 8),
        ]))
        story.append(t_b)
        story.append(Spacer(1, 4))
        # Warning box as a single-cell table — guaranteed to render correctly
        warn_text = Paragraph(
            "<b>WARNING:</b> 3B claims exceed 2B availability. "
            "Excess claimed ITC may attract interest and penalty under Sec 50 of CGST Act. "
            "Review and reverse excess claim before next filing.",
            ParagraphStyle("RiskNote", fontName=FONT,
                           textColor=colors.HexColor("#b91c1c"),
                           fontSize=8, leading=13)
        )
        warn_table = Table([[warn_text]], colWidths=[6.3*inch])
        warn_table.setStyle(TableStyle([
            ("BACKGROUND", (0,0),(-1,-1), colors.HexColor("#fde8e8")),
            ("BOX",        (0,0),(-1,-1), 1.0, colors.HexColor("#e85d50")),
            ("PADDING",    (0,0),(-1,-1), 8),
            ("VALIGN",     (0,0),(-1,-1), "MIDDLE"),
        ]))
        story.append(warn_table)
        story.append(Spacer(1, 14))

    # ── Section C/D/E: Invoice Gap Summary ───────────────────────
    story.append(Paragraph("C   INVOICE RECONCILIATION GAP", S_bold))
    story.append(Spacer(1, 6))
    data_c = [
        ["Category", "Count", "Amount"],
        ["Missing in GSTR-2B (supplier not filed)",
         str(summary.get("missing_in_2b_count", 0)),
         _pdf_rupee(summary.get("missing_in_2b_sum", 0))],
        ["Missing in GSTR-1 (sales reporting gap)",
         str(summary.get("missing_in_1_count", 0)),
         _pdf_rupee(summary.get("missing_in_1_sum", 0))],
        ["Value Mismatches (same invoice, diff amount)",
         str(summary.get("value_mm_count", 0)),
         _pdf_rupee(summary.get("value_mm_sum", 0))],
        ["TOTAL INVOICE GAP",
         str(summary.get("mismatch_count", 0)),
         _pdf_rupee(summary.get("invoice_gap", 0))],
    ]
    t_c = Table(data_c, colWidths=[3.2*inch, 0.8*inch, 2.3*inch])
    t_c.setStyle(TableStyle([
        ("BACKGROUND", (0,0),(-1,0),  TBL_HDR),
        ("TEXTCOLOR",  (0,0),(-1,0),  TBL_HDR_TEXT),
        ("FONTNAME",   (0,0),(-1,0),  FONT_BOLD),
        ("BACKGROUND", (0,-1),(-1,-1),TBL_HDR),
        ("TEXTCOLOR",  (0,-1),(-1,-1),colors.HexColor("#005DAA")),
        ("FONTNAME",   (0,-1),(-1,-1),FONT_BOLD),
        ("FONTNAME",   (0,1),(-1,-2), FONT),
        ("FONTSIZE",   (0,0),(-1,-1), 9),
        ("ROWBACKGROUNDS",(0,1),(-1,-2),
         [colors.HexColor("#f6f8fa"), colors.white]),
        ("GRID",    (0,0),(-1,-1), 0.5, colors.HexColor("#d0d7de")),
        ("PADDING", (0,0),(-1,-1), 7),
    ]))
    story.append(t_c)
    story.append(Spacer(1, 20))

    # ── AI Narrative ─────────────────────────────────────────────
    if ai_narrative:
        S_narr_title = ParagraphStyle(
            "NarrTitle", fontName=FONT_BOLD,
            textColor=colors.HexColor("#00CFFF"), fontSize=11)
        S_narr_body = ParagraphStyle(
            "NarrBody", fontName=FONT,
            textColor=colors.HexColor("#24292f"),
            fontSize=10, leading=17,
            borderPadding=(10, 12, 10, 12),
            backColor=colors.HexColor("#f0f7ff"),
            borderColor=colors.HexColor("#00CFFF"),
            borderWidth=0.5, borderRadius=4)
        story.append(Paragraph("AI AUDIT ANALYSIS", S_narr_title))
        story.append(Spacer(1, 6))
        for para in [p.strip() for p in ai_narrative.split("\n\n") if p.strip()]:
            story.append(Paragraph(para, S_narr_body))
            story.append(Spacer(1, 6))
        story.append(Spacer(1, 10))
        story.append(Paragraph(
            "<i>Analysis generated by Audit Desk AI  -  For professional review only</i>",
            ParagraphStyle("NarrFoot", parent=S_cert,
                           textColor=colors.HexColor("#00CFFF"))))
        story.append(Spacer(1, 14))

    # ── Mismatch detail table ─────────────────────────────────────
    if not mismatches_df.empty:
        story.append(Paragraph(
            f"INVOICE-LEVEL MISMATCH DETAIL (Top 50)", S_bold))
        story.append(Spacer(1, 6))

        top = mismatches_df.head(50).copy()

        # Clean risk — strip emojis
        if "Risk" in top.columns:
            top["Risk"] = top["Risk"].apply(_clean_risk)

        # Format rupee columns — integer display
        for col in list(top.columns):
            if any(x in col for x in ["ITC", "Tax", "Delta", "Mismatch", "(₹)"]):
                top[col] = pd.to_numeric(top[col], errors="coerce")                             .fillna(0).apply(lambda x: f"{x:,.0f}")

        # Rename ₹ → Rs. for PDF font safety
        top.columns = [c.replace("₹","Rs.").replace("(₹)","(Rs.)") for c in top.columns]

        # ── Fixed column widths — prevents GSTIN+Date concatenation ──
        # Map each column to a specific width in inches
        col_widths_map = {
            "Invoice No."     : 0.95,   # slightly wider for longer inv numbers
            "Supplier GSTIN"  : 1.50,   # 15-char GSTIN fits comfortably
            "Date"            : 0.85,   # separate column — no concat with GSTIN
            "ITC in 2B (Rs.)" : 0.85,
            "Tax in 1 (Rs.)"  : 0.85,
            "Delta (Rs.)"     : 0.85,
            "Type"            : 1.10,   # "Missing in GSTR-1" needs room
            "Risk"            : 0.70,   # "Critical" = 8 chars, fits
        }
        cols      = list(top.columns)
        page_w    = 7.6   # usable page width in inches
        col_w_list= [col_widths_map.get(c, page_w/len(cols)) for c in cols]
        # Scale to fit page exactly
        total_w   = sum(col_w_list)
        col_w_list= [w * page_w / total_w for w in col_w_list]

        tdata  = [cols] + [[str(v) for v in row]
                            for row in top.values.tolist()]
        risk_idx = cols.index("Risk") if "Risk" in cols else None
        type_idx = cols.index("Type") if "Type" in cols else None

        mt = Table(tdata, colWidths=[w*inch for w in col_w_list], repeatRows=1)
        ts = TableStyle([
            ("BACKGROUND", (0,0),(-1,0),  TBL_HDR),
        ("TEXTCOLOR",  (0,0),(-1,0),  TBL_HDR_TEXT),
            ("TEXTCOLOR",  (0,0),(-1,0),  colors.white),
            ("FONTNAME",   (0,0),(-1,0),  FONT_BOLD),
            ("FONTNAME",   (0,1),(-1,-1), FONT),
            ("FONTSIZE",   (0,0),(-1,-1), 7),
            ("ROWBACKGROUNDS", (0,1),(-1,-1),
             [colors.HexColor("#f6f8fa"), colors.white]),
            ("GRID",    (0,0),(-1,-1), 0.3, colors.HexColor("#d0d7de")),
            ("PADDING", (0,0),(-1,-1), 4),
            ("VALIGN",  (0,0),(-1,-1), "MIDDLE"),
            ("WORDWRAP",(0,0),(-1,-1), True),
        ])
        # Colour risk cells
        if risk_idx is not None:
            for i, row in enumerate(tdata[1:], 1):
                rc = _risk_color(row[risk_idx])
                ts.add("TEXTCOLOR", (risk_idx,i), (risk_idx,i), rc)
                ts.add("FONTNAME",  (risk_idx,i), (risk_idx,i), FONT_BOLD)
        # Colour type cells
        if type_idx is not None:
            type_colors = {
                "Missing in 2B"    : colors.HexColor("#00CFFF"),
                "Missing in GSTR-1": colors.HexColor("#00CFFF"),
                "Value Mismatch"   : colors.HexColor("#e85d50"),
            }
            for i, row in enumerate(tdata[1:], 1):
                tc = type_colors.get(row[type_idx])
                if tc:
                    ts.add("TEXTCOLOR", (type_idx,i), (type_idx,i), tc)
        mt.setStyle(ts)
        story.append(mt)
        story.append(Spacer(1, 20))

    # ── Section D: Supplier Risk Ranking ────────────────────────
    # Derived from missing_in_2b grouped by supplier GSTIN
    # Shows CA exactly which suppliers to chase — ranked by ITC at risk
    if supplier_intel_df is not None and not supplier_intel_df.empty:
        story.append(Paragraph("D   SUPPLIER RISK RANKING", S_bold))
        story.append(Spacer(1, 4))

        top5_pct    = summary.get("top5_concentration_pct", 0)
        rep_count   = summary.get("repeat_defaulter_count", 0)
        sup_count   = summary.get("supplier_count", 0)
        top1_amt    = summary.get("top1_amount", 0)
        top1_gstin  = summary.get("top1_gstin", "")

        # Concentration note above the table
        conc_note = (
            f"<b>{sup_count} suppliers</b> have invoices missing from GSTR-2B.  "
            f"Top 5 account for <b>{top5_pct}%</b> of total gap.  "
            f"<b>{rep_count}</b> supplier(s) flagged as Repeat Defaulters "
            f"(filed &lt;50% of their own invoices)."
        )
        story.append(Paragraph(conc_note,
            ParagraphStyle("ConNote", fontName=FONT,
                           textColor=colors.HexColor("#24292f"),
                           fontSize=9, leading=14)))
        story.append(Spacer(1, 8))

        # Top 10 suppliers table
        top10 = supplier_intel_df.head(10).copy()
        # Clean risk emojis for PDF
        top10["Risk"] = top10["Risk"].apply(_clean_risk)
        top10["Repeat Defaulter"] = top10["Repeat Defaulter"].apply(
            lambda x: "Yes" if "Yes" in str(x) else "—")
        # Format ITC column
        top10["ITC at Risk (Rs.)"] = pd.to_numeric(
            top10["ITC at Risk (₹)"], errors="coerce"
        ).fillna(0).apply(lambda x: f"{x:,.0f}")
        top10 = top10.drop(columns=["ITC at Risk (₹)"], errors="ignore")

        pdf_cols = ["Rank","Supplier GSTIN","Invoices Missed",
                    "ITC at Risk (Rs.)","Filing Rate","Risk Score","Risk","Repeat Defaulter"]
        pdf_cols = [c for c in pdf_cols if c in top10.columns]

        col_w_sup = {
            "Rank"             : 0.35,
            "Supplier GSTIN"   : 1.45,
            "Invoices Missed"  : 0.70,
            "ITC at Risk (Rs.)": 0.90,
            "Filing Rate"      : 0.65,
            "Risk Score"       : 0.65,
            "Risk"             : 0.75,
            "Repeat Defaulter" : 0.80,
        }
        cw_list = [col_w_sup.get(c, 0.80) for c in pdf_cols]
        total_w_sup = sum(cw_list); page_w_sup = 7.6
        cw_list = [w * page_w_sup / total_w_sup for w in cw_list]

        tdata_sup = [pdf_cols] + [
            [str(row[c]) for c in pdf_cols]
            for _, row in top10.iterrows()
        ]

        S_cell_s = ParagraphStyle("CellS", fontName=FONT, fontSize=7, leading=10)
        S_hdr_s  = ParagraphStyle("HdrS",  fontName=FONT_BOLD, fontSize=7,
                                   leading=10, textColor=colors.white)

        # Wrap all cells in Paragraph for word-wrap
        tdata_para = [[Paragraph(str(v), S_hdr_s if r==0 else S_cell_s)
                       for v in row]
                      for r, row in enumerate(tdata_sup)]

        t_sup = Table(tdata_para, colWidths=[w*inch for w in cw_list], repeatRows=1)
        ts_sup = TableStyle([
            ("BACKGROUND", (0,0),(-1,0),  TBL_HDR),
        ("TEXTCOLOR",  (0,0),(-1,0),  TBL_HDR_TEXT),
            ("ROWBACKGROUNDS",(0,1),(-1,-1),
             [colors.HexColor("#f6f8fa"), colors.white]),
            ("GRID",    (0,0),(-1,-1), 0.3, colors.HexColor("#d0d7de")),
            ("PADDING", (0,0),(-1,-1), 5),
            ("VALIGN",  (0,0),(-1,-1), "MIDDLE"),
        ])
        # Color-code Risk column (last before Repeat Defaulter)
        risk_col_idx = pdf_cols.index("Risk") if "Risk" in pdf_cols else None
        rep_col_idx  = pdf_cols.index("Repeat Defaulter") if "Repeat Defaulter" in pdf_cols else None
        if risk_col_idx is not None:
            for i, row in enumerate(tdata_sup[1:], 1):
                rc = _risk_color(row[risk_col_idx])
                ts_sup.add("TEXTCOLOR", (risk_col_idx,i),(risk_col_idx,i), rc)
                ts_sup.add("FONTNAME",  (risk_col_idx,i),(risk_col_idx,i), FONT_BOLD)
        if rep_col_idx is not None:
            for i, row in enumerate(tdata_sup[1:], 1):
                if "Yes" in str(row[rep_col_idx]):
                    ts_sup.add("TEXTCOLOR", (rep_col_idx,i),(rep_col_idx,i),
                               colors.HexColor("#e85d50"))
                    ts_sup.add("FONTNAME",  (rep_col_idx,i),(rep_col_idx,i), FONT_BOLD)
        t_sup.setStyle(ts_sup)
        story.append(t_sup)
        story.append(Spacer(1, 6))

        # Footnote
        story.append(Paragraph(
            "Filing Rate = % of this supplier's invoices that appeared in your GSTR-2B.  "
            "Repeat Defaulter = filed <50% of their own invoices.  "
            "Risk Score = weighted: ITC amount (60%) + filing failure rate (40%).",
            ParagraphStyle("SupNote", fontName=FONT,
                           textColor=colors.HexColor("#FFFFFF"),
                           fontSize=7, leading=11)))
        story.append(Spacer(1, 20))

    # ── Action Priority in PDF ────────────────────────────────────
    if summary:
        overclaim   = summary.get("itc_overclaim", 0)
        opportunity = summary.get("itc_opportunity", 0)
        integrity   = summary.get("recon_integrity", 0)
        net_exp     = summary.get("net_exposure", 0)
        mm_pct      = summary.get("mismatch_pct", 0)
        overclaim_p = summary.get("overclaim_pct", 0)

        story.append(Paragraph("RECON INTELLIGENCE SUMMARY", S_bold))
        story.append(Spacer(1, 6))
        sup_count   = summary.get("supplier_count", 0)
        top5_pct    = summary.get("top5_concentration_pct", 0)
        rep_count   = summary.get("repeat_defaulter_count", 0)
        top1_amt    = summary.get("top1_amount", 0)

        intel_data = [
            ["Metric", "Value", "Interpretation"],
            ["Recon Integrity Score",
             f"{integrity}%",
             "Strong (>75%)  Moderate (50-75%)  Weak (<50%)"],
            ["Invoice Mismatch Rate",
             f"{mm_pct}%",
             f"{summary.get('mismatch_count',0):,} of {summary.get('invoices_total', summary.get('invoices_2b',0)):,} combined unique invoices across GSTR-1 & GSTR-2B"],
            ["Net GST Exposure",
             _pdf_rupee(net_exp),
             "Overclaim Risk + Value Mismatch Risk combined"],
            ["Overclaim as % of 2B",
             f"{overclaim_p}%",
             "No excess ITC claim detected. ITC claimed is within available GSTR-2B limits." if overclaim_p == 0.0 else f"Excess ITC of {overclaim_p}% claimed relative to GSTR-2B — reversal required."],
            ["Supplier Risk Concentration",
             f"{top5_pct}%",
             f"Top 5 suppliers account for {top5_pct}% of total supplier gap"],
            ["Repeat Defaulters",
             str(rep_count),
             f"{rep_count} supplier(s) filed <50% of their own invoices — assess eligibility under Section 16(2) and evaluate the need for ITC reversal."],
            ["Highest Single Supplier Risk",
             _pdf_rupee(top1_amt),
             f"GSTIN: {summary.get('top1_gstin','')} — largest single supplier exposure"],
        ]
        t_intel = Table(intel_data, colWidths=[1.8*inch, 1.2*inch, 4.3*inch])
        t_intel.setStyle(TableStyle([
            ("BACKGROUND", (0,0),(-1,0),  TBL_HDR),
        ("TEXTCOLOR",  (0,0),(-1,0),  TBL_HDR_TEXT),
            ("TEXTCOLOR",  (0,0),(-1,0),  colors.white),
            ("FONTNAME",   (0,0),(-1,0),  FONT_BOLD),
            ("FONTNAME",   (0,1),(-1,-1), FONT),
            ("FONTSIZE",   (0,0),(-1,-1), 8),
            ("ROWBACKGROUNDS",(0,1),(-1,-1),
             [colors.HexColor("#f6f8fa"), colors.white]),
            ("GRID",    (0,0),(-1,-1), 0.3, colors.HexColor("#d0d7de")),
            ("PADDING", (0,0),(-1,-1), 6),
            ("VALIGN",  (0,0),(-1,-1), "MIDDLE"),
        ]))
        story.append(t_intel)
        story.append(Spacer(1, 14))

        # Action priority table
        story.append(Paragraph("ACTION PRIORITY", S_bold))
        story.append(Spacer(1, 6))
        actions = []
        if overclaim > 0:
            actions.append(["Critical", "Reverse Excess ITC",
                f"Reverse Rs.{overclaim:,.0f} ({overclaim_p}% of 2B) before next filing. "
                "Attracts interest u/s 50 CGST Act if not reversed."])
        if summary.get("missing_in_2b_count", 0) > 0:
            # Name the top 3 suppliers specifically — more actionable than a count
            top3_gstin = ""
            if supplier_intel_df is not None and not supplier_intel_df.empty:
                top3 = [str(g) for g in supplier_intel_df.head(3)["Supplier GSTIN"].tolist()
                           if pd.notna(g) and str(g) not in ("","nan","NaN","UNKNOWN")]
                top3_gstin = ("  Priority GSTINs: " + " | ".join(top3) + ".") if top3 else ""
            actions.append([
                "High",
                "Follow Up Suppliers",
                f"Follow up on {summary['missing_in_2b_count']:,} invoices "
                f"reported in suppliers' GSTR-1 but missing from GSTR-2B. "
                f"Rs.{summary['missing_in_2b_sum']:,.0f} of potential Input Tax Credit is pending reflection in GSTR-2B."
                f"{top3_gstin}"
        ])
        if summary.get("missing_in_1_count", 0) > 0:
            actions.append(["Medium", "Reconcile GSTR-1 Gaps",
                f"Verify {summary['missing_in_1_count']} invoices present in 2B "
                f"but missing from GSTR-1. "
                f"Rs.{summary['missing_in_1_sum']:,.0f} needs reconciliation."])
        if summary.get("value_mm_count", 0) > 0:
            actions.append(["Medium", "Resolve Value Mismatches",
                f"{summary['value_mm_count']} invoices show same number "
                "but different tax amounts in GSTR-1 vs 2B."])
        if opportunity > 0:
            actions.append(["Opportunity", "Review Unclaimed ITC",
            (
            f"₹{opportunity:,.0f} of ITC is reflected in GSTR-2B but "
            f"does not appear to be claimed in GSTR-3B for the selected period. "
            f"Eligibility should be verified before claiming in a subsequent return."
            )
        ])
   
        # Add Sec 50 interest estimate to critical action if overclaim exists
        if overclaim > 0:
            sec50_30 = summary.get("sec50_30d", 0)
            sec50_90 = summary.get("sec50_90d", 0)
            for i, act in enumerate(actions):
                if act[0] == "Critical":
                    actions[i][2] += (
                        f" Estimated Sec 50 interest: "
                        f"Rs.{sec50_30:,.0f} (30 days) / "
                        f"Rs.{sec50_90:,.0f} (90 days) at 18% p.a."
                    )
                    break

        if actions:
            # Use Paragraph objects so text wraps properly inside cells
            S_cell = ParagraphStyle("Cell", fontName=FONT,
                                    fontSize=8, leading=12)
            S_hdr  = ParagraphStyle("Hdr",  fontName=FONT_BOLD,
                                    fontSize=8, leading=12,
                                    textColor=colors.white)
            priority_colors = {
                "Critical"   : colors.HexColor("#e85d50"),
                "High"       : colors.HexColor("#00CFFF"),
                "Medium"     : colors.HexColor("#00CFFF"),
                "Opportunity": colors.HexColor("#3fb950"),
            }
            # Header row
            act_data = [[
                Paragraph("Priority", S_hdr),
                Paragraph("Action",   S_hdr),
                Paragraph("Detail",   S_hdr),
            ]]
            ts_act = TableStyle([
                ("BACKGROUND", (0,0),(-1,0),  TBL_HDR),
        ("TEXTCOLOR",  (0,0),(-1,0),  TBL_HDR_TEXT),
                ("ROWBACKGROUNDS",(0,1),(-1,-1),
                 [colors.HexColor("#f6f8fa"), colors.white]),
                ("GRID",    (0,0),(-1,-1), 0.3, colors.HexColor("#d0d7de")),
                ("PADDING", (0,0),(-1,-1), 6),
                ("VALIGN",  (0,0),(-1,-1), "TOP"),
            ])
            for i, act in enumerate(actions, 1):
                pc = priority_colors.get(act[0], colors.black)
                S_pri = ParagraphStyle(f"Pri{i}", fontName=FONT_BOLD,
                                       fontSize=8, leading=12,
                                       textColor=pc)
                act_data.append([
                    Paragraph(act[0], S_pri),
                    Paragraph(act[1], S_cell),
                    Paragraph(act[2], S_cell),
                ])
            t_act = Table(act_data, colWidths=[1.05*inch, 1.3*inch, 4.95*inch])
            t_act.setStyle(ts_act)
            story.append(t_act)
            story.append(Spacer(1, 20))

    # ── Certification stamp ───────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=1,
                             color=colors.HexColor("#d0d7de")))
    story.append(Spacer(1, 8))
    # Clickable links in PDF footer — ReportLab uses <link> tags
    # ReportLab clickable links: use <link href='...'> — color via <font>
    cert_text = (
        f"Forensic Analysis by <b>Audit Desk</b>  |  "
        "<link href='https://www.itcrecon.in'><font color='#1a56db'><u>www.itcrecon.in</u></font></link>  |  "
        "<link href='mailto:auditdesk.hq@gmail.com'><font color='#1a56db'><u>auditdesk.hq@gmail.com</u></font></link>  |  "
        f"Report ID: {link_token}  |  "
        f"Generated: {datetime.now().strftime('%d-%m-%Y %H:%M')}  |  "
        "This report is for professional use only. "
        "Verify findings with a qualified CA before taking action."
    )
    story.append(Paragraph(cert_text, S_cert))

    doc.build(story)
    buf.seek(0)
    return buf

# ============================================================
# SECTION 7: LOGIN & REGISTRATION
# ============================================================

def page_login():
    # Password reset via URL
    if _handle_password_reset_from_url():
        return

    params = st.query_params

    # Public report
    if "report" in params:
        S.public_token = params["report"]
        S.page = "public_report"
        st.rerun()

    # Auto-login via ?email= param passed from itcrecon.in
    url_email = params.get("email", "")
    url_role  = params.get("role", "")

    if url_email:
        email = url_email.strip().lower()
        # Sovereign check — email matches SOVEREIGN_EMAIL secret OR has sovereign subscription
        sov_email = _get_secret("SOVEREIGN_EMAIL", "auditdesk.hq@gmail.com").lower()
        if email == sov_email:
            S.logged_in = True; S.email = email; S.role = "sovereign"
            S.is_subscriber = True; S.is_trial = False
            S.subscription = {"plan":"sovereign","early_bird":True,"amount":0,"status":"active"}
            S.page = "sovereign"
            st.query_params.clear(); st.rerun(); return
        # Staff
        if url_role == "staff":
            S.logged_in = True; S.email = email; S.role = "staff"
            S.is_subscriber = True; S.is_trial = False
            S.subscription = {"plan":"staff","early_bird":False,"amount":0,"status":"active"}
            S.page = "dashboard"
            st.query_params.clear(); st.rerun(); return
        # Regular user — email already verified by landing page, just look up the user
        try:
            # Check subscriber first
            sub_res = db("subscriptions").select("*").eq("email", email)\
                .eq("status","active").execute()
            if sub_res.data and len(sub_res.data) > 0:
                _set_session_subscriber(email, sub_res.data[0])
                st.query_params.clear(); st.rerun(); return

            # Check free user
            fu_res = db("free_users").select("*").eq("email", email).execute()
            if fu_res.data and len(fu_res.data) > 0:
                _set_session_free(fu_res.data[0])
                st.query_params.clear(); st.rerun(); return
            else:
                st.error(f"No account found for {email}. Please register at itcrecon.in first.")
        except Exception as _login_err:
            st.error(f"Login error: {_login_err}")

    # Not logged in — show redirect card
    st.markdown("""<style>
    section[data-testid="stSidebar"] { display: none; }
    </style>""", unsafe_allow_html=True)
    st.markdown("<div style='height:80px'></div>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.4, 1])
    with col:
        try:
            st.image("logo.png", width=100)
        except:
            pass
        st.markdown("""
        <div style='background:#071233; border:1px solid #1A3A6E;
                    border-top:2px solid #00CFFF; border-radius:14px;
                    padding:36px 32px; text-align:center;'>
            <p style='color:#00CFFF; font-family:IBM Plex Mono; font-size:0.75rem;
                      letter-spacing:3px; margin:0 0 12px 0;'>AUDIT DESK · ITC RECON</p>
            <p style='color:#FFFFFF; font-size:1.4rem; font-weight:700;
                      margin:0 0 12px 0;'>Sign in at itcrecon.in</p>
            <p style='color:#FFFFFF; font-size:0.9rem; margin:0 0 28px 0;'>
            Please log in from our website to access the app.</p>
            <a href='https://itcrecon.in' style='background:linear-gradient(135deg,#0095BF,#00CFFF);
               color:#0A1B44; padding:14px 32px; border-radius:8px; text-decoration:none;
               font-weight:700; font-size:1rem; display:inline-block;'>
            Go to itcrecon.in →</a>
            <p style='color:#FFFFFF; font-size:0.75rem; margin:20px 0 0 0;'>
            New user? Create a free account at itcrecon.in</p>
        </div>
        """, unsafe_allow_html=True)


def _do_login(email, password):
    # ── Special accounts (sovereign / staff) — checked first, no DB needed ──
    role = check_special_login(email, password)
    if role == "sovereign":
        S.logged_in     = True
        S.email         = email
        S.role          = "sovereign"
        S.is_subscriber = True
        S.is_trial      = False
        S.subscription  = {"plan": "sovereign", "early_bird": True,
                           "amount": 0, "status": "active"}
        S.page          = "sovereign"   # land directly on sovereign dashboard
        st.rerun()
        return
    if role == "staff":
        S.logged_in     = True
        S.email         = email
        S.role          = "staff"
        S.is_subscriber = True
        S.is_trial      = False
        S.subscription  = {"plan": "staff", "early_bird": False,
                           "amount": 0, "status": "active"}
        S.page          = "dashboard"
        st.rerun()
        return

    # ── Regular database login ──
    if not DB_LIVE:
        st.error("Database not connected.")
        return
    try:
        sub = db("subscriptions").select("*")\
            .eq("email", email)\
            .eq("status", "active")\
            .maybe_single().execute()
        if sub.data:
            fu = db("free_users").select("*")\
                .eq("email", email).maybe_single().execute()
            if fu.data and fu.data["password"] == password:
                _set_session_subscriber(email, sub.data)
                st.rerun()
                return
    except:
        pass
    fu, err = get_or_create_free_user(email, password)
    if fu and not err:
        _set_session_free(fu)
        st.rerun()
    else:
        st.error("Invalid email or password.")

def _send_password_reset(email):
    """
    Self-service password reset.
    Generates a reset token, stores it in the database with a 1-hour expiry,
    and sends the user an email with the reset link via Supabase's built-in
    email service (no SMTP setup needed — uses Supabase Auth email).

    The reset link looks like:
    https://yourapp.streamlit.app?reset=<token>

    When user clicks it, page_login() detects the ?reset= param and shows
    the new password form automatically.
    """
    if not email:
        st.error("Please enter your email address.")
        return

    if not DB_LIVE:
        st.info("Email reset not available in offline mode.")
        return

    try:
        # Check if email exists in our system
        user_check = db("free_users").select("email")\
            .eq("email", email).maybe_single().execute()

        if not user_check.data:
            # Don't reveal whether email exists — security best practice
            st.success("If that email is registered, a reset link has been sent.")
            return

        # Generate a secure token
        reset_token = str(uuid.uuid4()).replace("-","")
        expiry      = (datetime.now() + timedelta(hours=1)).isoformat()

        # Store reset token (create table if not exists — handled in SQL setup)
        try:
            db("password_resets").insert({
                "email"      : email,
                "token"      : reset_token,
                "expires_at" : expiry,
                "used"       : False
            }).execute()
        except:
            # Table may not exist yet — graceful fallback
            st.info("Password reset is being set up. "
                    "Please contact auditdesk.hq@gmail.com for now.")
            return

        reset_url = f"{SITE_URL}?reset={reset_token}"

        # Use Supabase to send the email
        # This requires Supabase email to be configured in your project settings
        try:
            supabase.auth.reset_password_email(
                email,
                options={"redirect_to": reset_url}
            )
            st.success("✅ Reset link sent! Check your email. "
                       "Link expires in 1 hour.")
            st.caption("Didn't receive it? Check your spam folder.")
        except:
            # Supabase Auth email not configured — show link directly
            # (for development/testing only)
            st.success("Reset token generated.")
            st.info(f"Reset URL (dev mode): `{reset_url}`")
            st.caption("In production, configure Supabase Auth email "
                       "to send this automatically.")

    except Exception as e:
        st.error(f"Reset failed: {e}")


def _handle_password_reset_from_url():
    """
    Called at top of page_login() when ?reset=<token> is in the URL.
    Shows the new password form and processes the reset.
    """
    params = st.query_params
    if "reset" not in params:
        return False

    token = params["reset"]
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    _, form_col, _ = st.columns([1, 1.2, 1])
    with form_col:
        st.markdown("""
        <div style='background:#071233; border:1px solid #1A3A6E;
                    border-radius:14px; padding:32px;'>
        <p style='color:#FFFFFF; font-size:1.3rem; font-weight:700;
                  margin:0 0 8px 0;'>Set New Password</p>
        <p style='color:#FFFFFF; font-size:0.88rem; margin:0 0 20px 0;'>
        Enter your new password below.
        </p>
        """, unsafe_allow_html=True)

        with st.form("new_password_form"):
            new_pass  = st.text_input("New Password", type="password",
                                       placeholder="Minimum 6 characters")
            new_pass2 = st.text_input("Confirm New Password", type="password",
                                       placeholder="Repeat password")
            set_btn   = st.form_submit_button("Set New Password →",
                            use_container_width=True, type="primary")

        if set_btn:
            if len(new_pass) < 6:
                st.error("Password must be at least 6 characters.")
            elif new_pass != new_pass2:
                st.error("Passwords don't match.")
            else:
                try:
                    # Validate token
                    reset_row = db("password_resets").select("*")\
                        .eq("token", token)\
                        .eq("used", False)\
                        .maybe_single().execute()

                    if not reset_row.data:
                        st.error("This reset link is invalid or has already been used.")
                    else:
                        expiry = datetime.fromisoformat(
                            reset_row.data["expires_at"])
                        if datetime.now() > expiry:
                            st.error("This reset link has expired. "
                                     "Please request a new one.")
                        else:
                            # Update password
                            db("free_users").update({"password": new_pass})\
                                .eq("email", reset_row.data["email"])\
                                .execute()
                            # Mark token as used
                            db("password_resets").update({"used": True})\
                                .eq("token", token).execute()
                            st.success("✅ Password updated successfully! "
                                       "You can now sign in.")
                            st.query_params.clear()
                            time.sleep(2)
                            st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

        st.markdown("</div>", unsafe_allow_html=True)

    return True  # Signal to page_login() to stop rendering the normal form


def _set_session_subscriber(email, sub_row):
    S.logged_in     = True
    S.email         = email
    S.is_subscriber = True
    S.is_trial      = False
    S.subscription  = sub_row
    S.page          = "dashboard"

def _set_session_free(fu_row):
    S.logged_in      = True
    S.email          = fu_row["email"]
    S.free_user_row  = fu_row
    S.is_subscriber  = False
    S.is_trial       = is_trial_active(fu_row)
    S.page           = "dashboard"

# ============================================================
# SECTION 8: SIDEBAR
# ============================================================

def sidebar():
    with st.sidebar:
        try:
            st.image("logo.png", width=130)
        except:
            st.markdown("### 📐 Audit Desk")
        st.caption("v3.0 · ITC Forensic Engine")
        st.divider()

        # Status badge
        role = S.get("role", "user")
        if role == "sovereign":
            st.markdown("""
            <div style='background:#071233; border:1px solid #00CFFF;
                        border-radius:8px; padding:10px 14px; margin-bottom:12px;'>
                <span style='color:#00CFFF; font-weight:700;'>👑 Sovereign</span><br>
                <span style='color:#FFFFFF; font-size:0.8rem;'>Full Access</span>
            </div>
            """, unsafe_allow_html=True)
        elif role == "staff":
            st.markdown("""
            <div style='background:#071233; border:1px solid #00CFFF;
                        border-radius:8px; padding:10px 14px; margin-bottom:12px;'>
                <span style='color:#00CFFF; font-weight:700;'>🔧 Staff</span><br>
                <span style='color:#FFFFFF; font-size:0.8rem;'>Developer Access</span>
            </div>
            """, unsafe_allow_html=True)
        elif S.is_subscriber:
            sub   = S.subscription or {}
            plan  = sub.get("plan","monthly")
            eb    = sub.get("early_bird", False)
            badge = "🔐 Early Bird" if eb else "✅ Subscribed"
            st.markdown(f"""
            <div style='background:#071233; border:1px solid #0080A8;
                        border-radius:8px; padding:10px 14px; margin-bottom:12px;'>
                <span style='color:#00CFFF; font-weight:700;'>{badge}</span><br>
                <span style='color:#00CFFF; font-size:0.8rem;'>
                ₹{MONTHLY_PRICE if plan=="monthly" else ANNUAL_PRICE} ·
                {"Monthly" if plan=="monthly" else "Annual"}</span>
            </div>
            """, unsafe_allow_html=True)
        elif S.is_trial:
            days = days_left_in_trial(S.free_user_row)
            st.markdown(f"""
            <div style='background:#071233; border:1px solid #00CFFF;
                        border-radius:8px; padding:10px 14px; margin-bottom:12px;'>
                <span style='color:#00CFFF; font-weight:700;'>⏳ Free Trial</span><br>
                <span style='color:#FFFFFF; font-size:0.8rem;'>
                {days} days remaining</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style='background:#0D2157; border:1px solid #1A3A6E;
                        border-radius:8px; padding:10px 14px; margin-bottom:12px;'>
                <span style='color:#FFFFFF; font-size:0.85rem;'>Free Account</span>
            </div>
            """, unsafe_allow_html=True)

        st.caption(S.email or "")
        st.divider()

        # Navigation
        pages = {
            "🏠 Dashboard"         : "dashboard",
            "📐 Triangle Recon"    : "recon",
            "👥 Client Roster"     : "clients",
            "📋 Recon History"     : "history",
            "🧮 Free Calculators"  : "calculators",
        }
        for label, key in pages.items():
            active = S.page == key
            if st.button(label, use_container_width=True,
                         type="primary" if active else "secondary",
                         key=f"nav_{key}"):
                nav(key)

        st.divider()

        # Subscription CTA for free users
        if not has_full_access():
            st.markdown("""
            <a href='https://itcrecon.in/#pricing' target='_blank'
               style='background:linear-gradient(135deg,#0095BF,#00CFFF);
                      color:#0A1B44; padding:10px 16px; border-radius:6px;
                      text-decoration:none; font-weight:700; font-size:0.9rem;
                      display:block; text-align:center; margin-bottom:8px;'>
            💳 Subscribe — ₹999/month
            </a>
            """, unsafe_allow_html=True)
        elif not S.is_subscriber:
            st.markdown("""
            <a href='https://itcrecon.in/#pricing' target='_blank'
               style='background:linear-gradient(135deg,#0095BF,#00CFFF);
                      color:#0A1B44; padding:10px 16px; border-radius:6px;
                      text-decoration:none; font-weight:700; font-size:0.9rem;
                      display:block; text-align:center; margin-bottom:8px;'>
            💳 Subscribe Now
            </a>
            """, unsafe_allow_html=True)

        # Sovereign mode — only visible to sovereign login
        if S.get("role") == "sovereign":
            st.divider()
            if st.button("👑 Sovereign View", use_container_width=True,
                         type="secondary"):
                nav("sovereign")

        st.divider()

        # Suggestion box
        with st.expander("💬 Feedback / Ideas / Issues"):
            st.markdown("""
            <p style='color:#FFFFFF; font-size:0.82rem; margin:0 0 8px 0;'>
            Tell us anything — bugs, ideas, feature requests.
            Attach a screenshot if helpful.</p>
            """, unsafe_allow_html=True)
            suggestion = st.text_area(
                "Your message",
                placeholder="e.g. The PDF table is cutting off on the right...",
                key="sidebar_suggestion", height=90,
                label_visibility="collapsed"
            )
            fb_image = st.file_uploader(
                "Attach screenshot (optional)",
                type=["png","jpg","jpeg","webp"],
                key="fb_image",
                help="Attach a screenshot of the issue if helpful"
            )
            if st.button("Send Feedback", key="send_suggestion", use_container_width=True):
                if suggestion.strip():
                    try:
                        import base64 as _b64
                        img_note = ""
                        if fb_image:
                            img_b64 = _b64.b64encode(fb_image.read()).decode()
                            img_note = f" [image:{fb_image.name}:{img_b64[:100]}...]"
                        db("suggestions").insert({
                            "email"  : S.email or "anonymous",
                            "message": suggestion.strip() + img_note,
                        }).execute()
                        st.success("✅ Received! We'll get back to you.")
                    except Exception as _e:
                        st.error(f"Couldn't save. Please email auditdesk.hq@gmail.com")
                else:
                    st.warning("Please type your feedback before sending.")

        st.divider()
        if st.button("Logout", use_container_width=True, type="secondary"):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.markdown("""
            <meta http-equiv="refresh" content="0;url=https://itcrecon.in">
            <script>window.location.replace('https://itcrecon.in');</script>
            """, unsafe_allow_html=True)
            st.stop()

# ============================================================
# SECTION 9: DASHBOARD
# ============================================================

def page_dashboard():
    _sponsor     = _get_secret("FOUNDING_SPONSOR_NAME", "")
    _sponsor_tag = _get_secret("FOUNDING_SPONSOR_TAG", "")
    _sponsor_url = _get_secret("FOUNDING_SPONSOR_URL", "#")
    if _sponsor:
        st.markdown(f"""
        <a href='{_sponsor_url}' target='_blank' style='text-decoration:none;'>
        <div style='background:linear-gradient(135deg,#071233,#0D2157);
                    border:1px solid #c9a84c; border-radius:10px;
                    padding:11px 20px; margin-bottom:18px;
                    display:flex; align-items:center; gap:24px;'>
            <span style='color:#c9a84c; font-size:0.65rem; font-family:IBM Plex Mono;
                          letter-spacing:2px; text-transform:uppercase; white-space:nowrap;'>
                ⭐ Founding Sponsor</span>
            <span style='color:#FFFFFF; font-size:0.9rem; font-weight:700;'>{_sponsor}</span>
            <span style='color:#FFFFFF; font-size:0.8rem; opacity:.8; flex:1;'>{_sponsor_tag}</span>
            <span style='color:#00CFFF; font-size:0.78rem;'>Learn more →</span>
        </div></a>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style='background:linear-gradient(135deg,#071233,#0D1833);
                    border:1px dashed rgba(201,168,76,0.45); border-radius:10px;
                    padding:11px 20px; margin-bottom:18px;
                    display:flex; align-items:center; gap:24px;'>
            <span style='color:rgba(201,168,76,0.6); font-size:0.65rem;
                          font-family:IBM Plex Mono; letter-spacing:2px;
                          text-transform:uppercase; white-space:nowrap;'>
                ⭐ Founding Sponsor</span>
            <span style='color:rgba(255,255,255,0.35); font-size:0.9rem;
                          font-weight:700; font-style:italic;'>Your Brand Here</span>
            <span style='color:rgba(255,255,255,0.2); font-size:0.8rem; flex:1;'>
                Reach every CA who uses Audit Desk™ — daily</span>
            <a href='mailto:auditdesk.hq@gmail.com?subject=Founding%20Sponsor%20Enquiry'
               style='color:rgba(0,207,255,0.5); font-size:0.75rem; text-decoration:none;
                      border:1px solid rgba(0,207,255,0.25); padding:4px 10px;
                      border-radius:4px; white-space:nowrap;'>1 spot available →</a>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<h1 style='color:#FFFFFF;'>Dashboard</h1>",
                unsafe_allow_html=True)
    st.markdown(f"<p style='color:#FFFFFF;'>Welcome, "
                f"<b style='color:#FFFFFF;'>{S.email}</b></p>",
                unsafe_allow_html=True)

    # Subscribe nudge for free users
    if not has_full_access():
        st.markdown("""
        <div style='background:#0D2157; border:1px solid #00CFFF;
                    border-radius:10px; padding:16px 20px; margin-bottom:16px;'>
        <b style='color:#00CFFF;'>🔥 Early Bird — ₹999/month or ₹8,999/year</b><br>
        <span style='color:#FFFFFF;'>Subscribe to unlock full Triangle Recon reports,
        PDF downloads, Supplier Intelligence, and Client Portal.</span>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <a href='https://itcrecon.in/#pricing' target='_blank'
           style='background:linear-gradient(135deg,#0095BF,#00CFFF);
                  color:#0A1B44; padding:12px 28px; border-radius:8px;
                  text-decoration:none; font-weight:700; font-size:1rem;
                  display:inline-block; margin-bottom:20px;'>
        💳 Subscribe Now — itcrecon.in
        </a>
        """, unsafe_allow_html=True)

    if S.is_trial and not S.is_subscriber:
        days = days_left_in_trial(S.free_user_row)
        st.markdown(f"""
        <div class='card card-amber'>
        <b style='color:#00CFFF;'>⏳ {days} trial days remaining</b> —
        <a href='#' style='color:#00CFFF;'>Subscribe now to keep access</a>
        </div>
        """, unsafe_allow_html=True)

    # Stats
    history = get_recon_history(S.email)
    total_wealth = sum(r.get("wealth_found",0) for r in history)
    total_scans  = len(history)
    clients      = get_client_roster(S.email)

    c1, c2, c3, c4 = st.columns(4)
    for col, num, label in [
        (c1, total_scans,   "Recon Scans Run"),
        (c2, len(clients),  "Clients Registered"),
        (c3, f"₹{total_wealth/100000:.1f}L", "Total ITC Found"),
        (c4, f"₹{total_wealth * 0.10 / 100000:.1f}L", "Est. CA Fee Potential"),
    ]:
        col.markdown(f"""
        <div class='stat-box'>
            <p class='stat-number'>{num}</p>
            <p class='stat-label'>{label}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Quick start
    st.markdown("<div class='section-hdr'>How To Use Every Month</div>",
                unsafe_allow_html=True)
    for i, (t, s) in enumerate([
        ("7th of every month: download GSTR-1, 2B, 3B from GST portal",
         "For each client — takes 2 minutes per client"),
        ("Open Triangle Recon → select client → upload 3 files",
         "Scan runs in under 30 seconds"),
        ("See total unclaimed ITC found",
         "Report shows invoice-level mismatch detail"),
        ("Send shareable link to client",
         "Client sees their recovery — you look like a hero"),
        ("Download certified PDF for your records",
         "'Audit Desk Certified' stamp builds your credibility"),
    ], 1):
        st.markdown(f"""
        <div class='card' style='padding:14px 18px;'>
            <span class='badge'>{i}</span>
            <b style='color:#FFFFFF;'>{t}</b>
            <span style='color:#FFFFFF; font-size:0.85rem;'> — {s}</span>
        </div>
        """, unsafe_allow_html=True)

    # ROI Calculator
    st.markdown("<div class='section-hdr'>ROI Calculator</div>",
                unsafe_allow_html=True)
    col_a, col_b = st.columns(2)
    with col_a:
        est = st.number_input("Estimated ITC per client per month (₹)",
                              value=100000, step=10000)
        clients_n = st.slider("Number of clients you'll scan monthly", 1, 100, 20)
    with col_b:
        your_pct = st.slider("Your recovery fee to client (%)", 5, 20, 10)

    your_fee   = est * clients_n * (your_pct/100)
    desk_cost  = MONTHLY_PRICE
    net        = your_fee - desk_cost

    r1, r2, r3 = st.columns(3)
    r1.metric("Your monthly fees",   f"₹{your_fee:,.0f}")
    r2.metric("Audit Desk cost",     f"₹{desk_cost:,}/month")
    r3.metric("Net monthly profit",  f"₹{net:,.0f}",
              delta=f"{int(net/desk_cost)}× ROI")

    if st.button("▶  Run Triangle Recon Now", type="primary"):
        nav("recon")

# ============================================================
# SECTION 10: TRIANGLE RECON PAGE
# ============================================================

def page_recon():
    st.markdown("<h1 style='color:#FFFFFF;'>📐 Triangle Recon</h1>",
                unsafe_allow_html=True)
    st.markdown(
        "<p style='color:#FFFFFF;'>GSTR-1 × GSTR-2B × GSTR-3B — "
        "Find every rupee of unclaimed ITC</p>",
        unsafe_allow_html=True)

    if not has_full_access():
        st.warning("⚡ Triangle Recon runs for all users. Subscribe to unlock the full invoice-level report, Excel download, and PDF.")
        st.markdown("""
        <a href='https://itcrecon.in/#pricing' target='_blank'
           style='background:linear-gradient(135deg,#0095BF,#00CFFF);color:#0A1B44;
                  padding:12px 28px;border-radius:8px;text-decoration:none;
                  font-weight:700;font-size:1rem;display:inline-block;margin:8px 0;'>
        💳 Subscribe Now — itcrecon.in
        </a>
        """, unsafe_allow_html=True)

    # Client selector
    clients = get_client_roster(S.email)
    st.markdown("<div class='section-hdr'>"
                "<span class='badge'>1</span> Select Client</div>",
                unsafe_allow_html=True)

    col_sel, col_add = st.columns([3, 1])
    with col_sel:
        if clients:
            client_names = [c["client_name"] for c in clients]
            chosen = st.selectbox("Client", client_names)
        else:
            chosen = st.text_input("Client Name",
                                   placeholder="No clients yet — type name here")
    with col_add:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("+ Add Client", type="secondary"):
            nav("clients")

    period = st.selectbox("Audit Period", [
        "Apr–Jun 2025 (Q1 FY26)", "Jul–Sep 2025 (Q2 FY26)",
        "Oct–Dec 2025 (Q3 FY26)", "Jan–Mar 2026 (Q4 FY26)",
        "Full FY 2025–26", "Full FY 2024–25"
    ])

    # File uploads
    st.markdown("<div class='section-hdr'>"
                "<span class='badge'>2</span> Upload Files</div>",
                unsafe_allow_html=True)
    st.info("📥 GST Portal → Returns → Download Excel for GSTR-1, 2B, 3B")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("**GSTR-1** · Sales Register")
        f1 = st.file_uploader("GSTR-1", type=["xlsx","csv"], key="f1",
                               label_visibility="collapsed")
        if f1: st.success(f"✓ {f1.name}")
    with c2:
        st.markdown("**GSTR-2B** · ITC Register")
        f2 = st.file_uploader("GSTR-2B", type=["xlsx","csv"], key="f2",
                               label_visibility="collapsed")
        if f2: st.success(f"✓ {f2.name}")
    with c3:
        st.markdown("**GSTR-3B** · Summary Return")
        f3 = st.file_uploader("GSTR-3B", type=["xlsx","csv"], key="f3",
                               label_visibility="collapsed")
        if f3: st.success(f"✓ {f3.name}")

    with st.expander("⚙️ Advanced"):
        threshold = st.number_input(
            "Minimum mismatch to flag (₹)",
            value=DELTA_THRESHOLD, step=100.0)

    # Client name is optional — never block the recon on it
    if not chosen:
        chosen = "Test Client"

    st.markdown("<br>", unsafe_allow_html=True)
    can_run = bool(f1 and f2 and f3)  # only files required, not client name

    if st.button("🚀 Run Triangle Recon", type="primary",
                 disabled=not can_run, use_container_width=True):

        with st.status("🔍 Interrogating GST data...", expanded=True) as status:
            st.write("Reading uploaded files...")
            time.sleep(0.4)
            try:
                def read(f):
                    return pd.read_csv(f) if f.name.endswith(".csv") \
                           else pd.read_excel(f)
                g1 = read(f1); g2 = read(f2); g3 = read(f3)
                st.write(f"✓ GSTR-1: {len(g1)} rows | "
                         f"2B: {len(g2)} rows | 3B: {len(g3)} rows")
                st.write("Cross-referencing invoices...")
                time.sleep(0.6)
                result = run_triangle_recon(g1, g2, g3, threshold, period)
                st.write("Calculating unclaimed ITC...")
                time.sleep(0.4)
                saved = save_recon_result(S.email, chosen, result["summary"])
                S.recon_result   = result
                S.recon_client   = chosen
                S.recon_unlocked = S.get("role") in ("sovereign", "staff") or S.is_subscriber
                S.recon_saved_id = saved["id"] if saved else None
                S.recon_token    = saved["link_token"] if saved and saved.get("link_token") else uuid.uuid4().hex[:24]
                if S.recon_unlocked and S.recon_saved_id:
                    mark_result_unlocked(S.recon_saved_id)
                status.update(label="✅ Recon Complete!", state="complete",
                              expanded=False)
            except Exception as e:
                status.update(label="❌ Error", state="error")
                st.error(f"Processing error: {e}")
                st.stop()
        st.rerun()

    # Results
    if S.recon_result:
        res        = S.recon_result
        summary    = res["summary"]
        mismatches = res["mismatches"]
        client     = S.recon_client

        st.divider()
        st.markdown(f"### Results · **{client}** · {summary['period']}")

        # ── A. ITC Opportunity — Recoverable Wealth ──────────────────
        opportunity = summary["itc_opportunity"]
        overclaim   = summary["itc_overclaim"]

        if opportunity > 0:
            st.markdown(f"""
            <div class='wealth-card'>
                <p class='wealth-label'>💎 ITC OPPORTUNITY — RECOVERABLE WEALTH</p>
                <p class='wealth-number'>₹{opportunity:,.2f}</p>
                <p class='wealth-label'>
                ITC available in 2B but not yet claimed in 3B ·
                {summary['invoices_2b']} invoices scanned
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class='card card-amber' style='padding:20px; margin:12px 0;'>
                <p style='color:#00CFFF; font-weight:700; margin:0 0 6px 0;'>
                💎 ITC Opportunity</p>
                <p style='color:#FFFFFF; font-size:1.4rem; font-weight:700; margin:0;'>
                ₹0.00</p>
                <p style='color:#FFFFFF; font-size:0.85rem; margin:6px 0 0 0;'>
                All available ITC has been claimed in 3B.</p>
            </div>
            """, unsafe_allow_html=True)

        # ── B. ITC Overclaim Risk ─────────────────────────────────────
        if overclaim > 0:
            st.markdown(f"""
            <div style='background:linear-gradient(135deg,#2a0a0a,#3d1010);
                        border:2px solid #e85d50; border-radius:12px;
                        padding:20px 24px; margin:12px 0;'>
                <p style='color:#e85d50; font-weight:700; font-size:0.85rem;
                           letter-spacing:1px; margin:0 0 6px 0;'>
                ⚠️ ITC OVERCLAIM RISK — COMPLIANCE EXPOSURE</p>
                <p style='color:#FFFFFF; font-size:1.8rem; font-weight:700;
                           font-family:monospace; margin:0;'>
                ₹{overclaim:,.2f}</p>
                <p style='color:#e8a09a; font-size:0.85rem; margin:8px 0 0 0;'>
                3B claims exceed 2B availability. This is a GST compliance risk.
                Excess claimed ITC may attract interest + penalty under Sec 50.
                Review and reverse excess claim before next filing.
                </p>
            </div>
            """, unsafe_allow_html=True)

        # ── Summary metrics ───────────────────────────────────────────
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("ITC Available (2B)", f"₹{summary['itc_available_2b']:,.0f}")
        m2.metric("ITC Claimed (3B)",   f"₹{summary['itc_claimed_3b']:,.0f}")
        m3.metric("ITC Opportunity",    f"₹{opportunity:,.0f}")
        m4.metric("Overclaim Risk",     f"₹{overclaim:,.0f}",
                  delta=f"{summary.get('overclaim_pct',0)}% of 2B" if overclaim > 0 else None,
                  delta_color="inverse")

        # ── Recon Integrity Score ─────────────────────────────────────
        integrity   = summary.get("recon_integrity", 0)
        net_exp     = summary.get("net_exposure", 0)
        mm_pct      = summary.get("mismatch_pct", 0)

        integrity_color = "#3fb950" if integrity >= 75 else "#00CFFF" if integrity >= 50 else "#e85d50"
        integrity_label = "Strong" if integrity >= 75 else "Moderate" if integrity >= 50 else "Weak"

        st.markdown(f"""
        <div style='display:flex; gap:16px; margin:16px 0;'>
            <div style='flex:1; background:#071233; border:1px solid #1A3A6E;
                        border-top:3px solid {integrity_color};
                        border-radius:8px; padding:16px 20px;'>
                <p style='color:#FFFFFF; font-size:0.75rem; letter-spacing:1px;
                           margin:0 0 4px 0;'>RECON INTEGRITY SCORE</p>
                <p style='color:{integrity_color}; font-size:1.8rem; font-weight:700;
                           font-family:monospace; margin:0;'>{integrity}%</p>
                <p style='color:#FFFFFF; font-size:0.78rem; margin:4px 0 0 0;'>
                {integrity_label} · {100-integrity:.1f}% of combined invoices flagged</p>
            </div>
            <div style='flex:1; background:#071233; border:1px solid #1A3A6E;
                        border-top:3px solid #e85d50;
                        border-radius:8px; padding:16px 20px;'>
                <p style='color:#FFFFFF; font-size:0.75rem; letter-spacing:1px;
                           margin:0 0 4px 0;'>NET GST EXPOSURE</p>
                <p style='color:#e85d50; font-size:1.8rem; font-weight:700;
                           font-family:monospace; margin:0;'>₹{net_exp:,.0f}</p>
                <p style='color:#FFFFFF; font-size:0.78rem; margin:4px 0 0 0;'>
                Overclaim Risk + Value Mismatch Risk</p>
            </div>
            <div style='flex:1; background:#071233; border:1px solid #1A3A6E;
                        border-top:3px solid #00CFFF;
                        border-radius:8px; padding:16px 20px;'>
                <p style='color:#FFFFFF; font-size:0.75rem; letter-spacing:1px;
                           margin:0 0 4px 0;'>INVOICE MISMATCH RATE</p>
                <p style='color:#00CFFF; font-size:1.8rem; font-weight:700;
                           font-family:monospace; margin:0;'>{mm_pct}%</p>
                <p style='color:#FFFFFF; font-size:0.78rem; margin:4px 0 0 0;'>
                {summary.get("mismatch_count",0):,} of {summary.get("invoices_total", summary["invoices_2b"]):,} combined unique invoices</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Action Priority ───────────────────────────────────────────
        actions = []
        if overclaim > 0:
            sec50_30 = summary.get("sec50_30d", 0)
            sec50_90 = summary.get("sec50_90d", 0)
            actions.append(("🔴 Critical",
                f"Reverse excess ITC of ₹{overclaim:,.0f} before next filing. "
                f"Sec 50 interest (18% p.a.): ₹{sec50_30:,.0f} after 30 days, "
                f"₹{sec50_90:,.0f} after 90 days"))
        if summary.get("missing_in_2b_count", 0) > 0:
            actions.append(("🟠 High", f"Follow up {summary['missing_in_2b_count']} suppliers — their invoices are in GSTR-1 but missing from your 2B (₹{summary['missing_in_2b_sum']:,.0f} at stake)"))
        if summary.get("missing_in_1_count", 0) > 0:
            actions.append(("🟡 Medium", f"Reconcile {summary['missing_in_1_count']} invoices in 2B with no matching GSTR-1 entry — verify with supplier (₹{summary['missing_in_1_sum']:,.0f})"))
        if summary.get("value_mm_count", 0) > 0:
            actions.append(("🟡 Medium", f"Resolve {summary['value_mm_count']} value mismatches — same invoice, different tax amount in 1 vs 2B"))
        if opportunity > 0:
            actions.append(("💎 Opportunity", f"Claim ₹{opportunity:,.0f} unclaimed ITC in next 3B filing"))

        if actions:
            st.markdown("#### Action Priority")
            for priority, action in actions:
                color = "#e85d50" if "Critical" in priority else "#00CFFF" if "High" in priority else "#00CFFF" if "Medium" in priority else "#3fb950"
                st.markdown(f"""
                <div style='background:#071233; border-left:4px solid {color};
                            border-radius:0 8px 8px 0; padding:12px 16px; margin:6px 0;
                            display:flex; align-items:center; gap:12px;'>
                    <span style='color:{color}; font-weight:700; font-size:0.82rem;
                                 white-space:nowrap;'>{priority}</span>
                    <span style='color:#FFFFFF; font-size:0.88rem;'>{action}</span>
                </div>
                """, unsafe_allow_html=True)

        if not S.recon_unlocked:
            st.markdown("---")
            st.markdown(f"""
            <div style='background:#0D2157; border:2px solid #00CFFF;
                        border-radius:12px; padding:24px; margin:16px 0;'>
                <p style='color:#00CFFF; font-weight:700; font-size:1.1rem; margin:0 0 8px 0;'>
                🔒 Full Report — Subscribe to Unlock
                </p>
                <p style='color:#FFFFFF; font-size:0.9rem; margin:0 0 16px 0;'>
                You've found <b style='color:#00CFFF;'>₹{summary.get('itc_opportunity',0):,.0f}</b> in ITC opportunity.
                Subscribe to see exactly which invoices, which suppliers, and download the certified PDF.
                </p>
                <div style='background:#071233; border-radius:8px; padding:16px; margin-bottom:16px;'>
                <p style='color:#FFFFFF; font-size:0.85rem; margin:0 0 10px 0;'><b>What you unlock with ₹999/month:</b></p>
                <p style='color:#FFFFFF; font-size:0.83rem; margin:4px 0;'>✅ Invoice-level mismatch table ({summary.get('mismatch_count',0)} rows)</p>
                <p style='color:#FFFFFF; font-size:0.83rem; margin:4px 0;'>✅ Missing in GSTR-2B breakdown ({summary.get('missing_in_2b_count',0)} invoices)</p>
                <p style='color:#FFFFFF; font-size:0.83rem; margin:4px 0;'>✅ Supplier Risk Intelligence report</p>
                <p style='color:#FFFFFF; font-size:0.83rem; margin:4px 0;'>✅ Download Certified PDF</p>
                <p style='color:#FFFFFF; font-size:0.83rem; margin:4px 0;'>✅ Shareable Client Portal link</p>
                <p style='color:#FFFFFF; font-size:0.83rem; margin:4px 0;'>✅ AI Audit Narrative</p>
                </div>
                <p style='color:#FFFFFF; font-size:0.8rem; margin:0;'>
                🔥 Early Bird — ₹999/month or ₹8,999/year · Both prices locked forever
                </p>
            </div>
            """, unsafe_allow_html=True)

            if st.button("💳 Subscribe Now — Unlock Full Report", type="primary", use_container_width=True):
                st.markdown("""<script>window.open('https://itcrecon.in/#pricing','_blank');</script>""", unsafe_allow_html=True)
                st.info("Opening payment page at itcrecon.in... If it didn't open, visit itcrecon.in and click Subscribe.")

        else:
            st.success("✅ Full Report Unlocked")

            # ── Invoice-level breakdown — 3 separate tabs ─────────────
            st.markdown("#### Invoice-Level Analysis")

            # Summary row
            c1, c2, c3 = st.columns(3)
            c1.metric(
                f"Missing in 2B ({summary['missing_in_2b_count']} invoices)",
                f"₹{summary['missing_in_2b_sum']:,.0f}",
                help="In GSTR-1 but not reflected in 2B — supplier may not have filed"
            )
            c2.metric(
                f"Missing in GSTR-1 ({summary['missing_in_1_count']} invoices)",
                f"₹{summary['missing_in_1_sum']:,.0f}",
                help="In 2B but no matching GSTR-1 entry — sales reporting gap"
            )
            c3.metric(
                f"Value Mismatches ({summary['value_mm_count']} invoices)",
                f"₹{summary['value_mm_sum']:,.0f}",
                help="Same invoice found in both but tax amounts differ"
            )

            tab1, tab2, tab3, tab4 = st.tabs([
                f"⚠️ Missing in 2B ({summary['missing_in_2b_count']})",
                f"📋 Missing in GSTR-1 ({summary['missing_in_1_count']})",
                f"🔢 Value Mismatches ({summary['value_mm_count']})",
                f"🏭 Supplier Risk ({summary.get('supplier_count',0)})",
            ])
            with tab1:
                st.caption(
                    "These invoices are reported in suppliers' GSTR-1 but are "
                    "not reflected in your GSTR-2B. Possible reasons include "
                    "delayed filing, incorrect GSTIN reporting, or GST portal timing differences. "
                    "Follow up with the respective suppliers to ensure reflection in GSTR-2B, "
                    "after which the corresponding ITC may be eligible for claim."
                )
                df1 = res.get("missing_in_2b", pd.DataFrame())
                if not df1.empty:
                    st.dataframe(df1, use_container_width=True, height=380)
                else:
                    st.success("No missing-in-2B invoices. All supplier invoices reflected.")

            with tab2:
                st.caption(
                    "These invoices are in your GSTR-2B but have no matching "
                    "entry in GSTR-1. Possible reasons: supplier filed under "
                    "wrong GSTIN, or invoice number mismatch between systems. "
                    "Verify with supplier before claiming ITC."
                )
                df2 = res.get("missing_in_1", pd.DataFrame())
                if not df2.empty:
                    st.dataframe(df2, use_container_width=True, height=380)
                else:
                    st.success("No missing-in-GSTR-1 invoices.")

            with tab3:
                st.caption(
                    "Same invoice found in both GSTR-1 and 2B but tax amounts "
                    "differ. Could be amendment, rate difference, or data entry "
                    "error. Each needs individual verification."
                )
                df3 = res.get("value_mismatches", pd.DataFrame())
                if not df3.empty:
                    st.dataframe(df3, use_container_width=True, height=380)
                else:
                    st.success("No value mismatches found.")

            with tab4:
                si_df = res.get("supplier_intel", pd.DataFrame())
                if si_df is not None and not si_df.empty:
                    top5_pct   = summary.get("top5_concentration_pct", 0)
                    rep_count  = summary.get("repeat_defaulter_count", 0)
                    sup_count  = summary.get("supplier_count", 0)
                    top1_amt   = summary.get("top1_amount", 0)

                    mc1, mc2, mc3, mc4 = st.columns(4)
                    mc1.metric("Suppliers with Gap",      sup_count)
                    mc2.metric("Top 5 Concentration",     f"{top5_pct}%",
                               help="% of total missing ITC concentrated in top 5 suppliers")
                    mc3.metric("Repeat Defaulters",       rep_count,
                               delta="filed <50% of invoices" if rep_count else None,
                               delta_color="inverse")
                    mc4.metric("Highest Single Exposure", f"₹{top1_amt:,.0f}")

                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown("""
                    <div style='font-size:0.75rem; color:#FFFFFF; opacity:.7;
                                line-height:1.8; padding:8px 0;'>
                    Ranked by ITC at risk (highest first).<br>
                    Filing Rate = % of this supplier&#39;s own invoices that appeared in your GSTR-2B.<br>
                    Repeat Defaulter = filed &lt;50% of their own invoices — consider ITC reversal.<br>
                    Risk Score = ITC amount (60%) + filing failure rate (40%).
                    </div>
                    """, unsafe_allow_html=True)

                    def _color_risk_cell(val):
                        s = str(val)
                        if "Critical" in s: return "color: #e85d50; font-weight: bold"
                        if "High"     in s: return "color: #00CFFF; font-weight: bold"
                        if "Medium"   in s: return "color: #00CFFF"
                        if "Low"      in s: return "color: #3fb950"
                        return ""
                    def _color_defaulter(val):
                        return "color: #e85d50; font-weight: bold" if "Yes" in str(val) else ""

                    styled = si_df.style                        .map(_color_risk_cell,   subset=["Risk"])                        .map(_color_defaulter,   subset=["Repeat Defaulter"])

                    st.dataframe(styled, use_container_width=True, height=420)

                    if rep_count > 0:
                        st.warning(
                            f"⚠️ {rep_count} supplier(s) are Repeat Defaulters. "
                            f"ITC claimed from these may be challenged during GST audit. "
                            f"Consider reversing ITC and issuing a formal vendor notice."
                        )
                    if top5_pct >= 75:
                        st.info(
                            f"💡 Top 5 suppliers account for {top5_pct}% of your total gap. "
                            f"Resolving these 5 GSTINs closes most of the ITC risk."
                        )
                else:
                    st.success("✅ No supplier gaps. All supplier invoices reflected in GSTR-2B.")

            if mismatches.empty:
                st.info("No invoice mismatches above threshold. "
                        "ITC opportunity identified from 2B vs 3B gap only.")

            # ── AI Narrative ────────────────────────────────────────────
            if "ai_narrative" not in S or S.get("ai_narrative_client") != client:
                with st.spinner("🤖 AI is writing your audit narrative..."):
                    narrative = generate_ai_narrative(client, summary, mismatches)
                S.ai_narrative        = narrative
                S.ai_narrative_client = client
            else:
                narrative = S.get("ai_narrative")

            if narrative:
                st.markdown("<div style='height:8px'></div>",
                            unsafe_allow_html=True)
                st.markdown("""
                <p style='color:#00CFFF; font-size:0.78rem; font-weight:700;
                           letter-spacing:1px; margin:0 0 8px 0;'>
                🤖 AI AUDIT ANALYSIS</p>
                """, unsafe_allow_html=True)
                st.markdown(f"""
                <div style='background:#f0f7ff; border-left:3px solid #00CFFF;
                            border-radius:6px; padding:16px 20px;
                            color:#24292f; font-size:0.9rem; line-height:1.7;'>
                {narrative.replace(chr(10)+chr(10), '<br><br>').replace(chr(10), ' ')}
                </div>
                """, unsafe_allow_html=True)
                st.caption("Generated by Audit Desk AI · Powered by Claude · "
                           "For professional review only")
            elif ANTHROPIC_AVAILABLE:
                st.caption("💡 Add ANTHROPIC_API_KEY to secrets.toml "
                           "to enable AI narrative (free credits included)")
            # ── End AI Narrative ─────────────────────────────────────────

            pdf = generate_pdf(
                client, S.email, summary, mismatches,
                S.get("recon_token",""),
                ai_narrative=S.get("ai_narrative"),
                supplier_intel_df=res.get("supplier_intel")
            )
            st.download_button(
                "📥 Download Certified PDF",
                data=pdf,
                file_name=f"AuditDesk_{client.replace(' ','_')}"
                          f"_{date.today().isoformat()}.pdf",
                mime="application/pdf",
                use_container_width=True
            )

# ============================================================
# SECTION 11: CLIENT ROSTER
# ============================================================

def page_clients():
    st.markdown("<h1 style='color:#FFFFFF;'>👥 Client Roster</h1>",
                unsafe_allow_html=True)
    st.markdown(
        "<p style='color:#FFFFFF;'>Register clients once. "
        "History stays forever.</p>",
        unsafe_allow_html=True)

    if not has_full_access():
        st.warning("Subscribe to manage your client roster.")
        return

    # Add client form
    with st.expander("➕ Add New Client", expanded=False):
        with st.form("add_client"):
            c1, c2 = st.columns(2)
            with c1:
                name  = st.text_input("Entity Name (Legal)")
                gstin = st.text_input("Primary GSTIN")
            with c2:
                etype = st.selectbox("Entity Type",
                    ["Proprietorship","Partnership","Pvt Ltd",
                     "LLP","Public Ltd","Trust/Society"])
            if st.form_submit_button("Add Client", use_container_width=True):
                if name.strip():
                    if add_client(S.email, name.strip(), gstin.strip(), etype):
                        st.success(f"✅ {name} added!")
                        st.rerun()
                    else:
                        st.error("Could not add client.")
                else:
                    st.warning("Enter a client name.")

    clients = get_client_roster(S.email)
    st.markdown(f"<div class='section-hdr'>"
                f"Your Clients ({len(clients)})</div>",
                unsafe_allow_html=True)

    if not clients:
        st.info("No clients yet. Add your first client above.")
        return

    # Search
    search = st.text_input("🔍 Search clients", placeholder="Type name or GSTIN...")
    if search:
        clients = [c for c in clients if
                   search.lower() in c["client_name"].lower() or
                   search.lower() in (c.get("gstin","") or "").lower()]

    for c in clients:
        with st.container():
            st.markdown(f"""
            <div class='card' style='margin:6px 0; padding:14px 18px;'>
                <b style='color:#FFFFFF;'>{c['client_name']}</b>
                <span style='color:#FFFFFF; margin-left:16px; font-size:0.85rem;'>
                {c.get('entity_type','')} ·
                GSTIN: {c.get('gstin','—')} ·
                Added: {c.get('added_at','')[:10]}
                </span>
            </div>
            """, unsafe_allow_html=True)

# ============================================================
# SECTION 12: RECON HISTORY
# ============================================================

def page_history():
    st.markdown("<h1 style='color:#FFFFFF;'>📋 Recon History</h1>",
                unsafe_allow_html=True)

    if not has_full_access():
        st.warning("Subscribe to view recon history.")
        return

    history = get_recon_history(S.email)

    if not history:
        st.info("No recon runs yet.")
        if st.button("Run First Recon →"):
            nav("recon")
        return

    df = pd.DataFrame(history)
    total_wealth = df["wealth_found"].sum() if "wealth_found" in df else 0
    total_scans  = len(df)

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Scans",        total_scans)
    c2.metric("Total ITC Found",    f"₹{total_wealth:,.2f}")
    c3.metric("Est. CA Fees (10%)", f"₹{total_wealth*0.1:,.2f}")

    st.markdown("<br>", unsafe_allow_html=True)

    show = [c for c in
            ["timestamp","client_name","period","wealth_found",
             "mismatch_count","unlocked"]
            if c in df.columns]
    disp = df[show].copy()
    if "wealth_found" in disp:
        disp["wealth_found"] = disp["wealth_found"].apply(
            lambda x: f"₹{x:,.2f}")
    if "unlocked" in disp:
        disp["unlocked"] = disp["unlocked"].apply(
            lambda x: "✅ Unlocked" if x else "🔒 Locked")
    st.dataframe(disp, use_container_width=True, height=500)

# ============================================================
# SECTION 13: FREE CALCULATORS
# ============================================================

def page_calculators():
    st.markdown("<h1 style='color:#FFFFFF;'>🧮 Free Calculators</h1>",
                unsafe_allow_html=True)
    st.markdown(
        "<p style='color:#FFFFFF;'>Free with every account — "
        "no active subscription needed</p>",
        unsafe_allow_html=True)
    _fp_name = _get_secret("FEATURED_PARTNER_NAME", "")
    _fp_tag  = _get_secret("FEATURED_PARTNER_TAG", "")
    _fp_url  = _get_secret("FEATURED_PARTNER_URL", "#")
    if _fp_name:
        st.markdown(f"""
        <a href='{_fp_url}' target='_blank' style='text-decoration:none;'>
        <div style='background:#071233; border:1px solid #00CFFF;
                    border-radius:10px; padding:12px 20px; margin-bottom:20px;
                    display:flex; align-items:center; gap:20px;'>
            <span style='color:#00CFFF; font-size:0.65rem; font-family:IBM Plex Mono;
                          letter-spacing:2px; text-transform:uppercase; white-space:nowrap;'>
                📌 Featured Partner</span>
            <span style='color:#FFFFFF; font-size:0.88rem; font-weight:700;'>{_fp_name}</span>
            <span style='color:#FFFFFF; font-size:0.8rem; opacity:.8; flex:1;'>{_fp_tag}</span>
            <span style='color:#00CFFF; font-size:0.75rem;'>Visit →</span>
        </div></a>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style='background:#071233; border:1px dashed rgba(0,207,255,0.3);
                    border-radius:10px; padding:12px 20px; margin-bottom:20px;
                    display:flex; align-items:center; gap:20px;'>
            <span style='color:rgba(0,207,255,0.5); font-size:0.65rem;
                          font-family:IBM Plex Mono; letter-spacing:2px;
                          text-transform:uppercase; white-space:nowrap;'>
                📌 Featured Partner</span>
            <span style='color:rgba(255,255,255,0.3); font-size:0.88rem;
                          font-weight:700; font-style:italic;'>Your Brand Here</span>
            <span style='color:rgba(255,255,255,0.2); font-size:0.8rem; flex:1;'>
                Seen by every CA who uses these free tools — daily</span>
            <a href='mailto:auditdesk.hq@gmail.com?subject=Featured%20Partner%20Enquiry'
               style='color:rgba(0,207,255,0.45); font-size:0.75rem; text-decoration:none;
                      border:1px solid rgba(0,207,255,0.2); padding:4px 10px;
                      border-radius:4px; white-space:nowrap;'>1 spot available →</a>
        </div>
        """, unsafe_allow_html=True)

    # Require login — but NOT subscription
    if not S.logged_in:
        st.markdown("""
        <div class='card card-blue'>
        <b style='color:#00CFFF;'>Create a free account to access calculators</b><br>
        <span style='color:#FFFFFF;'>
        These tools are completely free forever. No subscription needed.<br>
        Just sign up (30 seconds, no card) to keep your calculation history.
        </span>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Create Free Account →", type="primary"):
            nav("login")
        return

    tab1, tab2, tab3, tab4 = st.tabs([
        "GST Calculator",
        "MSME 45-Day",
        "Sec 50 Interest",
        "HSN/SAC Finder"
    ])

    with tab1:
        log_calculator_use("gst_calculator", S.session_id)
        st.subheader("GST Calculator")
        c1, c2 = st.columns(2)
        with c1:
            amt  = st.number_input("Amount (₹)", 0.0, value=10000.0, step=100.0)
            rate = st.selectbox("GST Rate", [5,12,18,28], index=2)
            mode = st.radio("Mode",
                ["Exclusive (Add GST)", "Inclusive (Remove GST)"],
                horizontal=True)
        with c2:
            st.markdown("<br><br>", unsafe_allow_html=True)
            if "Exclusive" in mode:
                taxable = amt
                gst     = taxable * rate / 100
                total   = taxable + gst
            else:
                total   = amt
                taxable = total / (1 + rate/100)
                gst     = total - taxable
            cgst = gst / 2; sgst = gst / 2
            r1,r2 = st.columns(2)
            r1.metric("Taxable",  f"₹{taxable:,.2f}")
            r2.metric(f"GST {rate}%", f"₹{gst:,.2f}")
            r3,r4 = st.columns(2)
            r3.metric("CGST",   f"₹{cgst:,.2f}")
            r4.metric("SGST",   f"₹{sgst:,.2f}")
            st.metric("Total",  f"₹{total:,.2f}")

    with tab2:
        log_calculator_use("msme_45day", S.session_id)
        st.subheader("MSME 45-Day Payment Checker — Section 43B(h)")
        inv_date = st.date_input("Invoice Date")
        vtype    = st.selectbox("Vendor Type", [
            "Micro/Small Enterprise — 45 days",
            "No Written Agreement — 15 days"])
        limit    = 45 if "45" in vtype else 15
        due      = inv_date + timedelta(days=limit)
        today    = date.today()
        left     = (due - today).days

        c1,c2,c3 = st.columns(3)
        c1.metric("Invoice Date",  inv_date.strftime("%d %b %Y"))
        c2.metric("Due Date",      due.strftime("%d %b %Y"))
        if left < 0:
            c3.metric("Status", f"{abs(left)}d OVERDUE",
                      delta="Disallowance Risk", delta_color="inverse")
            st.error(f"⚠️ {abs(left)} days overdue — risk of Section 43B(h) disallowance.")
        elif left <= 5:
            c3.metric("Status", f"{left}d left", delta="Urgent")
            st.warning(f"Only {left} days remaining.")
        else:
            c3.metric("Status", f"{left}d left")
            st.success("Payment on track.")

    with tab3:
        log_calculator_use("sec50_interest", S.session_id)
        st.subheader("Section 50 — GST Late Payment Interest (18% p.a.)")
        tax  = st.number_input("Tax Amount (₹)", 0.0, value=50000.0, step=1000.0)
        due2 = st.date_input("Due Date", key="d2")
        paid = st.date_input("Payment Date", key="p2")
        days = max(0, (paid - due2).days)
        intr = tax * 0.18 * days / 365
        c1,c2,c3 = st.columns(3)
        c1.metric("Days Delayed", days)
        c2.metric("Interest",     f"₹{intr:,.2f}")
        c3.metric("Total Payable",f"₹{tax+intr:,.2f}")

    with tab4:
        log_calculator_use("hsn_finder", S.session_id)
        st.subheader("HSN/SAC Code Finder")
        st.caption("Common codes — type to search")
        # Embedded common HSN/SAC reference
        hsn_data = [
            ("0101","Live horses, asses, mules","Nil"),
            ("1001","Wheat and meslin","Nil"),
            ("2701","Coal; briquettes, ovoids","5%"),
            ("3004","Medicaments","12%"),
            ("3401","Soap, organic surface-active products","18%"),
            ("3923","Plastic articles for packaging","18%"),
            ("4901","Printed books","Nil"),
            ("6101","Men's overcoats, jackets","5%/12%"),
            ("7208","Flat-rolled iron/steel products","18%"),
            ("8471","Computers, laptops","18%"),
            ("8517","Telephones, smartphones","18%"),
            ("8703","Motor cars","28%+cess"),
            ("9403","Other furniture","18%"),
            ("9503","Toys","12%"),
            ("996111","SAC: Postal/courier services","18%"),
            ("996311","SAC: Hotel accommodation","12%/18%"),
            ("997211","SAC: Renting immovable property","18%"),
            ("998311","SAC: Management consulting","18%"),
            ("998399","SAC: IT software services","18%"),
            ("999311","SAC: Education services","Exempt/18%"),
        ]
        df_hsn = pd.DataFrame(hsn_data, columns=["Code","Description","GST Rate"])
        search = st.text_input("Search by description or code",
                               placeholder="e.g. software, furniture, coal...")
        if search:
            mask = (df_hsn["Description"].str.contains(search, case=False) |
                    df_hsn["Code"].str.contains(search, case=False))
            df_hsn = df_hsn[mask]
        st.dataframe(df_hsn, use_container_width=True, hide_index=True)
        st.caption("This is a simplified reference list. "
                   "Always verify on the official GST portal.")

    # Soft registration prompt for anonymous users
    if not S.logged_in:
        S.calc_uses = S.get("calc_uses", 0) + 1
        if S.calc_uses >= 2:
            st.markdown("---")
            st.markdown("""
            <div class='card card-blue'>
            <b style='color:#00CFFF;'>📊 Save your calculation history</b><br>
            <span style='color:#FFFFFF;'>
            Create a free account to save results and get access
            to Triangle Recon (14-day free trial, no card needed).
            </span>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Create Free Account →", type="primary"):
                nav("login")

# ============================================================
# SECTION 14: SUBSCRIBE PAGE
# ============================================================

def page_subscribe():
    # Payment happens at itcrecon.in — redirect immediately
    st.markdown("""
    <style>section[data-testid="stSidebar"]{display:none;}</style>
    <meta http-equiv="refresh" content="0; url=https://itcrecon.in/#pricing">
    """, unsafe_allow_html=True)
    st.markdown("""
    <div style='display:flex;align-items:center;justify-content:center;
                min-height:70vh;flex-direction:column;gap:20px;text-align:center;'>
        <p style='color:#00CFFF;font-family:IBM Plex Mono;font-size:0.75rem;
                  letter-spacing:3px;'>REDIRECTING</p>
        <p style='color:#FFFFFF;font-size:1.3rem;font-weight:700;'>
        Taking you to the payment page...</p>
        <p style='color:#FFFFFF;font-size:0.9rem;'>
        Payment is processed securely at itcrecon.in</p>
        <a href='https://itcrecon.in/#pricing'
           style='background:linear-gradient(135deg,#0095BF,#00CFFF);color:#0A1B44;
                  padding:14px 32px;border-radius:8px;text-decoration:none;
                  font-weight:700;font-size:1rem;margin-top:8px;'>
        Go to Payment Page →</a>
    </div>
    """, unsafe_allow_html=True)
    return

    # ── DEAD CODE — kept for reference ──
    count  = get_subscriber_count()
    eb_open = count < EARLY_BIRD_LIMIT
    slots_left = max(0, EARLY_BIRD_LIMIT - count)

    if eb_open:
        st.markdown("""
        <div class='eb-banner'>
            <div style='font-size:2rem;'>🔥</div>
            <div>
                <b style='color:#00CFFF; font-size:1.1rem;'>
                Early Bird Pricing — Limited Time</b><br>
                <span style='color:#FFFFFF;'>
                Both monthly (₹999) and annual (₹8,999) prices are
                <b>locked forever</b> for early subscribers —
                even after prices rise for new users.
                Continuous subscription required to keep the locked rate.
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # If already subscribed — show their personal renewal price
    if S.is_subscriber and S.subscription:
        sub = S.subscription
        renew_m, _, _ = get_renewal_amount(S.email, "monthly")
        renew_a, _, _ = get_renewal_amount(S.email, "annual")
        eb_locked     = sub.get("early_bird", False)
        st.markdown(f"""
        <div class='card card-green'>
        <b style='color:#00CFFF;'>✅ Your Active Subscription</b><br>
        <span style='color:#FFFFFF;'>
        Current plan: <b style='color:#FFFFFF;'>{sub.get('plan','').title()}</b> ·
        Your renewal prices:
        <b style='color:#00CFFF;'>₹{renew_m:,}/month</b> or
        <b style='color:#00CFFF;'>₹{renew_a:,}/year</b>
        {"· 🔥 <b style='color:#00CFFF;'>Early Bird locked — this price is yours forever</b>"
         if eb_locked else ""}
        </span>
        </div>
        """, unsafe_allow_html=True)

    # Pricing cards
    col1, col2 = st.columns(2)

    with col1:
        monthly_price = MONTHLY_PRICE if eb_open else FUTURE_MONTHLY
        st.markdown(f"""
        <div class='price-card'>
            <p style='color:#FFFFFF; margin:0;'>MONTHLY</p>
            <p class='price-amount'>₹{monthly_price:,}</p>
            <p class='price-period'>per month · cancel anytime</p>
            <hr style='border-color:#1A3A6E; margin:16px 0;'>
            <p style='color:#FFFFFF; font-size:0.9rem;'>
            ✅ Unlimited Triangle Recon<br>
            ✅ Client Roster<br>
            ✅ Certified PDF Reports<br>
            ✅ Shareable Client Links<br>
            ✅ Monthly ITC Dashboard<br>
            ✅ All Free Calculators<br>
            {"🔥 <b>Early Bird Price</b> — this ₹999 is locked forever" if eb_open else ""}
            </p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Subscribe Monthly →", type="primary",
                     use_container_width=True, key="sub_monthly"):
            _initiate_payment("monthly", monthly_price)

    with col2:
        annual_price = ANNUAL_PRICE if eb_open else FUTURE_ANNUAL
        saving = (monthly_price * 12) - annual_price
        st.markdown(f"""
        <div class='price-card featured'>
            <p style='color:#00CFFF; font-weight:700; margin:0;'>
            ⭐ ANNUAL · MOST POPULAR</p>
            <p class='price-amount'>₹{annual_price:,}</p>
            <p class='price-period'>per year · save ₹{saving:,}</p>
            <hr style='border-color:#1A3A6E; margin:16px 0;'>
            <p style='color:#FFFFFF; font-size:0.9rem;'>
            ✅ Everything in Monthly<br>
            ✅ 2 months free (vs monthly)<br>
            ✅ Fully tax deductible as software<br>
            ✅ Priority support<br>
            {"🔥 <b>Early Bird Price</b> — this ₹8,999 is locked forever" if eb_open else ""}
            </p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Subscribe Annual → Best Value",
                     type="primary", use_container_width=True,
                     key="sub_annual"):
            _initiate_payment("annual", annual_price)

    st.markdown("""
    <div style='text-align:center; color:#FFFFFF; font-size:0.85rem; margin-top:24px;'>
    🔒 <b style='color:#00CFFF;'>Both monthly and annual Early Bird prices are locked
    permanently</b> — as long as your subscription remains continuous.<br>
    If you cancel and rejoin later, you pay the price applicable at that time.<br>
    <span style='color:#FFFFFF;'>14-day free trial · no card needed · cancel anytime</span>
    </div>
    """, unsafe_allow_html=True)

def get_renewal_amount(email, plan):
    """
    RENEWAL PRICE LOGIC — The Early Bird Annual Fix.

    Rule 1: If subscriber has early_bird = true on their existing
            subscription, they ALWAYS renew at their original locked amount.
            This applies to BOTH monthly and annual plans.
            The current subscriber count is completely irrelevant at renewal.

    Rule 2: If they cancelled and are rejoining, early_bird = false
            and they pay the current market price.

    Rule 3: Brand new subscriber — price depends on whether
            early bird slots are still open right now.

    Returns: (amount, early_bird_flag, is_renewal)
    """
    try:
        # Check if this email has ANY subscription history
        # including cancelled ones — to detect rejoining
        history = db("subscriptions").select("*")\
            .eq("email", email)\
            .order("started_at", desc=True)\
            .limit(1).execute()

        if history.data:
            last_sub = history.data[0]
            was_early_bird = last_sub.get("early_bird", False)
            was_active     = last_sub.get("status") == "active"

            # CASE 1: Currently active early bird renewing
            # Give them their original locked price — no questions asked
            if was_active and was_early_bird:
                original_amount = last_sub.get("amount", 0)
                return original_amount, True, True

            # CASE 2: Was early bird but cancelled — loses privilege
            if not was_active and was_early_bird:
                # They cancelled — rejoin at current price, no early bird
                eb_open = is_early_bird_open()
                if plan == "monthly":
                    price = MONTHLY_PRICE if eb_open else FUTURE_MONTHLY
                else:
                    price = ANNUAL_PRICE if eb_open else FUTURE_ANNUAL
                return price, False, False  # early_bird = False, period.

            # CASE 3: Was NOT early bird (joined after slot 5000)
            # Renews at same amount they originally paid
            if was_active and not was_early_bird:
                original_amount = last_sub.get("amount", 0)
                return original_amount, False, True

        # CASE 4: Brand new subscriber — never subscribed before
        eb_open = is_early_bird_open()
        if plan == "monthly":
            price = MONTHLY_PRICE if eb_open else FUTURE_MONTHLY
        else:
            price = ANNUAL_PRICE if eb_open else FUTURE_ANNUAL
        return price, eb_open, False

    except Exception as e:
        # Fallback — charge current price, no early bird
        eb_open = is_early_bird_open()
        price = (MONTHLY_PRICE if plan == "monthly" else ANNUAL_PRICE) \
                if eb_open else \
                (FUTURE_MONTHLY if plan == "monthly" else FUTURE_ANNUAL)
        return price, eb_open, False


def _initiate_payment(plan, requested_amount):
    """
    Handles both new subscriptions and renewals.
    Always uses get_renewal_amount() to determine the correct price —
    never trusts the amount passed from the UI for renewals.
    """
    if not DB_LIVE:
        st.error("Database not connected.")
        return

    # Always recalculate the correct amount server-side
    # This prevents any UI manipulation of the price
    correct_amount, eb_flag, is_renewal = get_renewal_amount(S.email, plan)

    try:
        if razor_client:
            notes = {
                "email"      : S.email,
                "plan"       : plan,
                "early_bird" : str(eb_flag),
                "is_renewal" : str(is_renewal),
                "locked_amount": str(correct_amount),
            }
            order = razor_client.order.create({
                "amount"         : int(correct_amount * 100),
                "currency"       : "INR",
                "payment_capture": 1,
                "notes"          : notes
            })
            st.info(f"Razorpay Order ID: `{order['id']}`")
            st.markdown(f"""
            <div class='card card-blue'>
            <b>Order Summary</b><br>
            Plan: <b>{plan.title()}</b> ·
            Amount: <b>₹{correct_amount:,}</b> ·
            Early Bird: <b>{'Yes 🔥' if eb_flag else 'No'}</b>
            {'· <b>Renewal — your locked price applied</b>' if is_renewal else ''}
            </div>
            """, unsafe_allow_html=True)
            st.info("In production: Razorpay checkout opens here. "
                    "On payment success, webhook calls activate_subscription().")

        else:
            # Simulation mode — activate directly
            activate_subscription(S.email, plan, correct_amount, eb_flag)

    except Exception as e:
        st.error(f"Payment error: {e}")


def activate_subscription(email, plan, amount, early_bird):
    """
    Called by Razorpay webhook on payment success.
    Also used in simulation mode.

    CRITICAL RULE: Never overwrite early_bird = true with false.
    If a subscriber is renewing, UPDATE the existing row.
    If new, INSERT a new row.
    This preserves the early_bird flag through all renewals.
    """
    try:
        existing = db("subscriptions").select("*")\
            .eq("email", email)\
            .eq("status", "active")\
            .maybe_single().execute()

        if existing.data:
            # RENEWAL — update renewed_at and amount only
            # Never touch early_bird — it was set at first subscription
            # and is permanent as long as they stay subscribed
            db("subscriptions").update({
                "renewed_at" : now_iso(),
                "amount"     : amount,
                "plan"       : plan,
                # early_bird is intentionally NOT updated here
            }).eq("id", existing.data["id"]).execute()
        else:
            # NEW subscription
            db("subscriptions").insert({
                "email"      : email,
                "plan"       : plan,
                "amount"     : amount,
                "early_bird" : early_bird,
                "status"     : "active",
                "started_at" : now_iso(),
                "renewed_at" : now_iso(),
            }).execute()

        snapshot_sovereign()
        sub = get_user_subscription(email)
        if sub:
            _set_session_subscriber(email, sub)

        # Send subscriber welcome email
        try:
            send_welcome_email_subscriber(
                email, plan, early_bird, int(amount))
        except:
            pass
        msg = "✅ Subscription activated!"
        if early_bird:
            msg += " 🔥 Early Bird price locked forever."
        st.success(msg)
        st.rerun()

    except Exception as e:
        st.error(f"Activation error: {e}")

# ============================================================
# SECTION 15: PUBLIC REPORT PAGE (shareable link)
# ============================================================

def page_public_report(token):
    report = get_report_by_token(token)
    if not report:
        st.error("Report not found or not yet unlocked.")
        st.caption("Ask your CA to unlock the report first.")
        return

    # CA-branded — no Audit Desk branding shown to client
    st.markdown(f"""
    <div style='max-width:700px; margin:0 auto;'>
    <h2 style='color:#FFFFFF;'>GST ITC Recovery Report</h2>
    <p style='color:#FFFFFF;'>Prepared by: <b style='color:#FFFFFF;'>
    {report['email']}</b></p>
    <p style='color:#FFFFFF;'>Client: <b style='color:#FFFFFF;'>
    {report['client_name']}</b></p>
    <p style='color:#FFFFFF;'>Period: {report.get('period','')}</p>
    </div>
    """, unsafe_allow_html=True)

    wealth = report["wealth_found"]
    st.markdown(f"""
    <div class='wealth-card' style='max-width:700px; margin:16px auto;'>
        <p class='wealth-label'>💎 UNCLAIMED ITC RECOVERED</p>
        <p class='wealth-number'>₹{wealth:,.2f}</p>
        <p class='wealth-label'>
        Identified through forensic analysis of your GST filings
        </p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("ITC Available",  f"₹{report['itc_available']:,.0f}")
    c2.metric("ITC Claimed",    f"₹{report['itc_claimed']:,.0f}")
    c3.metric("Unclaimed",      f"₹{report['unclaimed_itc']:,.0f}")

    st.markdown("""
    <div style='max-width:700px; margin:24px auto; background:#0D2157;
                border:1px solid #1A3A6E; border-radius:10px; padding:20px;'>
    <b style='color:#FFFFFF;'>What this means for you:</b><br><br>
    <span style='color:#FFFFFF;'>
    Your CA has identified Input Tax Credit that is available in
    your GSTR-2B but has not yet been claimed in your GSTR-3B returns.
    This represents real money owed to your business that can be
    recovered by filing an amendment. Contact your CA to initiate
    the recovery process.
    </span>
    </div>
    """, unsafe_allow_html=True)

    st.caption(
        f"Forensic Analysis by Audit Desk™ · itcrecon.in · "
        f"Report ID: {token} · "
        f"Generated: {report['timestamp'][:10]}"
    )

# ============================================================
# SECTION 16: SOVEREIGN DASHBOARD (owner only)
# ============================================================

def page_sovereign():
    if S.get("role") != "sovereign":
        st.error("Access denied. Sovereign login required.")
        return

    import plotly.graph_objects as go

    # ── Header ──────────────────────────────────────────────────────────────────
    st.markdown("""
    <div style='background:linear-gradient(135deg,#071233 0%,#071233 100%);
                border:1px solid #00CFFF; border-radius:14px;
                padding:24px 28px; margin-bottom:24px;'>
        <p style='color:#00CFFF; font-family:IBM Plex Mono; font-size:0.8rem;
                  letter-spacing:3px; margin:0;'>SOVEREIGN DASHBOARD</p>
        <h1 style='color:#FFFFFF; margin:4px 0; font-size:2rem;'>
        Audit Desk — Business Intelligence</h1>
        <p style='color:#FFFFFF; margin:0; font-size:0.9rem;'>
        Live metrics · Acquisition ready · Screenshot any section
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── Fetch all data ───────────────────────────────────────────────────────────
    data       = get_sovereign_data()
    snaps      = data.get("snapshots", [])
    recons     = data.get("recons", [])
    calcs      = data.get("calc_events", [])

    subs        = get_subscriber_count()
    free_users  = get_free_user_count()
    mrr_monthly = subs * MONTHLY_PRICE
    arr         = mrr_monthly * 12
    eb_used     = min(subs, EARLY_BIRD_LIMIT)
    eb_slots    = max(0, EARLY_BIRD_LIMIT - subs)

    total_recons = len(recons)
    total_wealth = sum(r.get("wealth_found", 0) for r in recons)
    unlocked     = sum(1 for r in recons if r.get("unlocked"))
    unlock_rate  = round(unlocked / total_recons * 100, 1) if total_recons else 0

    val_3x  = arr * 3
    val_5x  = arr * 5
    val_10x = arr * 10

    report_date = datetime.now().strftime("%d %B %Y, %I:%M %p")

    # ════════════════════════════════════════════════════════════════════════════
    # SECTION A — REVENUE (Screenshot this for acquirer)
    # ════════════════════════════════════════════════════════════════════════════
    st.markdown("""
    <p style='color:#00CFFF; font-family:IBM Plex Mono; font-size:0.75rem;
              letter-spacing:2px; margin:8px 0 12px 0;'>A · REVENUE</p>
    """, unsafe_allow_html=True)

    r1,r2,r3,r4 = st.columns(4)
    for col, val, label, color in [
        (r1, f"₹{mrr_monthly:,.0f}",  "Monthly Recurring Revenue", "#00CFFF"),
        (r2, f"₹{arr:,.0f}",          "Annual Run Rate (ARR)",     "#00CFFF"),
        (r3, f"{subs:,}",             "Live Subscribers",          "#00CFFF"),
        (r4, f"₹{MONTHLY_PRICE:,}",   "Price Per Subscriber/Month","#FFFFFF"),
    ]:
        col.markdown(f"""
        <div style='background:#071233; border:1px solid #1A3A6E;
                    border-radius:10px; padding:18px; text-align:center;
                    border-top:3px solid {color};'>
            <p style='font-family:IBM Plex Mono; color:{color};
                      font-size:1.7rem; font-weight:700; margin:0;'>{val}</p>
            <p style='color:#FFFFFF; font-size:0.75rem;
                      margin:6px 0 0 0;'>{label}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════════════════════
    # SECTION B — USER BASE
    # ════════════════════════════════════════════════════════════════════════════
    st.markdown("""
    <p style='color:#00CFFF; font-family:IBM Plex Mono; font-size:0.75rem;
              letter-spacing:2px; margin:8px 0 12px 0;'>B · USER BASE</p>
    """, unsafe_allow_html=True)

    u1,u2,u3,u4,u5 = st.columns(5)
    for col, val, label, color in [
        (u1, f"{subs:,}",           "Paying Subscribers",        "#00CFFF"),
        (u2, f"{free_users:,}",     "Free Registered Users",     "#00CFFF"),
        (u3, f"{subs+free_users:,}","Total Registered Users",    "#FFFFFF"),
        (u4, f"{eb_used:,} / {EARLY_BIRD_LIMIT:,}", "Early Bird Slots Used", "#00CFFF"),
        (u5, f"{eb_slots:,}",       "Early Bird Slots Remaining","#FFFFFF"),
    ]:
        col.markdown(f"""
        <div style='background:#071233; border:1px solid #1A3A6E;
                    border-radius:10px; padding:16px; text-align:center;'>
            <p style='font-family:IBM Plex Mono; color:{color};
                      font-size:1.4rem; font-weight:700; margin:0;'>{val}</p>
            <p style='color:#FFFFFF; font-size:0.72rem;
                      margin:6px 0 0 0;'>{label}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════════════════════
    # SECTION C — PRODUCT USAGE (proof of engagement)
    # ════════════════════════════════════════════════════════════════════════════
    st.markdown("""
    <p style='color:#00CFFF; font-family:IBM Plex Mono; font-size:0.75rem;
              letter-spacing:2px; margin:8px 0 12px 0;'>C · PRODUCT USAGE</p>
    """, unsafe_allow_html=True)

    p1,p2,p3,p4 = st.columns(4)
    wealth_display = (
        f"₹{total_wealth/10000000:.2f} Cr" if total_wealth >= 10000000 else
        f"₹{total_wealth/100000:.2f} L"    if total_wealth >= 100000   else
        f"₹{total_wealth:,.0f}"
    )
    for col, val, label, color in [
        (p1, f"{total_recons:,}",  "Total Triangle Recon Scans",         "#00CFFF"),
        (p2, wealth_display,        "Total ITC Found Platform-Wide",       "#00CFFF"),
        (p3, f"{unlock_rate}%",    "Report Unlock Rate",                  "#00CFFF"),
        (p4, f"{unlocked:,}",      "Full Reports Unlocked",               "#FFFFFF"),
    ]:
        col.markdown(f"""
        <div style='background:#071233; border:1px solid #1A3A6E;
                    border-radius:10px; padding:18px; text-align:center;
                    border-top:3px solid {color};'>
            <p style='font-family:IBM Plex Mono; color:{color};
                      font-size:1.7rem; font-weight:700; margin:0;'>{val}</p>
            <p style='color:#FFFFFF; font-size:0.75rem;
                      margin:6px 0 0 0;'>{label}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════════════════════
    # SECTION D — ACQUISITION VALUATION (the screenshot acquirers want)
    # ════════════════════════════════════════════════════════════════════════════
    st.markdown("""
    <p style='color:#00CFFF; font-family:IBM Plex Mono; font-size:0.75rem;
              letter-spacing:2px; margin:8px 0 12px 0;'>D · ACQUISITION VALUATION</p>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style='background:linear-gradient(135deg,#071233 0%,#0D2157 100%);
                border:1px solid #00CFFF; border-radius:14px; padding:28px;'>
        <p style='color:#00CFFF; font-weight:700; font-size:1rem; margin:0 0 20px 0;'>
        📋 Audit Desk — Acquisition Snapshot &nbsp;
        <span style='color:#FFFFFF; font-size:0.8rem; font-weight:400;'>
        as of {report_date}</span>
        </p>
        <div style='display:grid; grid-template-columns:1fr 1fr; gap:12px;'>
            <div style='background:#071233; border:1px solid #1A3A6E;
                        border-radius:8px; padding:16px;'>
                <p style='color:#FFFFFF; font-size:0.75rem; margin:0;'>MRR</p>
                <p style='color:#00CFFF; font-family:IBM Plex Mono;
                          font-size:1.4rem; font-weight:700; margin:4px 0;'>
                ₹{mrr_monthly:,.0f}</p>
            </div>
            <div style='background:#071233; border:1px solid #1A3A6E;
                        border-radius:8px; padding:16px;'>
                <p style='color:#FFFFFF; font-size:0.75rem; margin:0;'>ARR</p>
                <p style='color:#00CFFF; font-family:IBM Plex Mono;
                          font-size:1.4rem; font-weight:700; margin:4px 0;'>
                ₹{arr:,.0f}</p>
            </div>
            <div style='background:#071233; border:1px solid #1A3A6E;
                        border-radius:8px; padding:16px;'>
                <p style='color:#FFFFFF; font-size:0.75rem; margin:0;'>
                Active Subscribers</p>
                <p style='color:#FFFFFF; font-family:IBM Plex Mono;
                          font-size:1.4rem; font-weight:700; margin:4px 0;'>
                {subs:,}</p>
            </div>
            <div style='background:#071233; border:1px solid #1A3A6E;
                        border-radius:8px; padding:16px;'>
                <p style='color:#FFFFFF; font-size:0.75rem; margin:0;'>
                Total Registered Users</p>
                <p style='color:#FFFFFF; font-family:IBM Plex Mono;
                          font-size:1.4rem; font-weight:700; margin:4px 0;'>
                {subs+free_users:,}</p>
            </div>
            <div style='background:#071233; border:1px solid #1A3A6E;
                        border-radius:8px; padding:16px;'>
                <p style='color:#FFFFFF; font-size:0.75rem; margin:0;'>
                Total ITC Found (Platform)</p>
                <p style='color:#FFFFFF; font-family:IBM Plex Mono;
                          font-size:1.4rem; font-weight:700; margin:4px 0;'>
                {wealth_display}</p>
            </div>
            <div style='background:#071233; border:1px solid #1A3A6E;
                        border-radius:8px; padding:16px;'>
                <p style='color:#FFFFFF; font-size:0.75rem; margin:0;'>
                Total Recon Scans</p>
                <p style='color:#FFFFFF; font-family:IBM Plex Mono;
                          font-size:1.4rem; font-weight:700; margin:4px 0;'>
                {total_recons:,}</p>
            </div>
        </div>
        <div style='margin-top:20px; padding-top:20px;
                    border-top:1px solid #1A3A6E;'>
            <p style='color:#00CFFF; font-weight:700; margin:0 0 12px 0;'>
            Estimated Valuation Range</p>
            <div style='display:grid; grid-template-columns:1fr 1fr 1fr; gap:12px;'>
                <div style='text-align:center; padding:12px;
                            background:#071233; border-radius:8px;
                            border:1px solid #1A3A6E;'>
                    <p style='color:#FFFFFF; font-size:0.75rem; margin:0;'>
                    Conservative (3× ARR)</p>
                    <p style='color:#00CFFF; font-family:IBM Plex Mono;
                              font-size:1.2rem; font-weight:700; margin:4px 0;'>
                    ₹{val_3x:,.0f}</p>
                </div>
                <div style='text-align:center; padding:12px;
                            background:#0a1a0a; border-radius:8px;
                            border:1px solid #0080A8;'>
                    <p style='color:#FFFFFF; font-size:0.75rem; margin:0;'>
                    Mid-Market (5× ARR)</p>
                    <p style='color:#00CFFF; font-family:IBM Plex Mono;
                              font-size:1.2rem; font-weight:700; margin:4px 0;'>
                    ₹{val_5x:,.0f}</p>
                </div>
                <div style='text-align:center; padding:12px;
                            background:#071233; border-radius:8px;
                            border:1px solid #00CFFF;'>
                    <p style='color:#FFFFFF; font-size:0.75rem; margin:0;'>
                    Premium (10× ARR)</p>
                    <p style='color:#00CFFF; font-family:IBM Plex Mono;
                              font-size:1.2rem; font-weight:700; margin:4px 0;'>
                    ₹{val_10x:,.0f}</p>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════════════════════
    # SECTION E — SUBSCRIBER LIST (sovereign eyes only)
    # ════════════════════════════════════════════════════════════════════════════
    st.markdown("""
    <p style='color:#00CFFF; font-family:IBM Plex Mono; font-size:0.75rem;
              letter-spacing:2px; margin:8px 0 12px 0;'>
    E · SUBSCRIBER REGISTRY — SOVEREIGN EYES ONLY</p>
    """, unsafe_allow_html=True)

    try:
        all_subs = db("subscriptions").select("*")            .order("started_at", desc=True).execute()
        if all_subs.data:
            df_subs = pd.DataFrame(all_subs.data)
            # Clean up for display
            show_cols = [c for c in
                ["email","plan","amount","early_bird","status",
                 "started_at","renewed_at","cancelled_at"]
                if c in df_subs.columns]
            df_display = df_subs[show_cols].copy()
            if "amount" in df_display.columns:
                df_display["amount"] = df_display["amount"].apply(
                    lambda x: f"₹{float(x):,.0f}")
            if "early_bird" in df_display.columns:
                df_display["early_bird"] = df_display["early_bird"].apply(
                    lambda x: "🔥 Yes" if x else "No")
            if "started_at" in df_display.columns:
                df_display["started_at"] = df_display["started_at"].apply(
                    lambda x: str(x)[:10])
            if "renewed_at" in df_display.columns:
                df_display["renewed_at"] = df_display["renewed_at"].apply(
                    lambda x: str(x)[:10] if x else "—")
            if "cancelled_at" in df_display.columns:
                df_display["cancelled_at"] = df_display["cancelled_at"].apply(
                    lambda x: str(x)[:10] if x else "—")

            active_count   = len(df_display[df_display.get("status","") == "active"])                              if "status" in df_display.columns else len(df_display)
            cancelled_count= len(df_display) - active_count

            c1,c2,c3 = st.columns(3)
            c1.metric("Total Subscribers (All Time)", len(df_display))
            c2.metric("Currently Active",             active_count)
            c3.metric("Cancelled / Lapsed",           cancelled_count)

            st.dataframe(df_display, use_container_width=True, hide_index=True,
                         height=400)

            # Download as CSV for meetings
            csv = df_display.to_csv(index=False)
            st.download_button(
                "📥 Download Subscriber List (CSV)",
                data=csv,
                file_name=f"AuditDesk_Subscribers_{date.today().isoformat()}.csv",
                mime="text/csv",
                type="secondary"
            )
        else:
            st.info("No subscribers yet.")
    except Exception as e:
        st.error(f"Could not load subscriber list: {e}")

    st.markdown("<br>", unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════════════════════
    # SECTION F — GROWTH CHART
    # ════════════════════════════════════════════════════════════════════════════
    if snaps:
        st.markdown("""
        <p style='color:#00CFFF; font-family:IBM Plex Mono; font-size:0.75rem;
                  letter-spacing:2px; margin:8px 0 12px 0;'>F · GROWTH CHART</p>
        """, unsafe_allow_html=True)

        df_s = pd.DataFrame(snaps)
        if "date" in df_s.columns and "subscribers" in df_s.columns:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df_s["date"], y=df_s["subscribers"],
                fill="tozeroy", line=dict(color="#00CFFF", width=2),
                fillcolor="rgba(0,207,255,0.10)", name="Subscribers"
            ))
            mrr_col = df_s.get("mrr", df_s["subscribers"] * MONTHLY_PRICE)                       if "mrr" in df_s.columns else df_s["subscribers"] * MONTHLY_PRICE
            fig.add_trace(go.Scatter(
                x=df_s["date"], y=mrr_col,
                line=dict(color="#00CFFF", width=2, dash="dot"),
                name="MRR (₹)", yaxis="y2"
            ))
            fig.update_layout(
                title=dict(text="Subscriber & Revenue Growth",
                           font=dict(color="#FFFFFF")),
                plot_bgcolor="#071233", paper_bgcolor="#071233",
                font=dict(color="#FFFFFF", family="DM Sans"),
                yaxis=dict(gridcolor="#1A3A6E", title="Subscribers",
                           titlefont=dict(color="#00CFFF")),
                yaxis2=dict(overlaying="y", side="right",
                            title="MRR (₹)", gridcolor="#1A3A6E",
                            titlefont=dict(color="#00CFFF")),
                legend=dict(bgcolor="#0D2157", bordercolor="#1A3A6E"),
                height=380,
                margin=dict(l=20, r=20, t=40, b=20)
            )
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════════════════════
    # SECTION G — CALCULATOR USAGE + RECENT ACTIVITY
    # ════════════════════════════════════════════════════════════════════════════
    col_calc, col_recon = st.columns(2)

    with col_calc:
        st.markdown("""
        <p style='color:#00CFFF; font-family:IBM Plex Mono; font-size:0.75rem;
                  letter-spacing:2px; margin:8px 0 12px 0;'>
        G · CALCULATOR USAGE</p>
        """, unsafe_allow_html=True)
        if calcs:
            df_c = pd.DataFrame(calcs)
            if "tool" in df_c.columns:
                usage = df_c["tool"].value_counts().reset_index()
                usage.columns = ["Tool", "Uses"]
                st.dataframe(usage, use_container_width=True,
                             hide_index=True, height=250)
        else:
            st.info("No calculator events yet.")

    with col_recon:
        st.markdown("""
        <p style='color:#00CFFF; font-family:IBM Plex Mono; font-size:0.75rem;
                  letter-spacing:2px; margin:8px 0 12px 0;'>
        H · RECENT RECON ACTIVITY</p>
        """, unsafe_allow_html=True)
        if recons:
            df_r = pd.DataFrame(recons[:15])
            show = [c for c in
                    ["timestamp","email","wealth_found","unlocked"]
                    if c in df_r.columns]
            disp = df_r[show].copy()
            if "wealth_found" in disp.columns:
                disp["wealth_found"] = disp["wealth_found"].apply(
                    lambda x: f"₹{x:,.0f}")
            if "unlocked" in disp.columns:
                disp["unlocked"] = disp["unlocked"].apply(
                    lambda x: "✅" if x else "🔒")
            if "timestamp" in disp.columns:
                disp["timestamp"] = disp["timestamp"].apply(
                    lambda x: str(x)[:16])
            st.dataframe(disp, use_container_width=True,
                         hide_index=True, height=250)
        else:
            st.info("No recon runs yet.")

    st.divider()
    col_snap, col_note = st.columns([1, 3])
    with col_snap:
        if st.button("📸 Save Daily Snapshot", type="secondary",
                     use_container_width=True):
            snapshot_sovereign()
            st.success("Snapshot saved.")
    with col_note:
        st.caption(
            f"Snapshot saves today's subscriber count and MRR to the "
            f"growth chart. Run once per day for accurate trend data. "
            f"Last generated: {report_date}"
        )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <p style='color:#00CFFF; font-family:IBM Plex Mono; font-size:0.75rem;
              letter-spacing:2px; margin:8px 0 4px 0;'>G · GRANT FREE SUBSCRIPTION</p>
    <p style='color:#FFFFFF; font-size:0.82rem; opacity:.75; margin:0 0 16px 0;'>
    Extend a subscriber's access instead of issuing a cash refund.
    </p>
    """, unsafe_allow_html=True)
    g1, g2, g3 = st.columns([2, 1, 1])
    with g1:
        grant_email = st.text_input("Subscriber Email", placeholder="ca@theirfirm.com",
                                    key="grant_email", label_visibility="collapsed")
    with g2:
        grant_plan = st.selectbox("Grant",
            ["1 Month Free","3 Months Free","6 Months Free","1 Year Free"],
            key="grant_plan", label_visibility="collapsed")
    with g3:
        grant_reason = st.text_input("Reason", placeholder="e.g. PDF issue, goodwill",
                                     key="grant_reason", label_visibility="collapsed")
    if st.button("🎁 Grant Free Subscription", type="primary",
                 use_container_width=True, key="btn_grant"):
        if not grant_email.strip():
            st.error("Please enter a subscriber email.")
        else:
            try:
                months_map = {"1 Month Free":1,"3 Months Free":3,"6 Months Free":6,"1 Year Free":12}
                months = months_map.get(grant_plan, 1)
                existing = db("subscriptions").select("*")\
                    .eq("email", grant_email.strip().lower())\
                    .eq("status","active").execute()
                now = datetime.now()
                if existing.data and len(existing.data) > 0:
                    sub = existing.data[0]
                    try:
                        exp_dt = datetime.fromisoformat(sub.get("expires_at","").replace("Z","").split(".")[0])
                        base = exp_dt if exp_dt > now else now
                    except Exception:
                        base = now
                    new_exp = base
                    for _ in range(months):
                        new_exp = new_exp.replace(
                            month=new_exp.month % 12 + 1,
                            year=new_exp.year + (1 if new_exp.month == 12 else 0))
                    db("subscriptions").update({
                        "expires_at": new_exp.isoformat(),
                        "grant_note": f"{grant_reason} [{grant_plan}] {now.strftime('%d-%m-%Y')} by sovereign",
                    }).eq("id", sub["id"]).execute()
                    st.success(f"✅ Extended until {new_exp.strftime('%d %B %Y')}")
                else:
                    new_exp = now
                    for _ in range(months):
                        new_exp = new_exp.replace(
                            month=new_exp.month % 12 + 1,
                            year=new_exp.year + (1 if new_exp.month == 12 else 0))
                    db("subscriptions").insert({
                        "email": grant_email.strip().lower(),
                        "plan": "granted", "status": "active", "amount": 0,
                        "early_bird": False, "expires_at": new_exp.isoformat(),
                        "razorpay_payment_id": "SOVEREIGN_GRANT",
                        "grant_note": f"{grant_reason} [{grant_plan}] {now.strftime('%d-%m-%Y')} by sovereign",
                    }).execute()
                    st.success(f"✅ Granted until {new_exp.strftime('%d %B %Y')}")
            except Exception as e:
                st.error(f"Grant error: {e}")


# ============================================================
# SECTION 17: MAIN ROUTER
# ============================================================

def main():
    params = st.query_params

    if "report" in params:
        page_public_report(params["report"])
        return

    if not S.logged_in and "session" in params and "email" in params:
        _email = params["email"].strip().lower()
        _token = params["session"].strip()
        if _verify_session_token(_email, _token):
            try:
                res = db("subscriptions").select("*").eq("email", _email).eq("status","active").execute()
                if res.data and len(res.data) > 0:
                    _set_session_subscriber(_email, res.data[0])
                else:
                    row_res = db("free_users").select("*").eq("email", _email).execute()
                    if row_res.data and len(row_res.data) > 0:
                        _set_session_free(row_res.data[0])
                    else:
                        _set_session_free({"email": _email})
                st.query_params.clear()
                st.rerun()
                return
            except Exception:
                pass

    if not S.logged_in:
        page_login()
        return

    sidebar()
    page = S.page

    if   page == "dashboard"     : page_dashboard()
    elif page == "recon"         : page_recon()
    elif page == "clients"       : page_clients()
    elif page == "history"       : page_history()
    elif page == "calculators"   : page_calculators()
    elif page == "subscribe"     : page_subscribe()
    elif page == "sovereign"     : page_sovereign()
    else                         : page_dashboard()

if __name__ == "__main__":
    main()


# ============================================================
# SUPABASE SQL — paste into Supabase SQL Editor and run once
# ============================================================
#
# CREATE TABLE free_users (
#   id             uuid DEFAULT gen_random_uuid() PRIMARY KEY,
#   email          text UNIQUE NOT NULL,
#   password       text NOT NULL,
#   registered_at  timestamp DEFAULT now(),
#   trial_started  timestamp
# );
#
# CREATE TABLE subscriptions (
#   id           uuid DEFAULT gen_random_uuid() PRIMARY KEY,
#   email        text NOT NULL,
#   plan         text NOT NULL,
#   amount       decimal NOT NULL,
#   early_bird   boolean DEFAULT false,
#   status       text DEFAULT 'active',
#   started_at   timestamp DEFAULT now(),
#   renewed_at   timestamp DEFAULT now(),
#   cancelled_at timestamp
# );
#
# CREATE TABLE clients (
#   id           uuid DEFAULT gen_random_uuid() PRIMARY KEY,
#   email        text NOT NULL,
#   client_name  text NOT NULL,
#   gstin        text,
#   entity_type  text,
#   added_at     timestamp DEFAULT now()
# );
#
# CREATE TABLE recon_results (
#   id              bigint GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
#   email           text NOT NULL,
#   client_name     text,
#   period          text,
#   itc_available   decimal DEFAULT 0,
#   itc_claimed     decimal DEFAULT 0,
#   unclaimed_itc   decimal DEFAULT 0,
#   mismatch_count  int DEFAULT 0,
#   wealth_found    decimal DEFAULT 0,
#   link_token      text UNIQUE,
#   unlocked        boolean DEFAULT false,
#   timestamp       timestamp DEFAULT now()
# );
#
# CREATE TABLE calculator_events (
#   id          bigint GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
#   tool        text,
#   session_id  text,
#   timestamp   timestamp DEFAULT now()
# );
#
# CREATE TABLE sovereign_snapshots (
#   id           bigint GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
#   date         text,
#   subscribers  int DEFAULT 0,
#   free_users   int DEFAULT 0,
#   mrr          decimal DEFAULT 0,
#   timestamp    timestamp DEFAULT now()
# );
#
# CREATE TABLE password_resets (
#   id          bigint GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
#   email       text NOT NULL,
#   token       text UNIQUE NOT NULL,
#   expires_at  timestamp NOT NULL,
#   used        boolean DEFAULT false,
#   created_at  timestamp DEFAULT now()
# );
#
# -- Run once — change to your email and password
# INSERT INTO free_users (email, password)
# VALUES ('auditdesk.hq@gmail.com', 'YourSecurePassword123');
# ============================================================
