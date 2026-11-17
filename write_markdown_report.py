import pandas as pd
import numpy as np

from create_excel_report import df_final_sorted, df_pos_clean, pos_agg_table, pos_cv_map

def fmt_cur(val):
    if pd.isna(val) or val is None:
        return '-'
    return f"{round(val):,d} đ".replace(',', '.')

def fmt_int(val):
    if pd.isna(val) or val is None:
        return '0'
    return f"{round(val):,d}".replace(',', '.')

def fmt_pct(val):
    if pd.isna(val) or val is None:
        return '0%'
    return f"{round(val * 100):,d}%"

# Generate Markdown content
md = []
md.append("# BÁO CÁO PHÂN TÍCH HIỆU QUẢ QUẢNG CÁO FACEBOOK CHI TIẾT")
md.append("*Thời gian báo cáo: 01/11/2026 - 16/11/2026 (16 ngày)*\n")
md.append("> **Định dạng chuẩn hóa**: Toàn bộ số liệu đã được làm tròn không có số thập phân. Các cột chi phí chuẩn hóa theo định dạng tiền tệ đồng (VNĐ). Sắp xếp ưu tiên theo Chi phí / Lượt mua tăng dần, sau đó đến Chi phí / Cuộc trò chuyện tăng dần.\n")

# Section 1: Tổng Hợp Toàn Bộ Chiến Dịch
tot_spend = df_final_sorted['spend'].sum()
tot_msg = df_final_sorted['msg'].sum()
tot_pur = df_final_sorted['pur'].sum()
tot_cmt = df_final_sorted['cmt'].sum()
avg_cpm = tot_spend / tot_msg
avg_cpp = tot_spend / tot_pur
avg_conv = tot_pur / tot_msg

md.append("## 1. TỔNG HỢP CHI PHÍ & KẾT QUẢ QUẢNG CÁO TOÀN DIỆN")
md.append(f"- **Tổng ngân sách chi tiêu**: **{fmt_cur(tot_spend)}**")
md.append(f"- **Tổng số cuộc trò chuyện (Tin nhắn)**: **{fmt_int(tot_msg)}** tin nhắn")
md.append(f"- **Chi phí trung bình / Cuộc trò chuyện**: **{fmt_cur(avg_cpm)}**")
md.append(f"- **Tổng lượt mua (Đơn hàng)**: **{fmt_int(tot_pur)}** đơn")
md.append(f"- **Chi phí trung bình / Lượt mua (CPA)**: **{fmt_cur(avg_cpp)}**")
md.append(f"- **Tỷ lệ chuyển đổi tổng thể (L2/L1 - Mua / Tin nhắn)**: **{fmt_pct(avg_conv)}**")
md.append(f"- **Tổng bình luận bài viết**: **{fmt_int(tot_cmt)}** bình luận\n")

# Section 1.2: Phân Tầng Theo Mức Chi Tiêu
md.append("### 1.1. Phân tầng theo mức chi tiêu của nhóm quảng cáo")
md.append("| Nhóm Ngân Sách | Số Lượng Ads | Tổng Chi Tiêu | Tỷ Trọng Chi Tiêu | Tổng Tin Nhắn | Chi Phí / Tin | Tổng Đơn | Tỷ Trọng Đơn | Chi Phí / Đơn | Tỷ Lệ L2/L1 |")
md.append("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |")

def spend_tier(s):
    if s >= 5000000: return 'Trên 5 triệu (> 5M)'
    elif s >= 2000000: return 'Từ 2M - 5M'
    elif s >= 1000000: return 'Từ 1M - 2M'
    else: return 'Dưới 1 triệu (< 1M)'

df_final_sorted['spend_tier'] = df_final_sorted['spend'].apply(spend_tier)
tier_order = ['Trên 5 triệu (> 5M)', 'Từ 2M - 5M', 'Từ 1M - 2M', 'Dưới 1 triệu (< 1M)']

for t in tier_order:
    sub = df_final_sorted[df_final_sorted['spend_tier'] == t]
    c_cnt = len(sub)
    c_sp = sub['spend'].sum()
    c_msg = sub['msg'].sum()
    c_pur = sub['pur'].sum()
    c_cpm = c_sp / c_msg if c_msg > 0 else 0
    c_cpp = c_sp / c_pur if c_pur > 0 else 0
    c_l2 = c_pur / c_msg if c_msg > 0 else 0
    md.append(f"| **{t}** | {fmt_int(c_cnt)} | {fmt_cur(c_sp)} | {fmt_pct(c_sp/tot_spend)} | {fmt_int(c_msg)} | {fmt_cur(c_cpm)} | {fmt_int(c_pur)} | {fmt_pct(c_pur/tot_pur)} | {fmt_cur(c_cpp)} | {fmt_pct(c_l2)} |")
md.append("\n")

# Section 1.3: Phân Tầng Theo Hiệu Quả Chi Phí Mua (CPP)
md.append("### 1.2. Phân tầng theo hiệu quả chi phí trên mỗi lượt mua (CPP)")
md.append("| Phân Tầng Hiệu Quả | Số Lượng Ads | Chi Tiêu | Tỷ Trọng Tiền | Số Đơn | Tỷ Trọng Đơn | Chi Phí / Đơn | Chi Phí / Tin | Tỷ Lệ Chốt | Đánh Giá & Hành Động |")
md.append("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |")

def cpp_tier_f(r):
    p = r['pur']
    c = r['cpp']
    if pd.isna(p) or p == 0: return '5. Không có đơn (0 lượt mua)'
    elif c < 100000: return '1. Siêu hiệu quả (< 100k)'
    elif c < 180000: return '2. Hiệu quả tốt (100k - 180k)'
    elif c < 250000: return '3. Trung bình (180k - 250k)'
    else: return '4. Kém hiệu quả (> 250k)'

df_final_sorted['cpp_tier'] = df_final_sorted.apply(cpp_tier_f, axis=1)
cpp_tiers = sorted(df_final_sorted['cpp_tier'].unique())

tier_actions = {
    '1. Siêu hiệu quả (< 100k)': 'Tăng ngân sách tối đa (+30-50%). Đang mang lại 28% đơn với chỉ 10% chi phí.',
    '2. Hiệu quả tốt (100k - 180k)': 'Tăng ngân sách vừa phải (+15-20%). Đang mang lại 26% đơn hàng.',
    '3. Trung bình (180k - 250k)': 'Duy trì ngân sách, tối ưu nội dung và vị trí hiển thị.',
    '4. Kém hiệu quả (> 250k)': 'Cắt giảm ngân sách, kiểm tra lại đối tượng hoặc tắt.',
    '5. Không có đơn (0 lượt mua)': 'TẮT NGAY LẬP TỨC. Đang lãng phí 12.3 triệu đồng mà không có đơn nào.'
}

for t in cpp_tiers:
    sub = df_final_sorted[df_final_sorted['cpp_tier'] == t]
    c_cnt = len(sub)
    c_sp = sub['spend'].sum()
    c_msg = sub['msg'].sum()
    c_pur = sub['pur'].sum()
    c_cpm = c_sp / c_msg if c_msg > 0 else 0
    c_cpp = c_sp / c_pur if c_pur > 0 else 0
    c_l2 = c_pur / c_msg if c_msg > 0 else 0
    md.append(f"| **{t[3:]}** | {fmt_int(c_cnt)} | {fmt_cur(c_sp)} | {fmt_pct(c_sp/tot_spend)} | {fmt_int(c_pur)} | {fmt_pct(c_pur/tot_pur)} | {fmt_cur(c_cpp) if c_pur > 0 else '-'} | {fmt_cur(c_cpm) if c_msg > 0 else '-'} | {fmt_pct(c_l2)} | {tier_actions[t]} |")
md.append("\n")

# Section 2: Top Ads Sắp Xếp
md.append("## 2. BẢNG SẮP XẾP ID ADS THEO TIÊU CHÍ ƯU TIÊN CHI PHÍ LƯỢT MUA & CHI PHÍ TIN NHẮN (TỪ THẤP ĐẾN CAO)")
md.append("*(Bảng hiển thị các Ad IDs có lượt mua tốt nhất, toàn bộ 163 ID Ads được lưu đầy đủ trong file Excel)*\n")
md.append("| Hạng | Mã Quảng Cáo (Ad ID) | Chi Tiêu (VND) | Tin Nhắn | Chi Phí / Tin | Lượt Mua | Chi Phí / Mua | Tỷ Lệ L2/L1 | Ngày Chạy | Ngày Đơn | Độ Ổn Định | Vị Trí Tối Ưu |")
md.append("| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |")

for idx, r in df_final_sorted[df_final_sorted['pur'] > 0].head(35).iterrows():
    md.append(f"| {idx+1} | `{r['ad_id']}` | {fmt_cur(r['spend'])} | {fmt_int(r['msg'])} | {fmt_cur(r['cpm'])} | {fmt_int(r['pur'])} | **{fmt_cur(r['cpp'])}** | {fmt_pct(r['l2_l1'])} | {r['active_days']} | {r['pur_days']} | {r['stability']} | {r['best_pos']} |")
md.append("\n")

# Section 3: Đánh giá độ ổn định theo sheet Theo Ngày
md.append("## 3. BÁO CÁO TÍNH ỔN ĐỊNH CỦA ID ADS THEO TỪNG NGÀY (DỰA TRÊN SHEET THEO NGÀY)")
md.append("Dựa vào dữ liệu 16 ngày chạy trong sheet **Theo Ngày**, đánh giá tính ổn định qua 2 tiêu chí cốt lõi:")
md.append("1. **Tỷ lệ ngày ra đơn đều đặn** (Số ngày có đơn / Số ngày chạy).")
md.append("2. **Độ biến động chi phí qua các ngày** (Hệ số biến thiên CV = Độ lệch chuẩn / Chi phí trung bình). CV càng thấp (< 40%) thể hiện chi phí càng ổn định.\n")

md.append("### 3.1. Nhóm ID Ads RẤT ỔN ĐỊNH & TIỀM NĂNG NHẤT")
md.append("| Mã Quảng Cáo (Ad ID) | Chi Tiêu | Lượt Mua | Chi Phí / Mua | Tỷ Lệ Ngày Ra Đơn | CV Chi Phí Tin | CV Chi Phí Đơn | Nhận Định & Tiềm Năng Tăng Ngân Sách |")
md.append("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |")

top_stable = ['120249153839930532', '52550106995296', '120249153794660532', '120249153813990532', '120249153839950532', '52521773324529', '52642651596220']
for aid in top_stable:
    r = df_final_sorted[df_final_sorted['ad_id'] == aid].iloc[0]
    eval_text = ""
    if aid == '120249153839930532':
        eval_text = "**Siêu ổn định 100%**: Chạy 11 ngày ra đơn cả 11 ngày. Chi phí tin nhắn cực đều (CV 31%), CPP chỉ 64k. ƯU TIÊN SỐ 1 TĂNG MẠNH NGÂN SÁCH."
    elif aid == '52550106995296':
        eval_text = "**Hoàn hảo 100%**: Chạy 6 ngày ra đơn cả 6 ngày. Cả CV tin (29%) và CV đơn (31%) đều cực thấp. CPP chỉ 65k. ĐỀ XUẤT TĂNG NGÂN SÁCH."
    elif aid == '120249153794660532':
        eval_text = "**Quán quân sản lượng**: 130 đơn hàng, CPP chỉ 61k. Ra đơn 10/11 ngày (91%). Độ ổn định cao, quy mô đơn lớn nhất tài khoản. ĐỀ XUẤT TĂNG MẠNH."
    elif aid == '120249153813990532':
        eval_text = "**Ổn định dài ngày**: Chạy 14 ngày ra đơn 12 ngày (86%). Chi phí tin nhắn CV chỉ 32%, CPP 74k. ĐỀ XUẤT TĂNG NGÂN SÁCH."
    elif aid == '120249153839950532':
        eval_text = "**Tỷ lệ chốt đỉnh cao**: L2/L1 đạt 49% (2 khách nhắn có 1 đơn), CPP chỉ 66k. Chạy 14 ngày ra 24 đơn. ĐỀ XUẤT TĂNG NGÂN SÁCH."
    elif aid == '52521773324529':
        eval_text = "**Cột trụ Bảng tin**: Chạy 16 ngày ra đơn cả 16 ngày (100%). CV đơn cực thấp 34%, tỷ lệ chốt 88%! Cực kỳ ổn định trên Bảng tin. DUY TRÌ & MỞ RỘNG BẢNG TIN."
    elif aid == '52642651596220':
        eval_text = "**Ổn định nhóm ngân sách lớn**: Tiêu 8.4M mang về 49 đơn, chạy 10 ngày ra đơn 8 ngày. CV đơn 52%, CV tin 49%. ỔN ĐỊNH NHÓM REELS."
    md.append(f"| `{aid}` | {fmt_cur(r['spend'])} | {fmt_int(r['pur'])} | **{fmt_cur(r['cpp'])}** | **{r['pur_days']}/{r['active_days']} ({fmt_pct(r['pur_ratio'])})** | {fmt_pct(r['cpm_cv'])} | {fmt_pct(r['cpp_cv'])} | {eval_text} |")
md.append("\n")

# Section 3.2: Nhóm Không Ổn Định
md.append("### 3.2. Nhóm ID Ads KHÔNG ỔN ĐỊNH & KÉM HIỆU QUẢ")
md.append("- **Nhóm 73 Ads Đốt Ngân Sách Không Ra Đơn (0 lượt mua)**: Đã tiêu tốn **12.296.941 đ** mà không đem lại bất kỳ đơn hàng nào. Ví dụ tiêu biểu: `52625109508219` (chi 1.475.785 đ, 0 tin, 0 đơn), `52528422038929` (chi 621.678 đ chạy 14 ngày, 0 đơn), `52630502224619` (chi 549.336 đ, 0 đơn), `52548569767096` (chi 546.092 đ, 0 đơn).")
md.append("- **Nhóm Chi Phí Đơn Bất Thường / Nhảy Vọt (> 500k - 900k / đơn)**: Ví dụ `52505497343329` (chi 922.241 đ chạy 12 ngày chỉ ra đúng 1 đơn), `52642651061420` (chi 888.971 đ chạy 11 ngày ra 1 đơn), `52542791258896` (chi 887.845 đ ra 1 đơn), `52516371049096` (chi 803.938 đ ra 1 đơn). Các ads này hiệu quả cực kỳ bấp bênh, tỷ lệ rủi ro cao.\n")

# Section 4: Nhận Định Tăng Ngân Sách
md.append("## 4. BẢNG NHẬN ĐỊNH CHI TIẾT: ID ADS TIỀM NĂNG ĐỂ TĂNG NGÂN SÁCH VS ID ADS CẦN TẮT")
md.append("| Nhóm Hành Động | Mã Quảng Cáo (Ad ID) | Chi Tiêu Hiện Tại | Số Đơn | Chi Phí / Đơn | L2/L1 | Tính Ổn Định | Vị Trí Tối Ưu | Kế Hoạch Triển Khai |")
md.append("| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |")

plan_items = [
    ('1. TĂNG MẠNH NGÂN SÁCH (+30% - +50%)', '120249153794660532', 'Facebook Reels', 'Tăng 30-50% ngân sách mỗi 48h. Duy trì vị trí Reels (đang mang lại 119 đơn, giá 60k/đơn).'),
    ('1. TĂNG MẠNH NGÂN SÁCH (+30% - +50%)', '120249153839930532', 'Facebook Reels', 'Tăng mạnh 30-50%. Ra đơn 11/11 ngày (100%), giá đơn 64k cực rẻ, tỷ lệ chốt 42%.'),
    ('1. TĂNG MẠNH NGÂN SÁCH (+30% - +50%)', '52550106995296', 'Facebook Reels', 'Tăng mạnh ngân sách gấp đôi. Ra đơn 6/6 ngày, giá đơn 65k, CV cực kỳ ổn định (31%).'),
    ('1. TĂNG MẠNH NGÂN SÁCH (+30% - +50%)', '120249153813990532', 'Facebook Reels', 'Tăng 30-40% ngân sách. Đã chạy 14 ngày, giá đơn 74k, ra 53 đơn rất đều đặn.'),
    ('1. TĂNG MẠNH NGÂN SÁCH (+30% - +50%)', '120249153839950532', 'Facebook Reels', 'Tăng 30-40%. Tỷ lệ chốt đơn tới 49%, giá đơn 66k. Đẩy mạnh ngân sách để scale volume.'),
    ('2. TĂNG NHẸ / MỞ RỘNG (+15% - +25%)', '120249153839980532', 'Bảng tin / Reels', 'Tăng 15-20%. CPP 94k dưới ngưỡng 100k, L2/L1 39%. Cân nhắc mở rộng hiển thị Bảng tin (CPP 64k).'),
    ('2. TĂNG NHẸ / MỞ RỘNG (+15% - +25%)', '120252740442820268', 'Bảng tin', 'Tăng 15-20% ngân sách tập trung vào Bảng tin (giá đơn trên Bảng tin chỉ 88k so với 117k ở Reels).'),
    ('2. TĂNG NHẸ / MỞ RỘNG (+15% - +25%)', '52550102779296', 'Bảng tin', 'Tăng 15-20%. CPP 109k, tỷ lệ chốt 42%, phù hợp Bảng tin.'),
    ('2. TĂNG NHẸ / MỞ RỘNG (+15% - +25%)', '120248174416610532', 'Facebook Reels', 'Tăng 15-20%. Chạy 16 ngày ra 41 đơn, CPP 142k. Ổn định và bền vững.'),
    ('3. DUY TRÌ & TỐI ƯU CỘT TRỤ', '52521773324529', 'Bảng tin', 'Duy trì ngân sách 12M, dồn ngân sách hiển thị vào Bảng tin (tỷ lệ chốt tới 93%, ra 40 đơn, giá 189k).'),
    ('3. DUY TRÌ & TỐI ƯU CỘT TRỤ', '52517259236329', 'Bảng tin / Reels', 'Duy trì ngân sách 12.7M. Tối ưu chuyển dịch bớt từ Reels sang Bảng tin (giá đơn Bảng tin 165k rẻ hơn Reels 203k).'),
    ('4. TẮT NGAY / THU HỒI NGÂN SÁCH', '73 Ads 0 Đơn (Nhóm rác)', 'Không rõ', 'TẮT TOÀN BỘ 73 ADS không ra đơn để thu hồi ngay 12.3M ngân sách tái đầu tư vào Nhóm 1.'),
    ('4. TẮT NGAY / THU HỒI NGÂN SÁCH', '52505497343329', 'Facebook Reels', 'Tắt ngay: Chi 922k chạy 12 ngày chỉ có 1 đơn, giá đơn 922k quá đắt.'),
    ('4. TẮT NGAY / THU HỒI NGÂN SÁCH', '52642651061420', 'Facebook Reels', 'Tắt ngay: Chi 888k chạy 11 ngày ra 1 đơn, giá đơn 888k.'),
    ('4. TẮT NGAY / THU HỒI NGÂN SÁCH', '52542791258896', 'Facebook Reels', 'Tắt ngay: Chi 887k chỉ ra 1 đơn, giá đơn 887k.'),
    ('4. TẮT NGAY / THU HỒI NGÂN SÁCH', '52516371049096', 'Facebook Reels', 'Tắt ngay: Chi 803k chỉ ra 1 đơn, giá đơn 803k.')
]

for grp, aid, pos, act in plan_items:
    if aid == '73 Ads 0 Đơn (Nhóm rác)':
        md.append(f"| **{grp}** | `{aid}` | 12.296.941 đ | 0 | - | 0% | Không có đơn | - | {act} |")
    else:
        r = df_final_sorted[df_final_sorted['ad_id'] == aid].iloc[0]
        md.append(f"| **{grp}** | `{aid}` | {fmt_cur(r['spend'])} | {fmt_int(r['pur'])} | **{fmt_cur(r['cpp'])}** | {fmt_pct(r['l2_l1'])} | {r['stability']} | **{pos}** | {act} |")
md.append("\n")

# Section 5: Phân tích vị trí quảng cáo
md.append("## 5. PHÂN TÍCH VỊ TRÍ QUẢNG CÁO: ĐÁNH GIÁ TÍNH ỔN ĐỊNH VÀ ĐỘ PHÙ HỢP CỦA TỪNG ID ADS")
md.append("Dựa trên sheet **Vị trí quảng cáo**, báo cáo phân tích chi tiết hiệu quả của từng vị trí hiển thị và mức độ phù hợp của từng ID Ads.\n")

md.append("### 5.1. Bảng tổng hợp hiệu quả & độ ổn định của các vị trí quảng cáo")
md.append("| Vị Trí Quảng Cáo | Chi Tiêu (VND) | % Ngân Sách | Số Tin Nhắn | Chi Phí / Tin | Số Đơn | % Đơn Hàng | Chi Phí / Đơn | Tỷ Lệ L2/L1 | CV Tin (Ngày) | CV Đơn (Ngày) | Đánh Giá Độ Ổn Định |")
md.append("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |")

for idx, r in pos_agg_table.iterrows():
    p_name = r['Vị trí quảng cáo']
    cv_info = pos_cv_map.get(p_name, {'cpm_cv': np.nan, 'cpp_cv': np.nan})
    cpm = r['spend'] / r['msg'] if r['msg'] > 0 else 0
    cpp = r['spend'] / r['pur'] if r['pur'] > 0 else 0
    l2 = r['pur'] / r['msg'] if r['msg'] > 0 else 0
    
    if p_name == 'Facebook Reels':
        stab_str = "**Cực kỳ ổn định**: Ra đơn 16/16 ngày, CV đơn 30%. Kênh chủ lực."
    elif p_name == 'Bảng tin':
        stab_str = "**Ổn định tuyệt đối**: Ra đơn 16/16 ngày, CV đơn 22%. Tỷ lệ chốt đơn cao nhất."
    elif p_name == 'Facebook Stories':
        stab_str = "**Tương đối ổn định**: Ra đơn 12/16 ngày, CV đơn 40%."
    elif p_name == 'Kết quả tìm kiếm':
        stab_str = "**Biến động do volume nhỏ**: Ra đơn 9/16 ngày, CV đơn 82%, giá rất rẻ."
    elif p_name == 'Thước phim trong luồng':
        stab_str = "**Kém ổn định**: Ra đơn 7/16 ngày, CV đơn 84%, giá đắt."
    else:
        stab_str = "**Không ổn định / 0 đơn**: Chi phí lãng phí."
        
    md.append(f"| **{p_name}** | {fmt_cur(r['spend'])} | {fmt_pct(r['spend']/tot_spend)} | {fmt_int(r['msg'])} | {fmt_cur(cpm)} | {fmt_int(r['pur'])} | {fmt_pct(r['pur']/tot_pur)} | {fmt_cur(cpp) if r['pur'] > 0 else '-'} | {fmt_pct(l2)} | {fmt_pct(cv_info['cpm_cv'])} | {fmt_pct(cv_info['cpp_cv'])} | {stab_str} |")
md.append("\n")

md.append("### 5.2. Giải thích tại sao ID Ads nào phù hợp với vị trí nào và kết quả có ổn định không?")
md.append("#### 1. Nhóm ID Ads phù hợp nhất với FACEBOOK REELS")
md.append("- **Các Ad IDs tiêu biểu**: `120249153794660532`, `120249153839930532`, `52550106995296`, `120249153813990532`, `120249153839950532`.")
md.append("- **Tại sao phù hợp?**")
md.append("  + Đây là các định dạng video ngắn dạng lướt (short-form vertical video), nhịp độ nhanh, hình ảnh bắt mắt và thông điệp trực diện trong 3 giây đầu.")
md.append("  + Thu hút lượng lớn tin nhắn với chi phí cực rẻ (chỉ **19.000 đ - 27.000 đ / tin nhắn**).")
md.append("  + Hơn 85% - 95% đơn hàng của các Ad ID này đều đến từ Facebook Reels.")
md.append("- **Vị trí này cho ra kết quả ổn định không?**")
md.append("  + **CỰC KỲ ỔN ĐỊNH**. Facebook Reels ra đơn liên tục **16/16 ngày** (100% số ngày chạy), hệ số biến thiên chi phí đơn hàng chỉ **30%**, là vị trí có khả năng tiếp nhận quy mô ngân sách lớn nhất mà không bị gãy chi phí.\n")

md.append("#### 2. Nhóm ID Ads phù hợp nhất với BẢNG TIN (FACEBOOK FEED)")
md.append("- **Các Ad IDs tiêu biểu**: `52521773324529`, `120252740442820268`, `52550102779296`, `120249223441840268`, `52517259236329`.")
md.append("- **Tại sao phù hợp?**")
md.append("  + Các Ad ID này thường là bài viết có nội dung sâu (text dài, dẫn dắt câu chuyện, hình ảnh chi tiết, feedback khách hàng).")
md.append("  + Người dùng Bảng tin có thói quen dừng lại đọc kỹ thông tin sản phẩm trước khi bấm nhắn tin. Do đó, mặc dù chi phí tin nhắn cao hơn Reels (**108.000 đ / tin**), nhưng chất lượng khách hàng cực kỳ cao:")
md.append("    * Ví dụ Ad `52521773324529`: Trên Bảng tin mang về 43 tin nhắn và chốt được tới **40 đơn hàng (Tỷ lệ chốt 93%!)**, giúp chi phí đơn trên Bảng tin chỉ **189.644 đ** (rẻ hơn trên Reels là 229.411 đ).")
md.append("    * Ví dụ Ad `120252740442820268`: Chi phí đơn trên Bảng tin chỉ **88.246 đ** (so với 117.174 đ trên Reels).")
md.append("- **Vị trí này cho ra kết quả ổn định không?**")
md.append("  + **ỔN ĐỊNH TUYỆT ĐỐI (Cao nhất tài khoản)**. Bảng tin ra đơn đều đặn **16/16 ngày**, và có độ biến thiên chi phí đơn hàng thấp nhất toàn tài khoản (**CV chỉ 21,9%**). Khách hàng từ Bảng tin luôn là nguồn doanh thu ổn định và chắc chắn nhất.\n")

md.append("#### 3. Nhóm vị trí cần xem xét và loại bỏ")
md.append("- **Facebook Stories**: Đóng vai trò phụ trợ khá tốt cho video ngắn (mang về 32 đơn, giá 235k/đơn, ổn định 12/16 ngày). Có thể giữ lại bật kèm Reels.")
md.append("- **Thước phim trong luồng, Thông báo Facebook, Video kèm phần thưởng, Tự nhiên & biểu ngữ**: Chi phí cao, tỷ lệ đơn thấp hoặc 0 đơn, biến động thất thường. **Nên tắt bỏ hoàn toàn** các vị trí này trong cài đặt nhóm quảng cáo để tập trung tối đa ngân sách vào **Facebook Reels và Bảng tin**.\n")

# Save file
with open('Bao_cao_chi_tiet.md', 'w', encoding='utf-8') as f:
    f.write('\n'.join(md))

print('Markdown report Bao_cao_chi_tiet.md successfully written!')
