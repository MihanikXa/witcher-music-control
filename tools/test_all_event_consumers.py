import tempfile
import unittest
from pathlib import Path
from test_regional_music import fixture
from regional_music import validate_event_directory


class AllEventConsumerTests(unittest.TestCase):
    def test_secondary_event_work_unit_is_not_missed(self):
        a,b,s,states,t=fixture()
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'Events/nested').mkdir(parents=True)
            (root/'Events/music.wwu').write_text('<Events/>')
            other=root/'Events/nested/other.wwu'
            other.write_text('<Events/>')
            self.assertEqual(validate_event_directory(a,root,s),2)
            other.write_text('<Events><ObjectRef ID="generic" /></Events>')
            with self.assertRaisesRegex(ValueError,'Direct event targets'):
                validate_event_directory(a,root,s)

    def test_missing_event_context_fails(self):
        a,b,s,states,t=fixture()
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError,'Missing complete event'):
                validate_event_directory(a,Path(tmp),s)
