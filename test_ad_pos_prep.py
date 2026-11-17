import json
import pandas as pd
import numpy as np

excel_path = 'sheet_data.xlsx'

# 1. Load Data
df_full = pd.read_excel(excel_path, sheet_name='Full', skiprows=2, dtype={'Mã quảng cáo': str}).dropna(subset=['Mã quảng cáo']).copy()
df_full['ad_id'] = df_full['Mã quảng cáo'].astype(str).str.strip()

num_cols = ['Lượt bắt đầu cuộc trò chuyện qua tin nhắn', 'Chi phí trên mỗi lượt bắt đầu cuộc trò chuyện qua tin nhắn', 
            'Bình luận về bài viết', 'Lượt mua', 'Chi phí trên mỗi lượt mua', 'Số tiền đã chi tiêu (VND)']
for c in num_cols:
    df_full[c] = pd.to_numeric(df_full[c], errors='coerce')

df_ngay = pd.read_excel(excel_path, sheet_name='Theo Ngày', skiprows=2, dtype={'Mã quảng cáo': str})
df_ngay['ad_id'] = df_ngay['Mã quảng cáo'].ffill().astype(str).str.strip()
df_daily = df_ngay[df_ngay['Ngày'].astype(str).str.strip().str.lower() != 'all'].copy()
for c in num_cols:
    df_daily[c] = pd.to_numeric(df_daily[c], errors='coerce')

df_pos = pd.read_excel(excel_path, sheet_name='Vị trí quảng cáo', skiprows=2, dtype={'Mã quảng cáo': str})
df_pos['ad_id'] = df_pos['Mã quảng cáo'].ffill().astype(str).str.strip()
df_pos['Ngày'] = df_pos['Ngày'].ffill()
for c in num_cols:
    df_pos[c] = pd.to_numeric(df_pos[c], errors='coerce')

df_pos_clean = df_pos[df_pos['Vị trí quảng cáo'].notna() & (df_pos['Vị trí quảng cáo'].astype(str).str.strip().str.lower() != 'all')].copy()
df_pos_daily = df_pos_clean[df_pos_clean['Ngày'].astype(str).str.strip().str.lower() != 'all'].copy()

# Ad ID x Placement Detailed Stability Calculation
ad_pos_detailed = []
for (aid, pos), g in df_pos_daily.groupby(['ad_id', 'Vị trí quảng cáo']):
    tot_spend = g['Số tiền đã chi tiêu (VND)'].sum()
    tot_msg = g['Lượt bắt đầu cuộc trò chuyện qua tin nhắn'].sum()
    tot_pur = g['Lượt mua'].sum()
    
    active_days = len(g[g['Số tiền đã chi tiêu (VND)'] > 0])
    msg_days = len(g[g['Lượt bắt đầu cuộc trò chuyện qua tin nhắn'] > 0])
    pur_days = len(g[g['Lượt mua'] > 0])
    
    g_pur = g[g['Lượt mua'] > 0]
    g_msg = g[g['Lượt bắt đầu cuộc trò chuyện qua tin nhắn'] > 0]
    
    cpm_mean = g_msg['Chi phí trên mỗi lượt bắt đầu cuộc trò chuyện qua tin nhắn'].mean() if len(g_msg) > 0 else np.nan
    cpm_std = g_msg['Chi phí trên mỗi lượt bắt đầu cuộc trò chuyện qua tin nhắn'].std() if len(g_msg) > 1 else 0.0
    cpm_cv = (cpm_std / cpm_mean) if (cpm_mean and cpm_mean > 0) else np.nan
    
    cpp_mean = g_pur['Chi phí trên mỗi lượt mua'].mean() if len(g_pur) > 0 else np.nan
    cpp_std = g_pur['Chi phí trên mỗi lượt mua'].std() if len(g_pur) > 1 else 0.0
    cpp_cv = (cpp_std / cpp_mean) if (cpp_mean and cpp_mean > 0) else np.nan
    
    pur_ratio = pur_days / active_days if active_days > 0 else 0
    cpm = tot_spend / tot_msg if tot_msg > 0 else np.nan
    cpp = tot_spend / tot_pur if tot_pur > 0 else np.nan
    l2_l1 = (tot_pur / tot_msg * 100) if tot_msg > 0 else 0
    
    if tot_pur == 0:
        if tot_spend >= 100000:
            stab = 'Kém hiệu quả (0 đơn)'
            rec = 'Tắt vị trí này (Chống lãng phí)'
        else:
            stab = 'Chi phí nhỏ / 0 đơn'
            rec = 'Bỏ chọn vị trí phụ'
    elif active_days <= 2 and tot_pur <= 2:
        stab = 'Mẫu ít (1-2 ngày)'
        rec = 'Theo dõi thêm'
    elif pur_ratio >= 0.70 and (pd.isna(cpp_cv) or cpp_cv <= 0.65) and (cpp < 200000):
        stab = 'Rất ổn định'
        rec = 'Tăng ngân sách vị trí này'
    elif pur_ratio >= 0.50 and (cpp < 250000):
        stab = 'Ổn định'
        rec = 'Duy trì / Tăng nhẹ'
    else:
        stab = 'Không ổn định'
        if cpp > 300000 or tot_spend > 1000000:
            rec = 'Tắt vị trí này / Dồn tiền sang vị trí khác'
        else:
            rec = 'Cần tối ưu nội dung cho vị trí này'
            
    ad_pos_detailed.append({
        'ad_id': aid,
        'placement': pos,
        'spend': round(tot_spend),
        'msg': round(tot_msg),
        'pur': round(tot_pur),
        'cpm': round(cpm) if pd.notna(cpm) else 0,
        'cpp': round(cpp) if pd.notna(cpp) else 0,
        'l2_l1': round(l2_l1),
        'active_days': active_days,
        'pur_days': pur_days,
        'pur_ratio': round(pur_ratio * 100),
        'cpm_cv': round(cpm_cv * 100) if pd.notna(cpm_cv) else None,
        'cpp_cv': round(cpp_cv * 100) if pd.notna(cpp_cv) else None,
        'stability': stab,
        'recommendation': rec
    })

df_ad_pos_all = pd.DataFrame(ad_pos_detailed)
df_ad_pos_filtered = df_ad_pos_all[(df_ad_pos_all['spend'] >= 20000) | (df_ad_pos_all['pur'] > 0) | (df_ad_pos_all['msg'] > 0)].copy()
df_ad_pos_filtered = df_ad_pos_filtered.sort_values(by=['pur', 'cpp'], ascending=[False, True])
print('Total ad_pos pairs filtered for dashboard:', len(df_ad_pos_filtered))
