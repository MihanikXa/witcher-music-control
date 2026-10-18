import contextlib
import io
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from white_orchard_wwise import generate


class GenerationOptionTests(unittest.TestCase):
    def test_decoded_cache_is_explicit_and_default_stays_unchanged(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); project=root/'generation/w3_audio.wproj'
            project.parent.mkdir();project.write_text('synthetic, no licence')
            for decode in (False,True):
                output=root/str(decode)
                def run(args,**kwargs):
                    self.assertEqual(args[0:2],['WwiseConsole.exe','generate-soundbank'])
                    self.assertEqual('--no-decode' in args,not decode)
                    self.assertIn('--no-source-control',args)
                    self.assertIn('--no-wwise-dat',args)
                    self.assertEqual(args[args.index('--bank')+1],'music_prologue')
                    for name in ('Init.bnk','music_prologue.bnk'):(output/name).write_bytes(b'test')
                    return SimpleNamespace(returncode=2)
                with patch('white_orchard_wwise.build_path',side_effect=lambda p:Path(p)), \
                     patch('white_orchard_wwise.subprocess.run',side_effect=run),contextlib.redirect_stdout(io.StringIO()):
                    generate(Path('WwiseConsole.exe'),project,output,decode_media=decode)
                    with self.assertRaises(FileExistsError):
                        generate(Path('WwiseConsole.exe'),project,output,decode_media=decode)


if __name__=='__main__':unittest.main()
