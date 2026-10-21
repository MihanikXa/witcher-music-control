"""Run the actual PowerShell witness against synthetic CIM responses; never launch a game."""
import json
from pathlib import Path
import shutil
import subprocess
import unittest

SCRIPT = Path(__file__).with_name('Get-WmcGameArguments.ps1')


@unittest.skipUnless(shutil.which('powershell.exe'), 'Windows PowerShell required')
class GameArgumentWitnessTests(unittest.TestCase):
    def witness(self, body):
        script = str(SCRIPT).replace("'", "''")
        code = f". '{script}'\nfunction Get-CimInstance {{ param($ClassName,$Filter,$ErrorAction)\n"
        code += "if ($ClassName -ne 'Win32_Process' -or $Filter -ne \"Name='witcher3.exe'\") { throw 'wrong scope' }\n"
        code += body + '\n}\nGet-WmcGameArgumentWitness | ConvertTo-Json -Depth 4'
        result = subprocess.run(['powershell.exe', '-NoProfile', '-NonInteractive', '-Command', code],
                                capture_output=True, text=True, check=True)
        self.assertNotIn('PRIVATE', result.stdout + result.stderr)
        return json.loads(result.stdout)

    def test_presence_and_privacy(self):
        row = self.witness("[pscustomobject]@{ExecutablePath='C:/Game/bin/x64_dx12/witcher3.exe';CommandLine='witcher3.exe -debugscripts PRIVATE';ProcessId=999}")
        self.assertEqual(row['Status'], 'Observed')
        self.assertEqual(row['Processes'], [{'ExecutablePath': 'C:/Game/bin/x64_dx12/witcher3.exe',
                                            'DebugScriptsSubstringPresent': True}])

    def test_native_case_sensitive_substring(self):
        for args, expected in [('PRIVATE -DEBUGSCRIPTS', False), ('PRIVATE -debugscriptsSuffix', True), ('PRIVATE', False)]:
            with self.subTest(args=args):
                row = self.witness(f"[pscustomobject]@{{ExecutablePath='game';CommandLine='{args}'}}")
                self.assertEqual(row['Processes'][0]['DebugScriptsSubstringPresent'], expected)

    def test_unreadable_is_not_absent_flag(self):
        row = self.witness("[pscustomobject]@{ExecutablePath=$null;CommandLine=$null}")
        self.assertEqual(row['Status'], 'Unreadable')
        self.assertIsNone(row['Processes'][0]['DebugScriptsSubstringPresent'])

    def test_no_process(self):
        self.assertEqual(self.witness(''), {'Status': 'NotRunning', 'Processes': []})

    def test_failure_is_sanitized(self):
        self.assertEqual(self.witness("throw 'PRIVATE'"), {'Status': 'QueryFailed', 'Processes': []})

    def test_multiple_is_explicit(self):
        row = self.witness("1..2 | ForEach-Object { [pscustomobject]@{ExecutablePath='game';CommandLine='-debugscripts PRIVATE'} }")
        self.assertEqual(row['Status'], 'MultipleGameProcesses')
        self.assertEqual(len(row['Processes']), 2)


if __name__ == '__main__':
    unittest.main()
