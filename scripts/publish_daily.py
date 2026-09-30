#!/usr/bin/env python3
"""
Publica en Instagram a publicación do día correspondente en publicacions/AAAA-MM-DD/.
So publica se existe un ficheiro APROBADO nesa carpeta.

Uso: publish_daily.py [AAAA-MM-DD]
Se non se indica data, usa a data de hoxe (hora de España).
"""
import os
import re
import sys
import time
import ftplib
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
import urllib.request
import urllib.parse
import json

ROOT = Path(__file__).resolve().parent.parent
PUBLIC_BASE_URL = "https://ariacedeira.gal/ig"
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


def resolve_ipv4(host: str) -> str:
    """Algúns runners non teñen ruta IPv6; forzamos resolución IPv4."""
    import socket
    infos = socket.getaddrinfo(host, 21, socket.AF_INET, socket.SOCK_STREAM)
    return infos[0][4][0]


def ftp_connect(host: str, user: str, password: str) -> ftplib.FTP:
    ip = resolve_ipv4(host)
    ftp = ftplib.FTP(timeout=60)
    ftp.connect(ip, 21)
    ftp.login(user, password)
    return ftp


def ftp_upload(local_path: Path) -> str:
    host = env("FTP_HOST")
    user = env("FTP_USER")
    password = env("FTP_PASSWORD")
    remote_dir = os.environ.get("FTP_REMOTE_DIR", "/")

    ftp = ftp_connect(host, user, password)
    if remote_dir and remote_dir != "/":
        ftp.cwd(remote_dir)
    with open(local_path, "rb") as f:
        ftp.storbinary(f"STOR {local_path.name}", f)
    ftp.quit()
    return f"{PUBLIC_BASE_URL}/{local_path.name}"


def ftp_delete(filename: str):
    host = env("FTP_HOST")
    user = env("FTP_USER")
    password = env("FTP_PASSWORD")
    remote_dir = os.environ.get("FTP_REMOTE_DIR", "/")
    try:
        ftp = ftp_connect(host, user, password)
        if remote_dir and remote_dir != "/":
            ftp.cwd(remote_dir)
        ftp.delete(filename)
        ftp.quit()
    except Exception as e:
        print(f"Aviso: non se puido borrar {filename} do FTP: {e}")


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

    print(f"Subindo {media_path.name} por FTP...")
    public_url = ftp_upload(media_path)
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

    print("Borrando arquivo do FTP...")
    ftp_delete(media_path.name)
    print("Feito.")


if __name__ == "__main__":
    main()
