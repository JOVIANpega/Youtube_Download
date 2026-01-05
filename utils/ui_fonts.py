#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
字體管理
全域字體物件與 A-/A+ 廣播更新
"""

import tkinter as tk
from tkinter import font
from constants import DEFAULT_FONT_SIZE, MIN_FONT_SIZE, MAX_FONT_SIZE

class FontManager:
    """字體管理器"""
    
    def __init__(self, root):
        self.root = root
        self.current_size = DEFAULT_FONT_SIZE
        self.fonts = {}
        self.widgets = []
        
        # 創建字體物件
        self.create_fonts()
        
    def create_fonts(self):
        """創建字體物件"""
        self.fonts = {
            'default': font.Font(family='Microsoft YaHei', size=self.current_size),
            'bold': font.Font(family='Microsoft YaHei', size=self.current_size, weight='bold'),
            'small': font.Font(family='Microsoft YaHei', size=max(8, self.current_size - 2)),
            'large': font.Font(family='Microsoft YaHei', size=self.current_size + 2, weight='bold'),
            'monospace': font.Font(family='Consolas', size=self.current_size),
            # 提供更完整符號/emoji 支援的字體（Windows 常見）
            'symbols': font.Font(family='Segoe UI Symbol', size=self.current_size),
            'emoji': font.Font(family='Segoe UI Emoji', size=self.current_size),
        }
        
    def get_font(self, font_type='default'):
        """獲取指定類型的字體"""
        return self.fonts.get(font_type, self.fonts['default'])
        
    def register_widget(self, widget, font_type='default'):
        """註冊需要字體更新的控件"""
        self.widgets.append((widget, font_type))
        try:
            widget.configure(font=self.get_font(font_type))
        except tk.TclError:
            # 某些控件（如 ttk.Button）不支援 font 選項，忽略錯誤
            pass
        
    def update_fonts(self):
        """更新所有字體大小"""
        # 更新字體物件
        for font_obj in self.fonts.values():
            current_family = font_obj.actual('family')
            current_weight = font_obj.actual('weight')
            current_slant = font_obj.actual('slant')
            
            if 'small' in str(font_obj):
                new_size = max(8, self.current_size - 2)
            elif 'large' in str(font_obj):
                new_size = self.current_size + 2
            else:
                new_size = self.current_size
                
            font_obj.configure(size=new_size)
        
        # 更新已註冊的控件
        for widget, font_type in self.widgets[:]:
            try:
                widget.configure(font=self.get_font(font_type))
            except tk.TclError:
                # 控件已被銷毀，從列表中移除
                self.widgets.remove((widget, font_type))
                
    def increase_font(self):
        """增大字體"""
        if self.current_size < MAX_FONT_SIZE:
            self.current_size += 1
            self.update_fonts()
            
    def decrease_font(self):
        """減小字體"""
        if self.current_size > MIN_FONT_SIZE:
            self.current_size -= 1
            self.update_fonts()
            
    def set_font_size(self, size):
        """設置字體大小"""
        if MIN_FONT_SIZE <= size <= MAX_FONT_SIZE:
            self.current_size = size
            self.update_fonts()
            
    def apply_to_widget(self, widget, font_type='default'):
        """將字體應用到控件"""
        try:
            widget.configure(font=self.get_font(font_type))
        except tk.TclError:
            # 某些控件（如 ttk.Button）不支援 font 選項，忽略錯誤
            pass
        
    def apply_to_tree(self, parent, font_type='default'):
        """遞歸應用字體到控件樹"""
        try:
            self.apply_to_widget(parent, font_type)
        except:
            pass
            
        for child in parent.winfo_children():
            self.apply_to_tree(child, font_type)

    def apply_ttk_default_styles(self):
        """將字體應用到常見 ttk 控件的預設樣式。
        注意：某些 ttk 控件不支援直接通過 widget.configure(font=...) 設置字體，
        需透過樣式設定。呼叫一次以套用全域樣式。
        """
        try:
            import tkinter.ttk as ttk
            style = ttk.Style(self.root)
            # 為常見樣式設置字體
            style.configure('TLabel', font=self.get_font('default'))
            style.configure('TButton', font=self.get_font('large'), padding=(8, 4))
            style.configure('TEntry', font=self.get_font('default'))
            style.configure('TCombobox', font=self.get_font('default'))
            style.configure('TRadiobutton', font=self.get_font('default'))
            style.configure('TCheckbutton', font=self.get_font('default'))
            style.configure('TLabelframe.Label', font=self.get_font('bold'))
        except Exception:
            # 若樣式套用失敗則忽略
            pass