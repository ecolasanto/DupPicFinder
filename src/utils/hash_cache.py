"""SQLite-backed cache for file hash results.

Stores (file_path, file_size, mtime_float, algorithm) -> hash_value so that
unchanged files skip re-hashing on subsequent runs.

The database lives at ~/.cache/DupPicFinder/hash_cache.db by default.

All public methods must be called from the same thread that created the
HashCache instance.  Do NOT call them from ThreadPoolExecutor workers.
"""

import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from src.core.file_model import ImageFile
from src.core.hasher import HashAlgorithm


# Bump this integer whenever the schema changes incompatibly.
_SCHEMA_VERSION = 1

# Maximum number of paths per SQLite IN clause (SQLite limit is 999).
_CHUNK_SIZE = 900

_DDL_HASHES = """
CREATE TABLE IF NOT EXISTS file_hashes (
    file_path   TEXT    NOT NULL,
    file_size   INTEGER NOT NULL,
    mtime_float REAL    NOT NULL,
    algorithm   TEXT    NOT NULL,
    hash_value  TEXT    NOT NULL,
    PRIMARY KEY (file_path, algorithm)
)
"""

_DDL_VERSION = """
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER NOT NULL
)
"""


class HashCache:
    """SQLite-backed cache mapping file identity keys to hash values.

    Cache key: (file_path, file_size, mtime_float, algorithm)
    Cache value: hash_value (hex string)

    A cache entry is valid only when both the file size and modification time
    match the stored values.  Any change to file content will advance the mtime
    on modern filesystems (ext4, NTFS, APFS) and produce a cache miss.

    Usage::

        cache = HashCache()
        hits, misses = cache.lookup_batch(image_files, algorithm='md5')
        # ... hash the misses ...
        cache.store_batch(new_hashes, misses, algorithm='md5')
        cache.close()
    """

    def __init__(self, db_path: Optional[Path] = None):
        """Open (or create) the cache database.

        Args:
            db_path: Path to the SQLite file.  Defaults to
                     ~/.cache/DupPicFinder/hash_cache.db.
        """
        if db_path is None:
            cache_dir = Path.home() / ".cache" / "DupPicFinder"
            cache_dir.mkdir(parents=True, exist_ok=True)
            db_path = cache_dir / "hash_cache.db"

        self._db_path = Path(db_path)
        self._conn = sqlite3.connect(str(self._db_path))
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA synchronous=NORMAL")
        self._ensure_schema()

    # ------------------------------------------------------------------
    # Schema management
    # ------------------------------------------------------------------

    def _ensure_schema(self) -> None:
        """Create tables or recreate them if the schema version is stale."""
        cur = self._conn.cursor()
        cur.execute(_DDL_VERSION)
        row = cur.execute("SELECT version FROM schema_version").fetchone()
        existing_version = row[0] if row else None

        if existing_version != _SCHEMA_VERSION:
            # Cache data is disposable — wipe and start fresh.
            cur.execute("DROP TABLE IF EXISTS file_hashes")
            cur.execute("DELETE FROM schema_version")
            cur.execute(_DDL_HASHES)
            cur.execute(
                "INSERT INTO schema_version (version) VALUES (?)",
                (_SCHEMA_VERSION,),
            )
        else:
            cur.execute(_DDL_HASHES)

        self._conn.commit()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def lookup_batch(
        self,
        image_files: List[ImageFile],
        algorithm: HashAlgorithm,
    ) -> Tuple[Dict[Path, str], List[ImageFile]]:
        """Look up a batch of files in the cache.

        For each file, the cached entry is a hit only when both file_size and
        mtime_float match the values stored in the database.

        Args:
            image_files: Files to look up.
            algorithm: Hash algorithm to check ('md5' or 'sha256').

        Returns:
            A 2-tuple of:
              - hits: dict mapping Path -> cached hash for files that hit.
              - misses: list of ImageFile objects not in the cache or stale.
        """
        hits: Dict[Path, str] = {}
        misses: List[ImageFile] = []

        if not image_files:
            return hits, misses

        # Build path-string -> ImageFile map for O(1) lookups.
        key_map: Dict[str, ImageFile] = {
            str(img.path): img for img in image_files
        }
        paths = list(key_map.keys())

        # Fetch all matching rows in chunks to respect SQLite's variable limit.
        cached: Dict[str, Tuple[int, float, str]] = {}
        for i in range(0, len(paths), _CHUNK_SIZE):
            chunk = paths[i: i + _CHUNK_SIZE]
            placeholders = ",".join("?" * len(chunk))
            rows = self._conn.execute(
                f"SELECT file_path, file_size, mtime_float, hash_value "
                f"FROM file_hashes "
                f"WHERE file_path IN ({placeholders}) AND algorithm = ?",
                chunk + [algorithm],
            ).fetchall()
            for row in rows:
                cached[row[0]] = (row[1], row[2], row[3])

        # Classify each file as a hit or miss.
        for path_str, img in key_map.items():
            # Get current mtime from disk; treat missing files as misses.
            try:
                mtime = img.path.stat().st_mtime
            except OSError:
                misses.append(img)
                continue

            if path_str in cached:
                cached_size, cached_mtime, cached_hash = cached[path_str]
                if cached_size == img.size and abs(cached_mtime - mtime) < 1e-3:
                    hits[img.path] = cached_hash
                    continue

            misses.append(img)

        return hits, misses

    def store_batch(
        self,
        results: Dict[Path, str],
        image_files: List[ImageFile],
        algorithm: HashAlgorithm,
    ) -> None:
        """Persist a batch of freshly computed hashes to the cache.

        Args:
            results: Mapping of Path -> hash_value for files just hashed.
            image_files: Original ImageFile objects (used to obtain size/path).
            algorithm: Hash algorithm that was used.
        """
        if not results:
            return

        meta: Dict[Path, ImageFile] = {img.path: img for img in image_files}

        rows = []
        for path, hash_value in results.items():
            img = meta.get(path)
            if img is None:
                continue
            try:
                mtime = path.stat().st_mtime
            except OSError:
                continue  # File disappeared; skip caching.
            rows.append((str(path), img.size, mtime, algorithm, hash_value))

        if rows:
            self._conn.executemany(
                "INSERT OR REPLACE INTO file_hashes "
                "(file_path, file_size, mtime_float, algorithm, hash_value) "
                "VALUES (?, ?, ?, ?, ?)",
                rows,
            )
            self._conn.commit()

    def purge_missing_files(self) -> int:
        """Remove cache entries for files that no longer exist on disk.

        Returns:
            Number of rows deleted.
        """
        cur = self._conn.cursor()
        cur.execute("SELECT ROWID, file_path FROM file_hashes")
        rows = cur.fetchall()
        to_delete = [row[0] for row in rows if not Path(row[1]).exists()]
        if to_delete:
            for i in range(0, len(to_delete), _CHUNK_SIZE):
                chunk = to_delete[i: i + _CHUNK_SIZE]
                placeholders = ",".join("?" * len(chunk))
                cur.execute(
                    f"DELETE FROM file_hashes WHERE ROWID IN ({placeholders})",
                    chunk,
                )
            self._conn.commit()
        return len(to_delete)

    def get_entry_count(self) -> int:
        """Return the total number of rows in the cache.

        Returns:
            Integer row count.
        """
        row = self._conn.execute(
            "SELECT COUNT(*) FROM file_hashes"
        ).fetchone()
        return row[0] if row else 0

    def close(self) -> None:
        """Close the database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None

    def __enter__(self):
        """Support use as a context manager."""
        return self

    def __exit__(self, *_):
        """Close on context exit."""
        self.close()
