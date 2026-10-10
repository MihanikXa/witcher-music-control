"""Synthetic controls for texture-footprint and empty-workspace gates."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec=importlib.util.spec_from_file_location('pipeline',Path(__file__).resolve().parents[1]/'tools/verify-field-folio-asset.py')
pipeline=importlib.util.module_from_spec(spec);spec.loader.exec_module(pipeline)


class PipelineTests(unittest.TestCase):
    def texture(self,pixels):
        return {},{'_i3b.dds':dict(id=59,width=1,height=1,pitch=16,alignment=16,pixels=pixels,rectangles=[])}

    def test_external_bitmap_without_subimages_checks_entire_footprint(self):
        with patch.object(pipeline,'textures',side_effect=[self.texture(b'a'),self.texture(b'b')]),patch.object(
                pipeline.font.native,'bc3',side_effect=[[[255,0,0,255]],[[0,255,0,255]]]):
            report=pipeline.compare_textures(b'old',b'new')
        self.assertEqual(report[0]['used_and_one_pixel_border_differences'],1)

    def test_fully_transparent_rgb_difference_is_separately_reported(self):
        with patch.object(pipeline,'textures',side_effect=[self.texture(b'a'),self.texture(b'b')]),patch.object(
                pipeline.font.native,'bc3',side_effect=[[[255,0,0,0]],[[0,255,0,0]]]):
            report=pipeline.compare_textures(b'old',b'new')
        self.assertEqual(report[0]['used_and_one_pixel_border_differences'],0)
        self.assertEqual(report[0]['transparent_rgb_differences'],1)

    def test_empty_workspace_stages_only_requested_key_and_restores_files(self):
        font=pipeline.font
        with tempfile.TemporaryDirectory(dir=font.ROOT/'build',prefix='utility-mount-test-') as tmp:
            root=Path(tmp);runner=root/'runner';workspace=runner/'bin/workspace';workspace.mkdir(parents=True)
            out=root/'output';out.mkdir();resource=root/'input';resource.write_bytes(b'original synthetic input')
            with font.mounted_input(runner,out,resource,key=pipeline.KEY) as stage:
                self.assertEqual(font.workspace_inventory(stage),{pipeline.KEY.replace('/', '\\'):font.audit.sha(resource.read_bytes())})
            self.assertEqual(font.workspace_inventory(workspace),{})
            self.assertEqual((out/'staged-workspace'/pipeline.KEY).read_bytes(),resource.read_bytes())
            # A subsequent run can reuse the now-empty directory tree.
            second=root/'second';second.mkdir()
            with font.mounted_input(runner,second,resource,key=pipeline.KEY):pass
            self.assertEqual(font.workspace_inventory(workspace),{})


if __name__=='__main__':unittest.main()
