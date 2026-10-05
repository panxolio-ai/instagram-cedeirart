#!/usr/bin/env python3
"""
Publica en Instagram a(s) publicación(s) do día correspondente en publicacions/AAAA-MM-DD/.
So publica se existe un ficheiro APROBADO na carpeta dese post.

Soporta dous formatos de carpeta:
- Antigo (1 publicación/día): publicacions/AAAA-MM-DD/{reel.mp4|foto.jpg, texto.md, APROBADO}
- Novo (varias publicacións/día, por franxa horaria): publicacions/AAAA-MM-DD/13h-*/{...} ,
  publicacions/AAAA-MM-DD/19h-*/{...} — o número ao principio do nome da carpeta marca a
  hora (en Madrid) á que se debe publicar.

O arquivo multimedia sírvese directamente dende GitHub (raw.githubusercontent.com),
a partir do commit que se está a executar no workflow — non fai falla subilo a
ningún outro sitio. Require que o repositorio sexa público.

Uso: publish_daily.py [AAAA-MM-DD]
Se non se indica data, usa a data de hoxe (hora de España) e respecta as franxas horarias.
Se se indica data explicitamente, publica tódolos posts aprobados e non publicados dese día,
sen importar a hora (útil para probas e execucións manuais).
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

    hashtags = None
    for key, val in sections.items():
        if key.lower().startswith("hashtags") and val:
            hashtags = val

    # Os créditos NON van no texto da publicación (decisión de Fran, 2026-10-05) —
    # van como primeiro comentario cando a licenza esixe atribución (ver credits_requiring_attribution()).
    if hashtags:
        caption += f"\n\n{hashtags}"
    return caption.strip()


def credits_requiring_attribution(sections: dict) -> str | None:
    """Devolve o texto de créditos só se a licenza esixe atribución (CC BY / CC BY-SA).
    Fotos/gravacións propias e licenza Pexels non a esixen, e nese caso non se publica nada."""
    creditos = None
    for key, val in sections.items():
        if key.lower().startswith("créditos") and val:
            creditos = val
    if creditos and "CC BY" in creditos:
        return creditos
    return None


def find_media_file(post_dir: Path):
    for name in ("reel.mp4", "foto.jpg", "foto.jpeg", "foto.png"):
        p = post_dir / name
        if p.exists():
            return p
    raise SystemExit(f"Non atopei ningún arquivo de media en {post_dir}")


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


def post_credits_comment(media_id: str, credits_text: str, access_token: str):
    try:
        result = api_post(f"{media_id}/comments", {
            "message": credits_text,
            "access_token": access_token,
        })
        if "id" not in result:
            print(f"Aviso: non se puido publicar o comentario de créditos: {result}")
    except Exception as e:
        print(f"Aviso: erro publicando o comentario de créditos: {e}")


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


def find_posts(day_dir: Path):
    """Devolve unha lista de (nome, post_dir, hora_programada_ou_None)."""
    # Formato antigo: media directamente na carpeta do día.
    for name in ("reel.mp4", "foto.jpg", "foto.jpeg", "foto.png"):
        if (day_dir / name).exists():
            return [("", day_dir, None)]

    # Formato novo: subcarpetas tipo "13h-territorio", "19h-festival".
    posts = []
    for sub in sorted(day_dir.iterdir()):
        if not sub.is_dir():
            continue
        m = re.match(r"^(\d{1,2})h", sub.name)
        hour = int(m.group(1)) if m else None
        posts.append((sub.name, sub, hour))
    return posts


def publish_post(post_dir: Path, label: str) -> bool:
    if not (post_dir / "APROBADO").exists():
        print(f"[{label}] Non está aprobado. Non se publica.")
        return False

    if (post_dir / "PUBLICADO").exists():
        print(f"[{label}] Xa foi publicado anteriormente. Non se repite.")
        return False

    media_path = find_media_file(post_dir)
    texto_path = post_dir / "texto.md"
    sections = parse_texto(texto_path)
    caption = build_caption(sections)

    access_token = env("IG_ACCESS_TOKEN")
    ig_user_id = env("IG_USER_ID")

    public_url = public_url_for(media_path)
    print(f"[{label}] URL pública: {public_url}")

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

    print(f"[{label}] Creando contedor de media en Instagram...")
    creation = api_post(f"{ig_user_id}/media", create_data)
    if "id" not in creation:
        raise SystemExit(f"[{label}] Erro creando o contedor: {creation}")
    creation_id = creation["id"]
    print(f"[{label}] Contedor creado: {creation_id}")

    if is_video:
        wait_until_ready(creation_id, access_token)

    print(f"[{label}] Publicando...")
    publish = api_post(f"{ig_user_id}/media_publish", {
        "creation_id": creation_id,
        "access_token": access_token,
    })
    if "id" not in publish:
        raise SystemExit(f"[{label}] Erro publicando: {publish}")

    print(f"[{label}] Publicado correctamente! Media ID: {publish['id']}")

    credits_text = credits_requiring_attribution(sections)
    if credits_text:
        print(f"[{label}] Publicando créditos como comentario...")
        post_credits_comment(publish["id"], credits_text, access_token)

    (post_dir / "PUBLICADO").write_text(
        f"Publicado o {datetime.now(ZoneInfo('Europe/Madrid')).isoformat()} — media id {publish['id']}\n",
        encoding="utf-8",
    )
    return True


def main():
    now_madrid = datetime.now(ZoneInfo("Europe/Madrid"))
    date_str = sys.argv[1] if len(sys.argv) > 1 else now_madrid.strftime("%Y-%m-%d")
    force = len(sys.argv) > 1  # data explícita = ignora a xanela horaria

    day_dir = ROOT / "publicacions" / date_str
    if not day_dir.exists():
        print(f"Non hai publicación preparada para {date_str}. Nada que facer.")
        return

    posts = find_posts(day_dir)
    if not posts:
        print(f"Non atopei ningunha publicación en {day_dir}.")
        return

    any_published = False
    for name, post_dir, hour in posts:
        label = f"{date_str}/{name}" if name else date_str

        # Xanela aberta: publica en canto se chegue á hora obxectivo (ou máis tarde) ESE
        # mesmo día. Os cron de GitHub Actions non son puntuais (poden chegar con hora/s
        # de atraso), así que unha xanela estreita facía que se perdesen publicacións
        # enteiras — mellor publicar tarde ca non publicar (comprobado o 2026-10-05).
        target_hour = hour if hour is not None else 19  # formato antigo = 19:00 clásico
        if not force and now_madrid.hour < target_hour:
            print(f"[{label}] Son as {now_madrid.strftime('%H:%M')} en Madrid, aínda non chegou a hora das {target_hour}:00. Omitido nesta execución.")
            continue

        if publish_post(post_dir, label):
            any_published = True

    if not any_published:
        print("Non se publicou nada nesta execución.")


if __name__ == "__main__":
    main()
