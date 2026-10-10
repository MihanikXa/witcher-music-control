"""Synthetic package regression checks; no proprietary fixtures."""
import importlib.util
import io
from pathlib import Path
import unittest
from unittest.mock import patch
import zipfile

spec = importlib.util.spec_from_file_location('package',Path(__file__).resolve().parents[1]/'tools/package-english-gentium.py')
package = importlib.util.module_from_spec(spec)
spec.loader.exec_module(package)


class PackageTests(unittest.TestCase):
    def test_deterministic_zip_and_exact_contents(self):
        files = {'Mods/example/content/b':b'two','Mods/example/notice':b'one'}
        data = package.archive_bytes(files)
        self.assertEqual(data,package.archive_bytes(dict(reversed(list(files.items())))))
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            self.assertIsNone(archive.testzip())
            self.assertEqual({k:archive.read(k) for k in archive.namelist()},files)

    def test_nonfont_change_rejected(self):
        movies = [(10,b'header',[(69,b'a')]),(10,b'header',[(69,b'b')])]
        with patch.object(package.verify,'movie_tags',side_effect=movies):
            with self.assertRaisesRegex(ValueError,'Non-font'):
                package.contract_delta(b'original',b'candidate')

    def test_movie_geometry_change_rejected(self):
        with patch.object(package.verify,'movie_tags',side_effect=[(10,b'a',[]),(10,b'b',[])]):
            with self.assertRaisesRegex(ValueError,'header'):
                package.contract_delta(b'original',b'candidate')

    def test_missing_style_rejected(self):
        with patch.object(package.verify,'movie_tags',return_value=(10,b'h',[])):
            with self.assertRaisesRegex(ValueError,'three'):
                package.contract_delta(b'original',b'candidate')

    def test_changed_mapping_rejected(self):
        movies = [(10,b'h',[(75,b'old')]),(10,b'h',[(75,b'new')])]
        before = dict(id=1,flags=140,name='alias',codes=[32],glyphs=383)
        after = dict(before,codes=[33])
        with patch.object(package.verify,'movie_tags',side_effect=movies),patch.object(package.prep,'layout',side_effect=[before,after]):
            with self.assertRaisesRegex(ValueError,'coverage'):
                package.contract_delta(b'original',b'candidate')


if __name__ == '__main__':
    unittest.main()
