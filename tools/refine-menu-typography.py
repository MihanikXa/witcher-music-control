"""Menu-owned Gentium display formatting; no localization or data mutations."""
import importlib.util,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('patch',ROOT/'tools/patch-menu-migration.py');p=importlib.util.module_from_spec(s);s.loader.exec_module(p)

HELPER='''private var qfTypeRecords:flash.utils.Dictionary = new flash.utils.Dictionary(true);

      private function qfCaps(tf:flash.text.TextField, requested:Number = 0) : void
      {
         if(!tf || !tf.visible || tf.length == 0) return;
         var rec:Object = this.qfTypeRecords[tf];
         var src:String = rec && tf.text == rec.shown ? rec.source : tf.text;
         if(src.indexOf("[[") >= 0) return;
         var base:flash.text.TextFormat = tf.defaultTextFormat;
         var size:Number = requested > 0 ? requested : Number(base.size);
         if(isNaN(size) || size <= 0) size = rec ? rec.size : 18;
         var shown:String = "";
         var starts:Array = [];
         var ends:Array = [];
         var lower:Array = [];
         var i:int;
         var ch:String;
         for(i = 0; i < src.length; i++)
         {
            ch = src.charAt(i);
            starts.push(shown.length);
            lower.push(ch != ch.toUpperCase());
            shown += ch.toUpperCase();
            ends.push(shown.length);
         }
         var signature:String = src + "|" + size + "|" + tf.width + "|" + tf.textColor;
         // upstream may reapply a uniform TextFormat without changing the text.
         var mixed:Boolean = tf.getTextFormat().size == null;
         if(rec && rec.signature == signature && tf.text == rec.shown && mixed) return;
         var color:uint = tf.textColor;
         tf.text = shown;
         base.font = "$NormalFont";
         base.bold = false;
         base.italic = false;
         base.size = size;
         base.letterSpacing = 0.65;
         base.color = color;
         tf.setTextFormat(base);
         for(i = 0; i < starts.length; i++)
         {
            if(lower[i])
            {
               var small:flash.text.TextFormat = new flash.text.TextFormat();
               small.size = size * 0.80;
               tf.setTextFormat(small,starts[i],ends[i]);
            }
         }
         // Fit only nonwrapping display headings inside their authored bounds.
         // No field, hit area, parent, or content-column geometry is changed.
         if(!tf.wordWrap && tf.autoSize == "none" && tf.width > 12 && tf.textWidth > tf.width - 4)
         {
            var fit:Number = Math.max(0.82,Math.min(1,(tf.width - 4) / tf.textWidth));
            for(i = 0; i < starts.length; i++)
            {
               var bounded:flash.text.TextFormat = new flash.text.TextFormat();
               bounded.size = size * fit * (lower[i] ? 0.80 : 1);
               tf.setTextFormat(bounded,starts[i],ends[i]);
            }
         }
         this.qfTypeRecords[tf] = {source:src,shown:shown,size:size,signature:signature};
      }

      private function qfTypeTree(node:flash.display.DisplayObjectContainer, depth:int = 0) : void
      {
         if(!node || depth > 7) return;
         for(var i:int = 0; i < node.numChildren; i++)
         {
            var child:flash.display.DisplayObject = node.getChildAt(i);
            if(!child.visible || child.alpha == 0) continue;
            var tf:flash.text.TextField = child as flash.text.TextField;
            if(tf && tf.length > 0)
            {
               var name:String = tf.name.toLowerCase();
               // Prose, numeric comparison semantics and search input stay natural.
               if(tf.type == "input" || name.indexOf("description") >= 0 || name.indexOf("body") >= 0 || name.indexOf("story") >= 0 || name.indexOf("value") >= 0 || name.indexOf("count") >= 0) continue;
               var fmt:flash.text.TextFormat = tf.defaultTextFormat;
               if(fmt.font == "$TitleFont" || name == "tfitemname" || name == "txtitemname" || name == "txttitle" || name == "tftitle" || name == "txtcategory") this.qfCaps(tf);
            }
            else if(child is flash.display.DisplayObjectContainer) this.qfTypeTree(child as flash.display.DisplayObjectContainer,depth + 1);
         }
      }'''

def append_method(text,name,code):
 _,a,z=p.body(text,name)
 return text[:z]+'\n         '+code+'\n      '+text[z:]

def add_helper(text,cls):
 if 'qfTypeRecords' in text:raise ValueError('Typography already present')
 return p.p.add(text,cls,HELPER)

def crafting(text):
 text=add_helper(text,'ItemCraftingModule')
 text=p.p.one(text,'own = this.inkOwnTF(r,rec,"nm",tf,"$BoldFont",17,10787199,0);','own = this.inkOwnTF(r,rec,"nm",tf,"$NormalFont",18,10787199,0.65);\n         this.qfCaps(own,18);')
 text=p.p.one(text,'own.textColor = code == 4 ? 8879985 : 14239803;','own.textColor = code == 4 ? 7829103 : 9603966;')
 text=append_method(text,'inkRow','this.qfCaps(own,16);')
 text=append_method(text,'inkHeader','this.qfCaps(own,21);')
 text=append_method(text,'inkRtRender','this.qfTypeTree(this.inkM);')
 # The narrow count/ingredient warning remains distinct from the list status.
 text=p.p.one(text,'rec.count.textColor = ok >= n ? 14861439 : 14239803;','rec.count.textColor = ok >= n ? 14861439 : 9603966;')
 return text

def hook(text,cls,method,root='this'):
 return append_method(add_helper(text,cls),method,'this.qfTypeTree('+root+');')

def class_methods(text):return re.findall(r'(?:public|private|protected|internal) function (\w+)\(',text)
