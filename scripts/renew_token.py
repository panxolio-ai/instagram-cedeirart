#!/usr/bin/env python3
"""
Renova o IG_ACCESS_TOKEN (token de longa duración, 60 días) antes de que caduque.
Imprime o novo token en stdout para que o workflow o garde como GitHub Secret.
"""
import os
import json
import urllib.request
import urllib.parse

GRAPH_API = "https://graph.facebook.com/v21.0"


def env(name):
    val = os.environ.get(name)
    if not val:
        raise SystemExit(f"Falta a variable de contorno {name}")
    return val


def main():
    app_id = env("APP_ID")
    app_secret = env("APP_SECRET")
    current_token = env("IG_ACCESS_TOKEN")

    params = {
        "grant_type": "fb_exchange_token",
        "client_id": app_id,
        "client_secret": app_secret,
        "fb_exchange_token": current_token,
    }
    url = f"{GRAPH_API}/oauth/access_token?{urllib.parse.urlencode(params)}"
    with urllib.request.urlopen(url, timeout=60) as resp:
        data = json.loads(resp.read().decode())

    if "access_token" not in data:
        raise SystemExit(f"Erro renovando o token: {data}")

    print(data["access_token"])


if __name__ == "__main__":
    main()
