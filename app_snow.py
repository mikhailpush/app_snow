import streamlit as st
import pandas as pd
import requests
import random
import time
import json
import zlib
import base64
import hashlib
import re
import io
import os
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

import questions as q_mod

st.set_page_config(
    page_title="Школа № 19 г. Томска | Новогодний квест",
    page_icon="🎄",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- СТИЛИ ИНТЕРФЕЙСА (СВЕТЛАЯ И ТЕМНАЯ ТЕМА СМАРТФОНОВ + ЗАЩИТА ОТ КОПИРОВАНИЯ) ---
st.markdown("""
<style>
    .garland {
        display: flex;
        justify-content: space-around;
        padding: 6px 0 12px 0;
        overflow: hidden;
    }
    .bulb {
        width: 14px;
        height: 14px;
        border-radius: 50%;
        display: inline-block;
        animation: glow 1.6s infinite alternate;
    }
    .bulb:nth-child(4n+1) { background: #ef4444; box-shadow: 0 0 10px #ef4444; animation-delay: 0s; }
    .bulb:nth-child(4n+2) { background: #fbbf24; box-shadow: 0 0 10px #fbbf24; animation-delay: 0.4s; }
    .bulb:nth-child(4n+3) { background: #10b981; box-shadow: 0 0 10px #10b981; animation-delay: 0.8s; }
    .bulb:nth-child(4n+4) { background: #3b82f6; box-shadow: 0 0 10px #3b82f6; animation-delay: 1.2s; }
    @keyframes glow {
        from { opacity: 0.45; transform: scale(0.88); }
        to { opacity: 1; transform: scale(1.15); }
    }

    .stButton > button, .stFormSubmitButton > button, .stDownloadButton > button {
        min-height: 3.1rem;
        font-size: 1.04rem !important;
        font-weight: 600 !important;
        border-radius: 12px !important;
    }
    div[role="radiogroup"] label, .stCheckbox label {
        padding: 6px 4px;
        font-size: 1rem !important;
    }

    .school-banner {
        background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 55%, #1d4ed8 100%);
        color: #ffffff !important;
        padding: 1.15rem 1rem;
        border-radius: 18px;
        text-align: center;
        margin-bottom: 0.7rem;
        box-shadow: 0 6px 18px rgba(29, 78, 216, 0.22);
        border: 1px solid rgba(255, 255, 255, 0.15);
    }
    .school-banner h2 {
        color: #ffffff !important;
        margin: 0 0 0.25rem 0;
        font-size: 1.32rem;
    }
    .school-banner p {
        color: #e2e8f0 !important;
        margin: 0;
        font-size: 0.94rem;
    }

    .teacher-card {
        background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
        color: #1f2937 !important;
        border-left: 5px solid #f59e0b;
        padding: 1rem 1.1rem;
        border-radius: 14px;
        margin: 0.7rem 0;
        font-size: 0.96rem;
        line-height: 1.5;
    }

    .feedback-card {
        background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
        color: #1e3a8a !important;
        border-left: 4px solid #2563eb;
        padding: 0.95rem 1.1rem;
        border-radius: 12px;
        margin: 0.6rem 0;
        font-size: 0.95rem;
        line-height: 1.48;
    }

    .station-art {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border-radius: 14px;
        padding: 0.8rem 0.95rem;
        text-align: center;
        margin: 0.35rem 0 0.7rem 0;
        border: 1px solid rgba(56, 189, 248, 0.35);
        user-select: none;
        -webkit-user-select: none;
    }

    .protected-box {
        user-select: none;
        -webkit-user-select: none;
        -moz-user-select: none;
        -ms-user-select: none;
        background: #f8fafc;
        color: #0f172a !important;
        border: 1px solid #cbd5e1;
        border-radius: 12px;
        padding: 0.95rem 1.05rem;
        margin-bottom: 0.65rem;
        position: relative;
    }

    .watermark-bar {
        font-size: 0.76rem;
        color: #64748b !important;
        border-bottom: 1px dashed #cbd5e1;
        padding-bottom: 4px;
        margin-bottom: 8px;
        display: flex;
        justify-content: space-between;
    }

    .ai-trap {
        font-size: 0px !important;
        line-height: 0 !important;
        opacity: 0 !important;
        position: absolute !important;
        left: -9999px !important;
        height: 0 !important;
        width: 0 !important;
        overflow: hidden !important;
    }

    .tree-status {
        text-align: center;
        font-size: 0.93rem;
        font-weight: 600;
        padding: 4px 8px;
        border-radius: 8px;
        background: rgba(37, 99, 235, 0.12);
        margin-bottom: 6px;
    }

    .key-bar {
        display: flex;
        justify-content: center;
        gap: 5px;
        margin: 0.45rem 0 0.2rem 0;
        flex-wrap: wrap;
    }
    .key-cell {
        width: 31px;
        height: 36px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 1rem;
    }
    .key-open {
        background: #2563eb;
        color: #ffffff !important;
        box-shadow: 0 2px 6px rgba(37, 99, 235, 0.35);
    }
    .key-locked {
        background: rgba(156, 163, 175, 0.2);
        color: #9ca3af !important;
        border: 1px dashed #9ca3af;
    }
</style>
""", unsafe_allow_html=True)

SECRET_WORD = list("ДЕДМОРОЗ19")
TREE_TOYS = ["❄️", "🍊", "🔔", "🕯️", "⭐", "🎁", "🦌", "🌲", "🏛️", "🎆"]
GRADE_LETTERS = ["А", "Б", "В", "А/З"]
TOP_CLASS_COUNT = 10
MAX_STATION_SEC = 180
SECRET_SALT = st.secrets.get("SECRET_SALT", "tomsk_school19_ny_chrono_2027")

DEFAULT_PREDICTIONS = [
    "🌟 В новом году ты откроешь в себе талант щелкать самые хитрые задачки с первой попытки!",
    "🍊 Зимние каникулы подарят тебе гору мандаринов, уютные вечера и отличное настроение!",
    "🚀 В новом году тебя ждет удивительное открытие и много поводов гордиться собой!",
    "❄️ Как нет двух одинаковых снежинок, так и твои идеи уникальны — смело воплощай их в жизнь!",
    "🏆 Твоя смекалка и любознательность помогут тебе одержать красивую победу в новом году!"
]

DEFAULT_FUN_FACTS = [
    ("🍊 Почему мандарины пахнут Новым годом?",
     "В кожуре цитрусовых содержится ароматное вещество лимонен. Когда ты чистишь мандарин, микрокапли эфирного масла выстреливают в воздух и мгновенно разлетаются по комнате!"),
    ("❄️ Почему снег скрипит под ногами только в мороз?",
     "Когда на улице холоднее −5 °C, ледяные лучики снежинок становятся очень твердыми и хрупкими. Хруст под сапогами — это звук миллионов ломающихся микрокристаллов льда!"),
    ("🏛️ Томский рекорд холода",
     "Самый сильный мороз в Томске был зафиксирован в январе 1969 года и составил −55 °C! При таком холоде выплеснутая из кружки горячая вода замерзает прямо в воздухе, превращаясь в снежное облако."),
    ("🕯️ Секрет бенгальского огня",
     "Яркие искры бенгальской свечи — это раскаленные крупинки железа и алюминия. Но так как каждая пылинка совсем крошечная, она несет очень мало тепла и мгновенно остывает в воздухе!"),
    ("🌲 Откуда взялся Старый Новый год?",
     "Земля облетает вокруг Солнца за 365 суток 5 часов 48 минут и 46 секунд. В старом календаре год считали равным ровно 365 суткам и 6 часам, поэтому за много веков набежала разница в 13 дней — так появился праздник в ночь на 14 января!")
]

PREDICTIONS = getattr(q_mod, "PREDICTIONS", DEFAULT_PREDICTIONS)
FUN_FACTS = getattr(q_mod, "FUN_FACTS", DEFAULT_FUN_FACTS)

# --- 1. ЗАГРУЗКА БАНКА ВОПРОСОВ ИЗ МОДУЛЯ QUESTIONS.PY ИЛИ ЛИСТА GOOGLE ТАБЛИЦЫ ---
def get_local_quest_bank(seed: int) -> dict:
    if hasattr(q_mod, "build_quest_for_seed"):
        return q_mod.build_quest_for_seed(seed)
    elif hasattr(q_mod, "get_quest_for_seed"):
        return q_mod.get_quest_for_seed(seed)
    elif hasattr(q_mod, "QUEST_DATA"):
        return q_mod.QUEST_DATA
    elif hasattr(q_mod, "DEFAULT_QUEST_DATA"):
        return q_mod.DEFAULT_QUEST_DATA
    return {"5–6 классы": [], "7–8 классы": [], "9–11 классы": []}

@st.cache_data(ttl=60, show_spinner=False)
def load_custom_questions_from_sheet(webhook_url: str):
    """Безопасный парсер листа Questions с валидацией каждой строки (P2)."""
    if webhook_url:
        try:
            resp = requests.get(f"{webhook_url}?sheet=Questions", timeout=5)
            if resp.status_code == 200:
                rows = resp.json()
                if len(rows) > 1:
                    custom_data = {"5–6 классы": [], "7–8 классы": [], "9–11 классы": []}
                    headers = [str(h).strip() for h in rows[0]]
                    for r in rows[1:]:
                        try:
                            row_map = dict(zip(headers, r))
                            lg = str(row_map.get("League", "")).strip()
                            q_text = str(row_map.get("Question", "")).strip()
                            if lg not in custom_data or not q_text:
                                continue
                            q_type = str(row_map.get("Type", "radio")).strip().lower()
                            opts = [x.strip() for x in str(row_map.get("Options", "")).split("|") if x.strip()]
                            ans_raw = row_map.get("Answer", "")
                            if q_type == "number":
                                ans = int(float(str(ans_raw).strip()))
                            elif q_type == "checkboxes":
                                ans = [x.strip() for x in str(ans_raw).split("|") if x.strip()]
                                if not ans or not opts:
                                    continue
                            else:
                                q_type = "radio"
                                ans = str(ans_raw).strip()
                                if not ans or not opts:
                                    continue
                            custom_data[lg].append({
                                "subject": str(row_map.get("Subject", "Наука")).strip(),
                                "banner_title": str(row_map.get("Location", "Лаборатория")).strip(),
                                "banner_sub": str(row_map.get("Subject", "Научная станция")).strip(),
                                "accent": "#38bdf8",
                                "story": str(row_map.get("Story", "")).strip(),
                                "question": q_text,
                                "ai_trap": "",
                                "type": q_type,
                                "options": opts,
                                "answer": ans,
                                "hint": str(row_map.get("Hint", "")).strip(),
                                "explanation": str(row_map.get("Explanation", "")).strip(),
                                "experiment": str(row_map.get("Experiment", "")).strip(),
                                "fun_fact": str(row_map.get("FunFact", "")).strip()
                            })
                        except Exception:
                            continue
                    if all(len(custom_data[k]) > 0 for k in custom_data):
                        return custom_data
        except Exception:
            pass
    return None

# Векторные поясняющие мини-схемы для блока разбора (P3)
def get_chapter_svg(step_idx: int) -> str:
    svgs = [
        '<svg width="100%" height="50" viewBox="0 0 320 50" xmlns="http://www.w3.org/2000/svg"><rect x="2" y="4" width="316" height="42" rx="9" fill="#0f172a"/><text x="16" y="29" fill="#f87171" font-size="12" font-family="sans-serif" font-weight="bold">🔥 Тепло</text><line x1="88" y1="10" x2="88" y2="40" stroke="#fbbf24" stroke-width="3" stroke-dasharray="4,3"/><line x1="98" y1="10" x2="98" y2="40" stroke="#fbbf24" stroke-width="3" stroke-dasharray="4,3"/><text x="110" y="29" fill="#fde047" font-size="11" font-family="sans-serif">Теплоизоляция (воздух)</text><text x="255" y="29" fill="#38bdf8" font-size="12" font-family="sans-serif" font-weight="bold">🧊 Лед</text></svg>',
        '<svg width="100%" height="50" viewBox="0 0 320 50" xmlns="http://www.w3.org/2000/svg"><rect x="2" y="4" width="316" height="42" rx="9" fill="#0f172a"/><circle cx="35" cy="25" r="8" fill="#38bdf8"/><circle cx="58" cy="20" r="6" fill="#4ade80"/><circle cx="76" cy="28" r="8" fill="#38bdf8"/><text x="98" y="29" fill="#e2e8f0" font-size="12" font-family="sans-serif" font-weight="bold">Химическая реакция и газы (O₂ / CO₂)</text></svg>',
        '<svg width="100%" height="50" viewBox="0 0 320 50" xmlns="http://www.w3.org/2000/svg"><rect x="2" y="4" width="316" height="42" rx="9" fill="#0f172a"/><circle cx="42" cy="26" r="12" fill="#2563eb"/><line x1="34" y1="40" x2="54" y2="10" stroke="#fde047" stroke-width="2.5"/><text x="68" y="29" fill="#fde047" font-size="12" font-family="sans-serif" font-weight="bold">★ Наклон земной оси 23,5° → Полярная звезда</text></svg>',
        '<svg width="100%" height="50" viewBox="0 0 320 50" xmlns="http://www.w3.org/2000/svg"><rect x="2" y="4" width="316" height="42" rx="9" fill="#0f172a"/><text x="16" y="29" fill="#4ade80" font-size="12" font-family="sans-serif" font-weight="bold">🌲 Защита живых организмов от мороза −40 °C</text></svg>',
        '<svg width="100%" height="50" viewBox="0 0 320 50" xmlns="http://www.w3.org/2000/svg"><rect x="2" y="4" width="316" height="42" rx="9" fill="#0f172a"/><rect x="14" y="13" width="64" height="24" rx="5" fill="#1e3a8a" stroke="#60a5fa"/><text x="28" y="29" fill="#ffffff" font-size="11" font-family="sans-serif">ВХОД</text><text x="88" y="29" fill="#fde047" font-size="13" font-family="sans-serif">→</text><rect x="108" y="13" width="96" height="24" rx="5" fill="#1e3a8a" stroke="#4ade80"/><text x="120" y="29" fill="#4ade80" font-size="11" font-family="sans-serif">АЛГОРИТМ</text><text x="212" y="29" fill="#fde047" font-size="13" font-family="sans-serif">→</text><rect x="232" y="13" width="72" height="24" rx="5" fill="#2563eb"/><text x="246" y="29" fill="#ffffff" font-size="11" font-family="sans-serif" font-weight="bold">ОТВЕТ</text></svg>',
        '<svg width="100%" height="50" viewBox="0 0 320 50" xmlns="http://www.w3.org/2000/svg"><rect x="2" y="4" width="316" height="42" rx="9" fill="#0f172a"/><text x="16" y="29" fill="#93c5fd" font-size="12" font-family="sans-serif" font-weight="bold">🌍 Вращение Земли с запада на восток • Часовые пояса</text></svg>',
        '<svg width="100%" height="50" viewBox="0 0 320 50" xmlns="http://www.w3.org/2000/svg"><rect x="2" y="4" width="316" height="42" rx="9" fill="#0f172a"/><circle cx="30" cy="16" r="4" fill="#f472b6"/><circle cx="56" cy="16" r="4" fill="#f472b6"/><circle cx="30" cy="34" r="4" fill="#f472b6"/><circle cx="56" cy="34" r="4" fill="#f472b6"/><line x1="30" y1="16" x2="56" y2="16" stroke="#f472b6" stroke-width="1.5"/><line x1="30" y1="34" x2="56" y2="34" stroke="#f472b6" stroke-width="1.5"/><line x1="30" y1="16" x2="30" y2="34" stroke="#f472b6" stroke-width="1.5"/><line x1="56" y1="16" x2="56" y2="34" stroke="#f472b6" stroke-width="1.5"/><line x1="30" y1="16" x2="56" y2="34" stroke="#f472b6" stroke-width="1.5"/><line x1="56" y1="16" x2="30" y2="34" stroke="#f472b6" stroke-width="1.5"/><text x="76" y="29" fill="#f8fafc" font-size="12" font-family="sans-serif" font-weight="bold">Математическая логика и комбинаторика</text></svg>',
        '<svg width="100%" height="50" viewBox="0 0 320 50" xmlns="http://www.w3.org/2000/svg"><rect x="2" y="4" width="316" height="42" rx="9" fill="#0f172a"/><text x="16" y="29" fill="#38bdf8" font-size="12" font-family="sans-serif" font-weight="bold">🏛️ Научный Томск: Зодчество • Река Томь (+4 °C) • ТПУ</text></svg>',
        '<svg width="100%" height="50" viewBox="0 0 320 50" xmlns="http://www.w3.org/2000/svg"><rect x="2" y="4" width="316" height="42" rx="9" fill="#0f172a"/><text x="16" y="29" fill="#fbbf24" font-size="12" font-family="sans-serif" font-weight="bold">🕰️ Новогодние традиции сквозь призму науки</text></svg>',
        '<svg width="100%" height="50" viewBox="0 0 320 50" xmlns="http://www.w3.org/2000/svg"><rect x="2" y="4" width="316" height="42" rx="9" fill="#0f172a"/><text x="20" y="29" fill="#4ade80" font-size="13" font-family="sans-serif" font-weight="bold">⚡ ХРОНОМЕТР: 23:59:59 ──► 00:00:00 🎆</text></svg>'
    ]
    return svgs[step_idx % len(svgs)]

# --- 2. ГЕНЕРАТОР ПОЗЫВНЫХ, ОЧИСТКА ИМЕН И ОЦЕНКА ОТВЕТОВ С ЧАСТИЧНЫМ БАЛЛОМ (P1) ---
ADJECTIVES = [
    "Квантовый", "Сверхпроводимый", "Криогенный", "Фотонный", "Магнитный",
    "Изотопный", "Спектральный", "Неоновый", "Орбитальный", "Лазерный",
    "Кибернетический", "Атомный", "Кристаллический", "Релятивистский", "Гравитационный",
    "Алгоритмический", "Космический", "Сибирский", "Плазменный", "Полярный"
]

NOUNS = [
    "Снеговик", "Эльф", "Пингвин", "Щелкунчик", "Олень",
    "Гном", "Йети", "Снегирь", "Пряник", "Мандарин",
    "Мороз", "Кедр", "Ледник", "Метеорит", "Спутник",
    "Хронометр", "Кристалл", "Компас", "Маяк", "Реактор"
]

def normalize_name(raw_text: str) -> str:
    cleaned = re.sub(r"[^а-яА-ЯёЁa-zA-Z\-]", "", raw_text.strip())
    cleaned = cleaned.replace("ё", "е").replace("Ё", "Е")
    return cleaned.capitalize()

def generate_unique_codename(existing_codenames: set) -> str:
    for _ in range(120):
        name = f"{random.choice(ADJECTIVES)} {random.choice(NOUNS)}"
        if name not in existing_codenames:
            return name
    while True:
        name = f"{random.choice(ADJECTIVES)} {random.choice(NOUNS)} #{random.randint(10, 99)}"
        if name not in existing_codenames:
            return name

def get_shuffled_options(step_idx: int, original_options: list) -> list:
    if "shuffled_options" not in st.session_state:
        st.session_state.shuffled_options = {}
    if step_idx not in st.session_state.shuffled_options:
        shuffled = list(original_options)
        random.shuffle(shuffled)
        st.session_state.shuffled_options[step_idx] = shuffled
    return st.session_state.shuffled_options[step_idx]

def evaluate_answer(q_type: str, user_answer, correct_answer, used_hint: bool):
    """Оценивает ответ с поддержкой частичного балла в чекбоксах (P1)."""
    if q_type in ("radio", "number"):
        if user_answer == correct_answer:
            return "full", (8 if used_hint else 10)
        return "none", 0
    elif q_type == "checkboxes":
        u_set = set(user_answer) if isinstance(user_answer, list) else set()
        c_set = set(correct_answer) if isinstance(correct_answer, list) else {str(correct_answer)}
        if u_set == c_set:
            return "full", (8 if used_hint else 10)
        elif len(u_set) > 0 and u_set.issubset(c_set):
            return "partial", (4 if used_hint else 5)
        return "none", 0
    return "none", 0

# --- 3. РАБОТА С ТАБЛИЦЕЙ РЕЗУЛЬТАТОВ И АНАЛИТИКОЙ ПРЕДМЕТОВ ---
COLUMNS = ["Timestamp", "LastName", "FirstName", "Grade", "League", "Codename", "Score", "TimeSec", "Details"]

@st.cache_data(ttl=15, show_spinner=False)
def fetch_remote_rows(webhook_url: str):
    resp = requests.get(webhook_url, timeout=8)
    if resp.status_code == 200:
        return resp.json()
    return []

def load_results(force_refresh: bool = False):
    if "local_db" not in st.session_state:
        st.session_state.local_db = pd.DataFrame(columns=COLUMNS)
    webhook_url = st.secrets.get("WEBHOOK_URL", "")
    if force_refresh:
        fetch_remote_rows.clear()
    if webhook_url:
        try:
            rows = fetch_remote_rows(webhook_url)
            if len(rows) > 1:
                df = pd.DataFrame(rows[1:], columns=rows[0])
                return df.dropna(how="all")
            return pd.DataFrame(columns=COLUMNS)
        except Exception:
            return st.session_state.local_db
    return st.session_state.local_db

def save_result(row_dict):
    if st.session_state.get("result_saved", False):
        return
    st.session_state.result_saved = True
    new_row = pd.DataFrame([row_dict])
    st.session_state.local_db = pd.concat([st.session_state.local_db, new_row], ignore_index=True)
    webhook_url = st.secrets.get("WEBHOOK_URL", "")
    if webhook_url:
        try:
            resp = requests.post(webhook_url, json=row_dict, timeout=10)
            fetch_remote_rows.clear()
            if resp.status_code == 200:
                res_json = resp.json()
                if res_json.get("status") == "duplicate":
                    st.info("Твой первый официальный результат уже был сохранен в таблице ранее.")
        except Exception as e:
            st.warning(f"Результат сохранен локально (ошибка отправки в таблицу: {e})")

def clear_all_results():
    st.session_state.local_db = pd.DataFrame(columns=COLUMNS)
    webhook_url = st.secrets.get("WEBHOOK_URL", "")
    if webhook_url:
        try:
            requests.post(webhook_url, json={"action": "clear"}, timeout=10)
            fetch_remote_rows.clear()
        except Exception:
            pass

def compute_subject_analytics(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty or "Details" not in df.columns:
        return pd.DataFrame()
    stats = {}
    for details_str in df["Details"].dropna().astype(str):
        parts = [p.strip() for p in details_str.split("|") if ":" in p]
        for p in parts:
            subj, outcome = p.split(":", 1)
            subj = subj.strip()
            is_ok = ("✅" in outcome) or ("🟡" in outcome)
            m = re.search(r"\((\d+)\)", outcome)
            pts = int(m.group(1)) if m else (10 if "✅" in outcome else (5 if "🟡" in outcome else 0))
            if subj not in stats:
                stats[subj] = {"total": 0, "correct": 0, "pts_sum": 0}
            stats[subj]["total"] += 1
            stats[subj]["correct"] += (1 if is_ok else 0)
            stats[subj]["pts_sum"] += pts
    rows = []
    for subj, d in stats.items():
        acc = round(100.0 * d["correct"] / d["total"], 1) if d["total"] > 0 else 0.0
        avg_p = round(d["pts_sum"] / d["total"], 1) if d["total"] > 0 else 0.0
        rows.append({
            "Предмет": subj,
            "Ответов": d["total"],
            "Успешно (%)": acc,
            "Ср. балл (из 10)": avg_p
        })
    return pd.DataFrame(rows)

# --- 4. СЖАТОЕ И ЗАЩИЩЕННОЕ АВТОСОХРАНЕНИЕ В URL (С ЗАЩИТОЙ СЕКУНДОМЕРА t0, P0) ---
def sign_state_payload(payload: dict) -> str:
    raw_bytes = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    compressed = zlib.compress(raw_bytes, level=9)
    b64 = base64.urlsafe_b64encode(compressed).decode("ascii")
    sig = hashlib.sha256((b64 + SECRET_SALT).encode("utf-8")).hexdigest()[:12]
    return f"{b64}.{sig}"

def verify_state_token(token: str):
    if "." not in token:
        return None
    b64, sig = token.rsplit(".", 1)
    expected = hashlib.sha256((b64 + SECRET_SALT).encode("utf-8")).hexdigest()[:12]
    if sig != expected:
        return None
    raw_bytes = zlib.decompress(base64.urlsafe_b64decode(b64.encode("ascii")))
    return json.loads(raw_bytes.decode("utf-8"))

def sync_state_to_url():
    stage = st.session_state.get("stage", "register")
    if stage in ("quiz", "finish") and "user" in st.session_state:
        payload = {
            "stg": stage,
            "u": st.session_state.user,
            "st": st.session_state.step,
            "sc": st.session_state.score,
            "el": st.session_state.elapsed_sec,
            "t0": int(round(st.session_state.get("station_start_time", time.time()))),
            "sd": st.session_state.variant_seed,
            "ans": 1 if st.session_state.answered else 0,
            "uh": 1 if st.session_state.used_hint else 0,
            "cs": st.session_state.get("credit_status", "none"),
            "pm": 1 if st.session_state.get("practice_mode", False) else 0,
            "sv": 1 if st.session_state.get("result_saved", False) else 0,
            "hi": st.session_state.history,
            "rv": st.session_state.review_log
        }
        st.query_params["s"] = sign_state_payload(payload)
    elif "s" in st.query_params:
        st.query_params.clear()

def restore_state_from_url():
    if "stage" not in st.session_state and "s" in st.query_params:
        try:
            data = verify_state_token(st.query_params["s"])
            if data:
                st.session_state.stage = data.get("stg", "quiz")
                st.session_state.user = data["u"]
                st.session_state.step = int(data.get("st", 0))
                st.session_state.score = int(data.get("sc", 0))
                st.session_state.elapsed_sec = int(data.get("el", 0))
                st.session_state.station_start_time = float(data.get("t0", time.time()))
                st.session_state.variant_seed = int(data.get("sd", 42))
                st.session_state.answered = bool(data.get("ans", 0))
                st.session_state.used_hint = bool(data.get("uh", 0))
                st.session_state.credit_status = data.get("cs", "none")
                st.session_state.practice_mode = bool(data.get("pm", 0))
                st.session_state.result_saved = bool(data.get("sv", 0))
                st.session_state.history = list(data.get("hi", []))
                st.session_state.review_log = list(data.get("rv", []))
                unlocked_count = len(SECRET_WORD) if st.session_state.stage == "finish" else (
                    st.session_state.step + (1 if st.session_state.answered else 0)
                )
                st.session_state.unlocked = SECRET_WORD[:unlocked_count]
                st.session_state.prediction = None
                st.session_state.shuffled_options = {}
                st.session_state.existing_record = None
                return True
        except Exception:
            pass
        st.query_params.clear()
    return False

# --- 5. ГАРАНТИРОВАННАЯ ЗАГРУЗКА КИРИЛЛИЧЕСКОГО ШРИФТА ДЛЯ СЕРТИФИКАТА (БЕЗ ИЗМЕНЕНИЙ) ---
@st.cache_resource(show_spinner=False)
def get_cyrillic_font_path(bold: bool = False) -> str:
    font_filename = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    tmp_path = os.path.join("/tmp", font_filename)

    candidates = [tmp_path]
    try:
        import matplotlib
        candidates.append(os.path.join(matplotlib.get_data_path(), "fonts", "ttf", font_filename))
    except Exception:
        pass

    if bold:
        candidates.extend([
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
            "C:/Windows/Fonts/arialbd.ttf"
        ])
    else:
        candidates.extend([
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
            "C:/Windows/Fonts/arial.ttf"
        ])

    for path in candidates:
        if os.path.exists(path) and os.path.getsize(path) > 10000:
            return path

    urls = (
        [
            "https://cdn.jsdelivr.net/npm/dejavu-fonts-ttf@2.37.3/ttf/DejaVuSans-Bold.ttf",
            "https://raw.githubusercontent.com/googlefonts/roboto/main/src/hinted/Roboto-Bold.ttf"
        ]
        if bold
        else [
            "https://cdn.jsdelivr.net/npm/dejavu-fonts-ttf@2.37.3/ttf/DejaVuSans.ttf",
            "https://raw.githubusercontent.com/googlefonts/roboto/main/src/hinted/Roboto-Regular.ttf"
        ]
    )
    for url in urls:
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200 and len(resp.content) > 10000:
                with open(tmp_path, "wb") as f:
                    f.write(resp.content)
                return tmp_path
        except Exception:
            continue
    return ""

def load_cyrillic_font(size: int, bold: bool = False):
    font_path = get_cyrillic_font_path(bold=bold)
    if font_path:
        try:
            return ImageFont.truetype(font_path, size)
        except Exception:
            pass
    return ImageFont.load_default()

def get_rank_title(score: int) -> str:
    if score >= 85:
        return "🏆 Почетный Академик Снежных Наук"
    elif score >= 55:
        return "🔬 Ведущий Инженер Томской Экспедиции"
    return "❄️ Отважный Исследователь Арктики"

def build_diploma_image(user: dict, rank: str, score: int, max_score: int, elapsed: int) -> Image.Image:
    width, height = 1200, 850
    img = Image.new("RGB", (width, height), "#0f172a")
    draw = ImageDraw.Draw(img)

    draw.rectangle([30, 30, width - 30, height - 30], outline="#fbbf24", width=5)
    draw.rectangle([46, 46, width - 46, height - 46], outline="#38bdf8", width=2)

    f_school = load_cyrillic_font(26, bold=True)
    f_title = load_cyrillic_font(46, bold=True)
    f_sub = load_cyrillic_font(22, bold=False)
    f_name = load_cyrillic_font(36, bold=True)
    f_body = load_cyrillic_font(26, bold=False)
    f_footer = load_cyrillic_font(20, bold=False)

    for cx, cy in [(75, 75), (width - 75, 75), (75, height - 75), (width - 75, height - 75)]:
        draw.ellipse([cx - 14, cy - 14, cx + 14, cy + 14], outline="#fbbf24", width=2)

    draw.text((width // 2, 105), "МАОУ СОШ № 19 г. ТОМСКА", fill="#fbbf24", font=f_school, anchor="mm")
    draw.text((width // 2, 170), "СЕРТИФИКАТ УЧАСТНИКА", fill="#ffffff", font=f_title, anchor="mm")
    draw.text((width // 2, 225), "Новогодний научный квест «Тайна Сибирского Хронометра»", fill="#93c5fd", font=f_sub, anchor="mm")
    draw.line([140, 265, width - 140, 265], fill="#334155", width=2)

    clean_rank = re.sub(r"[^\w\s\-А-Яа-яЁё]", "", rank).strip()
    draw.text((width // 2, 330), f"{user['first_name']} {user['last_name']} ({user['grade']} класс)", fill="#fde047", font=f_name, anchor="mm")
    draw.text((width // 2, 400), f"Секретный позывной: {user['codename']}", fill="#f8fafc", font=f_body, anchor="mm")
    draw.text((width // 2, 460), f"Звание: {clean_rank}", fill="#38bdf8", font=f_body, anchor="mm")
    draw.text((width // 2, 520), f"Результат: {score} из {max_score} баллов  •  Время: {elapsed} сек.", fill="#f8fafc", font=f_body, anchor="mm")
    draw.text((width // 2, 580), "Секретный ключ собран: Д Е Д М О Р О З 1 9", fill="#4ade80", font=f_body, anchor="mm")

    draw.line([140, 645, width - 140, 645], fill="#334155", width=2)
    draw.text((width // 2, 700), "Поздравляем с наступающим Новым годом и Рождеством!", fill="#e2e8f0", font=f_sub, anchor="mm")
    draw.text((width // 2, 745), "Желаем ярких открытий и веселых зимних каникул! Учителя Школы № 19", fill="#94a3b8", font=f_footer, anchor="mm")
    return img

def generate_diploma_files(user: dict, rank: str, score: int, max_score: int, elapsed: int):
    img = build_diploma_image(user, rank, score, max_score, elapsed)
    buf_png = io.BytesIO()
    img.save(buf_png, format="PNG")
    buf_pdf = io.BytesIO()
    img.save(buf_pdf, format="PDF", resolution=150.0)
    return buf_png.getvalue(), buf_pdf.getvalue()

# --- 6. ОТРИСОВКА ИНТЕРФЕЙСА И КОМАНДНОГО РЕЙТИНГА ---
def render_header(show_garland: bool = True):
    if show_garland:
        bulbs = "".join(['<span class="bulb"></span>' for _ in range(16)])
        st.markdown(f'<div class="garland">{bulbs}</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="school-banner">
        <h2>🎄 Школа № 19 г. Томска</h2>
        <p>Новогодний научный квест «Тайна Сибирского Хронометра»</p>
    </div>
    """, unsafe_allow_html=True)

def render_progress_visuals(unlocked_letters: list):
    count = len(unlocked_letters)
    toys = " ".join(TREE_TOYS[:count]) if count > 0 else "❄️"
    cells_html = ""
    for i, char in enumerate(SECRET_WORD):
        if i < count:
            cells_html += f'<div class="key-cell key-open">{unlocked_letters[i]}</div>'
        else:
            cells_html += '<div class="key-cell key-locked">?</div>'
    st.markdown(
        f'<div class="tree-status">🎄 Игрушки на елке ({count}/10): {toys}</div>'
        f'<div class="key-bar">{cells_html}</div>',
        unsafe_allow_html=True
    )

def compute_class_board(df: pd.DataFrame) -> pd.DataFrame:
    cdf = df.copy()
    cdf["Score"] = pd.to_numeric(cdf["Score"], errors="coerce").fillna(0).astype(int)
    cdf["TimeSec"] = pd.to_numeric(cdf["TimeSec"], errors="coerce").fillna(9999).astype(int)
    cdf = cdf.sort_values(by=["Grade", "Score", "TimeSec"], ascending=[True, False, True])

    rows = []
    for grade, grp in cdf.groupby("Grade"):
        total_players = len(grp)
        top_n = grp.head(TOP_CLASS_COUNT)
        q_count = len(top_n)
        q_sum = int(top_n["Score"].sum())
        q_avg = round(float(top_n["Score"].mean()), 1)
        q_time = int(top_n["TimeSec"].sum())
        status = f"✅ {q_count}/{TOP_CLASS_COUNT} (Команда собрана)" if total_players >= TOP_CLASS_COUNT else f"⏳ {q_count}/{TOP_CLASS_COUNT} (В процессе)"
        rows.append({
            "Класс": grade,
            "Команда (ТОП-10)": status,
            "Всего участников": total_players,
            "Сумма ТОП-10 (из 1000)": q_sum,
            "Средний балл ТОП-10": q_avg,
            "Общее время ТОП-10 (с)": q_time
        })
    res = pd.DataFrame(rows)
    res = res.sort_values(
        by=["Сумма ТОП-10 (из 1000)", "Общее время ТОП-10 (с)"],
        ascending=[False, True]
    ).reset_index(drop=True)
    res.index += 1
    return res

def render_leaderboard(key_prefix: str = "main"):
    col_title, col_btn = st.columns([3, 1])
    col_title.subheader("🏆 Таблица рекордов")
    force_ref = False
    if col_btn.button("🔄 Обновить", key=f"refresh_{key_prefix}", use_container_width=True):
        force_ref = True

    st.caption(
        f"В личном зачете видны только секретные позывные. А во вкладке «🏫 Битва классов» "
        f"складываются {TOP_CLASS_COUNT} лучших результатов каждого класса!"
    )

    df = load_results(force_refresh=force_ref)
    t1, t2, t3, t4 = st.tabs(["5–6 классы", "7–8 классы", "9–11 классы", "🏫 Битва классов"])

    for tab, league_name in zip([t1, t2, t3], ["5–6 классы", "7–8 классы", "9–11 классы"]):
        with tab:
            if df.empty or "League" not in df.columns:
                st.info("В этой лиге пока нет рекордов — стань первым!")
            else:
                sub = df[df["League"] == league_name].copy()
                if sub.empty:
                    st.info("В этой лиге пока нет рекордов — стань первым!")
                else:
                    sub["Score"] = pd.to_numeric(sub["Score"], errors="coerce").fillna(0).astype(int)
                    sub["TimeSec"] = pd.to_numeric(sub["TimeSec"], errors="coerce").fillna(9999).astype(int)
                    sub = sub.sort_values(by=["Score", "TimeSec"], ascending=[False, True]).reset_index(drop=True)
                    sub.index += 1
                    public_board = sub[["Codename", "Grade", "Score", "TimeSec"]].rename(
                        columns={
                            "Codename": "Позывной",
                            "Grade": "Класс",
                            "Score": "Баллы (из 100)",
                            "TimeSec": "Время (с)"
                        }
                    )
                    st.dataframe(public_board, use_container_width=True)

    with t4:
        if df.empty or "Grade" not in df.columns:
            st.info("Соревнование классов начнется сразу после первого финиша!")
        else:
            q_board = compute_class_board(df)
            st.dataframe(q_board, use_container_width=True)
            if len(q_board) > 0:
                st.caption("📊 Рейтинг классов по сумме 10 лучших результатов:")
                chart_df = q_board.set_index("Класс")[["Сумма ТОП-10 (из 1000)"]].head(10)
                st.bar_chart(chart_df)

# --- 7. ИНИЦИАЛИЗАЦИЯ СОСТОЯНИЯ ---
restore_state_from_url()

if "stage" not in st.session_state:
    st.session_state.stage = "register"
    st.session_state.step = 0
    st.session_state.score = 0
    st.session_state.elapsed_sec = 0
    st.session_state.station_start_time = time.time()
    st.session_state.answered = False
    st.session_state.used_hint = False
    st.session_state.credit_status = "none"
    st.session_state.practice_mode = False
    st.session_state.result_saved = False
    st.session_state.variant_seed = random.randint(100, 9999)
    st.session_state.unlocked = []
    st.session_state.history = []
    st.session_state.prediction = None
    st.session_state.shuffled_options = {}
    st.session_state.review_log = []
    st.session_state.existing_record = None

with st.sidebar:
    st.header("🏫 Школа № 19 г. Томска")
    st.write("Новогодний квест из 10 глав про науку, зимний Томск и праздничные традиции.")
    st.markdown("""
    <div class="teacher-card">
        <b>💌 От учителей Школы № 19:</b><br>
        Ребята! Пусть в новом году ваши идеи сияют ярче Полярной звезды, любая задачка решается легко и красиво, а каникулы подарят море радости! ✨
    </div>
    """, unsafe_allow_html=True)

    with st.expander("🔑 Панель учителя (аналитика и управление)"):
        admin_pwd = st.text_input("Пароль учителя:", type="password", placeholder="Введите пароль...")
        expected_pwd = st.secrets.get("ADMIN_PASSWORD", "tomsk19")
        if admin_pwd == expected_pwd:
            st.success("Доступ открыт")
            df_admin = load_results()
            st.metric("Всего записей в базе", len(df_admin))

            if not df_admin.empty:
                csv_bytes = df_admin.to_csv(index=False).encode("utf-8-sig")
                st.download_button(
                    label="📥 Скачать полную ведомость (CSV для Excel)",
                    data=csv_bytes,
                    file_name="vedomost_school19_quest.csv",
                    mime="text/csv",
                    use_container_width=True
                )

                subj_df = compute_subject_analytics(df_admin)
                if not subj_df.empty:
                    st.caption("📊 Статистика по предметам:")
                    st.dataframe(subj_df, use_container_width=True, hide_index=True)
                    st.bar_chart(subj_df.set_index("Предмет")[["Успешно (%)"]])

            if st.button("🗑️ Очистить все пробные попытки", use_container_width=True):
                clear_all_results()
                st.success("Таблица результатов очищена!")
                st.rerun()
        elif admin_pwd:
            st.error("Неверный пароль.")

render_header(show_garland=(st.session_state.stage != "quiz"))

nav_quest, nav_board, nav_facts = st.tabs([
    "🚀 Играть в квест",
    "🏆 Таблица рекордов",
    "✨ Научные чудеса зимы"
])

with nav_quest:
    if st.session_state.stage == "register":
        st.markdown("""
        <div class="teacher-card">
            <b>🎄 Привет, искатель приключений!</b><br>
            Из-за снежной бури Главный Хронометр остановился на отметке <b>23:59:59</b>. 
            Пройди 10 новогодних локаций, наряди школьную елку, собери секретный код <b>ДЕДМОРОЗ19</b> и запусти Новый год!
        </div>
        """, unsafe_allow_html=True)

        st.caption(
            "🔒 Твое настоящее имя увидят только учителя, а для общей таблицы рекордов система выдаст тебе секретный новогодний позывной!"
        )

        with st.form("reg_form"):
            last_name = st.text_input("Фамилия *", placeholder="Например: Сидоров")
            first_name = st.text_input("Имя *", placeholder="Например: Илья")
            col_g, col_l = st.columns(2)
            grade_num = col_g.selectbox("Класс *", list(range(5, 12)), format_func=lambda x: f"{x} класс")
            grade_letter = col_l.selectbox("Буква класса *", GRADE_LETTERS)
            submitted = st.form_submit_button("Получить позывной и начать игру 🚀", type="primary", use_container_width=True)

        if submitted:
            clean_last = normalize_name(last_name)
            clean_first = normalize_name(first_name)
            if len(clean_last) < 2 or len(clean_first) < 2:
                st.error("Пожалуйста, введи свои настоящие Фамилию и Имя русскими буквами.")
            else:
                df = load_results()
                full_grade = f"{grade_num}{grade_letter}"
                if grade_num <= 6:
                    league = "5–6 классы"
                elif grade_num <= 8:
                    league = "7–8 классы"
                else:
                    league = "9–11 классы"

                dup = pd.DataFrame()
                if not df.empty and {"LastName", "FirstName", "Grade"}.issubset(df.columns):
                    norm_last_col = df["LastName"].astype(str).apply(normalize_name).str.lower()
                    norm_first_col = df["FirstName"].astype(str).apply(normalize_name).str.lower()
                    dup = df[
                        (norm_last_col == clean_last.lower()) &
                        (norm_first_col == clean_first.lower()) &
                        (df["Grade"].astype(str) == full_grade)
                    ]

                if not dup.empty:
                    row0 = dup.iloc[0]
                    st.session_state.existing_record = {
                        "last_name": clean_last,
                        "first_name": clean_first,
                        "grade": full_grade,
                        "league": str(row0.get("League", league)),
                        "codename": str(row0.get("Codename", "Квантовый Снегирь")),
                        "score": int(pd.to_numeric(row0.get("Score", 0), errors="coerce") or 0),
                        "elapsed": int(pd.to_numeric(row0.get("TimeSec", 180), errors="coerce") or 180)
                    }
                else:
                    st.session_state.existing_record = None
                    existing_codes = set(df["Codename"].dropna().astype(str)) if "Codename" in df.columns else set()
                    codename = generate_unique_codename(existing_codes)

                    st.session_state.user = {
                        "last_name": clean_last,
                        "first_name": clean_first,
                        "grade": full_grade,
                        "league": league,
                        "codename": codename
                    }
                    st.session_state.practice_mode = False
                    st.session_state.result_saved = False
                    st.session_state.variant_seed = random.randint(100, 9999)
                    st.session_state.shuffled_options = {}
                    st.session_state.review_log = []
                    st.session_state.history = []
                    st.session_state.unlocked = []
                    st.session_state.step = 0
                    st.session_state.score = 0
                    st.session_state.elapsed_sec = 0
                    st.session_state.station_start_time = time.time()
                    st.session_state.answered = False
                    st.session_state.used_hint = False
                    st.session_state.credit_status = "none"
                    st.session_state.stage = "quiz"
                    sync_state_to_url()
                    st.rerun()

        if st.session_state.get("existing_record"):
            rec = st.session_state.existing_record
            st.info(
                f"🎉 Привет, {rec['first_name']}! Твой результат уже записан в таблицу рекордов: "
                f"{rec['score']} из 100 баллов (позывной: {rec['codename']}). "
                f"Ниже ты можешь снова скачать свой сертификат или пройти квест еще раз для тренировки!"
            )
            rec_rank = get_rank_title(rec["score"])
            png_b, pdf_b = generate_diploma_files(rec, rec_rank, rec["score"], 100, rec["elapsed"])
            st.image(png_b, use_container_width=True)

            c_dl1, c_dl2 = st.columns(2)
            c_dl1.download_button(
                label="📥 Скачать сертификат (PNG)",
                data=png_b,
                file_name="sertifikat_school19.png",
                mime="image/png",
                type="primary",
                use_container_width=True,
                key="re_dl_png"
            )
            c_dl2.download_button(
                label="📄 Скачать сертификат (PDF)",
                data=pdf_b,
                file_name="sertifikat_school19.pdf",
                mime="application/pdf",
                use_container_width=True,
                key="re_dl_pdf"
            )

            if st.button("🔄 Пройти квест еще раз в режиме тренировки (с новыми вариантами, без записи в таблицу)", use_container_width=True):
                st.session_state.user = {
                    "last_name": rec["last_name"],
                    "first_name": rec["first_name"],
                    "grade": rec["grade"],
                    "league": rec["league"],
                    "codename": rec["codename"]
                }
                st.session_state.practice_mode = True
                st.session_state.result_saved = True
                st.session_state.existing_record = None
                st.session_state.variant_seed = random.randint(100, 9999)
                st.session_state.shuffled_options = {}
                st.session_state.review_log = []
                st.session_state.history = []
                st.session_state.unlocked = []
                st.session_state.step = 0
                st.session_state.score = 0
                st.session_state.elapsed_sec = 0
                st.session_state.station_start_time = time.time()
                st.session_state.answered = False
                st.session_state.used_hint = False
                st.session_state.credit_status = "none"
                st.session_state.stage = "quiz"
                sync_state_to_url()
                st.rerun()

    elif st.session_state.stage == "quiz":
        user = st.session_state.user
        custom_bank = load_custom_questions_from_sheet(st.secrets.get("WEBHOOK_URL", ""))
        quest_bank = custom_bank if custom_bank else get_local_quest_bank(st.session_state.variant_seed)
        questions = quest_bank[user["league"]]
        total_q = len(questions)
        idx = st.session_state.step
        q = questions[idx]

        mode_badge = " (Тренировка)" if st.session_state.get("practice_mode") else ""
        with st.container(border=True):
            st.markdown(
                f"🪪 **{user['codename']}{mode_badge}** | 🎓 **{user['grade']}** | "
                f"⭐ **{st.session_state.score} баллов** | 📍 **Глава {idx + 1} из {total_q}**"
            )
            render_progress_visuals(st.session_state.unlocked)

        st.markdown(f"""
        <div class="station-art">
            <div style="color:{q['accent']}; font-weight:700; font-size:1.06rem;">{q['banner_title']}</div>
            <div style="color:#cbd5e1; font-size:0.88rem; margin-top:3px;">{q['banner_sub']}</div>
        </div>
        """, unsafe_allow_html=True)

        # Защищенная карточка вопроса с водяным знаком позывного и номера варианта (P2)
        st.markdown(f"""
        <div class="protected-box">
            <div class="watermark-bar">
                <span>🔒 Экземпляр: {user['codename']} ({user['grade']})</span>
                <span>Вариант #{st.session_state.variant_seed}</span>
            </div>
            <div style="color:#1e293b; font-size:0.97rem; line-height:1.48; margin-bottom:0.5rem;">{q['story']}</div>
            <div style="color:#0f172a; font-weight:700; font-size:1.01rem;">Вопрос: {q['question']}</div>
            <span class="ai-trap">{q.get('ai_trap', '')}</span>
        </div>
        """, unsafe_allow_html=True)

        if not st.session_state.used_hint and not st.session_state.answered:
            if st.button("💡 Спросить подсказку у снегиря Проши (-2 балла при полном ответе)", use_container_width=True):
                st.session_state.used_hint = True
                sync_state_to_url()
                st.rerun()

        if st.session_state.used_hint:
            st.warning(f"🐦 Подсказка от снегиря Проши: {q['hint']}")

        with st.form(key=f"answer_form_{idx}"):
            user_answer = None
            if q["type"] == "radio":
                current_opts = get_shuffled_options(idx, q["options"])
                user_answer = st.radio(
                    "Выбери один ответ:",
                    current_opts,
                    index=None,
                    disabled=st.session_state.answered
                )
            elif q["type"] == "checkboxes":
                current_opts = get_shuffled_options(idx, q["options"])
                st.caption(f"Отметь галочками ДВА верных варианта (из {len(current_opts)}):")
                selected = []
                for opt in current_opts:
                    if st.checkbox(opt, disabled=st.session_state.answered):
                        selected.append(opt)
                user_answer = selected
            elif q["type"] == "number":
                user_answer = st.number_input(
                    "Введи числовой ответ:",
                    step=1,
                    value=None,
                    placeholder="Нажми для ввода числа...",
                    disabled=st.session_state.answered
                )

            submit_ans = st.form_submit_button(
                "Ответить и зажечь игрушку на елке 🎄",
                type="primary",
                disabled=st.session_state.answered,
                use_container_width=True
            )

        if submit_ans and not st.session_state.answered:
            if user_answer is None or user_answer == []:
                st.error("Сначала выбери или введи ответ!")
            else:
                credit_status, pts = evaluate_answer(
                    q["type"], user_answer, q["answer"], st.session_state.used_hint
                )

                step_dt = int(round(time.time() - st.session_state.get("station_start_time", time.time())))
                step_dt = max(1, min(step_dt, MAX_STATION_SEC))
                st.session_state.elapsed_sec += step_dt

                st.session_state.answered = True
                st.session_state.credit_status = credit_status
                if len(st.session_state.unlocked) <= idx:
                    st.session_state.unlocked.append(SECRET_WORD[idx])

                st.session_state.score += pts
                if credit_status == "full":
                    st.session_state.history.append(f"{q['subject']}:✅({pts})")
                elif credit_status == "partial":
                    st.session_state.history.append(f"{q['subject']}:🟡({pts})")
                else:
                    st.session_state.history.append(f"{q['subject']}:❌(0)")

                ans_str = ", ".join(user_answer) if isinstance(user_answer, list) else str(user_answer)
                st.session_state.review_log.append({
                    "i": idx,
                    "u": ans_str,
                    "c": 2 if credit_status == "full" else (1 if credit_status == "partial" else 0),
                    "p": pts
                })
                sync_state_to_url()
                st.rerun()

        if st.session_state.answered:
            letter = SECRET_WORD[idx]
            toy = TREE_TOYS[idx]
            c_stat = st.session_state.get("credit_status", "none")
            last_pts = st.session_state.review_log[-1]["p"] if st.session_state.review_log else 0

            if c_stat == "full":
                st.success(f"✅ Верно! +{last_pts} баллов. На елке зажглась игрушка {toy}, открыта буква ключа: «{letter}»!")
            elif c_stat == "partial":
                st.warning(f"🟡 Почти полностью верно (найдена половина ответа без ошибок)! +{last_pts} баллов. Зажглась игрушка {toy}, открыта буква «{letter}»!")
            else:
                st.error(f"❌ Чуть-чуть мимо (0 баллов). Но снегирь Проша все равно зажег игрушку {toy} и открыл букву «{letter}»!")

            svg_diagram = get_chapter_svg(idx)
            exp_line = f"<br><br><b>🔬 Проверь на каникулах:</b> {q['experiment']}" if q.get("experiment") else ""
            fact_line = f"<br><br><b>✨ Интересный факт:</b> {q['fun_fact']}" if q.get("fun_fact") else ""

            st.markdown(f"""
            <div class="feedback-card">
                <div style="margin-bottom:8px;">{svg_diagram}</div>
                <b>🧠 Почему так:</b> {q['explanation']}{exp_line}{fact_line}
            </div>
            """, unsafe_allow_html=True)

            next_label = "Дальше ➡️" if idx + 1 < total_q else "Собрать код «ДЕДМОРОЗ19» и запустить Часы! 🎆"
            if st.button(next_label, type="primary", use_container_width=True):
                if idx + 1 < total_q:
                    st.session_state.step += 1
                    st.session_state.answered = False
                    st.session_state.used_hint = False
                    st.session_state.credit_status = "none"
                    st.session_state.station_start_time = time.time()
                    sync_state_to_url()
                    st.rerun()
                else:
                    if not st.session_state.get("practice_mode", False):
                        save_result({
                            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "LastName": user["last_name"],
                            "FirstName": user["first_name"],
                            "Grade": user["grade"],
                            "League": user["league"],
                            "Codename": user["codename"],
                            "Score": st.session_state.score,
                            "TimeSec": st.session_state.elapsed_sec,
                            "Details": " | ".join(st.session_state.history)
                        })
                    st.session_state.stage = "finish"
                    sync_state_to_url()
                    st.rerun()

    elif st.session_state.stage == "finish":
        st.snow()
        user = st.session_state.user
        score = st.session_state.score
        max_score = 100
        elapsed = st.session_state.get("elapsed_sec", 120)

        st.success("🎉 Ключ «Д Е Д М О Р О З 1 9» собран, елочка наряжена, а Главный Хронометр запущен!")
        if st.session_state.get("practice_mode"):
            st.info("🔄 Это было тренировочное прохождение! Твой первый официальный рекорд в таблице сохранен без изменений.")
        render_progress_visuals(SECRET_WORD)

        rank = get_rank_title(score)
        png_bytes, pdf_bytes = generate_diploma_files(user, rank, score, max_score, elapsed)

        st.subheader("🎓 Твой именной сертификат")
        st.image(png_bytes, use_container_width=True)

        col_dl1, col_dl2 = st.columns(2)
        col_dl1.download_button(
            label="📥 Скачать картинкой (PNG)",
            data=png_bytes,
            file_name="sertifikat_school19.png",
            mime="image/png",
            type="primary",
            use_container_width=True
        )
        col_dl2.download_button(
            label="📄 Скачать документом (PDF)",
            data=pdf_bytes,
            file_name="sertifikat_school19.pdf",
            mime="application/pdf",
            use_container_width=True
        )

        df_all = load_results()
        if not df_all.empty and "Grade" in df_all.columns:
            class_count = len(df_all[df_all["Grade"].astype(str) == user["grade"]])
            if class_count < TOP_CLASS_COUNT:
                need_more = TOP_CLASS_COUNT - class_count
                st.info(
                    f"🏫 В зачете «Битвы классов» от {user['grade']} класса уже {class_count} из {TOP_CLASS_COUNT} человек! "
                    f"Зови еще {need_more} одноклассников, чтобы собрать полную команду класса!"
                )
            else:
                st.success(
                    f"🏫 Команда {user['grade']} класса полностью собрана ({class_count} участников)! "
                    f"В копилку класса идут 10 лучших результатов!"
                )

        if st.session_state.get("review_log"):
            custom_bank = load_custom_questions_from_sheet(st.secrets.get("WEBHOOK_URL", ""))
            quest_bank = custom_bank if custom_bank else get_local_quest_bank(st.session_state.variant_seed)
            questions = quest_bank[user["league"]]
            with st.expander("🧐 Посмотреть свои ответы по всем главам"):
                for item in st.session_state.review_log:
                    q_idx = int(item.get("i", 0))
                    if q_idx < len(questions):
                        q_obj = questions[q_idx]
                        c_val = int(item.get("c", 0))
                        icon = "✅" if c_val == 2 else ("🟡" if c_val == 1 else "❌")
                        corr_str = ", ".join(q_obj["answer"]) if isinstance(q_obj["answer"], list) else str(q_obj["answer"])
                        st.markdown(
                            f"**{icon} {q_obj['banner_title']} (+{item.get('p', 0)} б.)**  \n"
                            f"Вопрос: {q_obj['question']}  \n"
                            f"Твой ответ: {item.get('u', '')} | Правильный ответ: {corr_str}  \n"
                            f"💡 {q_obj['explanation']}"
                        )
                        st.divider()

        if st.button("🔮 Вытянуть новогоднее предсказание от снегиря Проши!", use_container_width=True):
            st.session_state.prediction = random.choice(PREDICTIONS)
            st.balloons()

        if st.session_state.prediction:
            st.info(f"Твое предсказание на Новый год: {st.session_state.prediction}")

        st.markdown("""
        <div class="teacher-card">
            <b>🎄 Дорогой ученик Школы № 19 города Томска!</b><br><br>
            Твои учителя от всей души поздравляют тебя с наступающим Новым годом и Рождеством! 
            Сегодня ты доказал(а), что смекалка и знание законов природы помогают творить настоящие чудеса. 
            Желаем тебе крепкого сибирского здоровья, верных друзей, ярких открытий и веселых зимних каникул!<br><br>
            <i>С теплом и гордостью за вас, учителя МАОУ СОШ № 19 г. Томска ❤️</i>
        </div>
        """, unsafe_allow_html=True)

        st.divider()
        render_leaderboard(key_prefix="finish")

with nav_board:
    render_leaderboard(key_prefix="tab")

with nav_facts:
    st.subheader("✨ Научные чудеса Нового года и зимнего Томска")
    st.write("Загляни в копилку удивительных фактов от учителей Школы № 19:")
    for title_fact, body_fact in FUN_FACTS:
        st.markdown(f"""
        <div class="feedback-card">
            <b>{title_fact}</b><br>{body_fact}
        </div>
        """, unsafe_allow_html=True)
