# -*- coding: utf-8 -*-
with open('update_all.py', 'r', encoding='utf-8') as f:
    code = f.read()

s6_start = "# Sheet 6: MỚI - Báo Cáo 2 Từ Khóa: \"Sản\" và \"Ở Cữ\""
s6_end = "# Adjust column widths"

p_s6_1 = code.find(s6_start)
p_s6_2 = code.find(s6_end)

new_sheet6_code = """# Sheet 6: Báo Cáo 2 Từ Khóa: "Sản" (15 Ads) và "Ở Cữ" (8 Ads) Dựa Trên Ghi Chú Điền Tay Của Bạn
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
    ws6.cell(row=curr_row, column=8, value=r['notes']).font = regular_font
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
    ws6.cell(row=curr_row, column=8, value=r['notes']).font = regular_font
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

"""

if p_s6_1 != -1 and p_s6_2 != -1:
    code = code[:p_s6_1] + new_sheet6_code + code[p_s6_2:]
    print("Replaced Sheet 6 code successfully!")
else:
    print(f"Error bounds: {p_s6_1}, {p_s6_2}")

with open('update_all.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated update_all.py!")
