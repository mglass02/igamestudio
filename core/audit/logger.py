import hashlib, json, time, uuid, sqlite3

class AuditLogger:
    """
    GLI Appendix B §B.3: tamper-evident hash-chained audit log.
    Any modification to a past entry breaks the chain.
    """
    def __init__(self, db_path: str = "db/audit.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._setup()
        self._last_hash = self._chain_head()

    def _setup(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                seq         INTEGER PRIMARY KEY AUTOINCREMENT,
                id          TEXT NOT NULL,
                timestamp   REAL NOT NULL,
                event_type  TEXT NOT NULL,
                player_id   TEXT,
                payload     TEXT NOT NULL,
                prev_hash   TEXT NOT NULL,
                entry_hash  TEXT NOT NULL
            )
        """)
        self.conn.commit()

    def _chain_head(self) -> str:
        row = self.conn.execute(
            "SELECT entry_hash FROM audit_log ORDER BY seq DESC LIMIT 1"
        ).fetchone()
        return row["entry_hash"] if row else "0" * 64

    def log(self, event_type: str, payload: dict, player_id: str = None) -> str:
        entry = {
            "id":          str(uuid.uuid4()),
            "timestamp":   time.time(),
            "event_type":  event_type,
            "player_id":   player_id,
            "payload":     payload,
            "prev_hash":   self._last_hash,
        }
        entry_str = json.dumps(entry, sort_keys=True)
        entry["entry_hash"] = hashlib.sha256(entry_str.encode()).hexdigest()
        self.conn.execute("""
            INSERT INTO audit_log
            (id, timestamp, event_type, player_id, payload, prev_hash, entry_hash)
            VALUES (?,?,?,?,?,?,?)
        """, (
            entry["id"], entry["timestamp"], entry["event_type"],
            entry["player_id"], json.dumps(entry["payload"]),
            entry["prev_hash"], entry["entry_hash"]
        ))
        self.conn.commit()
        self._last_hash = entry["entry_hash"]
        return entry["entry_hash"]

    def verify_chain(self) -> dict:
        """Run daily. If valid=False, something was tampered with."""
        rows = self.conn.execute(
            "SELECT * FROM audit_log ORDER BY seq ASC"
        ).fetchall()
        prev_hash = "0" * 64
        for row in rows:
            check = {
                "id": row["id"], "timestamp": row["timestamp"],
                "event_type": row["event_type"], "player_id": row["player_id"],
                "payload": json.loads(row["payload"]), "prev_hash": row["prev_hash"],
            }
            computed = hashlib.sha256(
                json.dumps(check, sort_keys=True).encode()
            ).hexdigest()
            if computed != row["entry_hash"] or row["prev_hash"] != prev_hash:
                return {"valid": False, "broken_at_seq": row["seq"]}
            prev_hash = row["entry_hash"]
        return {"valid": True, "entries_checked": len(rows)}
