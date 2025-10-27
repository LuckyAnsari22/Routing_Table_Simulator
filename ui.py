"""ui.py

Lightweight UI helpers for the Routing Simulator app.
Provides:
- inject_theme(): injects minimal CSS + JS helpers (toast stack)
- toast(message, kind='info', duration=4000): show a transient stacked toast
- skeleton_box(width, height): render a skeleton placeholder
- progress_js(percent): update a progress bar element with id '__progress_bar'

This module injects carefully-scoped CSS so it won't accidentally make
Streamlit widgets unreadable. If a dark theme is requested we set
high-contrast light-on-dark tokens and also ensure form controls inherit
the readable colors.
"""
from __future__ import annotations
import time
import streamlit as st
import streamlit.components.v1 as components


def inject_theme(dark: bool = False) -> None:
    """Inject a CSS + JS payload that supports light and dark themes.

    Pass `dark=True` to set the dark theme on initial render. The function
    will inject CSS variables and a small JS helper to toggle the class
    on <html> so theme can be switched by re-calling this function with
    a different value or by user interaction stored in localStorage.
    """
    js_set = 'true' if dark else 'false'

    # Compact but explicit theme tokens. We use `!important` for color
    # rules so Streamlit's own styles don't override them and also set
    # form controls (input/button/textarea/select) to inherit readable
    # colors from the tokens.
    css = '''
<style>
:root{--bg:#f6f8fb;--card:#ffffff;--muted:#6b7280;--primary:#0b5fff;--text:#0f172a}
.dark{--bg:#0b1220;--card:#0f1724;--muted:#94a3b8;--primary:#4f46e5;--text:#e6eef8}
html,body,[data-testid='stAppViewContainer']{background:var(--bg) !important;color:var(--text) !important;font-family:Inter,system-ui,-apple-system,'Segoe UI',Roboto,Arial}
[data-testid='stSidebar']{background:var(--bg) !important;color:var(--text) !important}
[data-testid='stToolbar']{background:transparent !important;}
*{color:var(--text) !important}
input,textarea,select,button{color:var(--text) !important;background:var(--card) !important;border-color:rgba(255,255,255,0.06) !important}
/* Streamlit uses div-based pseudo-selects; target common roles and wrappers */
div[role='combobox'],div[role='listbox'],div[role='option'],.stSelectbox{color:var(--text) !important;background:var(--card) !important;border:1px solid rgba(255,255,255,0.04) !important}
div[role='combobox']:focus,div[role='listbox']:focus,.stSelectbox:focus{outline:2px solid var(--primary) !important;box-shadow:0 0 0 4px rgba(79,70,229,0.08) !important}
/* Extra robust selectors for Streamlit's baseweb select overlays and options */
[data-baseweb='select'] *{color:var(--text) !important;background:var(--card) !important}
[data-testid='stSidebar'] [data-baseweb='select'] *{color:var(--text) !important}
[role='option']{color:var(--text) !important;background:var(--card) !important}
[data-testid='stAppViewContainer'] [data-baseweb='menu'] *{color:var(--text) !important;background:var(--card) !important}
div[role='listbox'] > div, div[role='option']{color:var(--text) !important;background:var(--card) !important}
.stButton>button, button, input[type='button'], input[type='submit']{background:linear-gradient(180deg, rgba(255,255,255,0.02), rgba(0,0,0,0.06)) !important;border-radius:6px;padding:6px 10px}
.app-card{background:var(--card);border-radius:10px;padding:12px;box-shadow:0 6px 18px rgba(20,25,30,0.06)}
#__toast-stack{position:fixed;right:20px;top:20px;z-index:9999;display:flex;flex-direction:column;gap:10px}
.toast{min-width:220px;padding:10px 12px;border-radius:8px;color:#fff;display:flex;align-items:center;gap:8px;background:rgba(0,0,0,0.6)}
@keyframes shine{0%{background-position:200% 0}100%{background-position:-200% 0}}
</style>
<div id='__toast-stack'></div>
<script>
function __show_toast(id,html,duration){const s=document.getElementById('__toast-stack');if(!s)return;const e=document.createElement('div');e.className='toast';e.id=id;e.innerHTML=html;s.appendChild(e);setTimeout(()=>{if(e) e.remove();},duration);}
function __dismiss_toast(id){const e=document.getElementById(id);if(e) e.remove();}
function __set_theme(pref){try{if(pref||localStorage.getItem('dark_mode')==='1'){document.documentElement.classList.add('dark')}else{document.documentElement.classList.remove('dark')}}catch(e){}}
function __toggle_theme(){const isDark=document.documentElement.classList.toggle('dark');try{localStorage.setItem('dark_mode', isDark? '1':'0');}catch(e){}}
</script>
'''

    # Inject once (combined CSS + script + initial call). Using unsafe HTML is
    # required to inject the small JS helper used by `toast()`.
    st.markdown(css + f"<script>__set_theme({js_set});</script>", unsafe_allow_html=True)


def toast(message: str, kind: str = "info", duration: int = 4000) -> None:
    """Show a stacked, dismissible toast using the injected JS helper.

    The toast HTML contains a small close button that calls __dismiss_toast.
    """
    uid = f"t{int(time.time()*1000)}"
    icon_map = {
        "info": "\u2139",    # ℹ
        "success": "\u2714", # ✔
        "error": "\u2716",   # ✖
        "warn": "\u26A0",    # ⚠
    }
    icon = icon_map.get(kind, icon_map["info"]) + "&nbsp;"

    inner = (
        f"<div style='display:flex;align-items:center;gap:10px'>"
        f"<div style='font-size:16px'>{icon}</div>"
        f"<div style='flex:1'>{message}</div>"
        f"<div style=\"cursor:pointer;padding-left:8px;font-weight:700\" onclick=\"__dismiss_toast('{uid}')\">&times;</div>"
        f"</div>"
    )
    js = f"<script>__show_toast('{uid}', `{inner}`, {duration});</script>"
    components.html(js, height=0)


def skeleton_box(width: str = "100%", height: str = "120px") -> None:
    st.markdown(
        f"<div class='skeleton' style='width:{width};height:{height};border-radius:8px;margin-bottom:12px;background:linear-gradient(90deg,#f0f2f5 25%, #e6e9ef 37%, #f0f2f5 63%);background-size:400% 100%;animation:shine 1.4s linear infinite'></div>",
        unsafe_allow_html=True,
    )


def progress_js(percent: int) -> None:
    """Update an inline progress bar element with id '__progress_bar' (if present)."""
    js = f"<script>const el=document.getElementById('__progress_bar');if(el) el.style.width='{percent}%';</script>"
    components.html(js, height=0)
