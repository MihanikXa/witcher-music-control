"""Synthetic controls for package delta and official build receipt gates."""
import importlib.util
import json
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch

spec=importlib.util.spec_from_file_location('package',Path(__file__).resolve().parents[1]/'tools/package-field-folio.py')
package=importlib.util.module_from_spec(spec);spec.loader.exec_module(package)


class PackageTests(unittest.TestCase):
    def test_unrelated_code_change_rejected(self):
        fonts=[(75,struct.pack('<HBBB',i,4,1,2)+b'x\0'+b'\0\0') for i in (218,219)]
        old=(15,b'header',[(82,b'original ABC')])
        new=(15,b'header',fonts+[(82,b'changed ABC')])
        with patch.object(package.pipeline,'critical',side_effect=[old,new]):
            with self.assertRaisesRegex(ValueError,'outside'):
                package.delta(b'old',b'new')

    def test_missing_utility_font_rejected(self):
        with patch.object(package.pipeline,'critical',side_effect=[(15,b'h',[]),(15,b'h',[])]):
            with self.assertRaisesRegex(ValueError,'IDs'):
                package.delta(b'old',b'new')

    def test_failed_official_command_cannot_package(self):
        with tempfile.TemporaryDirectory() as tmp:
            work=Path(tmp)
            receipt={'commands':[dict(label=label,exit_code=1 if label=='validate' else 0,assertions=[])
                                 for label in ('cook','validate','pack','metadata')]}
            (work/'receipt.json').write_text(json.dumps(receipt))
            with self.assertRaisesRegex(ValueError,'failed'):
                package.gate(work)


if __name__=='__main__':unittest.main()
