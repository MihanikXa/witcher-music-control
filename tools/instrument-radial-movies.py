"""Original bounded checkpoint insertion; diagnostic only, never suppress errors."""
import re

def body_span(text,signature):
 start=text.index(signature);left=text.index('{',start);depth=1;i=left+1;quote=None;comment=None
 while depth:
  ch=text[i];n=text[i:i+2]
  if comment=='line':
   if ch=='\n':comment=None
  elif comment=='block':
   if n=='*/':comment=None;i+=1
  elif quote:
   if ch=='\\':i+=1
   elif ch==quote:quote=None
  elif n=='//':comment='line';i+=1
  elif n=='/*':comment='block';i+=1
  elif ch in ('"',"'"):quote=ch
  elif ch=='{':depth+=1
  elif ch=='}':depth-=1
  i+=1
 return left,i-1

def wrap(text,signature,label,root=False):
 a,z=body_span(text,signature);old=text[a+1:z];call='this.qfRadialTrace' if root else 'this.qfDiagEmit'
 prefix=''
 if re.search(r'function (InputFeedbackButton|HintButton|ModuleInputFeedback)\(',signature):
  if old.count('super();')!=1:raise ValueError('Constructor super contract changed')
  pos=old.index('super();')+len('super();');prefix=old[:pos];old=old[pos:]
 body=prefix+'\n'+call+'("'+label+' enter");\ntry {\n'+old+'\n'+call+'("'+label+' exit");\n} catch(qfDiagError:Error) {\n'+call+'("FAULT '+label+' " + qfDiagError.name + ": " + qfDiagError.message);\nthrow qfDiagError;\n}\n'
 return text[:a+1]+body+text[z:]

ROOT_HELPER='''
      private var qfDiagLines:Array = [];
      private var qfDiagFaults:Array = [];
      private var qfDiagText:TextField;
      public function qfRadialTrace(message:String) : void
      {
         try {
            if(!this.qfDiagLines) this.qfDiagLines = [];
            if(!this.qfDiagFaults) this.qfDiagFaults = [];
            trace("[QFR] " + message);
            if(message.indexOf("FAULT") >= 0 && this.qfDiagFaults.indexOf(message) < 0) {
               this.qfDiagFaults.push(message);
               if(this.qfDiagFaults.length > 5) this.qfDiagFaults.shift();
            }
            this.qfDiagLines.push(message);
            if(this.qfDiagLines.length > 25) this.qfDiagLines.shift();
            if(!this.qfDiagText) {
               this.qfDiagText = new TextField();
               this.qfDiagText.name = "QFRDiagnosticLedger";
               this.qfDiagText.x = 40; this.qfDiagText.y = 55;
               this.qfDiagText.width = 1450; this.qfDiagText.height = 620;
               this.qfDiagText.defaultTextFormat = new TextFormat("$TitleFont",16,0xFFFFFF);
               this.qfDiagText.embedFonts = true;
               this.qfDiagText.multiline = true; this.qfDiagText.wordWrap = true;
               this.qfDiagText.background = true; this.qfDiagText.backgroundColor = 0x16191B;
               this.qfDiagText.mouseEnabled = false; this.qfDiagText.selectable = false;
               if(stage) stage.addChild(this.qfDiagText);
            }
            this.qfDiagText.text = "QFR TRACE D1 (diagnostic, not a fix)\\n" + this.qfDiagFaults.join("\\n") + "\\n" + this.qfDiagLines.join("\\n");
            if(stage && this.qfDiagText.parent == stage) stage.setChildIndex(this.qfDiagText,stage.numChildren-1);
         } catch(qfLedgerError:Error) { trace("[QFR LEDGER ERROR] " + qfLedgerError.message); }
      }
      private function qfDiagDetach(e:Event) : void
      {
         if(this.qfDiagText && this.qfDiagText.parent) this.qfDiagText.parent.removeChild(this.qfDiagText);
         if(stage) stage.removeEventListener(InputEvent.INPUT,this.qfDiagRawInput,false);
      }
      private function qfDiagRawInput(e:InputEvent) : void
      {
         if(e.details && (e.details.code == 9 || e.details.navEquivalent == "gamepad_L1"))
            this.qfRadialTrace("AS raw input code=" + e.details.code + " nav=" + e.details.navEquivalent + " value=" + e.details.value);
      }
'''

CHILD_HELPER='''
      private var qfDiagSeen:Object;
      private function qfDiagEmit(message:String) : void
      {
         if(!this.qfDiagSeen) this.qfDiagSeen = {};
         if(message.indexOf("FAULT") < 0 && this.qfDiagSeen[message]) return;
         this.qfDiagSeen[message] = true;
         trace("[QFR] " + message);
         try {
            var qfNode:Object = this;
            while(qfNode) {
               if("qfRadialTrace" in qfNode) { qfNode["qfRadialTrace"](message); return; }
               qfNode = qfNode.parent;
            }
            if(stage) {
               var qfIndex:int = 0;
               while(qfIndex < stage.numChildren) {
                  qfNode = stage.getChildAt(qfIndex);
                  if("qfRadialTrace" in qfNode) { qfNode["qfRadialTrace"](message); return; }
                  qfIndex++;
               }
            }
         } catch(qfEmitError:Error) { trace("[QFR ROUTE ERROR] " + qfEmitError.message); }
      }
'''

def insert_helper(text,class_name,helper):
 match=re.search(r'\bclass\s+'+class_name+r'\b[^\{]*\{',text)
 if not match:raise ValueError('Class missing')
 return text[:match.end()]+helper+text[match.end():]

def root(text):
 text=insert_helper(text,'Hud',ROOT_HELPER)
 text=wrap(text,'override protected function configUI()', 'AS HUD configUI',True)
 text=text.replace('super.configUI();','if(stage) stage.addEventListener(InputEvent.INPUT,this.qfDiagRawInput,false,0,true);\nthis.addEventListener(Event.REMOVED_FROM_STAGE,this.qfDiagDetach,false,0,true);\nsuper.configUI();',1)
 for cls in ('InputFeedbackButton','HintButton','HudModuleBase','W3ScrollingList','ModuleInputFeedback'):
  needle=re.search(r'var \w+:'+cls+r' = new '+cls+r'\(\);',text)
  if needle:text=text[:needle.start()]+'this.qfRadialTrace("AS HUD preload '+cls+' before");\n'+needle.group()+'\nthis.qfRadialTrace("AS HUD preload '+cls+' after");'+text[needle.end():]
 text=wrap(text,'override protected function loadModule(', 'AS HUD loadModule',True)
 text=wrap(text,'private function handleMovieLoadComplete(', 'AS HUD loadComplete',True)
 text=wrap(text,'private function handleMovieLoadError(', 'AS HUD loadError',True)
 text=text.replace('var _loc6_:HudModuleManagerEntry = this.moduleManager.FindModuleByName(param1);','this.qfRadialTrace("AS request " + param1);\nvar _loc6_:HudModuleManagerEntry = this.moduleManager.FindModuleByName(param1);',1)
 text=text.replace('var _loc2_:LoaderInfo = LoaderInfo(param1.target);','var _loc2_:LoaderInfo = LoaderInfo(param1.target);\nthis.qfRadialTrace("AS loaded " + _loc2_.url);',1)
 a,z=body_span(text,'private function handleMovieLoadError(')
 chunk=text[a+1:z].replace('var _loc2_:LoaderInfo = LoaderInfo(param1.target);','var _loc2_:LoaderInfo = LoaderInfo(param1.target);\nthis.qfRadialTrace("FAULT AS loadError url=" + _loc2_.url + " event=" + param1);',1)
 text=text[:a+1]+chunk+text[z:]
 return text

def component(text,name,label):
 text=insert_helper(text,name,CHILD_HELPER)
 for signature in ['override protected function configUI()']:
  if signature in text:text=wrap(text,signature,'AS '+label+' configUI')
 if name=='HudModuleRadialMenu':
  for sig in ['override public function ShowElementFromState(', 'public function setSelectedItem(']:
   text=wrap(text,sig,'AS radial '+sig.split('function ')[1].split('(')[0])
  text=text.replace('if(!this.bBlockRadialMenu)','this.qfDiagEmit("AS radial state requested=" + bShow + " blocked=" + this.bBlockRadialMenu + " stick=" + this.bCheckStick);\nif(!this.bBlockRadialMenu)',1)
 if name=='HudModuleItemInfo':text=wrap(text,'public function setRadialMenuOn(','AS iteminfo setRadialMenuOn')
 return text


def prompt(text,name,label):
 text=insert_helper(text,name,CHILD_HELPER)
 if name=='InputFeedbackButton':
  text=insert_helper(text,name,'\npublic function qfDiagProvider() : String { return "'+label+'"; }\n')
  for sig in ['public function InputFeedbackButton()', 'override protected function updateText()', 'protected function SetupGamepadIcon(']:
   text=wrap(text,sig,'AS '+label+' '+sig.split('function ')[1].split('(')[0])
 elif name=='HintButton':
  text=wrap(text,'public function HintButton()','AS '+label+' HintButton constructor')
  text=wrap(text,'protected function alignIcons()','AS '+label+' HintButton alignIcons')
 elif name=='ModuleInputFeedback':
  text=wrap(text,'public function ModuleInputFeedback()','AS '+label+' ModuleInputFeedback constructor')
  text=wrap(text,'protected function createButton(','AS '+label+' createButton')
  found=re.search(r'var (\w+):InputFeedbackButton = new \w+\(\) as InputFeedbackButton;',text)
  if not found:raise ValueError('Renderer construction contract changed')
  variable=found.group(1)
  note='\nthis.qfDiagEmit("AS '+label+' renderer provider=" + (("qfDiagProvider" in '+variable+') ? Object('+variable+')["qfDiagProvider"]() : "un-instrumented first-domain class"));'
  text=text[:found.end()]+note+text[found.end():]
  text=wrap(text,'protected function repositionButtons()','AS '+label+' footer layout')
 return text
