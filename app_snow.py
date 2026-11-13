import streamlit as st
import pandas as pd
import random
import time
from datetime import datetime

# Попытка импорта коннектора к Google Sheets
try:
    from streamlit_gsheets import GSheetsConnection
    GSHEETS_AVAILABLE = True
except ImportError:
    GSHEETS_AVAILABLE = False

st.set_page_config(
    page_title="Школа № 19 г. Томска | Новогодний квест",
    page_icon="🎄",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- АДАПТИВНЫЙ ДИЗАЙН (CSS ДЛЯ ТЕЛЕФОНОВ И ПК) ---
st.markdown("""
<style>
    /* Увеличиваем кнопки и зоны нажатия для смартфонов */
    .stButton > button, .stFormSubmitButton > button {
        min-height: 3.1rem;
        font-size: 1.05rem !important;
        font-weight: 600 !important;
        border-radius: 12px !important;
    }
    /* Удобные отступы у радиокнопок и чекбоксов на мобильном экране */
    div[role="radiogroup"] label, .stCheckbox label {
        padding: 6px 4px;
        font-size: 1rem !important;
    }
    /* Праздничный баннер школы */
    .school-banner {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: #ffffff;
        padding: 1.2rem;
        border-radius: 16px;
        text-align: center;
        margin-bottom: 1rem;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.12);
    }
    .school-banner h2 {
        color: #ffffff !important;
        margin: 0 0 0.3rem 0;
        font-size: 1.35rem;
    }
    .school-banner p {
        margin: 0;
        font-size: 0.95rem;
        opacity: 0.92;
    }
    /* Открытка с поздравлением от учителей */
    .teacher-card {
        background: linear-gradient(135deg, #fffDF9 0%, #fef3c7 100%);
        color: #1f2937;
        border-left: 5px solid #f59e0b;
        padding: 1.1rem;
        border-radius: 12px;
        margin: 1rem 0;
        font-size: 0.98rem;
        line-height: 1.5;
    }
    /* Панель крио-ключа (буквы) */
    .key-bar {
        display: flex;
        justify-content: center;
        gap: 6px;
        margin: 0.8rem 0 1.2rem 0;
        flex-wrap: wrap;
    }
    .key-cell {
        width: 36px;
        height: 40px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 1.1rem;
    }
    .key-open {
        background: #2563eb;
        color: #ffffff;
        box-shadow: 0 2px 6px rgba(37, 99, 235, 0.35);
    }
    .key-locked {
        background: rgba(156, 163, 175, 0.2);
        color: #9ca3af;
        border: 1px dashed #9ca3af;
    }
</style>
""", unsafe_allow_html=True)

SECRET_WORD = list("СНЕЖИНКА")

# --- 1. БАЗА ЗАДАНИЙ ПО ЛИГАМ ---
QUEST_DATA = {
    "5–7 классы": [
        {
            "subject": "Физика",
            "location": "Локация 1. Крио-ангар (Физика)",
            "story": "Над Томском разыгралась магнитная метель! Главная ледяная линза Хронометра оказалась в теплом помещении (+22 °C). Нужно срочно замедлить ее таяние до прихода инженеров.",
            "question": "Во что лучше всего укутать ледяную линзу, чтобы она таяла как можно медленнее?",
            "type": "radio",
            "options": [
                "В толстый шерстяной шарф",
                "В тонкий медный лист",
                "Положить на алюминиевый поднос",
                "Оставить открытой под вентилятором"
            ],
            "answer": "В толстый шерстяной шарф",
            "hint": "Шерсть сама по себе не греет — она плохо пропускает тепло из-за воздуха между ворсинками.",
            "explanation": "Шерсть — отличный теплоизолятор. Она не пускает комнатное тепло ко льду, поэтому в шарфе лед не растает гораздо дольше!"
        },
        {
            "subject": "Химия",
            "location": "Локация 2. Пиротехнический цех (Химия)",
            "story": "Чтобы подать световой сигнал над Лагерным садом, нужно зажечь сигнальные огни ярко-зеленого и желтого цветов.",
            "question": "Отметьте галочками РОВНО ДВА вещества, которые окрасят пламя в зеленый и желтый цвета:",
            "type": "checkboxes",
            "options": [
                "Соли бария (зеленое свечение)",
                "Соли натрия (желтое свечение)",
                "Обычный речной песок",
                "Дистиллированная вода"
            ],
            "answer": ["Соли бария (зеленое свечение)", "Соли натрия (желтое свечение)"],
            "hint": "В пиротехнике цвет огню придают соли металлов — обратите внимание на подсказки в скобках!",
            "explanation": "При нагревании ионы бария излучают красивый зеленый свет, а соединения натрия дают ярко-желтое пламя."
        },
        {
            "subject": "Астрономия",
            "location": "Локация 3. Томская обсерватория (Астрономия)",
            "story": "Метель сбила прицел телескопа. Нам нужно сориентировать антенну строго на Север по Полярной звезде.",
            "question": "Через крайние звезды «ковша» какого созвездия проще всего найти Полярную звезду?",
            "type": "radio",
            "options": ["Большая Медведица", "Орион", "Кассиопея", "Лебедь"],
            "answer": "Большая Медведица",
            "hint": "Если провести прямую линию через две крайние звезды этого знаменитого «ковша», она укажет прямо на Полярную звезду.",
            "explanation": "Полярная звезда находится в Малой Медведице, а находят ее с помощью «стенки» ковша Большой Медведицы."
        },
        {
            "subject": "Биология",
            "location": "Локация 4. Сибирский кедровник (Биология)",
            "story": "На улице сибирский мороз -35 °C. Березы и осины давно сбросили листья, а сосны, ели и кедры стоят зелеными.",
            "question": "Почему хвоя не замерзает и не высыхает зимой?",
            "type": "radio",
            "options": [
                "У хвоинок малая площадь, восковой налет, а в клетках много сахаров и смол",
                "Корни хвойных деревьев зимой нагревают почву вокруг себя",
                "Внутри хвоинок вообще нет жидкости",
                "Зимой иголки превращаются в твердую кору"
            ],
            "answer": "У хвоинок малая площадь, восковой налет, а в клетках много сахаров и смол",
            "hint": "Густой сахарный сироп замерзает гораздо хуже обычной воды, а воск не дает влаге испаряться.",
            "explanation": "Плотная кожица с воском бережет влагу, а высокая концентрация сахаров и эфирных масел работает как природный антифриз."
        },
        {
            "subject": "Информатика",
            "location": "Локация 5. Серверная Школы № 19 (Информатика)",
            "story": "На дверях серверной активировался защитный шифр! Вместо номера нашей школы система просит расшифровать двоичный код `10011`.",
            "question": "Переведите двоичное число 10011 в привычную десятичную систему:",
            "type": "number",
            "answer": 19,
            "hint": "Сложите степени двойки справа налево там, где стоят единицы: 16 + 0 + 0 + 2 + 1 (кстати, вспомните номер вашей школы!).",
            "explanation": "1×16 + 0×8 + 0×4 + 1×2 + 1×1 = 19! Конечно же, код доступа — родная Школа № 19!"
        },
        {
            "subject": "География",
            "location": "Локация 6. Навигационный штаб (География)",
            "story": "В Томске Новый год наступает на 4 часа раньше, чем в Москве. Но бортовой компьютер спрашивает точку, где праздник встречают самым первым на планете.",
            "question": "Где на Земле Новый год наступает раньше всех?",
            "type": "radio",
            "options": [
                "Острова Лайн (Кирибати) в Тихом океане",
                "Гринвичский меридиан (Великобритания)",
                "Остров Врангеля",
                "Мыс Горн (Южная Америка)"
            ],
            "answer": "Острова Лайн (Кирибати) в Тихом океане",
            "hint": "Это островное государство в Тихом океане живет в самом первом часовом поясе Земли (UTC+14).",
            "explanation": "На островах Лайн (Кирибати) Новый год наступает первым на планете — когда в Томске еще только 17:00 31 декабря!"
        },
        {
            "subject": "Математика",
            "location": "Локация 7. Шифровальный узел (Математика)",
            "story": "На пульте сейфа с запасным аккумулятором горят 3 цветных тумблера: красный, синий и зеленый.",
            "question": "Сколько всего различных цветовых последовательностей можно составить, переставляя эти 3 тумблера местами?",
            "type": "number",
            "answer": 6,
            "hint": "На первое место можно поставить любой из 3 цветов, на второе — любой из 2 оставшихся, на третье — 1 (3 × 2 × 1).",
            "explanation": "Количество перестановок из трех элементов равно 3! = 3 × 2 × 1 = 6 комбинаций."
        },
        {
            "subject": "Блиц",
            "location": "Локация 8. Пульт Хронометра (Финальный блиц)",
            "story": "Последний рубеж! Отметьте галочками ТОЛЬКО ПРАВДИВЫЕ научные утверждения, чтобы запустить Главные Часы.",
            "question": "Какие из этих трех фактов — чистая правда?",
            "type": "checkboxes",
            "options": [
                "Лед легче жидкой воды, поэтому реки промерзают сверху вниз, а не со дна",
                "Полярная звезда — самая яркая звезда на всем ночном небе",
                "Белые медведи в дикой природе охотятся на пингвинов"
            ],
            "answer": ["Лед легче жидкой воды, поэтому реки промерзают сверху вниз, а не со дна"],
            "hint": "Правда здесь только одна! Полярная звезда лишь 48-я по яркости, а белые медведи и пингвины живут на разных полюсах Земли.",
            "explanation": "Плотность льда меньше плотности воды, поэтому лед плавает наверху и защищает обитателей реки Томь от промерзания до дна!"
        }
    ],
    "8–11 классы": [
        {
            "subject": "Физика",
            "location": "Локация 1. Крио-ангар (Физика)",
            "story": "Аномальный циклон над Томском вызвал скачок напряжения в крио-камере. Нужно рассчитать энергию для аварийного контура охлаждения.",
            "question": "Сколько килоджоулей (кДж) теплоты потребуется, чтобы полностью расплавить 2 кг льда, взятого при температуре 0 °C? (Удельная теплота плавления льда λ = 330 кДж/кг).",
            "type": "number",
            "answer": 660,
            "hint": "Используйте формулу плавления: Q = λ · m, где m = 2 кг.",
            "explanation": "Q = 330 кДж/кг × 2 кг = 660 кДж. Этой энергии хватило бы, чтобы нагреть 2 литра ледяной воды почти до кипения!"
        },
        {
            "subject": "Химия",
            "location": "Локация 2. Пиротехнический цех (Химия)",
            "story": "Для калибровки спектрального маяка нужно получить изумрудно-зеленое и ярко-желтое окрашивание пламени.",
            "question": "Отметьте РОВНО ДВА реагента, ионы которых окрасят пламя в зеленый и желтый цвета:",
            "type": "checkboxes",
            "options": [
                "BaCl₂ (хлорид бария)",
                "NaCl (хлорид натрия)",
                "KCl (хлорид калия)",
                "SiO₂ (оксид кремния)"
            ],
            "answer": ["BaCl₂ (хлорид бария)", "NaCl (хлорид натрия)"],
            "hint": "Ионы Ba²⁺ дают зеленый цвет пламени, ионы Na⁺ — желтый, а калий дает фиолетовое свечение.",
            "explanation": "Хлорид бария (BaCl₂) отвечает за зеленое свечение, а хлорид натрия (NaCl) — за интенсивную желтую линию спектра."
        },
        {
            "subject": "Астрономия",
            "location": "Локация 3. Томская обсерватория (Астрономия)",
            "story": "Вирус внес ошибку в астрономический модуль. Нужно восстановить истинную причину смены времен года и декабрьского солнцестояния.",
            "question": "Что является главной причиной наступления зимы в Северном полушарии?",
            "type": "radio",
            "options": [
                "Наклон оси вращения Земли к плоскости орбиты (около 23,5°)",
                "Максимальное удаление Земли от Солнца в декабре и январе",
                "Замедление орбитальной скорости Земли зимой",
                "Перекрытие солнечного потока поясом астероидов"
            ],
            "answer": "Наклон оси вращения Земли к плоскости орбиты (около 23,5°)",
            "hint": "В начале января Земля, наоборот, проходит ближайшую к Солнцу точку орбиты (перигелий), но в Сибири в это время зима.",
            "explanation": "Из-за наклона земной оси на 23,44° Северное полушарие в декабре отклонено от Солнца: солнечные лучи скользят под малым углом и слабо прогревают поверхность."
        },
        {
            "subject": "Биология",
            "location": "Локация 4. Сибирский кедровник (Биология)",
            "story": "Датчики в припоселковом кедровнике под Томском фиксируют -40 °C, но клетки хвои не разрываются кристаллами льда.",
            "question": "Какой биохимический механизм защищает клетки хвойных от замерзания зимой?",
            "type": "radio",
            "options": [
                "Перевод крахмала в растворимые сахара и частичное обезвоживание цитоплазмы",
                "Превращение клеточной воды в тяжелую воду (D₂O)",
                "Интенсивное деление клеток с выделением тепла",
                "Полное разрушение клеточных мембран на зимний период"
            ],
            "answer": "Перевод крахмала в растворимые сахара и частичное обезвоживание цитоплазмы",
            "hint": "По закону Рауля рост концентрации растворенных веществ (глюкозы и олигосахаридов) понижает точку замерзания раствора.",
            "explanation": "К зиме крахмал в клетках гидролизуется до простых сахаров, которые работают как криопротекторы и не дают воде образовать острые кристаллы льда."
        },
        {
            "subject": "Информатика",
            "location": "Локация 5. Серверная Школы № 19 (Информатика)",
            "story": "Для перезагрузки школьного узла связи нужно вычислить сумму двух чисел, записанных в разных системах счисления: `13₁₆ + 110₂`.",
            "question": "Переведите числа 13₁₆ (шестнадцатеричное) и 110₂ (двоичное) в десятичную систему и введите их СУММУ:",
            "type": "number",
            "answer": 25,
            "hint": "13₁₆ = 1×16 + 3 = 19 (номер нашей школы!). А 110₂ = 4 + 2 + 0 = 6. Осталось их сложить.",
            "explanation": "13₁₆ = 19, а 110₂ = 6. Сумма: 19 + 6 = 25. Связь с сервером Школы № 19 полностью восстановлена!"
        },
        {
            "subject": "География",
            "location": "Локация 6. Навигационный штаб (География)",
            "story": "Экспериментальный ракетоплан вылетает из Томска (UTC+7) на восток и пересекает 180-й меридиан (Линию перемены дат), направляясь к Аляске.",
            "question": "Как изменится календарная дата при пересечении Линии перемены дат с запада на восток (из Восточного полушария в Западное)?",
            "type": "radio",
            "options": [
                "Дата уменьшится на 1 сутки (можно встретить Новый год второй раз)",
                "Дата увеличится на 1 сутки (один день пропадет из календаря)",
                "Календарная дата не изменится",
                "Часы автоматически переведутся на время Гринвича"
            ],
            "answer": "Дата уменьшится на 1 сутки (можно встретить Новый год второй раз)",
            "hint": "В Азии (к западу от линии) уже наступило 1 января, а на Аляске (к востоку от линии) все еще продолжается 31 декабря.",
            "explanation": "При пересечении 180-го меридиана с запада на восток из календаря вычитаются одни сутки — попадаешь во «вчера» и можешь отпраздновать Новый год дважды!"
        },
        {
            "subject": "Математика",
            "location": "Локация 7. Шифровальный узел (Математика)",
            "story": "Криптографический замок требует перебрать все возможные перестановки из 5 разноцветных кристаллов в панели управления.",
            "question": "Сколько уникальных комбинаций (перестановок без повторений) можно составить из 5 различных кристаллов?",
            "type": "number",
            "answer": 120,
            "hint": "Вычислите факториал пяти: P₅ = 5! = 1 × 2 × 3 × 4 × 5.",
            "explanation": "Число перестановок из 5 элементов равно 5! = 120 комбинаций."
        },
        {
            "subject": "Блиц",
            "location": "Локация 8. Пульт Хронометра (Финальный блиц)",
            "story": "Финальная калибровка! Отметьте галочками ТОЛЬКО НАУЧНО ВЕРНЫЕ утверждения, чтобы снять блокировку со времени.",
            "question": "Выберите все верные физические утверждения:",
            "type": "checkboxes",
            "options": [
                "Эффект Мпембы — парадокс, при котором горячая вода в некоторых условиях замерзает быстрее холодной",
                "Полярные сияния возникают из-за отражения солнечных лучей от ледяного щита Арктики",
                "Абсолютный ноль температуры по шкале Цельсия равен −273,15 °C"
            ],
            "answer": [
                "Эффект Мпембы — парадокс, при котором горячая вода в некоторых условиях замерзает быстрее холодной",
                "Абсолютный ноль температуры по шкале Цельсия равен −273,15 °C"
            ],
            "hint": "Верных утверждений здесь ДВА. Полярное сияние вызвано солнечным ветром и магнитосферой, а не отражением света ото льда.",
            "explanation": "Эффект Мпембы и температура абсолютного нуля (−273,15 °C или 0 К) — реальные научные факты, а полярное сияние — это свечение верхних слоев атмосферы при столкновении с частицами солнечного ветра."
        }
    ]
}

# --- 2. ГЕНЕРАТОР УНИКАЛЬНЫХ ПОЗЫВНЫХ ---
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

def generate_unique_codename(existing_codenames: set) -> str:
    for _ in range(120):
        name = f"{random.choice(ADJECTIVES)} {random.choice(NOUNS)}"
        if name not in existing_codenames:
            return name
    while True:
        name = f"{random.choice(ADJECTIVES)} {random.choice(NOUNS)} #{random.randint(10, 99)}"
        if name not in existing_codenames:
            return name

# --- 3. РАБОТА С БАЗОЙ ДАННЫХ ---
COLUMNS = ["Timestamp", "LastName", "FirstName", "Grade", "League", "Codename", "Score", "TimeSec", "Details"]

def load_results(fresh: bool = False):
    if "local_db" not in st.session_state:
        st.session_state.local_db = pd.DataFrame(columns=COLUMNS)
    if GSHEETS_AVAILABLE and "connections" in st.secrets:
        try:
            conn = st.connection("gsheets", type=GSheetsConnection)
            df = conn.read(ttl=0 if fresh else 5)
            return df.dropna(how="all")
        except Exception:
            return st.session_state.local_db
    return st.session_state.local_db

def save_result(row_dict):
    df = load_results(fresh=True)
    new_row = pd.DataFrame([row_dict])
    updated_df = pd.concat([df, new_row], ignore_index=True)
    st.session_state.local_db = updated_df
    if GSHEETS_AVAILABLE and "connections" in st.secrets:
        try:
            conn = st.connection("gsheets", type=GSheetsConnection)
            conn.update(data=updated_df)
        except Exception as e:
            st.warning(f"Результат сохранен локально (ошибка облачной записи: {e})")

# --- 4. ОТРИСОВКА ШАПКИ И КРИО-КЛЮЧА ---
def render_header():
    st.markdown("""
    <div class="school-banner">
        <h2>🎄 МАОУ СОШ № 19 г. Томска</h2>
        <p>Новогодняя научная экспедиция «Тайна Сибирского Хронометра»</p>
    </div>
    """, unsafe_allow_html=True)

def render_key_bar(unlocked_letters: list):
    cells_html = ""
    for i, char in enumerate(SECRET_WORD):
        if i < len(unlocked_letters):
            cells_html += f'<div class="key-cell key-open">{unlocked_letters[i]}</div>'
        else:
            cells_html += '<div class="key-cell key-locked">?</div>'
    st.markdown(f'<div class="key-bar">{cells_html}</div>', unsafe_allow_html=True)

# --- 5. ИНИЦИАЛИЗАЦИЯ СОСТОЯНИЯ ---
if "stage" not in st.session_state:
    st.session_state.stage = "register"
    st.session_state.step = 0
    st.session_state.score = 0
    st.session_state.answered = False
    st.session_state.used_hint = False
    st.session_state.last_correct = False
    st.session_state.start_time = 0.0
    st.session_state.unlocked = []
    st.session_state.history = []

# Боковая панель с информацией о школе и поздравлением
with st.sidebar:
    st.header("🏫 Школа № 19 г. Томска")
    st.write("Интерактивный новогодний квест по естественным и точным наукам для учеников 5–11 классов.")
    st.markdown("""
    <div class="teacher-card">
        <b>💌 От учителей Школы № 19:</b><br>
        Дорогие ребята! Пусть в новом году ваши идеи сияют ярче Полярной звезды, любая сложная задачка решается красиво, а каникулы подарят море снежной радости и вдохновения! Вперед к открытиям! ✨
    </div>
    """, unsafe_allow_html=True)
    st.caption("Правила: 8 лабораторий, +10 баллов за чистый ответ, +8 баллов при взятии подсказки.")

render_header()

# --- ЭКРАН 1: РЕГИСТРАЦИЯ ---
if st.session_state.stage == "register":
    st.markdown("""
    <div class="teacher-card">
        <b>🎄 С наступающим Новым годом и Рождеством, друзья!</b><br>
        Учителя <b>Школы № 19 города Томска</b> приготовили для вас праздничное научное приключение. 
        Из-за снежной магнитной бури Главный Хронометр остановился на отметке <b>23:59:59</b>. 
        Пройдите 8 лабораторий, соберите 8 букв крио-ключа и запустите отсчет Нового года!
    </div>
    """, unsafe_allow_html=True)

    with st.expander("🛡️ Как работает анонимный рейтинг (Лидерборд)?"):
        st.write(
            "Вы вводите свои настоящие Фамилию, Имя и Класс для школьного зачета (их увидят только учителя). "
            "Для общей таблицы рекордов система выдаст вам уникальный **новогодний научный позывной**!"
        )

    with st.form("reg_form"):
        last_name = st.text_input("Фамилия *", placeholder="Например: Сидоров")
        first_name = st.text_input("Имя *", placeholder="Например: Илья")
        col_g, col_l = st.columns(2)
        grade_num = col_g.selectbox("Класс *", list(range(5, 12)), format_func=lambda x: f"{x} класс")
        grade_letter = col_l.selectbox("Буква класса", ["А", "Б", "В", "Г", "Д", "Е", "Без буквы"])
        submitted = st.form_submit_button("Получить позывной и начать квест 🚀", type="primary", use_container_width=True)

    if submitted:
        if len(last_name.strip()) < 2 or len(first_name.strip()) < 2:
            st.error("Пожалуйста, введите корректные Фамилию и Имя.")
        else:
            df = load_results()
            clean_last = last_name.strip().capitalize()
            clean_first = first_name.strip().capitalize()
            full_grade = f"{grade_num}" if grade_letter == "Без буквы" else f"{grade_num}{grade_letter}"

            # Проверка на дубликат
            if not df.empty and {"LastName", "FirstName", "Grade"}.issubset(df.columns):
                dup = df[
                    (df["LastName"].astype(str).str.lower() == clean_last.lower()) &
                    (df["FirstName"].astype(str).str.lower() == clean_first.lower()) &
                    (df["Grade"].astype(str) == full_grade)
                ]
                if not dup.empty:
                    st.warning(
                        f"Исследователь **{clean_first} {clean_last} ({full_grade} класс)** уже прошел квест!  \n"
                        f"Позывной: **{dup.iloc[0]['Codename']}**, результат: **{dup.iloc[0]['Score']} баллов**."
                    )
                    st.stop()

            existing_codes = set(df["Codename"].dropna().astype(str)) if "Codename" in df.columns else set()
            codename = generate_unique_codename(existing_codes)
            league = "5–7 классы" if grade_num <= 7 else "8–11 классы"

            st.session_state.user = {
                "last_name": clean_last,
                "first_name": clean_first,
                "grade": full_grade,
                "league": league,
                "codename": codename
            }
            st.session_state.start_time = time.time()
            st.session_state.stage = "quiz"
            st.rerun()

# --- ЭКРАН 2: ЛАБОРАТОРИИ КВЕСТА ---
elif st.session_state.stage == "quiz":
    user = st.session_state.user
    questions = QUEST_DATA[user["league"]]
    total_q = len(questions)
    idx = st.session_state.step
    q = questions[idx]

    # Компактная информационная карточка для смартфона
    with st.container(border=True):
        st.markdown(
            f"🪪 Позывной: **{user['codename']}**  \n"
            f"🎓 Класс: **{user['grade']}** ({user['league']}) | ⭐ Баллы: **{st.session_state.score}**"
        )
        st.progress((idx) / total_q, text=f"Лаборатория {idx + 1} из {total_q} • Собрано букв крио-ключа: {len(st.session_state.unlocked)}/8")
        render_key_bar(st.session_state.unlocked)

    st.subheader(q["location"])
    st.info(q["story"])

    # Честная кнопка подсказки (без возможности подсмотреть бесплатно)
    if not st.session_state.used_hint and not st.session_state.answered:
        if st.button("💡 Взять научную подсказку (-2 балла при верном ответе)", use_container_width=True):
            st.session_state.used_hint = True
            st.rerun()

    if st.session_state.used_hint:
        st.warning(f"**Подсказка лаборатории:** {q['hint']}")

    # Форма ответа (исключает двойные нажатия на мобильных устройствах)
    with st.form(key=f"answer_form_{idx}"):
        st.markdown(f"**Задание:** {q['question']}")

        user_answer = None
        if q["type"] == "radio":
            user_answer = st.radio(
                "Выберите один вариант:",
                q["options"],
                index=None,
                disabled=st.session_state.answered
            )
        elif q["type"] == "checkboxes":
            selected = []
            for opt in q["options"]:
                if st.checkbox(opt, disabled=st.session_state.answered):
                    selected.append(opt)
            user_answer = selected
        elif q["type"] == "number":
            user_answer = st.number_input(
                "Введите целое число:",
                step=1,
                value=None,
                placeholder="Нажмите для ввода числа...",
                disabled=st.session_state.answered
            )

        submit_ans = st.form_submit_button(
            "Проверить и активировать узел ⚡",
            type="primary",
            disabled=st.session_state.answered,
            use_container_width=True
        )

    if submit_ans and not st.session_state.answered:
        if user_answer is None or user_answer == []:
            st.error("Пожалуйста, выберите или введите ответ перед проверкой!")
        else:
            is_correct = False
            if q["type"] in ["radio", "number"]:
                is_correct = (user_answer == q["answer"])
            elif q["type"] == "checkboxes":
                is_correct = (set(user_answer) == set(q["answer"]))

            st.session_state.answered = True
            st.session_state.last_correct = is_correct
            st.session_state.unlocked.append(SECRET_WORD[idx])

            if is_correct:
                pts = 8 if st.session_state.used_hint else 10
                st.session_state.score += pts
                st.session_state.history.append(f"{q['subject']}:✅({pts})")
            else:
                st.session_state.history.append(f"{q['subject']}:❌(0)")
            st.rerun()

    # Вывод разбора после ответа
    if st.session_state.answered:
        letter = SECRET_WORD[idx]
        if st.session_state.last_correct:
            earned = 8 if st.session_state.used_hint else 10
            st.success(
                f"✅ **Верно! +{earned} баллов.** Получена буква крио-ключа: **«{letter}»**  \n"
                f"**Научное объяснение:** {q['explanation']}"
            )
        else:
            st.error(
                f"❌ **Ошибка калибровки (0 баллов).** Резервный генератор все равно открыл букву **«{letter}»**!  \n"
                f"**Как правильно:** {q['explanation']}"
            )

        next_label = "В следующую лабораторию ➡️" if idx + 1 < total_q else "Собрать слово «СНЕЖИНКА» и запустить Часы! 🎆"
        if st.button(next_label, type="primary", use_container_width=True):
            if idx + 1 < total_q:
                st.session_state.step += 1
                st.session_state.answered = False
                st.session_state.used_hint = False
                st.rerun()
            else:
                elapsed = int(round(time.time() - st.session_state.start_time))
                st.session_state.elapsed = elapsed
                save_result({
                    "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "LastName": user["last_name"],
                    "FirstName": user["first_name"],
                    "Grade": user["grade"],
                    "League": user["league"],
                    "Codename": user["codename"],
                    "Score": st.session_state.score,
                    "TimeSec": elapsed,
                    "Details": " | ".join(st.session_state.history)
                })
                st.session_state.stage = "finish"
                st.rerun()

# --- ЭКРАН 3: ФИНАЛ, ПОЗДРАВЛЕНИЕ ОТ УЧИТЕЛЕЙ И ЛИДЕРБОРД ---
elif st.session_state.stage == "finish":
    st.snow()
    user = st.session_state.user
    score = st.session_state.score
    max_score = len(QUEST_DATA[user["league"]]) * 10

    st.success("🎉 Крио-ключ **«С Н Е Ж И Н К А»** собран! Главный Хронометр запущен!")
    render_key_bar(SECRET_WORD)

    if score >= max_score * 0.85:
        rank = "🏆 Почетный Академик Снежных Наук"
    elif score >= max_score * 0.55:
        rank = "🔬 Ведущий Инженер Томской Экспедиции"
    else:
        rank = "❄️ Отважный Исследователь Арктики"

    # Адаптивная карточка диплома (отлично смотрится на экране телефона)
    with st.container(border=True):
        st.markdown(f"### 🎓 Сертификат участника экспедиции")
        st.markdown(
            f"* **Секретный позывной:** `{user['codename']}` *(сохраните скриншот!)*  \n"
            f"* **Присвоенное звание:** **{rank}**  \n"
            f"* **Набрано баллов:** **{score} из {max_score}**  \n"
            f"* **Время прохождения:** **{st.session_state.elapsed} сек.**  \n"
            f"* **Отчет по лабораториям:** {' • '.join(st.session_state.history)}"
        )

    # Душевное поздравление от учителей Школы № 19 г. Томска
    st.markdown("""
    <div class="teacher-card">
        <b>🎄 Дорогой ученик Школы № 19 города Томска!</b><br><br>
        Твои учителя поздравляют тебя с наступающим Новым годом и Рождеством! 
        Сегодня ты доказал(а), что законы физики, химии, биологии, географии, астрономии, информатики и математики 
        помогают творить настоящие чудеса. Пусть наступающий год принесет тебе крепкое сибирское здоровье, 
        верных друзей, яркие победы и отличное настроение. Счастливых и уютных зимних каникул!<br><br>
        <i>С теплом и гордостью за вас, педагогический коллектив МАОУ СОШ № 19 г. Томска ❤️</i>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("🏆 Таблица рекордов Школы № 19")
    st.caption("В рейтинге отображаются только секретные позывные. При равенстве баллов выше стоит тот, кто прошел квест быстрее.")

    df = load_results()
    if not df.empty:
        tab1, tab2 = st.tabs(["Лига 5–7 классов", "Лига 8–11 классов"])
        for tab, league_name in zip([tab1, tab2], ["5–7 классы", "8–11 классы"]):
            with tab:
                sub = df[df["League"] == league_name].copy()
                if sub.empty:
                    st.info("В этой лиге пока нет записей.")
                else:
                    sub["Score"] = pd.to_numeric(sub["Score"])
                    sub["TimeSec"] = pd.to_numeric(sub["TimeSec"])
                    sub = sub.sort_values(by=["Score", "TimeSec"], ascending=[False, True]).reset_index(drop=True)
                    sub.index += 1
                    public_board = sub[["Codename", "Grade", "Score", "TimeSec"]].rename(
                        columns={
                            "Codename": "Позывной",
                            "Grade": "Класс",
                            "Score": "Баллы",
                            "TimeSec": "Время (с)"
                        }
                    )
                    st.dataframe(public_board, use_container_width=True)
