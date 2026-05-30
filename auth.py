# auth.py

import sqlite3
import bcrypt
import os
import shutil

# Absolute path — works correctly on Mac regardless of working directory
DB_NAME = os.path.join(os.path.dirname(os.path.abspath(__file__)), "users.db")

# Required columns for the users table
REQUIRED_USER_COLS = {"id", "name", "mobile", "email", "password"}

STARTING_BALANCE = 1_000_000.0   # ₹10,00,000 virtual cash


# ── Database Connection ────────────────────────────────────────────
def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


# ── Schema validator ───────────────────────────────────────────────
def _get_columns(conn: sqlite3.Connection, table: str) -> set:
    """Return set of column names for a table, or empty set if table missing."""
    try:
        rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
        return {row[1] for row in rows}
    except Exception:
        return set()


def _schema_is_valid(conn: sqlite3.Connection) -> bool:
    """Return True only if users table has all required columns."""
    cols = _get_columns(conn, "users")
    return REQUIRED_USER_COLS.issubset(cols)


# ── Initialize / repair Database ───────────────────────────────────
def init_db():
    """
    Creates all tables with correct schema.
    If the existing DB is missing critical columns (broken schema),
    it backs up the old file and creates a fresh DB automatically.
    """
    if os.path.exists(DB_NAME):
        try:
            with get_conn() as conn:
                if not _schema_is_valid(conn):
                    broken_path = DB_NAME + ".broken.bak"
                    shutil.copy2(DB_NAME, broken_path)
                    os.remove(DB_NAME)
        except Exception:
            if os.path.exists(DB_NAME):
                os.remove(DB_NAME)

    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                name       TEXT    NOT NULL,
                mobile     TEXT    DEFAULT '',
                email      TEXT    UNIQUE NOT NULL,
                password   TEXT    NOT NULL,
                created_at TEXT    DEFAULT (datetime('now'))
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS watchlist (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id    INTEGER NOT NULL,
                symbol     TEXT    NOT NULL,
                added_at   TEXT    DEFAULT (datetime('now')),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE (user_id, symbol)
            )
        """)

        # ── Paper Trading: virtual wallet ──────────────────────────
        conn.execute("""
            CREATE TABLE IF NOT EXISTS paper_wallet (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id    INTEGER UNIQUE NOT NULL,
                cash       REAL    NOT NULL DEFAULT 1000000.0,
                created_at TEXT    DEFAULT (datetime('now')),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        # ── Paper Trading: open holdings ───────────────────────────
        # avg_price = weighted average buy price
        conn.execute("""
            CREATE TABLE IF NOT EXISTS paper_holdings (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id    INTEGER NOT NULL,
                symbol     TEXT    NOT NULL,
                qty        REAL    NOT NULL DEFAULT 0,
                avg_price  REAL    NOT NULL DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE (user_id, symbol)
            )
        """)

        # ── Paper Trading: trade log ───────────────────────────────
        # action: 'BUY' | 'SELL'
        conn.execute("""
            CREATE TABLE IF NOT EXISTS paper_trades (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id    INTEGER NOT NULL,
                symbol     TEXT    NOT NULL,
                action     TEXT    NOT NULL,
                qty        REAL    NOT NULL,
                price      REAL    NOT NULL,
                total      REAL    NOT NULL,
                traded_at  TEXT    DEFAULT (datetime('now')),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        conn.commit()


# ── Register User ─────────────────────────────────────────────────
def register_user(name: str, mobile: str, email: str, password: str) -> bool:
    """
    Returns True if registration successful.
    Returns False if email already exists or any error occurs.
    """
    try:
        hashed_pw = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt(rounds=12)
        ).decode("utf-8")

        with get_conn() as conn:
            conn.execute(
                "INSERT INTO users (name, mobile, email, password) VALUES (?, ?, ?, ?)",
                (
                    name.strip(),
                    mobile.strip() if mobile else "",
                    email.strip().lower(),
                    hashed_pw,
                )
            )
            conn.commit()
        return True

    except sqlite3.IntegrityError:
        return False
    except Exception:
        return False


# ── Login User ────────────────────────────────────────────────────
def login_user(email: str, password: str) -> tuple:
    """
    Returns (user_id, name) on success.
    Returns (None, None) on any failure.
    """
    if not email or not password:
        return None, None

    try:
        with get_conn() as conn:
            row = conn.execute(
                "SELECT id, name, password FROM users WHERE email = ?",
                (email.strip().lower(),)
            ).fetchone()

        if row and bcrypt.checkpw(
            password.encode("utf-8"),
            row["password"].encode("utf-8")
        ):
            return row["id"], row["name"]

    except Exception:
        pass

    return None, None


# ── Paper Trading Helpers ─────────────────────────────────────────

def get_or_create_wallet(user_id: int) -> float:
    """Return current cash balance, creating wallet with starting balance if needed."""
    with get_conn() as conn:
        row = conn.execute(
            "SELECT cash FROM paper_wallet WHERE user_id=?", (user_id,)
        ).fetchone()
        if row is None:
            conn.execute(
                "INSERT INTO paper_wallet (user_id, cash) VALUES (?, ?)",
                (user_id, STARTING_BALANCE)
            )
            conn.commit()
            return STARTING_BALANCE
        return float(row["cash"])


def get_holdings(user_id: int) -> list:
    """Return list of dicts: symbol, qty, avg_price."""
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT symbol, qty, avg_price FROM paper_holdings WHERE user_id=? AND qty > 0 ORDER BY symbol",
            (user_id,)
        ).fetchall()
    return [{"symbol": r["symbol"], "qty": float(r["qty"]), "avg_price": float(r["avg_price"])} for r in rows]


def get_trades(user_id: int, limit: int = 50) -> list:
    """Return most recent trades."""
    with get_conn() as conn:
        rows = conn.execute(
            """SELECT symbol, action, qty, price, total, traded_at
               FROM paper_trades WHERE user_id=? ORDER BY id DESC LIMIT ?""",
            (user_id, limit)
        ).fetchall()
    return [dict(r) for r in rows]


def execute_trade(user_id: int, symbol: str, action: str, qty: float, price: float) -> tuple:
    """
    Execute a BUY or SELL paper trade.
    Returns (success: bool, message: str)
    """
    if qty <= 0 or price <= 0:
        return False, "Quantity and price must be positive."

    total = round(qty * price, 2)
    action = action.upper()

    with get_conn() as conn:
        # Ensure wallet exists
        wallet_row = conn.execute(
            "SELECT cash FROM paper_wallet WHERE user_id=?", (user_id,)
        ).fetchone()
        if wallet_row is None:
            conn.execute(
                "INSERT INTO paper_wallet (user_id, cash) VALUES (?, ?)",
                (user_id, STARTING_BALANCE)
            )
            conn.commit()
            cash = STARTING_BALANCE
        else:
            cash = float(wallet_row["cash"])

        holding = conn.execute(
            "SELECT qty, avg_price FROM paper_holdings WHERE user_id=? AND symbol=?",
            (user_id, symbol)
        ).fetchone()
        held_qty    = float(holding["qty"])       if holding else 0.0
        held_avg    = float(holding["avg_price"]) if holding else 0.0

        if action == "BUY":
            if cash < total:
                return False, f"Insufficient funds. Need ₹{total:,.2f}, have ₹{cash:,.2f}."

            new_cash = round(cash - total, 2)
            new_qty  = held_qty + qty
            # Weighted average price
            new_avg  = round((held_qty * held_avg + qty * price) / new_qty, 4)

            conn.execute(
                "UPDATE paper_wallet SET cash=? WHERE user_id=?",
                (new_cash, user_id)
            )
            if holding:
                conn.execute(
                    "UPDATE paper_holdings SET qty=?, avg_price=? WHERE user_id=? AND symbol=?",
                    (new_qty, new_avg, user_id, symbol)
                )
            else:
                conn.execute(
                    "INSERT INTO paper_holdings (user_id, symbol, qty, avg_price) VALUES (?,?,?,?)",
                    (user_id, symbol, new_qty, new_avg)
                )

        elif action == "SELL":
            if held_qty < qty:
                return False, f"Not enough shares. You hold {held_qty:.4f}, trying to sell {qty:.4f}."

            new_cash = round(cash + total, 2)
            new_qty  = round(held_qty - qty, 6)

            conn.execute(
                "UPDATE paper_wallet SET cash=? WHERE user_id=?",
                (new_cash, user_id)
            )
            if new_qty <= 1e-6:
                conn.execute(
                    "DELETE FROM paper_holdings WHERE user_id=? AND symbol=?",
                    (user_id, symbol)
                )
            else:
                conn.execute(
                    "UPDATE paper_holdings SET qty=? WHERE user_id=? AND symbol=?",
                    (new_qty, user_id, symbol)
                )
        else:
            return False, "Invalid action. Use BUY or SELL."

        # Log the trade
        conn.execute(
            "INSERT INTO paper_trades (user_id, symbol, action, qty, price, total) VALUES (?,?,?,?,?,?)",
            (user_id, symbol, action, qty, price, total)
        )
        conn.commit()

    return True, f"{action} {qty} × {symbol} @ ₹{price:,.2f} executed."


def reset_wallet(user_id: int):
    """Reset everything back to starting balance for a user."""
    with get_conn() as conn:
        conn.execute("DELETE FROM paper_holdings WHERE user_id=?", (user_id,))
        conn.execute("DELETE FROM paper_trades    WHERE user_id=?", (user_id,))
        conn.execute(
            "INSERT OR REPLACE INTO paper_wallet (user_id, cash) VALUES (?,?)",
            (user_id, STARTING_BALANCE)
        )
        conn.commit()


# ── Initialize DB on import ────────────────────────────────────────
init_db()