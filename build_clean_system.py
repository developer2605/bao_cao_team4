# -*- coding: utf-8 -*-
"""
Master update script:
1. Only read the 3 authorized sheets: 'Full', 'Theo Ngày', 'Vị trí quảng cáo'.
2. Use the user's manual notes (from user_manual_notes.json) containing 23 manually annotated ads:
   - 15 ads with 'Sản'
   - 8 ads with 'Ở cữ'
   - 138 ads with 'Chưa ghi chú'
3. Re-generate Bao_cao_quang_cao_Facebook_Cap_Nhat.xlsx (Sheet 6 & Sheet 1 updated).
4. Update Bao_cao_chi_tiet.md & artifact Bao_cao_hieu_qua_quang_cao.md.
5. Update Dashboard_Quang_Cao.html & artifact dashboard.html.
"""

import os
import json
import shutil
import pandas as pd
import numpy as np
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# Load user manual notes
with open('user_manual_notes.json', 'r', encoding='utf-8') as f:
    user_notes = json.load(f)

excel_path = 'sheet_data.xlsx'

# ONLY read 3 authorized sheets
df_full = pd.read_excel(excel_path, sheet_name='Full', skiprows=2, dtype={'Mã quảng cáo': str})
df_daily = pd.read_excel(excel_path, sheet_name='Theo Ngày', dtype={'Mã quảng cáo': str})
df_pos = pd.read_excel(excel_path, sheet_name='Vị trí quảng cáo', dtype={'Mã quảng cáo': str})

# Exclude the 2 deleted ads
deleted_ads = ['52625109508219', '52625109961219']
df_full = df_full.dropna(subset=['Mã quảng cáo']).copy()
df_full['ad_id'] = df_full['Mã quảng cáo'].str.strip()
df_full = df_full[~df_full['ad_id'].isin(deleted_ads)].copy()

df_daily = df_daily.dropna(subset=['Mã quảng cáo']).copy()
df_daily['ad_id'] = df_daily['Mã quảng cáo'].str.strip()
df_daily = df_daily[~df_daily['ad_id'].isin(deleted_ads)].copy()

df_pos = df_pos.dropna(subset=['Mã quảng cáo']).copy()
df_pos['ad_id'] = df_pos['Mã quảng cáo'].str.strip()
df_pos = df_pos[~df_pos['ad_id'].isin(deleted_ads)].copy()

# Parse numeric columns
df_full['spend'] = pd.to_numeric(df_full['Số tiền đã chi tiêu (VND)'], errors='coerce').fillna(0)
df_full['msg'] = pd.to_numeric(df_full['Lượt bắt đầu cuộc trò chuyện qua tin nhắn'], errors='coerce').fillna(0)
df_full['pur'] = pd.to_numeric(df_full['Lượt mua'], errors='coerce').fillna(0)
df_full['cpm'] = np.where(df_full['msg'] > 0, df_full['spend'] / df_full['msg'], 0)
df_full['cpp'] = np.where(df_full['pur'] > 0, df_full['spend'] / df_full['pur'], 0)
df_full['l2_l1'] = np.where(df_full['msg'] > 0, (df_full['pur'] / df_full['msg']) * 100, 0)

# Sort: buyers by cpp asc, then non-buyers by cpm asc
df_pur = df_full[df_full['pur'] > 0].sort_values(by=['cpp', 'cpm'], ascending=[True, True])
df_nopur = df_full[df_full['pur'] == 0].sort_values(by=['cpm', 'spend'], ascending=[True, False])
df_sorted = pd.concat([df_pur, df_nopur], ignore_index=True)

# Build manual keyword classification map
ad_annotations_map = {}
for aid in df_sorted['ad_id']:
    un = user_notes.get(aid, {})
    note = (un.get('notes') or '').strip()
    url = (un.get('postUrl') or '').strip()
    
    note_lower = note.lower()
    if 'ở cữ' in note_lower or 'o cu' in note_lower or 'nghỉ dưỡng' in note_lower:
        kw = 'ocu'
        kw_label = 'Ở cữ'
    elif 'sản' in note_lower or 'san' in note_lower or 'thai sản' in note_lower or 'mđtc' in note_lower or 'chạm đích' in note_lower:
        kw = 'san'
        kw_label = 'Sản'
    else:
        kw = 'none'
        kw_label = 'Chưa ghi chú'
        
    ad_annotations_map[aid] = {
        'keyword': kw,
        'keyword_label': kw_label,
        'note': note,
        'link': url
    }

print(f"Total sorted ads: {len(df_sorted)}")
san_count = sum(1 for a in ad_annotations_map.values() if a['keyword'] == 'san')
ocu_count = sum(1 for a in ad_annotations_map.values() if a['keyword'] == 'ocu')
none_count = sum(1 for a in ad_annotations_map.values() if a['keyword'] == 'none')
print(f"Keyword breakdown: Sản={san_count}, Ở cữ={ocu_count}, Chưa ghi chú={none_count}")

# Save JSON of annotations map for re-use
with open('clean_annotations_map.json', 'w', encoding='utf-8') as f:
    json.dump(ad_annotations_map, f, ensure_ascii=False, indent=2)

print("Saved clean_annotations_map.json!")
