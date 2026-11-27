"""Synthetic container tests; no game data or keys required."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'tools/xci/split_xci.py'

class SplitReportTests(unittest.TestCase):
    def run_case(self, mismatch=False, truncate=False):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            shutil.copy2(SCRIPT, root / 'split_xci.py')
            payloads = [b'synthetic program', b'synthetic metadata']
            records = []
            offset = 0
            for kind, data in zip((0, 1), payloads):
                digest = hashlib.sha256(data).hexdigest()[:32]
                if mismatch and kind == 0:
                    digest = '0' * 32
                records.append(dict(name=digest+'.nca', nca_offset=offset,
                                    size=len(data), content_type=kind, patch=False))
                offset += len(data)
            (root/'container.json').write_text(json.dumps(records))
            raw = b''.join(payloads)
            (root/'source.xci').write_bytes(raw[:-1] if truncate else raw)
            result = subprocess.run([sys.executable, str(root/'split_xci.py'),
                                     str(root/'source.xci'), str(root/'out')],
                                    capture_output=True, text=True)
            final_files = list((root/'out').glob('*.nsp'))
            return result, len(final_files)

    def test_mismatch_is_never_reported_as_pass(self):
        result, count = self.run_case(mismatch=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout.splitlines()[-1])
        self.assertEqual(report['sha256'], 'MISMATCH')
        self.assertEqual(report['hash_mismatches'], 1)
        self.assertFalse(report['content_integrity_verified'])

    def test_matching_filename_hash_is_reported_without_claiming_full_integrity(self):
        result, count = self.run_case()
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout.splitlines()[-1])
        self.assertEqual(report['sha256'], 'PASS')
        self.assertEqual(report['hash_mismatches'], 0)
        self.assertFalse(report['content_integrity_verified'])
        self.assertEqual(count, 1)

    def test_truncated_payload_never_becomes_final_nsp(self):
        result, count = self.run_case(truncate=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(count, 0)

if __name__ == '__main__':
    unittest.main()
