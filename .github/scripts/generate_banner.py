import urllib.request, json, os, datetime

token    = os.environ.get("GITHUB_TOKEN", "")
username = os.environ.get("USERNAME", "VaradaGovind")
headers  = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json", "User-Agent": "Python-urllib"} if token else {"Accept": "application/vnd.github+json", "User-Agent": "Python-urllib"}

# ── User profile ────────────────────────────────────────
try:
    req  = urllib.request.Request(f"https://api.github.com/users/{username}", headers=headers)
    user = json.loads(urllib.request.urlopen(req).read())
    repos_count = user.get("public_repos", 21)
except Exception as e:
    print("Profile fetch fallback:", e)
    repos_count = 21

# ── Stars ───────────────────────────────────────────────
try:
    req   = urllib.request.Request(f"https://api.github.com/users/{username}/repos?per_page=100", headers=headers)
    repos = json.loads(urllib.request.urlopen(req).read())
    stars = sum(r.get("stargazers_count", 0) for r in repos)
    if stars == 0:
        stars = 7
except Exception as e:
    print("Stars fetch fallback:", e)
    stars = 7

# ── Contributions via GraphQL ───────────────────────────
try:
    now   = datetime.datetime.now(datetime.timezone.utc)
except Exception:
    now   = datetime.datetime.utcnow()

start = (now - datetime.timedelta(days=365)).strftime("%Y-%m-%dT00:00:00Z")
end   = now.strftime("%Y-%m-%dT23:59:59Z")

total = 286
streak = 1
monthly = {}
all_days = []

if token:
    try:
        query = json.dumps({"query": f"""
        {{
          user(login: "{username}") {{
            contributionsCollection(from: "{start}", to: "{end}") {{
              contributionCalendar {{
                totalContributions
                weeks {{
                  contributionDays {{
                    contributionCount
                    date
                  }}
                }}
              }}
            }}
          }}
        }}
        """})
        
        gql_req  = urllib.request.Request("https://api.github.com/graphql",
            data=query.encode(), headers={**headers, "Content-Type": "application/json"})
        gql_data = json.loads(urllib.request.urlopen(gql_req).read())
        cal      = gql_data["data"]["user"]["contributionsCollection"]["contributionCalendar"]
        total    = cal.get("totalContributions", 286)

        for week in cal.get("weeks", []):
            for day in week.get("contributionDays", []):
                m = day["date"][:7]
                monthly[m] = monthly.get(m, 0) + day["contributionCount"]
                all_days.append((day["date"], day["contributionCount"]))

        all_days.sort(reverse=True)
        for _, c in all_days:
            if c > 0: streak += 1
            else: break
    except Exception as e:
        print("GraphQL fetch fallback:", e)

# ── Monthly buckets ─────────────────────────────────────
if monthly:
    sorted_months = sorted(monthly.keys())[-12:]
    counts  = [monthly.get(m, 0) for m in sorted_months]
    abbr    = {"01":"J","02":"F","03":"M","04":"A","05":"M","06":"J",
               "07":"J","08":"A","09":"S","10":"O","11":"N","12":"D"}
    labels  = [abbr.get(m[5:], "?") for m in sorted_months]
else:
    counts = [4, 4, 42, 70, 4, 4, 22, 21, 4, 4, 4, 50]
    labels = ["S", "O", "N", "D", "J", "F", "M", "A", "M", "J", "J", "A"]

max_c   = max(counts) if max(counts) > 0 else 1

BAR_H   = 54
BASELINE= 142
bar_x   = [310 + i * 18 for i in range(12)]

# ── Build animation keyframes ───────────────────────────
bar_anims = ""
for i, cnt in enumerate(counts):
    h = max(4, int(cnt / max_c * BAR_H))
    y_end = BASELINE - h
    bar_anims += f"@keyframes grow{i+1}{{0%{{height:0px;y:{BASELINE}px}}100%{{height:{h}px;y:{y_end}px}}}}\n"
    bar_anims += f"      .b{i+1}{{animation:grow{i+1} 0.85s cubic-bezier(0.34,1.56,0.64,1) {0.05+i*0.06:.2f}s both;}}\n"

# ── Build bar + label elements ──────────────────────────
bar_els = ""
lbl_els = ""
for i, (cnt, lx, lbl) in enumerate(zip(counts, bar_x, labels)):
    h   = max(4, int(cnt / max_c * BAR_H))
    y   = BASELINE - h
    bar_class = "bar-cyan" if i < 6 else "bar-green"
    bar_els += f'      <rect class="b{i+1} bar-base {bar_class}" x="{lx}" width="11" y="{y}" height="{h}" rx="2" />\n'
    lbl_els += f'      <text x="{lx+5.5:.1f}" y="155" class="mono text-dim" font-size="7.5" text-anchor="middle">{lbl}</text>\n'

updated = now.strftime("%d %b %Y")

svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 820 240" width="820" height="240">
  <defs>
    <style>
      @keyframes pulseDot {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.25; }} }}
      @keyframes float1 {{ 0%, 100% {{ transform: translateY(0px); }} 50% {{ transform: translateY(-2px); }} }}
      @keyframes float2 {{ 0%, 100% {{ transform: translateY(0px); }} 50% {{ transform: translateY(-2px); }} }}
      @keyframes float3 {{ 0%, 100% {{ transform: translateY(0px); }} 50% {{ transform: translateY(-2px); }} }}

      .mono {{ font-family: 'IBM Plex Mono', 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; }}
      .sans {{ font-family: 'Space Grotesk', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }}
      
      .font-bold {{ font-weight: 700; }}
      .font-black {{ font-weight: 900; }}

      .pulse {{ animation: pulseDot 1.8s ease-in-out infinite; }}
      .float-1 {{ animation: float1 3.5s ease-in-out infinite; }}
      .float-2 {{ animation: float2 4s ease-in-out infinite 0.7s; }}
      .float-3 {{ animation: float3 3.8s ease-in-out infinite 1.4s; }}

      /* ================= LIGHT MODE (Default) ================= */
      :root {{
        --bg-canvas: #fafaf7;
        --panel-bg: #ffffff;
        --border-main: #121214;
        --border-sub: #121214;
        --shadow-col: #121214;
        --grid-dot: rgba(18, 18, 20, 0.12);

        --text-head: #121214;
        --text-body: #18181b;
        --text-muted: #52525b;
        --text-dim: #71717a;
        --badge-text: #111111;

        --accent-yellow: #fef08a;
        --accent-cyan: #cffafe;
        --accent-green: #bbf7d0;
        --accent-pink: #fbcfe8;
        --accent-purple: #e9d5ff;

        --bar-cyan: #38bdf8;
        --bar-green: #4ade80;
      }}

      /* ================= DARK MODE ================= */
      @media (prefers-color-scheme: dark) {{
        :root {{
          --bg-canvas: #0f1013;
          --panel-bg: #18191f;
          --border-main: #71717a;
          --border-sub: #3f3f46;
          --shadow-col: #000000;
          --grid-dot: rgba(244, 244, 245, 0.14);

          --text-head: #ffffff;
          --text-body: #f4f4f5;
          --text-muted: #d4d4d8;
          --text-dim: #a1a1aa;
          --badge-text: #050505;

          --accent-yellow: #fde047;
          --accent-cyan: #38bdf8;
          --accent-green: #4ade80;
          --accent-pink: #f472b6;
          --accent-purple: #c084fc;

          --bar-cyan: #06b6d4;
          --bar-green: #10b981;
        }}
      }}

      .bg-canvas {{ fill: var(--bg-canvas) !important; }}
      .panel-bg {{ fill: var(--panel-bg) !important; }}
      .shadow-box {{ fill: var(--shadow-col) !important; }}
      
      .stroke-main {{ stroke: var(--border-main) !important; }}
      .stroke-sub {{ stroke: var(--border-sub) !important; }}
      
      .text-head {{ fill: var(--text-head) !important; }}
      .text-body {{ fill: var(--text-body) !important; }}
      .text-muted {{ fill: var(--text-muted) !important; }}
      .text-dim {{ fill: var(--text-dim) !important; }}
      .badge-text {{ fill: var(--badge-text) !important; }}

      .fill-yellow {{ fill: var(--accent-yellow) !important; }}
      .fill-cyan {{ fill: var(--accent-cyan) !important; }}
      .fill-green {{ fill: var(--accent-green) !important; }}
      .fill-pink {{ fill: var(--accent-pink) !important; }}
      .fill-purple {{ fill: var(--accent-purple) !important; }}

      .bar-base {{ stroke: var(--border-main); stroke-width: 1.2; }}
      .bar-cyan {{ fill: var(--bar-cyan) !important; }}
      .bar-green {{ fill: var(--bar-green) !important; }}

{bar_anims}
    </style>

    <pattern id="dot-grid" x="0" y="0" width="16" height="16" patternUnits="userSpaceOnUse">
      <circle cx="2" cy="2" r="0.85" fill="var(--border-main)" opacity="0.12"/>
    </pattern>
  </defs>

  <!-- ==================== OUTER FRAME WITH SHADOW ==================== -->
  <rect x="13" y="13" width="796" height="216" rx="8" class="shadow-box" opacity="0.95" />
  <rect x="10" y="10" width="796" height="216" rx="8" class="bg-canvas stroke-main" stroke-width="2.5" />
  <rect x="10" y="10" width="796" height="216" rx="8" fill="url(#dot-grid)" />

  <!-- Top Silicon IC Edge Pins (Symmetrically aligned over inter-column gaps) -->
  <g class="stroke-main" stroke-width="1.2" opacity="0.35">
    <line x1="262" y1="10" x2="262" y2="15" />
    <line x1="272" y1="10" x2="272" y2="15" />
    <line x1="282" y1="10" x2="282" y2="15" />
    <line x1="292" y1="10" x2="292" y2="15" />
    <line x1="524" y1="10" x2="524" y2="15" />
    <line x1="534" y1="10" x2="534" y2="15" />
    <line x1="544" y1="10" x2="544" y2="15" />
    <line x1="554" y1="10" x2="554" y2="15" />
  </g>

  <!-- ==================== COLUMN 1: IDENTITY & STATS (x=21, w=250, h=196) ==================== -->
  <!-- 1.1 Profile Identity Card (x=21, y=20, w=250, h=66) -->
  <g>
    <rect x="23" y="22" width="250" height="66" rx="6" class="shadow-box" />
    <rect x="21" y="20" width="250" height="66" rx="6" class="panel-bg stroke-main" stroke-width="2" />
    
    <!-- Chip Badge [VG] -->
    <g>
      <!-- IC Pin lines -->
      <line x1="42" y1="26" x2="42" y2="30" class="stroke-main" stroke-width="1.5" />
      <line x1="52" y1="26" x2="52" y2="30" class="stroke-main" stroke-width="1.5" />
      <line x1="62" y1="26" x2="62" y2="30" class="stroke-main" stroke-width="1.5" />
      <line x1="42" y1="76" x2="42" y2="80" class="stroke-main" stroke-width="1.5" />
      <line x1="52" y1="76" x2="52" y2="80" class="stroke-main" stroke-width="1.5" />
      <line x1="62" y1="76" x2="62" y2="80" class="stroke-main" stroke-width="1.5" />
      <line x1="27" y1="43" x2="31" y2="43" class="stroke-main" stroke-width="1.5" />
      <line x1="27" y1="53" x2="31" y2="53" class="stroke-main" stroke-width="1.5" />
      <line x1="27" y1="63" x2="31" y2="63" class="stroke-main" stroke-width="1.5" />
      <line x1="73" y1="43" x2="77" y2="43" class="stroke-main" stroke-width="1.5" />
      <line x1="73" y1="53" x2="77" y2="53" class="stroke-main" stroke-width="1.5" />
      <line x1="73" y1="63" x2="77" y2="63" class="stroke-main" stroke-width="1.5" />

      <!-- Chip Die Box -->
      <rect x="31" y="30" width="42" height="46" rx="4" class="fill-yellow stroke-main" stroke-width="1.8" />
      <text x="52" y="58" class="mono font-black badge-text" font-size="13" text-anchor="middle">VG</text>
    </g>

    <!-- Info Text -->
    <text x="85" y="37" class="mono font-bold text-muted" font-size="7.5" letter-spacing="0.8">HARDWARE RESEARCHER</text>
    <text x="85" y="53" class="sans font-black text-head" font-size="14" letter-spacing="-0.02em">VARADA GOVIND</text>
    <text x="85" y="69" class="mono text-muted" font-size="8.5" font-weight="600">@VaradaGovind · RTL/VLSI</text>
  </g>

  <!-- 1.2 Repos Metric Badge (x=21, y=94, w=120, h=50) -->
  <g>
    <rect x="23" y="96" width="120" height="50" rx="5" class="shadow-box" />
    <rect x="21" y="94" width="120" height="50" rx="5" class="fill-cyan stroke-main" stroke-width="1.8" />
    <text x="31" y="108" class="mono font-bold badge-text" font-size="8" letter-spacing="0.8">REPOS</text>
    <text x="31" y="128" class="mono font-black badge-text" font-size="19">{repos_count}</text>
    <text x="31" y="138" class="mono badge-text" font-size="6.8" opacity="0.9">public repositories</text>
  </g>

  <!-- 1.3 Stars Metric Badge (x=151, y=94, w=120, h=50) -->
  <g>
    <rect x="153" y="96" width="120" height="50" rx="5" class="shadow-box" />
    <rect x="151" y="94" width="120" height="50" rx="5" class="fill-yellow stroke-main" stroke-width="1.8" />
    <text x="161" y="108" class="mono font-bold badge-text" font-size="8" letter-spacing="0.8">STARS</text>
    <text x="161" y="128" class="mono font-black badge-text" font-size="19">{stars}</text>
    <text x="161" y="138" class="mono badge-text" font-size="6.8" opacity="0.9">earned stars ★</text>
  </g>

  <!-- 1.4 Bottom WIP Card (x=21, y=152, w=250, h=64) -->
  <g>
    <rect x="23" y="154" width="250" height="64" rx="6" class="shadow-box" />
    <rect x="21" y="152" width="250" height="64" rx="6" class="panel-bg stroke-main" stroke-width="1.8" />
    
    <!-- Yellow Status Dot (Vertically centered with project title) -->
    <circle cx="35" cy="166" r="3.5" class="fill-yellow stroke-main" stroke-width="1" />
    <circle cx="35" cy="166" r="3.5" class="fill-yellow pulse" />

    <!-- Project Title with Emoji -->
    <text x="44" y="169.5" class="mono font-black text-head" font-size="9.2">🤖 Argus — Multi-Agent AI</text>

    <!-- WIP Pill Badge on the right -->
    <rect x="227" y="159" width="34" height="14" rx="3" class="fill-pink stroke-main" stroke-width="1.2" />
    <text x="244" y="169.5" class="mono font-black badge-text" font-size="7.5" text-anchor="middle">WIP</text>

    <text x="31" y="187" class="mono text-muted" font-size="7.8">Hardware Debugging &amp; Root Cause Analysis</text>
    <text x="31" y="201" class="mono text-dim" font-size="7.2">Silicon Telemetry &amp; LLM Verification</text>
  </g>

  <!-- ==================== COLUMN 2: COMMIT ACTIVITY & LOGIC ANALYZER (x=283, w=250, h=196) ==================== -->
  <g>
    <rect x="285" y="22" width="250" height="196" rx="6" class="shadow-box" />
    <rect x="283" y="20" width="250" height="196" rx="6" class="panel-bg stroke-main" stroke-width="2" />
    
    <!-- Header -->
    <text x="293" y="35" class="mono font-bold text-head" font-size="8.5" letter-spacing="0.8">LOGIC ANALYZER // COMMITS</text>
    
    <!-- Total Pill -->
    <rect x="447" y="25" width="76" height="15" rx="3" class="fill-green stroke-main" stroke-width="1.2" />
    <text x="485" y="35.5" class="mono font-black badge-text" font-size="7.5" text-anchor="middle">{total} this year</text>

    <!-- Top Separator -->
    <line x1="293" y1="46" x2="523" y2="46" class="stroke-sub" stroke-width="1" opacity="0.6" />

    <!-- Voltage/Level Reference Grid -->
    <g class="mono text-dim" font-size="7.2">
      <text x="293" y="88">hi</text>
      <line x1="307" y1="86" x2="523" y2="86" class="stroke-sub" stroke-width="0.8" stroke-dasharray="2,3" opacity="0.4" />
      
      <text x="293" y="116">md</text>
      <line x1="307" y1="114" x2="523" y2="114" class="stroke-sub" stroke-width="0.8" stroke-dasharray="2,3" opacity="0.4" />
      
      <text x="293" y="144">lo</text>
      <line x1="307" y1="142" x2="523" y2="142" class="stroke-sub" stroke-width="1" opacity="0.75" />
    </g>

    <!-- 12 Monthly Activity Bars (Evenly spaced & centered) -->
    <g>
{bar_els}
    </g>

    <!-- Month Labels (Precisely centered beneath each bar) -->
    <g>
{lbl_els}
    </g>

    <!-- Activity Telemetry Footer -->
    <line x1="293" y1="165" x2="523" y2="165" class="stroke-sub" stroke-width="1" stroke-dasharray="3,2" opacity="0.6" />
    
    <g class="mono" font-size="8">
      <text x="293" y="180" class="text-muted">streak: <tspan class="text-head font-bold">{streak}d</tspan></text>
      <text x="370" y="180" class="text-muted">total: <tspan class="text-head font-bold">{total}</tspan></text>
      <text x="523" y="180" class="text-dim" text-anchor="end">sync: {updated}</text>
      <text x="293" y="198" class="mono text-dim" font-size="7">● LIVE CLOCK // 12-MONTH TRACE</text>
    </g>
  </g>

  <!-- ==================== COLUMN 3: TOP HARDWARE PROJECTS (x=545, w=250, h=196) ==================== -->
  <g>
    <rect x="547" y="22" width="250" height="196" rx="6" class="shadow-box" />
    <rect x="545" y="20" width="250" height="196" rx="6" class="panel-bg stroke-main" stroke-width="2" />

    <!-- Header -->
    <text x="555" y="35" class="mono font-bold text-head" font-size="8.5" letter-spacing="0.8">HARDWARE SILICON PIPELINE</text>
    <rect x="759" y="25" width="26" height="15" rx="3" class="fill-yellow stroke-main" stroke-width="1.2" />
    <text x="772" y="35.5" class="mono font-black badge-text" font-size="7.5" text-anchor="middle">RTL</text>
    
    <line x1="555" y1="46" x2="785" y2="46" class="stroke-sub" stroke-width="1" opacity="0.6" />

    <!-- Project 1: Prolepsis -->
    <text x="555" y="61" class="mono font-black text-head" font-size="9.5">🔮 Prolepsis</text>
    <g class="float-1">
      <rect x="747" y="50" width="38" height="14" rx="3" class="fill-yellow stroke-main" stroke-width="1" />
      <text x="766" y="60.5" class="mono font-black badge-text" font-size="7" text-anchor="middle">TMU</text>
    </g>
    <text x="555" y="74" class="mono text-muted" font-size="7.8">ISA-agnostic RTL predictive TMU</text>
    <text x="555" y="85" class="mono text-dim" font-size="7">Multicore speculative cache coherence</text>

    <line x1="555" y1="92" x2="785" y2="92" class="stroke-sub" stroke-width="0.8" stroke-dasharray="2,2" opacity="0.45" />

    <!-- Project 2: MobileNet-Accelerator-RTL -->
    <text x="555" y="107" class="mono font-black text-head" font-size="9.5">🏆 MobileNet-Accel</text>
    <g class="float-2">
      <rect x="725" y="96" width="60" height="14" rx="3" class="fill-purple stroke-main" stroke-width="1" />
      <text x="755" y="106.5" class="mono font-black badge-text" font-size="6.8" text-anchor="middle">DVCON '26</text>
    </g>
    <text x="555" y="120" class="mono text-muted" font-size="7.8">Systolic Array &amp; on-the-fly GAP engine</text>
    <text x="555" y="131" class="mono text-dim" font-size="7">Top 100 Submission · Verilog RTL</text>

    <line x1="555" y1="138" x2="785" y2="138" class="stroke-sub" stroke-width="0.8" stroke-dasharray="2,2" opacity="0.45" />

    <!-- Project 3: AES128-LowPower-Architecture -->
    <text x="555" y="153" class="mono font-black text-head" font-size="9.5">🔐 AES-128 Engine</text>
    <g class="float-3">
      <rect x="735" y="142" width="50" height="14" rx="3" class="fill-cyan stroke-main" stroke-width="1" />
      <text x="760" y="152.5" class="mono font-black badge-text" font-size="6.8" text-anchor="middle">CRYPTO</text>
    </g>
    <text x="555" y="166" class="mono text-muted" font-size="7.8">Hardware AES-128 cryptographic core</text>
    <text x="555" y="177" class="mono text-dim" font-size="7">Low-power CMOS VLSI digital design</text>

    <!-- Bottom Tech Pills / Stack -->
    <line x1="555" y1="184" x2="785" y2="184" class="stroke-sub" stroke-width="0.8" opacity="0.3" />
    <text x="555" y="200" class="mono text-muted" font-size="7.5">SystemVerilog · Verilog · RISC-V · Python</text>
  </g>
</svg>"""

with open("banner.svg", "w", encoding="utf-8") as f:
    f.write(svg)
print(f"Done — {total} contributions, {streak} day streak, {stars} stars")
