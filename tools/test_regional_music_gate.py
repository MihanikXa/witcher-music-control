import tempfile
from pathlib import Path
import struct
import unittest

from regional_music_gate import bank_preflight


def bank(folder, ident=1, media=b'unchanged', project=17637):
    folder.mkdir()
    chunks={
        'BKHD':struct.pack('<6I',150,1,393239870,16,project,0)+bytes(28),
        'HIRC':struct.pack('<IBII',1,12,5,ident)+b'x',
        'DIDX':b'index','DATA':media}
    (folder/'music_nomansgrad.bnk').write_bytes(b''.join(tag.encode()+struct.pack('<I',len(data))+data for tag,data in chunks.items()))
    (folder/'SoundbanksInfo.xml').write_text('<Info><SoundBank Id="1" Hash="{00000000-0000-0000-0000-000000000000}"/></Info>')


class GateTests(unittest.TestCase):
    def run_gate(self, **kwargs):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);bank(root/'baseline');bank(root/'candidate',**kwargs)
            return bank_preflight(root/'baseline',root/'candidate',{'region':'music_nomansgrad','purpose':'scoped-pilot'})

    def test_unmeasured_layout_never_approved_even_if_identical(self):
        r=self.run_gate();self.assertFalse(r['passed']);self.assertIn('measured_record_decoder_required_for_this_manifest',r['failures'])

    def test_media_change_reported(self):
        self.assertIn('embedded_media_changed:DATA',self.run_gate(media=b'changed')['failures'])

    def test_global_identity_change_reported(self):
        self.assertIn('BKHD_identity_or_metadata',self.run_gate(project=39)['failures'])

    def test_added_removed_record_reported(self):
        self.assertIn('unexpected_HIRC_addition_or_removal',self.run_gate(ident=2)['failures'])


if __name__=='__main__':unittest.main()
