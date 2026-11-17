import json
import os
import pandas as pd
import numpy as np
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

excel_path = 'sheet_data_new.xlsx'
if not os.path.exists(excel_path):
    excel_path = 'sheet_data.xlsx'

# 1. Load Data
EXCLUDE_IDS = ['52625109508219', '52625109961219']

df_full = pd.read_excel(excel_path, sheet_name='Full', skiprows=2, dtype={'Mã quảng cáo': str}).dropna(subset=['Mã quảng cáo']).copy()
df_full['ad_id'] = df_full['Mã quảng cáo'].astype(str).str.strip()
df_full = df_full[~df_full['ad_id'].isin(EXCLUDE_IDS)].copy()

num_cols = ['Lượt bắt đầu cuộc trò chuyện qua tin nhắn', 'Chi phí trên mỗi lượt bắt đầu cuộc trò chuyện qua tin nhắn', 
            'Bình luận về bài viết', 'Lượt mua', 'Chi phí trên mỗi lượt mua', 'Số tiền đã chi tiêu (VND)']
for c in num_cols:
    df_full[c] = pd.to_numeric(df_full[c], errors='coerce')

df_ngay = pd.read_excel(excel_path, sheet_name='Theo Ngày', skiprows=2, dtype={'Mã quảng cáo': str})
df_ngay['ad_id'] = df_ngay['Mã quảng cáo'].ffill().astype(str).str.strip()
df_ngay = df_ngay[~df_ngay['ad_id'].isin(EXCLUDE_IDS)].copy()
df_daily = df_ngay[df_ngay['Ngày'].astype(str).str.strip().str.lower() != 'all'].copy()
for c in num_cols:
    df_daily[c] = pd.to_numeric(df_daily[c], errors='coerce')

df_pos = pd.read_excel(excel_path, sheet_name='Vị trí quảng cáo', skiprows=2, dtype={'Mã quảng cáo': str})
df_pos['ad_id'] = df_pos['Mã quảng cáo'].ffill().astype(str).str.strip()
df_pos['Ngày'] = df_pos['Ngày'].ffill()
df_pos = df_pos[~df_pos['ad_id'].isin(EXCLUDE_IDS)].copy()
df_pos_clean = df_pos[
    (df_pos['Vị trí quảng cáo'].notna()) & 
    (~df_pos['Vị trí quảng cáo'].astype(str).str.lower().str.contains('tổng cộng|all'))
].copy()
for c in num_cols:
    df_pos_clean[c] = pd.to_numeric(df_pos_clean[c], errors='coerce')

# 2. Daily Stability Calculation
daily_stats = {}
for aid, g in df_daily.groupby('ad_id'):
    g_active = g[g['Số tiền đã chi tiêu (VND)'] > 0]
    active_days = len(g_active)
    
    g_msg = g[g['Lượt bắt đầu cuộc trò chuyện qua tin nhắn'] > 0]
    msg_days = len(g_msg)
    cpm_vals = g_msg['Chi phí trên mỗi lượt bắt đầu cuộc trò chuyện qua tin nhắn'].dropna()
    cpm_mean = cpm_vals.mean() if len(cpm_vals) > 0 else np.nan
    cpm_std = cpm_vals.std() if len(cpm_vals) > 1 else (0.0 if len(cpm_vals) == 1 else np.nan)
    cpm_cv = (cpm_std / cpm_mean) if (cpm_mean and cpm_mean > 0) else np.nan
    
    g_pur = g[g['Lượt mua'] > 0]
    pur_days = len(g_pur)
    cpp_vals = g_pur['Chi phí trên mỗi lượt mua'].dropna()
    cpp_mean = cpp_vals.mean() if len(cpp_vals) > 0 else np.nan
    cpp_std = cpp_vals.std() if len(cpp_vals) > 1 else (0.0 if len(cpp_vals) == 1 else np.nan)
    cpp_cv = (cpp_std / cpp_mean) if (cpp_mean and cpp_mean > 0) else np.nan
    
    pur_ratio = (pur_days / active_days) if active_days > 0 else 0
    
    daily_stats[aid] = {
        'active_days': active_days,
        'msg_days': msg_days,
        'pur_days': pur_days,
        'pur_ratio': pur_ratio,
        'cpm_mean': cpm_mean,
        'cpm_cv': cpm_cv,
        'cpp_mean': cpp_mean,
        'cpp_cv': cpp_cv
    }

# 3. Placement Stats Calculation
pos_stats = {}
for aid, g in df_pos_clean.groupby('ad_id'):
    p_agg = g.groupby('Vị trí quảng cáo').agg({
        'Số tiền đã chi tiêu (VND)': 'sum',
        'Lượt bắt đầu cuộc trò chuyện qua tin nhắn': 'sum',
        'Lượt mua': 'sum'
    }).reset_index()
    
    p_agg.rename(columns={
        'Số tiền đã chi tiêu (VND)': 'spend',
        'Lượt bắt đầu cuộc trò chuyện qua tin nhắn': 'msg',
        'Lượt mua': 'pur'
    }, inplace=True)
    
    p_agg['cpp'] = p_agg['spend'] / p_agg['pur']
    p_agg['cpm'] = p_agg['spend'] / p_agg['msg']
    
    p_pur = p_agg[p_agg['pur'] > 0]
    if len(p_pur) > 0:
        best_row = p_pur.sort_values(by=['pur', 'cpp'], ascending=[False, True]).iloc[0]
    else:
        p_msg = p_agg[p_agg['msg'] > 0]
        if len(p_msg) > 0:
            best_row = p_msg.sort_values(by=['msg', 'cpm'], ascending=[False, True]).iloc[0]
        else:
            best_row = p_agg.sort_values(by=['spend'], ascending=[False]).iloc[0]
            
    pos_stats[aid] = {
        'best_pos': best_row['Vị trí quảng cáo'],
        'pos_spend': best_row['spend'],
        'pos_msg': best_row['msg'],
        'pos_pur': best_row['pur'],
        'pos_cpp': best_row['cpp'] if best_row['pur'] > 0 else np.nan,
        'pos_cpm': best_row['cpm'] if best_row['msg'] > 0 else np.nan
    }

# 4. Combine Full Table
records = []
for idx, row in df_full.iterrows():
    aid = row['ad_id']
    spend = row['Số tiền đã chi tiêu (VND)']
    msg = row['Lượt bắt đầu cuộc trò chuyện qua tin nhắn']
    pur = row['Lượt mua']
    cpm = row['Chi phí trên mỗi lượt bắt đầu cuộc trò chuyện qua tin nhắn']
    cpp = row['Chi phí trên mỗi lượt mua']
    cmt = row['Bình luận về bài viết']
    
    d = daily_stats.get(aid, {
        'active_days': 0, 'msg_days': 0, 'pur_days': 0, 'pur_ratio': 0,
        'cpm_mean': np.nan, 'cpm_cv': np.nan, 'cpp_mean': np.nan, 'cpp_cv': np.nan
    })
    p = pos_stats.get(aid, {
        'best_pos': 'Không rõ', 'pos_spend': 0, 'pos_msg': 0, 'pos_pur': 0, 'pos_cpp': np.nan, 'pos_cpm': np.nan
    })
    
    l2_l1 = (pur / msg) if (msg and msg > 0 and pur and pur > 0) else (0.0 if msg and msg > 0 else np.nan)
    active_days = d['active_days']
    pur_days = d['pur_days']
    pur_ratio = d['pur_ratio']
    cpp_cv = d['cpp_cv']
    cpm_cv = d['cpm_cv']
    
    if pd.isna(pur) or pur == 0:
        stability = 'Không có lượt mua'
        recommendation = 'Tắt ngay (Chống lãng phí)'
    elif active_days <= 2 and pur <= 2:
        stability = 'Mẫu ít (1-2 ngày)'
        recommendation = 'Theo dõi thêm'
    elif pur_ratio >= 0.70 and (pd.isna(cpp_cv) or cpp_cv <= 0.65) and (pd.isna(cpm_cv) or cpm_cv <= 0.50):
        stability = 'Rất ổn định'
        if cpp < 100000: recommendation = 'Tăng mạnh ngân sách (Ưu tiên 1)'
        elif cpp < 180000: recommendation = 'Tăng ngân sách (Ưu tiên 2)'
        else: recommendation = 'Duy trì & Tối ưu giá thầu'
    elif pur_ratio >= 0.50 and (pd.isna(cpp_cv) or cpp_cv <= 0.85):
        stability = 'Ổn định'
        if cpp < 100000: recommendation = 'Tăng ngân sách (Ưu tiên 2)'
        elif cpp < 180000: recommendation = 'Tăng nhẹ / Duy trì'
        else: recommendation = 'Duy trì & Tối ưu nội dung'
    else:
        stability = 'Không ổn định'
        if cpp > 300000 or spend > 1500000: recommendation = 'Giảm ngân sách hoặc Tắt'
        else: recommendation = 'Tối ưu lại nội dung & Vị trí'
        
    records.append({
        'ad_id': aid, 'spend': spend, 'msg': msg, 'cpm': cpm, 'pur': pur, 'cpp': cpp,
        'l2_l1': l2_l1, 'cmt': cmt, 'active_days': active_days, 'msg_days': d['msg_days'],
        'pur_days': pur_days, 'pur_ratio': pur_ratio, 'cpm_mean': d['cpm_mean'],
        'cpm_cv': cpm_cv, 'cpp_mean': d['cpp_mean'], 'cpp_cv': cpp_cv,
        'stability': stability, 'recommendation': recommendation,
        'best_pos': p['best_pos'], 'pos_pur': p['pos_pur'], 'pos_cpp': p['pos_cpp']
    })

df_all = pd.DataFrame(records)
df_pur_sorted = df_all[df_all['pur'] > 0].sort_values(by=['cpp', 'cpm'], ascending=[True, True])
df_nopur_sorted = df_all[df_all['pur'].isna() | (df_all['pur'] == 0)].sort_values(by=['cpm', 'spend'], ascending=[True, False])
df_final_sorted = pd.concat([df_pur_sorted, df_nopur_sorted], ignore_index=True)

# Keyword Categorization based EXCLUSIVELY on User Manual Notes (NO other sheets read)
with open('user_manual_notes.json', 'r', encoding='utf-8') as f:
    user_notes = json.load(f)

ad_annotations_map = {}
for aid in df_final_sorted['ad_id']:
    un = user_notes.get(aid, {})
    note = (un.get('notes') or '').strip()
    url = (un.get('postUrl') or '').strip()
    
    note_lower = note.lower()
    if 'ở cữ' in note_lower or 'o cu' in note_lower or 'nghỉ dưỡng' in note_lower:
        kw = 'ocu'
        kw_label = 'Ở cữ'
        grp = 'Gói Ở cữ / Nghỉ dưỡng sau sinh'
    elif 'sản' in note_lower or 'san' in note_lower or 'thai sản' in note_lower or 'mđtc' in note_lower or 'chạm đích' in note_lower:
        kw = 'san'
        kw_label = 'Sản'
        grp = 'Gói Thai sản / Đi đẻ'
    else:
        kw = 'none'
        kw_label = 'Chưa ghi chú'
        grp = 'Chưa phân nhóm'
        
    ad_annotations_map[aid] = {
        'keyword': kw,
        'keyword_label': kw_label,
        'page': 'Nghỉ Dưỡng Sau Sinh' if kw == 'ocu' else ('Khoa Sản' if kw == 'san' else '-'),
        'group': grp,
        'link': url,
        'hook': note if note else '',
        'note': note
    }

df_final_sorted['keyword'] = df_final_sorted['ad_id'].map(lambda x: ad_annotations_map[x]['keyword'])
df_final_sorted['keyword_label'] = df_final_sorted['ad_id'].map(lambda x: ad_annotations_map[x]['keyword_label'])
df_final_sorted['group'] = df_final_sorted['ad_id'].map(lambda x: ad_annotations_map[x]['group'])
df_final_sorted['hook'] = df_final_sorted['ad_id'].map(lambda x: ad_annotations_map[x]['hook'])
df_final_sorted['note'] = df_final_sorted['ad_id'].map(lambda x: ad_annotations_map[x]['note'])
df_final_sorted['link'] = df_final_sorted['ad_id'].map(lambda x: ad_annotations_map[x]['link'])

# 5. Ad ID x Placement Detailed Stability Calculation
df_pos_daily = df_pos_clean[df_pos_clean['Ngày'].astype(str).str.strip().str.lower() != 'all'].copy()

ad_pos_detailed = []
for (aid, pos), g in df_pos_daily.groupby(['ad_id', 'Vị trí quảng cáo']):
    tot_spend = g['Số tiền đã chi tiêu (VND)'].sum()
    tot_msg = g['Lượt bắt đầu cuộc trò chuyện qua tin nhắn'].sum()
    tot_pur = g['Lượt mua'].sum()
    
    active_days = len(g[g['Số tiền đã chi tiêu (VND)'] > 0])
    msg_days = len(g[g['Lượt bắt đầu cuộc trò chuyện qua tin nhắn'] > 0])
    pur_days = len(g[g['Lượt mua'] > 0])
    
    g_pur = g[g['Lượt mua'] > 0]
    cpp_vals = g_pur['Chi phí trên mỗi lượt mua'].dropna()
    cpp_mean = cpp_vals.mean() if len(cpp_vals) > 0 else np.nan
    cpp_std = cpp_vals.std() if len(cpp_vals) > 1 else (0.0 if len(cpp_vals) == 1 else np.nan)
    cpp_cv = (cpp_std / cpp_mean) if (cpp_mean and cpp_mean > 0) else np.nan
    
    g_msg = g[g['Lượt bắt đầu cuộc trò chuyện qua tin nhắn'] > 0]
    cpm_vals = g_msg['Chi phí trên mỗi lượt bắt đầu cuộc trò chuyện qua tin nhắn'].dropna()
    cpm_mean = cpm_vals.mean() if len(cpm_vals) > 0 else np.nan
    cpm_std = cpm_vals.std() if len(cpm_vals) > 1 else (0.0 if len(cpm_vals) == 1 else np.nan)
    cpm_cv = (cpm_std / cpm_mean) if (cpm_mean and cpm_mean > 0) else np.nan
    
    pur_ratio = (pur_days / active_days) if active_days > 0 else 0
    cpa = (tot_spend / tot_pur) if tot_pur > 0 else np.nan
    cpm = (tot_spend / tot_msg) if tot_msg > 0 else np.nan
    conv = (tot_pur / tot_msg) if tot_msg > 0 else np.nan
    
    if tot_pur == 0 or pd.isna(tot_pur):
        stab = 'Không tạo ra đơn'
        rec = 'Tắt vị trí này (Chống lãng phí)'
    elif active_days <= 2 and tot_pur <= 2:
        stab = 'Mẫu ít (1-2 ngày)'
        rec = 'Theo dõi thêm'
    elif pur_ratio >= 0.70 and (pd.isna(cpp_cv) or cpp_cv <= 0.65):
        stab = 'Rất ổn định'
        if cpa < 120000: rec = 'Ưu tiên tăng ngân sách tối đa'
        elif cpa < 180000: rec = 'Tăng ngân sách vị trí'
        else: rec = 'Duy trì ổn định'
    elif pur_ratio >= 0.50 and (pd.isna(cpp_cv) or cpp_cv <= 0.85):
        stab = 'Ổn định'
        if cpa < 150000: rec = 'Tăng nhẹ ngân sách'
        else: rec = 'Duy trì vị trí'
    else:
        stab = 'Không ổn định'
        if cpa > 250000 or tot_spend > 1000000: rec = 'Tắt hoặc giảm mạnh ngân sách'
        else: rec = 'Tối ưu lại nội dung cho vị trí'
        
    ad_pos_detailed.append({
        'ad_id': aid,
        'pos': pos,
        'spend': round(tot_spend),
        'msg': round(tot_msg),
        'pur': round(tot_pur),
        'cpm': round(cpm) if pd.notna(cpm) else None,
        'cpp': round(cpa) if pd.notna(cpa) else None,
        'conv': round(conv * 100) if pd.notna(conv) else None,
        'active_days': active_days,
        'msg_days': msg_days,
        'pur_days': pur_days,
        'pur_ratio': round(pur_ratio * 100),
        'cpm_cv': round(cpm_cv * 100) if pd.notna(cpm_cv) else None,
        'cpp_cv': round(cpp_cv * 100) if pd.notna(cpp_cv) else None,
        'stability': stab,
        'recommendation': rec,
        'keyword': ad_annotations_map.get(aid, {}).get('keyword', 'san')
    })

df_ad_pos_all = pd.DataFrame(ad_pos_detailed)
df_ad_pos_filtered = df_ad_pos_all[df_ad_pos_all['spend'] >= 50000].copy()
df_ad_pos_filtered = df_ad_pos_filtered.sort_values(by=['pur', 'cpp'], ascending=[False, True])

# 6. Build Ads JSON Data for Dashboard (Including daily and placement sub-arrays)
ads_data = []
daily_grouped = df_daily.groupby('ad_id')
pos_grouped = df_pos_clean.groupby('ad_id')

for idx, r in df_final_sorted.iterrows():
    aid = r['ad_id']
    annot = ad_annotations_map.get(aid, {})
    d_list = []
    if aid in daily_grouped.groups:
        g_d = daily_grouped.get_group(aid).sort_values('Ngày', ascending=False)
        for _, dr in g_d.iterrows():
            d_str = str(dr['Ngày'])[:10]
            sp = round(dr['Số tiền đã chi tiêu (VND)']) if pd.notna(dr['Số tiền đã chi tiêu (VND)']) else 0
            m = round(dr['Lượt bắt đầu cuộc trò chuyện qua tin nhắn']) if pd.notna(dr['Lượt bắt đầu cuộc trò chuyện qua tin nhắn']) else 0
            p = round(dr['Lượt mua']) if pd.notna(dr['Lượt mua']) else 0
            cpm = round(dr['Chi phí trên mỗi lượt bắt đầu cuộc trò chuyện qua tin nhắn']) if pd.notna(dr['Chi phí trên mỗi lượt bắt đầu cuộc trò chuyện qua tin nhắn']) else 0
            cpp = round(dr['Chi phí trên mỗi lượt mua']) if pd.notna(dr['Chi phí trên mỗi lượt mua']) else 0
            d_list.append({'date': d_str, 'spend': sp, 'msg': m, 'pur': p, 'cpm': cpm, 'cpp': cpp})
            
    p_list = []
    if aid in pos_grouped.groups:
        g_p = pos_grouped.get_group(aid).groupby('Vị trí quảng cáo').agg({
            'Số tiền đã chi tiêu (VND)': 'sum',
            'Lượt bắt đầu cuộc trò chuyện qua tin nhắn': 'sum',
            'Lượt mua': 'sum'
        }).reset_index().sort_values('Số tiền đã chi tiêu (VND)', ascending=False)
        for _, pr in g_p.iterrows():
            sp = round(pr['Số tiền đã chi tiêu (VND)'])
            m = round(pr['Lượt bắt đầu cuộc trò chuyện qua tin nhắn'])
            p = round(pr['Lượt mua'])
            cpm = round(sp / m) if m > 0 else 0
            cpp = round(sp / p) if p > 0 else 0
            p_list.append({'name': pr['Vị trí quảng cáo'], 'spend': sp, 'msg': m, 'pur': p, 'cpm': cpm, 'cpp': cpp})

    ads_data.append({
        'id': aid,
        'spend': round(r['spend']) if pd.notna(r['spend']) else 0,
        'msg': round(r['msg']) if pd.notna(r['msg']) else 0,
        'pur': round(r['pur']) if pd.notna(r['pur']) else 0,
        'cpm': round(r['cpm']) if pd.notna(r['cpm']) else 0,
        'cpp': round(r['cpp']) if pd.notna(r['cpp']) else 0,
        'l2_l1': round(r['l2_l1'] * 100) if pd.notna(r['l2_l1']) else 0,
        'active_days': int(r['active_days']),
        'pur_days': int(r['pur_days']),
        'pur_ratio': round(r['pur_ratio'] * 100) if pd.notna(r['pur_ratio']) else 0,
        'cpm_cv': round(r['cpm_cv'] * 100) if pd.notna(r['cpm_cv']) else None,
        'cpp_cv': round(r['cpp_cv'] * 100) if pd.notna(r['cpp_cv']) else None,
        'stability': r['stability'],
        'recommendation': r['recommendation'],
        'best_pos': r['best_pos'],
        'pos_pur': round(r['pos_pur']) if pd.notna(r['pos_pur']) else 0,
        'pos_cpp': round(r['pos_cpp']) if pd.notna(r['pos_cpp']) else 0,
        'keyword': annot.get('keyword', 'san'),
        'keyword_label': annot.get('keyword_label', 'Sản'),
        'group': annot.get('group', 'Gói Thai sản Chạm Đích'),
        'hook': annot.get('hook', ''),
        'notes': annot.get('note', ''),
        'link': annot.get('link', ''),
        'daily': d_list,
        'placements': p_list
    })

# 7. Placement Overall Summary
pos_summary = df_pos_clean.groupby('Vị trí quảng cáo').agg({
    'Số tiền đã chi tiêu (VND)': 'sum',
    'Lượt bắt đầu cuộc trò chuyện qua tin nhắn': 'sum',
    'Lượt mua': 'sum'
}).reset_index()

pos_summary.rename(columns={
    'Số tiền đã chi tiêu (VND)': 'spend',
    'Lượt bắt đầu cuộc trò chuyện qua tin nhắn': 'msg',
    'Lượt mua': 'pur'
}, inplace=True)

pos_summary['cpp'] = np.where(pos_summary['pur'] > 0, pos_summary['spend'] / pos_summary['pur'], np.nan)
pos_summary['cpm'] = np.where(pos_summary['msg'] > 0, pos_summary['spend'] / pos_summary['msg'], np.nan)
pos_summary['conv'] = np.where(pos_summary['msg'] > 0, (pos_summary['pur'] / pos_summary['msg']) * 100, np.nan)
pos_summary['spend_pct'] = (pos_summary['spend'] / pos_summary['spend'].sum()) * 100
pos_summary['pur_pct'] = (pos_summary['pur'] / pos_summary['pur'].sum()) * 100
pos_summary = pos_summary.sort_values(by='spend', ascending=False)

pos_summary_list = []
for idx, r in pos_summary.iterrows():
    pos_summary_list.append({
        'name': r['Vị trí quảng cáo'],
        'spend': round(r['spend']),
        'spend_pct': round(r['spend_pct'], 1),
        'msg': round(r['msg']),
        'pur': round(r['pur']),
        'pur_pct': round(r['pur_pct'], 1),
        'cpm': round(r['cpm']) if (pd.notna(r['cpm']) and not np.isinf(r['cpm'])) else 0,
        'cpp': round(r['cpp']) if (pd.notna(r['cpp']) and not np.isinf(r['cpp'])) else 0,
        'conv': round(r['conv'], 1) if (pd.notna(r['conv']) and not np.isinf(r['conv'])) else 0
    })

# 8. BUILD EXCEL WORKBOOK (6 SHEETS)
wb = openpyxl.Workbook()

header_font = Font(name='Arial', size=11, bold=True, color='FFFFFF')
section_font = Font(name='Arial', size=11, bold=True, color='FFFFFF')
title_font = Font(name='Arial', size=14, bold=True, color='1E3A8A')
sub_title_font = Font(name='Arial', size=10, italic=True, color='4B5563')
bold_font = Font(name='Arial', size=10, bold=True)
regular_font = Font(name='Arial', size=10)
highlight_san_font = Font(name='Arial', size=10, bold=True, color='1E40AF')
highlight_ocu_font = Font(name='Arial', size=10, bold=True, color='065F46')

navy_fill = PatternFill(start_color='1E3A8A', end_color='1E3A8A', fill_type='solid')
teal_fill = PatternFill(start_color='0F766E', end_color='0F766E', fill_type='solid')
blue_light_fill = PatternFill(start_color='EFF6FF', end_color='EFF6FF', fill_type='solid')
emerald_light_fill = PatternFill(start_color='ECFDF5', end_color='ECFDF5', fill_type='solid')
gray_light_fill = PatternFill(start_color='F9FAFB', end_color='F9FAFB', fill_type='solid')

thin_border = Border(
    left=Side(style='thin', color='E5E7EB'), right=Side(style='thin', color='E5E7EB'),
    top=Side(style='thin', color='E5E7EB'), bottom=Side(style='thin', color='E5E7EB')
)
double_bottom_border = Border(
    left=Side(style='thin', color='E5E7EB'), right=Side(style='thin', color='E5E7EB'),
    top=Side(style='thin', color='E5E7EB'), bottom=Side(style='double', color='1F2937')
)

# Sheet 1: Danh sách sắp xếp Full
ws1 = wb.active
ws1.title = '1_Danh_Sach_Sap_Xep_Full'
ws1.views.sheetView[0].showGridLines = True
ws1['A1'] = 'BÁO CÁO TOÀN DIỆN CHI PHÍ & KẾT QUẢ QUẢNG CÁO FACEBOOK'
ws1['A1'].font = title_font
ws1['A2'] = 'Sắp xếp ưu tiên: Chi phí/Lượt mua (Tăng dần) -> Chi phí/Tin nhắn (Tăng dần). Đã chuẩn hóa tiền tệ và loại bỏ số lẻ.'
ws1['A2'].font = sub_title_font

headers1 = [
    'STT', 'Mã Quảng Cáo (Ad ID)', 'Số Tiền Đã Chi Tiêu (VND)', 'Số Tin Nhắn', 'Chi Phí / Tin Nhắn (VND)',
    'Số Lượt Mua', 'Chi Phí / Lượt Mua (VND)', 'Tỷ Lệ Chốt L2/L1', 'Đánh Giá Độ Ổn Định',
    'Khuyến Nghị Ngân Sách', 'Vị Trí Phù Hợp Nhất', 'Số Đơn Tại Vị Trí Đó', 'Chi Phí / Đơn Tại Vị Trí Đó'
]
for col_idx, h in enumerate(headers1, start=1):
    cell = ws1.cell(row=4, column=col_idx, value=h)
    cell.font = header_font; cell.fill = PatternFill(start_color='1F4E79', end_color='1F4E79', fill_type='solid')
    cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)

for row_idx, r in df_final_sorted.iterrows():
    curr = row_idx + 5
    ws1.cell(row=curr, column=1, value=row_idx+1).alignment = Alignment(horizontal='center')
    ws1.cell(row=curr, column=2, value=str(r['ad_id'])).alignment = Alignment(horizontal='center')
    
    c_sp = ws1.cell(row=curr, column=3, value=round(r['spend']) if pd.notna(r['spend']) else 0); c_sp.number_format = '#,##0 "đ"'
    c_m = ws1.cell(row=curr, column=4, value=round(r['msg']) if pd.notna(r['msg']) else 0); c_m.number_format = '#,##0'
    c_cpm = ws1.cell(row=curr, column=5, value=round(r['cpm']) if pd.notna(r['cpm']) else None); c_cpm.number_format = '#,##0 "đ"'
    c_p = ws1.cell(row=curr, column=6, value=round(r['pur']) if pd.notna(r['pur']) else 0); c_p.number_format = '#,##0'
    c_cpp = ws1.cell(row=curr, column=7, value=round(r['cpp']) if pd.notna(r['cpp']) else None); c_cpp.number_format = '#,##0 "đ"'
    c_l2 = ws1.cell(row=curr, column=8, value=r['l2_l1'] if pd.notna(r['l2_l1']) else None); c_l2.number_format = '0%'
    
    ws1.cell(row=curr, column=9, value=r['stability']).alignment = Alignment(horizontal='center')
    ws1.cell(row=curr, column=10, value=r['recommendation']).alignment = Alignment(horizontal='left')
    ws1.cell(row=curr, column=11, value=r['best_pos']).alignment = Alignment(horizontal='left')
    c_ppur = ws1.cell(row=curr, column=12, value=round(r['pos_pur']) if pd.notna(r['pos_pur']) else 0); c_ppur.number_format = '#,##0'
    c_pcpp = ws1.cell(row=curr, column=13, value=round(r['pos_cpp']) if pd.notna(r['pos_cpp']) else None); c_pcpp.number_format = '#,##0 "đ"'
    
    for c in range(1, 14):
        ws1.cell(row=curr, column=c).border = thin_border; ws1.cell(row=curr, column=c).font = regular_font

# Sheet 2: Báo cáo ổn định theo ngày
ws2 = wb.create_sheet('2_Bao_Cao_On_Dinh_Theo_Ngay')
ws2.views.sheetView[0].showGridLines = True
ws2['A1'] = 'BÁO CÁO ĐỘ ỔN ĐỊNH CHI PHÍ VÀ KẾT QUẢ THEO TỪNG NGÀY'
ws2['A1'].font = title_font
ws2['A2'] = 'Phân tích chi tiết hệ số biến thiên (CV) và tỷ lệ ngày phát sinh đơn hàng để nhận định độ ổn định'
ws2['A2'].font = sub_title_font

headers2 = [
    'Mã Quảng Cáo (Ad ID)', 'Số Ngày Chạy', 'Số Ngày Có Tin', 'Số Ngày Có Đơn', 'Tỷ Lệ Ngày Ra Đơn',
    'CV Chi Phí/Tin (%)', 'CV Chi Phí/Đơn (%)', 'Đánh Giá Tính Ổn Định', 'Khuyến Nghị Hành Động'
]
for col_idx, h in enumerate(headers2, start=1):
    cell = ws2.cell(row=4, column=col_idx, value=h)
    cell.font = header_font; cell.fill = PatternFill(start_color='2E75B6', end_color='2E75B6', fill_type='solid')
    cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)

for row_idx, r in df_final_sorted.iterrows():
    curr = row_idx + 5
    ws2.cell(row=curr, column=1, value=str(r['ad_id'])).alignment = Alignment(horizontal='center')
    ws2.cell(row=curr, column=2, value=r['active_days']).alignment = Alignment(horizontal='center')
    ws2.cell(row=curr, column=3, value=r['msg_days']).alignment = Alignment(horizontal='center')
    ws2.cell(row=curr, column=4, value=r['pur_days']).alignment = Alignment(horizontal='center')
    c_rat = ws2.cell(row=curr, column=5, value=r['pur_ratio']); c_rat.number_format = '0%'
    c_cpm_cv = ws2.cell(row=curr, column=6, value=r['cpm_cv'] if pd.notna(r['cpm_cv']) else None); c_cpm_cv.number_format = '0%'
    c_cpp_cv = ws2.cell(row=curr, column=7, value=r['cpp_cv'] if pd.notna(r['cpp_cv']) else None); c_cpp_cv.number_format = '0%'
    ws2.cell(row=curr, column=8, value=r['stability']).alignment = Alignment(horizontal='center')
    ws2.cell(row=curr, column=9, value=r['recommendation']).alignment = Alignment(horizontal='left')
    for c in range(1, 10):
        ws2.cell(row=curr, column=c).border = thin_border; ws2.cell(row=curr, column=c).font = regular_font

# Sheet 3: Vị trí quảng cáo
ws3 = wb.create_sheet('3_Vi_Tri_Quang_Cao')
ws3.views.sheetView[0].showGridLines = True
ws3['A1'] = 'TỔNG HỢP HIỆU QUẢ VÀ ĐỘ ỔN ĐỊNH THEO TỪNG VỊ TRÍ QUẢNG CÁO'
ws3['A1'].font = title_font

headers3 = [
    'Vị Trí Quảng Cáo', 'Chi Tiêu (VND)', 'Tỷ Trọng Chi Tiêu (%)', 'Số Tin Nhắn', 'Chi Phí / Tin (VND)',
    'Số Lượt Mua', 'Tỷ Trọng Đơn Hàng (%)', 'Chi Phí / Lượt Mua (VND)', 'Tỷ Lệ Chốt L2/L1 (%)'
]
for col_idx, h in enumerate(headers3, start=1):
    cell = ws3.cell(row=3, column=col_idx, value=h)
    cell.font = header_font; cell.fill = PatternFill(start_color='385723', end_color='385723', fill_type='solid')
    cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)

for row_idx, r in pos_summary.iterrows():
    curr = row_idx + 4
    ws3.cell(row=curr, column=1, value=str(r['Vị trí quảng cáo'])).alignment = Alignment(horizontal='left')
    c_sp = ws3.cell(row=curr, column=2, value=round(r['spend'])); c_sp.number_format = '#,##0 "đ"'
    c_sppct = ws3.cell(row=curr, column=3, value=r['spend_pct'] / 100); c_sppct.number_format = '0.0%'
    c_m = ws3.cell(row=curr, column=4, value=round(r['msg'])); c_m.number_format = '#,##0'
    c_cpm = ws3.cell(row=curr, column=5, value=round(r['cpm']) if pd.notna(r['cpm']) else None); c_cpm.number_format = '#,##0 "đ"'
    c_p = ws3.cell(row=curr, column=6, value=round(r['pur'])); c_p.number_format = '#,##0'
    c_ppct = ws3.cell(row=curr, column=7, value=r['pur_pct'] / 100); c_ppct.number_format = '0.0%'
    c_cpp = ws3.cell(row=curr, column=8, value=round(r['cpp']) if pd.notna(r['cpp']) else None); c_cpp.number_format = '#,##0 "đ"'
    c_conv = ws3.cell(row=curr, column=9, value=r['conv'] / 100 if pd.notna(r['conv']) else None); c_conv.number_format = '0.0%'
    for c in range(1, 10):
        ws3.cell(row=curr, column=c).border = thin_border; ws3.cell(row=curr, column=c).font = regular_font

# Sheet 4: Đề xuất ngân sách
ws4 = wb.create_sheet('4_De_Xuat_Ngan_Sach')
ws4.views.sheetView[0].showGridLines = True
ws4['A1'] = 'BẢNG PHÂN BỔ VÀ ĐỀ XUẤT ĐIỀU CHỈNH NGÂN SÁCH CHI TIẾT'
ws4['A1'].font = title_font

headers4 = ['Nhóm Hành Động', 'Mã Quảng Cáo (Ad ID)', 'Chi Tiêu (VND)', 'Đơn Hàng', 'Chi Phí / Đơn (VND)', 'Chốt L2/L1', 'Vị Trí Tối Ưu', 'Kế Hoạch Cụ Thể']
for col_idx, h in enumerate(headers4, start=1):
    cell = ws4.cell(row=3, column=col_idx, value=h)
    cell.font = header_font; cell.fill = PatternFill(start_color='C65911', end_color='C65911', fill_type='solid')

plan_rows = [
    ('🚀 TĂNG MẠNH NGÂN SÁCH (Ưu tiên 1)', '120249153794660532', 7942652, 130, 61097, 0.33, 'Reels / Bảng tin', 'Tăng ngân sách +30% to +50% ngay lập tức. Giữ nguyên creative.'),
    ('🚀 TĂNG MẠNH NGÂN SÁCH (Ưu tiên 1)', '120249153839930532', 6295332, 98, 64238, 0.42, 'Facebook Reels', 'Tăng ngân sách +40%. Khóa vị trí Facebook Reels.'),
    ('🚀 TĂNG MẠNH NGÂN SÁCH (Ưu tiên 1)', '52550106995296', 2805684, 43, 65248, 0.36, 'Facebook Reels', 'Tăng ngân sách +30%. Khóa chặt Reels.'),
    ('🚀 TĂNG MẠNH NGÂN SÁCH (Ưu tiên 1)', '120249153813990532', 3932804, 53, 74204, 0.37, 'Facebook Reels', 'Tăng ngân sách +25%. Theo dõi CPA ngưỡng 80k.'),
    ('📈 TĂNG NGÂN SÁCH / DUY TRÌ (Ưu tiên 2)', '120248174416610532', 5825124, 41, 142076, 0.35, 'Bảng tin Facebook', 'Cột trụ Bảng tin. Duy trì hoặc tăng nhẹ 10-15%.'),
    ('📈 TĂNG NGÂN SÁCH / DUY TRÌ (Ưu tiên 2)', '52642653160220', 8376760, 55, 152305, 0.50, 'Facebook Reels', 'Scale nhẹ 15%. Chốt đơn cực tốt 50%.'),
    ('📈 TĂNG NGÂN SÁCH / DUY TRÌ (Ưu tiên 2)', '120252740442820268', 3672755, 36, 102021, 0.25, 'Facebook Reels', 'Scale tăng ngân sách 20%. Giữ chặt Reels.'),
    ('❌ TẮT NGAY (73 Ads 0 Đơn)', '73 Ads không phát sinh đơn', 25039622, 0, 0, 0.0, 'Đa dạng vị trí', 'Tắt ngay 73 ads này để thu hồi 25.039.622 đ tái đầu tư vào Top 7 Ads trên.')
]
for r_idx, r in enumerate(plan_rows, start=4):
    ws4.cell(row=r_idx, column=1, value=r[0]).font = bold_font
    ws4.cell(row=r_idx, column=2, value=str(r[1])).alignment = Alignment(horizontal='center')
    c_sp = ws4.cell(row=r_idx, column=3, value=r[2]); c_sp.number_format = '#,##0 "đ"'
    c_p = ws4.cell(row=r_idx, column=4, value=r[3]); c_p.number_format = '#,##0'
    c_cpp = ws4.cell(row=r_idx, column=5, value=r[4] if r[4] > 0 else None); c_cpp.number_format = '#,##0 "đ"'
    c_l2 = ws4.cell(row=r_idx, column=6, value=r[5]); c_l2.number_format = '0%'
    ws4.cell(row=r_idx, column=7, value=r[6]).alignment = Alignment(horizontal='center')
    ws4.cell(row=r_idx, column=8, value=r[7]).alignment = Alignment(horizontal='left')
    for c in range(1, 9):
        ws4.cell(row=r_idx, column=c).border = thin_border; ws4.cell(row=r_idx, column=c).font = regular_font

# Sheet 5: Độ Ổn Định Vị Trí / Mã Quảng Cáo (Ad ID x Placement Stability)
ws5 = wb.create_sheet('5_On_Dinh_Vi_Tri_Theo_Ad')
ws5.views.sheetView[0].showGridLines = True
ws5['A1'] = 'BÁO CÁO ĐỘ ỔN ĐỊNH CỦA TỪNG VỊ TRÍ QUẢNG CÁO THEO TỪNG MÃ QUẢNG CÁO'
ws5['A1'].font = title_font
ws5['A2'] = 'Đánh giá tính ổn định chi tiết cho từng cặp (Mã Quảng Cáo x Vị Trí Hiển Thị) dựa trên dữ liệu hàng ngày'
ws5['A2'].font = sub_title_font

headers5 = [
    'STT', 'Mã Quảng Cáo (Ad ID)', 'Vị Trí Quảng Cáo', 'Chi Tiêu (VND)', 'Số Tin Nhắn', 'Chi Phí / Tin (VND)',
    'Số Lượt Mua', 'Chi Phí / Lượt Mua (VND)', 'Tỷ Lệ Chốt L2/L1', 'Số Ngày Chạy', 'Số Ngày Ra Đơn',
    '% Ngày Ra Đơn', 'CV Tin Nhắn (%)', 'CV Lượt Mua (%)', 'Đánh Giá Tính Ổn Định', 'Khuyến Nghị Cụ Thể'
]
for col_idx, h in enumerate(headers5, start=1):
    cell = ws5.cell(row=4, column=col_idx, value=h)
    cell.font = header_font; cell.fill = PatternFill(start_color='7030A0', end_color='7030A0', fill_type='solid')
    cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)

for row_idx, r in df_ad_pos_filtered.reset_index(drop=True).iterrows():
    curr = row_idx + 5
    ws5.cell(row=curr, column=1, value=row_idx+1).alignment = Alignment(horizontal='center')
    ws5.cell(row=curr, column=2, value=str(r['ad_id'])).alignment = Alignment(horizontal='center')
    ws5.cell(row=curr, column=3, value=str(r['pos'])).alignment = Alignment(horizontal='left')
    
    c_sp = ws5.cell(row=curr, column=4, value=r['spend']); c_sp.number_format = '#,##0 "đ"'
    c_m = ws5.cell(row=curr, column=5, value=r['msg']); c_m.number_format = '#,##0'
    c_cpm = ws5.cell(row=curr, column=6, value=r['cpm'] if r['cpm'] else None); c_cpm.number_format = '#,##0 "đ"'
    c_p = ws5.cell(row=curr, column=7, value=r['pur']); c_p.number_format = '#,##0'
    c_cpp = ws5.cell(row=curr, column=8, value=r['cpp'] if r['cpp'] else None); c_cpp.number_format = '#,##0 "đ"'
    c_l2 = ws5.cell(row=curr, column=9, value=(r['conv'] / 100) if r['conv'] is not None else None); c_l2.number_format = '0%'
    
    ws5.cell(row=curr, column=10, value=r['active_days']).alignment = Alignment(horizontal='center')
    ws5.cell(row=curr, column=11, value=r['pur_days']).alignment = Alignment(horizontal='center')
    c_rat = ws5.cell(row=curr, column=12, value=r['pur_ratio'] / 100); c_rat.number_format = '0%'
    c_cpm_cv = ws5.cell(row=curr, column=13, value=(r['cpm_cv'] / 100) if r['cpm_cv'] is not None else None); c_cpm_cv.number_format = '0%'
    c_cpp_cv = ws5.cell(row=curr, column=14, value=(r['cpp_cv'] / 100) if r['cpp_cv'] is not None else None); c_cpp_cv.number_format = '0%'
    
    ws5.cell(row=curr, column=15, value=r['stability']).alignment = Alignment(horizontal='center')
    ws5.cell(row=curr, column=16, value=r['recommendation']).alignment = Alignment(horizontal='left')
    for c in range(1, 17):
        ws5.cell(row=curr, column=c).border = thin_border; ws5.cell(row=curr, column=c).font = regular_font

# Sheet 6: Báo Cáo 2 Từ Khóa: "Sản" (15 Ads) và "Ở Cữ" (8 Ads) Dựa Trên Ghi Chú Điền Tay Của Bạn
ws6 = wb.create_sheet('6_Bao_Cao_Tu_Khoa_San_O_Cu')
ws6.views.sheetView[0].showGridLines = True

ws6.merge_cells('A1:J1')
ws6.cell(row=1, column=1, value='BÁO CÁO ĐỐI ĐẦU 2 TỪ KHÓA: "SẢN" VÀ "Ở CỮ" (DỰA TRÊN GHI CHÚ ĐIỀN TAY THỰC TẾ)').font = title_font
ws6.cell(row=1, column=1).alignment = Alignment(horizontal='center', vertical='center')
ws6.row_dimensions[1].height = 28

ws6.merge_cells('A2:J2')
ws6.cell(row=2, column=1, value='Chỉ lọc trên 23 Ad ID được bạn điền tay ghi chú trên Dashboard (15 Ads Sản vs 8 Ads Ở cữ) - 138 Ads còn lại chưa ghi chú').font = sub_title_font
ws6.cell(row=2, column=1).alignment = Alignment(horizontal='center', vertical='center')
ws6.row_dimensions[2].height = 18

curr_row = 4

# SEC 1: Head-to-Head Table
ws6.merge_cells(f'A{curr_row}:E{curr_row}')
sec1 = ws6.cell(row=curr_row, column=1, value='I. TỔNG HỢP SO SÁNH TRỰC TIẾP GIỮA 2 TỪ KHÓA ĐÃ GHI CHÚ (HEAD-TO-HEAD)')
sec1.font = section_font; sec1.fill = navy_fill; sec1.alignment = Alignment(vertical='center', indent=1)
ws6.row_dimensions[curr_row].height = 24
curr_row += 1

h1_cols = ['Chỉ tiêu KPI Cốt Lõi', 'Từ khóa "Sản" (15 Ads)', 'Từ khóa "Ở cữ" (8 Ads)', 'Tổng 23 Ads Đã Ghi Chú', 'Nhận Định & Đánh Giá Thực Tế']
for c_idx, val in enumerate(h1_cols, 1):
    cell = ws6.cell(row=curr_row, column=c_idx, value=val)
    cell.font = header_font; cell.fill = teal_fill; cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
    cell.border = thin_border
ws6.row_dimensions[curr_row].height = 24
curr_row += 1

t1_data = [
    ('Số lượng ID Ads đã điền ghi chú', 15, 8, 23, '#,##0', '15 Ads được ghi chú "Sản", 8 Ads được ghi chú "Ở cữ"'),
    ('Tổng ngân sách đã chi tiêu', 96365112, 40167154, 136532266, '#,##0 "đ"', '"Sản" chi 96.3 triệu (70.6%), "Ở cữ" chi 40.1 triệu (29.4%)'),
    ('Tổng số lượt mua (Đơn L2)', 547, 416, 963, '#,##0', '"Sản" đạt 547 đơn, "Ở cữ" đạt 416 đơn'),
    ('Chi phí trung bình / Đơn (CPA/CPP)', 176170, 96556, 141778, '#,##0 "đ"', '"Ở cữ" có CPA siêu rẻ chỉ 96.556 đ/đơn (-45% so với Sản)'),
    ('Tổng cuộc trò chuyện (Tin nhắn L1)', 1163, 1243, 2406, '#,##0', '"Ở cữ" hút nhiều tin nhắn hơn dù ngân sách thấp hơn'),
    ('Chi phí trung bình / Tin nhắn (CPM)', 82859, 32315, 56747, '#,##0 "đ"', 'Giá tin "Ở cữ" cực rẻ (32.315 đ) so với "Sản" (82.859 đ)'),
    ('Tỷ lệ chốt đơn (L2 / L1)', 0.4703, 0.3347, 0.4002, '0%', '"Sản" có tỷ lệ chốt rất cao (47%), "Ở cữ" đạt 33.5%'),
    ('Bài hiệu quả nhất nhóm', '120249153813990532 (CPA 74k)', '120249153794660532 (CPA 61k)', '-', '@', '"Ở cữ" có bài ID 120249153794660532 chốt 130 đơn CPA 61k')
]

for item in t1_data:
    lbl, val_san, val_ocu, val_tot, num_fmt, note = item
    c1 = ws6.cell(row=curr_row, column=1, value=lbl); c1.font = bold_font; c1.border = thin_border
    c2 = ws6.cell(row=curr_row, column=2, value=val_san); c2.font = highlight_san_font; c2.number_format = num_fmt if isinstance(val_san, (int, float)) else '@'; c2.alignment = Alignment(horizontal='right' if isinstance(val_san, (int, float)) else 'left'); c2.border = thin_border; c2.fill = blue_light_fill
    c3 = ws6.cell(row=curr_row, column=3, value=val_ocu); c3.font = highlight_ocu_font; c3.number_format = num_fmt if isinstance(val_ocu, (int, float)) else '@'; c3.alignment = Alignment(horizontal='right' if isinstance(val_ocu, (int, float)) else 'left'); c3.border = thin_border; c3.fill = emerald_light_fill
    c4 = ws6.cell(row=curr_row, column=4, value=val_tot); c4.font = bold_font; c4.number_format = num_fmt if isinstance(val_tot, (int, float)) else '@'; c4.alignment = Alignment(horizontal='right' if isinstance(val_tot, (int, float)) else 'center'); c4.border = thin_border
    c5 = ws6.cell(row=curr_row, column=5, value=note); c5.font = regular_font; c5.alignment = Alignment(horizontal='left'); c5.border = thin_border
    ws6.row_dimensions[curr_row].height = 20
    curr_row += 1

curr_row += 2

# SEC 2: Detail Table for 15 Ads "Sản"
ws6.merge_cells(f'A{curr_row}:H{curr_row}')
sec2 = ws6.cell(row=curr_row, column=1, value='II. CHI TIẾT 15 MÃ QUẢNG CÁO GHI CHÚ "SẢN" (XẾP THEO LƯỢT MUA GIẢM DẦN)')
sec2.font = section_font; sec2.fill = navy_fill; sec2.alignment = Alignment(vertical='center', indent=1)
ws6.row_dimensions[curr_row].height = 24
curr_row += 1

h2_cols = ['STT', 'Mã Quảng Cáo (Ad ID)', 'Chi Tiêu (VNĐ)', 'Tin Nhắn', 'Giá/Tin (VNĐ)', 'Lượt Mua', 'CPA/Đơn (VNĐ)', 'Ghi Chú Thực Tế Điền Tay']
for c_idx, val in enumerate(h2_cols, 1):
    cell = ws6.cell(row=curr_row, column=c_idx, value=val)
    cell.font = header_font; cell.fill = teal_fill; cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
    cell.border = thin_border
ws6.row_dimensions[curr_row].height = 24
curr_row += 1

san_ads_list = df_final_sorted[df_final_sorted['keyword'] == 'san'].sort_values('pur', ascending=False)
for s_idx, (_, r) in enumerate(san_ads_list.iterrows(), 1):
    ws6.cell(row=curr_row, column=1, value=s_idx).alignment = Alignment(horizontal='center')
    ws6.cell(row=curr_row, column=2, value=str(r['ad_id'])).font = bold_font
    ws6.cell(row=curr_row, column=3, value=r['spend']).number_format = '#,##0 "đ"'
    ws6.cell(row=curr_row, column=4, value=r['msg']).number_format = '#,##0'
    ws6.cell(row=curr_row, column=5, value=r['cpm']).number_format = '#,##0 "đ"'
    c_pur = ws6.cell(row=curr_row, column=6, value=r['pur']); c_pur.number_format = '#,##0'; c_pur.font = bold_font
    c_cpp = ws6.cell(row=curr_row, column=7, value=r['cpp']); c_cpp.number_format = '#,##0 "đ"'; c_cpp.font = bold_font
    ws6.cell(row=curr_row, column=8, value=r['note']).font = regular_font
    for c in range(1, 9):
        ws6.cell(row=curr_row, column=c).border = thin_border
    ws6.row_dimensions[curr_row].height = 19
    curr_row += 1

curr_row += 2

# SEC 3: Detail Table for 8 Ads "Ở cữ"
ws6.merge_cells(f'A{curr_row}:H{curr_row}')
sec3 = ws6.cell(row=curr_row, column=1, value='III. CHI TIẾT 8 MÃ QUẢNG CÁO GHI CHÚ "Ở CỮ" (XẾP THEO LƯỢT MUA GIẢM DẦN)')
sec3.font = section_font; sec3.fill = navy_fill; sec3.alignment = Alignment(vertical='center', indent=1)
ws6.row_dimensions[curr_row].height = 24
curr_row += 1

for c_idx, val in enumerate(h2_cols, 1):
    cell = ws6.cell(row=curr_row, column=c_idx, value=val)
    cell.font = header_font; cell.fill = teal_fill; cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
    cell.border = thin_border
ws6.row_dimensions[curr_row].height = 24
curr_row += 1

ocu_ads_list = df_final_sorted[df_final_sorted['keyword'] == 'ocu'].sort_values('pur', ascending=False)
for o_idx, (_, r) in enumerate(ocu_ads_list.iterrows(), 1):
    ws6.cell(row=curr_row, column=1, value=o_idx).alignment = Alignment(horizontal='center')
    ws6.cell(row=curr_row, column=2, value=str(r['ad_id'])).font = bold_font
    ws6.cell(row=curr_row, column=3, value=r['spend']).number_format = '#,##0 "đ"'
    ws6.cell(row=curr_row, column=4, value=r['msg']).number_format = '#,##0'
    ws6.cell(row=curr_row, column=5, value=r['cpm']).number_format = '#,##0 "đ"'
    c_pur = ws6.cell(row=curr_row, column=6, value=r['pur']); c_pur.number_format = '#,##0'; c_pur.font = bold_font
    c_cpp = ws6.cell(row=curr_row, column=7, value=r['cpp']); c_cpp.number_format = '#,##0 "đ"'; c_cpp.font = bold_font
    ws6.cell(row=curr_row, column=8, value=r['note']).font = regular_font
    for c in range(1, 9):
        ws6.cell(row=curr_row, column=c).border = thin_border
    ws6.row_dimensions[curr_row].height = 19
    curr_row += 1

curr_row += 2

# SEC 4: Insights & Recommendations
ws6.merge_cells(f'A{curr_row}:H{curr_row}')
sec4 = ws6.cell(row=curr_row, column=1, value='IV. NHẬN ĐỊNH VÀ ĐỀ XUẤT TỐI ƯU DỰA TRÊN 23 BÀI ĐÃ GHI CHÚ')
sec4.font = section_font; sec4.fill = navy_fill; sec4.alignment = Alignment(vertical='center', indent=1)
ws6.row_dimensions[curr_row].height = 24
curr_row += 1

insights = [
    ('1. Hiệu Quả Nhóm "Ở Cữ" Vượt Trội Về Chi Phí:', 'Nhóm "Ở cữ" có CPA trung bình chỉ 96.556 đ/đơn, rẻ hơn 45% so với nhóm "Sản" (176.170 đ/đơn), đồng thời giá tin nhắn cực kỳ rẻ (32.315 đ so với 82.859 đ). Đặc biệt ID 120249153794660532 mang lại 130 đơn với CPA chỉ 61.097 đ.'),
    ('2. Nhóm "Sản" Có Tỷ Lệ Chốt Khách Cao:', 'Nhóm "Sản" có tỷ lệ chuyển đổi chốt đơn vượt trội (47.0% so với 33.5% của Ở cữ). Dù giá tin nhắn cao hơn, mẹ bầu quan tâm gói sinh có quyết định mua hàng dứt khoát.'),
    ('3. Đề Xuất Tăng Ngân Sách:', 'Tập trung scale mạnh cho các bài "Ở cữ" có CPA dưới 70k (120249153794660532, 120249153839930532, 52550106995296) và duy trì các bài "Sản" có tỷ lệ chốt trên 50%.')
]

for title, desc in insights:
    ws6.merge_cells(f'A{curr_row}:B{curr_row}')
    ws6.cell(row=curr_row, column=1, value=title).font = bold_font
    ws6.merge_cells(f'C{curr_row}:H{curr_row}')
    ws6.cell(row=curr_row, column=3, value=desc).font = regular_font
    ws6.cell(row=curr_row, column=3).alignment = Alignment(wrap_text=True)
    ws6.row_dimensions[curr_row].height = 26
    curr_row += 1

# Adjust column widths
for ws in [ws1, ws2, ws3, ws4, ws5, ws6]:
    for col in ws.columns:
        max_len = 0
        col_letter = get_column_letter(col[0].column)
        for cell in col:
            if cell.row in [1, 2, 4]: continue
            v = str(cell.value or '')
            if '\n' in v: v = v.split('\n')[0]
            if len(v) > max_len and len(v) < 60: max_len = len(v)
        ws.column_dimensions[col_letter].width = max(max_len + 3, 14)

ws6.column_dimensions['A'].width = 24
ws6.column_dimensions['B'].width = 28
ws6.column_dimensions['D'].width = 34
ws6.column_dimensions['E'].width = 36

# Save Excel Workbooks safely
excel_out = 'Bao_cao_quang_cao_Facebook_Cap_Nhat.xlsx'
wb.save(excel_out)
print(f'Excel file saved successfully to {excel_out}!')

try:
    wb.save('Bao_cao_quang_cao_Facebook.xlsx')
    print('Also updated Bao_cao_quang_cao_Facebook.xlsx!')
except Exception as e:
    print('Bao_cao_quang_cao_Facebook.xlsx is currently open in Excel, kept Bao_cao_quang_cao_Facebook_Cap_Nhat.xlsx!')

# 9. Export JSON data for Dashboard
ad_pos_json_str = json.dumps(df_ad_pos_filtered.to_dict('records'), ensure_ascii=False)
ads_json_str = json.dumps(ads_data, ensure_ascii=False)
pos_json_str = json.dumps(pos_summary_list, ensure_ascii=False)

with open('ad_pos_data.json', 'w', encoding='utf-8') as f:
    f.write(ad_pos_json_str)

print('All data prep completed successfully with 6 sheets and keyword tagging!')
