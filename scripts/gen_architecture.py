#!/usr/bin/env python3
"""Render the marketplace architecture in the repo's HUD style, from repo data.

Usage: gen_hud.py <repo> "<TITLE>" "<SUBTITLE>" <out.svg>
Reads marketplace.json, every SKILL.md / agent frontmatter and hooks.json, so
the picture cannot drift from what the repo actually ships.
"""
import glob, json, os, re, sys

repo, title, subtitle, out = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]

CY, CY_DIM, AM, AM_DIM = "#22d3ee", "#4a90b8", "#fbbf24", "#fde68a"
RED, RED_DIM, PUR, PUR_DIM = "#f87171", "#fca5a5", "#a78bfa", "#c4b5fd"
TXT, SUB, GLOW = "#e6f8ff", "#8aa8c0", "#7ff3ff"
W = 1280

mp = json.load(open(os.path.join(repo, ".claude-plugin", "marketplace.json")))


def front(path):
    """First sentence of a SKILL.md / agent description field."""
    t = open(path).read()
    m = re.search(r"^description:\s*(?:[>|]-?\s*)?(.*?)(?=\n[a-z_]+:|\n---)", t, re.S | re.M)
    if not m:
        return ""
    d = " ".join(m.group(1).split())
    d = re.split(r"(?<=[a-z])\.\s|\. Trigger|\. Use ", d)[0]
    return d.strip(" .")


def wrap_items(items, width):
    """Two lines of ' · '-joined items, never breaking a name in half."""
    l1, l2, rest = "", "", []
    for it in items:
        cand = (l1 + " · " + it) if l1 else it
        if len(cand) <= width:
            l1 = cand
        else:
            rest.append(it)
    for it in rest:
        cand = (l2 + " · " + it) if l2 else it
        if len(cand) <= width:
            l2 = cand
        else:
            l2 = (l2 + " · …") if l2 else "…"
            break
    return l1, l2


def short(s, n):
    return s if len(s) <= n else s[: n - 1].rstrip(" ,·") + "…"


skill_groups, agents, hook_groups, infra, cmds = [], [], [], [], []
for p in mp["plugins"]:
    d = os.path.join(repo, p["source"].lstrip("./"))
    name = p["name"]
    sk = sorted(os.path.basename(os.path.dirname(f))
                for f in glob.glob(os.path.join(d, "skills", "*", "SKILL.md")))
    ag = sorted(glob.glob(os.path.join(d, "agents", "*.md")))
    cm = sorted(os.path.basename(f)[:-3] for f in glob.glob(os.path.join(d, "commands", "*.md")))
    hj = os.path.join(d, "hooks", "hooks.json")

    if sk:
        skill_groups.append((name, sk))
    for a in ag:
        agents.append((os.path.basename(a)[:-3], short(front(a), 34)))
    for c in cm:
        cmds.append("/" + c)
    if os.path.exists(hj):
        h = json.load(open(hj))
        n = sum(len(e.get("hooks", [])) for evs in h.get("hooks", {}).values() for e in evs)
        events = sorted(h.get("hooks", {}).keys())
        hook_groups.append((name, n, events, "blocking" if "guard" in name else "non-blocking",
                            short(p["description"].split(":")[-1].split(".")[0].strip(), 62)))
    if not sk and not ag and not cm and not os.path.exists(hj):
        infra.append((name, short(p["description"].split(":")[-1].split(".")[0].strip(), 46)))

N_SK = sum(len(s) for _, s in skill_groups)
svg = []
a = svg.append


def panel(x, y, w, h, color, dim, label):
    a(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="9" fill="url(#panelFill)" stroke="{color}" stroke-width="1.1"/>')
    for cx, cy, sx, sy in ((x, y, 22, 22), (x + w, y, -22, 22), (x, y + h, 22, -22), (x + w, y + h, -22, -22)):
        a(f'<path d="M{cx},{cy} h{sx} M{cx},{cy} v{sy}" stroke="{dim}" stroke-width="2.4" fill="none"/>')
    a(f'<text x="{x+w/2}" y="{y+35}" text-anchor="middle" fill="{dim}" font-size="19" letter-spacing="3" filter="url(#glow)">{label}</text>')
    a(f'<line x1="{x+50}" y1="{y+50}" x2="{x+w-50}" y2="{y+50}" stroke="{color}" stroke-width="0.9" opacity="0.6"/>')


# panel geometry
PY = 360
skill_rows = (len(skill_groups) + 1) // 2
PA_H = 104 + skill_rows * 62
agent_rows = (len(agents) + 1) // 2
PB_H = 104 + agent_rows * 50
TOP_H = max(PA_H, PB_H)
PC_Y = PY + TOP_H + 26
PC_H = 70 + sum(48 + 18 * max(1, len(e)) for _, _, e, _, _ in hook_groups) + 50
PD_H = 110 + (len(infra) + 2) * 52
BOT_H = max(PC_H, PD_H)
LIFE_Y = PC_Y + BOT_H + 60
H = LIFE_Y + 250

a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="Menlo, SF Mono, Consolas, monospace">')
a(f'''<defs>
<filter id="glow" x="-40%" y="-40%" width="180%" height="180%"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<radialGradient id="bgGlow" cx="50%" cy="14%" r="90%"><stop offset="0%" stop-color="#0e2233"/><stop offset="100%" stop-color="#070d16"/></radialGradient>
<linearGradient id="panelFill" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#0c1a2b" stop-opacity="0.95"/><stop offset="100%" stop-color="#081120" stop-opacity="0.95"/></linearGradient>
<marker id="arrowC" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{CY}"/></marker>
<marker id="arrowG" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{AM}"/></marker>
</defs>''')
a(f'<rect width="{W}" height="{H}" fill="url(#bgGlow)"/>')
grid_h = " ".join(f"M0,{y} H{W}" for y in range(160, H, 160))
grid_v = " ".join(f"M{x},0 V{H}" for x in range(160, W, 160))
a(f'<g stroke="#123049" stroke-width="0.5" opacity="0.3"><path d="{grid_h} {grid_v}"/></g>')

# header
a(f'<g filter="url(#glow)"><text x="{W/2}" y="58" text-anchor="middle" fill="{GLOW}" font-size="30" letter-spacing="6">{title}</text></g>')
a(f'<text x="{W/2}" y="88" text-anchor="middle" fill="{CY_DIM}" font-size="15" letter-spacing="4">{subtitle}</text>')
a(f'<path d="M300,104 H560 M720,104 H980" stroke="{CY}" stroke-width="1" opacity="0.6"/>')
a(f'<circle cx="{W/2}" cy="104" r="5" fill="none" stroke="{CY}"/><circle cx="{W/2}" cy="104" r="2" fill="{GLOW}"/>')

# settings + core
a(f'<rect x="400" y="126" width="480" height="64" rx="7" fill="url(#panelFill)" stroke="{CY}" stroke-width="1.3"/>')
a(f'<text x="{W/2}" y="153" text-anchor="middle" fill="{TXT}" font-size="17">~/.claude/settings.json</text>')
a(f'<text x="{W/2}" y="176" text-anchor="middle" fill="{CY_DIM}" font-size="13">extraKnownMarketplaces + enabledPlugins · user scope</text>')
a(f'<line x1="640" y1="190" x2="640" y2="222" stroke="{CY}" stroke-width="1.3" marker-end="url(#arrowC)"/>')
a(f'<g filter="url(#glow)"><circle cx="640" cy="272" r="46" fill="#0c1a2b" stroke="{CY}" stroke-width="1.6"/>')
a(f'<circle cx="640" cy="272" r="56" fill="none" stroke="{CY}" stroke-width="0.8" opacity="0.5" stroke-dasharray="4 6"/>')
a(f'<text x="640" y="268" text-anchor="middle" fill="{GLOW}" font-size="15">{mp["name"]}</text>')
a(f'<text x="640" y="286" text-anchor="middle" fill="{CY_DIM}" font-size="11">{len(mp["plugins"])} plugins</text></g>')
a(f'<path d="M598,296 C480,330 360,330 335,{PY-4}" fill="none" stroke="{CY}" stroke-width="1.1" marker-end="url(#arrowC)" opacity="0.85"/>')
a(f'<path d="M682,296 C800,330 920,330 945,{PY-4}" fill="none" stroke="{AM}" stroke-width="1.1" marker-end="url(#arrowG)" opacity="0.85"/>')
a(f'<path d="M614,316 C520,420 380,{PC_Y-120} 335,{PC_Y-4}" fill="none" stroke="{RED}" stroke-width="1" marker-end="url(#arrowC)" opacity="0.55"/>')
a(f'<path d="M666,316 C760,420 900,{PC_Y-120} 945,{PC_Y-4}" fill="none" stroke="{PUR}" stroke-width="1" marker-end="url(#arrowC)" opacity="0.55"/>')

# A: skills
panel(40, PY, 590, PA_H, CY, GLOW, f"WORKFLOW SKILLS · {N_SK}")
for i, (name, sk) in enumerate(skill_groups):
    col, row = i % 2, i // 2
    x, y = 66 + col * 290, PY + 86 + row * 62
    a(f'<text x="{x}" y="{y}" fill="{TXT}" font-size="15">▸ {name}</text>')
    l1, l2 = wrap_items(sk, 34)
    a(f'<text x="{x+14}" y="{y+20}" fill="{CY_DIM}" font-size="11.5">{l1}</text>')
    if l2:
        a(f'<text x="{x+14}" y="{y+36}" fill="{CY_DIM}" font-size="11.5">{l2}</text>')
a(f'<text x="66" y="{PY+PA_H-18}" fill="{CY}" font-size="12.5" opacity="0.85">triggered by intent or /command, run inline in the main context</text>')

# B: subagents
panel(650, PY, 590, PB_H, AM, AM_DIM, f"SUBAGENTS · {len(agents)}")
for i, (name, desc) in enumerate(agents):
    col, row = i % 2, i // 2
    x, y = 676 + col * 290, PY + 84 + row * 50
    a(f'<text x="{x}" y="{y}" fill="{TXT}" font-size="14">⬡ {name}</text>')
    a(f'<text x="{x+14}" y="{y+18}" fill="{SUB}" font-size="11">{short(desc, 32)}</text>')
a(f'<text x="676" y="{PY+PB_H-20}" fill="{AM}" font-size="12" opacity="0.85">fresh context each, restricted tools, run in parallel</text>')

# C: hooks
panel(40, PC_Y, 590, PC_H, RED, RED_DIM, "HOOKS · AUTOMATIC")
y = PC_Y + 84
for name, n, events, kind, desc in hook_groups:
    mark, col = ("⛔", RED) if kind == "blocking" else ("◈", GLOW)
    a(f'<text x="66" y="{y}" fill="{col}" font-size="15">{mark} {name} · {kind.upper()} · {n}</text>')
    y += 20
    a(f'<text x="82" y="{y}" fill="{SUB}" font-size="12.5">{desc}</text>')
    for e in events:
        y += 18
        a(f'<text x="82" y="{y}" fill="{SUB}" font-size="12">{e}</text>')
    y += 28
a(f'<text x="66" y="{PC_Y+PC_H-18}" fill="{RED}" font-size="12.5" opacity="0.85">fire on events, no one calls them: exit 2 vetoes the action</text>')

# D: infrastructure
panel(650, PC_Y, 590, PD_H, PUR, PUR_DIM, "INFRASTRUCTURE")
y = PC_Y + 84
for name, desc in infra:
    a(f'<text x="676" y="{y}" fill="{TXT}" font-size="15">⚙ {name}</text>')
    a(f'<text x="692" y="{y+20}" fill="{SUB}" font-size="12.5">{desc}</text>')
    y += 52
if cmds:
    a(f'<text x="676" y="{y}" fill="{TXT}" font-size="15">⚙ slash commands</text>')
    a(f'<text x="692" y="{y+20}" fill="{SUB}" font-size="12.5">{" · ".join(cmds)}</text>')
    y += 52
a(f'<text x="676" y="{y}" fill="{TXT}" font-size="15">⚙ .claude/ · versioned config</text>')
a(f'<text x="692" y="{y+20}" fill="{SUB}" font-size="12.5">settings.json + scripts, new machine = clone + copy</text>')
a(f'<text x="676" y="{PC_Y+PD_H-18}" fill="{PUR}" font-size="12.5" opacity="0.85">loaded when plugins are enabled, work in the background</text>')

# lifecycle strip
a(f'<text x="{W/2}" y="{LIFE_Y}" text-anchor="middle" fill="{GLOW}" font-size="17" letter-spacing="5" filter="url(#glow)">TASK LIFECYCLE</text>')
a(f'<line x1="380" y1="{LIFE_Y+12}" x2="580" y2="{LIFE_Y+12}" stroke="{CY}" stroke-width="0.9" opacity="0.5"/>')
a(f'<line x1="700" y1="{LIFE_Y+12}" x2="900" y2="{LIFE_Y+12}" stroke="{CY}" stroke-width="0.9" opacity="0.5"/>')
steps = [("requirements", "concretize + edges", CY_DIM, CY), ("plan-task", "+ architect", AM, CY),
         ("implement", "coach + guardrails", RED, CY), ("qa", "real flows", CY_DIM, CY),
         ("task-review", "+ reviewers", AM, CY), ("push gate", "pre-push-review", RED, RED),
         ("deploy", "runbook + verify", CY_DIM, CY), ("monitor", "logs + debugger", AM, CY)]
bx, by, bw = 34, LIFE_Y + 34, 145
for i, (t, s2, c2, edge) in enumerate(steps):
    x = bx + i * (bw + 10)
    a(f'<rect x="{x}" y="{by}" width="{bw}" height="64" rx="7" fill="#0c1a2b" stroke="{edge}"/>')
    a(f'<text x="{x+bw/2}" y="{by+27}" text-anchor="middle" fill="{TXT}" font-size="13">{t}</text>')
    a(f'<text x="{x+bw/2}" y="{by+45}" text-anchor="middle" fill="{c2}" font-size="11">{s2}</text>')
    if i < len(steps) - 1:
        a(f'<line x1="{x+bw}" y1="{by+32}" x2="{x+bw+8}" y2="{by+32}" stroke="{CY}" marker-end="url(#arrowC)"/>')
a(f'<path d="M{bx+7*(bw+10)+bw/2},{by+64} C{bx+7*(bw+10)},{by+130} {bx+80},{by+130} {bx+bw/2},{by+64}" fill="none" stroke="{AM}" stroke-width="1.1" stroke-dasharray="5 5" marker-end="url(#arrowG)" opacity="0.85"/>')
a(f'<text x="{W/2}" y="{by+152}" text-anchor="middle" fill="{AM}" font-size="12.5" opacity="0.9">bugs and incidents feed back into requirements</text>')
a(f'<text x="{W/2}" y="{H-24}" text-anchor="middle" fill="{CY_DIM}" font-size="12.5">{len(mp["plugins"])} plugins · {N_SK} skills · {len(agents)} subagents · {sum(n for _, n, _, _, _ in hook_groups)} hooks · every piece is plain Markdown and shell</text>')
a("</svg>")

open(out, "w").write("\n".join(svg))
print(f'{out}: {len(mp["plugins"])} plugins, {N_SK} skills, {len(agents)} agents, '
      f'{sum(n for _, n, _, _, _ in hook_groups)} hooks')
