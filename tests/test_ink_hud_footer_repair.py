"""Pure source regression checks for D1 footer #1065 candidate fix."""
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'tools' / (name + '.py'))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

repair = load('repair-ink-hud-footer')
layout = load('polish-hud-layout')

class FooterRepairTests(unittest.TestCase):
    def test_reverts_exact_v4_fit_but_preserves_all_other_code(self):
        original = ('public class ModuleInputFeedback {\n'
                    'BUTTONS_PADDING:Number = 20;\n'
                    '         switch(this._buttonAlign) { foo(); }\n}')
        injected = original.replace(
            '         switch(this._buttonAlign)',
            '         this._canvas.scaleX = this._canvas.scaleY = '
            'this._cachedWidth > 0 && buttonsSize > this._cachedWidth ? '
            'this._cachedWidth / buttonsSize : 1;\n'
            '         buttonsSize *= this._canvas.scaleX;\n'
            '         switch(this._buttonAlign)'
        )
        self.assertEqual(repair.repair(injected), original)

    def test_rejects_unmatched_or_wrong_class(self):
        with self.assertRaisesRegex(ValueError, 'exactly one'):
            repair.repair('public class ModuleInputFeedback { }')
        with self.assertRaisesRegex(ValueError, 'not ModuleInputFeedback'):
            repair.repair('public class SomethingElse { }')

    def test_future_footer_generator_does_not_inject_unbound_identifier(self):
        source = ('public class ModuleInputFeedback {\n'
                  'BUTTONS_PADDING:Number = 15;\n'
                  '         switch(this._buttonAlign) {}\n}')
        output = layout.footer(source)
        self.assertIn('BUTTONS_PADDING:Number = 20', output)
        self.assertNotIn('buttonsSize', output)
        self.assertNotIn('this._canvas.scaleX', output)
        self.assertIn('switch(this._buttonAlign)', output)

if __name__ == '__main__':
    unittest.main()
