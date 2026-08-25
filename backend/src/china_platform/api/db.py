"""Stage 1 / S1.10 — psycopg2 connection pool with read-only enforcement.

Per docs/24 §4.
"""
from __future__ import annotations

import logging
from contextlib import contextmanager
from typing import Iterator

import psycopg2
from psycopg2 import pool

log = logging.getLogger(__name__)


class Database:
    """Threaded connection pool with per-session read-only enforcement."""

    def __init__(
        self,
        dsn: str,
        min_conn: int = 2,
        max_conn: int = 10,
    ) -> None:
        self._dsn = dsn
        self._pool = pool.ThreadedConnectionPool(
            min_conn,
            max_conn,
            dsn=dsn,
            connect_timeout=5,
        )
        log.info("DB pool initialized (min=%d, max=%d)", min_conn, max_conn)

    @contextmanager
    def session(self) -> Iterator[psycopg2.extensions.connection]:
        """Yield a connection; enforce read-only at session level.

        Per docs/24 §4.3: SET TRANSACTION READ ONLY per session.
        """
        conn = self._pool.getconn()
        try:
            with conn.cursor() as cur:
                cur.execute("SET TRANSACTION READ ONLY")
            yield conn
        finally:
            # Roll back any open txn (read-only sessions can't commit anyway)
            try:
                conn.rollback()
            except psycopg2.InterfaceError:
                pass
            self._pool.putconn(conn)

    def close(self) -> None:
        """Close all pool connections."""
        if self._pool is not None:
            self._pool.closeall()
            log.info("DB pool closed")

    @property
    def is_alive(self) -> bool:
        """Lightweight health check: ping DB."""
        try:
            with self.session() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
                    row = cur.fetchone()
                    return row == (1,)
        except (psycopg2.OperationalError, psycopg2.errors.Error) as exc:
            log.warning("DB ping failed: %s", exc)
            return False