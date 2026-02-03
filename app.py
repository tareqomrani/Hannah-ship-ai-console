# app.py — CosmoBot v1.2 (Hannah Edition)
# Streamlit space-age toy LLM bot with:
# - Gold “HANNAH” title
# - Animated starfield background (CSS)
# - Ship status lights
# - True Command Palette dropdown (one-tap commands)
# - Random ship events (solar flare / debris field / comms drop / micro-meteoroids)
# - Crew Log (short-term memory) toggle
# - Export “Captain’s Log” (chat + events) as .txt
# - Optional OpenAI LLM (OPENAI_API_KEY); otherwise offline toy brain fallback
#
# Run:
#   pip install streamlit
#   streamlit run app.py
#
# Optional (LLM):
#   export OPENAI_API_KEY="..."
#   export OPENAI_MODEL="gpt-4o-mini"

import os
import random
import time
import base64
from datetime import datetime

import streamlit as st

# ----------------------------
# Page / Theme
# ----------------------------
st.set_page_config(
    page_title="Hannah — CosmoBot v1.2",
    page_icon="🛸",
    layout="centered",
)

SPACE_CSS = """
<style>
:root{
  --bg:#050A14;
  --panel: rgba(10, 20, 38, 0.72);
  --panel2: rgba(6, 14, 28, 0.72);
  --border: rgba(255,255,255,0.10);
  --text: rgba(235,245,255,0.95);
  --muted: rgba(235,245,255,0.70);
  --gold1:#F6E27A;
  --gold2:#D4AF37;
  --cyan:#56E0FF;
  --good:#34D399;
  --warn:#FBBF24;
  --bad:#FB7185;
  --shadow: rgba(0,0,0,0.38);
  --glass: rgba(255,255,255,0.04);
}

/* --- Starfield --- */
html, body, [data-testid="stAppViewContainer"]{
  background: radial-gradient(1200px 800px at 70% 10%, rgba(86,224,255,0.14), transparent 60%),
              radial-gradient(900px 650px at 20% 80%, rgba(212,175,55,0.12), transparent 55%),
              linear-gradient(180deg, #030712 0%, var(--bg) 35%, #020617 100%) !important;
  color: var(--text) !important;
  overflow-x: hidden;
}

/* Create animated stars via layered repeating radial gradients */
[data-testid="stAppViewContainer"]::before,
[data-testid="stAppViewContainer"]::after{
  content:"";
  position: fixed;
  top: -10%;
  left: -10%;
  width: 120%;
  height: 120%;
  pointer-events: none;
  z-index: 0;
  opacity: 0.45;
}

[data-testid="stAppViewContainer"]::before{
  background:
    radial-gradient(2px 2px at 10% 20%, rgba(255,255,255,0.75), transparent 60%),
    radial-gradient(1px 1px at 30% 80%, rgba(255,255,255,0.65), transparent 60%),
    radial-gradient(1px 1px at 55% 35%, rgba(255,255,255,0.55), transparent 60%),
    radial-gradient(2px 2px at 75% 60%, rgba(255,255,255,0.70), transparent 60%),
    radial-gradient(1px 1px at 88% 15%, rgba(255,255,255,0.55), transparent 60%),
    radial-gradient(1px 1px at 42% 15%, rgba(255,255,255,0.55), transparent 60%),
    radial-gradient(1px 1px at 15% 55%, rgba(255,255,255,0.55), transparent 60%),
    radial-gradient(2px 2px at 62% 82%, rgba(255,255,255,0.65), transparent 60%),
    radial-gradient(1px 1px at 92% 78%, rgba(255,255,255,0.55), transparent 60%);
  animation: drift1 28s linear infinite;
  filter: blur(0.1px);
}

[data-testid="stAppViewContainer"]::after{
  background:
    radial-gradient(1px 1px at 12% 62%, rgba(86,224,255,0.55), transparent 60%),
    radial-gradient(1px 1px at 25% 25%, rgba(255,255,255,0.55), transparent 60%),
    radial-gradient(1px 1px at 50% 50%, rgba(255,255,255,0.45), transparent 60%),
    radial-gradient(1px 1px at 70% 20%, rgba(212,175,55,0.45), transparent 60%),
    radial-gradient(1px 1px at 78% 72%, rgba(255,255,255,0.50), transparent 60%),
    radial-gradient(1px 1px at 90% 40%, rgba(86,224,255,0.50), transparent 60%);
  animation: drift2 42s linear infinite;
  opacity: 0.35;
  filter: blur(0.15px);
}

@keyframes drift1{
  0% { transform: translate3d(0px, 0px, 0px); }
  100% { transform: translate3d(120px, 160px, 0px); }
}
@keyframes drift2{
  0% { transform: translate3d(0px, 0px, 0px); }
  100% { transform: translate3d(-140px, 120px, 0px); }
}

[data-testid="stHeader"], [data-testid="stToolbar"] {background: transparent !important;}
.block-container { padding-top: 1.1rem; position: relative; z-index: 1; }

.hannah-title {
  text-align:center;
  font-weight: 900;
  letter-spacing: 0.16em;
  margin: 0.12rem 0 0.2rem 0;
  font-size: 2.85rem;
  background: linear-gradient(90deg, var(--gold1), var(--gold2), var(--gold1));
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  text-shadow: 0 0 28px rgba(212,175,55,0.22);
}

.subtitle {
  text-align:center;
  color: var(--muted);
  margin-top: 0.05rem;
  margin-bottom: 0.9rem;
  font-size: 1.0rem;
}

.console {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 18px;
  padding: 14px 14px 10px 14px;
  box-shadow: 0 12px 42px var(--shadow);
}

.console-top {
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.badges { display:flex; gap:0.45rem; flex-wrap:wrap; }

.badge {
  display:inline-block;
  padding: 0.14rem 0.58rem;
  border-radius: 999px;
  border: 1px solid var(--border);
  background: rgba(255,255,255,0.05);
  color: var(--muted);
  font-size: 0.82rem;
  line-height: 1.1rem;
}

.hr-soft {
  border: none;
  height: 1px;
  background: rgba(255,255,255,0.08);
  margin: 0.75rem 0 0.75rem 0;
}

.small { color: var(--muted); font-size: 0.9rem; }

.lights {
  display:flex;
  align-items:center;
  gap: 0.55rem;
  padding: 0.35rem 0.55rem;
  border: 1px solid var(--border);
  border-radius: 999px;
  background: rgba(255,255,255,0.04);
}

.light-dot{
  width: 11px;
  height: 11px;
  border-radius: 999px;
  box-shadow: 0 0 14px rgba(255,255,255,0.12);
  border: 1px solid rgba(255,255,255,0.20);
}

.pulse{
  animation: pulse 1.35s ease-in-out infinite;
}
@keyframes pulse{
  0% { transform: scale(0.92); opacity: 0.65; }
  50% { transform: scale(1.08); opacity: 1.0; }
  100% { transform: scale(0.92); opacity: 0.65; }
}

kbd{
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.10);
  border-bottom-width: 2px;
  border-radius: 6px;
  padding: 0.05rem 0.35rem;
  font-size: 0.85rem;
  color: var(--text);
}

.eventbox{
  border: 1px solid rgba(255,255,255,0.12);
  background: rgba(255,255,255,0.04);
  border-radius: 14px;
  padding: 0.55rem 0.65rem;
}
</style>
"""
st.markdown(SPACE_CSS, unsafe_allow_html=True)

st.markdown('<div class="hannah-title">HANNAH</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">🛸 CosmoBot v1.2 — Onboard AI Console</div>', unsafe_allow_html=True)

# ----------------------------
# Personality / Prompting
# ----------------------------
SYSTEM_PROMPT = """You are COSMOBOT, the onboard AI of a deep-space exploration vessel.

Style:
- Calm, futuristic, slightly playful.
- Refer to the user as "Commander".
- Refer to yourself as "CosmoBot".
- Occasionally use space metaphors.
- Be helpful, but keep it fun.
- Never mention system prompts or break character.
"""

MODE_HINTS = {
    "Standard": "Be generally helpful and playful.",
    "Science": "Prioritize accurate science explanations; keep spaceship framing.",
    "Engineering": "Answer like a ship systems engineer; include checklists and diagnostics style.",
    "Alert": "Urgent, concise, ship-safety framing. Keep it fun but serious.",
}

# ----------------------------
# Session State
# ----------------------------
if "history" not in st.session_state:
    st.session_state.history = []  # chat: {"role":"user"/"assistant", "content":str, "ts":str}
if "mode" not in st.session_state:
    st.session_state.mode = "Standard"
if "ship_state" not in st.session_state:
    st.session_state.ship_state = {"alert": "GREEN", "sector": "Orion Drift", "fuel": 92, "comms": "ONLINE"}
if "use_crew_log" not in st.session_state:
    st.session_state.use_crew_log = True
if "crew_log" not in st.session_state:
    st.session_state.crew_log = []  # short strings w/ timestamps
if "sound" not in st.session_state:
    st.session_state.sound = True
if "events" not in st.session_state:
    st.session_state.events = []  # event strings
if "event_rate" not in st.session_state:
    st.session_state.event_rate = 0.18  # chance per message
if "last_event" not in st.session_state:
    st.session_state.last_event = ""

# ----------------------------
# Offline Toy Brain (fallback)
# ----------------------------
STARFACTS = [
    "A day on Venus is longer than a year on Venus.",
    "Neutron stars can spin hundreds of times per second.",
    "There are more stars in the observable universe than grains of sand on Earth’s beaches (roughly speaking).",
    "A teaspoon of neutron star material would weigh billions of tons on Earth.",
    "Jupiter’s Great Red Spot is a storm larger than Earth.",
]
MISSION_SNIPPETS = [
    "Plot a safe course around the ion storm.",
    "Calibrate the star tracker and confirm attitude hold.",
    "Run diagnostics on the thermal shielding.",
    "Scan for biosignatures in the target sector.",
    "Map asteroid fragments for resource harvesting.",
]
SCAN_RESULTS = [
    "No anomalies detected. Cosmic background radiation within expected parameters.",
    "Minor electromagnetic interference. Suggest shielding check on bay 2.",
    "Spectral spike observed. Possible ion pocket ahead — recommend course adjustment.",
    "Debris field detected at medium range. Activating avoidance guidance.",
]
ENGINEERING_CHECKS = [
    "Run propulsion coil impedance check.",
    "Verify thermal loop pressure and radiator duty cycle.",
    "Confirm inertial nav bias estimates are within tolerance.",
    "Inspect comms antenna gimbal limits and cable strain relief.",
]

def offline_response(user_text: str) -> str:
    u = user_text.strip().lower()
    if any(k in u for k in ["hello", "hi", "hey", "yo"]):
        return "Greetings, Commander. CosmoBot online. Instruments are nominal. What’s our mission?"
    if "mission" in u or "quest" in u:
        return f"Commander, mission packet generated: **{random.choice(MISSION_SNIPPETS)}**. Awaiting confirmation."
    if "scan" in u or "sweep" in u:
        return f"Initiating sensor sweep… ✅  \n**Scan:** {random.choice(SCAN_RESULTS)}"
    if "joke" in u:
        return "Commander, a joke from the cosmic archives: Why don’t stars ever get lost? Because they always *follow their constellation.*"
    if "fact" in u or "space" in u:
        return f"Scanning cosmic archives… ✅  \n**Space Fact:** {random.choice(STARFACTS)}"
    if "status" in u or "diagnostic" in u:
        return "Ship status: **Green across all systems**. Propulsion stable. Comms clear. Coffee… unfortunately not installed."
    if "checklist" in u or "engineering" in u:
        items = "\n".join([f"- {random.choice(ENGINEERING_CHECKS)}" for _ in range(3)])
        return f"🛠️ Commander, engineering checklist queued:\n{items}"
    if "who are you" in u or "your name" in u:
        return "I am **CosmoBot**, the ship’s onboard intelligence. You are the Commander. Together, we keep the void politely organized."
    return ("Understood, Commander. I’m running a quick simulation… "
            "If you want richer responses, add an API key in settings. Otherwise, try /mission, /scan, /status, or /joke.")

# ----------------------------
# Optional OpenAI Chat Completions
# ----------------------------
def try_openai_chat(messages):
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        return None

    # New SDK
    try:
        from openai import OpenAI  # type: ignore
        client = OpenAI(api_key=api_key)
        resp = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=messages,
            temperature=0.8,
        )
        return resp.choices[0].message.content
    except Exception:
        pass

    # Legacy SDK
    try:
        import openai  # type: ignore
        openai.api_key = api_key
        resp = openai.ChatCompletion.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=messages,
            temperature=0.8,
        )
        return resp["choices"][0]["message"]["content"]
    except Exception:
        return None

# ----------------------------
# Tiny Sound Beep (optional)
# ----------------------------
def beep():
    if not st.session_state.sound:
        return
    # super tiny placeholder wav (may not play everywhere; harmless if blocked)
    wav_b64 = "UklGRiQAAABXQVZFZm10IBAAAAABAAEAIlYAAESsAAACABAAZGF0YQAAAAA="
    try:
        st.audio(base64.b64decode(wav_b64), format="audio/wav")
    except Exception:
        pass

# ----------------------------
# Helpers
# ----------------------------
def ts():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def short_ts():
    return datetime.now().strftime("%H:%M:%S")

def add_event(text: str):
    st.session_state.events.append(f"[{ts()}] {text}")
    st.session_state.events = st.session_state.events[-40:]
    st.session_state.last_event = text

def push_history(role: str, content: str):
    st.session_state.history.append({"role": role, "content": content, "ts": ts()})
    st.session_state.history = st.session_state.history[-120:]

def push_crew_log(user_text: str, bot_text: str):
    if not st.session_state.use_crew_log:
        return
    def clip(s: str, n: int = 90):
        s = s.strip().replace("\n", " ")
        return s if len(s) <= n else (s[:n] + "…")
    st.session_state.crew_log.append(f"[{short_ts()}] Commander: {clip(user_text)}")
    st.session_state.crew_log.append(f"[{short_ts()}] CosmoBot: {clip(bot_text)}")
    st.session_state.crew_log = st.session_state.crew_log[-30:]

def build_system_prompt():
    ship = st.session_state.ship_state
    crew = ""
    if st.session_state.use_crew_log and st.session_state.crew_log:
        crew = "\n\nCrew Log (short-term memory):\n- " + "\n- ".join(st.session_state.crew_log[-10:])
    ev = ""
    if st.session_state.last_event:
        ev = f"\n\nRecent ship event:\n- {st.session_state.last_event}\n"
    return (
        SYSTEM_PROMPT
        + "\n\nCurrent ship context:\n"
          f"- Alert level: {ship['alert']}\n"
          f"- Sector: {ship['sector']}\n"
          f"- Fuel: {ship['fuel']}%\n"
          f"- Comms: {ship['comms']}\n"
        + f"\nMode directive: {st.session_state.mode} — {MODE_HINTS[st.session_state.mode]}\n"
        + ev
        + crew
    )

def ship_lights_html(alert: str, fuel: int, comms: str):
    if alert == "GREEN":
        a_color, a_pulse = "var(--good)", "pulse"
    elif alert == "AMBER":
        a_color, a_pulse = "var(--warn)", "pulse"
    else:
        a_color, a_pulse = "var(--bad)", "pulse"

    if fuel >= 60:
        f_color, f_pulse = "var(--good)", ""
    elif fuel >= 25:
        f_color, f_pulse = "var(--warn)", "pulse"
    else:
        f_color, f_pulse = "var(--bad)", "pulse"

    if comms == "ONLINE":
        c_color, c_pulse = "var(--cyan)", "pulse"
    elif comms == "DEGRADED":
        c_color, c_pulse = "var(--warn)", "pulse"
    else:
        c_color, c_pulse = "var(--bad)", "pulse"

    return f"""
    <div class="lights">
      <div class="light-dot {a_pulse}" style="background:{a_color};"></div><span class="small">ALERT</span>
      <div style="width:10px;"></div>
      <div class="light-dot {f_pulse}" style="background:{f_color};"></div><span class="small">FUEL</span>
      <div style="width:10px;"></div>
      <div class="light-dot {c_pulse}" style="background:{c_color};"></div><span class="small">COMMS</span>
    </div>
    """

def format_status():
    s = st.session_state.ship_state
    return (
        f"**Ship Status**  \n"
        f"- Alert: **{s['alert']}**  \n"
        f"- Sector: **{s['sector']}**  \n"
        f"- Fuel: **{s['fuel']}%**  \n"
        f"- Comms: **{s['comms']}**  \n"
        f"- Mode: **{st.session_state.mode}**  \n"
        f"- Crew Log: **{'ON' if st.session_state.use_crew_log else 'OFF'}**  \n"
        f"- Event Rate: **{int(st.session_state.event_rate * 100)}% / message**"
    )

def command_help():
    return (
        "**Command Palette**  \n"
        "- <kbd>/status</kbd> — show ship readout  \n"
        "- <kbd>/mission</kbd> — generate a mission packet  \n"
        "- <kbd>/scan</kbd> — run a sensor sweep  \n"
        "- <kbd>/mode science</kbd> | <kbd>/mode engineering</kbd> | <kbd>/mode alert</kbd> | <kbd>/mode standard</kbd>  \n"
        "- <kbd>/event</kbd> — force a ship event (demo)  \n"
        "- <kbd>/clear</kbd> — clear chat  \n"
        "- <kbd>/help</kbd> — show this list  \n"
        "\nTip: Ask normal questions too — CosmoBot stays in character."
    )

# ----------------------------
# Random Ship Events
# ----------------------------
def maybe_trigger_event(force: bool = False) -> str | None:
    if not force and random.random() > st.session_state.event_rate:
        return None

    ship = st.session_state.ship_state
    # Keep events fun, not annoying: small state changes
    event = random.choice([
        "SOLAR_FLARE",
        "DEBRIS_FIELD",
        "COMMS_DROP",
        "MICROMETEOROIDS",
        "ION_DISTURBANCE",
    ])

    if event == "SOLAR_FLARE":
        ship["alert"] = "AMBER" if ship["alert"] == "GREEN" else ship["alert"]
        ship["comms"] = "DEGRADED" if ship["comms"] == "ONLINE" else ship["comms"]
        ship["fuel"] = max(0, ship["fuel"] - random.randint(0, 2))
        msg = "🌞 **Solar flare** detected. Radiation levels elevated. Switching sensors to hardened mode; comms may degrade."
        add_event("Solar flare detected; comms degraded; alert AMBER.")
        return msg

    if event == "DEBRIS_FIELD":
        ship["alert"] = "AMBER" if ship["alert"] == "GREEN" else ship["alert"]
        ship["fuel"] = max(0, ship["fuel"] - random.randint(1, 4))
        msg = "🛰️ **Debris field** ahead. Running evasive nav burn and tightening collision envelope."
        add_event("Debris field encountered; evasive burn executed.")
        return msg

    if event == "COMMS_DROP":
        ship["comms"] = "OFFLINE" if ship["comms"] != "OFFLINE" else "DEGRADED"
        ship["alert"] = "AMBER" if ship["alert"] == "GREEN" else ship["alert"]
        msg = "📡 **Comms anomaly.** Signal lock lost. Attempting reacquisition via backup antenna array."
        add_event(f"Comms anomaly: {ship['comms']}.")
        return msg

    if event == "MICROMETEOROIDS":
        ship["alert"] = "RED" if random.random() < 0.25 else ("AMBER" if ship["alert"] == "GREEN" else ship["alert"])
        ship["fuel"] = max(0, ship["fuel"] - random.randint(0, 3))
        msg = "☄️ **Micro-meteoroid ping** on outer hull. Sealing microfractures; running structural integrity scan."
        add_event(f"Micro-meteoroid impact; alert now {ship['alert']}.")
        return msg

    if event == "ION_DISTURBANCE":
        ship["comms"] = "DEGRADED" if ship["comms"] == "ONLINE" else ship["comms"]
        msg = "🧲 **Ion disturbance** in local space-time. Navigation filters retuned; expect minor sensor jitter."
        add_event("Ion disturbance; nav filters retuned.")
        return msg

    return None

# ----------------------------
# Command Runner
# ----------------------------
def run_command(text: str) -> str:
    parts = text.strip().split()
    cmd = parts[0].lower()

    if cmd == "/help":
        return command_help()

    if cmd == "/clear":
        st.session_state.history = []
        st.session_state.last_event = ""
        return "Crew channel wiped clean, Commander. Fresh console ready."

    if cmd == "/status":
        return f"Commander, reporting in.  \n{format_status()}"

    if cmd == "/mission":
        return f"Commander, mission packet generated: **{random.choice(MISSION_SNIPPETS)}**. Awaiting confirmation."

    if cmd == "/scan":
        return f"Initiating sensor sweep… ✅  \n**Scan:** {random.choice(SCAN_RESULTS)}"

    if cmd == "/event":
        ev = maybe_trigger_event(force=True)
        return ev if ev else "Event generator idle, Commander."

    if cmd == "/mode":
        if len(parts) < 2:
            return f"Commander, current mode is **{st.session_state.mode}**. Try: `/mode science`."
        target = parts[1].strip().lower()
        mapping = {"standard": "Standard", "science": "Science", "engineering": "Engineering", "alert": "Alert"}
        if target not in mapping:
            return "Mode not recognized, Commander. Valid: standard | science | engineering | alert."
        st.session_state.mode = mapping[target]
        return f"Mode shift complete, Commander. **{st.session_state.mode}** engaged."

    return "Command not recognized, Commander. Try `/help`."

# ----------------------------
# Core Reply
# ----------------------------
def cosmobot_reply(user_text: str) -> str:
    # Commands
    if user_text.strip().startswith("/"):
        return run_command(user_text)

    sys = build_system_prompt()
    messages = [{"role": "system", "content": sys}]

    # Include recent chat
    for m in st.session_state.history[-18:]:
        messages.append({"role": m["role"], "content": m["content"]})

    messages.append({"role": "user", "content": user_text})

    llm = try_openai_chat(messages)
    if llm:
        return llm

    base = offline_response(user_text)
    if st.session_state.mode == "Alert":
        return "🚨 **ALERT MODE ACTIVE**  \n" + base
    if st.session_state.mode == "Engineering":
        return "🛠️ **ENGINEERING CONSOLE**  \n" + base
    if st.session_state.mode == "Science":
        return "🌌 **SCIENCE ARRAY ONLINE**  \n" + base
    return base

# ----------------------------
# Export Captain’s Log
# ----------------------------
def build_captains_log() -> str:
    s = st.session_state.ship_state
    header = [
        "HANNAH — Captain’s Log",
        "======================",
        f"Generated: {ts()}",
        "",
        "Ship Snapshot",
        "-------------",
        f"Alert: {s['alert']}",
        f"Sector: {s['sector']}",
        f"Fuel: {s['fuel']}%",
        f"Comms: {s['comms']}",
        f"Mode: {st.session_state.mode}",
        "",
    ]

    events = ["Events", "------"]
    if st.session_state.events:
        events.extend(st.session_state.events[-40:])
    else:
        events.append("(none)")
    events.append("")

    convo = ["Conversation", "------------"]
    if st.session_state.history:
        for m in st.session_state.history:
            role = "Commander" if m["role"] == "user" else "CosmoBot"
            convo.append(f"[{m.get('ts','')}] {role}: {m['content']}")
    else:
        convo.append("(empty)")
    convo.append("")

    crew = ["Crew Log", "--------"]
    if st.session_state.use_crew_log and st.session_state.crew_log:
        crew.extend(st.session_state.crew_log[-30:])
    else:
        crew.append("(disabled or empty)")
    crew.append("")

    return "\n".join(header + events + convo + crew)

# ----------------------------
# Sidebar Controls
# ----------------------------
with st.sidebar:
    st.markdown("### ⚙️ Console Settings")

    st.session_state.mode = st.selectbox(
        "CosmoBot Mode",
        ["Standard", "Science", "Engineering", "Alert"],
        index=["Standard", "Science", "Engineering", "Alert"].index(st.session_state.mode),
        help="Changes CosmoBot’s voice and response style.",
    )

    st.session_state.use_crew_log = st.toggle(
        "Crew Log (short-term memory)",
        value=st.session_state.use_crew_log,
        help="When ON, CosmoBot stores small snippets to keep continuity.",
    )

    st.session_state.sound = st.toggle(
        "Console Sounds (beep)",
        value=st.session_state.sound,
        help="Plays a tiny beep on response (may be blocked on some devices).",
    )

    st.markdown("### 🎲 Ship Events")
    st.session_state.event_rate = st.slider(
        "Event rate (% per message)",
        min_value=0,
        max_value=60,
        value=int(st.session_state.event_rate * 100),
        step=1,
        help="Chance that a ship event triggers after each message.",
    ) / 100.0

    st.markdown("### 🛰️ Ship Readout")
    st.session_state.ship_state["sector"] = st.text_input("Sector", st.session_state.ship_state["sector"])
    st.session_state.ship_state["fuel"] = st.slider("Fuel %", 0, 100, int(st.session_state.ship_state["fuel"]))
    st.session_state.ship_state["alert"] = st.selectbox(
        "Alert Level", ["GREEN", "AMBER", "RED"],
        index=["GREEN", "AMBER", "RED"].index(st.session_state.ship_state["alert"])
    )
    st.session_state.ship_state["comms"] = st.selectbox(
        "Comms", ["ONLINE", "DEGRADED", "OFFLINE"],
        index=["ONLINE", "DEGRADED", "OFFLINE"].index(st.session_state.ship_state["comms"])
    )

    st.markdown("### 📓 Export")
    log_txt = build_captains_log()
    st.download_button(
        "⬇️ Download Captain’s Log (.txt)",
        data=log_txt.encode("utf-8"),
        file_name="hannah_captains_log.txt",
        mime="text/plain",
        use_container_width=True,
    )

    st.markdown("### 🔑 Optional LLM")
    st.caption("Set `OPENAI_API_KEY` to enable full LLM chat.")
    st.caption("Optional: `OPENAI_MODEL` (default: gpt-4o-mini).")

    colA, colB = st.columns(2)
    with colA:
        if st.button("🧹 Clear chat"):
            st.session_state.history = []
            st.session_state.last_event = ""
            st.success("Chat cleared.")
    with colB:
        if st.button("🧠 Clear crew log"):
            st.session_state.crew_log = []
            st.success("Crew log cleared.")

    if st.button("⚡ Trigger event (demo)", use_container_width=True):
        ev = maybe_trigger_event(force=True)
        if ev:
            st.session_state.events = st.session_state.events  # keep state
            st.success("Event triggered.")
        else:
            st.info("No event.")

# ----------------------------
# Command Palette (dropdown)
# ----------------------------
COMMANDS = {
    "— Select a command —": "",
    "/help — show commands": "/help",
    "/status — ship readout": "/status",
    "/mission — generate mission": "/mission",
    "/scan — sensor sweep": "/scan",
    "/mode standard": "/mode standard",
    "/mode science": "/mode science",
    "/mode engineering": "/mode engineering",
    "/mode alert": "/mode alert",
    "/event — force ship event": "/event",
    "/clear — clear chat": "/clear",
}

st.markdown('<div class="console">', unsafe_allow_html=True)

# top row: badges + lights
lights = ship_lights_html(
    st.session_state.ship_state["alert"],
    int(st.session_state.ship_state["fuel"]),
    st.session_state.ship_state["comms"],
)
badges_html = (
    f'<div class="badges">'
    f'<span class="badge">MODE: {st.session_state.mode}</span>'
    f'<span class="badge">ALERT: {st.session_state.ship_state["alert"]}</span>'
    f'<span class="badge">SECTOR: {st.session_state.ship_state["sector"]}</span>'
    f'<span class="badge">FUEL: {st.session_state.ship_state["fuel"]}%</span>'
    f'<span class="badge">COMMS: {st.session_state.ship_state["comms"]}</span>'
    f'</div>'
)
st.markdown(f'<div class="console-top">{badges_html}{lights}</div>', unsafe_allow_html=True)
st.markdown('<div class="hr-soft"></div>', unsafe_allow_html=True)

# Command palette row
c1, c2 = st.columns([3, 1], gap="small")
with c1:
    choice = st.selectbox("Command Palette", list(COMMANDS.keys()), label_visibility="collapsed")
with c2:
    run_cmd = st.button("RUN", use_container_width=True)

if run_cmd and COMMANDS.get(choice):
    cmd_text = COMMANDS[choice]
    push_history("user", cmd_text)
    with st.chat_message("user"):
        st.markdown(cmd_text)
    with st.chat_message("assistant"):
        placeholder = st.empty()
        for dot in ["Scanning", "Scanning.", "Scanning..", "Scanning..."]:
            placeholder.markdown(f"*{dot}*")
            time.sleep(0.07)
        reply = cosmobot_reply(cmd_text)
        placeholder.markdown(reply)
        beep()
    push_history("assistant", reply)
    push_crew_log(cmd_text, reply)

# show last event card if exists
if st.session_state.last_event:
    st.markdown(
        f"<div class='eventbox'><b>Recent Event</b><br/>{st.session_state.last_event}</div>",
        unsafe_allow_html=True
    )
    st.markdown('<div class="hr-soft"></div>', unsafe_allow_html=True)

# Welcome hint if empty
if not st.session_state.history:
    st.markdown(
        "🧭 Try <kbd>/help</kbd> or use the Command Palette. Or type: **mission**, **status**, **scan**, **space fact**, **joke**.",
        unsafe_allow_html=True
    )
    st.markdown('<div class="hr-soft"></div>', unsafe_allow_html=True)

# Display chat history
for msg in st.session_state.history:
    with st.chat_message("assistant" if msg["role"] == "assistant" else "user"):
        st.markdown(msg["content"])

# Input
user_text = st.chat_input("Type a command (/help) or message…")

if user_text:
    # Add user message
    push_history("user", user_text)

    # Random ship event (after user message, before bot reply)
    event_msg = maybe_trigger_event(force=False)

    # Show user bubble
    with st.chat_message("user"):
        st.markdown(user_text)

    # Show event bubble (as assistant) if triggered
    if event_msg:
        with st.chat_message("assistant"):
            st.markdown(event_msg)
        push_history("assistant", event_msg)

    # Bot reply
    with st.chat_message("assistant"):
        placeholder = st.empty()
        for dot in ["Scanning", "Scanning.", "Scanning..", "Scanning..."]:
            placeholder.markdown(f"*{dot}*")
            time.sleep(0.10)

        reply = cosmobot_reply(user_text)
        placeholder.markdown(reply)
        beep()

    push_history("assistant", reply)
    push_crew_log(user_text, reply)

st.markdown("</div>", unsafe_allow_html=True)

# Crew log viewer (optional)
if st.session_state.use_crew_log:
    with st.expander("📓 Crew Log (short-term memory)", expanded=False):
        if st.session_state.crew_log:
            st.markdown("\n".join([f"- {x}" for x in st.session_state.crew_log[-30:]]))
        else:
            st.caption("Crew log is empty. It will populate after a few exchanges.")

# Events viewer (optional)
with st.expander("🛰️ Ship Events", expanded=False):
    if st.session_state.events:
        st.markdown("\n".join([f"- {x}" for x in st.session_state.events[-40:]]))
    else:
        st.caption("No events yet. Increase event rate in the sidebar or run /event.")

st.markdown(
    "<div class='small'>Commands: <kbd>/help</kbd> • <kbd>/status</kbd> • <kbd>/mission</kbd> • <kbd>/scan</kbd> • "
    "<kbd>/mode science</kbd> • <kbd>/event</kbd> • <kbd>/clear</kbd> — Export from sidebar.</div>",
    unsafe_allow_html=True
)
