#!/usr/bin/env python3
"""ASCEND — Web version (mobile-friendly)"""

import json, random, os
from datetime import date
from pathlib import Path
from flask import Flask, session, redirect, url_for, request

app = Flask(__name__)
app.secret_key = os.urandom(24)
SAVE_DIR = Path("/tmp/ascend_saves")
SAVE_DIR.mkdir(exist_ok=True)

# ── Data ──────────────────────────────────────────────────────

ARCHETYPES = {
    "Guerrier":  {"emoji":"⚔️",  "color":"#e74c3c", "desc":"Force et discipline. Tu avances quoi qu'il arrive.",
                  "stats":{"focus":6,"energie":8,"mental":5,"discipline":9,"sante":7,"social":5}},
    "Érudit":    {"emoji":"📚",  "color":"#3498db", "desc":"La connaissance est ton arme.",
                  "stats":{"focus":9,"energie":5,"mental":8,"discipline":7,"sante":4,"social":7}},
    "Athlète":   {"emoji":"🏆",  "color":"#2ecc71", "desc":"Le corps est ton temple. L'effort te définit.",
                  "stats":{"focus":6,"energie":9,"mental":6,"discipline":8,"sante":9,"social":7}},
    "Moine":     {"emoji":"🧘",  "color":"#9b59b6", "desc":"La paix intérieure est ta force.",
                  "stats":{"focus":8,"energie":6,"mental":10,"discipline":8,"sante":6,"social":5}},
    "Leader":    {"emoji":"👑",  "color":"#f39c12", "desc":"Tu inspires les autres.",
                  "stats":{"focus":7,"energie":7,"mental":7,"discipline":7,"sante":6,"social":10}},
}

STAT_META = {
    "focus":      {"emoji":"🎯","color":"#3498db","name":"Focus"},
    "energie":    {"emoji":"⚡","color":"#f1c40f","name":"Énergie"},
    "mental":     {"emoji":"🧠","color":"#9b59b6","name":"Mental"},
    "discipline": {"emoji":"🔥","color":"#e74c3c","name":"Discipline"},
    "sante":      {"emoji":"💪","color":"#2ecc71","name":"Santé"},
    "social":     {"emoji":"🌐","color":"#1abc9c","name":"Social"},
}

ACTIONS = {
    "1":{"name":"Deep Work",     "emoji":"💻","cost":3,"xp":30,"gains":{"focus":2,"discipline":1},
         "desc":"2h de concentration totale. Zéro distraction.",
         "msg":"Tu rentres dans un état de flow intense. Tu as accompli plus en 2h qu'en une journée normale.",
         "track":None},
    "2":{"name":"S'entraîner",   "emoji":"🏋️","cost":4,"xp":35,"gains":{"sante":3,"discipline":2,"energie":-1},
         "desc":"Entraînement physique intense.",
         "msg":"La sueur coule. Tu dépasses ta limite. Plus fort qu'hier.",
         "track":"train_today"},
    "3":{"name":"Méditer",       "emoji":"🧘","cost":1,"xp":20,"gains":{"mental":3,"focus":1,"energie":2},
         "desc":"20 minutes. Calme le chaos intérieur.",
         "msg":"Les pensées s'agitent, puis le silence s'installe. Tu rouvres les yeux — tout est plus net.",
         "track":"meditate_today"},
    "4":{"name":"Apprendre",     "emoji":"📖","cost":2,"xp":25,"gains":{"focus":1,"mental":2,"social":1},
         "desc":"Livre, podcast, formation. Nourris ton esprit.",
         "msg":"Une idée nouvelle s'allume. Une connexion inattendue se crée dans ton cerveau.",
         "track":"learn_count"},
    "5":{"name":"Se connecter",  "emoji":"🤝","cost":2,"xp":20,"gains":{"social":3,"mental":1},
         "desc":"Appel, rencontre, donner de la valeur.",
         "msg":"Tu tends la main sans attente. La conversation prend vie. Cette relation compte.",
         "track":"connect_count"},
    "6":{"name":"Créer",         "emoji":"🎨","cost":3,"xp":30,"gains":{"focus":2,"mental":2,"social":1},
         "desc":"Écrire, coder, construire quelque chose.",
         "msg":"Les idées coulent. Tu as créé quelque chose qui n'existait pas avant.",
         "track":None},
    "7":{"name":"Se reposer",    "emoji":"😴","cost":0,"xp":5,"gains":{"energie":5,"sante":1},
         "desc":"Récupérer — c'est stratégique, pas de la faiblesse.",
         "msg":"Tu lâches prise. Le corps récupère. Demain tu seras plus fort.",
         "track":None},
    "8":{"name":"Défi Boss",     "emoji":"⚔️","cost":5,"xp":0,"gains":{},
         "desc":"Affronte un ennemi intérieur. Haut risque, haute récompense.",
         "msg":"",
         "track":None},
}

EVENTS = [
    {"title":"TENTATION DIGITALE","color":"#f39c12",
     "desc":"Le scroll infini t'appelle. 30 min gaspillées... ou tu résistes ?",
     "choices":[
         ("Poser le téléphone et résister",{"discipline":2,"focus":1},15,"Victoire silencieuse. Ces moments comptent."),
         ("Céder — juste 5 min (c'est ce qu'on dit)",{"discipline":-1,"energie":-1},-5,"30 min deviennent 2h. Tu le savais."),
     ]},
    {"title":"OPPORTUNITÉ RISQUÉE","color":"#2ecc71",
     "desc":"Un projet excitant mais incertain se présente. Deadline courte.",
     "choices":[
         ("Foncer — l'inconfort est le chemin",{"discipline":1,"social":2,"focus":1},25,"Tu dis oui. L'aventure commence."),
         ("Refuser — pas le bon moment",{"mental":1},5,"Tu gardes le cap actuel. Sage décision."),
     ]},
    {"title":"CRITIQUE PUBLIQUE","color":"#e74c3c",
     "desc":"Quelqu'un critique ton travail devant tout le monde.",
     "choices":[
         ("Répondre avec calme et faits",{"mental":2,"social":1},20,"Tu réponds avec classe. Les gens remarquent."),
         ("Ignorer et continuer d'avancer",{"discipline":2},15,"Tu préserves ton énergie pour ce qui compte."),
         ("Répondre avec émotion",{"social":-2,"mental":-1},-10,"Tu le regrettes. Mais c'est humain."),
     ]},
    {"title":"INSPIRATION À 3H","color":"#9b59b6",
     "desc":"Une idée brillante surgit. Le sommeil ou l'idée ?",
     "choices":[
         ("Se lever pour noter",{"focus":2,"mental":2,"sante":-1},25,"L'idée est capturée. Valait le coup."),
         ("Se rendormir",{"sante":2,"energie":2},5,"Si elle est bonne, elle reviendra."),
     ]},
    {"title":"FLOW STATE","color":"#1abc9c",
     "desc":"Tout coule. Tu es dans la zone. Comment tu en profites ?",
     "choices":[
         ("Pousser encore — journée légendaire",{"focus":3,"discipline":2,"energie":-2},40,"Tu te surpasses. Journée gravée."),
         ("Finir sur une note haute et s'arrêter",{"mental":2,"sante":1},20,"Sage. L'élan sera là demain."),
     ]},
]

BOSSES = [
    {"name":"Le Syndrome de l'Imposteur","emoji":"👤","hp":30,
     "desc":"La voix qui dit que tu n'es pas assez bien.",
     "moves":[
         {"q":"Un gros projet. La voix dit : 'T'es pas à la hauteur.' Tu...",
          "opts":[("Agis malgré la peur — le courage c'est ça",15,True),
                  ("Procrastines jusqu'à la dernière minute",-5,False),
                  ("Demandes de l'aide sans honte",10,True),
                  ("Abandonnes pour éviter l'inconfort",-15,False)]},
         {"q":"Tu vois quelqu'un de plus avancé que toi. Tu ressens...",
          "opts":[("De l'inspiration — leur succès prouve que c'est possible",15,True),
                  ("De la jalousie transformée en carburant",10,True),
                  ("Du découragement total",-10,False),
                  ("Rien — tu te compares seulement à hier",12,True)]},
     ],"reward":{"mental":5,"discipline":3,"xp":150}},
    {"name":"La Procrastination","emoji":"⏰","hp":25,
     "desc":"L'ennemi silencieux de tous tes rêves.",
     "moves":[
         {"q":"UNE chose importante à faire. C'est inconfortable. Tu...",
          "opts":[("5 secondes de courage et tu commences maintenant",15,True),
                  ("Fais 10 petites tâches inutiles d'abord",-5,False),
                  ("Bloques 25 min sur le calendrier — là, tout de suite",12,True),
                  ("Regardes des vidéos de motivation pendant 1h",-8,False)]},
         {"q":"Quelle est la vraie racine de ta procrastination ?",
          "opts":[("Peur de l'échec — mieux vaut ne pas essayer",-5,False),
                  ("Peur du succès — et si tu dois maintenir ça ?",10,True),
                  ("Manque de clarté sur le prochain pas concret",15,True),
                  ("C'est juste de la flemme",-3,False)]},
     ],"reward":{"discipline":5,"focus":3,"xp":120}},
    {"name":"Le Saboteur Intérieur","emoji":"🌑","hp":35,
     "desc":"Le narrateur toxique qui vit dans ta tête.",
     "moves":[
         {"q":"Tu échoues à quelque chose d'important. Ton réflexe ?",
          "opts":[("Analyser sans jugement — qu'est-ce que ça m'apprend ?",15,True),
                  ("Te flageller pendant des jours",-10,False),
                  ("Blâmer les circonstances",-5,False),
                  ("Voir ça comme du feedback et recalibrer",18,True)]},
         {"q":"Complète : 'Je mérite...'",
          "opts":[("...de souffrir pour mes erreurs",-15,False),
                  ("...ce que je construis par mes actions",15,True),
                  ("...moins que les autres",-12,False),
                  ("...d'être traité comme je traite ceux que j'aime",18,True)]},
     ],"reward":{"mental":6,"social":3,"xp":180}},
]

QUESTS_DEF = [
    {"name":"Premier Pas",         "desc":"Effectue ta première action",        "check":lambda p:p["actions_done"]>=1,                                          "reward":{"xp":50,"discipline":2}},
    {"name":"Bâtisseur",           "desc":"Effectue 10 actions",               "check":lambda p:p["actions_done"]>=10,                                         "reward":{"xp":100,"focus":3}},
    {"name":"Corps & Esprit",      "desc":"Entraîne-toi ET médite le même jour","check":lambda p:p.get("train_today") and p.get("meditate_today"),              "reward":{"xp":80,"sante":3,"mental":3}},
    {"name":"Dévoreur",            "desc":"Apprends 5 fois",                   "check":lambda p:p.get("learn_count",0)>=5,                                     "reward":{"xp":90,"focus":4}},
    {"name":"Slayer de Boss",      "desc":"Vaincs ton premier boss intérieur",  "check":lambda p:p.get("bosses_killed",0)>=1,                                   "reward":{"xp":200,"mental":5}},
    {"name":"Régularité",          "desc":"Joue 3 jours consécutifs",          "check":lambda p:p.get("streak",0)>=3,                                          "reward":{"xp":150,"discipline":5}},
    {"name":"Niveau 5",            "desc":"Atteins le niveau 5",               "check":lambda p:p.get("level",1)>=5,                                           "reward":{"xp":0,"focus":3,"mental":3,"discipline":3}},
    {"name":"Connecteur",          "desc":"Connecte-toi aux autres 3 fois",    "check":lambda p:p.get("connect_count",0)>=3,                                   "reward":{"xp":70,"social":5}},
]

XP_TABLE = [0,100,250,450,700,1000,1400,1900,2500,3200,4000]

# ── Helpers ───────────────────────────────────────────────────

def save_file():
    sid = session.get("sid","default")
    return SAVE_DIR / f"{sid}.json"

def load_state():
    f = save_file()
    if f.exists():
        return json.loads(f.read_text())
    return None

def save_state(state):
    save_file().write_text(json.dumps(state, ensure_ascii=False))

def new_player(name, arch_name):
    arch = ARCHETYPES[arch_name]
    return {
        "name":name,"archetype":arch_name,"xp":0,"level":1,
        "stats":arch["stats"].copy(),
        "actions_done":0,"bosses_killed":0,"streak":1,
        "last_played":str(date.today()),
        "train_today":False,"meditate_today":False,
        "learn_count":0,"connect_count":0,
        "quest_done":[False]*len(QUESTS_DEF),
        "killed_bosses":[],
    }

def get_level(p):
    xp = p["xp"]
    for i,t in enumerate(XP_TABLE):
        if xp < t: return max(1,i-1)
    return len(XP_TABLE)-1

def xp_progress(p):
    lv = get_level(p)
    if lv >= len(XP_TABLE)-1: return XP_TABLE[-1],XP_TABLE[-1]
    lo,hi = XP_TABLE[lv],XP_TABLE[lv+1]
    return p["xp"]-lo, hi-lo

def add_xp(p, amount):
    old = get_level(p)
    p["xp"] += amount
    new = get_level(p)
    p["level"] = new
    return new if new > old else None

def apply_stat(p, stat, delta):
    if stat in p["stats"]:
        p["stats"][stat] = min(20, max(0, p["stats"][stat]+delta))

def check_quests(p):
    gained = []
    for i,qd in enumerate(QUESTS_DEF):
        if not p["quest_done"][i] and qd["check"](p):
            p["quest_done"][i] = True
            gained.append(qd)
            for k,v in qd["reward"].items():
                if k=="xp": add_xp(p,v)
                elif k in p["stats"]: p["stats"][k] = min(20,p["stats"][k]+v)
    return gained

def update_streak(p):
    today = str(date.today())
    last = p.get("last_played")
    if last == today: return
    if last:
        from datetime import timedelta
        delta = date.today() - date.fromisoformat(last)
        p["streak"] = (p.get("streak",1)+1) if delta.days==1 else 1
    else:
        p["streak"] = 1
    p["last_played"] = today
    p["train_today"] = False
    p["meditate_today"] = False

# ── HTML helpers ──────────────────────────────────────────────

CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{background:#0d0d14;color:#e8e8f0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;min-height:100vh;padding-bottom:2rem}
a{color:inherit;text-decoration:none}
.wrap{max-width:480px;margin:0 auto;padding:0 1rem}

/* header */
.hdr{background:linear-gradient(135deg,#1a1a2e,#16213e);padding:1rem;border-bottom:2px solid #f1c40f33}
.hdr-name{font-size:1.3rem;font-weight:700;color:#f1c40f}
.hdr-sub{font-size:.8rem;color:#888;margin-top:.2rem}
.xp-bar-wrap{margin-top:.5rem}
.xp-label{font-size:.75rem;color:#aaa;margin-bottom:.3rem}
.bar-outer{background:#1e1e2e;border-radius:99px;height:10px;overflow:hidden}
.bar-inner{height:100%;border-radius:99px;transition:width .4s}
.streak{font-size:.8rem;color:#e74c3c;margin-top:.4rem}

/* stats */
.stats-grid{display:grid;grid-template-columns:1fr 1fr;gap:.5rem;margin:1rem 0}
.stat-card{background:#1a1a2e;border-radius:10px;padding:.6rem .8rem}
.stat-top{display:flex;justify-content:space-between;align-items:center;margin-bottom:.4rem}
.stat-name{font-size:.75rem;font-weight:600}
.stat-val{font-size:.75rem;color:#888}
.stat-bar{height:6px;border-radius:99px;background:#0d0d14;overflow:hidden}
.stat-fill{height:100%;border-radius:99px}

/* actions */
.section-title{font-size:.8rem;font-weight:700;color:#888;letter-spacing:.1em;text-transform:uppercase;margin:.8rem 0 .5rem}
.action-btn{display:flex;align-items:center;gap:.8rem;background:#1a1a2e;border:1px solid #2a2a3e;border-radius:12px;padding:.8rem 1rem;margin-bottom:.5rem;width:100%;cursor:pointer;transition:all .15s;text-align:left}
.action-btn:active{transform:scale(.97);background:#252540}
.action-icon{font-size:1.4rem;width:2rem;text-align:center}
.action-info{flex:1}
.action-name{font-size:.95rem;font-weight:600}
.action-desc{font-size:.72rem;color:#888;margin-top:.15rem}
.action-cost{font-size:.75rem;color:#f1c40f;white-space:nowrap}
.action-btn.boss{border-color:#e74c3c44;background:#1e0d0d}
.action-btn.disabled{opacity:.4;cursor:not-allowed}

/* result / event */
.card{background:#1a1a2e;border-radius:14px;padding:1.2rem;margin:1rem 0}
.card-title{font-size:1.1rem;font-weight:700;margin-bottom:.8rem}
.result-item{display:flex;align-items:center;gap:.5rem;padding:.3rem 0;font-size:.9rem}
.up{color:#2ecc71}.down{color:#e74c3c}
.xp-gain{color:#f1c40f;font-weight:700}
.levelup{background:linear-gradient(135deg,#f39c12,#e74c3c);color:white;border-radius:10px;padding:.8rem 1rem;text-align:center;font-weight:700;font-size:1rem;margin:.8rem 0}
.msg{color:#aaa;font-style:italic;line-height:1.5;margin-bottom:.8rem;font-size:.9rem}
.quest-done{background:#1e2d1e;border:1px solid #2ecc7144;border-radius:10px;padding:.7rem;margin:.5rem 0}
.quest-title{color:#2ecc71;font-weight:700;font-size:.85rem}
.quest-rew{color:#aaa;font-size:.78rem;margin-top:.2rem}

/* choices */
.choice-btn{display:block;width:100%;background:#141424;border:1px solid #2a2a3e;border-radius:12px;padding:.85rem 1rem;margin-bottom:.5rem;cursor:pointer;text-align:left;font-size:.88rem;color:#e8e8f0;transition:all .15s}
.choice-btn:active{transform:scale(.97);background:#1e1e3e}
.event-title{font-size:1.1rem;font-weight:700;margin-bottom:.5rem}
.event-desc{color:#ccc;line-height:1.5;margin-bottom:1rem;font-size:.9rem}

/* boss */
.boss-banner{background:linear-gradient(135deg,#2d0000,#1a0000);border:1px solid #e74c3c44;border-radius:14px;padding:1.2rem;text-align:center;margin:1rem 0}
.boss-name{font-size:1.2rem;font-weight:700;color:#e74c3c}
.boss-emoji{font-size:2.5rem;margin:.5rem 0}
.boss-desc{color:#aaa;font-size:.85rem}
.hp-row{display:flex;align-items:center;gap:.8rem;margin:.6rem 0;font-size:.85rem}
.hp-label{width:4rem;color:#888}

/* quests */
.quest-card{background:#1a1a2e;border-radius:12px;padding:.8rem 1rem;margin-bottom:.5rem;border-left:3px solid #333}
.quest-card.done{border-left-color:#2ecc71;opacity:.6}
.quest-card.pending{border-left-color:#f39c12}
.q-name{font-weight:600;font-size:.9rem}
.q-desc{color:#888;font-size:.78rem;margin-top:.2rem}
.q-rew{color:#f39c12;font-size:.75rem;margin-top:.3rem}

/* create */
.create-wrap{padding:1.5rem 1rem}
.logo{text-align:center;padding:2rem 0 1.5rem}
.logo-title{font-size:2rem;font-weight:900;color:#f1c40f;letter-spacing:.05em}
.logo-sub{color:#888;margin-top:.3rem;font-size:.85rem}
.input-group{margin:1rem 0}
label{display:block;font-size:.8rem;color:#888;margin-bottom:.4rem;font-weight:600;letter-spacing:.05em;text-transform:uppercase}
input[type=text]{width:100%;background:#1a1a2e;border:1px solid #2a2a3e;border-radius:10px;padding:.8rem 1rem;color:#e8e8f0;font-size:1rem;outline:none}
input[type=text]:focus{border-color:#f1c40f55}
.arch-grid{display:grid;grid-template-columns:1fr 1fr;gap:.6rem;margin:.5rem 0}
.arch-card{background:#1a1a2e;border:2px solid #2a2a3e;border-radius:12px;padding:.8rem;cursor:pointer;transition:all .15s;text-align:center}
.arch-card:active{transform:scale(.95)}
.arch-card input{display:none}
.arch-card.selected,.arch-card:has(input:checked){border-color:#f1c40f;background:#1e1e0a}
.arch-emoji{font-size:1.8rem}
.arch-name{font-size:.85rem;font-weight:700;margin:.3rem 0}
.arch-desc{font-size:.7rem;color:#888;line-height:1.3}
.btn-primary{display:block;width:100%;background:linear-gradient(135deg,#f39c12,#e74c3c);color:white;border:none;border-radius:12px;padding:1rem;font-size:1rem;font-weight:700;cursor:pointer;margin-top:1.2rem;letter-spacing:.03em}
.btn-secondary{display:block;background:#1a1a2e;border:1px solid #2a2a3e;border-radius:12px;padding:.8rem 1rem;text-align:center;color:#aaa;margin-top:.5rem;font-size:.9rem;cursor:pointer;width:100%}
.nav-bar{display:flex;gap:.5rem;padding:.8rem 1rem;background:#0d0d14;border-bottom:1px solid #1e1e2e;position:sticky;top:0;z-index:10}
.nav-btn{flex:1;text-align:center;padding:.5rem;border-radius:8px;font-size:.75rem;color:#888;background:#1a1a2e}
.nav-btn.active{background:#f1c40f;color:#0d0d14;font-weight:700}
"""

def base(content, title="ASCEND"):
    return f"""<!DOCTYPE html><html lang="fr"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1">
<title>{title}</title><style>{CSS}</style></head><body>{content}</body></html>"""

def stat_bars_html(stats):
    html = '<div class="stats-grid">'
    for k,m in STAT_META.items():
        v = stats[k]; pct = (v/20)*100
        html += f"""<div class="stat-card">
  <div class="stat-top"><span class="stat-name">{m['emoji']} {m['name']}</span><span class="stat-val">{v}/20</span></div>
  <div class="stat-bar"><div class="stat-fill" style="width:{pct}%;background:{m['color']}"></div></div>
</div>"""
    return html + "</div>"

def player_header_html(p):
    arch = ARCHETYPES[p["archetype"]]
    lv = get_level(p)
    xp_cur, xp_max = xp_progress(p)
    pct = int((xp_cur/xp_max)*100) if xp_max else 100
    streak = p.get("streak",1)
    return f"""<div class="hdr"><div class="wrap">
  <div class="hdr-name">{arch['emoji']} {p['name']}</div>
  <div class="hdr-sub">{p['archetype']} · Niveau {lv}</div>
  <div class="xp-bar-wrap">
    <div class="xp-label">XP {xp_cur}/{xp_max}</div>
    <div class="bar-outer"><div class="bar-inner" style="width:{pct}%;background:linear-gradient(90deg,#f39c12,#e74c3c)"></div></div>
  </div>
  <div class="streak">🔥 Streak : {streak} jour{'s' if streak>1 else ''} · {date.today()}</div>
</div></div>"""

# ── Routes ────────────────────────────────────────────────────

@app.before_request
def ensure_session():
    if "sid" not in session:
        session["sid"] = os.urandom(8).hex()

@app.route("/")
def index():
    state = load_state()
    if not state:
        return redirect(url_for("create"))
    update_streak(state["player"])
    save_state(state)
    return redirect(url_for("game"))

# ── Create character ──────────────────────────────────────────

@app.route("/create", methods=["GET","POST"])
def create():
    if request.method == "POST":
        name = request.form.get("name","").strip() or "Aventurier"
        arch = request.form.get("archetype","Guerrier")
        if arch not in ARCHETYPES: arch = "Guerrier"
        p = new_player(name, arch)
        save_state({"player": p})
        return redirect(url_for("game"))

    arch_html = ""
    for k,a in ARCHETYPES.items():
        arch_html += f"""<label class="arch-card">
  <input type="radio" name="archetype" value="{k}" {'checked' if k=='Guerrier' else ''}>
  <div class="arch-emoji">{a['emoji']}</div>
  <div class="arch-name" style="color:{a['color']}">{k}</div>
  <div class="arch-desc">{a['desc']}</div>
</label>"""

    body = f"""<div class="create-wrap">
<div class="logo">
  <div class="logo-title">⚡ ASCEND</div>
  <div class="logo-sub">Le RPG du Développement Personnel</div>
</div>
<form method="POST">
  <div class="input-group">
    <label>Ton nom</label>
    <input type="text" name="name" placeholder="Ton prénom ou pseudo" maxlength="30" autocomplete="off">
  </div>
  <div class="input-group">
    <label>Ton archétype</label>
    <div class="arch-grid">{arch_html}</div>
  </div>
  <button type="submit" class="btn-primary">Commencer ma quête →</button>
</form></div>""" + """<script>
document.querySelectorAll('.arch-card').forEach(function(c){
  c.addEventListener('click',function(){
    document.querySelectorAll('.arch-card').forEach(function(x){x.classList.remove('selected');});
    c.classList.add('selected');
  });
});
document.querySelector('.arch-card').classList.add('selected');
</script>"""
    return base(body, "ASCEND — Créer un personnage")

# ── Main game ─────────────────────────────────────────────────

@app.route("/game")
def game():
    state = load_state()
    if not state: return redirect(url_for("create"))
    p = state["player"]
    arch = ARCHETYPES[p["archetype"]]

    actions_html = ""
    for key, a in ACTIONS.items():
        en = p["stats"]["energie"]
        disabled = "disabled" if a["cost"] > en else ""
        boss_cls = " boss" if key=="8" else ""
        cost_s = f"-{a['cost']}⚡" if a["cost"] > 0 else "gratuit"
        gains_s = " · ".join(f"+{v} {STAT_META[s]['name']}" for s,v in a["gains"].items() if v>0)
        btn_content = f"""<div class="action-icon">{a['emoji']}</div>
<div class="action-info">
  <div class="action-name">{a['name']}</div>
  <div class="action-desc">{a['desc']}{(' · ' + gains_s) if gains_s else ''}</div>
</div>
<div class="action-cost">{cost_s}</div>"""
        if disabled:
            actions_html += f'<div class="action-btn{boss_cls} disabled">{btn_content}</div>'
        else:
            actions_html += f'<form method="POST" action="/action"><input type="hidden" name="key" value="{key}"><button type="submit" class="action-btn{boss_cls}">{btn_content}</button></form>'

    body = player_header_html(p) + f"""
<div class="wrap">
  <div class="nav-bar" style="position:static;padding:.5rem 0;border:none;background:none">
    <span class="nav-btn active">Jouer</span>
    <a href="/quests" class="nav-btn">Quêtes</a>
    <a href="/create" class="nav-btn" onclick="return confirm('Nouveau personnage ? Ta sauvegarde sera effacée.')">Nouveau</a>
  </div>
  {stat_bars_html(p['stats'])}
  <div class="section-title">Actions</div>
  {actions_html}
</div>"""
    return base(body)

# ── Do action ─────────────────────────────────────────────────

@app.route("/action", methods=["POST"])
def action():
    state = load_state()
    if not state: return redirect(url_for("create"))
    p = state["player"]
    key = request.form.get("key","")
    if key not in ACTIONS: return redirect(url_for("game"))

    if key == "8":
        return redirect(url_for("boss_start"))

    a = ACTIONS[key]
    if p["stats"]["energie"] < a["cost"]:
        return redirect(url_for("game"))

    p["stats"]["energie"] = max(0, p["stats"]["energie"] - a["cost"])
    changes = []
    for stat, delta in a["gains"].items():
        if stat in p["stats"]:
            before = p["stats"][stat]
            p["stats"][stat] = min(20, max(0, before+delta))
            diff = p["stats"][stat]-before
            if diff: changes.append((stat, diff))

    p["actions_done"] = p.get("actions_done",0)+1
    t = a["track"]
    if t == "train_today":    p["train_today"] = True
    elif t == "meditate_today": p["meditate_today"] = True
    elif t == "learn_count":  p["learn_count"] = p.get("learn_count",0)+1
    elif t == "connect_count":p["connect_count"] = p.get("connect_count",0)+1

    level_up = add_xp(p, a["xp"])
    quests_done = check_quests(p)

    # maybe trigger random event
    trigger_event = (key != "7" and random.random() < 0.35)
    if trigger_event:
        ev = random.choice(EVENTS)
        state["pending_event"] = ev
        save_state(state)

    save_state(state)

    # Build result page
    changes_html = ""
    for stat, diff in changes:
        m = STAT_META[stat]
        cls = "up" if diff>0 else "down"
        arrow = "↑" if diff>0 else "↓"
        changes_html += f'<div class="result-item"><span>{m["emoji"]} {m["name"]}</span><span class="{cls}">{arrow}{abs(diff)} → {p["stats"][stat]}/20</span></div>'
    if a["xp"]:
        changes_html += f'<div class="result-item xp-gain">✨ +{a["xp"]} XP</div>'

    levelup_html = ""
    if level_up:
        levelup_html = f'<div class="levelup">🎉 LEVEL UP → Niveau {level_up} !</div>'

    quests_html = ""
    for q in quests_done:
        rew = "  ".join(f"+{v} {k}" for k,v in q["reward"].items())
        quests_html += f'<div class="quest-done"><div class="quest-title">🏆 {q["name"]}</div><div class="quest-rew">{q["desc"]} · Récompense : {rew}</div></div>'

    next_url = "/event" if trigger_event else "/game"

    body = player_header_html(p) + f"""<div class="wrap">
<div class="card">
  <div class="card-title">{a['emoji']} {a['name']}</div>
  <p class="msg">{a['msg']}</p>
  {changes_html}
  {levelup_html}
  {quests_html}
</div>
<a href="{next_url}" class="btn-primary" style="display:block;text-align:center;padding:1rem;background:linear-gradient(135deg,#f39c12,#e74c3c);color:white;border-radius:12px;font-weight:700">
  {'⚡ Événement →' if trigger_event else '← Retour au jeu'}
</a></div>"""
    return base(body, a["name"])

# ── Random event ──────────────────────────────────────────────

@app.route("/event", methods=["GET","POST"])
def event():
    state = load_state()
    if not state: return redirect(url_for("create"))
    p = state["player"]
    ev = state.get("pending_event")
    if not ev: return redirect(url_for("game"))

    if request.method == "POST":
        idx = int(request.form.get("choice",0))
        choices = ev["choices"]
        if 0 <= idx < len(choices):
            label, effects, xp_gain, msg = choices[idx]
            for stat, delta in effects.items():
                apply_stat(p, stat, delta)
            level_up = add_xp(p, max(0, xp_gain)) if xp_gain else None
            quests_done = check_quests(p)
            state.pop("pending_event", None)
            save_state(state)

            changes_html = ""
            for stat, delta in effects.items():
                if stat in p["stats"]:
                    m = STAT_META[stat]
                    cls = "up" if delta>0 else "down"
                    arrow = "↑" if delta>0 else "↓"
                    changes_html += f'<div class="result-item"><span>{m["emoji"]} {m["name"]}</span><span class="{cls}">{arrow}{abs(delta)} → {p["stats"][stat]}/20</span></div>'
            if xp_gain:
                cls = "up" if xp_gain>0 else "down"
                changes_html += f'<div class="result-item {cls} xp-gain">✨ {xp_gain:+d} XP</div>'
            levelup_html = f'<div class="levelup">🎉 LEVEL UP → Niveau {level_up} !</div>' if level_up else ""
            quests_html = "".join(f'<div class="quest-done"><div class="quest-title">🏆 {q["name"]}</div></div>' for q in quests_done)

            body = player_header_html(p) + f"""<div class="wrap">
<div class="card" style="border-left:3px solid {ev['color']}">
  <div class="card-title">⚡ {ev['title']}</div>
  <p class="msg">"{label}" — {msg}</p>
  {changes_html}{levelup_html}{quests_html}
</div>
<a href="/game" class="btn-primary" style="display:block;text-align:center;padding:1rem;background:linear-gradient(135deg,#f39c12,#e74c3c);color:white;border-radius:12px;font-weight:700">← Retour au jeu</a>
</div>"""
            return base(body, ev["title"])

    choices_html = ""
    for i,(label,_,_,_) in enumerate(ev["choices"]):
        choices_html += f'<button type="submit" name="choice" value="{i}" class="choice-btn">{label}</button>'

    body = player_header_html(p) + f"""<div class="wrap">
<div class="card" style="border-left:3px solid {ev['color']};margin-top:1rem">
  <div class="event-title">⚡ {ev['title']}</div>
  <div class="event-desc">{ev['desc']}</div>
  <form method="POST">{choices_html}</form>
</div></div>"""
    return base(body, ev["title"])

# ── Boss fight ────────────────────────────────────────────────

@app.route("/boss")
def boss_start():
    state = load_state()
    if not state: return redirect(url_for("create"))
    p = state["player"]

    if p["stats"]["energie"] < 5:
        return redirect(url_for("game"))

    available = [i for i,b in enumerate(BOSSES) if i not in p.get("killed_bosses",[])]
    if not available:
        body = player_header_html(p) + """<div class="wrap">
<div class="card" style="text-align:center;padding:2rem">
  <div style="font-size:2rem">🏆</div>
  <div style="font-size:1.1rem;font-weight:700;margin:.5rem 0">Tous les boss vaincus</div>
  <div style="color:#888">Tu es libéré de tes ennemis intérieurs.</div>
</div>
<a href="/game" class="btn-secondary">← Retour</a></div>"""
        return base(body)

    boss_idx = random.choice(available)
    boss = BOSSES[boss_idx]
    state["boss_fight"] = {"idx": boss_idx, "move": 0, "player_hp": 20, "boss_hp": boss["hp"], "damage_dealt": 0}
    save_state(state)
    return redirect(url_for("boss_move"))

@app.route("/boss/fight", methods=["GET","POST"])
def boss_move():
    state = load_state()
    if not state: return redirect(url_for("create"))
    p = state["player"]
    bf = state.get("boss_fight")
    if not bf: return redirect(url_for("game"))

    boss = BOSSES[bf["idx"]]

    if request.method == "POST":
        opt_idx = int(request.form.get("opt",0))
        move = boss["moves"][bf["move"]]
        opt_text, dmg, correct = move["opts"][opt_idx]

        if correct:
            bf["boss_hp"] = max(0, bf["boss_hp"]-abs(dmg))
            bf["damage_dealt"] += abs(dmg)
            feedback = (f'<div class="result-item up">✅ Bonne réponse ! -{abs(dmg)} HP au boss !</div>', True)
        else:
            atk = random.randint(3,8)
            bf["player_hp"] = max(0, bf["player_hp"]-atk)
            feedback = (f'<div class="result-item down">❌ Le boss riposte ! -{atk} HP</div>', False)

        bf["move"] += 1
        save_state(state)

        # Check end condition
        if bf["player_hp"] <= 0 or bf["move"] >= len(boss["moves"]):
            return redirect(url_for("boss_end"))

        # Show feedback then next move
        next_move = boss["moves"][bf["move"]]
        opts_html = ""
        for i,(label,_,_) in enumerate(next_move["opts"]):
            opts_html += f'<button type="submit" name="opt" value="{i}" class="choice-btn">{label}</button>'

        body = player_header_html(p) + f"""<div class="wrap">
<div class="boss-banner">
  <div class="hp-row"><span class="hp-label">👹 Boss</span>
    <div style="flex:1"><div class="bar-outer"><div class="bar-inner" style="width:{int(bf['boss_hp']/boss['hp']*100)}%;background:#e74c3c"></div></div></div>
    <span style="font-size:.8rem;color:#e74c3c">{bf['boss_hp']}/{boss['hp']}</span>
  </div>
  <div class="hp-row"><span class="hp-label">💚 Toi</span>
    <div style="flex:1"><div class="bar-outer"><div class="bar-inner" style="width:{int(bf['player_hp']/20*100)}%;background:#2ecc71"></div></div></div>
    <span style="font-size:.8rem;color:#2ecc71">{bf['player_hp']}/20</span>
  </div>
</div>
<div class="card">
  {feedback[0]}
  <div style="margin-top:.8rem;font-size:.85rem;color:#f1c40f;font-weight:700">{next_move['q']}</div>
</div>
<form method="POST">{opts_html}</form></div>"""
        return base(body, boss["name"])

    # First move
    move = boss["moves"][0]
    opts_html = ""
    for i,(label,_,_) in enumerate(move["opts"]):
        opts_html += f'<button type="submit" name="opt" value="{i}" class="choice-btn">{label}</button>'

    body = player_header_html(p) + f"""<div class="wrap">
<div class="boss-banner">
  <div class="boss-emoji">{boss['emoji']}</div>
  <div class="boss-name">{boss['name']}</div>
  <div class="boss-desc">{boss['desc']}</div>
  <div class="hp-row" style="margin-top:.8rem"><span class="hp-label">👹 Boss</span>
    <div style="flex:1"><div class="bar-outer"><div class="bar-inner" style="width:100%;background:#e74c3c"></div></div></div>
    <span style="font-size:.8rem;color:#e74c3c">{boss['hp']}/{boss['hp']}</span>
  </div>
  <div class="hp-row"><span class="hp-label">💚 Toi</span>
    <div style="flex:1"><div class="bar-outer"><div class="bar-inner" style="width:100%;background:#2ecc71"></div></div></div>
    <span style="font-size:.8rem;color:#2ecc71">20/20</span>
  </div>
</div>
<div class="card">
  <div style="font-size:.85rem;color:#f1c40f;font-weight:700">{move['q']}</div>
</div>
<form method="POST">{opts_html}</form></div>"""
    return base(body, boss["name"])

@app.route("/boss/end")
def boss_end():
    state = load_state()
    if not state: return redirect(url_for("create"))
    p = state["player"]
    bf = state.pop("boss_fight", None)
    if not bf: return redirect(url_for("game"))

    boss = BOSSES[bf["idx"]]
    p["stats"]["energie"] = max(0, p["stats"]["energie"]-5)
    win = bf["player_hp"] > 0 and (bf["boss_hp"] == 0 or bf["damage_dealt"] >= boss["hp"]//2)

    rewards_html = ""
    if win:
        for k,v in boss["reward"].items():
            if k=="xp":
                lv = add_xp(p,v)
                rewards_html += f'<div class="result-item xp-gain">✨ +{v} XP</div>'
                if lv: rewards_html += f'<div class="levelup">🎉 LEVEL UP → Niveau {lv} !</div>'
            elif k in p["stats"]:
                p["stats"][k] = min(20, p["stats"][k]+v)
                m = STAT_META[k]
                rewards_html += f'<div class="result-item up">{m["emoji"]} +{v} {m["name"]}</div>'
        p["bosses_killed"] = p.get("bosses_killed",0)+1
        if bf["idx"] not in p.get("killed_bosses",[]): p.setdefault("killed_bosses",[]).append(bf["idx"])
    else:
        p["stats"]["mental"] = max(0, p["stats"]["mental"]-1)

    quests_done = check_quests(p)
    save_state(state)

    quests_html = "".join(f'<div class="quest-done"><div class="quest-title">🏆 {q["name"]}</div></div>' for q in quests_done)

    if win:
        title_html = f'<div style="font-size:2rem">🏆</div><div style="font-size:1.1rem;font-weight:700;color:#f1c40f;margin:.5rem 0">VICTOIRE !</div><div style="color:#aaa;font-size:.85rem">"{boss["name"]}" est vaincu.</div>'
    else:
        title_html = f'<div style="font-size:2rem">💀</div><div style="font-size:1.1rem;font-weight:700;color:#e74c3c;margin:.5rem 0">Défaite</div><div style="color:#aaa;font-size:.85rem">L\'échec est un professeur. Reviens plus fort.</div>'

    body = player_header_html(p) + f"""<div class="wrap">
<div class="card" style="text-align:center">{title_html}</div>
<div class="card">{rewards_html}{quests_html}</div>
<a href="/game" class="btn-primary" style="display:block;text-align:center;padding:1rem;background:linear-gradient(135deg,#f39c12,#e74c3c);color:white;border-radius:12px;font-weight:700">← Retour au jeu</a>
</div>"""
    return base(body, "Combat terminé")

# ── Quests ────────────────────────────────────────────────────

@app.route("/quests")
def quests():
    state = load_state()
    if not state: return redirect(url_for("create"))
    p = state["player"]

    cards = ""
    for i, qd in enumerate(QUESTS_DEF):
        done = p["quest_done"][i]
        rew = "  ".join(f"+{v} {k}" for k,v in qd["reward"].items())
        cls = "done" if done else "pending"
        icon = "✅" if done else "⬜"
        cards += f"""<div class="quest-card {cls}">
  <div class="q-name">{icon} {qd['name']}</div>
  <div class="q-desc">{qd['desc']}</div>
  {'<div class="q-rew">🎁 '+rew+'</div>' if not done else ''}
</div>"""

    body = player_header_html(p) + f"""<div class="wrap">
<div style="display:flex;align-items:center;justify-content:space-between;margin:1rem 0 .5rem">
  <span style="font-weight:700">📜 Quêtes</span>
  <a href="/game" style="color:#888;font-size:.85rem">← Retour</a>
</div>
{cards}</div>"""
    return base(body, "Quêtes")

# ── Run ───────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
