# Báo Cáo & Dashboard Tối Ưu Quảng Cáo Facebook - Team 4

> **Bệnh viện Đa khoa Phương Đông - Chiến dịch Quảng Cáo Khoa Sản & Ở Cữ**  
> Dự án tổng hợp, phân tích độ ổn định và trực quan hóa hiệu quả 161 mã quảng cáo Facebook.

---

## 🌟 Trực Tiếp Trải Nghiệm Dashboard Online
- 🚀 **Live Demo (GitHub Pages)**: `https://developer2605.github.io/bao_cao_team4/`
- Hoặc clone repository và mở trực tiếp tệp `index.html` hoặc `Dashboard_Quang_Cao.html` trên trình duyệt bất kỳ (Chrome, Edge, Firefox, Cốc Cốc).

---

## 📊 Cấu Trúc Dashboard (5 Phân Hệ Chuyên Sâu)

1. **Tab 1: Toàn Bộ Mã Quảng Cáo (161 Ads)**
   - Sắp xếp thông minh ưu tiên: Chi phí/Lượt mua (CPA) và Chi phí/Tin nhắn (CPM) từ thấp đến cao.
   - Định dạng chuẩn tiền tệ Việt Nam Đồng (không có số thập phân).
   - Bộ lọc đa chiều: Lọc theo từ khóa ghi chú (`Sản` - 15 Ads, `Ở cữ` - 8 Ads, `Chưa ghi chú` - 138 Ads), lọc độ ổn định (`Ổn định`, `Không ổn định`), tìm kiếm theo Ad ID hoặc hook bài viết.
   - Tích hợp tính năng chỉnh sửa nhanh link bài viết và ghi chú trực tiếp ngay trên từng dòng.

2. **Tab 2: Báo Cáo Phân Tích 2 Từ Khóa "Sản" vs "Ở Cữ"**
   - Phân tích đối đầu trực tiếp (Head-to-head) dựa trên 23 bài đã được điền tay ghi chú.
   - Thống kê chi tiết KPI: Ngân sách, số lượng đơn hàng, tin nhắn, CPA, CPM, tỷ lệ chốt đơn L2/L1.
   - Nhận định chuyên sâu: Nhóm "Ở cữ" có CPA siêu rẻ chỉ 96.556 đ/đơn (-45% so với Sản), nhóm "Sản" có tỷ lệ chốt đơn kỷ lục 47.0%.

3. **Tab 3: Độ Ổn Định Chi Tiết Từng Ngày & Từng Vị Trí**
   - Phân tích ma trận 296 dòng kết hợp giữa từng Mã Quảng Cáo và Vị Trí Hiển Thị theo chuỗi thời gian thực tế.
   - Tích hợp nút bật/tắt trạng thái quảng cáo trực quan kèm ghi chú lý do tắt (Off do bão hòa giá cao, trùng tệp, CPM vọt ngưỡng).

4. **Tab 4: Hiệu Quả Tổng Thể Các Vị Trí Quảng Cáo**
   - Đánh giá 12 vị trí hiển thị trên hệ sinh thái Meta (Facebook Reels, Bảng tin, Instagram Stories, Video trên Bảng tin, Facebook Stories...).
   - Facebook Reels là vị trí mang lại hiệu quả cao nhất: chiếm 66.7% ngân sách và đóng góp tới 72.9% lượng đơn hàng toàn viện với CPA 172.562 đ/đơn.

5. **Tab 5: Đề Xuất Kế Hoạch Ngân Sách Thực Chiến**
   - Phân loại rõ ràng 4 nhóm hành động: Scale ngân sách mạnh (+30% - 50%), Duy trì ổn định, Tối ưu/Giảm ngân sách, Tắt hoàn toàn (Kill ads).

---

## 📁 Danh Mục Tệp Tin Trong Dự Án

- `index.html`: Giao diện Dashboard hoàn chỉnh (tương thích GitHub Pages).
- `Dashboard_Quang_Cao.html`: Bản sao lưu Dashboard độc lập.
- `Bao_cao_quang_cao_Facebook_Cap_Nhat.xlsx`: File Excel báo cáo 6 sheet chuẩn hóa toàn bộ dữ liệu, định dạng số nguyên và tiền tệ VNĐ.
- `Bao_cao_chi_tiet.md`: Báo cáo phân tích chi tiết đầy đủ với biểu đồ Mermaid và số liệu thống kê.

---

## 🛠 Hướng Dẫn Bật GitHub Pages Cho Repository
1. Truy cập vào **Settings** của repository trên GitHub.
2. Chọn mục **Pages** ở thanh menu bên trái.
3. Tại phần **Build and deployment > Branch**, chọn branch `main` và thư mục `/ (root)`.
4. Nhấn **Save**. Sau khoảng 1 - 2 phút, Dashboard sẽ chạy trực tiếp tại đường dẫn `https://developer2605.github.io/bao_cao_team4/`.
