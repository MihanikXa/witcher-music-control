"""Reference composition/data-policy checks; explicitly no runtime acceptance."""
import hashlib,importlib.util,json,unittest
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'build/inventory-approved-gate1'
def load(name):
    s=importlib.util.spec_from_file_location(name,ROOT/'tools'/(name+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
class VisualProof(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d=json.loads((OUT/'visual-receipt.json').read_text(encoding='utf-8'));cls.a=load('inspect-approved-inventory')
        cls.ref=Image.open(cls.a.REFERENCE).convert('RGB')
    def test_authorized_reference_is_unchanged(self):
        self.assertEqual(self.ref.size,(1672,941));self.assertEqual(self.a.sha(self.a.REFERENCE),self.d['reference_sha256'])
        self.assertEqual(self.d['reference_sha256'],self.a.AUTHORIZED_SHA)
    def test_important_reference_regions_are_pixel_identical(self):
        for state in ('sparse','populated','six-row-fit'):
            im=Image.open(self.d['outputs'][state]['path']).convert('RGB')
            for box in self.d['protected_regions'].values():self.assertEqual(self.ref.crop(box).tobytes(),im.crop(box).tobytes())
    def test_same_row_scale_no_icon_upscale_and_fit(self):
        states=self.d['outputs'];s=states['sparse']['rows'];p=states['populated']['rows']
        self.assertEqual([r['bounds'] for r in s],[r['bounds'] for r in p[:len(s)]])
        for state in states.values():
            for row in state['rows']:
                self.assertLessEqual(row['text_width'],row['text_allowance'])
                self.assertFalse(row['upscaled'])
                self.assertTrue(all(x<=y for x,y in zip(row['icon_display'],row['icon_source'])))
        self.assertIn('…',p[-1]['display']);self.assertEqual(states['sparse']['total_equipment_items'],6)
    def test_scroll_and_fixture_counts_are_explicit(self):
        state=self.d['outputs']['populated'];self.assertGreater(state['total_weapon_rows'],state['visible_rows'])
        for state in self.d['outputs'].values():self.assertTrue(state['review_count_illustrative'])
        self.assertFalse(self.d['runtime_behavior_proven']);self.assertFalse(self.d['native_binary_built'])
    def test_exports_and_metadata_hashes(self):
        for state,data in self.d['outputs'].items():
            self.assertEqual(self.a.sha(Path(data['path'])),data['sha256'])
            for w,h in ((1672,941),(1920,1080),(3840,2160)):
                with Image.open(OUT/(state+f'-{w}x{h}.png')) as image:self.assertEqual(image.size,(w,h))
    def test_v4_source_and_equipped_mark_contract(self):
        d=json.loads((OUT/'source-receipt.json').read_text(encoding='utf-8'))
        self.assertEqual(d['baseline']['sha256'],self.a.V4_SHA)
        self.assertEqual(d['marker']['vertices'],[[3,3],[12,3],[3,12],[3,3]])
        self.assertEqual(d['marker']['hex'],'#B48C44');self.assertEqual(d['marker']['alpha'],.9)
        self.assertEqual(d['winners'][self.a.KEY]['sha256'],self.a.V4_SHA)
    def test_live_inputs_unchanged(self):
        d=json.loads((OUT/'source-receipt.json').read_text(encoding='utf-8'))
        self.assertEqual(load('build-inventory-p2').freeze(),d['frozen'])
class ReviewExamples(unittest.TestCase):
    def test_provisional_examples(self):
        p=load('propose-inventory-review-policy')
        for label,facts,expected in p.EXAMPLES:
            with self.subTest(label=label):self.assertEqual(p.decision(facts),expected)
    def test_repeated_materials_do_not_create_work(self):
        p=load('propose-inventory-review-policy')
        inputs=[dict(routine_material=True) for _ in range(100)]+[dict(noteworthy_equipment=True)]
        self.assertEqual(sum(p.decision(f)[0]=='include' for f in inputs),1)
    def test_familiarity_is_not_a_damage_score(self):
        p=load('propose-inventory-review-policy')
        self.assertEqual(p.decision(dict(indistinct_common_equipment=True,damage=200)),p.decision(dict(indistinct_common_equipment=True,damage=20)))
        self.assertEqual(p.decision(dict(noteworthy_equipment=True,damage=20))[0],'include')
if __name__=='__main__':unittest.main()
