"""Original bounded transforms. All copied third-party bodies stay private."""
import importlib.util,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(name):
 s=importlib.util.spec_from_file_location(name,ROOT/'tools'/(name+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
p=load('patch-ink-gear-grid');layout=load('polish-hud-layout');E=ROOT/'reference/ink-and-iron-0.8.7/migration-evidence'
def menu_button(text):
 if 'currentPadIconWidth' in text:return layout.button(text)
 # A few unchanged upstream secondary movies embed the earlier native renderer.
 # Keep its API and hold-state model; apply the same accepted optical measurements.
 text=p.add(text,'InputFeedbackButton','private var qfXboxScaleX:Number = NaN;\n      private var qfXboxScaleY:Number = NaN;')
 scale='''if(this._gpadIcon == this.mcIconXbox)
         {
            if(isNaN(this.qfXboxScaleX))
            {
               this.qfXboxScaleX = this._gpadIcon.scaleX;
               this.qfXboxScaleY = this._gpadIcon.scaleY;
            }
            this._gpadIcon.scaleX = this.qfXboxScaleX * 0.6875;
            this._gpadIcon.scaleY = this.qfXboxScaleY * 0.6875;
         }
         '''
 text=p.one(text,'hitArea = this._gpadIcon["viewrect"] as Sprite;',scale+'hitArea = this._gpadIcon["viewrect"] as Sprite;')
 text=p.one(text,'iconWidth = hitArea ? hitArea.width : this._gpadIcon.width;','iconWidth = hitArea ? hitArea.width * Math.abs(this._gpadIcon.scaleX) : this._gpadIcon.width;')
 text=p.one(text,'this._labelPosition = iconWidth + TEXT_PADDING_PAD;','this._labelPosition = iconWidth + (this._gpadIcon == this.mcIconXbox ? 7 : TEXT_PADDING_PAD);')
 width='this._currentWidth = iconWidth + textField.width + TEXT_PADDING_PAD + ('+('this.tfHoldPrefix.visible' if 'this._currentWidth = iconWidth + textField.width + TEXT_PADDING_PAD + (this.tfHoldPrefix.visible' in text else 'this._holdDuration > 0')+' ? this.tfHoldPrefix.width : 0);'
 text=p.one(text,width,'this._currentWidth = textField.x + textField.width;')
 text=p.one(text,'textField.x = this._labelPosition + this.tfHoldPrefix.width;','textField.x = this._labelPosition + this.tfHoldPrefix.width + (this._gpadIcon == this.mcIconXbox ? 4 : 0);')
 baseline='''textField.width = textField.textWidth + TEXT_OFFSET;
            if(this._gpadIcon == this.mcIconXbox && this._gpadIcon.visible && textField.numLines > 0)
            {
               textField.y = this._gpadIcon.y - 2 - (textField.getLineMetrics(0).ascent + textField.getLineMetrics(0).descent) / 2;
               if(this.tfHoldPrefix && this.tfHoldPrefix.visible && this.tfHoldPrefix.numLines > 0)
                  this.tfHoldPrefix.y = textField.y + textField.getLineMetrics(0).ascent - this.tfHoldPrefix.getLineMetrics(0).ascent;
               this._currentWidth = textField.x + textField.width;
            }'''
 return p.one(text,'textField.width = textField.textWidth + TEXT_OFFSET;',baseline)
def one_file(folder,name):
 paths=list(folder.rglob(name+'.as'))
 if name=='HubMap' and len(paths)>1:paths=[p for p in paths if p.as_posix().endswith('/red/game/witcher3/menus/worldmap/HubMap.as')]
 if len(paths)!=1:raise ValueError('Nonunique class '+name)
 return paths[0]
def body(text,name):
 signatures=list(re.finditer(r'(?:override )?(?:public|private|protected|internal) function '+re.escape(name)+r'\([^\n]*',text))
 if len(signatures)!=1:raise ValueError('Nonunique method '+name)
 sig=signatures[0];a,z=p.trace.body_span(text,sig[0]);return sig,a,z
def replace_body(text,name,source):
 _,a,z=body(text,name);_,b,y=body(source,name);return text[:a+1]+source[b+1:y]+text[z:]
def common(text):
 current=one_file(E/'installed-export/panel_common/scripts','MenuCommon').read_text(encoding='utf-8-sig')
 imports=set(re.findall(r'^   import [^;]+;',text,re.M));needed=set(re.findall(r'^   import [^;]+;',current,re.M))-imports
 text=text.replace('   import ', '\n'.join(sorted(needed))+'\n   import ',1)
 fields=re.findall(r'^      private var ow\w+:[^;]+;',current,re.M)
 if len(fields)<15 or 'OWOpen' in text:raise ValueError('OW merge precondition')
 methods=[]
 for match in re.finditer(r'^      (?:public|private|protected) function (?:OW|ow)\w+\([^\n]*',current,re.M):
  _,end=p.trace.body_span(current,match[0]);methods.append(current[match.start():end+1])
 if len(methods)!=26:raise ValueError('OW method set changed')
 return p.add(text,'MenuCommon','\n'.join(fields+methods))
def hoods_slot(text):
 official=one_file(ROOT/'reference/ink-and-iron-0.8.6/inventory-source/hoods-export/scripts','SlotPaperdoll').read_text(encoding='utf-8-sig')
 if 'slotData.isDyeable' in text:raise ValueError('Already has Hoods rule; review equivalence')
 return replace_body(text,'canDrop',official)
def hoods_data(text):return p.one(text,'public var canBeDyed:Boolean;','public var canBeDyed:Boolean;\n      public var isDyeable:Boolean;')
def topbar(text):
 # The shared ApplicationDomain may supply RC2's renderer, which intentionally
 # has no upstream iaiPadIcon helper. Resolve its existing public icon clips.
 text=p.one(text,'this.mcLeftGamepadButton.iaiPadIcon()','this.qfMenuPadIcon(this.mcLeftGamepadButton)')
 text=p.one(text,'btn.iaiPadIcon()','this.qfMenuPadIcon(btn)')
 return p.add(text,'TopBarNew','''protected function qfMenuPadIcon(btn:InputFeedbackButton) : MovieClip
      {
         if(!btn) return null;
         for each(var key:String in ["mcIconXbox","mcIconPS","mcIconPS4","mcIconPS5","mcIconSteam","mcIconSwitch"])
         {
            if(key in btn)
            {
               var clip:MovieClip = btn[key] as MovieClip;
               if(clip && clip.visible) return clip;
            }
         }
         return null;
      }''')
def smooth_map(text):
 installed=(E/'installed-export/panel_worldmap/scripts/red/game/witcher3/menus/worldmap/HubMap.as').read_text(encoding='utf-8-sig')
 installed=installed.replace('_smLastScrollTime','inkLastPanTime').replace('_smZoomAccum','inkZoomAccum')
 text=replace_body(text,'handleScrollAndZoomTimer',installed)
 for constant in ('SHOW_INTERVAL','FADING_GRADIENT_DURATION','FADING_TEXTURES_DURATION'):
  rx=r'(const '+constant+r':\* = )([^;]+);'
  value=re.search(rx,installed)
  if not value or len(re.findall(rx,text))!=1:raise ValueError('Smooth Map constant changed')
  text=re.sub(rx,lambda m:m[1]+value[2]+';',text)
 return text
