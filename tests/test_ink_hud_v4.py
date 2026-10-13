"""Regression gates for v4 geometry, palette and bounded prompt adapters."""
import importlib.util,struct,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(n):
 s=importlib.util.spec_from_file_location(n,ROOT/'tools'/(n+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
m=load('build-ink-hud-v4');s=m.smooth
class PolishTests(unittest.TestCase):
 def test_curved_resolution_independent_circle(self):
  path=s.circle(32,32,19)
  self.assertEqual(sum(k=='Q' for k,v in path),8)
  self.assertEqual(path[0][1],(51,32))
  self.assertLess(abs(path[-1][1][-1]-32),1e-6)
 def test_shape_export_dictionary_id(self):
  for name in ['A','B','X','Y','LT','RT','LB','RB','L_hold','R_tabs','dpad_up','View','Menu']:
   data=s.shape(123,'ICO_Xbox_'+name,64,64,m.FONT)
   self.assertEqual(struct.unpack_from('<H',data)[0],123)
   self.assertLess(len(data),4000)
   offset=2+(5+4*(data[2]>>3)+7)//8
   count=data[offset];offset+=1
   for i in range(count):
    self.assertEqual(data[offset],0);offset+=5
   self.assertEqual(data[offset],0)
 def test_opposing_ring_windings(self):
  self.assertGreater(s.circle(0,0,10)[1][1][1],0)
  self.assertLess(s.circle(0,0,9,True)[1][1][1],0)
 def test_dpad_directions_remain_distinct(self):
  shapes=[s.shape(123,'ICO_Xbox_'+n,64,64,m.FONT) for n in ['dpad','dpad_up','dpad_down','dpad_left','dpad_right','dpad_left_right','dpad_double_up']]
  self.assertEqual(len(set(shapes)),len(shapes))
 def test_palette_hierarchy(self):
  colors=[b for a,b in m.PALETTE.values()]
  self.assertEqual(colors,['#B94A40','#D9695A','#C77D6E'])
  self.assertGreater(int(colors[1][1:3],16),int(colors[0][1:3],16))
 @unittest.skipUnless((m.WORK/'exports/panel_common/scripts').exists(),'Private source evidence absent')
 def test_idempotent_scale_and_baseline_adapter(self):
  original=next((m.WORK/'exports/panel_common/scripts').rglob('InputFeedbackButton.as')).read_text(encoding='utf-8-sig')
  modified=m.layout.button(original)
  self.assertIn('this.qfXboxScaleX * 0.6875',modified)
  self.assertNotIn('scaleX *=',modified)
  self.assertIn('hitArea.width * Math.abs',modified)
  self.assertIn('getLineMetrics(0).ascent + textField.getLineMetrics(0).descent',modified)
  self.assertIn('textField.getLineMetrics(0).ascent - this.tfHoldPrefix.getLineMetrics(0).ascent',modified)
  self.assertEqual(original.count('addEventListener'),modified.count('addEventListener'))
 @unittest.skipUnless((m.WORK/'exports/panel_common/scripts').exists(),'Private source evidence absent')
 def test_footer_fit_is_reset_and_bounded(self):
  original=next((m.WORK/'exports/panel_common/scripts').rglob('ModuleInputFeedback.as')).read_text(encoding='utf-8-sig')
  self.assertIn('BUTTONS_PADDING:Number = 20',m.layout.footer(original))
  for width in [640,1920,3840]:
   total=1440;scale=width/total if total>width else 1
   self.assertLessEqual(total*scale,width)
 @unittest.skipUnless((m.PARENT/'receipt.json').exists(),'Private source evidence absent')
 def test_warning_changes_only_two_bytes(self):
  key=next(k for k in __import__('json').loads((m.PARENT/'receipt.json').read_text())['resource_hashes'] if k.endswith('hud_enemyfocus.redswf'))
  original=(m.WORK/'inputs'/key).read_bytes();patched,edits=m.warning(original)
  a=m.b.audit.swf_tags(original)[2];b=m.b.audit.swf_tags(patched)[2]
  differences=[]
  for (ca,pa),(cb,pb) in zip(a,b):
   self.assertEqual(ca,cb);self.assertEqual(len(pa),len(pb))
   differences.extend((ca,x,y) for x,y in zip(pa,pb) if x!=y)
  self.assertEqual(sorted(differences),[(39,255,179),(83,255,179)])
  self.assertEqual(len(edits),2)
if __name__=='__main__':unittest.main()
