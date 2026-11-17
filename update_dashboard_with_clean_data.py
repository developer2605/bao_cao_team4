# -*- coding: utf-8 -*-
import json
import re
import shutil

from update_all import ads_json_str, pos_json_str

with open('ad_pos_data.json', 'r', encoding='utf-8') as f:
    ad_pos_json_str = f.read()

with open('Dashboard_Quang_Cao.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Update const ADS = [...] and const PLACEMENTS = [...]
# Find const ADS = ...;
p1 = html.find('const ADS = [')
p2 = html.find('const AD_POS = [')
if p1 != -1 and p2 != -1:
    html = html[:p1] + f"const ADS = {ads_json_str};\n    const PLACEMENTS = {pos_json_str};\n    " + html[p2:]
    print("Updated const ADS and const PLACEMENTS in Dashboard_Quang_Cao.html!")
else:
    print("Could not find const ADS bounds!")

# 2. Update keywordFilter options in Tab 1
old_filter_options = """              <option value="ALL">🔍 Tất cả từ khóa (161 Ads)</option>
              <option value="san">🍼 Từ khóa "Sản" (107 Ads - Thai sản / Đi đẻ)</option>
              <option value="ocu">🌿 Từ khóa "Ở cữ" (54 Ads - Nghỉ dưỡng A-Z)</option>"""

new_filter_options = """              <option value="ALL">🔍 Tất cả trạng thái (161 Ads)</option>
              <option value="san">🍼 Đã ghi chú "Sản" (15 Ads)</option>
              <option value="ocu">🌿 Đã ghi chú "Ở cữ" (8 Ads)</option>
              <option value="none">⚪ Chưa có ghi chú (138 Ads)</option>"""

if old_filter_options in html:
    html = html.replace(old_filter_options, new_filter_options)
    print("Updated keywordFilter dropdown options!")
else:
    print("Warning: old_filter_options not matched exactly.")

# 3. Update kwBadge in renderTable
old_kw_badge = """        let kwBadge = '';
        if (ad.keyword === 'ocu') {
          kwBadge = '<span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-teal-500/10 text-teal-600 border border-teal-500/20 whitespace-nowrap">🌿 Ở cữ</span>';
        } else {
          kwBadge = '<span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-blue-500/10 text-blue-600 border border-blue-500/20 whitespace-nowrap">🍼 Sản</span>';
        }"""

new_kw_badge = """        let kwBadge = '';
        if (ad.keyword === 'ocu') {
          kwBadge = '<span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-teal-500/10 text-teal-600 border border-teal-500/20 whitespace-nowrap">🌿 Ở cữ</span>';
        } else if (ad.keyword === 'san') {
          kwBadge = '<span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-blue-500/10 text-blue-600 border border-blue-500/20 whitespace-nowrap">🍼 Sản</span>';
        } else {
          kwBadge = '<span class="text-[10px] text-slate-400 font-mono">-</span>';
        }"""

if old_kw_badge in html:
    html = html.replace(old_kw_badge, new_kw_badge)
    print("Updated kwBadge logic in renderTable!")
else:
    print("Warning: old_kw_badge not matched exactly.")

# 4. Update Tab 2 Content (tab-content-keywords)
# Let's inspect where tab-content-keywords starts and ends
t2_start = '<div id="tab-content-keywords" class="space-y-5 hidden">'
t2_end = '<!-- ========================================================================= -->\n    <!-- TAB 3:'

p_t2_1 = html.find(t2_start)
p_t2_2 = html.find(t2_end)

new_tab2_content = """<div id="tab-content-keywords" class="space-y-5 hidden">
      <!-- Header Banner -->
      <div class="bg-gradient-to-r from-blue-900 via-indigo-900 to-slate-900 rounded-2xl p-6 text-white shadow-lg relative overflow-hidden">
        <div class="relative z-10 space-y-2">
          <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/10 backdrop-blur text-xs font-semibold text-emerald-300">
            <span>✨ Phân Tích Thực Tế Dựa Trên Ghi Chú Bạn Đã Điền Tay</span>
          </div>
          <h2 class="text-2xl font-bold tracking-tight">Báo Cáo Đối Đầu 2 Từ Khóa: "Sản" (15 Ads) vs "Ở Cữ" (8 Ads)</h2>
          <p class="text-xs md:text-sm text-slate-300 max-w-3xl">
            Báo cáo được trích xuất hoàn toàn dựa trên <strong>23 Ad ID bạn đã trực tiếp điền tay ghi chú</strong> trên Dashboard.
            138 Ad ID còn lại giữ nguyên trạng thái <em>Chưa có ghi chú</em> (không suy đoán hoặc lấy thông tin từ các sheet ngoài 3 sheet gốc).
          </p>
        </div>
      </div>

      <!-- Head-to-Head KPI Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
        <!-- Card 1: Sản (15 Ads) -->
        <div class="bg-[var(--card)] border border-blue-500/30 rounded-2xl p-5 space-y-4 shadow-sm relative overflow-hidden">
          <div class="flex items-center justify-between border-b border-[var(--border)] pb-3">
            <div class="flex items-center gap-2.5">
              <span class="p-2.5 rounded-xl bg-blue-500/10 text-blue-600 text-lg">🍼</span>
              <div>
                <h3 class="font-bold text-base text-[var(--foreground)]">Từ Khóa "SẢN"</h3>
                <p class="text-xs text-[var(--muted-foreground)]">15 Ads được bạn gắn nhãn "Sản"</p>
              </div>
            </div>
            <span class="px-2.5 py-1 rounded-full text-xs font-bold bg-blue-500/10 text-blue-600">15 Ads (65.2%)</span>
          </div>

          <div class="grid grid-cols-2 sm:grid-cols-3 gap-3 text-center">
            <div class="bg-[var(--background)] p-3 rounded-xl border border-[var(--border)]">
              <span class="text-[11px] text-[var(--muted-foreground)]">Tổng Chi Tiêu</span>
              <p class="text-base font-bold text-[var(--foreground)] mt-0.5">96.365.112 đ</p>
              <span class="text-[10px] text-blue-600 font-medium">70.6% ngân sách</span>
            </div>
            <div class="bg-[var(--background)] p-3 rounded-xl border border-[var(--border)]">
              <span class="text-[11px] text-[var(--muted-foreground)]">Lượt Mua (Đơn)</span>
              <p class="text-base font-bold text-emerald-600 mt-0.5">547 đơn</p>
              <span class="text-[10px] text-emerald-600 font-medium">56.8% tổng đơn</span>
            </div>
            <div class="bg-[var(--background)] p-3 rounded-xl border border-[var(--border)]">
              <span class="text-[11px] text-[var(--muted-foreground)]">Chi Phí / Đơn (CPA)</span>
              <p class="text-base font-bold text-blue-600 mt-0.5">176.170 đ</p>
              <span class="text-[10px] text-slate-500 font-medium">Trung bình ổn định</span>
            </div>
            <div class="bg-[var(--background)] p-3 rounded-xl border border-[var(--border)]">
              <span class="text-[11px] text-[var(--muted-foreground)]">Tin Nhắn (L1)</span>
              <p class="text-base font-bold text-[var(--foreground)] mt-0.5">1.163 tin</p>
              <span class="text-[10px] text-[var(--muted-foreground)]">Khách hỏi gói sinh</span>
            </div>
            <div class="bg-[var(--background)] p-3 rounded-xl border border-[var(--border)]">
              <span class="text-[11px] text-[var(--muted-foreground)]">Giá / Tin (CPM)</span>
              <p class="text-base font-bold text-slate-700 mt-0.5">82.859 đ</p>
              <span class="text-[10px] text-slate-500 font-medium">Độ chốt cao</span>
            </div>
            <div class="bg-[var(--background)] p-3 rounded-xl border border-[var(--border)]">
              <span class="text-[11px] text-[var(--muted-foreground)]">Tỷ Lệ Chốt (L2/L1)</span>
              <p class="text-base font-bold text-purple-600 mt-0.5">47.0%</p>
              <span class="text-[10px] text-purple-600 font-medium">Chốt đơn rất cao</span>
            </div>
          </div>
        </div>

        <!-- Card 2: Ở cữ (8 Ads) -->
        <div class="bg-[var(--card)] border border-teal-500/30 rounded-2xl p-5 space-y-4 shadow-sm relative overflow-hidden">
          <div class="flex items-center justify-between border-b border-[var(--border)] pb-3">
            <div class="flex items-center gap-2.5">
              <span class="p-2.5 rounded-xl bg-teal-500/10 text-teal-600 text-lg">🌿</span>
              <div>
                <h3 class="font-bold text-base text-[var(--foreground)]">Từ Khóa "Ở CỮ"</h3>
                <p class="text-xs text-[var(--muted-foreground)]">8 Ads được bạn gắn nhãn "Ở cữ"</p>
              </div>
            </div>
            <span class="px-2.5 py-1 rounded-full text-xs font-bold bg-teal-500/10 text-teal-600">8 Ads (34.8%)</span>
          </div>

          <div class="grid grid-cols-2 sm:grid-cols-3 gap-3 text-center">
            <div class="bg-[var(--background)] p-3 rounded-xl border border-[var(--border)]">
              <span class="text-[11px] text-[var(--muted-foreground)]">Tổng Chi Tiêu</span>
              <p class="text-base font-bold text-[var(--foreground)] mt-0.5">40.167.154 đ</p>
              <span class="text-[10px] text-teal-600 font-medium">29.4% ngân sách</span>
            </div>
            <div class="bg-[var(--background)] p-3 rounded-xl border border-[var(--border)]">
              <span class="text-[11px] text-[var(--muted-foreground)]">Lượt Mua (Đơn)</span>
              <p class="text-base font-bold text-emerald-600 mt-0.5">416 đơn</p>
              <span class="text-[10px] text-emerald-600 font-medium">43.2% tổng đơn</span>
            </div>
            <div class="bg-[var(--background)] p-3 rounded-xl border border-[var(--border)]">
              <span class="text-[11px] text-[var(--muted-foreground)]">Chi Phí / Đơn (CPA)</span>
              <p class="text-base font-bold text-emerald-600 mt-0.5">96.556 đ</p>
              <span class="text-[10px] text-emerald-600 font-bold">Rẻ hơn 45% (-45%)</span>
            </div>
            <div class="bg-[var(--background)] p-3 rounded-xl border border-[var(--border)]">
              <span class="text-[11px] text-[var(--muted-foreground)]">Tin Nhắn (L1)</span>
              <p class="text-base font-bold text-[var(--foreground)] mt-0.5">1.243 tin</p>
              <span class="text-[10px] text-teal-600 font-medium">Hút nhiều tin nhắn</span>
            </div>
            <div class="bg-[var(--background)] p-3 rounded-xl border border-[var(--border)]">
              <span class="text-[11px] text-[var(--muted-foreground)]">Giá / Tin (CPM)</span>
              <p class="text-base font-bold text-teal-600 mt-0.5">32.315 đ</p>
              <span class="text-[10px] text-teal-600 font-bold">Giá tin siêu rẻ!</span>
            </div>
            <div class="bg-[var(--background)] p-3 rounded-xl border border-[var(--border)]">
              <span class="text-[11px] text-[var(--muted-foreground)]">Tỷ Lệ Chốt (L2/L1)</span>
              <p class="text-base font-bold text-slate-700 mt-0.5">33.5%</p>
              <span class="text-[10px] text-slate-500 font-medium">Khách cần tư vấn thêm</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Detail Tables for 15 Sản Ads & 8 Ở Cữ Ads -->
      <div class="space-y-4">
        <!-- Table 1: 15 Sản Ads -->
        <div class="bg-[var(--card)] border border-[var(--border)] rounded-2xl overflow-hidden shadow-sm">
          <div class="p-4 bg-blue-50/50 border-b border-[var(--border)] flex items-center justify-between">
            <div class="flex items-center gap-2">
              <span class="text-blue-600 font-bold">🍼</span>
              <h3 class="font-bold text-sm text-[var(--foreground)]">Danh Sách 15 Mã Quảng Cáo Được Bạn Điền Ghi Chú "Sản"</h3>
            </div>
            <span class="text-xs font-semibold text-blue-600">Tổng: 547 đơn · 96.3M chi tiêu</span>
          </div>

          <div class="overflow-x-auto">
            <table class="w-full text-xs text-left border-collapse">
              <thead class="bg-[var(--background)] text-[var(--muted-foreground)] border-b border-[var(--border)] uppercase font-semibold text-[11px]">
                <tr>
                  <th class="py-2.5 px-3">STT</th>
                  <th class="py-2.5 px-3">Mã Quảng Cáo (Ad ID)</th>
                  <th class="py-2.5 px-3 text-right">Chi Tiêu</th>
                  <th class="py-2.5 px-2.5 text-center">Tin Nhắn</th>
                  <th class="py-2.5 px-3 text-right">Giá/Tin</th>
                  <th class="py-2.5 px-2.5 text-center font-bold text-emerald-600">Đơn</th>
                  <th class="py-2.5 px-3 text-right font-bold text-blue-600">CPA/Đơn</th>
                  <th class="py-2.5 px-3">Ghi Chú Thực Tế Điền Tay</th>
                  <th class="py-2.5 px-3 text-center">Link Bài Viết</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-[var(--border)]">
                <tr class="hover:bg-[var(--accent)]/50 transition">
                  <td class="py-2.5 px-3 font-mono text-center">1</td>
                  <td class="py-2.5 px-3 font-mono font-bold text-blue-600 cursor-pointer hover:underline" onclick="openModal('52517259236329')">52517259236329</td>
                  <td class="py-2.5 px-3 text-right font-mono font-medium">12.743.197 đ</td>
                  <td class="py-2.5 px-2.5 text-center font-mono">114</td>
                  <td class="py-2.5 px-3 text-right font-mono">111.782 đ</td>
                  <td class="py-2.5 px-2.5 text-center font-mono font-bold text-emerald-600">71</td>
                  <td class="py-2.5 px-3 text-right font-mono font-bold text-blue-600">179.482 đ</td>
                  <td class="py-2.5 px-3 font-medium text-slate-800">Sản - Check theo ngày</td>
                  <td class="py-2.5 px-3 text-center"><a href="https://www.facebook.com/reel/1449701503257097" target="_blank" class="text-blue-600 hover:underline">Mở Reel ↗</a></td>
                </tr>
                <tr class="hover:bg-[var(--accent)]/50 transition">
                  <td class="py-2.5 px-3 font-mono text-center">2</td>
                  <td class="py-2.5 px-3 font-mono font-bold text-blue-600 cursor-pointer hover:underline" onclick="openModal('52521773324529')">52521773324529</td>
                  <td class="py-2.5 px-3 text-right font-mono font-medium">12.180.559 đ</td>
                  <td class="py-2.5 px-2.5 text-center font-mono">66</td>
                  <td class="py-2.5 px-3 text-right font-mono">184.554 đ</td>
                  <td class="py-2.5 px-2.5 text-center font-mono font-bold text-emerald-600">58</td>
                  <td class="py-2.5 px-3 text-right font-mono font-bold text-blue-600">210.010 đ</td>
                  <td class="py-2.5 px-3 font-medium text-slate-800">Sản - MĐTC</td>
                  <td class="py-2.5 px-3 text-center"><a href="https://www.facebook.com/reel/938858948956474" target="_blank" class="text-blue-600 hover:underline">Mở Reel ↗</a></td>
                </tr>
                <tr class="hover:bg-[var(--accent)]/50 transition">
                  <td class="py-2.5 px-3 font-mono text-center">3</td>
                  <td class="py-2.5 px-3 font-mono font-bold text-blue-600 cursor-pointer hover:underline" onclick="openModal('52642653160220')">52642653160220</td>
                  <td class="py-2.5 px-3 text-right font-mono font-medium">8.376.760 đ</td>
                  <td class="py-2.5 px-2.5 text-center font-mono">110</td>
                  <td class="py-2.5 px-3 text-right font-mono">76.152 đ</td>
                  <td class="py-2.5 px-2.5 text-center font-mono font-bold text-emerald-600">55</td>
                  <td class="py-2.5 px-3 text-right font-mono font-bold text-blue-600">152.305 đ</td>
                  <td class="py-2.5 px-3 font-medium text-slate-800">Sản - Bị đánh spam L3</td>
                  <td class="py-2.5 px-3 text-center"><a href="https://www.facebook.com/reel/3854749188000584" target="_blank" class="text-blue-600 hover:underline">Mở Reel ↗</a></td>
                </tr>
                <tr class="hover:bg-[var(--accent)]/50 transition">
                  <td class="py-2.5 px-3 font-mono text-center">4</td>
                  <td class="py-2.5 px-3 font-mono font-bold text-blue-600 cursor-pointer hover:underline" onclick="openModal('120249153813990532')">120249153813990532</td>
                  <td class="py-2.5 px-3 text-right font-mono font-medium">3.932.804 đ</td>
                  <td class="py-2.5 px-2.5 text-center font-mono">144</td>
                  <td class="py-2.5 px-3 text-right font-mono">27.311 đ</td>
                  <td class="py-2.5 px-2.5 text-center font-mono font-bold text-emerald-600">53</td>
                  <td class="py-2.5 px-3 text-right font-mono font-bold text-blue-600">74.204 đ</td>
                  <td class="py-2.5 px-3 font-medium text-slate-800">Sản - Babymoon</td>
                  <td class="py-2.5 px-3 text-center"><a href="https://www.facebook.com/reel/1449701503257097" target="_blank" class="text-blue-600 hover:underline">Mở Reel ↗</a></td>
                </tr>
                <tr class="hover:bg-[var(--accent)]/50 transition">
                  <td class="py-2.5 px-3 font-mono text-center">5</td>
                  <td class="py-2.5 px-3 font-mono font-bold text-blue-600 cursor-pointer hover:underline" onclick="openModal('52642651596220')">52642651596220</td>
                  <td class="py-2.5 px-3 text-right font-mono font-medium">8.415.517 đ</td>
                  <td class="py-2.5 px-2.5 text-center font-mono">104</td>
                  <td class="py-2.5 px-3 text-right font-mono">80.918 đ</td>
                  <td class="py-2.5 px-2.5 text-center font-mono font-bold text-emerald-600">49</td>
                  <td class="py-2.5 px-3 text-right font-mono font-bold text-blue-600">171.745 đ</td>
                  <td class="py-2.5 px-3 font-medium text-slate-800">Sản - Bị đánh Spam L3</td>
                  <td class="py-2.5 px-3 text-center"><a href="https://www.facebook.com/reel/1403115735201925" target="_blank" class="text-blue-600 hover:underline">Mở Reel ↗</a></td>
                </tr>
                <tr class="hover:bg-[var(--accent)]/50 transition">
                  <td class="py-2.5 px-3 font-mono text-center">6</td>
                  <td class="py-2.5 px-3 font-mono font-bold text-blue-600 cursor-pointer hover:underline" onclick="openModal('52521772982929')">52521772982929</td>
                  <td class="py-2.5 px-3 text-right font-mono font-medium">8.739.924 đ</td>
                  <td class="py-2.5 px-2.5 text-center font-mono">81</td>
                  <td class="py-2.5 px-3 text-right font-mono">107.899 đ</td>
                  <td class="py-2.5 px-2.5 text-center font-mono font-bold text-emerald-600">37</td>
                  <td class="py-2.5 px-3 text-right font-mono font-bold text-blue-600">236.214 đ</td>
                  <td class="py-2.5 px-3 font-medium text-slate-800">Sản - Bị đánh spam L3</td>
                  <td class="py-2.5 px-3 text-center"><a href="https://www.facebook.com/reel/766312903186433/#" target="_blank" class="text-blue-600 hover:underline">Mở Reel ↗</a></td>
                </tr>
                <tr class="hover:bg-[var(--accent)]/50 transition">
                  <td class="py-2.5 px-3 font-mono text-center">7</td>
                  <td class="py-2.5 px-3 font-mono font-bold text-blue-600 cursor-pointer hover:underline" onclick="openModal('120249153925720532')">120249153925720532</td>
                  <td class="py-2.5 px-3 text-right font-mono font-medium">6.268.535 đ</td>
                  <td class="py-2.5 px-2.5 text-center font-mono">111</td>
                  <td class="py-2.5 px-3 text-right font-mono">56.473 đ</td>
                  <td class="py-2.5 px-2.5 text-center font-mono font-bold text-emerald-600">35</td>
                  <td class="py-2.5 px-3 text-right font-mono font-bold text-blue-600">179.101 đ</td>
                  <td class="py-2.5 px-3 font-medium text-slate-800">Sản - Bị đánh Spam L3</td>
                  <td class="py-2.5 px-3 text-center"><a href="https://www.facebook.com/reel/1288763059425415" target="_blank" class="text-blue-600 hover:underline">Mở Reel ↗</a></td>
                </tr>
                <tr class="hover:bg-[var(--accent)]/50 transition">
                  <td class="py-2.5 px-3 font-mono text-center">8</td>
                  <td class="py-2.5 px-3 font-mono font-bold text-blue-600 cursor-pointer hover:underline" onclick="openModal('52542791483096')">52542791483096</td>
                  <td class="py-2.5 px-3 text-right font-mono font-medium">6.654.383 đ</td>
                  <td class="py-2.5 px-2.5 text-center font-mono">48</td>
                  <td class="py-2.5 px-3 text-right font-mono">138.633 đ</td>
                  <td class="py-2.5 px-2.5 text-center font-mono font-bold text-emerald-600">31</td>
                  <td class="py-2.5 px-3 text-right font-mono font-bold text-blue-600">214.658 đ</td>
                  <td class="py-2.5 px-3 font-medium text-slate-800">Sản</td>
                  <td class="py-2.5 px-3 text-center"><a href="https://www.facebook.com/reel/1288763059425415" target="_blank" class="text-blue-600 hover:underline">Mở Reel ↗</a></td>
                </tr>
                <tr class="hover:bg-[var(--accent)]/50 transition">
                  <td class="py-2.5 px-3 font-mono text-center">9</td>
                  <td class="py-2.5 px-3 font-mono font-bold text-blue-600 cursor-pointer hover:underline" onclick="openModal('52534409199296')">52534409199296</td>
                  <td class="py-2.5 px-3 text-right font-mono font-medium">6.979.494 đ</td>
                  <td class="py-2.5 px-2.5 text-center font-mono">139</td>
                  <td class="py-2.5 px-3 text-right font-mono">50.212 đ</td>
                  <td class="py-2.5 px-2.5 text-center font-mono font-bold text-emerald-600">28</td>
                  <td class="py-2.5 px-3 text-right font-mono font-bold text-blue-600">249.268 đ</td>
                  <td class="py-2.5 px-3 font-medium text-slate-800">Sản</td>
                  <td class="py-2.5 px-3 text-center"><a href="https://www.facebook.com/reel/859087953745426" target="_blank" class="text-blue-600 hover:underline">Mở Reel ↗</a></td>
                </tr>
                <tr class="hover:bg-[var(--accent)]/50 transition">
                  <td class="py-2.5 px-3 font-mono text-center">10</td>
                  <td class="py-2.5 px-3 font-mono font-bold text-blue-600 cursor-pointer hover:underline" onclick="openModal('120249153839980532')">120249153839980532</td>
                  <td class="py-2.5 px-3 text-right font-mono font-medium">2.459.433 đ</td>
                  <td class="py-2.5 px-2.5 text-center font-mono">66</td>
                  <td class="py-2.5 px-3 text-right font-mono">37.264 đ</td>
                  <td class="py-2.5 px-2.5 text-center font-mono font-bold text-emerald-600">26</td>
                  <td class="py-2.5 px-3 text-right font-mono font-bold text-blue-600">94.594 đ</td>
                  <td class="py-2.5 px-3 font-medium text-slate-800">Sản</td>
                  <td class="py-2.5 px-3 text-center"><a href="https://www.facebook.com/reel/1211094267613179" target="_blank" class="text-blue-600 hover:underline">Mở Reel ↗</a></td>
                </tr>
                <tr class="hover:bg-[var(--accent)]/50 transition">
                  <td class="py-2.5 px-3 font-mono text-center">11</td>
                  <td class="py-2.5 px-3 font-mono font-bold text-blue-600 cursor-pointer hover:underline" onclick="openModal('52521772982729')">52521772982729</td>
                  <td class="py-2.5 px-3 text-right font-mono font-medium">4.407.057 đ</td>
                  <td class="py-2.5 px-2.5 text-center font-mono">36</td>
                  <td class="py-2.5 px-3 text-right font-mono">122.418 đ</td>
                  <td class="py-2.5 px-2.5 text-center font-mono font-bold text-emerald-600">24</td>
                  <td class="py-2.5 px-3 text-right font-mono font-bold text-blue-600">183.627 đ</td>
                  <td class="py-2.5 px-3 font-medium text-slate-800">Sản</td>
                  <td class="py-2.5 px-3 text-center"><a href="https://www.facebook.com/reel/988541016912103" target="_blank" class="text-blue-600 hover:underline">Mở Reel ↗</a></td>
                </tr>
                <tr class="hover:bg-[var(--accent)]/50 transition">
                  <td class="py-2.5 px-3 font-mono text-center">12</td>
                  <td class="py-2.5 px-3 font-mono font-bold text-blue-600 cursor-pointer hover:underline" onclick="openModal('120249153839950532')">120249153839950532</td>
                  <td class="py-2.5 px-3 text-right font-mono font-medium">1.595.845 đ</td>
                  <td class="py-2.5 px-2.5 text-center font-mono">49</td>
                  <td class="py-2.5 px-3 text-right font-mono">32.568 đ</td>
                  <td class="py-2.5 px-2.5 text-center font-mono font-bold text-emerald-600">24</td>
                  <td class="py-2.5 px-3 text-right font-mono font-bold text-blue-600">66.494 đ</td>
                  <td class="py-2.5 px-3 font-medium text-slate-800">Sản</td>
                  <td class="py-2.5 px-3 text-center"><a href="https://www.facebook.com/reel/938858948956474" target="_blank" class="text-blue-600 hover:underline">Mở Reel ↗</a></td>
                </tr>
                <tr class="hover:bg-[var(--accent)]/50 transition">
                  <td class="py-2.5 px-3 font-mono text-center">13</td>
                  <td class="py-2.5 px-3 font-mono font-bold text-blue-600 cursor-pointer hover:underline" onclick="openModal('52542793235096')">52542793235096</td>
                  <td class="py-2.5 px-3 text-right font-mono font-medium">5.169.093 đ</td>
                  <td class="py-2.5 px-2.5 text-center font-mono">31</td>
                  <td class="py-2.5 px-3 text-right font-mono">166.745 đ</td>
                  <td class="py-2.5 px-2.5 text-center font-mono font-bold text-emerald-600">21</td>
                  <td class="py-2.5 px-3 text-right font-mono font-bold text-blue-600">246.147 đ</td>
                  <td class="py-2.5 px-3 font-medium text-slate-800">Sản</td>
                  <td class="py-2.5 px-3 text-center"><a href="https://www.facebook.com/reel/2520909615077120" target="_blank" class="text-blue-600 hover:underline">Mở Reel ↗</a></td>
                </tr>
                <tr class="hover:bg-[var(--accent)]/50 transition">
                  <td class="py-2.5 px-3 font-mono text-center">14</td>
                  <td class="py-2.5 px-3 font-mono font-bold text-blue-600 cursor-pointer hover:underline" onclick="openModal('120249153925760532')">120249153925760532</td>
                  <td class="py-2.5 px-3 text-right font-mono font-medium">4.962.771 đ</td>
                  <td class="py-2.5 px-2.5 text-center font-mono">45</td>
                  <td class="py-2.5 px-3 text-right font-mono">110.284 đ</td>
                  <td class="py-2.5 px-2.5 text-center font-mono font-bold text-emerald-600">19</td>
                  <td class="py-2.5 px-3 text-right font-mono font-bold text-blue-600">261.198 đ</td>
                  <td class="py-2.5 px-3 font-medium text-slate-800">Sản</td>
                  <td class="py-2.5 px-3 text-center"><a href="https://www.facebook.com/reel/1013949657861950" target="_blank" class="text-blue-600 hover:underline">Mở Reel ↗</a></td>
                </tr>
                <tr class="hover:bg-[var(--accent)]/50 transition">
                  <td class="py-2.5 px-3 font-mono text-center">15</td>
                  <td class="py-2.5 px-3 font-mono font-bold text-blue-600 cursor-pointer hover:underline" onclick="openModal('52542791483496')">52542791483496</td>
                  <td class="py-2.5 px-3 text-right font-mono font-medium">3.479.740 đ</td>
                  <td class="py-2.5 px-2.5 text-center font-mono">19</td>
                  <td class="py-2.5 px-3 text-right font-mono">183.144 đ</td>
                  <td class="py-2.5 px-2.5 text-center font-mono font-bold text-emerald-600">16</td>
                  <td class="py-2.5 px-3 text-right font-mono font-bold text-blue-600">217.484 đ</td>
                  <td class="py-2.5 px-3 font-medium text-slate-800">Sản</td>
                  <td class="py-2.5 px-3 text-center"><a href="https://www.facebook.com/reel/1288763059425415" target="_blank" class="text-blue-600 hover:underline">Mở Reel ↗</a></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Table 2: 8 Ở Cữ Ads -->
        <div class="bg-[var(--card)] border border-[var(--border)] rounded-2xl overflow-hidden shadow-sm">
          <div class="p-4 bg-teal-50/50 border-b border-[var(--border)] flex items-center justify-between">
            <div class="flex items-center gap-2">
              <span class="text-teal-600 font-bold">🌿</span>
              <h3 class="font-bold text-sm text-[var(--foreground)]">Danh Sách 8 Mã Quảng Cáo Được Bạn Điền Ghi Chú "Ở Cữ"</h3>
            </div>
            <span class="text-xs font-semibold text-teal-600">Tổng: 416 đơn · 40.1M chi tiêu · CPA TB 96.5k</span>
          </div>

          <div class="overflow-x-auto">
            <table class="w-full text-xs text-left border-collapse">
              <thead class="bg-[var(--background)] text-[var(--muted-foreground)] border-b border-[var(--border)] uppercase font-semibold text-[11px]">
                <tr>
                  <th class="py-2.5 px-3">STT</th>
                  <th class="py-2.5 px-3">Mã Quảng Cáo (Ad ID)</th>
                  <th class="py-2.5 px-3 text-right">Chi Tiêu</th>
                  <th class="py-2.5 px-2.5 text-center">Tin Nhắn</th>
                  <th class="py-2.5 px-3 text-right">Giá/Tin</th>
                  <th class="py-2.5 px-2.5 text-center font-bold text-emerald-600">Đơn</th>
                  <th class="py-2.5 px-3 text-right font-bold text-teal-600">CPA/Đơn</th>
                  <th class="py-2.5 px-3">Ghi Chú Thực Tế Điền Tay</th>
                  <th class="py-2.5 px-3 text-center">Link Bài Viết</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-[var(--border)]">
                <tr class="hover:bg-[var(--accent)]/50 transition">
                  <td class="py-2.5 px-3 font-mono text-center">1</td>
                  <td class="py-2.5 px-3 font-mono font-bold text-teal-600 cursor-pointer hover:underline" onclick="openModal('120249153794660532')">120249153794660532</td>
                  <td class="py-2.5 px-3 text-right font-mono font-medium">7.942.652 đ</td>
                  <td class="py-2.5 px-2.5 text-center font-mono">397</td>
                  <td class="py-2.5 px-3 text-right font-mono">20.007 đ</td>
                  <td class="py-2.5 px-2.5 text-center font-mono font-bold text-emerald-600">130</td>
                  <td class="py-2.5 px-3 text-right font-mono font-bold text-teal-600">61.097 đ</td>
                  <td class="py-2.5 px-3 font-medium text-slate-800">Ở Cữ - Bị đánh Spam L3</td>
                  <td class="py-2.5 px-3 text-center"><a href="https://www.facebook.com/reel/1578116963507679/#" target="_blank" class="text-blue-600 hover:underline">Mở Reel ↗</a></td>
                </tr>
                <tr class="hover:bg-[var(--accent)]/50 transition">
                  <td class="py-2.5 px-3 font-mono text-center">2</td>
                  <td class="py-2.5 px-3 font-mono font-bold text-teal-600 cursor-pointer hover:underline" onclick="openModal('120249153839930532')">120249153839930532</td>
                  <td class="py-2.5 px-3 text-right font-mono font-medium">6.295.332 đ</td>
                  <td class="py-2.5 px-2.5 text-center font-mono">232</td>
                  <td class="py-2.5 px-3 text-right font-mono">27.135 đ</td>
                  <td class="py-2.5 px-2.5 text-center font-mono font-bold text-emerald-600">98</td>
                  <td class="py-2.5 px-3 text-right font-mono font-bold text-teal-600">64.238 đ</td>
                  <td class="py-2.5 px-3 font-medium text-slate-800">Ở cữ bị đánh Spam L3</td>
                  <td class="py-2.5 px-3 text-center"><a href="https://www.facebook.com/reel/1345695507319188/#" target="_blank" class="text-blue-600 hover:underline">Mở Reel ↗</a></td>
                </tr>
                <tr class="hover:bg-[var(--accent)]/50 transition">
                  <td class="py-2.5 px-3 font-mono text-center">3</td>
                  <td class="py-2.5 px-3 font-mono font-bold text-teal-600 cursor-pointer hover:underline" onclick="openModal('52550106995296')">52550106995296</td>
                  <td class="py-2.5 px-3 text-right font-mono font-medium">2.805.684 đ</td>
                  <td class="py-2.5 px-2.5 text-center font-mono">121</td>
                  <td class="py-2.5 px-3 text-right font-mono">23.187 đ</td>
                  <td class="py-2.5 px-2.5 text-center font-mono font-bold text-emerald-600">43</td>
                  <td class="py-2.5 px-3 text-right font-mono font-bold text-teal-600">65.248 đ</td>
                  <td class="py-2.5 px-3 font-medium text-slate-800">Ở cữ</td>
                  <td class="py-2.5 px-3 text-center"><a href="https://www.facebook.com/reel/1610174230075281" target="_blank" class="text-blue-600 hover:underline">Mở Reel ↗</a></td>
                </tr>
                <tr class="hover:bg-[var(--accent)]/50 transition">
                  <td class="py-2.5 px-3 font-mono text-center">4</td>
                  <td class="py-2.5 px-3 font-mono font-bold text-teal-600 cursor-pointer hover:underline" onclick="openModal('120248174416610532')">120248174416610532</td>
                  <td class="py-2.5 px-3 text-right font-mono font-medium">5.825.124 đ</td>
                  <td class="py-2.5 px-2.5 text-center font-mono">117</td>
                  <td class="py-2.5 px-3 text-right font-mono">49.787 đ</td>
                  <td class="py-2.5 px-2.5 text-center font-mono font-bold text-emerald-600">41</td>
                  <td class="py-2.5 px-3 text-right font-mono font-bold text-teal-600">142.076 đ</td>
                  <td class="py-2.5 px-3 font-medium text-slate-800">Ở cữ</td>
                  <td class="py-2.5 px-3 text-center"><a href="https://www.facebook.com/reel/1345695507319188" target="_blank" class="text-blue-600 hover:underline">Mở Reel ↗</a></td>
                </tr>
                <tr class="hover:bg-[var(--accent)]/50 transition">
                  <td class="py-2.5 px-3 font-mono text-center">5</td>
                  <td class="py-2.5 px-3 font-mono font-bold text-teal-600 cursor-pointer hover:underline" onclick="openModal('120252740442820268')">120252740442820268</td>
                  <td class="py-2.5 px-3 text-right font-mono font-medium">3.672.755 đ</td>
                  <td class="py-2.5 px-2.5 text-center font-mono">146</td>
                  <td class="py-2.5 px-3 text-right font-mono">25.156 đ</td>
                  <td class="py-2.5 px-2.5 text-center font-mono font-bold text-emerald-600">36</td>
                  <td class="py-2.5 px-3 text-right font-mono font-bold text-teal-600">102.021 đ</td>
                  <td class="py-2.5 px-3 font-medium text-slate-800">Ở cữ</td>
                  <td class="py-2.5 px-3 text-center"><a href="https://www.facebook.com/reel/1610174230075281" target="_blank" class="text-blue-600 hover:underline">Mở Reel ↗</a></td>
                </tr>
                <tr class="hover:bg-[var(--accent)]/50 transition">
                  <td class="py-2.5 px-3 font-mono text-center">6</td>
                  <td class="py-2.5 px-3 font-mono font-bold text-teal-600 cursor-pointer hover:underline" onclick="openModal('52528421829729')">52528421829729</td>
                  <td class="py-2.5 px-3 text-right font-mono font-medium">5.613.142 đ</td>
                  <td class="py-2.5 px-2.5 text-center font-mono">83</td>
                  <td class="py-2.5 px-3 text-right font-mono">67.628 đ</td>
                  <td class="py-2.5 px-2.5 text-center font-mono font-bold text-emerald-600">26</td>
                  <td class="py-2.5 px-3 text-right font-mono font-bold text-teal-600">215.890 đ</td>
                  <td class="py-2.5 px-3 font-medium text-slate-800">Ở cữ</td>
                  <td class="py-2.5 px-3 text-center"><a href="https://www.facebook.com/reel/2194647091004626" target="_blank" class="text-blue-600 hover:underline">Mở Reel ↗</a></td>
                </tr>
                <tr class="hover:bg-[var(--accent)]/50 transition">
                  <td class="py-2.5 px-3 font-mono text-center">7</td>
                  <td class="py-2.5 px-3 font-mono font-bold text-teal-600 cursor-pointer hover:underline" onclick="openModal('120248174396270532')">120248174396270532</td>
                  <td class="py-2.5 px-3 text-right font-mono font-medium">4.366.056 đ</td>
                  <td class="py-2.5 px-2.5 text-center font-mono">68</td>
                  <td class="py-2.5 px-3 text-right font-mono">64.207 đ</td>
                  <td class="py-2.5 px-2.5 text-center font-mono font-bold text-emerald-600">24</td>
                  <td class="py-2.5 px-3 text-right font-mono font-bold text-teal-600">181.919 đ</td>
                  <td class="py-2.5 px-3 font-medium text-slate-800">Ở cữ</td>
                  <td class="py-2.5 px-3 text-center"><a href="https://www.facebook.com/reel/2028410744652119" target="_blank" class="text-blue-600 hover:underline">Mở Reel ↗</a></td>
                </tr>
                <tr class="hover:bg-[var(--accent)]/50 transition">
                  <td class="py-2.5 px-3 font-mono text-center">8</td>
                  <td class="py-2.5 px-3 font-mono font-bold text-teal-600 cursor-pointer hover:underline" onclick="openModal('120249223441840268')">120249223441840268</td>
                  <td class="py-2.5 px-3 text-right font-mono font-medium">3.646.409 đ</td>
                  <td class="py-2.5 px-2.5 text-center font-mono">79</td>
                  <td class="py-2.5 px-3 text-right font-mono">46.157 đ</td>
                  <td class="py-2.5 px-2.5 text-center font-mono font-bold text-emerald-600">18</td>
                  <td class="py-2.5 px-3 text-right font-mono font-bold text-teal-600">202.578 đ</td>
                  <td class="py-2.5 px-3 font-medium text-slate-800">Ở Cữ</td>
                  <td class="py-2.5 px-3 text-center"><a href="https://www.facebook.com/reel/1610174230075281" target="_blank" class="text-blue-600 hover:underline">Mở Reel ↗</a></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Actionable Insights Card -->
      <div class="bg-[var(--card)] border border-[var(--border)] rounded-2xl p-5 space-y-3 shadow-sm">
        <h3 class="font-bold text-sm text-[var(--foreground)] flex items-center gap-2">
          <span>💡</span> Nhận Định Hành Động Dựa Trên 23 Bài Đã Được Điền Ghi Chú:
        </h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
          <div class="p-3 bg-teal-50/50 rounded-xl border border-teal-200/50 space-y-1">
            <h4 class="font-bold text-teal-800">1. Ưu thế vượt trội của nhóm "Ở Cữ":</h4>
            <p class="text-teal-900 leading-relaxed">
              Nhóm "Ở cữ" có CPA trung bình chỉ <strong>96.556 đ/đơn</strong> (rẻ hơn 45% so với Sản), giá tin nhắn chỉ <strong>32.315 đ/tin</strong>.
              Đặc biệt ID <code>120249153794660532</code> và <code>120249153839930532</code> là 2 cỗ máy tạo đơn lớn nhất với CPA siêu rẻ (~61k - 64k).
            </p>
          </div>
          <div class="p-3 bg-blue-50/50 rounded-xl border border-blue-200/50 space-y-1">
            <h4 class="font-bold text-blue-800">2. Độ chuyển đổi chắc chắn của nhóm "Sản":</h4>
            <p class="text-blue-900 leading-relaxed">
              Nhóm "Sản" đạt tỷ lệ chốt đơn tới <strong>47.0%</strong> (cứ ~2 tin nhắn là có 1 đơn chốt).
              Dù giá tin nhắn cao hơn, mẹ bầu quan tâm gói sinh có quyết định mua hàng dứt khoát hơn.
            </p>
          </div>
        </div>
      </div>
    </div>\n\n    """

if p_t2_1 != -1 and p_t2_2 != -1:
    html = html[:p_t2_1] + new_tab2_content + html[p_t2_2:]
    print("Updated Tab 2 content successfully!")
else:
    print(f"Tab 2 bounds error: {p_t2_1}, {p_t2_2}")

# 5. Update initialAnnotations pre-seeding in JS
# Make sure initialAnnotations uses user_manual_notes.json directly!
with open('user_manual_notes.json', 'r', encoding='utf-8') as f:
    user_notes_obj = json.load(f)

user_notes_json_str = json.dumps(user_notes_obj, ensure_ascii=False)

old_init_annot_pattern = """    const initialAnnotations = {};
    ADS.forEach(a => {
      let fullNote = (a.notes || '').trim();
      if (a.hook && !fullNote.includes(a.hook)) {
        fullNote = fullNote ? (fullNote + ' [' + a.hook + ']') : a.hook;
      }
      initialAnnotations[a.id] = {
        postUrl: a.link || '',
        notes: fullNote,
        keyword: a.keyword || 'san',
        updatedAt: new Date().toISOString()
      };
    });"""

new_init_annot_pattern = f"""    // Initial annotations sourced EXCLUSIVELY from your manual notes
    const manualNotesFromUser = {user_notes_json_str};
    const initialAnnotations = {{}};
    ADS.forEach(a => {{
      const userItem = manualNotesFromUser[a.id];
      if (userItem) {{
        initialAnnotations[a.id] = {{
          postUrl: userItem.postUrl || a.link || '',
          notes: userItem.notes || a.notes || '',
          keyword: a.keyword || 'none',
          updatedAt: userItem.updatedAt || new Date().toISOString()
        }};
      }} else {{
        initialAnnotations[a.id] = {{
          postUrl: '',
          notes: '',
          keyword: 'none',
          updatedAt: new Date().toISOString()
        }};
      }}
    }});"""

if old_init_annot_pattern in html:
    html = html.replace(old_init_annot_pattern, new_init_annot_pattern)
    print("Updated initialAnnotations pre-seeding!")
else:
    print("Warning: old_init_annot_pattern not matched exactly.")

with open('Dashboard_Quang_Cao.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Saved updated Dashboard_Quang_Cao.html!")

# Sync to brain artifact
artifact_path = r'C:\Users\hungnv\.gemini\antigravity\brain\cb140b8e-59b1-4f14-8019-0f8942e7ecfb\dashboard.html'
shutil.copyfile('Dashboard_Quang_Cao.html', artifact_path)
print("Synced to brain artifact dashboard.html!")
