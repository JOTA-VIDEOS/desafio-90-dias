"""Robô do Desafio 90 Dias.

Lê as contas do Instagram pela API oficial (Instagram API com login do Instagram),
pega os vídeos postados desde o início do desafio e as métricas de cada um,
e grava tudo em dados.js, que o site (index.html) lê.

Uso:
  python coletar.py          -> coleta de verdade (tokens nas variáveis de ambiente)
  python coletar.py --demo   -> gera dados de exemplo para ver o site
"""
import json, os, random, subprocess, sys, urllib.parse, urllib.request
from datetime import datetime, timedelta, timezone

API = "https://graph.instagram.com/v23.0"
BRT = timezone(timedelta(hours=-3))  # Brasília, sem horário de verão
AQUI = os.path.dirname(os.path.abspath(__file__))


def get(caminho, token, **params):
    params["access_token"] = token
    url = caminho if caminho.startswith("http") else f"{API}/{caminho}?{urllib.parse.urlencode(params)}"
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.load(r)


def insights(media_id, token):
    """Visualizações, alcance, salvos, compartilhamentos. Tenta de novo sem 'views' se a API recusar."""
    for metricas in ("views,reach,saved,shares", "reach,saved,shares"):
        try:
            d = get(f"{media_id}/insights", token, metric=metricas)
            return {m["name"]: m["values"][0]["value"] for m in d.get("data", [])}
        except Exception:
            continue
    return {}


def coletar_conta(p, token, inicio):
    perfil = get("me", token, fields="username,profile_picture_url,followers_count")
    posts, url = [], None
    campos = "id,caption,media_type,media_product_type,timestamp,permalink,thumbnail_url,media_url,like_count,comments_count"
    pagina = get("me/media", token, fields=campos, limit=50)
    while True:
        acabou = False
        for m in pagina.get("data", []):
            quando = datetime.strptime(m["timestamp"], "%Y-%m-%dT%H:%M:%S%z").astimezone(BRT)
            if quando.date() < inicio:
                acabou = True
                break
            if m.get("media_type") != "VIDEO":  # só vídeo/Reels conta no desafio
                continue
            i = insights(m["id"], token)
            posts.append({
                "dia": quando.date().isoformat(),
                "hora": quando.strftime("%H:%M"),
                "link": m.get("permalink"),
                "thumb": m.get("thumbnail_url") or m.get("media_url"),
                "legenda": (m.get("caption") or "")[:90],
                "curtidas": m.get("like_count", 0),
                "comentarios": m.get("comments_count", 0),
                "views": i.get("views"),
                "alcance": i.get("reach"),
                "salvos": i.get("saved"),
                "compart": i.get("shares"),
            })
        proxima = pagina.get("paging", {}).get("next")
        if acabou or not proxima:
            break
        with urllib.request.urlopen(proxima, timeout=30) as r:
            pagina = json.load(r)
    return {
        "username": perfil.get("username"),
        "foto": perfil.get("profile_picture_url"),
        "seguidores": perfil.get("followers_count"),
        "posts": posts,
    }


def renovar_token(nome_secret, token):
    """Renova o token (vale 60 dias) e salva de volta no GitHub. Só roda se houver GH_PAT."""
    if not os.environ.get("GH_PAT"):
        return
    try:
        novo = get(f"{API.rsplit('/', 1)[0]}/refresh_access_token?"
                   + urllib.parse.urlencode({"grant_type": "ig_refresh_token", "access_token": token}), token)
        subprocess.run(["gh", "secret", "set", nome_secret], input=novo["access_token"], text=True,
                       check=True, env={**os.environ, "GH_TOKEN": os.environ["GH_PAT"]},
                       stdout=subprocess.DEVNULL)
        print(f"  token {nome_secret} renovado")
    except Exception as e:
        print(f"  não consegui renovar {nome_secret}: {type(e).__name__}")


def demo(cfg):
    random.seed(7)
    hoje = datetime.now(BRT).date()
    inicio = hoje - timedelta(days=23)
    cfg["inicio"] = inicio.isoformat()
    perfis = []
    for k, p in enumerate(cfg["participantes"]):
        posts, d = [], inicio
        while d <= hoje:
            chance = [0.97, 0.85, 0.75][k % 3]
            if random.random() < chance and not (d == hoje and k == 2):
                v = int(random.lognormvariate(7.6 + k * 0.2, 0.8))
                posts.append({"dia": d.isoformat(), "hora": f"{random.randint(9, 23):02d}:{random.randint(0, 59):02d}",
                              "link": "https://instagram.com", "thumb": None,
                              "legenda": random.choice(["POV: o vídeo de hoje saiu", "Dia de gravar na rua",
                                                        "Isso mudou meu jeito de editar", "Ninguém fala disso"]),
                              "curtidas": v // 12, "comentarios": v // 150, "views": v,
                              "alcance": int(v * 0.8), "salvos": v // 90, "compart": v // 70})
            d += timedelta(days=1)
        perfis.append({**p, "username": p["id"] + ".videos", "foto": None,
                       "seguidores": random.randint(800, 9000), "posts": posts[::-1], "erro": None})
    return perfis


def main():
    cfg = json.load(open(os.path.join(AQUI, "config.json"), encoding="utf-8"))
    eh_demo = "--demo" in sys.argv
    if eh_demo:
        perfis = demo(cfg)
    else:
        inicio = datetime.strptime(cfg["inicio"], "%Y-%m-%d").date()
        domingo = datetime.now(BRT).weekday() == 6
        perfis = []
        for p in cfg["participantes"]:
            token = os.environ.get(p["secret"], "").strip()
            base = {k: p[k] for k in ("id", "nome")}
            if not token:
                perfis.append({**base, "erro": "conta ainda não conectada", "posts": []})
                print(f"{p['nome']}: sem token")
                continue
            try:
                perfis.append({**base, **coletar_conta(p, token, inicio), "erro": None})
                print(f"{p['nome']}: {len(perfis[-1]['posts'])} vídeos")
                if domingo:
                    renovar_token(p["secret"], token)
            except Exception as e:
                perfis.append({**base, "erro": "falha ao ler o Instagram (token vencido?)", "posts": []})
                print(f"{p['nome']}: erro {type(e).__name__}")
    saida = {"titulo": cfg["titulo"], "inicio": cfg["inicio"], "dias": cfg["dias"], "demo": eh_demo,
             "atualizado": datetime.now(BRT).strftime("%d/%m/%Y %H:%M"), "participantes": perfis}
    with open(os.path.join(AQUI, "dados.js"), "w", encoding="utf-8") as f:
        f.write("window.DADOS = " + json.dumps(saida, ensure_ascii=False, indent=1) + ";\n")


if __name__ == "__main__":
    main()
