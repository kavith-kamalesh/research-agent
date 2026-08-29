"""
Local Stress/Rumination Tracker — MVP
100% local. Data stored in SQLite on your machine. Nothing leaves localhost.
"""

import sqlite3
import datetime
import re
import os
from flask import Flask, render_template, request, jsonify, g

DB_PATH = os.path.join(os.path.dirname(__file__), "data.db")
app = Flask(__name__)

VAULT_PATH = os.path.expanduser("~/Desktop/Rumination-Journal")


def write_obsidian_note(entry: dict):
    try:
        os.makedirs(VAULT_PATH, exist_ok=True)
        now = datetime.datetime.now()
        filename = now.strftime("%Y-%m-%d-%H%M") + ".md"
        filepath = os.path.join(VAULT_PATH, filename)

        tags = ["check-in", "arc"]
        if entry.get("activity_tag"):
            tags.append(entry["activity_tag"])
        if entry.get("crisis_flag"):
            tags.append("flagged")

        frontmatter = (
            "---\n"
            f"date: {now.strftime('%Y-%m-%d')}\n"
            f"time: {now.strftime('%H:%M')}\n"
            f"index: {entry.get('index_score')}\n"
            f"self_report: {entry.get('self_report_subscore')}\n"
            f"somatic: {entry.get('somatic_subscore')}\n"
            f"text_signal: {entry.get('text_subscore')}\n"
            f"activity: {entry.get('activity_tag')}\n"
            f"habits: {entry.get('habit_pct')}\n"
            f"tags: [{', '.join(tags)}]\n"
            "---\n\n"
        )
        body = f"# Check-in — {now.strftime('%b %d, %Y')}\n\n{entry.get('journal_text', '')}\n"

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(frontmatter + body)
    except Exception as e:
        print("Obsidian export skipped (non-fatal):", e)

CRISIS_PATTERNS = [
    r"\bkill myself\b", r"\bsuicide\b", r"\bend it all\b", r"\bnot worth living\b",
    r"\bwant to die\b", r"\bcan't go on\b", r"\bcant go on\b", r"\bhurt myself\b",
    r"\bself harm\b", r"\bno reason to live\b",
]

CRISIS_MESSAGE = (
    "What you just wrote matters, and I don't want it to just sit in a log. "
    "If you're in India, you can reach the KIRAN mental health helpline anytime "
    "at 1800-599-0019 (toll-free), or the iCall helpline at 9152987821. "
    "If you're outside India, please look up a local crisis line right now. "
    "This app can't help you the way a person can — please reach out to one."
)

ABSOLUTIST_WORDS = {
    "always", "never", "everyone", "no one", "nobody", "everything", "nothing",
    "completely", "totally", "everytime", "every time", "forever", "impossible",
    "constantly", "all the time", "none", "everybody"
}

NEGATIVE_EMOTION_WORDS = {
    "sad", "hopeless", "worthless", "empty", "hurt", "pain", "alone", "lonely",
    "angry", "afraid", "scared", "anxious", "panic", "broken", "numb", "tired",
    "exhausted", "crying", "cry", "miss", "missing", "hate", "guilt", "ashamed",
    "worried", "worry", "regret", "grief", "devastated", "abandoned", "rejected"
}

PAST_FOCUS_WORDS = {
    "was", "were", "had", "used to", "back then", "before", "remember",
    "remembered", "used", "did", "went", "said", "told", "left", "ago"
}

SOMATIC_WORDS = {
    "chest", "heart racing", "can't breathe", "cant breathe", "tight", "tension",
    "shaking", "nauseous", "sick", "headache", "dizzy", "sweating", "panic attack",
    "can't sleep", "cant sleep", "insomnia", "racing thoughts"
}


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(DB_PATH)
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            journal_text TEXT,
            pss_scores TEXT,
            rrs_scores TEXT,
            activity_tag TEXT,
            text_subscore REAL,
            self_report_subscore REAL,
            index_score REAL,
            crisis_flag INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS incidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            rough_date TEXT,
            title TEXT,
            description TEXT
        );

        CREATE TABLE IF NOT EXISTS intake (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            trigger_type TEXT,
            trigger_date TEXT
        );

        CREATE TABLE IF NOT EXISTS phq9_screenings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            answers TEXT NOT NULL,
            total INTEGER NOT NULL,
            band TEXT NOT NULL,
            item9_flag INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS gad7_screenings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            answers TEXT NOT NULL,
            total INTEGER NOT NULL,
            band TEXT NOT NULL
        );
        """
    )
    cols = [r[1] for r in db.execute("PRAGMA table_info(entries)").fetchall()]
    if "sleep_disruption" not in cols:
        db.execute("ALTER TABLE entries ADD COLUMN sleep_disruption INTEGER DEFAULT 0")
    if "chest_tightness" not in cols:
        db.execute("ALTER TABLE entries ADD COLUMN chest_tightness INTEGER DEFAULT 0")
    if "appetite_change" not in cols:
        db.execute("ALTER TABLE entries ADD COLUMN appetite_change INTEGER DEFAULT 0")
    if "somatic_subscore" not in cols:
        db.execute("ALTER TABLE entries ADD COLUMN somatic_subscore REAL DEFAULT 0")
    if "habit_pct" not in cols:
        db.execute("ALTER TABLE entries ADD COLUMN habit_pct REAL DEFAULT NULL")
    db.commit()
    db.close()


def score_text(text: str) -> dict:
    if not text:
        return {"absolutist": 0, "negative_emotion": 0, "past_focus": 0,
                "somatic": 0, "word_count": 0, "text_subscore": 0.0}

    lower = text.lower()
    word_count = max(len(lower.split()), 1)

    def count_hits(vocab):
        hits = 0
        for term in vocab:
            hits += len(re.findall(r"\b" + re.escape(term) + r"\b", lower))
        return hits

    absolutist = count_hits(ABSOLUTIST_WORDS)
    neg_emotion = count_hits(NEGATIVE_EMOTION_WORDS)
    past_focus = count_hits(PAST_FOCUS_WORDS)
    somatic = count_hits(SOMATIC_WORDS)

    per100 = lambda c: (c / word_count) * 100
    raw = (
        per100(absolutist) * 1.5 +
        per100(neg_emotion) * 1.2 +
        per100(past_focus) * 0.8 +
        per100(somatic) * 1.5
    )
    text_subscore = min(round(raw, 1), 100.0)

    return {
        "absolutist": absolutist,
        "negative_emotion": neg_emotion,
        "past_focus": past_focus,
        "somatic": somatic,
        "word_count": word_count,
        "text_subscore": text_subscore,
    }


def score_self_report(pss_answers: list, rrs_answers) -> dict:
    pss = list(pss_answers) if pss_answers else []

    if isinstance(rrs_answers, (int, float)):
        rrs = [int(rrs_answers)]
    else:
        rrs = list(rrs_answers) if rrs_answers else [0]

    if pss:
        reverse_idx = {3, 4, 6, 7}
        pss_total = 0
        for i, val in enumerate(pss):
            v = val if i not in reverse_idx else (4 - val)
            pss_total += v
        pss_pct = (pss_total / 40) * 100
    else:
        pss_total = 0
        pss_pct = None

    rrs_total = sum(rrs)
    rrs_max = 3 * len(rrs)
    rrs_pct = (rrs_total / rrs_max) * 100 if rrs_max else 0

    if pss_pct is None:
        self_report_subscore = round(rrs_pct, 1)
    else:
        self_report_subscore = round((pss_pct * 0.5) + (rrs_pct * 0.5), 1)

    return {
        "pss_total": pss_total,
        "pss_pct": round(pss_pct, 1) if pss_pct is not None else None,
        "rrs_total": rrs_total,
        "rrs_pct": round(rrs_pct, 1),
        "self_report_subscore": self_report_subscore,
    }


def score_somatic(sleep_disruption: int, chest_tightness: int, appetite_change: int) -> float:
    items = [sleep_disruption or 0, chest_tightness or 0, appetite_change or 0]
    total = sum(items)
    max_total = 9
    return round((total / max_total) * 100, 1)


def check_crisis(text: str) -> bool:
    if not text:
        return False
    lower = text.lower()
    return any(re.search(pat, lower) for pat in CRISIS_PATTERNS)


PHQ9_ITEMS = [
    "Little interest or pleasure in doing things",
    "Feeling down, depressed, or hopeless",
    "Trouble falling/staying asleep, or sleeping too much",
    "Feeling tired or having little energy",
    "Poor appetite or overeating",
    "Feeling bad about yourself — or that you're a failure, or have let yourself or your family down",
    "Trouble concentrating on things, such as reading or watching TV",
    "Moving or speaking noticeably slowly, or being fidgety/restless",
    "Thoughts that you would be better off dead, or of hurting yourself in some way",
]

PHQ9_BANDS = [
    (0, 4, "minimal"),
    (5, 9, "mild"),
    (10, 14, "moderate"),
    (15, 19, "moderately severe"),
    (20, 27, "severe"),
]

GAD7_ITEMS = [
    "Feeling nervous, anxious, or on edge",
    "Not being able to stop or control worrying",
    "Worrying too much about different things",
    "Trouble relaxing",
    "Being so restless that it's hard to sit still",
    "Becoming easily annoyed or irritable",
    "Feeling afraid, as if something awful might happen",
]

GAD7_BANDS = [
    (0, 4, "minimal"),
    (5, 9, "mild"),
    (10, 14, "moderate"),
    (15, 21, "severe"),
]


def score_gad7(answers: list) -> dict:
    a = list(answers) if answers else [0] * 7
    a = (a + [0] * 7)[:7]
    total = sum(a)
    band = next((label for lo, hi, label in GAD7_BANDS if lo <= total <= hi), "unknown")
    return {"answers": a, "total": total, "band": band}


def score_phq9(answers: list) -> dict:
    a = list(answers) if answers else [0] * 9
    a = (a + [0] * 9)[:9]
    total = sum(a)
    band = next((label for lo, hi, label in PHQ9_BANDS if lo <= total <= hi), "unknown")
    item9_flag = a[8] > 0
    return {
        "answers": a,
        "total": total,
        "band": band,
        "item9_flag": item9_flag,
    }


def score_habits(habits: dict) -> dict:
    keys = ["gratitude", "decision", "movement", "social", "sleep_regular", "named_rumination"]
    checked = sum(1 for k in keys if habits.get(k))
    total = len(keys)
    pct = round((checked / total) * 100, 1) if total else 0.0
    return {"checked": checked, "total": total, "habit_pct": pct}


def combine_index(text_subscore: float, self_report_subscore: float,
                   somatic_subscore: float = 0.0, habit_pct: float = None) -> float:
    if habit_pct is None:
        return round((self_report_subscore * 0.50) + (somatic_subscore * 0.25) + (text_subscore * 0.25), 1)
    habit_inverse = 100 - habit_pct
    return round(
        (self_report_subscore * 0.40) + (somatic_subscore * 0.20) +
        (text_subscore * 0.20) + (habit_inverse * 0.20), 1
    )


@app.route("/")
def index():
    return render_template("card_stack_live.html")


@app.route("/dashboard")
def dashboard_ui():
    return render_template("index.html")


@app.route("/api/entry", methods=["POST"])
def create_entry():
    data = request.get_json(force=True)
    journal_text = data.get("journal_text", "")
    pss_answers = data.get("pss_answers", [])
    rrs_answers = data.get("rrs_answers", [])
    activity_tag = data.get("activity_tag", "neutral")
    sleep_disruption = int(data.get("sleep_disruption", 0))
    chest_tightness = int(data.get("chest_tightness", 0))
    appetite_change = int(data.get("appetite_change", 0))
    habits = data.get("habits", None)

    text_result = score_text(journal_text)
    self_result = score_self_report(pss_answers, rrs_answers)
    somatic_subscore = score_somatic(sleep_disruption, chest_tightness, appetite_change)
    habits_result = score_habits(habits) if habits is not None else None
    habit_pct = habits_result["habit_pct"] if habits_result else None
    idx = combine_index(text_result["text_subscore"], self_result["self_report_subscore"],
                         somatic_subscore, habit_pct)
    crisis = check_crisis(journal_text)

    db = get_db()
    db.execute(
        """INSERT INTO entries
           (created_at, journal_text, pss_scores, rrs_scores, activity_tag,
            text_subscore, self_report_subscore, index_score, crisis_flag,
            sleep_disruption, chest_tightness, appetite_change, somatic_subscore,
            habit_pct)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            datetime.datetime.now().isoformat(),
            journal_text,
            str(pss_answers),
            str(rrs_answers),
            activity_tag,
            text_result["text_subscore"],
            self_result["self_report_subscore"],
            idx,
            1 if crisis else 0,
            sleep_disruption,
            chest_tightness,
            appetite_change,
            somatic_subscore,
            habit_pct,
        ),
    )
    db.commit()

    write_obsidian_note({
        "journal_text": journal_text,
        "activity_tag": activity_tag,
        "index_score": idx,
        "self_report_subscore": self_result["self_report_subscore"],
        "somatic_subscore": somatic_subscore,
        "text_subscore": text_result["text_subscore"],
        "habit_pct": habit_pct,
        "crisis_flag": crisis,
    })

    response = {
        "index_score": idx,
        "text_breakdown": text_result,
        "self_report_breakdown": self_result,
        "somatic_subscore": somatic_subscore,
        "habits_breakdown": habits_result,
        "crisis_flag": crisis,
        "crisis_message": CRISIS_MESSAGE if crisis else None,
    }
    return jsonify(response)


@app.route("/api/intake", methods=["POST"])
def create_intake():
    data = request.get_json(force=True)
    db = get_db()
    db.execute(
        "INSERT INTO intake (created_at, trigger_type, trigger_date) VALUES (?, ?, ?)",
        (datetime.datetime.now().isoformat(), data.get("trigger_type", ""), data.get("trigger_date", "")),
    )
    db.commit()
    return jsonify({"status": "ok"})


@app.route("/api/intake", methods=["GET"])
def get_intake():
    db = get_db()
    row = db.execute("SELECT * FROM intake ORDER BY created_at DESC LIMIT 1").fetchone()
    return jsonify(dict(row) if row else None)


@app.route("/api/phq9", methods=["POST"])
def create_phq9():
    data = request.get_json(force=True)
    answers = data.get("answers", [])
    result = score_phq9(answers)

    db = get_db()
    db.execute(
        "INSERT INTO phq9_screenings (created_at, answers, total, band, item9_flag) "
        "VALUES (?, ?, ?, ?, ?)",
        (
            datetime.datetime.now().isoformat(),
            str(result["answers"]),
            result["total"],
            result["band"],
            1 if result["item9_flag"] else 0,
        ),
    )
    db.commit()

    response = {
        "total": result["total"],
        "band": result["band"],
        "item9_flag": result["item9_flag"],
        "crisis_message": CRISIS_MESSAGE if result["item9_flag"] else None,
        "items": PHQ9_ITEMS,
    }
    return jsonify(response)


@app.route("/api/phq9", methods=["GET"])
def list_phq9():
    db = get_db()
    rows = db.execute(
        "SELECT id, created_at, total, band, item9_flag FROM phq9_screenings "
        "ORDER BY created_at DESC"
    ).fetchall()
    return jsonify([dict(r) for r in rows])


@app.route("/api/gad7", methods=["POST"])
def create_gad7():
    data = request.get_json(force=True)
    answers = data.get("answers", [])
    result = score_gad7(answers)

    db = get_db()
    db.execute(
        "INSERT INTO gad7_screenings (created_at, answers, total, band) VALUES (?, ?, ?, ?)",
        (
            datetime.datetime.now().isoformat(),
            str(result["answers"]),
            result["total"],
            result["band"],
        ),
    )
    db.commit()

    response = {
        "total": result["total"],
        "band": result["band"],
        "items": GAD7_ITEMS,
    }
    return jsonify(response)


@app.route("/api/gad7", methods=["GET"])
def list_gad7():
    db = get_db()
    rows = db.execute(
        "SELECT id, created_at, total, band FROM gad7_screenings ORDER BY created_at DESC"
    ).fetchall()
    return jsonify([dict(r) for r in rows])


@app.route("/api/entries", methods=["GET"])
def list_entries():
    db = get_db()
    rows = db.execute(
        "SELECT id, created_at, journal_text, activity_tag, text_subscore, "
        "self_report_subscore, index_score, crisis_flag FROM entries "
        "ORDER BY created_at ASC"
    ).fetchall()
    return jsonify([dict(r) for r in rows])


@app.route("/api/incident", methods=["POST"])
def create_incident():
    data = request.get_json(force=True)
    db = get_db()
    db.execute(
        "INSERT INTO incidents (created_at, rough_date, title, description) "
        "VALUES (?, ?, ?, ?)",
        (
            datetime.datetime.now().isoformat(),
            data.get("rough_date", ""),
            data.get("title", ""),
            data.get("description", ""),
        ),
    )
    db.commit()
    return jsonify({"status": "ok"})


@app.route("/api/incidents", methods=["GET"])
def list_incidents():
    db = get_db()
    rows = db.execute(
        "SELECT * FROM incidents ORDER BY created_at DESC"
    ).fetchall()
    return jsonify([dict(r) for r in rows])


if __name__ == "__main__":
    init_db()
    print("Local tracker running.")
    print("All data stays in:", DB_PATH)
    app.run(debug=True, port=5000)
