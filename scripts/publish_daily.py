#!/usr/bin/env python3
"""
Publica en Instagram a publicación do día correspondente en publicacions/AAAA-MM-DD/.
So publica se existe un ficheiro APROBADO nesa carpeta.

O arquivo multimedia sírvese directamente dende GitHub (raw.githubusercontent.com),
a partir do commit que se está a executar no workflow — non fai falla subilo a
ningún outro sitio. Require que o repositorio sexa público (ou que a URL raw sexa
accesible dende internet).

Uso: publish_daily.py [AAAA-MM-DD]
Se non se indica data, usa a data de hoxe (hora de España).
"""
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
import urllib.request
import urllib.parse
import json

ROOT = Path(__file__).resolve().parent.parent
GRAPH_API = "https://graph.facebook.com/v21.0"


def env(name):
    val = os.environ.get(name)
    if not val:
        raise SystemExit(f"Falta a variable de contorno {name}")
    return val


def parse_texto(texto_path: Path) -> dict:
    text = texto_path.read_text(encoding="utf-8")
    sections = {}
    current = None
    for line in text.splitlines():
        m = re.match(r"^##\s+(.+)$", line)
        if m:
            current = m.group(1).strip()
            sections[current] = []
            continue
        if line.startswith("# "):
            continue
        if current is not None:
            sections[current].append(line)
    return {k: "\n".join(v).strip() for k, v in sections.items()}


def build_caption(sections: dict) -> str:
    parts = []
    for key in sections:
        if key.lower().startswith("texto (galego)") or key.lower().startswith("texto (castellano)") or key.lower().startswith("text (english)"):
            if sections[key]:
                parts.append(sections[key])
    caption = "\n\n".join(parts)

    creditos = None
    hashtags = None
    for key, val in sections.items():
        if key.lower().startswith("créditos") and val:
            creditos = val
        if key.lower().startswith("hashtags") and val:
            hashtags = val

    if creditos:
        caption += f"\n\n{creditos}"
    if hashtags:
        caption += f"\n\n{hashtags}"
    return caption.strip()


def find_media_file(day_dir: Path):
    for name in ("reel.mp4", "foto.jpg", "foto.jpeg", "foto.png"):
        p = day_dir / name
        if p.exists():
            return p
    raise SystemExit(f"Non atopei ningún arquivo de media en {day_dir}")


def public_url_for(media_path: Path) -> str:
    """URL pública do arquivo, servido directamente dende GitHub (repo público)."""
    repo = env("GITHUB_REPOSITORY")  # "owner/repo", proporcionado por Actions
    sha = env("GITHUB_SHA")  # commit exacto que se está a executar
    rel_path = media_path.relative_to(ROOT).as_posix()
    return f"https://raw.githubusercontent.com/{repo}/{sha}/{urllib.parse.quote(rel_path)}"


def api_post(path: str, data: dict) -> dict:
    url = f"{GRAPH_API}/{path}"
    encoded = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(url, data=encoded, method="POST")
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read().decode())


def api_get(path: str, params: dict) -> dict:
    url = f"{GRAPH_API}/{path}?{urllib.parse.urlencode(params)}"
    with urllib.request.urlopen(url, timeout=60) as resp:
        return json.loads(resp.read().decode())


def wait_until_ready(creation_id: str, access_token: str, timeout_s=600):
    start = time.time()
    while time.time() - start < timeout_s:
        status = api_get(creation_id, {"fields": "status_code", "access_token": access_token})
        code = status.get("status_code")
        print(f"Estado do contedor {creation_id}: {code}")
        if code == "FINISHED":
            return
        if code == "ERROR":
            raise SystemExit(f"Erro procesando o media: {status}")
        time.sleep(10)
    raise SystemExit("Tempo esgotado esperando a que Instagram procese o media.")


def main():
    now_madrid = datetime.now(ZoneInfo("Europe/Madrid"))
    date_str = sys.argv[1] if len(sys.argv) > 1 else now_madrid.strftime("%Y-%m-%d")

    # Garda horaria: só publica sobre as 19:00 hora de España (agás chamada manual con data explícita).
    force = len(sys.argv) > 1
    if not force and not (18 <= now_madrid.hour <= 19):
        print(f"Son as {now_madrid.strftime('%H:%M')} en Madrid, fóra da xanela das 19:00. Non se publica nesta execución.")
        return

    day_dir = ROOT / "publicacions" / date_str

    if not day_dir.exists():
        print(f"Non hai publicación preparada para {date_str}. Nada que facer.")
        return

    if not (day_dir / "APROBADO").exists():
        print(f"A publicación de {date_str} non está aprobada. Non se publica.")
        return

    if (day_dir / "PUBLICADO").exists():
        print(f"A publicación de {date_str} xa foi publicada anteriormente. Non se repite.")
        return

    media_path = find_media_file(day_dir)
    texto_path = day_dir / "texto.md"
    sections = parse_texto(texto_path)
    caption = build_caption(sections)

    access_token = env("IG_ACCESS_TOKEN")
    ig_user_id = env("IG_USER_ID")

    public_url = public_url_for(media_path)
    print(f"URL pública: {public_url}")

    is_video = media_path.suffix.lower() == ".mp4"
    create_data = {
        "caption": caption,
        "access_token": access_token,
    }
    if is_video:
        create_data["media_type"] = "REELS"
        create_data["video_url"] = public_url
    else:
        create_data["image_url"] = public_url

    print("Creando contedor de media en Instagram...")
    creation = api_post(f"{ig_user_id}/media", create_data)
    if "id" not in creation:
        raise SystemExit(f"Erro creando o contedor: {creation}")
    creation_id = creation["id"]
    print(f"Contedor creado: {creation_id}")

    if is_video:
        wait_until_ready(creation_id, access_token)

    print("Publicando...")
    publish = api_post(f"{ig_user_id}/media_publish", {
        "creation_id": creation_id,
        "access_token": access_token,
    })
    if "id" not in publish:
        raise SystemExit(f"Erro publicando: {publish}")

    print(f"Publicado correctamente! Media ID: {publish['id']}")
    (day_dir / "PUBLICADO").write_text(
        f"Publicado o {datetime.now(ZoneInfo('Europe/Madrid')).isoformat()} — media id {publish['id']}\n",
        encoding="utf-8",
    )
    print("Feito.")


if __name__ == "__main__":
    main()
