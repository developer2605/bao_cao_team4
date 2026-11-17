import json
import pandas as pd
import numpy as np

from create_excel_report import df_final_sorted, df_daily, df_pos_clean, pos_agg_table, pos_cv_map

# 1. Build Ads Data
ads_data = []
daily_grouped = df_daily.groupby('ad_id')
pos_grouped = df_pos_clean.groupby('ad_id')

for idx, r in df_final_sorted.iterrows():
    aid = r['ad_id']
    
    # daily
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
            
    # pos
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
        'pur_ratio': round(r['pur_ratio'] * 100),
        'cpm_cv': round(r['cpm_cv'] * 100) if pd.notna(r['cpm_cv']) else None,
        'cpp_cv': round(r['cpp_cv'] * 100) if pd.notna(r['cpp_cv']) else None,
        'stability': r['stability'],
        'recommendation': r['recommendation'],
        'best_pos': r['best_pos'],
        'daily': d_list,
        'placements': p_list
    })

# 2. Build Placements Aggregate Data
pos_summary_list = []
tot_pos_spend = pos_agg_table['spend'].sum()
tot_pos_pur = pos_agg_table['pur'].sum()

for _, pr in pos_agg_table.iterrows():
    p_name = pr['Vị trí quảng cáo']
    cv_info = pos_cv_map.get(p_name, {'cpm_cv': np.nan, 'cpp_cv': np.nan})
    sp = round(pr['spend'])
    m = round(pr['msg'])
    p = round(pr['pur'])
    cpm = round(sp / m) if m > 0 else 0
    cpp = round(sp / p) if p > 0 else 0
    l2 = round(p / m * 100) if m > 0 else 0
    pos_summary_list.append({
        'name': p_name,
        'spend': sp,
        'spend_pct': round(sp / tot_pos_spend * 100),
        'msg': m,
        'pur': p,
        'pur_pct': round(p / tot_pos_pur * 100) if tot_pos_pur > 0 else 0,
        'cpm': cpm,
        'cpp': cpp,
        'l2_l1': l2,
        'cpm_cv': round(cv_info['cpm_cv'] * 100) if pd.notna(cv_info['cpm_cv']) else None,
        'cpp_cv': round(cv_info['cpp_cv'] * 100) if pd.notna(cv_info['cpp_cv']) else None
    })

ads_json_str = json.dumps(ads_data, ensure_ascii=False)
pos_json_str = json.dumps(pos_summary_list, ensure_ascii=False)

html_template = f"""<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Facebook Ads Analytics Dashboard</title>
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
  <style>
    /* Custom scrollbar */
    ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
    ::-webkit-scrollbar-track {{ background: rgba(0,0,0,0.05); }}
    ::-webkit-scrollbar-thumb {{ background: rgba(100,116,139,0.3); border-radius: 3px; }}
    ::-webkit-scrollbar-thumb:hover {{ background: rgba(100,116,139,0.5); }}
  </style>
</head>
<body class="bg-[var(--background)] text-[var(--foreground)] antialiased min-h-screen p-4 md:p-6 font-sans">
  <div class="max-w-7xl mx-auto space-y-6">

    <!-- Header & Title -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-[var(--border)] pb-4">
      <div>
        <div class="flex items-center gap-2">
          <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-blue-500/10 text-blue-500">Facebook Ads Insights</span>
          <span class="text-xs text-[var(--muted-foreground)]">01/11/2026 - 16/11/2026 (16 ngày)</span>
        </div>
        <h1 class="text-2xl font-bold tracking-tight mt-1 text-[var(--foreground)]">Bảng Điều Khiển Tối Ưu Quảng Cáo & Ngân Sách</h1>
        <p class="text-sm text-[var(--muted-foreground)]">Bộ công cụ tra cứu, lọc và phân tích 163 ID Ads từ 3 sheet Full, Theo Ngày & Vị Trí Quảng Cáo</p>
      </div>
      <div class="flex items-center gap-2">
        <a href="Bao_cao_quang_cao_Facebook.xlsx" download class="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg bg-[var(--card)] hover:bg-[var(--accent)] border border-[var(--border)] transition">
          <svg class="w-4 h-4 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
          Tải File Excel (.xlsx)
        </a>
      </div>
    </div>

    <!-- Top KPI Cards -->
    <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
      <div class="bg-[var(--card)] border border-[var(--border)] rounded-xl p-3.5 shadow-sm">
        <p class="text-xs font-medium text-[var(--muted-foreground)]">Tổng Chi Tiêu</p>
        <p class="text-lg font-bold text-[var(--foreground)] mt-1 tracking-tight">250.426.909 đ</p>
        <span class="text-[11px] text-emerald-500 font-medium">163 Ads hoạt động</span>
      </div>
      <div class="bg-[var(--card)] border border-[var(--border)] rounded-xl p-3.5 shadow-sm">
        <p class="text-xs font-medium text-[var(--muted-foreground)]">Tổng Lượt Mua</p>
        <p class="text-lg font-bold text-emerald-500 mt-1 tracking-tight">1.320 đơn</p>
        <span class="text-[11px] text-[var(--muted-foreground)]">90 Ads có đơn (55%)</span>
      </div>
      <div class="bg-[var(--card)] border border-[var(--border)] rounded-xl p-3.5 shadow-sm">
        <p class="text-xs font-medium text-[var(--muted-foreground)]">Chi Phí / Lượt Mua</p>
        <p class="text-lg font-bold text-blue-500 mt-1 tracking-tight">189.717 đ</p>
        <span class="text-[11px] text-emerald-500">Top ads chỉ 61k</span>
      </div>
      <div class="bg-[var(--card)] border border-[var(--border)] rounded-xl p-3.5 shadow-sm">
        <p class="text-xs font-medium text-[var(--muted-foreground)]">Tổng Cuộc Trò Chuyện</p>
        <p class="text-lg font-bold text-[var(--foreground)] mt-1 tracking-tight">3.425 tin</p>
        <span class="text-[11px] text-[var(--muted-foreground)]">Giá tin: 73.117 đ</span>
      </div>
      <div class="bg-[var(--card)] border border-[var(--border)] rounded-xl p-3.5 shadow-sm">
        <p class="text-xs font-medium text-[var(--muted-foreground)]">Tỷ Lệ Chốt (L2/L1)</p>
        <p class="text-lg font-bold text-amber-500 mt-1 tracking-tight">39%</p>
        <span class="text-[11px] text-amber-500">Bảng tin đạt 47%</span>
      </div>
      <div class="bg-[var(--card)] border border-[var(--border)] rounded-xl p-3.5 shadow-sm">
        <p class="text-xs font-medium text-[var(--muted-foreground)]">Tiền Lãng Phí (0 Đơn)</p>
        <p class="text-lg font-bold text-rose-500 mt-1 tracking-tight">12.296.941 đ</p>
        <span class="text-[11px] text-rose-500">73 Ads cần tắt ngay</span>
      </div>
    </div>

    <!-- Navigation Tabs -->
    <div class="flex items-center gap-2 border-b border-[var(--border)] text-sm">
      <button onclick="switchTab('ads')" id="tab-btn-ads" class="px-4 py-2.5 font-medium border-b-2 border-blue-500 text-blue-500 transition">
        Tra Cứu & Lọc ID Ads (163)
      </button>
      <button onclick="switchTab('pos')" id="tab-btn-pos" class="px-4 py-2.5 font-medium border-b-2 border-transparent text-[var(--muted-foreground)] hover:text-[var(--foreground)] transition">
        Phân Tích Vị Trí Quảng Cáo
      </button>
      <button onclick="switchTab('plan')" id="tab-btn-plan" class="px-4 py-2.5 font-medium border-b-2 border-transparent text-[var(--muted-foreground)] hover:text-[var(--foreground)] transition">
        Kế Hoạch Tăng & Cắt Giảm Ngân Sách
      </button>
    </div>

    <!-- TAB 1: BẢNG TRA CỨU & BỘ LỌC ID ADS -->
    <div id="tab-content-ads" class="space-y-4">
      
      <!-- Filters Box -->
      <div class="bg-[var(--card)] border border-[var(--border)] rounded-xl p-4 space-y-3 shadow-sm">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-3">
          <!-- Search box -->
          <div class="relative md:col-span-2">
            <span class="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none text-[var(--muted-foreground)]">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
            </span>
            <input type="text" id="searchInput" oninput="applyFilters()" placeholder="Tìm kiếm nhanh Mã quảng cáo (Ad ID)..." class="w-full pl-9 pr-3 py-2 text-xs md:text-sm bg-[var(--background)] border border-[var(--border)] rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-[var(--foreground)] placeholder-[var(--muted-foreground)]">
          </div>

          <!-- Filter Recommendation -->
          <div>
            <select id="recFilter" onchange="applyFilters()" class="w-full px-3 py-2 text-xs md:text-sm bg-[var(--background)] border border-[var(--border)] rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-[var(--foreground)]">
              <option value="ALL">Tất cả khuyến nghị hành động</option>
              <option value="SCALE_UP">🚀 Ưu tiên tăng mạnh ngân sách</option>
              <option value="SCALE_MOD">📈 Tăng nhẹ / Mở rộng</option>
              <option value="MAINTAIN">⚖️ Duy trì & Cột trụ Bảng tin</option>
              <option value="UNSTABLE">⚠️ Kém hiệu quả / Cần tối ưu</option>
              <option value="KILL">❌ Tắt ngay (73 Ads 0 đơn)</option>
            </select>
          </div>

          <!-- Filter Placement -->
          <div>
            <select id="posFilter" onchange="applyFilters()" class="w-full px-3 py-2 text-xs md:text-sm bg-[var(--background)] border border-[var(--border)] rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-[var(--foreground)]">
              <option value="ALL">Tất cả vị trí tối ưu</option>
              <option value="Facebook Reels">Facebook Reels (Video ngắn)</option>
              <option value="Bảng tin">Bảng tin (Facebook Feed)</option>
              <option value="OTHER">Vị trí khác / Chưa xác định</option>
            </select>
          </div>
        </div>

        <!-- Filter Sub-row -->
        <div class="grid grid-cols-2 md:grid-cols-4 gap-3 pt-2 border-t border-[var(--border)] text-xs">
          <div>
            <label class="block text-[var(--muted-foreground)] mb-1 font-medium">Mức Chi Phí Đơn (CPP)</label>
            <select id="cppFilter" onchange="applyFilters()" class="w-full px-2.5 py-1.5 bg-[var(--background)] border border-[var(--border)] rounded-md text-[var(--foreground)]">
              <option value="ALL">Mọi mức chi phí</option>
              <option value="CHEAP">Siêu rẻ (&lt; 100k)</option>
              <option value="GOOD">Tốt (100k - 180k)</option>
              <option value="AVG">Trung bình (180k - 250k)</option>
              <option value="EXPENSIVE">Cao (&gt; 250k)</option>
              <option value="ZERO">0 Lượt mua (0 đơn)</option>
            </select>
          </div>
          <div>
            <label class="block text-[var(--muted-foreground)] mb-1 font-medium">Tính Ổn Định</label>
            <select id="stabFilter" onchange="applyFilters()" class="w-full px-2.5 py-1.5 bg-[var(--background)] border border-[var(--border)] rounded-md text-[var(--foreground)]">
              <option value="ALL">Mọi mức độ ổn định</option>
              <option value="Rất ổn định">Rất ổn định</option>
              <option value="Ổn định">Ổn định</option>
              <option value="Không ổn định">Không ổn định</option>
              <option value="Mẫu ít (1-2 ngày)">Mẫu ít (1-2 ngày)</option>
              <option value="Không có lượt mua">Không có lượt mua</option>
            </select>
          </div>
          <div>
            <label class="block text-[var(--muted-foreground)] mb-1 font-medium">Sắp Xếp Theo</label>
            <select id="sortField" onchange="applyFilters()" class="w-full px-2.5 py-1.5 bg-[var(--background)] border border-[var(--border)] rounded-md text-[var(--foreground)] font-medium">
              <option value="cpp_asc">Chi Phí / Mua (Thấp &rarr; Cao)</option>
              <option value="cpm_asc">Chi Phí / Tin (Thấp &rarr; Cao)</option>
              <option value="pur_desc">Số Lượt Mua (Nhiều &rarr; Ít)</option>
              <option value="spend_desc">Chi Tiêu (Lớn &rarr; Nhỏ)</option>
              <option value="conv_desc">Tỷ Lệ Chốt L2/L1 (Cao &rarr; Thấp)</option>
              <option value="pur_days_desc">Số Ngày Có Đơn (Nhiều &rarr; Ít)</option>
            </select>
          </div>
          <div>
            <label class="block text-[var(--muted-foreground)] mb-1 font-medium">Hiển Thị Mỗi Trang</label>
            <select id="pageSize" onchange="applyFilters()" class="w-full px-2.5 py-1.5 bg-[var(--background)] border border-[var(--border)] rounded-md text-[var(--foreground)]">
              <option value="15">15 dòng</option>
              <option value="30">30 dòng</option>
              <option value="50">50 dòng</option>
              <option value="163">Tất cả (163 Ads)</option>
            </select>
          </div>
        </div>

        <!-- Filter stats summary readout -->
        <div class="flex flex-wrap items-center justify-between text-xs text-[var(--muted-foreground)] pt-1">
          <div id="filterSummaryText">Đang hiển thị <span class="font-bold text-[var(--foreground)]">163</span> / 163 Ads</div>
          <div class="flex items-center gap-4 font-mono text-[11px]">
            <span>Tổng chi: <strong class="text-[var(--foreground)]" id="filteredSpend">250.426.909 đ</strong></span>
            <span>Tổng đơn: <strong class="text-emerald-500" id="filteredPur">1.320</strong></span>
            <span>CPA trung bình: <strong class="text-blue-500" id="filteredCPP">189.717 đ</strong></span>
          </div>
        </div>
      </div>

      <!-- Main Ads Table -->
      <div class="bg-[var(--card)] border border-[var(--border)] rounded-xl overflow-hidden shadow-sm">
        <div class="overflow-x-auto">
          <table class="w-full text-xs text-left border-collapse">
            <thead class="bg-[var(--background)] text-[var(--muted-foreground)] border-b border-[var(--border)] uppercase font-semibold text-[11px]">
              <tr>
                <th class="py-3 px-3 text-center">Hạng</th>
                <th class="py-3 px-3">Mã Quảng Cáo (Ad ID)</th>
                <th class="py-3 px-3 text-right">Chi Tiêu</th>
                <th class="py-3 px-3 text-center">Tin Nhắn</th>
                <th class="py-3 px-3 text-right">Giá / Tin</th>
                <th class="py-3 px-3 text-center font-bold text-emerald-500">Lượt Mua</th>
                <th class="py-3 px-3 text-right font-bold text-blue-500">Giá / Đơn (CPA)</th>
                <th class="py-3 px-3 text-center">Chốt L2/L1</th>
                <th class="py-3 px-3 text-center">Ngày Ra Đơn</th>
                <th class="py-3 px-3 text-center">Độ Ổn Định</th>
                <th class="py-3 px-3 text-center">Vị Trí Tối Ưu</th>
                <th class="py-3 px-3 text-center">Chi Tiết</th>
              </tr>
            </thead>
            <tbody id="adsTableBody" class="divide-y divide-[var(--border)]">
              <!-- Rendered via JS -->
            </tbody>
          </table>
        </div>

        <!-- Pagination Controls -->
        <div class="p-3 border-t border-[var(--border)] flex items-center justify-between text-xs">
          <span id="pageInfo" class="text-[var(--muted-foreground)]">Trang 1 / 11</span>
          <div class="flex items-center gap-1.5" id="pageButtons">
            <!-- Buttons via JS -->
          </div>
        </div>
      </div>
    </div>

    <!-- TAB 2: PHÂN TÍCH VỊ TRÍ QUẢNG CÁO -->
    <div id="tab-content-pos" class="space-y-4 hidden">
      <!-- Head to Head: Reels vs Feed -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <!-- Facebook Reels Card -->
        <div class="bg-[var(--card)] border border-blue-500/30 rounded-xl p-5 space-y-3 relative overflow-hidden">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <span class="p-2 rounded-lg bg-blue-500/10 text-blue-500">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"/></svg>
              </span>
              <div>
                <h3 class="font-bold text-base text-[var(--foreground)]">Facebook Reels (Video Ngắn)</h3>
                <p class="text-xs text-[var(--muted-foreground)]">Kênh tạo phễu số 1 &amp; Thống trị sản lượng đơn hàng</p>
              </div>
            </div>
            <span class="px-2 py-1 rounded bg-blue-500/10 text-blue-500 text-xs font-bold">73% Đơn Hàng</span>
          </div>

          <div class="grid grid-cols-3 gap-2 pt-2 border-t border-[var(--border)] text-center">
            <div class="bg-[var(--background)] p-2 rounded-lg">
              <p class="text-[11px] text-[var(--muted-foreground)]">Tổng Chi Tiêu</p>
              <p class="font-bold text-sm text-[var(--foreground)] mt-0.5">167.120.268 đ</p>
              <span class="text-[10px] text-[var(--muted-foreground)]">67% ngân sách</span>
            </div>
            <div class="bg-[var(--background)] p-2 rounded-lg">
              <p class="text-[11px] text-[var(--muted-foreground)]">Tổng Lượt Mua</p>
              <p class="font-bold text-sm text-emerald-500 mt-0.5">962 đơn</p>
              <span class="text-[10px] text-emerald-500 font-medium">16/16 ngày có đơn</span>
            </div>
            <div class="bg-[var(--background)] p-2 rounded-lg">
              <p class="text-[11px] text-[var(--muted-foreground)]">Chi Phí / Đơn (CPA)</p>
              <p class="font-bold text-sm text-blue-500 mt-0.5">173.722 đ</p>
              <span class="text-[10px] text-blue-500 font-medium">CV chỉ 30% (Rất đều)</span>
            </div>
          </div>

          <div class="text-xs space-y-1.5 text-[var(--muted-foreground)] pt-1">
            <p><strong class="text-[var(--foreground)]">&bull; Đặc điểm:</strong> Tạo ra lượng tin nhắn khổng lồ (2.631 tin) với giá cực rẻ (63.520 đ/tin).</p>
            <p><strong class="text-[var(--foreground)]">&bull; Ad IDs phù hợp nhất:</strong> <code>120249153794660532</code> (119 đơn), <code>120249153839930532</code> (92 đơn), <code>52550106995296</code> (39 đơn).</p>
            <p><strong class="text-[var(--foreground)]">&bull; Độ ổn định:</strong> <span class="text-emerald-500 font-bold">CỰC KỲ ỔN ĐỊNH</span>. Ra đơn 100% số ngày chạy, khả năng scale ngân sách tốt nhất mà không gãy chi phí.</p>
          </div>
        </div>

        <!-- Facebook Feed Card -->
        <div class="bg-[var(--card)] border border-emerald-500/30 rounded-xl p-5 space-y-3 relative overflow-hidden">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <span class="p-2 rounded-lg bg-emerald-500/10 text-emerald-500">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z"/></svg>
              </span>
              <div>
                <h3 class="font-bold text-base text-[var(--foreground)]">Bảng Tin (Facebook Feed)</h3>
                <p class="text-xs text-[var(--muted-foreground)]">Kênh chuyển đổi chất lượng cao &amp; Tỷ lệ chốt đơn kỷ lục</p>
              </div>
            </div>
            <span class="px-2 py-1 rounded bg-emerald-500/10 text-emerald-500 text-xs font-bold">Tỷ Lệ Chốt 47%</span>
          </div>

          <div class="grid grid-cols-3 gap-2 pt-2 border-t border-[var(--border)] text-center">
            <div class="bg-[var(--background)] p-2 rounded-lg">
              <p class="text-[11px] text-[var(--muted-foreground)]">Tổng Chi Tiêu</p>
              <p class="font-bold text-sm text-[var(--foreground)] mt-0.5">69.339.895 đ</p>
              <span class="text-[10px] text-[var(--muted-foreground)]">28% ngân sách</span>
            </div>
            <div class="bg-[var(--background)] p-2 rounded-lg">
              <p class="text-[11px] text-[var(--muted-foreground)]">Tổng Lượt Mua</p>
              <p class="font-bold text-sm text-emerald-500 mt-0.5">298 đơn</p>
              <span class="text-[10px] text-emerald-500 font-medium">16/16 ngày có đơn</span>
            </div>
            <div class="bg-[var(--background)] p-2 rounded-lg">
              <p class="text-[11px] text-[var(--muted-foreground)]">Chi Phí / Đơn (CPA)</p>
              <p class="font-bold text-sm text-amber-500 mt-0.5">232.684 đ</p>
              <span class="text-[10px] text-emerald-500 font-medium">CV chỉ 22% (Ổn định nhất)</span>
            </div>
          </div>

          <div class="text-xs space-y-1.5 text-[var(--muted-foreground)] pt-1">
            <p><strong class="text-[var(--foreground)]">&bull; Đặc điểm:</strong> Khách hàng đọc kỹ nội dung bài viết trước khi nhắn tin. Tỷ lệ chuyển đổi chốt đơn đạt 47% (cao hơn Reels 37%).</p>
            <p><strong class="text-[var(--foreground)]">&bull; Case study tiêu biểu:</strong> Ad <code>52521773324529</code> có tỷ lệ chốt tới <strong class="text-emerald-500">93%</strong> (43 tin ra 40 đơn), giá đơn Bảng tin rẻ hơn Reels tới 40.000 đ.</p>
            <p><strong class="text-[var(--foreground)]">&bull; Độ ổn định:</strong> <span class="text-emerald-500 font-bold">ỔN ĐỊNH TUYỆT ĐỐI</span>. Hệ số biến thiên chi phí đơn chỉ 21,9%, là kênh giữ doanh số chắc chắn nhất.</p>
          </div>
        </div>
      </div>

      <!-- Placements Full Table -->
      <div class="bg-[var(--card)] border border-[var(--border)] rounded-xl overflow-hidden shadow-sm">
        <div class="p-4 border-b border-[var(--border)] flex items-center justify-between">
          <h3 class="font-bold text-sm text-[var(--foreground)]">Bảng Tổng Hợp Chi Tiết Tất Cả Vị Trí Quảng Cáo</h3>
          <span class="text-xs text-[var(--muted-foreground)]">Dữ liệu từ sheet Vị Trí Quảng Cáo</span>
        </div>
        <div class="overflow-x-auto">
          <table class="w-full text-xs text-left border-collapse" id="posTable">
            <thead class="bg-[var(--background)] text-[var(--muted-foreground)] border-b border-[var(--border)] uppercase font-semibold text-[11px]">
              <tr>
                <th class="py-2.5 px-3">Vị Trí Hiển Thị</th>
                <th class="py-2.5 px-3 text-right">Chi Tiêu</th>
                <th class="py-2.5 px-3 text-center">% Tiền</th>
                <th class="py-2.5 px-3 text-center">Tin Nhắn</th>
                <th class="py-2.5 px-3 text-right">Giá / Tin</th>
                <th class="py-2.5 px-3 text-center font-bold text-emerald-500">Lượt Mua</th>
                <th class="py-2.5 px-3 text-center">% Đơn</th>
                <th class="py-2.5 px-3 text-right font-bold text-blue-500">Giá / Đơn</th>
                <th class="py-2.5 px-3 text-center font-bold text-amber-500">Chốt L2/L1</th>
                <th class="py-2.5 px-3 text-center">CV Đơn</th>
                <th class="py-2.5 px-3">Đánh Giá &amp; Khuyến Nghị</th>
              </tr>
            </thead>
            <tbody id="posTableBody" class="divide-y divide-[var(--border)]">
              <!-- Rendered via JS -->
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- TAB 3: KẾ HOẠCH PHÂN BỔ NGÂN SÁCH -->
    <div id="tab-content-plan" class="space-y-4 hidden">
      <!-- Strategy Simulator Card -->
      <div class="bg-gradient-to-r from-blue-500/10 via-purple-500/10 to-emerald-500/10 border border-blue-500/20 rounded-xl p-5 space-y-4">
        <div class="flex flex-col md:flex-row md:items-center justify-between gap-3">
          <div>
            <h3 class="font-bold text-base text-[var(--foreground)]">Mô Phỏng Tối Ưu &amp; Tái Phân Bổ Ngân Sách</h3>
            <p class="text-xs text-[var(--muted-foreground)]">Thu hồi 12.3 triệu lãng phí từ 73 Ads 0 đơn để tái đầu tư vào Top 5 Ads hiệu suất cao nhất</p>
          </div>
          <div class="bg-[var(--card)] px-3 py-1.5 rounded-lg border border-[var(--border)] text-xs font-mono">
            Hiệu quả ước tính: <span class="text-emerald-500 font-bold">+189 đơn hàng mới</span>
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
          <div class="bg-[var(--card)] p-3 rounded-lg border border-[var(--border)]">
            <span class="text-rose-500 font-bold">Bước 1: Thu hồi 12.296.941 đ</span>
            <p class="text-[var(--muted-foreground)] mt-1">Tắt hoàn toàn 73 Ads không phát sinh đơn và các Ads chi phí &gt; 800k/đơn. Tiết kiệm ngay ~15.8 triệu tiền lãng phí.</p>
          </div>
          <div class="bg-[var(--card)] p-3 rounded-lg border border-[var(--border)]">
            <span class="text-blue-500 font-bold">Bước 2: Tăng ngân sách Top 5 Ads</span>
            <p class="text-[var(--muted-foreground)] mt-1">Dồn số tiền thu hồi sang nhóm Ads giá đơn ~65k (<code>120249153839930532</code>, <code>52550106995296</code>...).</p>
          </div>
          <div class="bg-[var(--card)] p-3 rounded-lg border border-[var(--border)]">
            <span class="text-emerald-500 font-bold">Bước 3: Tăng thêm 189 đơn hàng</span>
            <p class="text-[var(--muted-foreground)] mt-1">Với cùng tổng ngân sách 250M, tổng đơn hàng tăng từ 1.320 lên 1.509 đơn, kéo CPA toàn tài khoản giảm từ 189k xuống ~165k/đơn!</p>
          </div>
        </div>
      </div>

      <!-- Action Table -->
      <div class="bg-[var(--card)] border border-[var(--border)] rounded-xl overflow-hidden shadow-sm">
        <div class="p-4 border-b border-[var(--border)] flex items-center justify-between">
          <h3 class="font-bold text-sm text-[var(--foreground)]">Danh Sách Phân Loại Hành Động Cho Từng Nhóm Quảng Cáo</h3>
        </div>
        <div class="overflow-x-auto">
          <table class="w-full text-xs text-left border-collapse">
            <thead class="bg-[var(--background)] text-[var(--muted-foreground)] border-b border-[var(--border)] uppercase font-semibold text-[11px]">
              <tr>
                <th class="py-2.5 px-3">Nhóm Hành Động</th>
                <th class="py-2.5 px-3">Mã Quảng Cáo (Ad ID)</th>
                <th class="py-2.5 px-3 text-right">Chi Tiêu</th>
                <th class="py-2.5 px-3 text-center">Đơn Hàng</th>
                <th class="py-2.5 px-3 text-right">Giá / Đơn</th>
                <th class="py-2.5 px-3 text-center">Chốt L2/L1</th>
                <th class="py-2.5 px-3 text-center">Vị Trí Tối Ưu</th>
                <th class="py-2.5 px-3">Kế Hoạch Triển Khai Cụ Thể</th>
              </tr>
            </thead>
            <tbody id="planTableBody" class="divide-y divide-[var(--border)]">
              <!-- Rendered via JS -->
            </tbody>
          </table>
        </div>
      </div>
    </div>

  </div>

  <!-- Detail Modal -->
  <div id="detailModal" class="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4 hidden">
    <div class="bg-[var(--card)] border border-[var(--border)] rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden flex flex-col shadow-2xl">
      <div class="p-4 border-b border-[var(--border)] flex items-center justify-between bg-[var(--background)]">
        <div>
          <span class="text-xs text-[var(--muted-foreground)]">Chi tiết hiệu quả Ad ID</span>
          <h3 id="modalAdId" class="text-lg font-bold font-mono text-[var(--foreground)]">120249153794660532</h3>
        </div>
        <button onclick="closeModal()" class="p-1.5 rounded-lg hover:bg-[var(--accent)] text-[var(--muted-foreground)] hover:text-[var(--foreground)]">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
        </button>
      </div>

      <div class="p-4 overflow-y-auto space-y-4 text-xs" id="modalContent">
        <!-- Dynamic Modal Content via JS -->
      </div>

      <div class="p-3 border-t border-[var(--border)] bg-[var(--background)] flex justify-end">
        <button onclick="closeModal()" class="px-4 py-1.5 text-xs font-medium rounded-lg bg-[var(--card)] hover:bg-[var(--accent)] border border-[var(--border)] text-[var(--foreground)]">Đóng</button>
      </div>
    </div>
  </div>

  <script>
    // Injected Data
    const ADS = {ads_json_str};
    const PLACEMENTS = {pos_json_str};

    let currentPage = 1;
    let filteredData = [...ADS];

    function fmtCur(val) {{
      if (val === null || val === undefined || isNaN(val) || val === 0) return '-';
      return Math.round(val).toLocaleString('vi-VN') + ' đ';
    }}

    function fmtInt(val) {{
      if (val === null || val === undefined || isNaN(val)) return '0';
      return Math.round(val).toLocaleString('vi-VN');
    }}

    function switchTab(tab) {{
      ['ads', 'pos', 'plan'].forEach(t => {{
        document.getElementById('tab-content-' + t).classList.add('hidden');
        document.getElementById('tab-btn-' + t).className = 'px-4 py-2.5 font-medium border-b-2 border-transparent text-[var(--muted-foreground)] hover:text-[var(--foreground)] transition';
      }});
      document.getElementById('tab-content-' + tab).classList.remove('hidden');
      document.getElementById('tab-btn-' + tab).className = 'px-4 py-2.5 font-medium border-b-2 border-blue-500 text-blue-500 transition';
    }}

    function copyToClipboard(text) {{
      navigator.clipboard.writeText(text);
      alert('Đã copy Ad ID: ' + text);
    }}

    function applyFilters() {{
      const query = document.getElementById('searchInput').value.trim().toLowerCase();
      const rec = document.getElementById('recFilter').value;
      const pos = document.getElementById('posFilter').value;
      const cpp = document.getElementById('cppFilter').value;
      const stab = document.getElementById('stabFilter').value;
      const sort = document.getElementById('sortField').value;

      filteredData = ADS.filter(ad => {{
        if (query && !ad.id.toLowerCase().includes(query)) return false;

        // Rec Filter
        if (rec === 'SCALE_UP' && !ad.recommendation.includes('Tăng mạnh')) return false;
        if (rec === 'SCALE_MOD' && !ad.recommendation.includes('Tăng nhẹ') && !ad.recommendation.includes('Tăng ngân sách')) return false;
        if (rec === 'MAINTAIN' && !ad.recommendation.includes('Duy trì')) return false;
        if (rec === 'UNSTABLE' && !ad.recommendation.includes('Không ổn định') && !ad.recommendation.includes('Tối ưu')) return false;
        if (rec === 'KILL' && !ad.recommendation.includes('Tắt ngay')) return false;

        // Pos Filter
        if (pos !== 'ALL') {{
          if (pos === 'OTHER') {{
            if (ad.best_pos === 'Facebook Reels' || ad.best_pos === 'Bảng tin') return false;
          }} else if (ad.best_pos !== pos) {{
            return false;
          }}
        }}

        // CPP Filter
        if (cpp === 'CHEAP' && (ad.pur === 0 || ad.cpp >= 100000)) return false;
        if (cpp === 'GOOD' && (ad.pur === 0 || ad.cpp < 100000 || ad.cpp >= 180000)) return false;
        if (cpp === 'AVG' && (ad.pur === 0 || ad.cpp < 180000 || ad.cpp >= 250000)) return false;
        if (cpp === 'EXPENSIVE' && (ad.pur === 0 || ad.cpp < 250000)) return false;
        if (cpp === 'ZERO' && ad.pur > 0) return false;

        // Stability Filter
        if (stab !== 'ALL' && ad.stability !== stab) return false;

        return true;
      }});

      // Sorting
      filteredData.sort((a, b) => {{
        if (sort === 'cpp_asc') {{
          if (a.pur > 0 && b.pur === 0) return -1;
          if (a.pur === 0 && b.pur > 0) return 1;
          if (a.cpp !== b.cpp) return a.cpp - b.cpp;
          return a.cpm - b.cpm;
        }} else if (sort === 'cpm_asc') {{
          return a.cpm - b.cpm;
        }} else if (sort === 'pur_desc') {{
          return b.pur - a.pur;
        }} else if (sort === 'spend_desc') {{
          return b.spend - a.spend;
        }} else if (sort === 'conv_desc') {{
          return b.l2_l1 - a.l2_l1;
        }} else if (sort === 'pur_days_desc') {{
          return b.pur_days - a.pur_days;
        }}
        return 0;
      }});

      currentPage = 1;
      renderTable();
      updateFilterSummary();
    }}

    function updateFilterSummary() {{
      const totalSpend = filteredData.reduce((acc, x) => acc + x.spend, 0);
      const totalPur = filteredData.reduce((acc, x) => acc + x.pur, 0);
      const avgCPP = totalPur > 0 ? Math.round(totalSpend / totalPur) : 0;

      document.getElementById('filterSummaryText').innerHTML = `Đang hiển thị <span class="font-bold text-[var(--foreground)]">${{filteredData.length}}</span> / ${{ADS.length}} Ads`;
      document.getElementById('filteredSpend').innerText = Math.round(totalSpend).toLocaleString('vi-VN') + ' đ';
      document.getElementById('filteredPur').innerText = totalPur.toLocaleString('vi-VN') + ' đơn';
      document.getElementById('filteredCPP').innerText = avgCPP > 0 ? avgCPP.toLocaleString('vi-VN') + ' đ' : '-';
    }}

    function renderTable() {{
      const pageSize = parseInt(document.getElementById('pageSize').value);
      const tbody = document.getElementById('adsTableBody');
      tbody.innerHTML = '';

      if (filteredData.length === 0) {{
        tbody.innerHTML = '<tr><td colspan="12" class="text-center py-8 text-[var(--muted-foreground)]">Không tìm thấy Ad ID nào thỏa mãn điều kiện lọc.</td></tr>';
        document.getElementById('pageInfo').innerText = '0 / 0';
        document.getElementById('pageButtons').innerHTML = '';
        return;
      }}

      const totalPages = Math.ceil(filteredData.length / pageSize);
      if (currentPage > totalPages) currentPage = totalPages;

      const startIdx = (currentPage - 1) * pageSize;
      const endIdx = Math.min(startIdx + pageSize, filteredData.length);
      const pageData = filteredData.slice(startIdx, endIdx);

      pageData.forEach((ad, i) => {{
        const globalRank = startIdx + i + 1;
        const tr = document.createElement('tr');
        tr.className = 'hover:bg-[var(--accent)]/50 transition cursor-pointer';
        tr.onclick = (e) => {{
          if (!e.target.closest('button')) openModal(ad.id);
        }};

        // Badges for stability
        let stabBadge = '';
        if (ad.stability === 'Rất ổn định') stabBadge = '<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/10 text-emerald-500">Rất ổn định</span>';
        else if (ad.stability === 'Ổn định') stabBadge = '<span class="px-2 py-0.5 rounded text-[10px] font-medium bg-blue-500/10 text-blue-500">Ổn định</span>';
        else if (ad.stability === 'Mẫu ít (1-2 ngày)') stabBadge = '<span class="px-2 py-0.5 rounded text-[10px] font-medium bg-amber-500/10 text-amber-500">Mẫu ít</span>';
        else if (ad.stability === 'Không có lượt mua') stabBadge = '<span class="px-2 py-0.5 rounded text-[10px] font-medium bg-rose-500/10 text-rose-500">0 đơn</span>';
        else stabBadge = '<span class="px-2 py-0.5 rounded text-[10px] font-medium bg-orange-500/10 text-orange-500">Biến động</span>';

        // Badge for placement
        let posBadge = ad.best_pos === 'Facebook Reels' 
          ? '<span class="px-1.5 py-0.5 rounded text-[10px] bg-blue-500/10 text-blue-500 font-medium">Reels</span>'
          : (ad.best_pos === 'Bảng tin' 
              ? '<span class="px-1.5 py-0.5 rounded text-[10px] bg-emerald-500/10 text-emerald-500 font-medium">Bảng tin</span>'
              : `<span class="px-1.5 py-0.5 rounded text-[10px] bg-gray-500/10 text-gray-500">${{ad.best_pos}}</span>`);

        tr.innerHTML = `
          <td class="py-2.5 px-3 text-center text-[var(--muted-foreground)] font-mono">${{globalRank}}</td>
          <td class="py-2.5 px-3 font-mono font-medium flex items-center gap-1.5">
            <span class="truncate max-w-[150px] md:max-w-[190px]">${{ad.id}}</span>
            <button onclick="copyToClipboard('${{ad.id}}')" title="Copy ID" class="p-1 rounded hover:bg-[var(--accent)] text-[var(--muted-foreground)]">
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"/></svg>
            </button>
          </td>
          <td class="py-2.5 px-3 text-right font-mono">${{fmtCur(ad.spend)}}</td>
          <td class="py-2.5 px-3 text-center font-mono">${{fmtInt(ad.msg)}}</td>
          <td class="py-2.5 px-3 text-right font-mono text-[var(--muted-foreground)]">${{fmtCur(ad.cpm)}}</td>
          <td class="py-2.5 px-3 text-center font-mono font-bold text-emerald-500">${{fmtInt(ad.pur)}}</td>
          <td class="py-2.5 px-3 text-right font-mono font-bold text-blue-500">${{fmtCur(ad.cpp)}}</td>
          <td class="py-2.5 px-3 text-center font-mono">${{ad.l2_l1}}%</td>
          <td class="py-2.5 px-3 text-center font-mono text-[var(--muted-foreground)]">${{ad.pur_days}}/${{ad.active_days}} (${{ad.pur_ratio}}%)</td>
          <td class="py-2.5 px-3 text-center">${{stabBadge}}</td>
          <td class="py-2.5 px-3 text-center">${{posBadge}}</td>
          <td class="py-2.5 px-3 text-center">
            <button onclick="openModal('${{ad.id}}')" class="px-2 py-0.5 rounded text-[11px] bg-[var(--background)] hover:bg-[var(--accent)] border border-[var(--border)] text-[var(--foreground)]">Xem</button>
          </td>
        `;
        tbody.appendChild(tr);
      }});

      // Render Pagination
      document.getElementById('pageInfo').innerText = `Trang ${{currentPage}} / ${{totalPages}} (Tổng ${{filteredData.length}} Ads)`;
      const pageBtns = document.getElementById('pageButtons');
      pageBtns.innerHTML = `
        <button onclick="gotoPage(1)" ${{currentPage === 1 ? 'disabled' : ''}} class="px-2 py-1 rounded bg-[var(--card)] border border-[var(--border)] disabled:opacity-40">Đầu</button>
        <button onclick="gotoPage(${{currentPage - 1}})" ${{currentPage === 1 ? 'disabled' : ''}} class="px-2 py-1 rounded bg-[var(--card)] border border-[var(--border)] disabled:opacity-40">&larr;</button>
        <span class="px-2 py-1 font-mono font-bold">${{currentPage}}</span>
        <button onclick="gotoPage(${{currentPage + 1}})" ${{currentPage === totalPages ? 'disabled' : ''}} class="px-2 py-1 rounded bg-[var(--card)] border border-[var(--border)] disabled:opacity-40">&rarr;</button>
        <button onclick="gotoPage(${{totalPages}})" ${{currentPage === totalPages ? 'disabled' : ''}} class="px-2 py-1 rounded bg-[var(--card)] border border-[var(--border)] disabled:opacity-40">Cuối</button>
      `;
    }}

    function gotoPage(p) {{
      const pageSize = parseInt(document.getElementById('pageSize').value);
      const totalPages = Math.ceil(filteredData.length / pageSize);
      if (p < 1 || p > totalPages) return;
      currentPage = p;
      renderTable();
    }}

    function renderPlacementsTable() {{
      const tbody = document.getElementById('posTableBody');
      tbody.innerHTML = '';
      PLACEMENTS.forEach(p => {{
        let evalStr = '';
        if (p.name === 'Facebook Reels') evalStr = '<span class="text-blue-500 font-bold">Chủ lực số 1</span>: 73% đơn hàng, giá rẻ nhất, cực ổn định.';
        else if (p.name === 'Bảng tin') evalStr = '<span class="text-emerald-500 font-bold">Chất lượng cao nhất</span>: Chốt đơn 47%, CV ổn định tuyệt đối (22%).';
        else if (p.name === 'Facebook Stories') evalStr = '<span class="text-amber-500">Kênh phụ trợ tốt</span>: 32 đơn giá 235k, phù hợp bật kèm Reels.';
        else if (p.name === 'Kết quả tìm kiếm') evalStr = '<span class="text-blue-500">Giá rẻ (133k)</span>, chốt 67%, nhưng volume ít.';
        else if (p.name === 'Thước phim trong luồng') evalStr = '<span class="text-rose-500">Đắt &amp; Kém</span>: 330k/đơn, CV biến động 84%. Cân nhắc tắt.';
        else evalStr = '<span class="text-rose-500 font-semibold">Tắt bỏ</span>: 0 đơn hoặc chi phí lãng phí.';

        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td class="py-2.5 px-3 font-medium text-[var(--foreground)]">${{p.name}}</td>
          <td class="py-2.5 px-3 text-right font-mono">${{fmtCur(p.spend)}}</td>
          <td class="py-2.5 px-3 text-center font-mono">${{p.spend_pct}}%</td>
          <td class="py-2.5 px-3 text-center font-mono">${{fmtInt(p.msg)}}</td>
          <td class="py-2.5 px-3 text-right font-mono text-[var(--muted-foreground)]">${{fmtCur(p.cpm)}}</td>
          <td class="py-2.5 px-3 text-center font-mono font-bold text-emerald-500">${{fmtInt(p.pur)}}</td>
          <td class="py-2.5 px-3 text-center font-mono font-bold text-emerald-500">${{p.pur_pct}}%</td>
          <td class="py-2.5 px-3 text-right font-mono font-bold text-blue-500">${{fmtCur(p.cpp)}}</td>
          <td class="py-2.5 px-3 text-center font-mono font-bold text-amber-500">${{p.l2_l1}}%</td>
          <td class="py-2.5 px-3 text-center font-mono">${{p.cpp_cv ? p.cpp_cv + '%' : '-'}}</td>
          <td class="py-2.5 px-3 text-xs">${{evalStr}}</td>
        `;
        tbody.appendChild(tr);
      }});
    }}

    function renderPlanTable() {{
      const tbody = document.getElementById('planTableBody');
      tbody.innerHTML = '';
      
      const planItems = [
        {{ group: '1. TĂNG MẠNH (+30% - +50%)', id: '120249153839930532', pos: 'Facebook Reels', act: 'Ưu tiên số 1: Ra đơn 11/11 ngày (100%), giá đơn 64k cực rẻ, tỷ lệ chốt 42%. Tăng mạnh 30-50% ngân sách mỗi 48h.' }},
        {{ group: '1. TĂNG MẠNH (+30% - +50%)', id: '52550106995296', pos: 'Facebook Reels', act: 'Độ ổn định hoàn hảo nhất: Ra đơn 6/6 ngày, cả CV tin (29%) và CV đơn (31%) đều cực thấp. Tăng gấp đôi ngân sách.' }},
        {{ group: '1. TĂNG MẠNH (+30% - +50%)', id: '120249153794660532', pos: 'Facebook Reels', act: 'Quán quân đơn hàng: 130 đơn giá 61k, ra đơn 10/11 ngày. Tăng mạnh ngân sách để chiếm lĩnh thị phần.' }},
        {{ group: '1. TĂNG MẠNH (+30% - +50%)', id: '120249153813990532', pos: 'Facebook Reels', act: 'Bền vững dài ngày: 53 đơn giá 74k, ra đơn 12/14 ngày. Tăng 30-40% ngân sách.' }},
        {{ group: '1. TĂNG MẠNH (+30% - +50%)', id: '120249153839950532', pos: 'Facebook Reels', act: 'Tỷ lệ chốt đỉnh cao: L2/L1 đạt 49%, giá đơn 66k. Tăng 30-40% ngân sách kéo thêm volume.' }},
        {{ group: '2. TĂNG NHẸ (+15% - +25%)', id: '120249153839980532', pos: 'Facebook Reels', act: 'Tăng 15-20% ngân sách. Giá đơn 94k dưới ngưỡng 100k, duy trì ổn định.' }},
        {{ group: '2. TĂNG NHẸ (+15% - +25%)', id: '120252740442820268', pos: 'Bảng tin', act: 'Tăng 15-20% ngân sách dồn vào Bảng tin (giá đơn trên Bảng tin chỉ 88k so với 117k ở Reels).' }},
        {{ group: '2. TĂNG NHẸ (+15% - +25%)', id: '52550102779296', pos: 'Bảng tin', act: 'Tăng 15-20% ngân sách. Tỷ lệ chốt 42%, rất phù hợp Bảng tin.' }},
        {{ group: '3. DUY TRÌ & TỐI ƯU CỘT TRỤ', id: '52521773324529', pos: 'Bảng tin', act: 'Duy trì 12M, dồn hiển thị sang Bảng tin (chốt 93%, 40 đơn, giá 189k rẻ hơn Reels 229k). Ra đơn 16/16 ngày.' }},
        {{ group: '3. DUY TRÌ & TỐI ƯU CỘT TRỤ', id: '52517259236329', pos: 'Bảng tin', act: 'Duy trì 12.7M, dịch chuyển bớt từ Reels sang Bảng tin (giá đơn Bảng tin 165k rẻ hơn Reels 203k).' }},
        {{ group: '4. TẮT NGAY (CHỐNG LÃNG PHÍ)', id: '73 Ads 0 Đơn', pos: 'Nhiều vị trí', act: 'TẮT TOÀN BỘ 73 ADS KHÔNG CÓ ĐƠN để thu hồi ngay 12.296.941 đ tái đầu tư vào Nhóm 1.' }},
        {{ group: '4. TẮT NGAY (CHỐNG LÃNG PHÍ)', id: '52505497343329', pos: 'Facebook Reels', act: 'Tắt ngay: Chi 922k chỉ có 1 đơn, giá đơn 922k quá đắt.' }},
        {{ group: '4. TẮT NGAY (CHỐNG LÃNG PHÍ)', id: '52642651061420', pos: 'Facebook Reels', act: 'Tắt ngay: Chi 888k chỉ có 1 đơn, giá đơn 888k.' }}
      ];

      planItems.forEach(item => {{
        let adObj = ADS.find(a => a.id === item.id);
        let spend = adObj ? fmtCur(adObj.spend) : '12.296.941 đ';
        let pur = adObj ? fmtInt(adObj.pur) : '0';
        let cpp = adObj ? fmtCur(adObj.cpp) : '-';
        let l2 = adObj ? adObj.l2_l1 + '%' : '0%';

        let grpBadge = item.group.includes('TĂNG MẠNH')
          ? '<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-blue-500/10 text-blue-500">1. Tăng Mạnh</span>'
          : (item.group.includes('TĂNG NHẸ')
              ? '<span class="px-2 py-0.5 rounded text-[10px] font-semibold bg-emerald-500/10 text-emerald-500">2. Tăng Nhẹ</span>'
              : (item.group.includes('DUY TRÌ')
                  ? '<span class="px-2 py-0.5 rounded text-[10px] font-semibold bg-amber-500/10 text-amber-500">3. Duy Trì</span>'
                  : '<span class="px-2 py-0.5 rounded text-[10px] font-semibold bg-rose-500/10 text-rose-500">4. Tắt Ngay</span>'));

        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td class="py-2.5 px-3">${{grpBadge}}</td>
          <td class="py-2.5 px-3 font-mono font-medium">${{item.id}}</td>
          <td class="py-2.5 px-3 text-right font-mono">${{spend}}</td>
          <td class="py-2.5 px-3 text-center font-mono font-bold text-emerald-500">${{pur}}</td>
          <td class="py-2.5 px-3 text-right font-mono font-bold text-blue-500">${{cpp}}</td>
          <td class="py-2.5 px-3 text-center font-mono">${{l2}}</td>
          <td class="py-2.5 px-3 text-center"><span class="px-1.5 py-0.5 rounded bg-[var(--background)] border border-[var(--border)] font-medium text-[11px]">${{item.pos}}</span></td>
          <td class="py-2.5 px-3 text-xs">${{item.act}}</td>
        `;
        tbody.appendChild(tr);
      }});
    }}

    function openModal(adId) {{
      const ad = ADS.find(a => a.id === adId);
      if (!ad) return;

      document.getElementById('modalAdId').innerText = ad.id;
      const content = document.getElementById('modalContent');

      // Top KPI in modal
      let html = `
        <div class="grid grid-cols-4 gap-2 text-center">
          <div class="bg-[var(--background)] p-2 rounded-lg border border-[var(--border)]">
            <span class="text-[10px] text-[var(--muted-foreground)]">Chi tiêu</span>
            <p class="font-bold text-sm mt-0.5">${{fmtCur(ad.spend)}}</p>
          </div>
          <div class="bg-[var(--background)] p-2 rounded-lg border border-[var(--border)]">
            <span class="text-[10px] text-[var(--muted-foreground)]">Lượt mua</span>
            <p class="font-bold text-sm text-emerald-500 mt-0.5">${{fmtInt(ad.pur)}} đơn</p>
          </div>
          <div class="bg-[var(--background)] p-2 rounded-lg border border-[var(--border)]">
            <span class="text-[10px] text-[var(--muted-foreground)]">Giá / Đơn</span>
            <p class="font-bold text-sm text-blue-500 mt-0.5">${{fmtCur(ad.cpp)}}</p>
          </div>
          <div class="bg-[var(--background)] p-2 rounded-lg border border-[var(--border)]">
            <span class="text-[10px] text-[var(--muted-foreground)]">Chốt L2/L1</span>
            <p class="font-bold text-sm text-amber-500 mt-0.5">${{ad.l2_l1}}%</p>
          </div>
        </div>

        <div class="p-3 bg-[var(--background)] rounded-lg border border-[var(--border)] space-y-1">
          <p><strong class="text-[var(--foreground)]">Khuyến nghị:</strong> <span class="font-semibold text-blue-500">${{ad.recommendation}}</span></p>
          <p><strong class="text-[var(--foreground)]">Độ ổn định:</strong> ${{ad.stability}} (Ra đơn ${{ad.pur_days}}/${{ad.active_days}} ngày - ${{ad.pur_ratio}}%).</p>
          <p><strong class="text-[var(--foreground)]">Độ biến thiên chi phí:</strong> CV Tin nhắn: ${{ad.cpm_cv ? ad.cpm_cv + '%' : '-'}} | CV Đơn hàng: ${{ad.cpp_cv ? ad.cpp_cv + '%' : '-'}}</p>
        </div>
      `;

      // Placements Breakdown
      if (ad.placements && ad.placements.length > 0) {{
        html += `
          <div>
            <h4 class="font-bold text-xs uppercase tracking-wider text-[var(--muted-foreground)] mb-2">Phân Bổ Theo Vị Trí Quảng Cáo</h4>
            <div class="border border-[var(--border)] rounded-lg overflow-hidden">
              <table class="w-full text-xs text-left">
                <thead class="bg-[var(--background)] border-b border-[var(--border)] text-[var(--muted-foreground)] text-[10px] uppercase">
                  <tr>
                    <th class="py-1.5 px-2.5">Vị Trí</th>
                    <th class="py-1.5 px-2.5 text-right">Chi Tiêu</th>
                    <th class="py-1.5 px-2.5 text-center">Tin</th>
                    <th class="py-1.5 px-2.5 text-center">Đơn</th>
                    <th class="py-1.5 px-2.5 text-right">Giá / Đơn</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-[var(--border)] font-mono">
                  ${{ad.placements.map(pl => `
                    <tr>
                      <td class="py-1.5 px-2.5 font-sans">${{pl.name}}</td>
                      <td class="py-1.5 px-2.5 text-right">${{fmtCur(pl.spend)}}</td>
                      <td class="py-1.5 px-2.5 text-center">${{fmtInt(pl.msg)}}</td>
                      <td class="py-1.5 px-2.5 text-center font-bold text-emerald-500">${{fmtInt(pl.pur)}}</td>
                      <td class="py-1.5 px-2.5 text-right font-bold text-blue-500">${{fmtCur(pl.cpp)}}</td>
                    </tr>
                  `).join('')}}
                </tbody>
              </table>
            </div>
          </div>
        `;
      }}

      // Daily Breakdown
      if (ad.daily && ad.daily.length > 0) {{
        html += `
          <div>
            <h4 class="font-bold text-xs uppercase tracking-wider text-[var(--muted-foreground)] mb-2">Lịch Sử Hàng Ngày (Sheet Theo Ngày)</h4>
            <div class="border border-[var(--border)] rounded-lg overflow-hidden max-h-48 overflow-y-auto">
              <table class="w-full text-xs text-left">
                <thead class="bg-[var(--background)] border-b border-[var(--border)] text-[var(--muted-foreground)] text-[10px] uppercase sticky top-0">
                  <tr>
                    <th class="py-1.5 px-2.5">Ngày</th>
                    <th class="py-1.5 px-2.5 text-right">Chi Tiêu</th>
                    <th class="py-1.5 px-2.5 text-center">Tin</th>
                    <th class="py-1.5 px-2.5 text-center font-bold text-emerald-500">Đơn</th>
                    <th class="py-1.5 px-2.5 text-right">Giá / Đơn</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-[var(--border)] font-mono">
                  ${{ad.daily.map(d => `
                    <tr>
                      <td class="py-1.5 px-2.5 font-sans">${{d.date}}</td>
                      <td class="py-1.5 px-2.5 text-right">${{fmtCur(d.spend)}}</td>
                      <td class="py-1.5 px-2.5 text-center">${{fmtInt(d.msg)}}</td>
                      <td class="py-1.5 px-2.5 text-center font-bold text-emerald-500">${{fmtInt(d.pur)}}</td>
                      <td class="py-1.5 px-2.5 text-right font-bold text-blue-500">${{fmtCur(d.cpp)}}</td>
                    </tr>
                  `).join('')}}
                </tbody>
              </table>
            </div>
          </div>
        `;
      }}

      content.innerHTML = html;
      document.getElementById('detailModal').classList.remove('hidden');
    }}

    function closeModal() {{
      document.getElementById('detailModal').classList.add('hidden');
    }}

    // Close modal on Escape or clicking backdrop
    window.addEventListener('keydown', (e) => {{
      if (e.key === 'Escape') closeModal();
    }});
    document.getElementById('detailModal').addEventListener('click', (e) => {{
      if (e.target === document.getElementById('detailModal')) closeModal();
    }});

    // Initialize
    applyFilters();
    renderPlacementsTable();
    renderPlanTable();
  </script>
</body>
</html>
"""

# Save to workspace
workspace_out = r'd:\Báo cáo\Dashboard_Quang_Cao.html'
with open(workspace_out, 'w', encoding='utf-8') as f:
    f.write(html_template)
print(f'Dashboard successfully saved to {workspace_out}!')

# Save to artifact directory
artifact_out = r'C:\Users\hungnv\.gemini\antigravity\brain\cb140b8e-59b1-4f14-8019-0f8942e7ecfb\dashboard.html'
with open(artifact_out, 'w', encoding='utf-8') as f:
    f.write(html_template)
print(f'Dashboard successfully saved to artifact: {artifact_out}!')
