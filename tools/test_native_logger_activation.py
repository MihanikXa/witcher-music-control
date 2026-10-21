import unittest

from native_logger_activation_audit import command_gate_model, literal_offsets, pc_order, logger_rows, native_proof


class ActivationTests(unittest.TestCase):
    def test_missing_flag_keeps_reviewed_gate_closed(self):
        self.assertTrue(command_gate_model('witcher3.exe')['disabled_field_17c'])
        self.assertFalse(command_gate_model('witcher3.exe -debugscripts')['disabled_field_17c'])
        self.assertTrue(command_gate_model('witcher3.exe -DEBUGSCRIPTS')['disabled_field_17c'])

    def test_substring_model_does_not_invent_argument_tokenization(self):
        self.assertFalse(command_gate_model('prefix-debugscripts-suffix')['disabled_field_17c'])
        self.assertTrue(command_gate_model('')['model_only'])

    def test_literal_scanning_never_interprets_machine_bytes_as_regex(self):
        self.assertEqual(list(literal_offsets(b'x|abc|a',b'|a')),[1,5])
        self.assertEqual(list(literal_offsets(b'aaaa',b'aa')),[0,1,2])
        with self.assertRaises(ValueError):list(literal_offsets(b'x',b''))

    def test_descriptor_order_and_path_boundary(self):
        a='<OverrideOrder><Set name="pc"><Path name="base\\"/><Path name="developer\\"/></Set></OverrideOrder>'
        self.assertEqual(pc_order(a),['base\\','developer\\'])
        for path in ('../elsewhere','C:/elsewhere','/elsewhere',''):
            with self.assertRaises(ValueError):pc_order(a.replace('base\\',path))
        with self.assertRaises(ValueError):pc_order('<OverrideOrder/>')

    def test_inspector_preserves_empty_and_duplicate_values_without_exposing_others(self):
        text='[Other]\nSecret=private\n[Scripts]\nDebugScriptsLogDir=\nDebugScriptsLogDir=elsewhere\nLogDebugScripts=true\n'
        rows=logger_rows(text)
        self.assertEqual([r['value'] for r in rows],['','elsewhere','true'])
        self.assertNotIn('private',str(rows))

    def test_unreviewed_image_fails_before_offset_decoding(self):
        with self.assertRaisesRegex(ValueError,'Unreviewed executable'):native_proof(b'not a reviewed image')


if __name__=='__main__':unittest.main()
