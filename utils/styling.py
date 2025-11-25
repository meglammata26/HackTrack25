# utils/styling.py
import streamlit as st

def set_page_config():
    st.set_page_config(
        page_title="Toyota Gazoo Racing — Barber Telemetry ML Lab",
        layout="wide",
    )

def inject_base_css():
    st.markdown(
        """
<style>
body {
    background-color: #000000 !important;
}
section.main {
    background-color: #050505 !important;
}
.block-container {
    padding-top: 1.3rem !important;
}
h1, h2, h3, h4 {
    color: #f44336 !important;
    font-weight: 800 !important;
}
.sidebar .sidebar-content {
    background: linear-gradient(180deg, #171717 0%, #050505 100%) !important;
}
div.stButton > button {
    background: linear-gradient(90deg, #f44336, #ff9100);
    color: #ffffff;
    font-weight: 700;
    border-radius: 999px;
    border: none;
    padding: 0.6rem 1.4rem;
    box-shadow: 0 0 12px rgba(244,67,54,0.6);
    transition: all 0.18s ease-out;
}
div.stButton > button:hover {
    transform: translateY(-1px) scale(1.02);
    box-shadow: 0 0 18px rgba(255,145,0,0.9);
}
.stTabs [data-baseweb="tab"] {
    color: #cccccc !important;
    background-color: #141414 !important;
    border-radius: 999px;
    padding: 0.4rem 1.1rem;
    margin-right: 0.45rem;
    font-weight: 500;
    border: 1px solid #333333;
}
.stTabs [data-baseweb="tab"][aria-selected="true"] {
    background: linear-gradient(90deg, #f44336, #ff9100) !important;
    color: #ffffff !important;
    border-color: #f44336;
}
.tgr-banner {
    width: 100%;
    padding: 1.1rem 1.5rem;
    border-radius: 16px;
    background-image:
        linear-gradient(120deg, rgba(244,67,54,0.4), rgba(255,145,0,0.4)),
        repeating-linear-gradient(135deg, #121212 0, #121212 4px, #050505 4px, #050505 8px);
    box-shadow: 0 0 24px rgba(0,0,0,0.9);
    display: flex;
    align-items: center;
    justify-content: space-between;
    color: #ffffff;
    position: relative;
    overflow: hidden;
}
.tgr-banner::after {
    content: "";
    position: absolute;
    top: 0;
    left: -40%;
    width: 40%;
    height: 100%;
    background: linear-gradient(120deg, rgba(255,255,255,0.25), transparent);
    transform: skewX(-20deg);
    animation: bannerSweep 6s infinite;
}
@keyframes bannerSweep {
    0%   { left: -40%; opacity: 0; }
    20%  { left: 110%; opacity: 1; }
    100% { left: 110%; opacity: 0; }
}
.grid-lights {
    display: flex;
    gap: 0.45rem;
    margin-top: 0.5rem;
}
.grid-light {
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background: #220000;
    box-shadow: 0 0 4px #000;
}
.grid-light:nth-child(1) { animation: lightSeq 3s infinite 0s; }
.grid-light:nth-child(2) { animation: lightSeq 3s infinite 0.25s; }
.grid-light:nth-child(3) { animation: lightSeq 3s infinite 0.5s; }
.grid-light:nth-child(4) { animation: lightSeq 3s infinite 0.75s; }
.grid-light:nth-child(5) { animation: lightSeq 3s infinite 1.0s; }
@keyframes lightSeq {
    0%   { background:#220000; box-shadow:0 0 4px #000; }
    30%  { background:#f44336; box-shadow:0 0 10px #f44336; }
    70%  { background:#f44336; box-shadow:0 0 12px #f44336; }
    100% { background:#111111; box-shadow:0 0 2px #000; }
}
.section-divider {
    height: 2px;
    background: linear-gradient(90deg, transparent, #f44336, #ff9100, transparent);
    box-shadow: 0 0 10px rgba(255,145,0,0.7);
    margin: 0.8rem 0 1.0rem 0;
}
.track-card {
    background: #050505;
    border-radius: 18px;
    padding: 0.8rem 1rem;
    border: 1px solid #373737;
    box-shadow: 0 0 16px rgba(0,0,0,0.8);
}
.track-anim {
    width: 100%;
    max-width: 340px;
    margin: 0.4rem auto 0.3rem auto;
}
.track-line {
    stroke: #00e5ff;
    stroke-width: 4;
    fill: none;
    stroke-linecap: round;
    filter: drop-shadow(0 0 8px rgba(0,229,255,0.9));
    stroke-dasharray: 1000;
    stroke-dashoffset: 1000;
    animation: trackDraw 4.3s infinite ease-in-out;
}
@keyframes trackDraw {
    0%   { stroke-dashoffset: 1000; opacity: 0.0; }
    20%  { opacity: 1.0; }
    65%  { stroke-dashoffset: 0;   opacity: 1.0; }
    100% { stroke-dashoffset: 0;   opacity: 0.0; }
}
</style>
        """,
        unsafe_allow_html=True,
    )

def render_banner():
    st.markdown(
        """
<div class="tgr-banner">
  <div>
    <div style="font-size: 1.0rem; text-transform: uppercase; letter-spacing: 0.14em;">
      Toyota Gazoo Racing
    </div>
    <div style="font-size: 1.6rem; font-weight: 800; margin-top: 0.2rem;">
      Barber Telemetry Machine Learning Lab
    </div>
    <div style="font-size: 0.85rem; opacity: 0.9; margin-top: 0.3rem;">
      Live racing telemetry. Predictive models. Driver style analytics.
    </div>
    <div class="grid-lights">
      <div class="grid-light"></div>
      <div class="grid-light"></div>
      <div class="grid-light"></div>
      <div class="grid-light"></div>
      <div class="grid-light"></div>
    </div>
  </div>
</div>
<div class="section-divider"></div>
        """,
        unsafe_allow_html=True,
    )

def render_track_card():
    st.markdown(
        """
<div class="track-card">
  <div style="font-size:0.85rem; text-transform:uppercase; letter-spacing:0.12em; color:#bbbbbb;">
    Virtual Barber track outline
  </div>
  <svg viewBox="0 0 400 200" class="track-anim">
    <path
      class="track-line"
      d="M40 150 
         Q100 50 200 70 
         T360 60 
         Q330 120 260 150 
         T120 160 
         Q70 150 40 150 Z"
    />
  </svg>
  <div style="font-size:0.8rem; color:#aaaaaa; text-align:center;">
    Approximate flow of a Barber GP lap, animated to suggest racing line evolution.
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )
