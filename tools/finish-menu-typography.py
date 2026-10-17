"""Bounded Menus v4 transforms against exact v3 classes; private assets stay local."""
import importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('v3type',ROOT/'tools/refine-menu-typography.py');v=importlib.util.module_from_spec(s);s.loader.exec_module(v)
p=v.p

# Reuse the original implementation, changing explicit role parameters and cache
# identity. No global font definition or caller-owned data is changed.
CAPS=v.HELPER[v.HELPER.index('      private function qfCaps'):v.HELPER.index('      private function qfTypeTree')]
CAPS=CAPS.replace('requested:Number = 0)', 'requested:Number = 0, ratio:Number = 0.88, tracking:Number = 0.9, heavy:Boolean = false)')
CAPS=CAPS.replace('var shown:String = "";', '''if(rec && rec.explicit && requested <= 0)
         {
            size = rec.size;
            ratio = rec.ratio;
            tracking = rec.tracking;
            heavy = rec.heavy;
         }
         var explicit:Boolean = requested > 0 || (rec && rec.explicit);
         var shown:String = "";''')
CAPS=CAPS.replace('var signature:String = src + "|" + size + "|" + tf.width + "|" + tf.textColor;', 'var signature:String = src + "|" + size + "|" + ratio + "|" + tracking + "|" + heavy + "|" + tf.width + "|" + tf.textColor;')
CAPS=CAPS.replace('base.font = "$NormalFont";', 'base.font = heavy ? "$BoldFont" : "$NormalFont";').replace('base.bold = false;', 'base.bold = heavy;')
CAPS=CAPS.replace('base.letterSpacing = 0.65;', 'base.letterSpacing = tracking;').replace('size * 0.80','size * ratio').replace('lower[i] ? 0.80 : 1','lower[i] ? ratio : 1')
CAPS=CAPS.replace('Math.max(0.82,Math.min', 'Math.max(size >= 28 ? 0.5625 : 0.82,Math.min')
CAPS=CAPS.replace('size:size,signature:signature', 'size:size,ratio:ratio,tracking:tracking,heavy:heavy,explicit:explicit,signature:signature')
CAPS=CAPS.replace('var shown:String = "";', '''var originalWrap:Boolean = rec && rec.didWrap ? rec.wrap : tf.wordWrap;
         var originalMulti:Boolean = rec && rec.didWrap ? rec.multi : tf.multiline;
         if(rec && rec.didWrap)
         {
            tf.wordWrap = originalWrap;
            tf.multiline = originalMulti;
         }
         var didWrap:Boolean = false;
         var shown:String = "";''')
CAPS=CAPS.replace('tf.text == rec.shown && mixed) return;', 'tf.text == rec.shown && mixed && !rec.didWrap) return;')
CAPS=CAPS.replace('var fit:Number = Math.max(size >= 28 ? 0.5625 : 0.82,Math.min(1,(tf.width - 4) / tf.textWidth));', '''var minimum:Number = size >= 28 ? 0.5625 : 0.82;
            var required:Number = Math.min(1,(tf.width - 4) / tf.textWidth);
            var fit:Number = Math.max(minimum,required);
            if(required < minimum && size >= 28)
            {
               tf.wordWrap = true;
               tf.multiline = true;
               didWrap = true;
            }''')
CAPS=CAPS.replace('bounded.size = size * fit * (lower[i] ? ratio : 1);','bounded.size = size * fit * (lower[i] ? ratio : 1);\n               bounded.letterSpacing = tracking * fit;')
CAPS=CAPS.replace('this.qfTypeRecords[tf] =', '''if(didWrap)
         {
            // Preserve all source data; only a bounded display title is shortened.
            var guard:int = 0;
            while(tf.textHeight > tf.height - 4 && tf.length > 4 && guard < 256)
            {
               tf.replaceText(tf.length - 2,tf.length,"…");
               guard++;
            }
         }
         this.qfTypeRecords[tf] =''')
CAPS=CAPS.replace('shown:shown,size:size','shown:tf.text,size:size').replace('explicit:explicit,signature:signature','explicit:explicit,wrap:originalWrap,multi:originalMulti,didWrap:didWrap,signature:signature')
TREE=v.HELPER[v.HELPER.index('      private function qfTypeTree'):]
TREE=TREE.replace('var name:String = tf.name.toLowerCase();', '''var name:String = tf.name.toLowerCase();
               if(name == "txtitemdescription" || name == "tfitemdescription") this.qfProse(tf);''')
PROSE='''private function qfProse(tf:flash.text.TextField) : void
      {
         if(!tf || !tf.visible || tf.length == 0 || tf.length > 100 || tf.text.indexOf("\\n") >= 0) return;
         var probe:flash.text.TextField = new flash.text.TextField();
         probe.embedFonts = true;
         probe.autoSize = "left";
         var format:flash.text.TextFormat = new flash.text.TextFormat("$BodyFont",19);
         format.letterSpacing = 0;
         var size:Number = 19;
         while(size >= 17.5)
         {
            format.size = size;
            probe.defaultTextFormat = format;
            probe.text = tf.text;
            if(probe.textWidth <= tf.width - 4 || size == 17.5) break;
            size -= 0.25;
         }
         var change:flash.text.TextFormat = new flash.text.TextFormat();
         change.size = size;
         change.letterSpacing = 0;
         tf.setTextFormat(change);
      }'''

def replace_function(text,name,method):
 sig,a,z=p.body(text,name)
 return text[:sig.start()]+method.strip()+text[z+1:]

def helper(text,cls):
 text=replace_function(text,'qfCaps',CAPS)
 text=replace_function(text,'qfTypeTree',TREE)
 return p.p.add(text,cls,PROSE)

ALIGN='''private function qfAlignRecipe(name:flash.text.TextField, status:flash.text.TextField, originalName:flash.text.TextField, originalStatus:flash.text.TextField, h:Number) : void
      {
         if(!name || !status || !originalName || !originalStatus || !name.visible || !status.visible || name.numLines == 0 || status.numLines == 0) return;
         var a:flash.text.TextLineMetrics = name.getLineMetrics(0);
         var b:flash.text.TextLineMetrics = status.getLineMetrics(0);
         // Installed Gentium's H cap height / ascender = 1260 / 1940.
         var capA:Number = a.ascent * (1260 / 1940);
         var capB:Number = b.ascent * (1260 / 1940);
         var nameExtra:Number = 0;
         var statusExtra:Number = 0;
         var i:int;
         for(i = 0; i < name.numLines - 1; i++) nameExtra += name.getLineMetrics(i).height;
         for(i = 0; i < status.numLines - 1; i++) statusExtra += status.getLineMetrics(i).height;
         var center:Number = (originalName.y + 2 + a.ascent - capA + originalStatus.y + 2 + b.ascent) / 2;
         var height:Number = capA + nameExtra + 4 + capB + statusExtra;
         var top:Number = Math.max(2,Math.min(center - height / 2,h - height - 4));
         name.y = top + capA - a.ascent - 2;
         status.y = top + capA + nameExtra + 4 + capB - b.ascent - 2;
         name.height = name.textHeight + 6;
         status.height = status.textHeight + 6;
      }'''

def crafting(text):
 text=helper(text,'ItemCraftingModule');text=p.p.add(text,'ItemCraftingModule',ALIGN)
 text=p.p.one(text,'this.qfCaps(own,18);','this.qfCaps(own,19.5,0.90,0.85);')
 text=p.p.one(text,'this.qfCaps(own,16);','''this.qfCaps(own,15.5,0.86,0.5);
         if(well)
         {
            this.qfCaps(nm,19.5,0.90,0.85);
            var qfNameBefore:Number = nm.y;
            this.qfAlignRecipe(nm,own,tf,s2,h);
            // inkLevelTag rebases these from the source name on every refresh.
            if(rec.lvBox && rec.lvTF && rec.lvTF.visible)
            {
               rec.lvBox.y = rec.lvBox.y + nm.y - qfNameBefore;
               rec.lvTF.y = rec.lvTF.y + nm.y - qfNameBefore;
            }
            if(rec.loz && rec.loz.visible) rec.loz.y = own.y + Math.round((own.textHeight + 4) / 2) - 3;
         }''')
 text=p.p.one(text,'this.qfCaps(own,21);','this.qfCaps(own,21.5,0.90,1.1);')
 text=p.p.one(text,'tf.textColor = good ? 10787199 : 14239803;','tf.textColor = good ? 10787199 : 9603966;')
 text=p.p.one(text,'ct.textColor = good ? 14861439 : 14239803;','ct.textColor = good ? 14861439 : 9603966;')
 text=v.append_method(text,'inkCraft','this.qfCaps(rec.title,32,0.92,1.6,true);')
 # This pass executes before the existing card layout measures wrapped height.
 text=p.p.one(text,'this.inkTipType(m as DisplayObjectContainer,0);','this.inkTipType(m as DisplayObjectContainer,0);\n            this.qfProse(this.inkTipMod.txtItemDescription);')
 return text

FOOTER='''private var qfFooterPositions:flash.utils.Dictionary = new flash.utils.Dictionary(true);

      private function qfFooter(node:flash.display.DisplayObjectContainer, depth:int = 0) : void
      {
         if(!node || depth > 6) return;
         if(node is red.game.witcher3.controls.InputFeedbackButton)
         {
            var button:flash.display.MovieClip = node as flash.display.MovieClip;
            var label:flash.text.TextField = button["textField"] as flash.text.TextField;
            var prefix:flash.text.TextField = "tfHoldPrefix" in button ? button["tfHoldPrefix"] as flash.text.TextField : null;
            if(label && label.visible && label.numLines > 0)
            {
               var rec:Object = this.qfFooterPositions[label];
               var line:flash.text.TextLineMetrics = label.getLineMetrics(0);
               var center:Number = rec && Math.abs(label.y - rec.lastY) < 0.01 ? rec.center : label.y + 2 + (line.ascent + line.descent) / 2;
               var color:uint = label.textColor;
               var red:uint = color >> 16 & 255;
               var green:uint = color >> 8 & 255;
               var blue:uint = color & 255;
               if(color != 14861439 && !(red > green + 50 && red > blue + 50)) label.textColor = button.enabled ? 10787199 : 7829103;
               this.qfCaps(label,17,0.88,0.55);
               line = label.getLineMetrics(0);
               label.y = center - 2 - (line.ascent + line.descent) / 2;
               this.qfFooterPositions[label] = {center:center,lastY:label.y};
               if(prefix && prefix.visible && prefix.numLines > 0)
               {
                  this.qfCaps(prefix,17,0.88,0.55);
                  prefix.y = label.y + line.ascent - prefix.getLineMetrics(0).ascent;
                  label.x = prefix.x + prefix.textWidth + 4;
               }
            }
            return;
         }
         for(var i:int = 0; i < node.numChildren; i++)
         {
            var child:flash.display.DisplayObject = node.getChildAt(i);
            if(child.visible && child is flash.display.DisplayObjectContainer) this.qfFooter(child as flash.display.DisplayObjectContainer,depth + 1);
         }
      }'''

def common(text):
 full='private var qfTypeRecords:flash.utils.Dictionary = new flash.utils.Dictionary(true);\n'+CAPS+TREE+PROSE+'\n'+FOOTER
 text=p.p.add(text,'MenuCommon',full)
 return v.append_method(text,'inkArtFrame','this.qfFooter(this.mcInpuFeedback);')

def finish(text,cls):
 text=helper(text,cls)
 if cls=='TextAreaModule':text=p.p.one(text,'this.qfCaps(this.tfTitle,30);','this.qfCaps(this.tfTitle,31,0.92,1.25,true);')
 if cls=='FeedbackDropdownMenuListItem':text=p.p.one(text,'this.qfCaps(this.textField,25);','this.qfCaps(this.textField,25,0.90,1.1);')
 return text
