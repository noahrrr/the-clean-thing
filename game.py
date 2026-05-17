#!/usr/bin/env python3
"""ASCEND — Le RPG du Développement Personnel"""

import json
import os
import random
import time
from datetime import date
from pathlib import Path

SAVE_FILE = Path.home() / ".ascend_save.json"


class C:
    RESET = "\033[0m"; BOLD = "\033[1m"; DIM = "\033[2m"
    RED = "\033[31m"; GREEN = "\033[32m"; YELLOW = "\033[33m"
    BLUE = "\033[34m"; MAGENTA = "\033[35m"; CYAN = "\033[36m"
    WHITE = "\033[37m"
    BRIGHT_RED = "\033[91m"; BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"; BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"; BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"


def clear():
    os.system("clear" if os.name != "nt" else "cls")


def slow_print(text, delay=0.03):
    for ch in text:
        print(ch, end="", flush=True)
        time.sleep(delay)
    print()


def stat_bar(val, max_val, length=18, color=C.GREEN):
    filled = int((val / max_val) * length)
    return f"{color}{'█' * filled}{'░' * (length - filled)}{C.RESET} {val}/{max_val}"


def xp_bar(cur, total, length=28):
    filled = int((cur / total) * length) if total else length
    return f"{C.BRIGHT_YELLOW}{'▓' * filled}{'░' * (length - filled)}{C.RESET} {cur}/{total}"


# ─────────────────────────── DATA ────────────────────────────

ARCHETYPES = {
    "Guerrier": {
        "emoji": "⚔️ ", "color": C.RED,
        "desc": "Force et discipline. Tu avances quoi qu'il arrive.",
        "stats": {"focus": 6, "energie": 8, "mental": 5, "discipline": 9, "sante": 7, "social": 5},
    },
    "Érudit": {
        "emoji": "📚", "color": C.BLUE,
        "desc": "La connaissance est ton arme. Tu apprends sans cesse.",
        "stats": {"focus": 9, "energie": 5, "mental": 8, "discipline": 7, "sante": 4, "social": 7},
    },
    "Athlète": {
        "emoji": "🏆", "color": C.GREEN,
        "desc": "Le corps est ton temple. L'effort te définit.",
        "stats": {"focus": 6, "energie": 9, "mental": 6, "discipline": 8, "sante": 9, "social": 7},
    },
    "Moine": {
        "emoji": "🧘", "color": C.MAGENTA,
        "desc": "La paix intérieure est ta force. Tu vois clair.",
        "stats": {"focus": 8, "energie": 6, "mental": 10, "discipline": 8, "sante": 6, "social": 5},
    },
    "Leader": {
        "emoji": "👑", "color": C.YELLOW,
        "desc": "Tu inspires les autres. Ensemble on va plus loin.",
        "stats": {"focus": 7, "energie": 7, "mental": 7, "discipline": 7, "sante": 6, "social": 10},
    },
}

STAT_META = {
    "focus":      {"emoji": "🎯", "color": C.BRIGHT_BLUE,    "name": "Focus"},
    "energie":    {"emoji": "⚡", "color": C.BRIGHT_YELLOW,  "name": "Énergie"},
    "mental":     {"emoji": "🧠", "color": C.BRIGHT_MAGENTA, "name": "Mental"},
    "discipline": {"emoji": "🔥", "color": C.BRIGHT_RED,     "name": "Discipline"},
    "sante":      {"emoji": "💪", "color": C.BRIGHT_GREEN,   "name": "Santé"},
    "social":     {"emoji": "🌐", "color": C.BRIGHT_CYAN,    "name": "Social"},
}

ACTIONS = {
    "1": {
        "name": "Deep Work",         "emoji": "💻",
        "cost": 3, "xp": 30,
        "gains": {"focus": 2, "discipline": 1},
        "desc": "2h de concentration totale. Zéro distraction.",
        "msgs": [
            "Tu coupes les notifications, tu entres dans la zone...",
            "Le temps s'efface. Seul le travail existe.",
            "Tu as accompli plus en 2h qu'une journée distraite.",
        ],
        "track": None,
    },
    "2": {
        "name": "S'entraîner",        "emoji": "🏋️ ",
        "cost": 4, "xp": 35,
        "gains": {"sante": 3, "discipline": 2, "energie": -1},
        "desc": "Entraînement physique intense.",
        "msgs": [
            "La sueur coule. Ton corps proteste.",
            "Tu dépasses ta limite du moment.",
            "Plus fort qu'hier. C'est tout ce qui compte.",
        ],
        "track": "train_today",
    },
    "3": {
        "name": "Méditer",            "emoji": "🧘",
        "cost": 1, "xp": 20,
        "gains": {"mental": 3, "focus": 1, "energie": 2},
        "desc": "20 minutes. Calme le chaos intérieur.",
        "msgs": [
            "Les pensées s'agitent au début...",
            "Doucement, le silence s'installe.",
            "Tu rouvres les yeux. Tout est plus net.",
        ],
        "track": "meditate_today",
    },
    "4": {
        "name": "Apprendre",          "emoji": "📖",
        "cost": 2, "xp": 25,
        "gains": {"focus": 1, "mental": 2, "social": 1},
        "desc": "Livre, podcast, formation. Nourris ton esprit.",
        "msgs": [
            "Tu ouvres le contenu avec intention...",
            "Une idée nouvelle s'allume dans ta tête.",
            "Une connexion inattendue se crée.",
        ],
        "track": "learn_count",
    },
    "5": {
        "name": "Se connecter",       "emoji": "🤝",
        "cost": 2, "xp": 20,
        "gains": {"social": 3, "mental": 1},
        "desc": "Appel, rencontre, donner de la valeur.",
        "msgs": [
            "Tu tends la main sans attente...",
            "La conversation prend vie.",
            "Cette relation compte. Les deux le savent.",
        ],
        "track": "connect_count",
    },
    "6": {
        "name": "Créer",              "emoji": "🎨",
        "cost": 3, "xp": 30,
        "gains": {"focus": 2, "mental": 2, "social": 1},
        "desc": "Écrire, coder, construire quelque chose.",
        "msgs": [
            "La page blanche t'attends...",
            "Les idées coulent. Tu les suis.",
            "Tu as créé quelque chose qui n'existait pas.",
        ],
        "track": None,
    },
    "7": {
        "name": "Se reposer",         "emoji": "😴",
        "cost": 0, "xp": 5,
        "gains": {"energie": 5, "sante": 1},
        "desc": "Récupérer. C'est stratégique, pas de la faiblesse.",
        "msgs": [
            "Tu lâches prise...",
            "Le corps récupère.",
            "Demain, tu seras plus fort.",
        ],
        "track": None,
    },
    "8": {
        "name": "Défi Boss",          "emoji": "⚔️ ",
        "cost": 5, "xp": 0,
        "gains": {},
        "desc": "Affronte un ennemi intérieur. Haut risque, haute récompense.",
        "msgs": [],
        "track": None,
    },
}

EVENTS = [
    {
        "title": "TENTATION DIGITALE", "color": C.YELLOW,
        "desc": "Le scroll infini t'appelle. 30 min gaspillées... ou tu résistes ?",
        "choices": [
            ("Poser le téléphone et résister",     {"discipline": 2, "focus": 1},    15, "Victoire silencieuse. Ces moments comptent."),
            ("Céder — juste 5 min (c'est ce qu'on dit)", {"discipline": -1, "energie": -1}, -5, "30 min deviennent 2h. Tu le savais."),
        ],
    },
    {
        "title": "OPPORTUNITÉ RISQUÉE", "color": C.GREEN,
        "desc": "Un projet excitant mais incertain se présente. Deadline courte.",
        "choices": [
            ("Foncer — l'inconfort est le chemin",  {"discipline": 1, "social": 2, "focus": 1}, 25, "Tu dis oui. L'aventure commence."),
            ("Refuser — pas le bon moment",         {"mental": 1},                               5,  "Tu gardes le cap actuel. Sage décision."),
        ],
    },
    {
        "title": "CRITIQUE PUBLIQUE", "color": C.RED,
        "desc": "Quelqu'un critique ton travail devant tout le monde.",
        "choices": [
            ("Répondre avec calme et faits",        {"mental": 2, "social": 1},       20, "Tu réponds avec classe. Les gens remarquent."),
            ("Ignorer et continuer d'avancer",      {"discipline": 2},                15, "Tu préserves ton énergie pour ce qui compte."),
            ("Répondre avec émotion",               {"social": -2, "mental": -1},    -10, "Tu le regrettes. Mais c'est humain."),
        ],
    },
    {
        "title": "FATIGUE SOUDAINE", "color": C.BLUE,
        "desc": "Ton énergie s'effondre sans prévenir.",
        "choices": [
            ("Push through — la discipline d'abord", {"discipline": 3, "sante": -1}, 10, "Tu forces. Ça passe."),
            ("Sieste 20 min, puis retour au travail", {"energie": 4, "sante": 1},     5, "Tu renais. Pas de honte là-dedans."),
        ],
    },
    {
        "title": "INSPIRATION À 3H DU MAT", "color": C.MAGENTA,
        "desc": "Une idée brillante surgit. Le sommeil ou l'idée ?",
        "choices": [
            ("Se lever pour noter, puis se recoucher", {"focus": 2, "mental": 2, "sante": -1}, 25, "L'idée est capturée. Valait le coup."),
            ("Se rendormir — si elle est bonne, elle reviendra", {"sante": 2, "energie": 2},   5,  "Tu choisis la récupération. Respecte ça."),
        ],
    },
    {
        "title": "FLOW STATE", "color": C.CYAN,
        "desc": "Tout coule. Tu es dans la zone. Comment tu en profites ?",
        "choices": [
            ("Pousser encore — journée légendaire", {"focus": 3, "discipline": 2, "energie": -2}, 40, "Tu te surpasses. Journée gravée."),
            ("Finir sur une note haute et s'arrêter", {"mental": 2, "sante": 1},                  20, "Sage. L'élan sera là demain."),
        ],
    },
]

BOSSES = [
    {
        "name": "Le Syndrome de l'Imposteur", "emoji": "👤", "hp": 30,
        "desc": "La voix qui dit que tu n'es pas assez bien.",
        "attacks": ["Doute paralysant", "Comparaison toxique", "Perfectionnisme"],
        "moves": [
            {
                "q": "Un gros projet. La voix dit : 'T'es pas à la hauteur.' Tu...",
                "opts": [
                    ("Agis malgré la peur — le courage c'est ça",          15, True),
                    ("Procrastines jusqu'à la dernière minute",              -5, False),
                    ("Demandes de l'aide sans honte",                        10, True),
                    ("Abandonnes pour éviter l'inconfort",                  -15, False),
                ],
            },
            {
                "q": "Tu vois quelqu'un de plus avancé que toi. Tu ressens...",
                "opts": [
                    ("De l'inspiration — leur succès prouve que c'est possible",  15, True),
                    ("De la jalousie transformée en carburant",                    10, True),
                    ("Du découragement total",                                    -10, False),
                    ("Rien — tu te compares seulement à hier",                    12, True),
                ],
            },
        ],
        "reward": {"mental": 5, "discipline": 3, "xp": 150},
    },
    {
        "name": "La Procrastination", "emoji": "⏰", "hp": 25,
        "desc": "L'ennemi silencieux de tous tes rêves.",
        "attacks": ["Demain sans fin", "Perfectionnisme paralysant", "Fausse urgence"],
        "moves": [
            {
                "q": "UNE chose importante à faire. C'est inconfortable. Tu...",
                "opts": [
                    ("5 secondes de courage et tu commences maintenant",           15, True),
                    ("Fais 10 petites tâches inutiles d'abord",                    -5, False),
                    ("Bloques 25 min sur le calendrier — là, tout de suite",       12, True),
                    ("Regardes des vidéos de motivation pendant 1h",               -8, False),
                ],
            },
            {
                "q": "Quelle est la vraie racine de ta procrastination ?",
                "opts": [
                    ("Peur de l'échec — mieux vaut ne pas essayer",               -5, False),
                    ("Peur du succès — et si tu dois maintenir ça ?",              10, True),
                    ("Manque de clarté sur le prochain pas concret",               15, True),
                    ("C'est juste de la flemme",                                   -3, False),
                ],
            },
        ],
        "reward": {"discipline": 5, "focus": 3, "xp": 120},
    },
    {
        "name": "Le Saboteur Intérieur", "emoji": "🌑", "hp": 35,
        "desc": "Le narrateur toxique qui vit dans ta tête.",
        "attacks": ["'T'es nul'", "'Ça sert à rien'", "'Les autres sont meilleurs'"],
        "moves": [
            {
                "q": "Tu échoues à quelque chose d'important. Ton réflexe ?",
                "opts": [
                    ("Analyser sans jugement — qu'est-ce que ça m'apprend ?",     15, True),
                    ("Te flageller pendant des jours",                            -10, False),
                    ("Blâmer les circonstances et passer à autre chose",           -5, False),
                    ("Voir ça comme du feedback et recalibrer",                    18, True),
                ],
            },
            {
                "q": "Complète : 'Je mérite...'",
                "opts": [
                    ("...de souffrir pour mes erreurs",                           -15, False),
                    ("...ce que je construis par mes actions",                     15, True),
                    ("...moins que les autres",                                   -12, False),
                    ("...d'être traité comme je traite ceux que j'aime",           18, True),
                ],
            },
        ],
        "reward": {"mental": 6, "social": 3, "xp": 180},
    },
]

QUESTS_DEF = [
    {
        "name": "Premier Pas",
        "desc": "Effectue ta première action",
        "check": lambda p: p["actions_done"] >= 1,
        "reward": {"xp": 50, "discipline": 2},
    },
    {
        "name": "Bâtisseur d'Habitudes",
        "desc": "Effectue 10 actions",
        "check": lambda p: p["actions_done"] >= 10,
        "reward": {"xp": 100, "focus": 3},
    },
    {
        "name": "Corps & Esprit",
        "desc": "Entraîne-toi ET médite la même journée",
        "check": lambda p: p.get("train_today") and p.get("meditate_today"),
        "reward": {"xp": 80, "sante": 3, "mental": 3},
    },
    {
        "name": "Dévoreur de Connaissance",
        "desc": "Apprends 5 fois",
        "check": lambda p: p.get("learn_count", 0) >= 5,
        "reward": {"xp": 90, "focus": 4},
    },
    {
        "name": "Slayer de Boss",
        "desc": "Vaincs ton premier boss intérieur",
        "check": lambda p: p.get("bosses_killed", 0) >= 1,
        "reward": {"xp": 200, "mental": 5},
    },
    {
        "name": "Régularité",
        "desc": "Joue 3 jours consécutifs",
        "check": lambda p: p.get("streak", 0) >= 3,
        "reward": {"xp": 150, "discipline": 5},
    },
    {
        "name": "Niveau 5",
        "desc": "Atteins le niveau 5",
        "check": lambda p: p.get("level", 1) >= 5,
        "reward": {"xp": 0, "focus": 3, "mental": 3, "discipline": 3},
    },
    {
        "name": "Connecteur",
        "desc": "Connecte-toi aux autres 3 fois",
        "check": lambda p: p.get("connect_count", 0) >= 3,
        "reward": {"xp": 70, "social": 5},
    },
]

XP_TABLE = [0, 100, 250, 450, 700, 1000, 1400, 1900, 2500, 3200, 4000]


# ─────────────────────────── GAME ────────────────────────────

class Game:
    def __init__(self):
        self.p = None
        self.quest_done = [False] * len(QUESTS_DEF)
        self.killed_bosses = set()

    # ── persistence ──────────────────────────────────────────

    def save(self):
        with open(SAVE_FILE, "w") as f:
            json.dump({"player": self.p, "quest_done": self.quest_done,
                       "killed_bosses": list(self.killed_bosses)}, f, ensure_ascii=False)

    def load(self):
        if not SAVE_FILE.exists():
            return False
        try:
            with open(SAVE_FILE) as f:
                d = json.load(f)
            self.p = d["player"]
            self.quest_done = d.get("quest_done", [False] * len(QUESTS_DEF))
            self.killed_bosses = set(d.get("killed_bosses", []))
            return True
        except Exception:
            return False

    # ── level / xp ───────────────────────────────────────────

    def level(self):
        xp = self.p["xp"]
        for i, t in enumerate(XP_TABLE):
            if xp < t:
                return max(1, i - 1)
        return len(XP_TABLE) - 1

    def xp_progress(self):
        lv = self.level()
        if lv >= len(XP_TABLE) - 1:
            return XP_TABLE[-1], XP_TABLE[-1]
        lo, hi = XP_TABLE[lv], XP_TABLE[lv + 1]
        return self.p["xp"] - lo, hi - lo

    def add_xp(self, amount):
        old = self.level()
        self.p["xp"] += amount
        new = self.level()
        self.p["level"] = new
        return new if new > old else None

    # ── quests ───────────────────────────────────────────────

    def check_quests(self):
        gained = []
        for i, qd in enumerate(QUESTS_DEF):
            if not self.quest_done[i] and qd["check"](self.p):
                self.quest_done[i] = True
                gained.append(qd)
                for k, v in qd["reward"].items():
                    if k == "xp":
                        self.add_xp(v)
                    elif k in self.p["stats"]:
                        self.p["stats"][k] = min(20, self.p["stats"][k] + v)
        return gained

    # ── display ──────────────────────────────────────────────

    def header(self):
        arch = ARCHETYPES[self.p["archetype"]]
        lv = self.level()
        xp_cur, xp_max = self.xp_progress()
        streak = self.p.get("streak", 1)
        w = 62
        print(f"\n{C.BOLD}{C.BRIGHT_WHITE}{'═' * w}{C.RESET}")
        print(f"  {arch['emoji']} {C.BOLD}{arch['color']}{self.p['name']}{C.RESET}"
              f"  •  {arch['color']}{self.p['archetype']}{C.RESET}"
              f"  •  Niv. {C.BOLD}{C.BRIGHT_YELLOW}{lv}{C.RESET}")
        print(f"  XP  {xp_bar(xp_cur, xp_max)}")
        print(f"  🔥 Streak {C.BRIGHT_RED}{streak} jour{'s' if streak > 1 else ''}{C.RESET}"
              f"   •  📅 {date.today()}")
        print(f"{C.BOLD}{C.BRIGHT_WHITE}{'═' * w}{C.RESET}")

    def stats_panel(self):
        print(f"\n  {C.BOLD}STATISTIQUES{C.RESET}   (max 20)")
        print(f"  {'─' * 52}")
        for stat, m in STAT_META.items():
            v = self.p["stats"][stat]
            print(f"  {m['emoji']} {m['color']}{m['name']:12}{C.RESET} {stat_bar(v, 20, 16, m['color'])}")
        print()

    def actions_menu(self):
        print(f"  {C.BOLD}{C.BRIGHT_CYAN}── ACTIONS ────────────────────────────────────{C.RESET}")
        for key, a in ACTIONS.items():
            cost_s = (f"{C.YELLOW}-{a['cost']}⚡{C.RESET}" if a["cost"] > 0 else f"{C.GREEN}gratuit{C.RESET}")
            print(f"  {C.BOLD}[{key}]{C.RESET} {a['emoji']} {C.WHITE}{a['name']:20}{C.RESET} {cost_s}"
                  f"  {C.DIM}{a['desc']}{C.RESET}")
        print(f"\n  {C.BOLD}[9]{C.RESET} 📜 Quêtes   {C.BOLD}[0]{C.RESET} 💾 Sauvegarder & quitter\n")

    # ── actions ──────────────────────────────────────────────

    def do_action(self, key):
        if key == "8":
            self.boss_fight()
            return

        a = ACTIONS[key]
        if self.p["stats"]["energie"] < a["cost"]:
            print(f"\n  {C.RED}⚠  Énergie insuffisante ({self.p['stats']['energie']}/{a['cost']}).{C.RESET}")
            print(f"  {C.DIM}Repose-toi d'abord.{C.RESET}")
            input(f"\n  {C.DIM}[Entrée]{C.RESET}")
            return

        clear()
        print(f"\n  {C.BOLD}{a['emoji']} {a['name'].upper()}{C.RESET}\n  {'─' * 45}")
        for msg in a["msgs"]:
            slow_print(f"  {C.DIM}{msg}{C.RESET}", 0.033)
            time.sleep(0.4)

        # apply cost
        self.p["stats"]["energie"] = max(0, self.p["stats"]["energie"] - a["cost"])

        # apply gains
        changes = []
        for stat, delta in a["gains"].items():
            if stat in self.p["stats"]:
                before = self.p["stats"][stat]
                self.p["stats"][stat] = min(20, max(0, before + delta))
                diff = self.p["stats"][stat] - before
                if diff:
                    changes.append((stat, diff))

        # tracking
        self.p["actions_done"] = self.p.get("actions_done", 0) + 1
        t = a["track"]
        if t == "train_today":
            self.p["train_today"] = True
        elif t == "meditate_today":
            self.p["meditate_today"] = True
        elif t == "learn_count":
            self.p["learn_count"] = self.p.get("learn_count", 0) + 1
        elif t == "connect_count":
            self.p["connect_count"] = self.p.get("connect_count", 0) + 1

        level_up = self.add_xp(a["xp"])

        print(f"\n  {C.BOLD}{C.GREEN}✅ RÉSULTATS{C.RESET}")
        for stat, diff in changes:
            m = STAT_META[stat]
            col = C.GREEN if diff > 0 else C.RED
            arrow = "↑" if diff > 0 else "↓"
            print(f"  {m['emoji']} {m['name']}: {col}{arrow}{abs(diff)}{C.RESET}  → {self.p['stats'][stat]}/20")
        if a["xp"]:
            print(f"  ✨ +{a['xp']} XP")
        if level_up:
            print(f"\n  {C.BOLD}{C.BRIGHT_YELLOW}🎉 LEVEL UP → Niveau {level_up} !{C.RESET}")

        if key != "7" and random.random() < 0.35:
            input(f"\n  {C.DIM}[Entrée pour continuer]{C.RESET}")
            self.random_event()
            return

        self._show_completed_quests()
        input(f"\n  {C.DIM}[Entrée pour continuer]{C.RESET}")

    def random_event(self):
        ev = random.choice(EVENTS)
        clear()
        print(f"\n  {ev['color']}{C.BOLD}⚡ ÉVÉNEMENT : {ev['title']}{C.RESET}")
        print(f"  {'─' * 52}")
        slow_print(f"\n  {ev['desc']}\n", 0.04)

        for i, (label, _, _, _) in enumerate(ev["choices"], 1):
            print(f"  [{i}] {label}")

        idx = self._pick(len(ev["choices"]))
        label, effects, xp_gain, msg = ev["choices"][idx]

        slow_print(f"\n  {C.DIM}{msg}{C.RESET}", 0.04)
        print()

        for stat, delta in effects.items():
            if stat in self.p["stats"]:
                self.p["stats"][stat] = min(20, max(0, self.p["stats"][stat] + delta))
                m = STAT_META[stat]
                col = C.GREEN if delta > 0 else C.RED
                print(f"  {m['emoji']} {m['name']}: {col}{delta:+d}{C.RESET}  → {self.p['stats'][stat]}/20")

        if xp_gain:
            lv = self.add_xp(max(0, xp_gain))
            col = C.GREEN if xp_gain > 0 else C.RED
            print(f"  ✨ {col}{xp_gain:+d} XP{C.RESET}")
            if lv:
                print(f"  {C.BRIGHT_YELLOW}🎉 LEVEL UP → Niveau {lv} !{C.RESET}")

        self._show_completed_quests()
        input(f"\n  {C.DIM}[Entrée pour continuer]{C.RESET}")

    # ── boss fight ───────────────────────────────────────────

    def boss_fight(self):
        available = [b for i, b in enumerate(BOSSES) if i not in self.killed_bosses]
        if not available:
            print(f"\n  {C.YELLOW}Tu as vaincu tous les boss. Tu es libéré.{C.RESET}")
            input(f"\n  {C.DIM}[Entrée]{C.RESET}")
            return

        if self.p["stats"]["energie"] < 5:
            print(f"\n  {C.RED}⚠  Il te faut au moins 5⚡ pour affronter un boss.{C.RESET}")
            input(f"\n  {C.DIM}[Entrée]{C.RESET}")
            return

        boss = random.choice(available)
        boss_idx = BOSSES.index(boss)
        clear()

        w = 60
        print(f"\n  {C.BOLD}{C.BRIGHT_RED}{'═' * w}{C.RESET}")
        print(f"  {C.BOLD}{C.BRIGHT_RED}          ⚔️   COMBAT DE BOSS   ⚔️{C.RESET}")
        print(f"  {C.BOLD}{C.BRIGHT_RED}{'═' * w}{C.RESET}\n")
        slow_print(f"  {boss['emoji']}  {C.BOLD}{C.RED}{boss['name'].upper()}{C.RESET}", 0.05)
        slow_print(f"  {C.DIM}« {boss['desc']} »{C.RESET}", 0.04)
        print(f"\n  Attaques : {C.RED}{', '.join(boss['attacks'])}{C.RESET}\n")
        input(f"  {C.DIM}[Entrée pour combattre]{C.RESET}")

        boss_hp = boss["hp"]
        player_hp = 20
        damage_dealt = 0

        for move in boss["moves"]:
            clear()
            print(f"\n  {C.RED}👹 {boss['name']}{C.RESET}  HP {stat_bar(boss_hp, boss['hp'], 18, C.RED)}")
            print(f"  {C.GREEN}💚 Toi     {C.RESET}  HP {stat_bar(player_hp, 20, 18, C.GREEN)}")
            print(f"\n  {'─' * 55}")
            slow_print(f"\n  {C.BRIGHT_YELLOW}❓ {move['q']}{C.RESET}\n", 0.04)

            for i, (opt, _, _) in enumerate(move["opts"], 1):
                print(f"  [{i}] {opt}")

            idx = self._pick(len(move["opts"]))
            opt_text, dmg, correct = move["opts"][idx]
            print()

            if correct:
                boss_hp = max(0, boss_hp - abs(dmg))
                damage_dealt += abs(dmg)
                slow_print(f"  {C.GREEN}✅ Bonne réponse ! Tu infliges {abs(dmg)} dégâts.{C.RESET}", 0.04)
            else:
                atk = random.randint(3, 8)
                player_hp = max(0, player_hp - atk)
                slow_print(f"  {C.RED}❌ Le boss riposte ! -{atk} HP{C.RESET}", 0.04)
            time.sleep(1.5)

        clear()
        self.p["stats"]["energie"] = max(0, self.p["stats"]["energie"] - 5)

        if player_hp > 0 and (boss_hp == 0 or damage_dealt >= boss["hp"] // 2):
            print(f"\n  {C.BOLD}{C.BRIGHT_YELLOW}🏆 VICTOIRE ! {boss['name']} est vaincu !{C.RESET}")
            slow_print(f"\n  {C.DIM}Il disparaît. Sa force était en toi depuis le début.{C.RESET}", 0.04)
            print(f"\n  {C.BOLD}RÉCOMPENSES :{C.RESET}")
            for k, v in boss["reward"].items():
                if k == "xp":
                    lv = self.add_xp(v)
                    print(f"  ✨ +{v} XP")
                    if lv:
                        print(f"  {C.BRIGHT_YELLOW}🎉 LEVEL UP → Niveau {lv} !{C.RESET}")
                elif k in self.p["stats"]:
                    self.p["stats"][k] = min(20, self.p["stats"][k] + v)
                    m = STAT_META[k]
                    print(f"  {m['emoji']} +{v} {m['name']}")
            self.p["bosses_killed"] = self.p.get("bosses_killed", 0) + 1
            self.killed_bosses.add(boss_idx)
        else:
            print(f"\n  {C.BOLD}{C.RED}💀 Défaite... Pas aujourd'hui.{C.RESET}")
            slow_print(f"\n  {C.DIM}L'échec est un professeur. Reviens plus fort.{C.RESET}", 0.04)
            self.p["stats"]["mental"] = max(0, self.p["stats"]["mental"] - 1)

        self._show_completed_quests()
        input(f"\n  {C.DIM}[Entrée pour continuer]{C.RESET}")

    # ── quests screen ─────────────────────────────────────────

    def quests_screen(self):
        clear()
        print(f"\n  {C.BOLD}{C.BRIGHT_YELLOW}📜 QUÊTES{C.RESET}\n  {'═' * 50}\n")

        pending = [(i, q) for i, q in enumerate(QUESTS_DEF) if not self.quest_done[i]]
        done    = [(i, q) for i, q in enumerate(QUESTS_DEF) if self.quest_done[i]]

        print(f"  {C.BOLD}En cours :{C.RESET}")
        if pending:
            for _, q in pending:
                rew = "  ".join(f"+{v} {k}" for k, v in q["reward"].items())
                print(f"  ⬜ {C.WHITE}{q['name']}{C.RESET} — {C.DIM}{q['desc']}{C.RESET}")
                print(f"     {C.YELLOW}{rew}{C.RESET}")
        else:
            print(f"  {C.DIM}(toutes complètes !){C.RESET}")

        if done:
            print(f"\n  {C.BOLD}Complètes :{C.RESET}")
            for _, q in done:
                print(f"  ✅ {C.DIM}{q['name']}{C.RESET}")

        input(f"\n  {C.DIM}[Entrée pour revenir]{C.RESET}")

    # ── helpers ──────────────────────────────────────────────

    def _pick(self, n):
        while True:
            try:
                v = int(input(f"\n  {C.CYAN}Ton choix (1-{n}) : {C.RESET}")) - 1
                if 0 <= v < n:
                    return v
            except (ValueError, KeyboardInterrupt):
                pass

    def _show_completed_quests(self):
        for q in self.check_quests():
            rew = "  ".join(f"+{v} {k}" for k, v in q["reward"].items())
            print(f"\n  {C.BOLD}{C.BRIGHT_GREEN}🏆 QUÊTE ACCOMPLIE : {q['name']}{C.RESET}")
            print(f"  {C.YELLOW}Récompense : {rew}{C.RESET}")

    def _update_streak(self):
        today = str(date.today())
        last = self.p.get("last_played")
        if last == today:
            return
        if last:
            from datetime import timedelta
            delta = date.today() - date.fromisoformat(last)
            self.p["streak"] = (self.p.get("streak", 1) + 1) if delta.days == 1 else 1
        else:
            self.p["streak"] = 1
        self.p["last_played"] = today
        self.p["train_today"] = False
        self.p["meditate_today"] = False

    # ── character creation ────────────────────────────────────

    def create_character(self):
        clear()
        banner = f"""
{C.BOLD}{C.BRIGHT_YELLOW}  ╔══════════════════════════════════════════════════╗
  ║       ⚡  ASCEND — Dev Personnel RPG  ⚡         ║
  ╚══════════════════════════════════════════════════╝{C.RESET}
"""
        print(banner)
        slow_print(f"  {C.DIM}Bienvenue dans le jeu de ta vie.{C.RESET}", 0.05)
        slow_print(f"  {C.DIM}Chaque action compte. Chaque jour est une chance.{C.RESET}", 0.05)
        print()

        name = input(f"  {C.CYAN}Ton nom ou pseudo : {C.RESET}").strip() or "Aventurier"

        print(f"\n  {C.BOLD}Choisis ton archétype :{C.RESET}\n")
        keys = list(ARCHETYPES.keys())
        for i, (k, a) in enumerate(ARCHETYPES.items(), 1):
            print(f"  [{i}] {a['emoji']} {a['color']}{C.BOLD}{k}{C.RESET} — {C.DIM}{a['desc']}{C.RESET}")

        idx = self._pick(len(keys))
        arch_name = keys[idx]
        arch = ARCHETYPES[arch_name]

        self.p = {
            "name": name, "archetype": arch_name,
            "xp": 0, "level": 1,
            "stats": arch["stats"].copy(),
            "actions_done": 0, "bosses_killed": 0,
            "streak": 1, "last_played": str(date.today()),
            "train_today": False, "meditate_today": False,
            "learn_count": 0, "connect_count": 0,
        }

        clear()
        print(f"\n  {arch['emoji']} {arch['color']}{C.BOLD}{name} le {arch_name}{C.RESET}\n")
        slow_print(f"  {C.DIM}{arch['desc']}{C.RESET}", 0.05)
        slow_print(f"\n  {C.DIM}Ta quête commence maintenant.{C.RESET}\n", 0.05)
        time.sleep(1.5)

    # ── main loop ─────────────────────────────────────────────

    def run(self):
        clear()
        if not self.load():
            self.create_character()
        else:
            self._update_streak()
        self.save()

        while True:
            clear()
            self.header()
            self.stats_panel()
            self.actions_menu()

            choice = input(f"  {C.CYAN}Que fais-tu ? {C.RESET}").strip()

            if choice == "0":
                self.save()
                clear()
                print(f"\n  {C.BRIGHT_GREEN}💾 Partie sauvegardée.{C.RESET}")
                slow_print(f"  {C.DIM}À demain. Continue d'avancer.\n{C.RESET}", 0.04)
                break
            elif choice == "9":
                self.quests_screen()
            elif choice in ACTIONS:
                self.do_action(choice)
                self.save()
            else:
                pass  # silently ignore invalid input


# ─────────────────────────── ENTRY ───────────────────────────

def main():
    try:
        Game().run()
    except KeyboardInterrupt:
        print(f"\n\n  {C.DIM}Session interrompue. À bientôt.{C.RESET}\n")


if __name__ == "__main__":
    main()
