import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
def load(name):
    spec=importlib.util.spec_from_file_location(name,ROOT/'tools'/(name+'.py'))
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
subtitle=load('verify-subtitle-shadow-asset');package=load('package-text-shadow-wave-a')


class ReleaseTests(unittest.TestCase):
    def resource(self):
        return [dict(class_name='CSwfResource',crc_valid=True,properties={
            'linkageName':dict(value='subtitle{test}.gfx'),'textures':dict(value='00000000')})]

    def check(self,chunks,tags):
        with patch.object(subtitle.font.native,'chunks',return_value=chunks),patch.object(
                subtitle.audit,'swf_tags',return_value=(0,'CFX',tags)):
            return subtitle.structure(b'synthetic')

    def test_subtitle_rejects_lost_texture_handle_without_chunk(self):
        chunks=self.resource();chunks[0]['properties']['textures']['value']='0100000002000000'
        with self.assertRaises(ValueError):self.check(chunks,[(1000,b'subtitle{test}')])

    def test_subtitle_rejects_bitmap_reference_even_with_empty_array(self):
        with self.assertRaises(ValueError):self.check(self.resource(),[(1000,b'subtitle{test}'),(1009,b'bitmap')])

    def test_subtitle_rejects_wrong_export_linkage_and_invalid_crc(self):
        with self.assertRaises(ValueError):self.check(self.resource(),[(1000,b'other')])
        chunks=self.resource();chunks[0]['crc_valid']=False
        with self.assertRaises(ValueError):self.check(chunks,[(1000,b'subtitle{test}')])

    def test_source_gate_rejects_changed_transformation_baseline(self):
        with tempfile.TemporaryDirectory() as d:
            source=Path(d)/'source';source.write_bytes(b'original')
            record=dict(input_path=str(source),input_sha256=package.audit.sha(b'original'),output_sha256='candidate',
                unchanged_selected_tags_exact=True,independently_decoded_delta_exact=True,other_tags_retained_from_source=True)
            package.check_source(dict(expected_swf_sha256='candidate'),record)
            source.write_bytes(b'changed')
            with self.assertRaises(ValueError):package.check_source(dict(expected_swf_sha256='candidate'),record)


if __name__=='__main__':unittest.main()
