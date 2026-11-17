import pandas as pd
import numpy as np
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

excel_path = 'sheet_data.xlsx'

# 1. Read Full
df_full = pd.read_excel(excel_path, sheet_name='Full', skiprows=2, dtype={'Mã quảng cáo': str}).dropna(subset=['Mã quảng cáo']).copy()
df_full['ad_id'] = df_full['Mã quảng cáo'].astype(str).str.strip()

num_cols = ['Lượt bắt đầu cuộc trò chuyện qua tin nhắn', 'Chi phí trên mỗi lượt bắt đầu cuộc trò chuyện qua tin nhắn', 
            'Bình luận về bài viết', 'Lượt mua', 'Chi phí trên mỗi lượt mua', 'Số tiền đã chi tiêu (VND)']
for c in num_cols:
    df_full[c] = pd.to_numeric(df_full[c], errors='coerce')

# 2. Read Theo Ngay
df_ngay = pd.read_excel(excel_path, sheet_name='Theo Ngày', skiprows=2, dtype={'Mã quảng cáo': str})
df_ngay['ad_id'] = df_ngay['Mã quảng cáo'].ffill().astype(str).str.strip()
df_daily = df_ngay[df_ngay['Ngày'].astype(str).str.strip().str.lower() != 'all'].copy()
for c in num_cols:
    df_daily[c] = pd.to_numeric(df_daily[c], errors='coerce')

# 3. Read Vi tri
df_pos = pd.read_excel(excel_path, sheet_name='Vị trí quảng cáo', skiprows=2, dtype={'Mã quảng cáo': str})
df_pos['ad_id'] = df_pos['Mã quảng cáo'].ffill().astype(str).str.strip()
df_pos['Ngày'] = df_pos['Ngày'].ffill()
for c in num_cols:
    df_pos[c] = pd.to_numeric(df_pos[c], errors='coerce')
df_pos_clean = df_pos[df_pos['Vị trí quảng cáo'].notna() & (df_pos['Vị trí quảng cáo'].astype(str).str.strip().str.lower() != 'all')].copy()

# Daily stats
daily_stats = {}
for ad_id, g in df_daily.groupby('ad_id'):
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
    
    daily_stats[ad_id] = {
        'active_days': active_days,
        'msg_days': msg_days,
        'pur_days': pur_days,
        'pur_ratio': (pur_days / active_days) if active_days > 0 else 0,
        'cpm_mean': cpm_mean,
        'cpm_cv': cpm_cv,
        'cpp_mean': cpp_mean,
        'cpp_cv': cpp_cv
    }

# Placement stats per ad
pos_stats = {}
for ad_id, g in df_pos_clean.groupby('ad_id'):
    g_pos = g.groupby('Vị trí quảng cáo').agg(
        spend=('Số tiền đã chi tiêu (VND)', 'sum'),
        msg=('Lượt bắt đầu cuộc trò chuyện qua tin nhắn', 'sum'),
        pur=('Lượt mua', 'sum')
    ).reset_index()
    g_pos['cpm'] = g_pos['spend'] / g_pos['msg']
    g_pos['cpp'] = g_pos['spend'] / g_pos['pur']
    
    g_pos_pur = g_pos[g_pos['pur'] > 0]
    if len(g_pos_pur) > 0:
        best_row = g_pos_pur.sort_values(by=['pur', 'cpp'], ascending=[False, True]).iloc[0]
    else:
        g_pos_msg = g_pos[g_pos['msg'] > 0]
        if len(g_pos_msg) > 0:
            best_row = g_pos_msg.sort_values(by=['msg', 'cpm'], ascending=[False, True]).iloc[0]
        else:
            best_row = g_pos.sort_values(by='spend', ascending=False).iloc[0]
            
    pos_stats[ad_id] = {
        'best_pos': best_row['Vị trí quảng cáo'],
        'pos_spend': best_row['spend'],
        'pos_msg': best_row['msg'],
        'pos_pur': best_row['pur'],
        'pos_cpp': best_row['cpp'] if best_row['pur'] > 0 else np.nan,
        'pos_cpm': best_row['cpm'] if best_row['msg'] > 0 else np.nan
    }

# Combine and classify
records = []
for idx, row in df_full.iterrows():
    ad_id = row['ad_id']
    spend = row['Số tiền đã chi tiêu (VND)']
    msg = row['Lượt bắt đầu cuộc trò chuyện qua tin nhắn']
    pur = row['Lượt mua']
    cpm = row['Chi phí trên mỗi lượt bắt đầu cuộc trò chuyện qua tin nhắn']
    cpp = row['Chi phí trên mỗi lượt mua']
    cmt = row['Bình luận về bài viết']
    
    d = daily_stats.get(ad_id, {
        'active_days': 0, 'msg_days': 0, 'pur_days': 0, 'pur_ratio': 0,
        'cpm_mean': np.nan, 'cpm_cv': np.nan, 'cpp_mean': np.nan, 'cpp_cv': np.nan
    })
    
    p = pos_stats.get(ad_id, {
        'best_pos': 'Không rõ', 'pos_spend': 0, 'pos_msg': 0, 'pos_pur': 0, 'pos_cpp': np.nan, 'pos_cpm': np.nan
    })
    
    l2_l1 = (pur / msg) if (msg and msg > 0 and pur and pur > 0) else (0.0 if msg and msg > 0 else np.nan)
    
    # Classification logic
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
        if cpp < 100000:
            recommendation = 'Tăng mạnh ngân sách (Ưu tiên 1)'
        elif cpp < 180000:
            recommendation = 'Tăng ngân sách (Ưu tiên 2)'
        else:
            recommendation = 'Duy trì & Tối ưu giá thầu'
    elif pur_ratio >= 0.50 and (pd.isna(cpp_cv) or cpp_cv <= 0.85):
        stability = 'Ổn định'
        if cpp < 100000:
            recommendation = 'Tăng ngân sách (Ưu tiên 2)'
        elif cpp < 180000:
            recommendation = 'Tăng nhẹ / Duy trì'
        else:
            recommendation = 'Duy trì & Tối ưu nội dung'
    else:
        stability = 'Không ổn định'
        if cpp > 300000 or spend > 1500000:
            recommendation = 'Giảm ngân sách hoặc Tắt'
        else:
            recommendation = 'Tối ưu lại nội dung & Vị trí'
            
    records.append({
        'ad_id': ad_id,
        'spend': spend,
        'msg': msg,
        'cpm': cpm,
        'pur': pur,
        'cpp': cpp,
        'l2_l1': l2_l1,
        'cmt': cmt,
        'active_days': active_days,
        'msg_days': d['msg_days'],
        'pur_days': pur_days,
        'pur_ratio': pur_ratio,
        'cpm_mean': d['cpm_mean'],
        'cpm_cv': cpm_cv,
        'cpp_mean': d['cpp_mean'],
        'cpp_cv': cpp_cv,
        'stability': stability,
        'recommendation': recommendation,
        'best_pos': p['best_pos'],
        'pos_pur': p['pos_pur'],
        'pos_cpp': p['pos_cpp']
    })

df_all = pd.DataFrame(records)

# Sort rule:
# Priority 1: cpp asc (with purchases first)
# Priority 2: cpm asc
df_pur_sorted = df_all[df_all['pur'] > 0].sort_values(by=['cpp', 'cpm'], ascending=[True, True])
df_nopur_sorted = df_all[df_all['pur'].isna() | (df_all['pur'] == 0)].sort_values(by=['cpm', 'spend'], ascending=[True, False])
df_final_sorted = pd.concat([df_pur_sorted, df_nopur_sorted], ignore_index=True)

# Create Excel Workbook
wb = openpyxl.Workbook()
# Styles
header_font = Font(name='Segoe UI', size=11, bold=True, color='FFFFFF')
header_fill = PatternFill(start_color='1F4E78', end_color='1F4E78', fill_type='solid')
title_font = Font(name='Segoe UI', size=14, bold=True, color='1F4E78')
sub_title_font = Font(name='Segoe UI', size=10, italic=True, color='595959')
bold_font = Font(name='Segoe UI', size=10, bold=True)
regular_font = Font(name='Segoe UI', size=10)
thin_border = Border(
    left=Side(style='thin', color='D9D9D9'),
    right=Side(style='thin', color='D9D9D9'),
    top=Side(style='thin', color='D9D9D9'),
    bottom=Side(style='thin', color='D9D9D9')
)
total_fill = PatternFill(start_color='D9E1F2', end_color='D9E1F2', fill_type='solid')

# -------------------------------------------------------------
# Sheet 1: Danh Sách Sắp Xếp Toàn Bộ
# -------------------------------------------------------------
ws1 = wb.active
ws1.title = '1_Danh_Sach_Sap_Xep_Full'
ws1.views.sheetView[0].showGridLines = True

ws1['A1'] = 'BÁO CÁO HIỆU QUẢ QUẢNG CÁO FACEBOOK - BẢNG SẮP XẾP TOÀN BỘ ID ADS'
ws1['A1'].font = title_font
ws1['A2'] = 'Tiêu chí sắp xếp: Ưu tiên Chi phí / Lượt mua tăng dần, sau đó đến Chi phí / Cuộc trò chuyện tăng dần'
ws1['A2'].font = sub_title_font

headers1 = [
    'STT', 'Mã Quảng Cáo (Ad ID)', 'Số Tiền Chi Tiêu', 'Số Tin Nhắn', 'Chi Phí / Tin Nhắn',
    'Số Lượt Mua', 'Chi Phí / Lượt Mua', 'Tỷ Lệ L2/L1', 'Số Bình Luận', 'Đánh Giá Ổn Định',
    'Khuyến Nghị Ngân Sách', 'Vị Trí Phù Hợp Nhất'
]

for col_idx, h in enumerate(headers1, start=1):
    cell = ws1.cell(row=4, column=col_idx, value=h)
    cell.font = header_font
    cell.fill = header_fill
    cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)

for row_idx, r in df_final_sorted.iterrows():
    curr_row = row_idx + 5
    ws1.cell(row=curr_row, column=1, value=row_idx+1).alignment = Alignment(horizontal='center')
    ws1.cell(row=curr_row, column=2, value=str(r['ad_id'])).alignment = Alignment(horizontal='center')
    
    c_spend = ws1.cell(row=curr_row, column=3, value=round(r['spend']) if pd.notna(r['spend']) else 0)
    c_spend.number_format = '#,##0 "₫"'
    
    c_msg = ws1.cell(row=curr_row, column=4, value=round(r['msg']) if pd.notna(r['msg']) else 0)
    c_msg.number_format = '#,##0'
    
    c_cpm = ws1.cell(row=curr_row, column=5, value=round(r['cpm']) if pd.notna(r['cpm']) else None)
    c_cpm.number_format = '#,##0 "₫"'
    
    c_pur = ws1.cell(row=curr_row, column=6, value=round(r['pur']) if pd.notna(r['pur']) else 0)
    c_pur.number_format = '#,##0'
    
    c_cpp = ws1.cell(row=curr_row, column=7, value=round(r['cpp']) if pd.notna(r['cpp']) else None)
    c_cpp.number_format = '#,##0 "₫"'
    
    c_l2 = ws1.cell(row=curr_row, column=8, value=r['l2_l1'] if pd.notna(r['l2_l1']) else 0)
    c_l2.number_format = '0%'
    
    c_cmt = ws1.cell(row=curr_row, column=9, value=round(r['cmt']) if pd.notna(r['cmt']) else 0)
    c_cmt.number_format = '#,##0'
    
    c_stab = ws1.cell(row=curr_row, column=10, value=r['stability'])
    c_stab.alignment = Alignment(horizontal='center')
    
    c_rec = ws1.cell(row=curr_row, column=11, value=r['recommendation'])
    c_rec.alignment = Alignment(horizontal='center')
    
    c_pos = ws1.cell(row=curr_row, column=12, value=r['best_pos'])
    c_pos.alignment = Alignment(horizontal='center')
    
    for c in range(1, 13):
        ws1.cell(row=curr_row, column=c).border = thin_border
        ws1.cell(row=curr_row, column=c).font = regular_font

# Total row
tot_row = len(df_final_sorted) + 5
ws1.cell(row=tot_row, column=1, value='TỔNG CỘNG').alignment = Alignment(horizontal='center')
ws1.cell(row=tot_row, column=1).font = bold_font

ws1.cell(row=tot_row, column=2, value=f'{len(df_final_sorted)} Ads').alignment = Alignment(horizontal='center')
ws1.cell(row=tot_row, column=2).font = bold_font

t_spend = ws1.cell(row=tot_row, column=3, value=round(df_final_sorted['spend'].sum()))
t_spend.number_format = '#,##0 "₫"'
t_spend.font = bold_font

t_msg = ws1.cell(row=tot_row, column=4, value=round(df_final_sorted['msg'].sum()))
t_msg.number_format = '#,##0'
t_msg.font = bold_font

t_cpm = ws1.cell(row=tot_row, column=5, value=round(df_final_sorted['spend'].sum() / df_final_sorted['msg'].sum()))
t_cpm.number_format = '#,##0 "₫"'
t_cpm.font = bold_font

t_pur = ws1.cell(row=tot_row, column=6, value=round(df_final_sorted['pur'].sum()))
t_pur.number_format = '#,##0'
t_pur.font = bold_font

t_cpp = ws1.cell(row=tot_row, column=7, value=round(df_final_sorted['spend'].sum() / df_final_sorted['pur'].sum()))
t_cpp.number_format = '#,##0 "₫"'
t_cpp.font = bold_font

t_l2 = ws1.cell(row=tot_row, column=8, value=df_final_sorted['pur'].sum() / df_final_sorted['msg'].sum())
t_l2.number_format = '0%'
t_l2.font = bold_font

t_cmt = ws1.cell(row=tot_row, column=9, value=round(df_final_sorted['cmt'].sum()))
t_cmt.number_format = '#,##0'
t_cmt.font = bold_font

for c in range(1, 13):
    cell = ws1.cell(row=tot_row, column=c)
    cell.fill = total_fill
    cell.border = thin_border

# -------------------------------------------------------------
# Sheet 2: Báo Cáo Tính Ổn Định Theo Ngày
# -------------------------------------------------------------
ws2 = wb.create_sheet('2_Bao_Cao_On_Dinh_Theo_Ngay')
ws2.views.sheetView[0].showGridLines = True

ws2['A1'] = 'PHÂN TÍCH ĐỘ ỔN ĐỊNH THEO TỪNG NGÀY (DỰA TRÊN SHEET THEO NGÀY)'
ws2['A1'].font = title_font
ws2['A2'] = 'Đánh giá độ biến động (CV = Độ lệch chuẩn / Trung bình) và tần suất phát sinh đơn hàng qua các ngày hoạt động'
ws2['A2'].font = sub_title_font

headers2 = [
    'STT', 'Mã Quảng Cáo (Ad ID)', 'Số Ngày Chạy', 'Số Ngày Ra Tin', 'Số Ngày Ra Đơn',
    'Tỷ Lệ Ngày Có Đơn', 'Chi Phí TB/Tin (Ngày)', 'Độ Biến Động Tin (CV %)',
    'Chi Phí TB/Đơn (Ngày)', 'Độ Biến Động Đơn (CV %)', 'Phân Loại Tính Ổn Định', 'Nhận Định Chi Tiết'
]

for col_idx, h in enumerate(headers2, start=1):
    cell = ws2.cell(row=4, column=col_idx, value=h)
    cell.font = header_font
    cell.fill = PatternFill(start_color='2E75B6', end_color='2E75B6', fill_type='solid')
    cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)

# Sort by stability: Rất ổn định, Ổn định, Không ổn định, Không có lượt mua, Mẫu ít
stab_order = {'Rất ổn định': 1, 'Ổn định': 2, 'Mẫu ít (1-2 ngày)': 3, 'Không ổn định': 4, 'Không có lượt mua': 5}
df_stab_sorted = df_all.copy()
df_stab_sorted['sort_stab'] = df_stab_sorted['stability'].map(stab_order)
df_stab_sorted = df_stab_sorted.sort_values(by=['sort_stab', 'pur', 'cpp'], ascending=[True, False, True])

for row_idx, r in df_stab_sorted.iterrows():
    curr_row = row_idx + 5
    ws2.cell(row=curr_row, column=1, value=row_idx+1).alignment = Alignment(horizontal='center')
    ws2.cell(row=curr_row, column=2, value=str(r['ad_id'])).alignment = Alignment(horizontal='center')
    ws2.cell(row=curr_row, column=3, value=r['active_days']).alignment = Alignment(horizontal='center')
    ws2.cell(row=curr_row, column=4, value=r['msg_days']).alignment = Alignment(horizontal='center')
    ws2.cell(row=curr_row, column=5, value=r['pur_days']).alignment = Alignment(horizontal='center')
    
    c_ratio = ws2.cell(row=curr_row, column=6, value=r['pur_ratio'])
    c_ratio.number_format = '0%'
    c_ratio.alignment = Alignment(horizontal='center')
    
    c_cpm_m = ws2.cell(row=curr_row, column=7, value=round(r['cpm_mean']) if pd.notna(r['cpm_mean']) else None)
    c_cpm_m.number_format = '#,##0 "₫"'
    
    c_cpm_cv = ws2.cell(row=curr_row, column=8, value=r['cpm_cv'] if pd.notna(r['cpm_cv']) else None)
    c_cpm_cv.number_format = '0%'
    c_cpm_cv.alignment = Alignment(horizontal='center')
    
    c_cpp_m = ws2.cell(row=curr_row, column=9, value=round(r['cpp_mean']) if pd.notna(r['cpp_mean']) else None)
    c_cpp_m.number_format = '#,##0 "₫"'
    
    c_cpp_cv = ws2.cell(row=curr_row, column=10, value=r['cpp_cv'] if pd.notna(r['cpp_cv']) else None)
    c_cpp_cv.number_format = '0%'
    c_cpp_cv.alignment = Alignment(horizontal='center')
    
    ws2.cell(row=curr_row, column=11, value=r['stability']).alignment = Alignment(horizontal='center')
    
    # Detail note
    if r['stability'] == 'Rất ổn định':
        note = f"Ra đơn {r['pur_days']}/{r['active_days']} ngày ({r['pur_ratio']*100:.0f}%). Biến động chi phí thấp, phong độ xuất sắc."
    elif r['stability'] == 'Ổn định':
        note = f"Ra đơn {r['pur_days']}/{r['active_days']} ngày. Chi phí duy trì mức hợp lý, có thể kiểm soát."
    elif r['stability'] == 'Không có lượt mua':
        note = f"Chạy {r['active_days']} ngày, chi {r['spend']:,.0f} đ nhưng không có lượt mua nào."
    elif r['stability'] == 'Mẫu ít (1-2 ngày)':
        note = f"Mới chạy {r['active_days']} ngày. Cần thêm thời gian theo dõi dữ liệu."
    else:
        note = f"Chi phí biến động mạnh (CV cao), ngày ra đơn ngày không. Cần tối ưu lại."
    ws2.cell(row=curr_row, column=12, value=note)
    
    for c in range(1, 13):
        ws2.cell(row=curr_row, column=c).border = thin_border
        ws2.cell(row=curr_row, column=c).font = regular_font

# -------------------------------------------------------------
# Sheet 3: Vị Trí Quảng Cáo
# -------------------------------------------------------------
ws3 = wb.create_sheet('3_Vi_Tri_Quang_Cao')
ws3.views.sheetView[0].showGridLines = True

ws3['A1'] = 'TỔNG HỢP HIỆU QUẢ THEO VỊ TRÍ QUẢNG CÁO'
ws3['A1'].font = title_font
ws3['A2'] = 'Dữ liệu được trích xuất từ Sheet Vị Trí Quảng Cáo và phân tích theo tỷ lệ chuyển đổi, chi phí và độ ổn định'
ws3['A2'].font = sub_title_font

headers3 = [
    'Vị Trí Quảng Cáo', 'Chi Tiêu (VND)', 'Tỷ Trọng Ngân Sách', 'Số Tin Nhắn', 'Chi Phí / Tin Nhắn',
    'Số Lượt Mua', 'Tỷ Trọng Đơn Hàng', 'Chi Phí / Lượt Mua', 'Tỷ Lệ Chốt L2/L1',
    'CV Tin Nhắn (%)', 'CV Lượt Mua (%)', 'Đánh Giá Hiệu Quả & Tính Ổn Định'
]

for col_idx, h in enumerate(headers3, start=1):
    cell = ws3.cell(row=4, column=col_idx, value=h)
    cell.font = header_font
    cell.fill = PatternFill(start_color='385723', end_color='385723', fill_type='solid')
    cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)

# Compute Placement aggregate table
pos_agg_table = df_pos_clean.groupby('Vị trí quảng cáo').agg(
    spend=('Số tiền đã chi tiêu (VND)', 'sum'),
    msg=('Lượt bắt đầu cuộc trò chuyện qua tin nhắn', 'sum'),
    pur=('Lượt mua', 'sum')
).reset_index().sort_values('spend', ascending=False)

tot_spend_pos = pos_agg_table['spend'].sum()
tot_msg_pos = pos_agg_table['msg'].sum()
tot_pur_pos = pos_agg_table['pur'].sum()

# Daily CV per placement
df_pos_daily = df_pos_clean[df_pos_clean['Ngày'].astype(str).str.strip().str.lower() != 'all'].copy()
pos_day_agg = df_pos_daily.groupby(['Vị trí quảng cáo', 'Ngày']).agg(
    spend=('Số tiền đã chi tiêu (VND)', 'sum'),
    msg=('Lượt bắt đầu cuộc trò chuyện qua tin nhắn', 'sum'),
    pur=('Lượt mua', 'sum')
).reset_index()
pos_day_agg['cpm'] = pos_day_agg['spend'] / pos_day_agg['msg']
pos_day_agg['cpp'] = pos_day_agg['spend'] / pos_day_agg['pur']

pos_cv_map = {}
for pos_name, g in pos_day_agg.groupby('Vị trí quảng cáo'):
    cpm_m = g['cpm'].mean()
    cpm_s = g['cpm'].std()
    cpm_cv = (cpm_s / cpm_m) if cpm_m else np.nan
    g_p = g[g['pur'] > 0]
    cpp_m = g_p['cpp'].mean() if len(g_p) > 0 else np.nan
    cpp_s = g_p['cpp'].std() if len(g_p) > 1 else np.nan
    cpp_cv = (cpp_s / cpp_m) if cpp_m else np.nan
    pos_cv_map[pos_name] = {'cpm_cv': cpm_cv, 'cpp_cv': cpp_cv}

for row_idx, r in pos_agg_table.iterrows():
    curr_row = row_idx + 5
    p_name = r['Vị trí quảng cáo']
    ws3.cell(row=curr_row, column=1, value=p_name).alignment = Alignment(horizontal='left')
    
    c_sp = ws3.cell(row=curr_row, column=2, value=round(r['spend']))
    c_sp.number_format = '#,##0 "₫"'
    
    c_sp_pct = ws3.cell(row=curr_row, column=3, value=r['spend'] / tot_spend_pos)
    c_sp_pct.number_format = '0%'
    c_sp_pct.alignment = Alignment(horizontal='center')
    
    c_m = ws3.cell(row=curr_row, column=4, value=round(r['msg']))
    c_m.number_format = '#,##0'
    
    c_cpm = ws3.cell(row=curr_row, column=5, value=round(r['spend'] / r['msg']) if r['msg'] > 0 else None)
    c_cpm.number_format = '#,##0 "₫"'
    
    c_p = ws3.cell(row=curr_row, column=6, value=round(r['pur']))
    c_p.number_format = '#,##0'
    
    c_p_pct = ws3.cell(row=curr_row, column=7, value=r['pur'] / tot_pur_pos if tot_pur_pos > 0 else 0)
    c_p_pct.number_format = '0%'
    c_p_pct.alignment = Alignment(horizontal='center')
    
    c_cpp = ws3.cell(row=curr_row, column=8, value=round(r['spend'] / r['pur']) if r['pur'] > 0 else None)
    c_cpp.number_format = '#,##0 "₫"'
    
    c_l2 = ws3.cell(row=curr_row, column=9, value=r['pur'] / r['msg'] if r['msg'] > 0 else 0)
    c_l2.number_format = '0%'
    c_l2.alignment = Alignment(horizontal='center')
    
    cv_info = pos_cv_map.get(p_name, {'cpm_cv': np.nan, 'cpp_cv': np.nan})
    c_cpm_cv = ws3.cell(row=curr_row, column=10, value=cv_info['cpm_cv'] if pd.notna(cv_info['cpm_cv']) else None)
    c_cpm_cv.number_format = '0%'
    c_cpm_cv.alignment = Alignment(horizontal='center')
    
    c_cpp_cv = ws3.cell(row=curr_row, column=11, value=cv_info['cpp_cv'] if pd.notna(cv_info['cpp_cv']) else None)
    c_cpp_cv.number_format = '0%'
    c_cpp_cv.alignment = Alignment(horizontal='center')
    
    # Evaluation
    if p_name == 'Facebook Reels':
        eval_txt = 'Vị trí chủ lực số 1: Chiếm 73% đơn hàng, chi phí rẻ nhất (174k/đơn), cực kỳ ổn định (CV 30%). Phù hợp video ngắn.'
    elif p_name == 'Bảng tin':
        eval_txt = 'Vị trí chốt đơn chất lượng cao: Tỷ lệ chốt đơn tới 47%, độ ổn định cao nhất (CV 22%). Phù hợp bài viết hình ảnh/nội dung sâu.'
    elif p_name == 'Facebook Stories':
        eval_txt = 'Vị trí bổ trợ: Chi phí tương đương Bảng tin (236k/đơn), hiệu quả ổn định. Phù hợp nội dung story ngắn.'
    elif p_name == 'Kết quả tìm kiếm':
        eval_txt = 'Tiềm năng cao: Chi phí rất rẻ (133k/đơn), tỷ lệ chốt 67%, nhưng lưu lượng tìm kiếm còn hạn chế.'
    elif p_name == 'Thước phim trong luồng':
        eval_txt = 'Kém hiệu quả: Chi phí đắt (330k/đơn), biến động mạnh (CV 84%). Cân nhắc tắt.'
    else:
        eval_txt = 'Chi phí nhỏ lẻ, không hiệu quả hoặc 0 lượt mua. Đề xuất tắt.'
    ws3.cell(row=curr_row, column=12, value=eval_txt)
    
    for c in range(1, 13):
        ws3.cell(row=curr_row, column=c).border = thin_border
        ws3.cell(row=curr_row, column=c).font = regular_font

# -------------------------------------------------------------
# Sheet 4: Đề Xuất Tăng Ngân Sách & Hành Động
# -------------------------------------------------------------
ws4 = wb.create_sheet('4_De_Xuat_Ngan_Sach')
ws4.views.sheetView[0].showGridLines = True

ws4['A1'] = 'KẾ HOẠCH HÀNH ĐỘNG & ĐỀ XUẤT PHÂN BỔ NGÂN SÁCH'
ws4['A1'].font = title_font
ws4['A2'] = 'Phân loại chi tiết các nhóm ID Ads tiềm năng tăng ngân sách, nhóm duy trì và nhóm cần tắt/cắt giảm ngay'
ws4['A2'].font = sub_title_font

headers4 = [
    'Nhóm Đề Xuất', 'Mã Quảng Cáo (Ad ID)', 'Chi Tiêu Hiện Tại', 'Lượt Mua', 'Chi Phí / Mua',
    'Tỷ Lệ Chốt L2/L1', 'Độ Ổn Định', 'Vị Trí Tối Ưu', 'Kế Hoạch & Hành Động Cụ Thể'
]

for col_idx, h in enumerate(headers4, start=1):
    cell = ws4.cell(row=4, column=col_idx, value=h)
    cell.font = header_font
    cell.fill = PatternFill(start_color='C65911', end_color='C65911', fill_type='solid')
    cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)

# Build action rows
action_rows = []
# 1. Scale Up
scale_ads = ['120249153794660532', '120249153839930532', '52550106995296', '120249153813990532', '120249153839950532']
for aid in scale_ads:
    r = df_all[df_all['ad_id'] == aid].iloc[0]
    action_rows.append({
        'group': '1. TĂNG MẠNH NGÂN SÁCH (+30% đến +50%)',
        'ad_id': aid, 'spend': r['spend'], 'pur': r['pur'], 'cpp': r['cpp'], 'l2_l1': r['l2_l1'],
        'stability': r['stability'], 'pos': r['best_pos'],
        'action': f"Tăng 30-50% ngân sách mỗi 2-3 ngày. Tập trung tối đa vào vị trí {r['best_pos']}."
    })

# 2. Moderate Scale
mod_ads = ['120249153839980532', '120252740442820268', '52550102779296', '120248174416610532', '52642653160220']
for aid in mod_ads:
    r = df_all[df_all['ad_id'] == aid].iloc[0]
    action_rows.append({
        'group': '2. TĂNG NHẸ NGÂN SÁCH (+15% đến +20%)',
        'ad_id': aid, 'spend': r['spend'], 'pur': r['pur'], 'cpp': r['cpp'], 'l2_l1': r['l2_l1'],
        'stability': r['stability'], 'pos': r['best_pos'],
        'action': f"Tăng nhẹ 15-20% ngân sách, theo dõi sát chi phí mua. Ưu tiên vị trí {r['best_pos']}."
    })

# 3. Maintain High Volume Feed
maint_ads = ['52521773324529', '52517259236329', '52642651596220']
for aid in maint_ads:
    r = df_all[df_all['ad_id'] == aid].iloc[0]
    action_rows.append({
        'group': '3. DUY TRÌ & TỐI ƯU VỊ TRÍ (CỘT TRỤ DOANH SỐ)',
        'ad_id': aid, 'spend': r['spend'], 'pur': r['pur'], 'cpp': r['cpp'], 'l2_l1': r['l2_l1'],
        'stability': r['stability'], 'pos': r['best_pos'],
        'action': f"Duy trì ngân sách hiện tại, dồn hiển thị vào vị trí {r['best_pos']} (giảm ngân sách các vị trí kém)."
    })

# 4. Turn off / Cut budget (Top money wasters)
cut_ads = ['52625109508219', '52528422038929', '52630502224619', '52548569767096', '52550498603096', 
           '52505497343329', '52642651061420', '52542791258896', '52516371049096', '52516371646696']
for aid in cut_ads:
    r = df_all[df_all['ad_id'] == aid].iloc[0]
    action_rows.append({
        'group': '4. TẮT NGAY / CẮT BỎ (CHỐNG LÃNG PHÍ)',
        'ad_id': aid, 'spend': r['spend'], 'pur': r['pur'], 'cpp': r['cpp'], 'l2_l1': r['l2_l1'],
        'stability': r['stability'], 'pos': r['best_pos'],
        'action': f"Tắt ngay lập tức để thu hồi ngân sách ({r['spend']:,.0f} đ đã chi). Dồn tiền sang Nhóm 1."
    })

for idx, r in enumerate(action_rows):
    curr_row = idx + 5
    ws4.cell(row=curr_row, column=1, value=r['group']).alignment = Alignment(horizontal='left')
    ws4.cell(row=curr_row, column=2, value=str(r['ad_id'])).alignment = Alignment(horizontal='center')
    
    c_sp = ws4.cell(row=curr_row, column=3, value=round(r['spend']))
    c_sp.number_format = '#,##0 "₫"'
    
    c_p = ws4.cell(row=curr_row, column=4, value=round(r['pur']) if pd.notna(r['pur']) else 0)
    c_p.number_format = '#,##0'
    
    c_cpp = ws4.cell(row=curr_row, column=5, value=round(r['cpp']) if pd.notna(r['cpp']) else None)
    c_cpp.number_format = '#,##0 "₫"'
    
    c_l2 = ws4.cell(row=curr_row, column=6, value=r['l2_l1'] if pd.notna(r['l2_l1']) else 0)
    c_l2.number_format = '0%'
    c_l2.alignment = Alignment(horizontal='center')
    
    ws4.cell(row=curr_row, column=7, value=r['stability']).alignment = Alignment(horizontal='center')
    ws4.cell(row=curr_row, column=8, value=r['pos']).alignment = Alignment(horizontal='center')
    ws4.cell(row=curr_row, column=9, value=r['action'])
    
    for c in range(1, 10):
        ws4.cell(row=curr_row, column=c).border = thin_border
        ws4.cell(row=curr_row, column=c).font = regular_font

# Adjust column widths for all sheets
for ws in [ws1, ws2, ws3, ws4]:
    for col in ws.columns:
        max_len = 0
        col_letter = get_column_letter(col[0].column)
        for cell in col:
            # ignore title rows
            if cell.row in [1, 2]:
                continue
            v = str(cell.value or '')
            if len(v) > max_len:
                max_len = len(v)
        ws.column_dimensions[col_letter].width = max(max_len + 3, 12)

out_file = 'Bao_cao_quang_cao_Facebook.xlsx'
wb.save(out_file)
print(f'Report successfully saved to {out_file}!')
