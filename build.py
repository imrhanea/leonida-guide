#!/usr/bin/env python3
"""Assemble le site statique : src/pages/*.html + template -> dist/.

Chaque page source commence par un en-tête :
    ---
    title: Titre de la page
    description: Description pour Google (150-160 caractères)
    updated: 2026-11-18
    ---
puis le contenu HTML de la page.
"""
import pathlib, re, shutil, datetime

ROOT = pathlib.Path(__file__).parent
SRC = ROOT / "src" / "pages"
DIST = ROOT / "dist"
SITE_URL = "https://leonida-guide.imrhane-a-483.workers.dev"  # à remplacer quand le domaine .fr sera acheté
SITE_NAME = "Leonida Guide"

NAV = [
    ("index.html", "Accueil"),
    ("sortie.html", "Sortie & prix"),
    ("notes-presse.html", "Notes de la presse"),
    ("argent.html", "Gagner de l'argent"),
    ("codes-triche.html", "Codes de triche"),
    ("collection.html", "Objets à collectionner"),
    ("carte.html", "Carte"),
    ("personnages.html", "Personnages"),
]

template = (ROOT / "src" / "template.html").read_text(encoding="utf-8")


def parse(path):
    raw = path.read_text(encoding="utf-8")
    m = re.match(r"---\n(.*?)\n---\n(.*)", raw, re.S)
    meta = dict(line.split(": ", 1) for line in m.group(1).splitlines() if ": " in line)
    return meta, m.group(2)


def build():
    if DIST.exists():
        shutil.rmtree(DIST)
    shutil.copytree(ROOT / "static", DIST)
    urls = []
    for page in sorted(SRC.glob("*.html")):
        meta, body = parse(page)
        name = page.name
        current = ' aria-current="page"'
        nav = "\n".join(
            f'<a href="{href}"{current if href == name else ""}>{label}</a>'
            for href, label in NAV
        )
        updated = meta.get("updated", datetime.date.today().isoformat())
        d = datetime.date.fromisoformat(updated)
        mois = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet",
                "août", "septembre", "octobre", "novembre", "décembre"][d.month - 1]
        canonical = f"{SITE_URL}/" if name == "index.html" else f"{SITE_URL}/{name}"
        html = (template
                .replace("{{title}}", meta["title"])
                .replace("{{description}}", meta["description"])
                .replace("{{canonical}}", canonical)
                .replace("{{site_name}}", SITE_NAME)
                .replace("{{nav}}", nav)
                .replace("{{updated_iso}}", updated)
                .replace("{{updated}}", f"{d.day} {mois} {d.year}")
                .replace("{{content}}", body))
        (DIST / name).write_text(html, encoding="utf-8")
        if name != "404.html":
            urls.append((canonical, updated))
    sitemap = "\n".join(f"  <url><loc>{u}</loc><lastmod>{m}</lastmod></url>" for u, m in urls)
    (DIST / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{sitemap}\n</urlset>\n", encoding="utf-8")
    (DIST / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n")
    print(f"{len(urls)} pages générées dans {DIST}")


if __name__ == "__main__":
    build()
