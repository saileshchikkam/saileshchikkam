import json

with open("data/contributions.json", encoding="utf-8") as f:
    data = json.load(f)

days = data["days"]
weeks = [days[i:i+7] for i in range(0, len(days), 7)][-53:]
palette = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
cell, gap, left, top = 12, 4, 28, 32
width = 53 * (cell + gap) + left + 12
height = 7 * (cell + gap) + 82

svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
       '<rect width="100%" height="100%" rx="10" fill="#0d1117"/>',
       f'<text x="{left}" y="19" font-family="monospace" font-size="12" fill="#8b949e">contributions - saileshchikkam</text>']

n = 0
for x, week in enumerate(weeks):
    for y, d in enumerate(week[:7]):
        level = max(0, min(5, int(d.get("level", 0))))
        px, py = left + x*(cell+gap), top + y*(cell+gap)
        delay = n * 0.004
        svg.append(
            f'<rect x="{px}" y="{py}" width="{cell}" height="{cell}" rx="3" fill="{palette[level]}" opacity="0">'
            f'<animate attributeName="opacity" from="0" to="1" begin="{delay:.3f}s" dur=".22s" fill="freeze"/>'
            f'<animateTransform attributeName="transform" type="translate" from="-5 -5" to="0 0" begin="{delay:.3f}s" dur=".22s" fill="freeze"/>'
            f'<title>{d.get("label","")}</title></rect>'
        )
        n += 1

total = sum(1 for d in days if d.get("level", 0) > 0)
svg.append(f'<text x="{left}" y="{height-30}" font-family="monospace" font-size="11" fill="#8b949e">{total:,} active contribution days in the captured calendar</text>')
svg.append(f'<text x="{width-205}" y="{height-30}" font-family="monospace" font-size="10" fill="#8b949e">Less</text>')
for i, c in enumerate(palette):
    svg.append(f'<rect x="{width-165+i*18}" y="{height-40}" width="12" height="12" rx="3" fill="{c}"/>')
svg.append(f'<text x="{width-18}" y="{height-30}" text-anchor="end" font-family="monospace" font-size="10" fill="#8b949e">More</text></svg>')

open("contrib-heatmap.svg", "w", encoding="utf-8").write("\n".join(svg))
