"""Read-only native/deployed notification contract audit. No Vortex or settings writes."""
import configparser
import ctypes
import hashlib
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
GAME = Path(r'C:\Program Files (x86)\Steam\steamapps\common\The Witcher 3')
KIT = Path(r'L:\Games\Steam\steamapps\common\The Witcher 3 REDkit')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def corrected_source(original):
    """Only identity changes, a unit comment, and the two evidenced duration corrections."""
    if original.count('4.0, false') != 1 or original.count('12.0, false') != 1:
        raise ValueError('Unexpected original durations')
    return (original.replace('wmcVisualSmoke', 'wmcVisualSmokeV2')
            .replace('WMCVisualSmoke', 'WMCVisualSmokeV2').replace('WMCVIS1', 'WMCVIS2')
            .replace('4.0, false', '4000.0, false').replace('12.0, false', '12000.0, false')
            .replace('// Optional, finite UI liveness diagnostic.',
                     '// V2: notification durations are milliseconds, not timer seconds.\n'
                     '// Optional, finite UI liveness diagnostic.'))


def contract(notification, overlay):
    required = ('private static const DEF_DURATION:Number = 4000;',
                'private static const ANIMATION_DURATION:Number = .3;',
                '_duration = msgDuration;', '_duration = _duration ? _duration : DEF_DURATION;',
                '_timer = new Timer(_duration)', 'initTimer();')
    if not all(x in notification for x in required):
        raise ValueError('Unreviewed notification timer contract')
    if 'notificationModule.show(msgText, msgDuration);' not in overlay:
        raise ValueError('Unreviewed forwarding contract')
    return dict(unit='milliseconds', default_ms=4000, entrance_tween_seconds=.3,
                original_ms=[4, 12], corrected_ms=[4000, 12000],
                retail_hook_execution_proven=False)


def audit():
    ui = KIT/'r4data/gameplay/gui_new/actionscript/red/game/witcher3/popups'
    original = REPO/'src/diagnostics/wmcVisualSmoke.ws'
    deployed = GAME/'Mods/modWMCVisualSmoke/content/scripts/local/wmcVisualSmoke.ws'
    revised = REPO/'src/diagnostics/wmcVisualSmokeV2.ws'
    if revised.read_text(encoding='utf-8') != corrected_source(original.read_text(encoding='utf-8')):
        raise ValueError('Changes beyond approved minimal correction')
    result = dict(contract=contract((ui/'NotificationModule.as').read_text(),
                                   (ui/'OverlayPopupMenu.as').read_text()),
                  original_sha256=sha(original), corrected_sha256=sha(revised),
                  deployed_exists=deployed.is_file(), installed_files_modified=False)
    if deployed.is_file():
        result.update(deployed_sha256=sha(deployed), deployed_matches_v1=sha(deployed) == sha(original))
    buf = ctypes.create_unicode_buffer(260)
    if ctypes.windll.shell32.SHGetFolderPathW(None, 5, None, 0, buf) != 0:
        raise ValueError('Documents resolution failed')
    settings = Path(buf.value)/'The Witcher 3/mods.settings'
    cfg = configparser.ConfigParser()
    cfg.read(settings, encoding='utf-8-sig')
    result['relevant_declared_mods'] = {
        name: {k:cfg[name].get(k) for k in ('Enabled', 'Priority')}
        for name in cfg.sections() if any(x in name.lower() for x in
            ('wmc', 'hud', 'merged', 'sharedutils', 'monsterhunt'))}
    result['pins'] = {}
    paths = [ui/'NotificationModule.as', ui/'OverlayPopupMenu.as',
             GAME/'content/content0/scripts/engine/entity.ws',
             GAME/'content/content0/scripts/game/gui/r4guimanager.ws',
             GAME/'content/content0/scripts/game/gui/popups/overlayPopup.ws',
             GAME/'Mods/mod0000_MergedFiles/content/scripts/game/r4Game.ws',
             GAME/'Mods/mod0000_MergedFiles/content/scripts/game/player/r4player.ws']
    for p in paths:
        result['pins'][str(p)] = sha(p)
    result['limits'] = ['Current disk declarations are not historical Vortex runtime status.',
                        'HUD menu behavior disabled by user is distinct from script mod Enabled flag.',
                        'REDkit ActionScript contract is source evidence; no retail call was observed.',
                        'No complete enabled-mod script cache/assembly or runtime callback proof.']
    return result


if __name__ == '__main__':
    print(json.dumps(audit(), indent=2))
