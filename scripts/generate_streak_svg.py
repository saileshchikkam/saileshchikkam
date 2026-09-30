#!/usr/bin/env python3
"""Render Sailesh's live GitHub contribution calendar with an animated snake."""
import datetime, html, json, os, sys
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH=os.path.join(ROOT,'data','contributions.json')
OUT=sys.argv[2] if len(sys.argv)>2 else os.path.join(ROOT,'contrib-heatmap.svg')
CELL,GAP=13,3; STEP=CELL+GAP; LEFT,TOP=34,43; PAD=12
COLORS=['#161b22','#0e4429','#006d32','#26a641','#39d353']
GRAY='#7d8590'; FRAME='#30363d'; SNAKE='#69f0a0'; SNAKE_HEAD='#b4ffaa'

def level(c):
    if c<=0:return 0
    if c<=5:return 1
    if c<=15:return 2
    if c<=30:return 3
    return 4

def build_grid(days):
    first=datetime.date.fromisoformat(days[0]['date']); lead=(first.weekday()+1)%7
    cells=[None]*lead+days
    while len(cells)%7: cells.append(None)
    return [cells[i:i+7] for i in range(0,len(cells),7)]

def render(data):
    days=data['days']; grid=build_grid(days); cols=len(grid)
    grid_w=cols*STEP; grid_h=7*STEP; width=LEFT+grid_w+PAD; height=TOP+grid_h+72
    labels=[]; seen=set()
    for ci,col in enumerate(grid):
        for cell in col:
            if not cell: continue
            d=datetime.date.fromisoformat(cell['date']); key=(d.year,d.month)
            if key not in seen and d.day<=7: seen.add(key); labels.append((ci,d.strftime('%b')))
            break
    # Route stays in the channels between cells: a classic serpentine path.
    y0=TOP+CELL+GAP/2; points=[]
    x1=LEFT-GAP/2; x2=LEFT+(cols-1)*STEP+CELL+GAP/2
    for r in range(7):
        y=y0+r*STEP
        if r%2==0: points += [(x1,y),(x2,y)]
        else: points += [(x2,y),(x1,y)]
        if r<6: points.append((x2 if r%2==0 else x1,y+STEP))
    d_attr='M '+' '.join(f'{x:.1f},{y:.1f}' for x,y in points)
    today=datetime.date.today(); ytd=sum(d['count'] for d in days if d['date'].startswith(f'{today.year}-'))
    total=data.get('total_contributions',sum(d['count'] for d in days))
    cs=data.get('current_streak',{}).get('length',0); ls=data.get('longest_streak',{}).get('length',0)
    out=[f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace">
<style>
.lbl{{fill:{GRAY};font-size:10px;font-weight:600}} .meta{{fill:{GRAY};font-size:11px}}
@keyframes pop{{0%{{opacity:0;transform:scale(.2)}}60%{{opacity:1;transform:scale(1.08)}}100%{{opacity:1;transform:scale(1)}}}}
.c{{transform-box:fill-box;transform-origin:center;opacity:0;animation:pop .48s ease-out both}}
.snake{{fill:none;stroke:{SNAKE};stroke-width:2.2;stroke-linecap:round;stroke-linejoin:round;opacity:.72;stroke-dasharray:5 7;animation:dash 1.1s linear infinite}}
@keyframes dash{{to{{stroke-dashoffset:-24}}}}
@media(prefers-reduced-motion:reduce){{.c,.snake{{animation:none!important;opacity:1!important}}}}
</style>
<defs><linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#111722"/><stop offset="1" stop-color="#0a0e14"/></linearGradient><filter id="glow" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="2.2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter><path id="snakeRoute" d="{d_attr}"/></defs>
<rect width="100%" height="100%" rx="12" fill="url(#bg)"/><rect x=".5" y=".5" width="{width-1}" height="{height-1}" rx="12" fill="none" stroke="{FRAME}"/><line x1="0" y1="25" x2="{width}" y2="25" stroke="{FRAME}" stroke-opacity=".55"/>
<circle cx="14" cy="12.5" r="4" fill="#ff5f56"/><circle cx="27" cy="12.5" r="4" fill="#ffbd2e"/><circle cx="40" cy="12.5" r="4" fill="#27c93f"/><text x="{width/2:.1f}" y="16" fill="{GRAY}" font-size="11" text-anchor="middle">sailesh@github: ~/contributions --graph</text>''']
    for ci,label in labels: out.append(f'<text class="lbl" x="{LEFT+ci*STEP}" y="35">{html.escape(label)}</text>')
    for name,row in [('Mon',1),('Wed',3),('Fri',5)]: out.append(f'<text class="lbl" x="2" y="{TOP+row*STEP+CELL-2}">{name}</text>')
    for ci,col in enumerate(grid):
        for ri,cell in enumerate(col):
            if cell is None: continue
            x=LEFT+ci*STEP; y=TOP+ri*STEP; c=cell['count']; delay=ci*.018+ri*.045
            out.append(f'<rect class="c" x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2.5" fill="{COLORS[level(c)]}" style="animation-delay:{delay:.3f}s"><title>{html.escape(cell["date"])}: {c} contributions</title></rect>')
    out.append(f'''<path class="snake" d="{d_attr}"/><circle r="4.1" fill="{SNAKE_HEAD}" filter="url(#glow)"><animateMotion dur="11s" begin="3.8s" repeatCount="indefinite" rotate="auto"><mpath href="#snakeRoute"/></animateMotion></circle><circle r="2" fill="{SNAKE_HEAD}"><animateMotion dur="11s" begin="3.8s" repeatCount="indefinite" rotate="auto"><mpath href="#snakeRoute"/></animateMotion></circle>''')
    sep=TOP+grid_h+8
    out.append(f'<line x1="0" y1="{sep}" x2="{width}" y2="{sep}" stroke="{FRAME}" stroke-opacity=".35"/><text class="meta" x="{PAD}" y="{sep+20}"><tspan fill="#39d353" font-weight="700">{ytd:,}</tspan><tspan> contributions in {today.year} YTD</tspan></text><text class="meta" x="{width-PAD}" y="{sep+20}" text-anchor="end"><tspan fill="#e6edf3" font-weight="700">{total:,}</tspan> last-year total</text><text class="meta" x="{PAD}" y="{sep+42}">current streak <tspan fill="#22d3ee" font-weight="700">{cs}d</tspan> · longest <tspan fill="#22d3ee" font-weight="700">{ls}d</tspan></text><text class="meta" x="{width-PAD}" y="{sep+42}" text-anchor="end">snake route: live · data refresh: daily</text></svg>')
    return ''.join(out)

def main():
    with open(DATA_PATH,encoding='utf-8') as f:data=json.load(f)
    with open(OUT,'w',encoding='utf-8') as f:f.write(render(data))
    print('Wrote',OUT)
if __name__=='__main__': main()
