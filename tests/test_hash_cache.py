"""Tests for the SQLite-backed hash cache.

All tests use a temporary database path so they never touch the real
~/.cache/DupPicFinder/hash_cache.db.  No Qt or threading is required
because HashCache is a pure Python / SQLite class.
"""

import shutil
import tempfile
import time
import unittest
from datetime import datetime
from pathlib import Path

from src.utils.hash_cache import HashCache, _SCHEMA_VERSION
import src.utils.hash_cache as cache_module


def _make_image_file(path: Path):
    """Create an ImageFile from a real file on disk."""
    from src.core.file_model import ImageFile
    stat = path.stat()
    return ImageFile(
        path=path,
        size=stat.st_size,
        created=datetime.fromtimestamp(stat.st_ctime),
        modified=datetime.fromtimestamp(stat.st_mtime),
    )


class TestHashCacheBasics(unittest.TestCase):
    """Unit tests for HashCache CRUD behaviour."""

    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.db_path = self.temp_dir / "test_cache.db"
        self.cache = HashCache(db_path=self.db_path)

        # Two real files so stat() works inside lookup_batch.
        self.file1 = self.temp_dir / "image1.jpg"
        self.file1.write_bytes(b"\xff\xd8\xff" + b"A" * 100)
        self.img1 = _make_image_file(self.file1)

        self.file2 = self.temp_dir / "image2.jpg"
        self.file2.write_bytes(b"\xff\xd8\xff" + b"B" * 100)
        self.img2 = _make_image_file(self.file2)

    def tearDown(self):
        self.cache.close()
        shutil.rmtree(self.temp_dir)

    # ------------------------------------------------------------------
    # lookup_batch: empty cache
    # ------------------------------------------------------------------

    def test_lookup_empty_cache_all_misses(self):
        """All files are misses when the cache is empty."""
        hits, misses = self.cache.lookup_batch([self.img1, self.img2], 'md5')
        self.assertEqual(hits, {})
        self.assertEqual(len(misses), 2)

    def test_lookup_empty_input(self):
        """Empty input returns empty hits and empty misses."""
        hits, misses = self.cache.lookup_batch([], 'md5')
        self.assertEqual(hits, {})
        self.assertEqual(misses, [])

    # ------------------------------------------------------------------
    # store_batch then lookup_batch: hits
    # ------------------------------------------------------------------

    def test_store_then_lookup_hit(self):
        """Stored entry is returned as a hit on the next lookup."""
        self.cache.store_batch({self.file1: "deadbeef01"}, [self.img1], 'md5')
        hits, misses = self.cache.lookup_batch([self.img1], 'md5')
        self.assertIn(self.file1, hits)
        self.assertEqual(hits[self.file1], "deadbeef01")
        self.assertEqual(misses, [])

    def test_store_multiple_then_lookup(self):
        """All stored entries are returned as hits."""
        self.cache.store_batch(
            {self.file1: "aaa111", self.file2: "bbb222"},
            [self.img1, self.img2],
            'md5',
        )
        hits, misses = self.cache.lookup_batch([self.img1, self.img2], 'md5')
        self.assertEqual(len(hits), 2)
        self.assertEqual(len(misses), 0)
        self.assertEqual(hits[self.file1], "aaa111")
        self.assertEqual(hits[self.file2], "bbb222")

    def test_partial_hit(self):
        """Only the stored file is a hit; the other is a miss."""
        self.cache.store_batch({self.file1: "hash1"}, [self.img1], 'md5')
        hits, misses = self.cache.lookup_batch([self.img1, self.img2], 'md5')
        self.assertEqual(len(hits), 1)
        self.assertEqual(len(misses), 1)
        self.assertIn(self.file1, hits)
        self.assertIn(self.img2, misses)

    # ------------------------------------------------------------------
    # Algorithm isolation
    # ------------------------------------------------------------------

    def test_algorithm_is_part_of_key(self):
        """An md5 entry does not satisfy a sha256 lookup."""
        self.cache.store_batch({self.file1: "md5hash"}, [self.img1], 'md5')
        hits, misses = self.cache.lookup_batch([self.img1], 'sha256')
        self.assertEqual(hits, {})
        self.assertEqual(len(misses), 1)

    def test_both_algorithms_stored_independently(self):
        """md5 and sha256 entries coexist for the same file."""
        self.cache.store_batch({self.file1: "md5hash"}, [self.img1], 'md5')
        self.cache.store_batch({self.file1: "sha256hash"}, [self.img1], 'sha256')
        hits_md5, _ = self.cache.lookup_batch([self.img1], 'md5')
        hits_sha, _ = self.cache.lookup_batch([self.img1], 'sha256')
        self.assertEqual(hits_md5[self.file1], "md5hash")
        self.assertEqual(hits_sha[self.file1], "sha256hash")

    # ------------------------------------------------------------------
    # Cache invalidation: size change
    # ------------------------------------------------------------------

    def test_size_change_causes_miss(self):
        """A cached entry becomes a miss when the file is larger."""
        self.cache.store_batch({self.file1: "oldhash"}, [self.img1], 'md5')
        # Grow the file.
        self.file1.write_bytes(b"\xff\xd8\xff" + b"A" * 200)
        updated_img = _make_image_file(self.file1)
        hits, misses = self.cache.lookup_batch([updated_img], 'md5')
        self.assertEqual(hits, {})
        self.assertEqual(len(misses), 1)

    # ------------------------------------------------------------------
    # Cache invalidation: mtime change
    # ------------------------------------------------------------------

    def test_mtime_change_causes_miss(self):
        """A cached entry becomes a miss when the file is re-written."""
        self.cache.store_batch({self.file1: "oldhash"}, [self.img1], 'md5')
        # Sleep briefly so mtime advances, then rewrite the file.
        time.sleep(0.02)
        self.file1.write_bytes(self.file1.read_bytes())
        updated_img = _make_image_file(self.file1)
        hits, misses = self.cache.lookup_batch([updated_img], 'md5')
        self.assertEqual(hits, {})
        self.assertEqual(len(misses), 1)

    # ------------------------------------------------------------------
    # INSERT OR REPLACE behaviour
    # ------------------------------------------------------------------

    def test_store_overwrites_old_entry(self):
        """Re-storing a file updates its hash value."""
        self.cache.store_batch({self.file1: "oldhash"}, [self.img1], 'md5')
        self.cache.store_batch({self.file1: "newhash"}, [self.img1], 'md5')
        hits, _ = self.cache.lookup_batch([self.img1], 'md5')
        self.assertEqual(hits[self.file1], "newhash")

    def test_store_empty_results_is_noop(self):
        """Calling store_batch with an empty dict does not raise."""
        self.cache.store_batch({}, [self.img1], 'md5')
        self.assertEqual(self.cache.get_entry_count(), 0)

    # ------------------------------------------------------------------
    # Persistence across close/open
    # ------------------------------------------------------------------

    def test_data_survives_reopen(self):
        """Cached data persists after closing and reopening the database."""
        self.cache.store_batch({self.file1: "persistedhash"}, [self.img1], 'md5')
        self.cache.close()
        reopened = HashCache(db_path=self.db_path)
        try:
            hits, _ = reopened.lookup_batch([self.img1], 'md5')
            self.assertEqual(hits[self.file1], "persistedhash")
        finally:
            reopened.close()

    # ------------------------------------------------------------------
    # Utility methods
    # ------------------------------------------------------------------

    def test_get_entry_count_empty(self):
        """get_entry_count returns 0 for an empty cache."""
        self.assertEqual(self.cache.get_entry_count(), 0)

    def test_get_entry_count_after_store(self):
        """get_entry_count reflects the number of stored rows."""
        self.cache.store_batch({self.file1: "h1"}, [self.img1], 'md5')
        self.assertEqual(self.cache.get_entry_count(), 1)
        self.cache.store_batch({self.file2: "h2"}, [self.img2], 'md5')
        self.assertEqual(self.cache.get_entry_count(), 2)

    def test_purge_missing_files(self):
        """purge_missing_files removes entries for deleted files."""
        self.cache.store_batch(
            {self.file1: "h1", self.file2: "h2"},
            [self.img1, self.img2],
            'md5',
        )
        self.file1.unlink()
        deleted = self.cache.purge_missing_files()
        self.assertEqual(deleted, 1)
        self.assertEqual(self.cache.get_entry_count(), 1)

    def test_purge_no_missing_files(self):
        """purge_missing_files returns 0 when all files still exist."""
        self.cache.store_batch({self.file1: "h1"}, [self.img1], 'md5')
        self.assertEqual(self.cache.purge_missing_files(), 0)

    # ------------------------------------------------------------------
    # Context manager
    # ------------------------------------------------------------------

    def test_context_manager(self):
        """HashCache works as a context manager."""
        ctx_db = self.temp_dir / "ctx.db"
        with HashCache(db_path=ctx_db) as cache:
            cache.store_batch({self.file2: "ctxhash"}, [self.img2], 'md5')
            hits, _ = cache.lookup_batch([self.img2], 'md5')
            self.assertEqual(hits[self.file2], "ctxhash")
        # Connection is closed; re-opening should still work.
        with HashCache(db_path=ctx_db) as cache2:
            hits2, _ = cache2.lookup_batch([self.img2], 'md5')
            self.assertEqual(hits2[self.file2], "ctxhash")

    # ------------------------------------------------------------------
    # Schema migration
    # ------------------------------------------------------------------

    def test_schema_version_migration_wipes_data(self):
        """A schema version change causes a clean slate (old data wiped)."""
        self.cache.store_batch({self.file1: "old"}, [self.img1], 'md5')
        self.cache.close()

        original = cache_module._SCHEMA_VERSION
        try:
            cache_module._SCHEMA_VERSION = 999
            fresh = HashCache(db_path=self.db_path)
            self.assertEqual(fresh.get_entry_count(), 0)
            fresh.close()
        finally:
            cache_module._SCHEMA_VERSION = original

    # ------------------------------------------------------------------
    # Missing file during lookup
    # ------------------------------------------------------------------

    def test_lookup_missing_file_returns_cached_hash(self):
        """A cached file that has since been deleted is still a hit.

        lookup_batch uses ImageFile.modified (from the scan) rather than
        calling stat() on disk, so it cannot detect files deleted after the
        scan.  HashWorker._hash_file handles the FileNotFoundError gracefully
        if the file has truly disappeared by hash time.
        """
        self.cache.store_batch({self.file1: "h1"}, [self.img1], 'md5')
        self.file1.unlink()
        hits, misses = self.cache.lookup_batch([self.img1], 'md5')
        # The cached entry is returned as a hit because no stat() is called.
        self.assertIn(self.file1, hits)
        self.assertEqual(misses, [])


if __name__ == '__main__':
    unittest.main()
