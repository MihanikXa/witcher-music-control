import json
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch
import unittest

from cue_treatment_predict import REPO,LEDGER,TRIAL
from cue_treatment_trial import registration


class TrialRegistrationTests(unittest.TestCase):
    def test_actual_committed_ledger_scope_and_registration(self):
        r=registration();m=json.loads(LEDGER.read_text())
        self.assertEqual(len(r['git_blob_sha256']),64)
        self.assertEqual(len(m['entries']),24)
        self.assertEqual([e['cue'] for e in m['entries'] if e['trial']],TRIAL)
        self.assertEqual(sum(e['alternative'] is not None and e['trial'] for e in m['entries']),2)
        self.assertEqual(sum(e['status']=='accepted' for e in m['entries']),5)
        self.assertTrue(all(not e['comparison_only'] for e in m['entries'] if e['trial']))

    def test_registration_accepts_only_git_line_ending_conversion(self):
        with TemporaryDirectory(dir=REPO/'build') as temp:
            p=Path(temp)/'ledger.json';blob=b'{"prediction": 1}\n'
            for raw,passes in [(blob,True),(blob.replace(b'\n',b'\r\n'),True),
                               (b'{"prediction": 2}\r\n',False),(b'{"prediction":1}\n',False)]:
                p.write_bytes(raw)
                responses=[SimpleNamespace(stdout='a'*40+'\n'),SimpleNamespace(stdout=blob)]
                with patch('cue_treatment_trial.LEDGER',p),patch('cue_treatment_trial.subprocess.run',side_effect=responses):
                    if passes:self.assertEqual(registration()['commit'],'a'*40)
                    else:
                        with self.assertRaisesRegex(ValueError,'differs'):registration()


if __name__=='__main__':unittest.main()
