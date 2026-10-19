"""Read-only, bounded native signal evidence and approved-cue metadata audit.

No game/Wwise session, authoring, audio processing or third-party execution.
Source symbols prove implementation paths, not delivery of mod callbacks.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import wave
import xml.etree.ElementTree as ET

REPO=Path(__file__).resolve().parents[1]
GAME=Path(r'C:\Program Files (x86)\Steam\steamapps\common\The Witcher 3\content\content0\scripts')
RED=Path(r'L:\Games\Steam\steamapps\common\The Witcher 3 REDkit\r4data\scripts')
WWISE=Path(r'L:\Games\Steam\steamapps\common\The Witcher 3 REDkit\assets\w3_audio')


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path):return json.loads(path.read_text(encoding='utf-8-sig'))


def locate(path,anchor):
    lines=path.read_text(encoding='utf-8-sig').splitlines()
    hits=[i+1 for i,s in enumerate(lines) if anchor in s]
    if len(hits)!=1:raise ValueError(f'Expected unique source anchor: {path.name}: {anchor}: {hits}')
    return dict(path=str(path),symbol=anchor,line=hits[0],sha256=sha(path))


def script(rel,anchor):
    a,b=locate(GAME/rel,anchor),locate(RED/rel,anchor)
    return dict(kind='native_game_script',primary=a,redkit=b,byte_identical=a['sha256']==b['sha256'])


def wwise(rel,anchor):return dict(kind='native_Wwise',primary=locate(WWISE/rel,anchor))


def catalog():
    rows=[]
    def add(id,rank,status,semantics,access,use,risk,probe,refs):
        rows.append(dict(id=id,rank=rank,availability=status,semantics=semantics,integration=access,
                         uses=use,reliability_limits=risk,minimum_runtime_test=probe,references=refs))
    verified='verified source implementation; mod delivery not runtime-tested'
    add('region','A',verified,'Persistent current area; initialization stops/starts regional music.',
        'Public map query; native regional Play event already reaches Wwise.','eligibility,palette',
        'Area is coarse, not biome or discovery; load/fast travel reseeds lifecycle.',
        'Log current area and initialization across ordinary reload, no travel manipulation.',
        [script('game/commonMapManager.ws','import final function GetCurrentArea()'),script('engine/sound.ws','function InitializeAreaMusic(')])
    add('music_location','A','verified Wwise definitions/actions; game event producer coverage incomplete',
        'Regional location Switch, not a generic arrival notification.',
        'Already Wwise; no script getter established. Native hook delivery requires separate proof.',
        'eligibility,palette,optional arrival opportunity',
        'Duplicates are normal; same event is not fresh arrival. Review selector consumers; world location can be thematic.',
        'Observe existing location events and actual effective selector, never force location.',
        [wwise('Switches/switches.wwu','ID="{3139B245-58B7-4C39-9BE9-414395307E75}"'),
         wwise('Events/music.wwu','ID="{DA48339C-9810-491C-A4A4-24CAF7811E13}"')])
    add('sound_state','A',verified,'Native music-state getter; default classifier includes explicit-state priority.',
        'Public GetCurrentGameState; Wwise game_state already native.','hard veto,eligibility',
        'Exploration does not imply authored-free or outro-complete; script getter is not exact audio timing.',
        'Log getter alongside native state changes; preserve all setters.',
        [script('engine/sound.ws','function GetCurrentGameState()'),script('engine/sound.ws','exec function CollectSoundStates()')])
    add('daynight','A',verified,'Game-time thresholds; day/night transition events/timer exist.',
        'envMgr.IsNight query; native exploration State names already Wwise.','palette,eligibility',
        'Game time skips/meditation differ from monotonic opportunity clock; day/night is context, not significance.',
        'Log stable day/night and game-time discontinuity without altering time.',
        [script('game/environmentManager.ws','final function IsNight()'),script('game/player/r4Player.ws','private function CheckDayNightCycle()'),
         script('engine/game.ws','import final function GetEngineTimeAsSeconds()')])
    add('weather','B',verified,'Weather-name/rain/snow queries; World.OnWeatherChange forwards to player.',
        'Script queries or localized world/player hook; direct regional music routing not established.','palette,optional opportunity',
        'OnWeatherChanged suppresses voice commentary in scenes/interiors/first60s; do not reuse commentary eligibility as event availability.',
        'Log world change and current query through natural weather transition; debounce blends.',
        [script('engine/environment.ws','import function GetWeatherConditionName()'),script('engine/environment.ws','import function GetRainStrength()'),
         script('engine/world.ws','event OnWeatherChange()'),script('game/player/r4Player.ws','public final function OnWeatherChanged()')])
    add('first_discovery','B',verified,'Fast-travel trigger checks player, disables FirstDiscoveryTrigger, invokes script map-pin discovery; wrapper tests previous saved discovery.',
        'Localized wrapper/callback observation, not existing Wwise input.','optional opportunity,palette hint',
        'Wrapper also called by quests/inventory/debug; discovery can occur remotely. Filter source, false→true and type; never guarantee music.',
        'Log existing natural first discovery: previous/new/tag/type/caller category; reload must not retrigger.',
        [script('game/gameplay/fast_travel_entities/fastTravelEntity.ws','event OnAreaEnter('),
         script('game/commonMapManager.ws','public function SetEntityMapPinDiscoveredScript('),
         script('game/commonMapManager.ws','previouslyDiscovered = IsEntityMapPinDiscovered(')])
    add('map_pin_changed','C',verified,'Broad map mutation signal emits scripted event with no tag/type payload.',
        'Dispatcher AddListener exists, but map-change event alone is insufficient.','dirty-notification only',
        'Not proof of discovery/proximity; do not start music on every UI/map change or diff all-world pins at high frequency.',
        'If used, log reasons/coverage first; no opportunity generation in pilot.',
        [script('game/commonMapManager.ws','event OnMapPinChanged()'),script('game/globalEventsScriptsDisptacher.ws','public function AddListener(')])
    add('location_area','B',verified,'W3LocationArea trigger displays area name; saved discovery reward conditional.',
        'Entity-local event, no central arrival bus established.','optional opportunity',
        'Source has no player guard in this handler; repeat/name/reward conditions and placement coverage need validation.',
        'Observe player identity and repeat enter on an already naturally visited area.',
        [script('game/gameplay/gameplay_triggers/locationArea.ws','event OnAreaEnter('),
         script('game/gameplay/gameplay_triggers/locationArea.ws','saved var discovered')])
    add('journal_subarea','B',verified,'Journal area derived from current area and player position.',
        'Public script method; not a semantic biome.','palette coarse context',
        'Hardcoded regional partition; cannot infer woodland/mountain/vista from journal area label.',
        'Log query transitions and compare location selector without narrative content.',
        [script('game/commonMapManager.ws','function GetCurrentJournalAreaByPosition(')])
    add('travel','A',verified,'Horse query distinguishes mount in progress; boat query tests used vehicle.',
        'Public actor queries; vehicle callbacks available but mod hook uncompiled.','palette,eligibility',
        'Mounting is not a dramatic opportunity by itself; use only mounted flag if needed.',
        'Log foot/mount/mounted/dismount during normal play, no forced action.',
        [script('game/actor.ws','public final function IsUsingHorse('),script('game/actor.ws','public function IsUsingBoat()'),
         script('game/vehicles/vehicleComponent.ws','event OnMountFinished(')])
    add('movement','B',verified,'MovingAgent speed/velocity and sprint state; locomotion consumes velocity.',
        'Script property query; avoid animation-state-name classifier.','palette,stability',
        'Movement speed != meaningful event; stationary can be menu, idle or vista. No scenic meaning inferred.',
        'Sample low rate and inspect mount/teleport discontinuities.',
        [script('game/components/movingAgentComponent.ws','import final function GetSpeed()'),
         script('game/player/player.ws','function GetIsSprinting()')])
    add('interior','B',verified,'Player IsInInterior query and native interior-area callbacks.',
        'Public imported player query; local component callbacks.','palette,conservative veto',
        'isCave field says postprocessing use, not universal cave classifier; trigger overlap/blends exist.',
        'Log interior query vs natural doorway; do not assume all caves.',
        [script('game/player/r4Player.ws','import final function IsInInterior()'),script('game/components/interiorArea.ws','event OnPlayerEntered(')])
    add('combat_hostility','A',verified,'ShouldEnableCombatMusic combines forced combat, threats, enemies and finishing; sound calls combat callbacks.',
        'Public classifier/IsThreatened/GetCurrentGameState; native Wwise States/intensity.','hard veto',
        'IsInCombat alone incomplete; callback end occurs before full musical outro.',
        'Log classifier and native State; do not modify combat callback or threat RTPC.',
        [script('game/player/r4Player.ws','public function ShouldEnableCombatMusic()'),script('game/player/r4Player.ws','public function IsThreatened()'),
         script('engine/sound.ws','private function SoundGameStateChange(')])
    add('outro_complete','C','not exposed in inspected script sound API; Wwise source/playback verified report90',
        'Exploration returns before native transition segment ends.',
        'Keep guard in Wwise; no verified script callback/cursor.','hard veto,recovery',
        'Never equate OnCombatFinished, exploration or fixed30s with observed completion.',
        'Future gateway must enforce actual transition ownership/quiet internally; external controller stays uncertain otherwise.',
        [script('game/player/r4Player.ws','event OnCombatFinished()'),script('engine/sound.ws','import function SoundMusicEvent('),
         wwise('Interactive Music Hierarchy/music.wwu','ID="{A79AC940-BEEA-48E2-81EA-BD307F4771D4}"')])
    add('authored_ownership','C','verified Wwise routing; no complete script ownership getter established',
        'Explicit authored event selects music_type=quests_cutscenes and authored subselector independently of game_state.',
        'Native Wwise music_type gate; complete native-event interception from script unproven.','hard veto',
        'World branch includes protected/mixed selections. Direct Play of imported cue could bypass selector priority.',
        'Prove a request gateway inside reviewed generic selector; unknown ownership must deny, not infer from scene absence.',
        [wwise('Events/music.wwu','ID="{52B7971D-0DD6-40FA-9275-8236C5EFC3B0}"'),
         wwise('Switches/switches.wwu','ID="{2076AA35-8BFD-4069-A941-1D9625ADD8F0}"'),
         script('engine/sound.ws','import function SoundMusicEvent(')])
    add('scenes','A',verified,'Blocking/cutscene/movie-start paths set native sound States; script scene checks also used by weather commentary.',
        'Existing sound State and scene queries.','hard veto',
        'Scene absence != absence of authored music during gameplay. Movie state method has source typo OnEnterSate; use actual OnMovieStarted path.',
        'Log scene predicates and public sound state during ordinary unforced play.',
        [script('game/scenes/scenePlayer.ws','event OnMovieStarted('),script('game/scenes/scenePlayer.ws','state Blocking in'),
         script('game/r4Game.ws','public final function IsDialogOrCutscenePlaying()'),script('game/player/r4Player.ws','public final function OnWeatherChanged()')])
    add('lifecycle_ui','A',verified,'Active/paused/stopped predicates and load completion event; area init stops old music.',
        'Public engine queries plus localized lifecycle callback.','hard veto,invalidate stale opportunities',
        'Loading completion must acquire fresh context/ownership, never replay queued discovery; real-time vs game-time distinction.',
        'Log initialization and user reload without altering saves.',
        [script('engine/game.ws','import final function IsPaused()'),script('engine/game.ws','import final function IsActive()'),
         script('game/r4Game.ws','event OnAfterLoadingScreenGameStart()')])
    add('facts','C',verified,'Fact mutations broadcast script category.',
        'Dispatcher is accessible; semantic interpretation per fact is unsupported.','exclude generic trigger',
        'No generic quest-completed/story-music-free meaning; narrative spoiler/conflict risk.',
        'No pilot trigger; only separately reviewed facts could qualify.',
        [script('game/facts.ws','function FactsAdd(')])
    add('biome_vista','C','absent as a semantic query in inspected engine APIs/common map interface',
        'Position/elevation exist; scenic significance and biome fit do not follow.',
        'No verified native scoring-ready notification.','unavailable for initial model',
        'Geometry/distance/name heuristics can fire in quests or ordinary slopes; no visual inference.',
        'Requires curated authored context evidence; do not invent vista events.',
        [script('game/commonMapManager.ws','function GetCurrentJournalAreaByPosition('),script('engine/world.ws','import final function NavigationComputeZ(')])
    cadence={
        'region':'Persistent query; initialization/world load edges, not per-frame arrival.',
        'music_location':'Event frequency unmeasured; identical events need not restart playback (report90).',
        'sound_state':'State changes;0.15s source throttle is not proof of CollectSoundStates caller frequency.',
        'daynight':'Game-time boundary timer and pollable threshold; meditation/time skip can jump.',
        'weather':'Native callback cadence unmeasured; blend/query values may evolve continuously.',
        'first_discovery':'Player trigger and first-discovery flag; wrapper can also run from nonlocal sources.',
        'map_pin_changed':'Any map-pin mutation; no unique discovery payload.',
        'location_area':'Repeat trigger enters; saved reward/discovered conditions are entity-specific.',
        'journal_subarea':'Position query; boundary jitter possible.',
        'travel':'Persistent mount/vehicle state plus mount callbacks; mounting-in-progress must be excluded explicitly.',
        'movement':'Continuous property; cadence chosen by future adapter, not per-frame required.',
        'interior':'Overlap/entry state; multiple volumes can blend or overlap.',
        'combat_hostility':'Classifier/state changes; finish callback precedes actual audio outro.',
        'outro_complete':'Actual audio transition boundary; no script notification established.',
        'authored_ownership':'Music event/switch transitions independent of scene-state changes.',
        'scenes':'Scene lifecycle edges; gameplay/ordinary dialogue/film are not one ownership signal.',
        'lifecycle_ui':'Native state queries and load callback; invalidate old epoch and pending opportunities.',
        'facts':'Potentially frequent gameplay mutations, not a scoring event bus.',
        'biome_vista':'No verified semantic notification/cadence.'}
    for row in rows:
        row['cadence_and_duplicate_semantics']=cadence[row['id']]
        row['retail_hook_tested']=False
    return rows


def cues():
    accepted=read(REPO/'research/85-accepted-private-cue-selections.json')['selections']
    plan={c['cue']:c for c in read(REPO/'research/61-private-cue-edit-plan.json')['cues']}
    feedback={c['id']:c for c in read(REPO/'research/58-user-musical-material-audition-feedback.json')}
    shortlist={c['id']:c for c in read(REPO/'research/57-music-material-shortlist.json')}
    result=[]
    for selected in accepted:
        id=selected['cue'];source=plan[id]['source'];path=REPO/selected['file']
        if sha(path)!=selected['sha256']:raise ValueError('Accepted audio changed: '+id)
        with wave.open(str(path),'rb') as wav:
            frames=wav.getnframes();rate=wav.getframerate()
            if (wav.getnchannels(),wav.getsampwidth(),rate)!=(2,2,48000):raise ValueError('Unexpected approved WAV format')
        result.append(dict(id=id,family=source,source_title=feedback[source]['title'],user_role=feedback[source]['role'],
            composition_key=str(shortlist[source]['pool'])+':'+str(shortlist[source]['key']),
            source_media=shortlist[source].get('media',shortlist[source]['key']),
            family_basis='Same source recording/selected native segment is a known family. Cross-recording remixes/compositional aliases are not fully established.',
            user_notes=feedback[source]['notes'],file=selected['file'],sha256=selected['sha256'],
            approved_file_seconds=frames/rate,wrapper_seconds=5,model_duration_seconds=(frames-5*rate)/rate,
            wrapper_basis='report61/accepted renders:2s audition lead+3s trail; only S04-a independently engine-derived in report87',
            source_cut=selected.get('source_cut'),policy='private illustrative use only; no final regional assignment',
            authored_reuse_caution=source=='S14'))
    if len(result)!=24 or len({c['id'] for c in result})!=24:raise ValueError('Incomplete accepted catalog')
    return result


def bounded_negatives():
    files=sorted((GAME/'engine').rglob('*.ws'))
    results=[]
    for pattern in (r'GetMusicPosition|GetMusicState|OnMusicFinished|OnMusicEnded',r'GetBiome|OnVista|OnLandmarkDiscovered'):
        matches=[]
        for path in files:
            for line,text in enumerate(path.read_text(encoding='utf-8-sig').splitlines(),1):
                if re.search(pattern,text):matches.append(dict(path=str(path),line=line))
        results.append(dict(scope=str(GAME/'engine'),files=len(files),pattern=pattern,matches=matches,
                            conclusion='Only an inspected-API negative; not proof no native engine capability exists.'))
    tree=ET.parse(WWISE/'Interactive Music Hierarchy/music.wwu')
    ids={'rain_intensity':'{2F4C8EC9-2A33-4D86-988C-FBC94F110301}',
         'wind_intensity':'{626DA028-6576-4E62-9FB6-B48496BA3100}',
         'ambient_time':'{418566CC-6F36-45D0-A7C8-E9AA0D61C9CB}'}
    counts={name:sum(n.get('ID')==id for n in tree.iter('ObjectRef')) for name,id in ids.items()}
    return dict(engine_queries=results,music_work_unit_weather_rtpc_reference_counts=counts,
                weather_limit='Global weather RTPC definitions exist elsewhere; no claim about their native engine updates or every audio hierarchy.')


def build_audit():
    return dict(schema=1,date='2026-10-19',source_status='Static source paths; no new runtime validation.',
                signals=catalog(),approved_cues=cues(),bounded_negative_evidence=bounded_negatives(),retail_tested=False)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.output.exists():raise FileExistsError(a.output)
    result=build_audit()
    a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(signals=len(result['signals']),approved_cues=len(result['approved_cues']))))
