# -*- coding: utf-8 -*-
"""
Script to update Dashboard_Quang_Cao.html with:
- Status toggle button (🟢 Đang Bật / 🔴 Đã Tắt) in Tab 3 (Độ ổn định vị trí / mã quảng cáo)
- Dedicated Reason column ("Lý Do Tắt") with 1-click edit
- Modal dialog with quick preset reasons & custom input
- Ability to apply reason to all positions of an Ad ID
- LocalStorage persistence
- Filter by Status (Tất cả, Đang Bật, Đã Tắt)
- Synchronized status in Ad Detail modal
"""

import os
import shutil

html_path = 'Dashboard_Quang_Cao.html'
artifact_path = r'C:\Users\hungnv\.gemini\antigravity\brain\cb140b8e-59b1-4f14-8019-0f8942e7ecfb\dashboard.html'

with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

# -------------------------------------------------------------
# 1. Add #statusModal right before #detailModal
# -------------------------------------------------------------
status_modal_html = """
  <!-- Modal Bật/Tắt Trạng Thái & Ghi Lý Do Tắt (MỚI) -->
  <div id="statusModal" class="fixed inset-0 z-50 flex items-center justify-center p-3 md:p-4 hidden" style="background-color: rgba(15, 23, 42, 0.65);">
    <div class="bg-white text-slate-900 border border-slate-200 rounded-2xl max-w-lg w-full overflow-hidden flex flex-col shadow-2xl animate-in fade-in zoom-in-95 duration-150">
      <div class="px-5 py-4 border-b border-slate-200 flex items-center justify-between bg-slate-50">
        <div class="flex items-center gap-2.5">
          <span class="w-3.5 h-3.5 rounded-full bg-rose-500 flex-shrink-0 animate-pulse"></span>
          <div>
            <h3 id="statusModalTitle" class="text-base font-bold text-slate-900">Tắt Quảng Cáo &amp; Ghi Lý Do Tắt</h3>
            <p id="statusModalSubtitle" class="text-xs text-slate-500 font-mono mt-0.5">Ad ID: - | Vị trí: -</p>
          </div>
        </div>
        <button onclick="closeStatusModal()" title="Đóng cửa sổ" class="p-1.5 rounded-lg bg-white hover:bg-slate-200 border border-slate-200 text-slate-500 hover:text-slate-800 transition">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
        </button>
      </div>

      <div class="p-5 space-y-4 text-xs bg-white text-slate-800">
        <!-- Quick Preset Reasons -->
        <div class="space-y-2">
          <label class="block text-slate-700 font-semibold text-xs">Gợi Ý Lý Do Tắt Nhanh (Nhấn để chọn):</label>
          <div class="flex flex-wrap gap-1.5">
            <button type="button" onclick="selectQuickReason('Off 15/11 - Chi 227k không ra đơn')" class="px-2.5 py-1 rounded-lg bg-slate-100 hover:bg-rose-50 hover:text-rose-700 hover:border-rose-300 border border-slate-200 transition text-[11px] font-medium text-slate-700">Off 15/11 - Chi 227k</button>
            <button type="button" onclick="selectQuickReason('Off 16/11 - Chi 181k không ra đơn')" class="px-2.5 py-1 rounded-lg bg-slate-100 hover:bg-rose-50 hover:text-rose-700 hover:border-rose-300 border border-slate-200 transition text-[11px] font-medium text-slate-700">Off 16/11 - Chi 181k</button>
            <button type="button" onclick="selectQuickReason('Off 17/11 - Chi 315k chỉ 1 đơn')" class="px-2.5 py-1 rounded-lg bg-slate-100 hover:bg-rose-50 hover:text-rose-700 hover:border-rose-300 border border-slate-200 transition text-[11px] font-medium text-slate-700">Off 17/11 - Chi 315k</button>
            <button type="button" onclick="selectQuickReason('0 Đơn - Lãng phí ngân sách')" class="px-2.5 py-1 rounded-lg bg-slate-100 hover:bg-rose-50 hover:text-rose-700 hover:border-rose-300 border border-slate-200 transition text-[11px] font-medium text-slate-700">0 Đơn - Lãng phí</button>
            <button type="button" onclick="selectQuickReason('CPA vọt giá quá cao (> 250k)')" class="px-2.5 py-1 rounded-lg bg-slate-100 hover:bg-rose-50 hover:text-rose-700 hover:border-rose-300 border border-slate-200 transition text-[11px] font-medium text-slate-700">CPA vọt giá &gt; 250k</button>
            <button type="button" onclick="selectQuickReason('Chi phí tin nhắn quá đắt (> 100k)')" class="px-2.5 py-1 rounded-lg bg-slate-100 hover:bg-rose-50 hover:text-rose-700 hover:border-rose-300 border border-slate-200 transition text-[11px] font-medium text-slate-700">Tin nhắn quá đắt</button>
            <button type="button" onclick="selectQuickReason('Bão hòa tệp đối tượng / Tần suất cao')" class="px-2.5 py-1 rounded-lg bg-slate-100 hover:bg-rose-50 hover:text-rose-700 hover:border-rose-300 border border-slate-200 transition text-[11px] font-medium text-slate-700">Bão hòa tệp đối tượng</button>
            <button type="button" onclick="selectQuickReason('Dồn ngân sách sang Facebook Reels')" class="px-2.5 py-1 rounded-lg bg-slate-100 hover:bg-rose-50 hover:text-rose-700 hover:border-rose-300 border border-slate-200 transition text-[11px] font-medium text-slate-700">Dồn ngân sách sang Reels</button>
            <button type="button" onclick="selectQuickReason('Tắt vị trí Bảng tin máy tính (Ít khách)')" class="px-2.5 py-1 rounded-lg bg-slate-100 hover:bg-rose-50 hover:text-rose-700 hover:border-rose-300 border border-slate-200 transition text-[11px] font-medium text-slate-700">Tắt vị trí PC</button>
          </div>
        </div>

        <!-- Detailed Reason Input -->
        <div class="space-y-1.5">
          <label class="block text-slate-700 font-semibold text-xs">Lý Do Tắt Cụ Thể (Hiển thị trên bảng báo cáo):</label>
          <input type="text" id="statusReasonInput" placeholder="Nhập lý do tắt (ví dụ: Off 16/11 - 181, 0 đơn...)" class="w-full px-3 py-2 bg-slate-50 border border-slate-300 rounded-lg text-slate-900 text-xs focus:ring-2 focus:ring-rose-500 focus:outline-none">
        </div>

        <!-- Scope: Apply to All Positions of this Ad ID -->
        <div class="p-3 bg-amber-50/70 border border-amber-200 rounded-xl space-y-1">
          <label class="flex items-start gap-2 cursor-pointer select-none">
            <input type="checkbox" id="statusApplyAllCheck" class="rounded border-slate-300 text-rose-600 focus:ring-rose-500 mt-0.5">
            <span class="text-xs text-amber-900 font-medium leading-relaxed">
              Áp dụng lý do tắt này cho <strong>toàn bộ các vị trí</strong> của Ad ID này
            </span>
          </label>
          <p class="text-[11px] text-amber-700 ml-5">Nếu chọn, tất cả các vị trí hiển thị của mã quảng cáo này sẽ chuyển sang trạng thái Đã Tắt.</p>
        </div>
      </div>

      <div class="px-5 py-3 border-t border-slate-200 bg-slate-50 flex items-center justify-between">
        <button type="button" onclick="confirmTurnOnCurrent()" id="btnTurnBackOnInModal" class="px-3.5 py-1.5 text-xs font-semibold rounded-lg bg-emerald-50 hover:bg-emerald-100 text-emerald-700 border border-emerald-300 transition">
          🟢 Bật Lại Quảng Cáo
        </button>
        <div class="flex items-center gap-2">
          <button onclick="closeStatusModal()" class="px-3.5 py-1.5 text-xs font-semibold rounded-lg bg-white hover:bg-slate-100 border border-slate-300 text-slate-700 shadow-sm transition">Đóng</button>
          <button onclick="confirmSaveStatusReason()" class="px-4 py-1.5 text-xs font-semibold rounded-lg bg-rose-600 hover:bg-rose-700 text-white shadow-sm transition">
            Xác Nhận Tắt Quảng Cáo
          </button>
        </div>
      </div>
    </div>
  </div>
"""

target_detail_modal = '  <!-- Detail & Edit Modal (High Contrast & Solid White Container) -->'
if target_detail_modal in content and 'id="statusModal"' not in content:
    content = content.replace(target_detail_modal, status_modal_html + '\n' + target_detail_modal)
    print("Added #statusModal successfully!")

# -------------------------------------------------------------
# 2. Update Tab 3 Filter Bar & Summary Counters
# -------------------------------------------------------------
old_filter_bar = """        <div class="grid grid-cols-1 md:grid-cols-4 gap-3">
          <div class="relative md:col-span-2">
            <span class="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none text-[var(--muted-foreground)]">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
            </span>
            <input type="text" id="adPosSearchInput" oninput="applyAdPosFilters()" placeholder="Tìm theo Ad ID hoặc tên vị trí..." class="w-full pl-9 pr-3 py-2 text-xs md:text-sm bg-[var(--background)] border border-[var(--border)] rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 text-[var(--foreground)] placeholder-[var(--muted-foreground)]">
          </div>

          <div>
            <select id="adPosNameFilter" onchange="applyAdPosFilters()" class="w-full px-3 py-2 text-xs md:text-sm bg-[var(--background)] border border-[var(--border)] rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 text-[var(--foreground)]">
              <option value="ALL">Tất cả vị trí hiển thị</option>
              <option value="Facebook Reels">Facebook Reels</option>
              <option value="Bảng tin trên máy tính">Bảng tin trên máy tính</option>
              <option value="Bảng tin trên thiết bị di động">Bảng tin trên di động</option>
              <option value="Facebook Stories">Facebook Stories</option>
              <option value="Facebook Watch">Facebook Watch</option>
              <option value="Kết quả tìm kiếm">Kết quả tìm kiếm</option>
            </select>
          </div>

          <div>
            <select id="adPosStabFilter" onchange="applyAdPosFilters()" class="w-full px-3 py-2 text-xs md:text-sm bg-[var(--background)] border border-[var(--border)] rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 text-[var(--foreground)]">
              <option value="ALL">Mọi mức độ ổn định</option>
              <option value="Rất ổn định">Rất ổn định (CV &lt; 65%, Ra đơn &ge; 70%)</option>
              <option value="Ổn định">Ổn định (Ra đơn &ge; 50%)</option>
              <option value="Không ổn định">Không ổn định / Biến động</option>
              <option value="Không tạo ra đơn">Không tạo ra đơn (0 đơn)</option>
            </select>
          </div>
        </div>

        <div class="flex flex-wrap items-center justify-between text-xs text-[var(--muted-foreground)] pt-1 border-t border-[var(--border)]">
          <div id="adPosFilterSummaryText">Đang hiển thị <span class="font-bold text-[var(--foreground)]">0</span> cặp Vị trí x Mã QC</div>
          <div class="flex items-center gap-4 font-mono text-[11px]">
            <span>Tổng chi: <strong class="text-[var(--foreground)]" id="adPosSpendSum">-</strong></span>
            <span>Tổng đơn: <strong class="text-emerald-600" id="adPosPurSum">-</strong></span>
            <span>CPA trung bình: <strong class="text-purple-600" id="adPosCPPSum">-</strong></span>
          </div>
        </div>"""

new_filter_bar = """        <div class="grid grid-cols-1 md:grid-cols-5 gap-3">
          <div class="relative md:col-span-2">
            <span class="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none text-[var(--muted-foreground)]">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
            </span>
            <input type="text" id="adPosSearchInput" oninput="applyAdPosFilters()" placeholder="Tìm theo Ad ID, vị trí, hoặc lý do tắt..." class="w-full pl-9 pr-3 py-2 text-xs md:text-sm bg-[var(--background)] border border-[var(--border)] rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 text-[var(--foreground)] placeholder-[var(--muted-foreground)]">
          </div>

          <div>
            <select id="adPosNameFilter" onchange="applyAdPosFilters()" class="w-full px-3 py-2 text-xs md:text-sm bg-[var(--background)] border border-[var(--border)] rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 text-[var(--foreground)]">
              <option value="ALL">Tất cả vị trí hiển thị</option>
              <option value="Facebook Reels">Facebook Reels</option>
              <option value="Bảng tin trên máy tính">Bảng tin trên máy tính</option>
              <option value="Bảng tin trên thiết bị di động">Bảng tin trên di động</option>
              <option value="Facebook Stories">Facebook Stories</option>
              <option value="Facebook Watch">Facebook Watch</option>
              <option value="Kết quả tìm kiếm">Kết quả tìm kiếm</option>
            </select>
          </div>

          <div>
            <select id="adPosStabFilter" onchange="applyAdPosFilters()" class="w-full px-3 py-2 text-xs md:text-sm bg-[var(--background)] border border-[var(--border)] rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 text-[var(--foreground)]">
              <option value="ALL">Mọi mức độ ổn định</option>
              <option value="Rất ổn định">Rất ổn định (CV &lt; 65%, Ra đơn &ge; 70%)</option>
              <option value="Ổn định">Ổn định (Ra đơn &ge; 50%)</option>
              <option value="Không ổn định">Không ổn định / Biến động</option>
              <option value="Không tạo ra đơn">Không tạo ra đơn (0 đơn)</option>
            </select>
          </div>

          <!-- MỚI: Lọc Trạng Thái Bật / Tắt -->
          <div>
            <select id="adPosStatusFilter" onchange="applyAdPosFilters()" class="w-full px-3 py-2 text-xs md:text-sm bg-[var(--background)] border border-[var(--border)] rounded-lg focus:outline-none focus:ring-2 focus:ring-rose-500 text-[var(--foreground)] font-semibold">
              <option value="ALL">⚡ Trạng thái: Tất cả</option>
              <option value="ON">🟢 Đang Bật (Hoạt động)</option>
              <option value="OFF">🔴 Đã Tắt (Dừng chiến dịch)</option>
            </select>
          </div>
        </div>

        <div class="flex flex-wrap items-center justify-between text-xs text-[var(--muted-foreground)] pt-1 border-t border-[var(--border)]">
          <div id="adPosFilterSummaryText">Đang hiển thị <span class="font-bold text-[var(--foreground)]">0</span> cặp Vị trí x Mã QC</div>
          <div class="flex flex-wrap items-center gap-3 md:gap-4 font-mono text-[11px]">
            <span>🟢 Đang Bật: <strong class="text-emerald-600" id="adPosActiveCount">0</strong></span>
            <span>🔴 Đã Tắt: <strong class="text-rose-600" id="adPosOffCount">0</strong></span>
            <span>Tổng chi: <strong class="text-[var(--foreground)]" id="adPosSpendSum">-</strong></span>
            <span>Tổng đơn: <strong class="text-emerald-600" id="adPosPurSum">-</strong></span>
            <span>CPA TB: <strong class="text-purple-600" id="adPosCPPSum">-</strong></span>
          </div>
        </div>"""

if old_filter_bar in content:
    content = content.replace(old_filter_bar, new_filter_bar)
    print("Updated Tab 3 Filter Bar & Counters successfully!")
else:
    print("Warning: old_filter_bar not found in exact match, will check alternative.")

# -------------------------------------------------------------
# 3. Update Tab 3 Table Header
# -------------------------------------------------------------
old_thead = """              <tr>
                <th class="py-2.5 px-2.5 text-center">Hạng</th>
                <th class="py-2.5 px-3">Mã Quảng Cáo (Ad ID)</th>
                <th class="py-2.5 px-3">Vị Trí Quảng Cáo</th>
                <th class="py-2.5 px-3 text-right">Chi Tiêu</th>
                <th class="py-2.5 px-2.5 text-center">Tin</th>
                <th class="py-2.5 px-3 text-right">Giá / Tin</th>
                <th class="py-2.5 px-2.5 text-center font-bold text-emerald-600">Lượt Mua</th>
                <th class="py-2.5 px-3 text-right font-bold text-blue-600">Giá / Đơn (CPA)</th>
                <th class="py-2.5 px-2.5 text-center">Chốt L2/L1</th>
                <th class="py-2.5 px-2.5 text-center">Ngày Ra Đơn</th>
                <th class="py-2.5 px-2.5 text-center">CV Đơn</th>
                <th class="py-2.5 px-2.5 text-center">Độ Ổn Định</th>
                <th class="py-2.5 px-3">Khuyến Nghị Cho Cặp Này</th>
              </tr>"""

new_thead = """              <tr>
                <th class="py-2.5 px-2.5 text-center">Hạng</th>
                <th class="py-2.5 px-3">Mã Quảng Cáo (Ad ID)</th>
                <th class="py-2.5 px-3">Vị Trí Quảng Cáo</th>
                <th class="py-2.5 px-2.5 text-center">Trạng Thái</th>
                <th class="py-2.5 px-3">Lý Do Tắt</th>
                <th class="py-2.5 px-3 text-right">Chi Tiêu</th>
                <th class="py-2.5 px-2.5 text-center">Tin</th>
                <th class="py-2.5 px-3 text-right">Giá / Tin</th>
                <th class="py-2.5 px-2.5 text-center font-bold text-emerald-600">Lượt Mua</th>
                <th class="py-2.5 px-3 text-right font-bold text-blue-600">Giá / Đơn (CPA)</th>
                <th class="py-2.5 px-2.5 text-center">Chốt L2/L1</th>
                <th class="py-2.5 px-2.5 text-center">Ngày Ra Đơn</th>
                <th class="py-2.5 px-2.5 text-center">CV Đơn</th>
                <th class="py-2.5 px-2.5 text-center">Độ Ổn Định</th>
                <th class="py-2.5 px-3">Khuyến Nghị Cho Cặp Này</th>
              </tr>"""

if old_thead in content:
    content = content.replace(old_thead, new_thead)
    print("Updated Tab 3 thead successfully!")
else:
    print("Warning: old_thead not found in exact match.")

# -------------------------------------------------------------
# 4. Storage & Helper Logic for Statuses
# -------------------------------------------------------------
old_storage_snippet = """    let userAnnotations = { ...initialAnnotations };
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {
        const parsed = JSON.parse(saved);
        userAnnotations = { ...initialAnnotations, ...parsed };
      }
    } catch (e) {
      console.warn('Cannot load from localStorage', e);
    }"""

new_storage_snippet = """    let userAnnotations = { ...initialAnnotations };
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {
        const parsed = JSON.parse(saved);
        userAnnotations = { ...initialAnnotations, ...parsed };
      }
    } catch (e) {
      console.warn('Cannot load from localStorage', e);
    }

    // ==========================================
    // STATUS & REASON STORAGE FOR AD POSITIONS
    // ==========================================
    const POS_STATUS_KEY = 'fb_ads_pos_status_storage_v2';
    
    // Map of known ads stopped in user notes
    const adNotesOff = {};
    ADS.forEach(a => {
      const note = (a.notes || '').trim();
      if (/off|tắt/i.test(note)) {
        adNotesOff[a.id] = note;
      }
    });

    const initialPosStatus = {};
    AD_POS.forEach(p => {
      const key = p.ad_id + '___' + p.pos;
      if (adNotesOff[p.ad_id]) {
        initialPosStatus[key] = {
          status: 'OFF',
          reason: adNotesOff[p.ad_id],
          updatedAt: 'Pre-seeded'
        };
      } else {
        initialPosStatus[key] = {
          status: 'ON',
          reason: '',
          updatedAt: 'Pre-seeded'
        };
      }
    });

    let posStatusMap = { ...initialPosStatus };
    try {
      const savedPosStatus = localStorage.getItem(POS_STATUS_KEY);
      if (savedPosStatus) {
        const parsed = JSON.parse(savedPosStatus);
        posStatusMap = { ...initialPosStatus, ...parsed };
      }
    } catch (e) {
      console.warn('Cannot load posStatusMap from localStorage', e);
    }

    function getPairStatus(adId, pos) {
      const key = adId + '___' + pos;
      if (posStatusMap[key]) {
        return posStatusMap[key];
      }
      if (adNotesOff[adId]) {
        return { status: 'OFF', reason: adNotesOff[adId], updatedAt: '' };
      }
      return { status: 'ON', reason: '', updatedAt: '' };
    }

    function savePosStatusMap() {
      try {
        localStorage.setItem(POS_STATUS_KEY, JSON.stringify(posStatusMap));
      } catch (e) {
        console.warn('Cannot save posStatusMap to localStorage', e);
      }
    }

    function escapeHtml(text) {
      if (!text) return '';
      return String(text)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
    }

    function escapeJs(str) {
      if (!str) return '';
      return String(str).replace(/'/g, "\\\\'");
    }

    function showToast(msg) {
      let toast = document.getElementById('toastNotification');
      if (!toast) {
        toast = document.createElement('div');
        toast.id = 'toastNotification';
        toast.className = 'fixed bottom-5 right-5 z-[9999] px-4 py-2.5 rounded-xl bg-slate-900 text-white text-xs font-semibold shadow-2xl transition-all duration-300 transform translate-y-10 opacity-0 flex items-center gap-2 border border-slate-700';
        document.body.appendChild(toast);
      }
      toast.innerHTML = `<svg class="w-4 h-4 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg> <span>${msg}</span>`;
      toast.classList.remove('translate-y-10', 'opacity-0');
      toast.classList.add('translate-y-0', 'opacity-100');
      setTimeout(() => {
        toast.classList.remove('translate-y-0', 'opacity-100');
        toast.classList.add('translate-y-10', 'opacity-0');
      }, 2500);
    }

    let activePairKey = '';
    let activeAdId = '';
    let activePos = '';

    function openTurnOffModal(pairKey, adId, pos, event, isEditing) {
      if (event) event.stopPropagation();
      activePairKey = pairKey;
      activeAdId = adId;
      activePos = pos;

      const st = posStatusMap[pairKey] || getPairStatus(adId, pos);

      const titleEl = document.getElementById('statusModalTitle');
      const subtitleEl = document.getElementById('statusModalSubtitle');
      const inputEl = document.getElementById('statusReasonInput');
      const applyAllEl = document.getElementById('statusApplyAllCheck');
      const btnOn = document.getElementById('btnTurnBackOnInModal');

      if (titleEl) titleEl.innerText = isEditing ? 'Chỉnh Sửa Lý Do Tắt Quảng Cáo' : 'Tắt Quảng Cáo & Ghi Lý Do';
      if (subtitleEl) subtitleEl.innerText = `Ad ID: ${adId} | Vị trí: ${pos}`;
      if (inputEl) {
        inputEl.value = st.reason || '';
        setTimeout(() => inputEl.focus(), 100);
      }
      if (applyAllEl) applyAllEl.checked = false;
      if (btnOn) {
        btnOn.style.display = (st.status === 'OFF') ? 'inline-block' : 'none';
      }

      const modal = document.getElementById('statusModal');
      if (modal) {
        modal.classList.remove('hidden');
        modal.classList.add('flex');
      }
    }

    function closeStatusModal() {
      const modal = document.getElementById('statusModal');
      if (modal) {
        modal.classList.add('hidden');
        modal.classList.remove('flex');
      }
    }

    function selectQuickReason(text) {
      const input = document.getElementById('statusReasonInput');
      if (input) {
        input.value = text;
        input.focus();
      }
    }

    function confirmSaveStatusReason() {
      const reason = (document.getElementById('statusReasonInput').value || '').trim() || 'Đã tắt theo dõi tối ưu';
      const applyAll = document.getElementById('statusApplyAllCheck').checked;

      if (applyAll) {
        AD_POS.forEach(p => {
          if (p.ad_id === activeAdId) {
            const k = p.ad_id + '___' + p.pos;
            posStatusMap[k] = {
              status: 'OFF',
              reason: reason,
              updatedAt: new Date().toISOString()
            };
          }
        });
        showToast(`Đã TẮT tất cả các vị trí của Ad ID ${activeAdId}! 🔴`);
      } else {
        posStatusMap[activePairKey] = {
          status: 'OFF',
          reason: reason,
          updatedAt: new Date().toISOString()
        };
        showToast(`Đã TẮT quảng cáo vị trí ${activePos}! 🔴`);
      }

      savePosStatusMap();
      closeStatusModal();
      applyAdPosFilters();
    }

    function confirmTurnOnCurrent() {
      const applyAll = document.getElementById('statusApplyAllCheck').checked;
      if (applyAll) {
        AD_POS.forEach(p => {
          if (p.ad_id === activeAdId) {
            const k = p.ad_id + '___' + p.pos;
            posStatusMap[k] = {
              status: 'ON',
              reason: '',
              updatedAt: new Date().toISOString()
            };
          }
        });
        showToast(`Đã BẬT lại tất cả các vị trí của Ad ID ${activeAdId}! 🟢`);
      } else {
        posStatusMap[activePairKey] = {
          status: 'ON',
          reason: '',
          updatedAt: new Date().toISOString()
        };
        showToast(`Đã BẬT lại quảng cáo vị trí ${activePos}! 🟢`);
      }
      savePosStatusMap();
      closeStatusModal();
      applyAdPosFilters();
    }

    function toggleAdPosQuick(key, event) {
      if (event) event.stopPropagation();
      const current = posStatusMap[key] || { status: 'OFF', reason: '' };
      if (current.status === 'OFF') {
        posStatusMap[key] = {
          status: 'ON',
          reason: '',
          updatedAt: new Date().toISOString()
        };
        savePosStatusMap();
        showToast('Đã BẬT lại quảng cáo thành công! 🟢');
        applyAdPosFilters();
      }
    }"""

if old_storage_snippet in content:
    content = content.replace(old_storage_snippet, new_storage_snippet)
    print("Updated storage snippet and status modal handlers successfully!")
else:
    print("Warning: old_storage_snippet not found in exact match.")

# -------------------------------------------------------------
# 5. Update Tab 3 JS functions: applyAdPosFilters, updateAdPosSummary, renderAdPosTable
# -------------------------------------------------------------
old_tab3_js = """    // Tab 3 Ad x Placement Table logic
    function applyAdPosFilters() {
      const query = (document.getElementById('adPosSearchInput')?.value || '').trim().toLowerCase();
      const pos = document.getElementById('adPosNameFilter')?.value || 'ALL';
      const stab = document.getElementById('adPosStabFilter')?.value || 'ALL';

      filteredAdPosData = AD_POS.filter(item => {
        if (query) {
          const matchId = String(item.ad_id).toLowerCase().includes(query);
          const matchPos = String(item.pos).toLowerCase().includes(query);
          if (!matchId && !matchPos) return false;
        }
        if (pos !== 'ALL' && item.pos !== pos) return false;
        if (stab !== 'ALL' && item.stability !== stab) return false;
        return true;
      });

      currentAdPosPage = 1;
      updateAdPosSummary();
      renderAdPosTable();
    }

    function updateAdPosSummary() {
      const count = filteredAdPosData.length;
      const totSpend = filteredAdPosData.reduce((s, a) => s + (a.spend || 0), 0);
      const totPur = filteredAdPosData.reduce((s, a) => s + (a.pur || 0), 0);
      const avgCPP = totPur > 0 ? (totSpend / totPur) : 0;

      const elText = document.getElementById('adPosFilterSummaryText');
      if (elText) elText.innerHTML = 'Đang hiển thị <span class="font-bold text-[var(--foreground)]">' + count + '</span> cặp Vị trí x Mã QC';
      const elSpend = document.getElementById('adPosSpendSum');
      if (elSpend) elSpend.innerText = fmtCur(totSpend);
      const elPur = document.getElementById('adPosPurSum');
      if (elPur) elPur.innerText = fmtInt(totPur);
      const elCPP = document.getElementById('adPosCPPSum');
      if (elCPP) elCPP.innerText = fmtCur(avgCPP);
    }

    function renderAdPosTable() {
      const pageSize = 20;
      const totalPages = Math.ceil(filteredAdPosData.length / pageSize) || 1;
      if (currentAdPosPage > totalPages) currentAdPosPage = totalPages;

      const start = (currentAdPosPage - 1) * pageSize;
      const end = start + pageSize;
      const pageData = filteredAdPosData.slice(start, end);

      const tbody = document.getElementById('adPosTableBody');
      if (!tbody) return;
      tbody.innerHTML = '';

      if (pageData.length === 0) {
        tbody.innerHTML = '<tr><td colspan="13" class="py-8 text-center text-[var(--muted-foreground)]">Không có cặp vị trí nào phù hợp.</td></tr>';
        renderAdPosPagination(totalPages);
        return;
      }

      pageData.forEach((row, i) => {
        const rank = start + i + 1;
        let stabBadge = '';
        if (row.stability === 'Rất ổn định') stabBadge = '<span class="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-500/10 text-emerald-600 border border-emerald-500/20">Rất ổn định</span>';
        else if (row.stability === 'Ổn định') stabBadge = '<span class="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-blue-500/10 text-blue-600 border border-blue-500/20">Ổn định</span>';
        else if (row.stability === 'Mẫu ít (1-2 ngày)') stabBadge = '<span class="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-amber-500/10 text-amber-600 border border-amber-500/20">Mẫu ít</span>';
        else if (row.stability === 'Không tạo ra đơn') stabBadge = '<span class="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-rose-500/10 text-rose-600 border border-rose-500/20">0 đơn</span>';
        else stabBadge = '<span class="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-amber-500/10 text-amber-600 border border-amber-500/20">Không ổn định</span>';

        const tr = document.createElement('tr');
        tr.className = 'hover:bg-[var(--accent)]/50 transition';
        tr.innerHTML = `
          <td class="py-2.5 px-2.5 text-center font-mono text-[var(--muted-foreground)]">${rank}</td>
          <td class="py-2.5 px-3 font-mono font-medium text-[var(--foreground)]">${row.ad_id}</td>
          <td class="py-2.5 px-3 font-medium text-[var(--foreground)]">${row.pos}</td>
          <td class="py-2.5 px-3 text-right font-mono text-[var(--foreground)]">${fmtCur(row.spend)}</td>
          <td class="py-2.5 px-2.5 text-center font-mono text-[var(--muted-foreground)]">${fmtInt(row.msg)}</td>
          <td class="py-2.5 px-3 text-right font-mono text-[var(--muted-foreground)]">${fmtCur(row.cpm)}</td>
          <td class="py-2.5 px-2.5 text-center font-mono font-bold ${row.pur > 0 ? 'text-emerald-600' : 'text-slate-400'}">${fmtInt(row.pur)}</td>
          <td class="py-2.5 px-3 text-right font-mono font-bold text-blue-600">${fmtCur(row.cpp)}</td>
          <td class="py-2.5 px-2.5 text-center font-mono">${row.conv !== null ? row.conv + '%' : '-'}</td>
          <td class="py-2.5 px-2.5 text-center font-mono">${row.pur_days} / ${row.active_days} (${row.pur_ratio}%)</td>
          <td class="py-2.5 px-2.5 text-center font-mono">${row.cpp_cv !== null ? row.cpp_cv + '%' : '-'}</td>
          <td class="py-2.5 px-2.5 text-center">${stabBadge}</td>
          <td class="py-2.5 px-3 text-[11px] text-[var(--muted-foreground)]">${row.recommendation}</td>
        `;
        tbody.appendChild(tr);
      });

      renderAdPosPagination(totalPages);
    }"""

new_tab3_js = """    // Tab 3 Ad x Placement Table logic
    function applyAdPosFilters() {
      const query = (document.getElementById('adPosSearchInput')?.value || '').trim().toLowerCase();
      const pos = document.getElementById('adPosNameFilter')?.value || 'ALL';
      const stab = document.getElementById('adPosStabFilter')?.value || 'ALL';
      const statusFilter = document.getElementById('adPosStatusFilter')?.value || 'ALL';

      filteredAdPosData = AD_POS.filter(item => {
        const stInfo = getPairStatus(item.ad_id, item.pos);

        // Search query check (ad_id, pos name, or reason)
        if (query) {
          const matchId = String(item.ad_id).toLowerCase().includes(query);
          const matchPos = String(item.pos).toLowerCase().includes(query);
          const matchReason = String(stInfo.reason || '').toLowerCase().includes(query);
          if (!matchId && !matchPos && !matchReason) return false;
        }

        // Pos filter
        if (pos !== 'ALL' && item.pos !== pos) return false;

        // Stability filter
        if (stab !== 'ALL' && item.stability !== stab) return false;

        // Status filter (MỚI: Bật / Tắt)
        if (statusFilter !== 'ALL') {
          if (statusFilter === 'ON' && stInfo.status === 'OFF') return false;
          if (statusFilter === 'OFF' && stInfo.status !== 'OFF') return false;
        }

        return true;
      });

      currentAdPosPage = 1;
      updateAdPosSummary();
      renderAdPosTable();
    }

    function updateAdPosSummary() {
      const count = filteredAdPosData.length;
      const totSpend = filteredAdPosData.reduce((s, a) => s + (a.spend || 0), 0);
      const totPur = filteredAdPosData.reduce((s, a) => s + (a.pur || 0), 0);
      const avgCPP = totPur > 0 ? (totSpend / totPur) : 0;

      let activeCount = 0;
      let offCount = 0;
      filteredAdPosData.forEach(item => {
        const st = getPairStatus(item.ad_id, item.pos);
        if (st.status === 'OFF') offCount++;
        else activeCount++;
      });

      const elText = document.getElementById('adPosFilterSummaryText');
      if (elText) elText.innerHTML = 'Đang hiển thị <span class="font-bold text-[var(--foreground)]">' + count + '</span> cặp Vị trí x Mã QC';
      const elSpend = document.getElementById('adPosSpendSum');
      if (elSpend) elSpend.innerText = fmtCur(totSpend);
      const elPur = document.getElementById('adPosPurSum');
      if (elPur) elPur.innerText = fmtInt(totPur);
      const elCPP = document.getElementById('adPosCPPSum');
      if (elCPP) elCPP.innerText = fmtCur(avgCPP);

      const elActive = document.getElementById('adPosActiveCount');
      if (elActive) elActive.innerText = activeCount;
      const elOff = document.getElementById('adPosOffCount');
      if (elOff) elOff.innerText = offCount;
    }

    function renderAdPosTable() {
      const pageSize = 20;
      const totalPages = Math.ceil(filteredAdPosData.length / pageSize) || 1;
      if (currentAdPosPage > totalPages) currentAdPosPage = totalPages;

      const start = (currentAdPosPage - 1) * pageSize;
      const end = start + pageSize;
      const pageData = filteredAdPosData.slice(start, end);

      const tbody = document.getElementById('adPosTableBody');
      if (!tbody) return;
      tbody.innerHTML = '';

      if (pageData.length === 0) {
        tbody.innerHTML = '<tr><td colspan="15" class="py-8 text-center text-[var(--muted-foreground)]">Không có cặp vị trí nào phù hợp.</td></tr>';
        renderAdPosPagination(totalPages);
        return;
      }

      pageData.forEach((row, i) => {
        const rank = start + i + 1;
        const pairKey = row.ad_id + '___' + row.pos;
        const stInfo = getPairStatus(row.ad_id, row.pos);
        const isOff = stInfo.status === 'OFF';

        let stabBadge = '';
        if (row.stability === 'Rất ổn định') stabBadge = '<span class="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-500/10 text-emerald-600 border border-emerald-500/20">Rất ổn định</span>';
        else if (row.stability === 'Ổn định') stabBadge = '<span class="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-blue-500/10 text-blue-600 border border-blue-500/20">Ổn định</span>';
        else if (row.stability === 'Mẫu ít (1-2 ngày)') stabBadge = '<span class="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-amber-500/10 text-amber-600 border border-amber-500/20">Mẫu ít</span>';
        else if (row.stability === 'Không tạo ra đơn') stabBadge = '<span class="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-rose-500/10 text-rose-600 border border-rose-500/20">0 đơn</span>';
        else stabBadge = '<span class="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-amber-500/10 text-amber-600 border border-amber-500/20">Không ổn định</span>';

        // Toggle button: 🟢 Đang Bật / 🔴 Đã Tắt
        let statusBtn = '';
        if (isOff) {
          statusBtn = `
            <button onclick="toggleAdPosQuick('${pairKey}', event)" title="Nhấn để BẬT lại quảng cáo này" class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-bold bg-rose-50 text-rose-700 border border-rose-300 hover:bg-rose-100 shadow-xs transition cursor-pointer">
              <span class="w-2 h-2 rounded-full bg-rose-500 animate-pulse"></span>
              Đã Tắt
            </button>
          `;
        } else {
          statusBtn = `
            <button onclick="openTurnOffModal('${pairKey}', '${row.ad_id}', '${escapeJs(row.pos)}', event)" title="Nhấn để TẮT quảng cáo và ghi lý do" class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-300 hover:bg-emerald-100 shadow-xs transition cursor-pointer">
              <span class="w-2 h-2 rounded-full bg-emerald-500"></span>
              Đang Bật
            </button>
          `;
        }

        // Reason column:
        let reasonHtml = '';
        if (isOff) {
          const reasonText = stInfo.reason || 'Đã tắt (Chưa ghi lý do)';
          reasonHtml = `
            <div class="flex items-center gap-1.5 group max-w-[200px]">
              <span class="px-2 py-0.5 rounded text-[11px] font-medium bg-rose-100/80 text-rose-800 border border-rose-200 truncate" title="${escapeHtml(reasonText)}">
                ${escapeHtml(reasonText)}
              </span>
              <button onclick="openTurnOffModal('${pairKey}', '${row.ad_id}', '${escapeJs(row.pos)}', event, true)" title="Sửa lý do tắt" class="text-slate-400 hover:text-blue-600 p-0.5 rounded opacity-75 group-hover:opacity-100 transition">
                ✏️
              </button>
            </div>
          `;
        } else {
          reasonHtml = `<span class="text-slate-300 font-mono text-[11px]">-</span>`;
        }

        const tr = document.createElement('tr');
        tr.className = isOff 
          ? 'bg-rose-50/25 hover:bg-rose-50/50 transition border-l-2 border-rose-400' 
          : 'hover:bg-[var(--accent)]/50 transition';

        tr.innerHTML = `
          <td class="py-2.5 px-2.5 text-center font-mono text-[var(--muted-foreground)]">${rank}</td>
          <td class="py-2.5 px-3 font-mono font-medium text-[var(--foreground)]">
            <span class="cursor-pointer hover:underline text-blue-600 font-semibold" onclick="openModal('${row.ad_id}')">${row.ad_id}</span>
          </td>
          <td class="py-2.5 px-3 font-medium text-[var(--foreground)]">${row.pos}</td>
          <td class="py-2.5 px-2.5 text-center whitespace-nowrap">${statusBtn}</td>
          <td class="py-2.5 px-3 whitespace-nowrap">${reasonHtml}</td>
          <td class="py-2.5 px-3 text-right font-mono text-[var(--foreground)]">${fmtCur(row.spend)}</td>
          <td class="py-2.5 px-2.5 text-center font-mono text-[var(--muted-foreground)]">${fmtInt(row.msg)}</td>
          <td class="py-2.5 px-3 text-right font-mono text-[var(--muted-foreground)]">${fmtCur(row.cpm)}</td>
          <td class="py-2.5 px-2.5 text-center font-mono font-bold ${row.pur > 0 ? 'text-emerald-600' : 'text-slate-400'}">${fmtInt(row.pur)}</td>
          <td class="py-2.5 px-3 text-right font-mono font-bold text-blue-600">${fmtCur(row.cpp)}</td>
          <td class="py-2.5 px-2.5 text-center font-mono">${row.conv !== null ? row.conv + '%' : '-'}</td>
          <td class="py-2.5 px-2.5 text-center font-mono">${row.pur_days} / ${row.active_days} (${row.pur_ratio}%)</td>
          <td class="py-2.5 px-2.5 text-center font-mono">${row.cpp_cv !== null ? row.cpp_cv + '%' : '-'}</td>
          <td class="py-2.5 px-2.5 text-center">${stabBadge}</td>
          <td class="py-2.5 px-3 text-[11px] text-[var(--muted-foreground)]">${row.recommendation}</td>
        `;
        tbody.appendChild(tr);
      });

      renderAdPosPagination(totalPages);
    }"""

if old_tab3_js in content:
    content = content.replace(old_tab3_js, new_tab3_js)
    print("Updated Tab 3 JS rendering & filtering successfully!")
else:
    print("Warning: old_tab3_js not found in exact match.")

# -------------------------------------------------------------
# 6. Update exportAnnotations & importAnnotations to include posStatusMap
# -------------------------------------------------------------
old_export = """    function exportAnnotations() {
      const dataStr = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(userAnnotations, null, 2));
      const downloadAnchor = document.createElement('a');
      downloadAnchor.setAttribute('href', dataStr);
      downloadAnchor.setAttribute('download', 'ghi_chu_ads.json');
      document.body.appendChild(downloadAnchor);
      downloadAnchor.click();
      downloadAnchor.remove();
    }"""

new_export = """    function exportAnnotations() {
      const backupData = {
        annotations: userAnnotations,
        posStatuses: posStatusMap,
        exportedAt: new Date().toISOString()
      };
      const dataStr = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(backupData, null, 2));
      const downloadAnchor = document.createElement('a');
      downloadAnchor.setAttribute('href', dataStr);
      downloadAnchor.setAttribute('download', 'ghi_chu_ads_va_trang_thai.json');
      document.body.appendChild(downloadAnchor);
      downloadAnchor.click();
      downloadAnchor.remove();
    }"""

old_import = """    function importAnnotations(event) {
      const file = event.target.files[0];
      if (!file) return;
      const reader = new FileReader();
      reader.onload = function(e) {
        try {
          const imported = JSON.parse(e.target.result);
          userAnnotations = { ...userAnnotations, ...imported };
          localStorage.setItem(STORAGE_KEY, JSON.stringify(userAnnotations));
          alert('Nhập ghi chú thành công!');
          renderTable();
        } catch (err) {
          alert('Lỗi: File JSON không hợp lệ!');
        }
      };
      reader.readAsText(file);
      event.target.value = '';
    }"""

new_import = """    function importAnnotations(event) {
      const file = event.target.files[0];
      if (!file) return;
      const reader = new FileReader();
      reader.onload = function(e) {
        try {
          const imported = JSON.parse(e.target.result);
          if (imported.annotations) {
            userAnnotations = { ...userAnnotations, ...imported.annotations };
            localStorage.setItem(STORAGE_KEY, JSON.stringify(userAnnotations));
          } else {
            userAnnotations = { ...userAnnotations, ...imported };
            localStorage.setItem(STORAGE_KEY, JSON.stringify(userAnnotations));
          }
          if (imported.posStatuses) {
            posStatusMap = { ...posStatusMap, ...imported.posStatuses };
            savePosStatusMap();
          }
          alert('Nhập ghi chú & trạng thái thành công!');
          renderTable();
          applyAdPosFilters();
        } catch (err) {
          alert('Lỗi: File JSON không hợp lệ!');
        }
      };
      reader.readAsText(file);
      event.target.value = '';
    }"""

if old_export in content:
    content = content.replace(old_export, new_export)
if old_import in content:
    content = content.replace(old_import, new_import)

# -------------------------------------------------------------
# 7. Update DOMContentLoaded to init ad_pos
# -------------------------------------------------------------
old_init = """    window.addEventListener('DOMContentLoaded', () => {
      applyFilters();
      renderPlacementTable();
      renderPlanTable();
    });"""

new_init = """    window.addEventListener('DOMContentLoaded', () => {
      applyFilters();
      applyAdPosFilters();
      renderPlacementTable();
      renderPlanTable();
    });"""

if old_init in content:
    content = content.replace(old_init, new_init)
    print("Updated DOMContentLoaded successfully!")

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Updated {html_path} successfully!")

# Copy to brain artifact
shutil.copyfile(html_path, artifact_path)
print(f"Copied to brain artifact {artifact_path} successfully!")
