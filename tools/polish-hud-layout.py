"""Original bounded v4 prompt adapters. Xbox only; input/hold contracts intact."""
import importlib.util
from pathlib import Path
s=importlib.util.spec_from_file_location('p',Path(__file__).with_name('patch-ink-hud-movies.py'));p=importlib.util.module_from_spec(s);s.loader.exec_module(p)

def button(t):
    marker='      protected function SetupGamepadIcon(navCode:String) : *'
    if marker not in t:marker='      protected function SetupGamepadIcon(param1:String) : *'
    t=p.one(t,marker,'      private var qfXboxScaleX:Number = NaN;\n      private var qfXboxScaleY:Number = NaN;\n\n'+marker)
    t=p.one(t,'            hitArea = this._gpadIcon["viewrect"] as Sprite;', '''            if(this._gpadIcon == this.mcIconXbox)
            {
               if(isNaN(this.qfXboxScaleX))
               {
                  this.qfXboxScaleX = this._gpadIcon.scaleX;
                  this.qfXboxScaleY = this._gpadIcon.scaleY;
               }
               this._gpadIcon.scaleX = this.qfXboxScaleX * 0.6875;
               this._gpadIcon.scaleY = this.qfXboxScaleY * 0.6875;
            }
            hitArea = this._gpadIcon["viewrect"] as Sprite;''')
    t=p.one(t,'hitArea ? hitArea.width : this._gpadIcon.width;', 'hitArea ? hitArea.width * Math.abs(this._gpadIcon.scaleX) : this._gpadIcon.width;')
    t=p.one(t,'this.currentPadIconWidth + TEXT_PADDING_PAD;', 'this.currentPadIconWidth + (this._gpadIcon == this.mcIconXbox ? 7 : TEXT_PADDING_PAD);')
    t=p.one(t,'this._currentWidth = this.currentPadIconWidth + textField.width + TEXT_PADDING_PAD + (this._holdDuration > 0 || this.forceHold ? this.tfHoldPrefix.width : 0);','this._currentWidth = textField.x + textField.width;')
    t=p.one(t,'textField.x = this._labelPosition + this.tfHoldPrefix.width;','textField.x = this._labelPosition + this.tfHoldPrefix.width + (this._gpadIcon == this.mcIconXbox ? 4 : 0);')
    t=p.one(t,'            textField.width = textField.textWidth + TEXT_OFFSET;', '''            textField.width = textField.textWidth + TEXT_OFFSET;
            if(this._gpadIcon == this.mcIconXbox && this._gpadIcon.visible && textField.numLines > 0)
            {
               textField.y = this._gpadIcon.y - 2 - (textField.getLineMetrics(0).ascent + textField.getLineMetrics(0).descent) / 2;
               if(this.tfHoldPrefix && this.tfHoldPrefix.visible && this.tfHoldPrefix.numLines > 0)
               {
                  this.tfHoldPrefix.y = textField.y + textField.getLineMetrics(0).ascent - this.tfHoldPrefix.getLineMetrics(0).ascent;
               }
               this._currentWidth = textField.x + textField.width;
            }''')
    return t

def footer(t):
    t=p.one(t,'BUTTONS_PADDING:Number = 15','BUTTONS_PADDING:Number = 20')
    # Preserve original anchor calculations, fitting the canvas width when necessary.
    marker='         switch(this._buttonAlign)'
    if marker not in t:marker='         switch(this._align)'
    t=p.one(t,marker,'''         this._canvas.scaleX = this._canvas.scaleY = this._cachedWidth > 0 && buttonsSize > this._cachedWidth ? this._cachedWidth / buttonsSize : 1;
         buttonsSize *= this._canvas.scaleX;
'''+marker)
    return t


def hint(t):
    marker='      protected function alignIcons() : void'
    t=p.one(t,marker,'      private var qfXboxScaleX:Number = NaN;\n      private var qfXboxScaleY:Number = NaN;\n'+marker)
    t=p.one(t,'            _loc5_ = _loc4_["viewrect"] as Sprite;', '''            if(_loc4_ == this.mcIconXbox)
            {
               if(isNaN(this.qfXboxScaleX))
               {
                  this.qfXboxScaleX = _loc4_.scaleX;
                  this.qfXboxScaleY = _loc4_.scaleY;
               }
               _loc4_.scaleX = this.qfXboxScaleX * 0.6875;
               _loc4_.scaleY = this.qfXboxScaleY * 0.6875;
            }
            _loc5_ = _loc4_["viewrect"] as Sprite;''')
    t=p.one(t,'_loc4_.x = _loc1_ + _loc5_.width / 2;', '_loc4_.x = _loc1_ + _loc5_.width * Math.abs(_loc4_.scaleX) / 2;')
    t=p.one(t,'_loc1_ += _loc5_.width + this.ICON_PADDING;', '_loc1_ += _loc5_.width * Math.abs(_loc4_.scaleX) + this.ICON_PADDING;')
    t=p.one(t,'            _loc3_++;\n         }\n      }\n      \n      private function getPadIconFrameLabel', '''            _loc3_++;
         }
         if(this.mcIconXbox && this.mcIconXbox.visible && this.textField && this.textField.numLines > 0)
         {
            this.textField.x = _loc1_ + 2;
            this.textField.y = this.mcIconXbox.y - 2 - (this.textField.getLineMetrics(0).ascent + this.textField.getLineMetrics(0).descent) / 2;
         }
      }

      private function getPadIconFrameLabel''')
    return t
