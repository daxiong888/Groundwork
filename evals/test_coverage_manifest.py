#!/usr/bin/env python3
import unittest

from evals import check_coverage_manifest


class CoverageManifestTests(unittest.TestCase):
    def test_manifest_references_existing_rows_and_public_skills(self):
        errors = check_coverage_manifest.validate_manifest(
            check_coverage_manifest.DEFAULT_MANIFEST,
        )
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
