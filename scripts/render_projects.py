import os
import sys
import requests

USERNAME = "khemendra-labs"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")

LANG_COLORS = {
    "Python": "#3572A5", "JavaScript": "#F1E05A", "TypeScript": "#3178C6",
    "HTML": "#E34C26", "CSS": "#563D7C", "Java": "#B07219", "C": "#555555",
    "C++": "#F34B7D", "Jupyter Notebook": "#DA5B0B", "Shell": "#89E051",
    "PHP": "#4F5D95", "Go": "#00ADD8", "Rust": "#DEA584", "Ruby": "#701516",
}

def fetch_repos():
    headers = {"Accept": "application/vnd.github+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    r = requests.get(
        f"https://api.github.com/users/{USERNAME}/repos",
        params={"type": "owner", "sort": "updated", "per_page": 100},
        headers=headers,
        timeout=30,
    )
    r.raise_for_status()
    repos = r.json()
    repos = [x for x in repos if not x.get("fork") and x["name"].lower() != USERNAME.lower()]
    repos.sort(key=lambda x: x["pushed_at"], reverse=True)
    return repos[:6]

def esc(s):
    if not s:
        return ""
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))

def wrap_text(s, max_chars=46):
    if not s:
        return ["No description provided."]
    words = s.split()
    lines, cur = [], ""
    for w in words:
        if len(cur) + len(w) + 1 > max_chars:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
        if len(lines) == 2:
            break
    if cur and len(lines) < 2:
        lines.append(cur)
    return lines[:2] if lines else ["No description provided."]

def build_card(x, y, w, h, repo, theme):
    if theme == "dark":
        card_bg, border, title_c, text_c, dim_c = "#0D1526", "#22D3EE", "#F8FAFC", "#94A3B8", "#64748B"
    else:
        card_bg, border, title_c, text_c, dim_c = "#F8FAFC", "#0891B2", "#0F172A", "#334155", "#94A3B8"

    name = esc(repo["name"])
    desc_lines = wrap_text(repo.get("description") or "")
    lang = repo.get("language") or "—"
    lang_color = LANG_COLORS.get(lang, "#8B949E")
    stars = repo.get("stargazers_count", 0)
    forks = repo.get("forks_count", 0)

    parts = []
    parts.append(f'<g>')
    parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{card_bg}" stroke="{border}" stroke-width="1" opacity="0.95"/>')
    parts.append(f'<circle cx="{x+20}" cy="{y+26}" r="5" fill="{lang_color}"/>')
    parts.append(f'<text x="{x+34}" y="{y+31}" font-size="14" font-weight="bold" fill="{title_c}" font-family="Consolas, Menlo, monospace">{name}</text>')
    ty = y + 54
    for line in desc_lines:
        parts.append(f'<text x="{x+20}" y="{ty}" font-size="11.5" fill="{text_c}" font-family="Consolas, Menlo, monospace">{esc(line)}</text>')
        ty += 17
    footer_y = y + h - 18
    parts.append(f'<text x="{x+20}" y="{footer_y}" font-size="11" fill="{dim_c}" font-family="Consolas, Menlo, monospace">{esc(lang)}</text>')
    parts.append(f'<text x="{x+w-155}" y="{footer_y}" font-size="11" fill="{dim_c}" font-family="Consolas, Menlo, monospace">★ {stars}</text>')
    parts.append(f'<text x="{x+w-20}" y="{footer_y}" font-size="11" fill="{dim_c}" font-family="Consolas, Menlo, monospace" text-anchor="end">Forks: {forks}</text>')
    parts.append('</g>')
    return "\n".join(parts)

def build_grid(repos, theme, out_path):
    cols = 2
    card_w, card_h = 560, 110
    gap = 20
    pad = 10
    rows = (len(repos) + cols - 1) // cols if repos else 1
    W = cols * card_w + (cols - 1) * gap + pad * 2
    H = rows * card_h + (rows - 1) * gap + pad * 2

    svg = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">']
    if not repos:
        text_c = "#94A3B8"
        svg.append(f'<text x="{W/2}" y="{H/2}" font-size="14" fill="{text_c}" text-anchor="middle" font-family="Consolas, Menlo, monospace">No public repositories yet.</text>')
    else:
        for i, repo in enumerate(repos):
            col = i % cols
            row = i // cols
            x = pad + col * (card_w + gap)
            y = pad + row * (card_h + gap)
            svg.append(build_card(x, y, card_w, card_h, repo, theme))
    svg.append('</svg>')
    with open(out_path, "w") as f:
        f.write("\n".join(svg))
    print(f"wrote {out_path} ({len(repos)} repos)")

if __name__ == "__main__":
    out_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    repos = fetch_repos()
    build_grid(repos, "dark", f"{out_dir}/projects-dark.svg")
    build_grid(repos, "light", f"{out_dir}/projects-light.svg")
