# -*- coding: utf-8 -*-
"""
Builder & Exporter for Dashboard_Quang_Cao.html
Synchronizes Dashboard_Quang_Cao.html to brain artifact dashboard.html
"""

import os
import shutil

src = 'Dashboard_Quang_Cao.html'
dest = r'C:\Users\hungnv\.gemini\antigravity\brain\cb140b8e-59b1-4f14-8019-0f8942e7ecfb\dashboard.html'

if os.path.exists(src):
    shutil.copyfile(src, dest)
    size_kb = os.path.getsize(src) / 1024
    print(f"Successfully synced {src} ({size_kb:.1f} KB) to {dest}")
else:
    print(f"Error: {src} not found!")
