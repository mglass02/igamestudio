from core.audit.logger import AuditLogger
import os

DB_PATH = "db/test_audit.db"

def setup_function():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

def test_chain_starts_valid():
    logger = AuditLogger(DB_PATH)
    result = logger.verify_chain()
    assert result["valid"]

def test_log_and_verify():
    logger = AuditLogger(DB_PATH)
    logger.log("WAGER_PLACED", {"wager_cents": 100}, player_id="p001")
    logger.log("GAME_COMPLETE", {"prize_cents": 300}, player_id="p001")
    result = logger.verify_chain()
    assert result["valid"]
    assert result["entries_checked"] == 2

def test_tamper_detected():
    logger = AuditLogger(DB_PATH)
    logger.log("WAGER_PLACED", {"wager_cents": 100}, player_id="p001")
    # Directly tamper with the database
    logger.conn.execute("UPDATE audit_log SET payload = ? WHERE seq = 1",
                       ('{"wager_cents": 999}',))
    logger.conn.commit()
    result = logger.verify_chain()
    assert not result["valid"]

