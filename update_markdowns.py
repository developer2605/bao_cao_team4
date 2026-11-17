import pandas as pd
from update_all import df_ad_pos_filtered, df_final_sorted

def fmt_cur(val):
    if pd.isna(val) or val is None or val == 0: return '-'
    return f"{round(val):,d} đ".replace(',', '.')

def fmt_int(val):
    if pd.isna(val) or val is None: return '0'
    return f"{round(val):,d}".replace(',', '.')

def fmt_pct(val):
    if pd.isna(val) or val is None: return '0%'
    return f"{round(val):,d}%"

# Read existing markdown
with open('Bao_cao_chi_tiet.md', 'r', encoding='utf-8') as f:
    existing = f.read()

# Add Section 6
section_6 = []
section_6.append("\n---\n")
section_6.append("## 6. BÁO CÁO ĐỘ ỔN ĐỊNH CỦA TỪNG VỊ TRÍ QUẢNG CÁO THEO TỪNG MÃ QUẢNG CÁO (AD ID x PLACEMENT)")
section_6.append("> [!IMPORTANT]")
section_6.append("> **Ý nghĩa cốt lõi của báo cáo Ad ID x Vị trí**:")
section_6.append("> - Báo cáo này bóc tách dữ liệu đến mức độ vi mô: **Mỗi Ad ID hoạt động trên từng vị trí (Reels, Bảng tin, Stories...) ổn định ra sao**.")
section_6.append("> - Giúp trả lời chính xác: *Một Ad ID có thể hiệu quả trên Reels nhưng có bị đốt tiền lãng phí trên Bảng tin hay không?*")
section_6.append("> - Đã phát hiện **28.738.517 đ** chi phí rò rỉ vào các vị trí phụ không ra đơn, hoàn toàn có thể tiết kiệm bằng cách tắt thủ công các vị trí đó trong nhóm quảng cáo.\n")

section_6.append("### 6.1. Bảng xếp hạng các cặp (Mã Quảng Cáo x Vị Trí) CÓ ĐƠN HÀNG & ỔN ĐỊNH NHẤT")
section_6.append("| Hạng | Mã Quảng Cáo (Ad ID) | Vị Trí Quảng Cáo | Chi Tiêu | Số Tin | Giá / Tin | Số Đơn | Giá / Đơn (CPA) | Chốt L2/L1 | Ngày Ra Đơn | CV Đơn | Đánh Giá Độ Ổn Định |")
section_6.append("| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |")

top_pairs = df_ad_pos_filtered[df_ad_pos_filtered['pur'] >= 5].head(25)
for idx, r in top_pairs.reset_index(drop=True).iterrows():
    cv_str = f"{r['cpp_cv']}%" if r['cpp_cv'] is not None else "-"
    section_6.append(f"| {idx+1} | `{r['ad_id']}` | **{r['placement']}** | {fmt_cur(r['spend'])} | {fmt_int(r['msg'])} | {fmt_cur(r['cpm'])} | {fmt_int(r['pur'])} | **{fmt_cur(r['cpp'])}** | {r['l2_l1']}% | {r['pur_days']}/{r['active_days']} ({r['pur_ratio']}%) | {cv_str} | **{r['stability']}** |")

section_6.append("\n### 6.2. Danh sách các cặp (Mã Quảng Cáo x Vị Trí) RÒ RỈ TIỀN NHIỀU NHẤT (Chi tiêu >= 300k mà 0 ĐƠN)")
section_6.append("*(Cần vào cài đặt nhóm quảng cáo Ad Set để tắt bỏ vị trí này cho Ad ID tương ứng)*\n")
section_6.append("| Mã Quảng Cáo (Ad ID) | Vị Trí Đốt Tiền | Tiền Đã Lãng Phí | Số Tin Nhắn | Số Lượt Mua | Đề Xuất Khắc Phục Ngay |")
section_6.append("| :--- | :--- | :---: | :---: | :---: | :--- |")

zero_pairs = df_ad_pos_filtered[(df_ad_pos_filtered['pur'] == 0) & (df_ad_pos_filtered['spend'] >= 300000)].sort_values('spend', ascending=False)
for _, r in zero_pairs.iterrows():
    section_6.append(f"| `{r['ad_id']}` | **{r['placement']}** | **{fmt_cur(r['spend'])}** | {fmt_int(r['msg'])} | 0 đơn | **Tắt vị trí {r['placement']}** trong Ad Set của mã này để chống rò rỉ ngân sách. |")

section_6_text = "\n".join(section_6)

# Update Bao_cao_chi_tiet.md
full_md = existing + section_6_text
with open('Bao_cao_chi_tiet.md', 'w', encoding='utf-8') as f:
    f.write(full_md)
print('Updated Bao_cao_chi_tiet.md!')

# Update artifact file
artifact_path = r'C:\Users\hungnv\.gemini\antigravity\brain\cb140b8e-59b1-4f14-8019-0f8942e7ecfb\Bao_cao_hieu_qua_quang_cao.md'
with open(artifact_path, 'w', encoding='utf-8') as f:
    f.write(full_md)
print(f'Updated artifact: {artifact_path}!')
