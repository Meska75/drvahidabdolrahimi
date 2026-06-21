/**
 * ویجت رزرو نوبت آنلاین — پذیرش24
 * تقویم شمسی (جلالی) با دریافت خودکار نوبت‌های ماه از API
 *
 * data-proxy-url : آدرس پروکسی Django  (مثال: /booking-proxy/)
 * data-lang      : زبان رابط کاربری   (fa | en | ar)
 */
(function () {
    'use strict';

    /* ================================================================
       الگوریتم تبدیل تاریخ جلالی (شمسی)
       منبع: Roozbeh Pournader — اجرای خالص JS بدون وابستگی خارجی
    ================================================================ */
    function toJalali(gy, gm, gd) {
        const g2d = _g2d(gy, gm, gd);
        return _d2j(g2d);
    }

    function fromJalali(jy, jm, jd) {
        const jDays = _j2d(jy, jm, jd);
        return _d2g(jDays);
    }

    function _g2d(gy, gm, gd) {
        let y = gy - 1600, m = gm - 1, d = gd - 1;
        let dn = 365 * y + Math.floor((y + 3) / 4) - Math.floor((y + 99) / 100) + Math.floor((y + 399) / 400);
        const gDays = [31, (gy % 4 === 0 && (gy % 100 !== 0 || gy % 400 === 0)) ? 29 : 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
        for (let i = 0; i < m; i++) dn += gDays[i];
        return dn + d;
    }

    function _d2j(dn) {
        dn -= 79;
        const np = Math.floor(dn / 12053); dn %= 12053;
        let jy = 979 + 33 * np + 4 * Math.floor(dn / 1461);
        dn %= 1461;
        if (dn >= 366) { jy += Math.floor((dn - 1) / 365); dn = (dn - 1) % 365; }
        const jDays = [31, 31, 31, 31, 31, 31, 30, 30, 30, 30, 30, 29];
        let jm = 0;
        for (; jm < 11 && dn >= jDays[jm]; jm++) dn -= jDays[jm];
        return [jy, jm + 1, dn + 1];
    }

    function _j2d(jy, jm, jd) {
        const jDays = [31, 31, 31, 31, 31, 31, 30, 30, 30, 30, 30, 29];
        let dn = 365 * (jy - 979) + Math.floor((jy - 979) / 4) * 8 - Math.floor((jy - 979 + 1) / 33) * 8;
        for (let i = 0; i < jm - 1; i++) dn += jDays[i];
        dn += jd + 78;
        return dn;
    }

    function _d2g(dn) {
        let y = 400 * Math.floor(dn / 146097); dn %= 146097;
        if (dn > 36524) { y += 100 * Math.floor(--dn / 36524); dn %= 36524; if (dn >= 365) dn++; }
        y += 4 * Math.floor(dn / 1461); dn %= 1461;
        if (dn > 365) { y += Math.floor((--dn) / 365); dn %= 365; }
        const isLeap = (y % 4 === 0 && (y % 100 !== 0 || y % 400 === 0));
        const gDays = [31, isLeap ? 29 : 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
        let gm = 0;
        for (; gm < 12 && dn >= gDays[gm]; gm++) dn -= gDays[gm];
        return [y + 1600, gm + 1, dn + 1];
    }

    function jalaliDaysInMonth(jy, jm) {
        if (jm <= 6) return 31;
        if (jm <= 11) return 30;
        /* اسفند: بررسی سال کبیسه */
        const y = jy - 979;
        return (((y % 33) === 1 || (y % 33) === 5 || (y % 33) === 9 || (y % 33) === 13 ||
                 (y % 33) === 17 || (y % 33) === 22 || (y % 33) === 26 || (y % 33) === 30)) ? 30 : 29;
    }

    function pad(n) { return String(n).padStart(2, '0'); }

    /* تاریخ Gregorian از تاریخ Jalali */
    function jalaliToISO(jy, jm, jd) {
        const [gy, gm, gd] = fromJalali(jy, jm, jd);
        return `${gy}-${pad(gm)}-${pad(gd)}`;
    }

    /* ================================================================
       ترجمه‌ها
    ================================================================ */
    const I18N = {
        fa: {
            months: ['فروردین','اردیبهشت','خرداد','تیر','مرداد','شهریور','مهر','آبان','آذر','دی','بهمن','اسفند'],
            weekdays: ['ش','ی','د','س','چ','پ','ج'],    /* شنبه اول */
            weekdaysFull: ['شنبه','یک‌شنبه','دوشنبه','سه‌شنبه','چهارشنبه','پنجشنبه','جمعه'],
            step1: 'انتخاب روز', step2: 'انتخاب ساعت', step3: 'اطلاعات بیمار', step4: 'تأیید',
            loading_month: 'در حال دریافت نوبت‌ها...', loading_slots: 'در حال بارگذاری ساعت‌ها...',
            no_slots: 'برای این روز نوبت خالی وجود ندارد.',
            has_slots: 'نوبت دارد', no_slot_day: 'نوبت ندارد', today: 'امروز',
            label_name: 'نام و نام خانوادگی', label_phone: 'شماره موبایل',
            label_national: 'کد ملی', hint_national: 'اختیاری', hint_phone: 'مثال: 09123456789',
            btn_submit: 'ثبت نوبت', btn_back: 'بازگشت', btn_new: 'رزرو نوبت جدید',
            success_title: 'نوبت شما با موفقیت ثبت شد!',
            success_sub: 'لطفاً در روز و ساعت مقرر به مطب مراجعه فرمایید.',
            err_required: 'این فیلد الزامی است.', err_phone: 'شماره موبایل نامعتبر است. (۰۹ + ۹ رقم)',
            err_service: 'خطا در ارتباط با سرور. لطفاً دوباره امتحان کنید.',
            lbl_date: 'تاریخ', lbl_time: 'ساعت',
        },
        en: {
            months: ['January','February','March','April','May','June','July','August','September','October','November','December'],
            weekdays: ['Su','Mo','Tu','We','Th','Fr','Sa'],
            weekdaysFull: ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'],
            step1: 'Select Day', step2: 'Select Time', step3: 'Patient Info', step4: 'Confirm',
            loading_month: 'Loading appointments...', loading_slots: 'Loading time slots...',
            no_slots: 'No appointments available for this day.',
            has_slots: 'Available', no_slot_day: 'No slots', today: 'Today',
            label_name: 'Full Name', label_phone: 'Mobile Number',
            label_national: 'National ID', hint_national: 'Optional', hint_phone: 'e.g. 09123456789',
            btn_submit: 'Book Appointment', btn_back: 'Back', btn_new: 'Book Another',
            success_title: 'Appointment Booked Successfully!',
            success_sub: 'Please arrive at the clinic on the scheduled date and time.',
            err_required: 'This field is required.', err_phone: 'Invalid mobile number.',
            err_service: 'Server error. Please try again.',
            lbl_date: 'Date', lbl_time: 'Time',
        },
        ar: {
            months: ['يناير','فبراير','مارس','أبريل','مايو','يونيو','يوليو','أغسطس','سبتمبر','أكتوبر','نوفمبر','ديسمبر'],
            weekdays: ['أح','اث','ث','أر','خ','ج','س'],
            weekdaysFull: ['الأحد','الاثنين','الثلاثاء','الأربعاء','الخميس','الجمعة','السبت'],
            step1: 'اختر اليوم', step2: 'اختر الوقت', step3: 'بيانات المريض', step4: 'التأكيد',
            loading_month: 'جارٍ تحميل المواعيد...', loading_slots: 'جارٍ تحميل الأوقات...',
            no_slots: 'لا توجد مواعيد متاحة لهذا اليوم.',
            has_slots: 'متاح', no_slot_day: 'غير متاح', today: 'اليوم',
            label_name: 'الاسم الكامل', label_phone: 'رقم الجوال',
            label_national: 'رقم الهوية', hint_national: 'اختياري', hint_phone: 'مثال: 09123456789',
            btn_submit: 'تأكيد الحجز', btn_back: 'رجوع', btn_new: 'حجز جديد',
            success_title: 'تم حجز موعدك بنجاح!',
            success_sub: 'يرجى الحضور إلى العيادة في الموعد المحدد.',
            err_required: 'هذا الحقل مطلوب.', err_phone: 'رقم الجوال غير صحيح.',
            err_service: 'خطأ في الاتصال. حاول مرة أخرى.',
            lbl_date: 'التاريخ', lbl_time: 'الوقت',
        },
    };

    /* ================================================================
       ابتکار اصلی: نمایش تعداد نوبت‌های خالی روی هر روز تقویم
    ================================================================ */
    function initBookingWidget(container) {
        const proxyUrl = container.dataset.proxyUrl || '/booking-proxy/';
        const lang     = container.dataset.lang     || 'fa';
        const t        = I18N[lang] || I18N.fa;
        const isRTL    = (lang === 'fa' || lang === 'ar');

        /* ـ وضعیت جاری ـ */
        const state = {
            /* کدام ماه تقویم نمایش داده می‌شود */
            viewGYear: 0, viewGMonth: 0,   /* Gregorian */
            viewJYear: 0, viewJMonth: 0,   /* Jalali (فقط fa) */

            /* نوبت‌های دریافت‌شده کش می‌شوند — کلید: "YYYY-MM" */
            slotsCache: {},

            selectedISO: null,            /* تاریخ انتخاب‌شده  YYYY-MM-DD */
            selectedSlot: null,           /* { id, display } */
        };

        /* ـ امروز ـ */
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        const todayISO = `${today.getFullYear()}-${pad(today.getMonth()+1)}-${pad(today.getDate())}`;

        /* مقداردهی view به ماه جاری */
        if (lang === 'fa') {
            const [jy, jm] = toJalali(today.getFullYear(), today.getMonth()+1, today.getDate());
            state.viewJYear = jy; state.viewJMonth = jm;
        } else {
            state.viewGYear = today.getFullYear(); state.viewGMonth = today.getMonth()+1;
        }

        /* ================================================================
           ساخت ساختار HTML اولیه
        ================================================================ */
        container.innerHTML = `
        <div class="bk-steps-bar">
          <div class="bk-step active" data-step="1"><span class="bk-step-n">1</span>${t.step1}</div>
          <div class="bk-step"        data-step="2"><span class="bk-step-n">2</span>${t.step2}</div>
          <div class="bk-step"        data-step="3"><span class="bk-step-n">3</span>${t.step3}</div>
          <div class="bk-step"        data-step="4"><span class="bk-step-n">4</span>${t.step4}</div>
        </div>

        <div class="bk-body">

          <!-- ===== مرحله ۱: تقویم ===== -->
          <div class="bk-panel active" id="bkPanel1">
            <div class="bk-cal-wrap">
              <!-- هدر تقویم -->
              <div class="bk-cal-header">
                <button class="bk-cal-nav" id="bkPrevMonth" aria-label="ماه قبل">
                  <i class="fa fa-chevron-${isRTL ? 'right' : 'left'}"></i>
                </button>
                <div class="bk-cal-title" id="bkCalTitle"></div>
                <button class="bk-cal-nav" id="bkNextMonth" aria-label="ماه بعد">
                  <i class="fa fa-chevron-${isRTL ? 'left' : 'right'}"></i>
                </button>
              </div>
              <!-- legend -->
              <div class="bk-cal-legend">
                <span class="leg-item"><span class="leg-dot leg-avail"></span>${t.has_slots}</span>
                <span class="leg-item"><span class="leg-dot leg-none"></span>${t.no_slot_day}</span>
              </div>
              <!-- بارگذاری -->
              <div class="bk-cal-loading" id="bkCalLoading" style="display:none">
                <i class="fa fa-spinner fa-spin"></i> ${t.loading_month}
              </div>
              <!-- شبکه روزهای هفته -->
              <div class="bk-cal-days-header" id="bkCalDaysHeader"></div>
              <!-- شبکه روزها -->
              <div class="bk-cal-grid" id="bkCalGrid"></div>
            </div>
            <div class="bk-error-box" id="bkErr1"></div>
          </div>

          <!-- ===== مرحله ۲: انتخاب ساعت ===== -->
          <div class="bk-panel" id="bkPanel2">
            <div class="bk-summary" id="bkSummary2"></div>
            <div id="bkSlotsWrap">
              <div class="bk-loading" id="bkSlotsLoading" style="display:none">
                <i class="fa fa-spinner fa-spin"></i> ${t.loading_slots}
              </div>
              <div class="bk-time-grid" id="bkTimeGrid"></div>
              <div class="bk-no-slots" id="bkNoSlots" style="display:none">
                <i class="fa fa-calendar-times-o"></i><p>${t.no_slots}</p>
              </div>
            </div>
            <div class="bk-error-box" id="bkErr2"></div>
            <div class="bk-actions">
              <button class="bk-btn-back" id="bkBack1"><i class="fa fa-arrow-${isRTL?'right':'left'}"></i> ${t.btn_back}</button>
            </div>
          </div>

          <!-- ===== مرحله ۳: اطلاعات بیمار ===== -->
          <div class="bk-panel" id="bkPanel3">
            <div class="bk-summary" id="bkSummary3"></div>
            <div class="bk-field">
              <label for="bkName">${t.label_name} <span class="bk-req">*</span></label>
              <input type="text" id="bkName" maxlength="100" autocomplete="name">
            </div>
            <div class="bk-field">
              <label for="bkPhone">${t.label_phone} <span class="bk-req">*</span></label>
              <input type="tel" id="bkPhone" maxlength="11" placeholder="${t.hint_phone}">
            </div>
            <div class="bk-field">
              <label for="bkNational">${t.label_national} <span class="bk-hint">${t.hint_national}</span></label>
              <input type="text" id="bkNational" maxlength="10">
            </div>
            <div class="bk-error-box" id="bkErr3"></div>
            <div class="bk-actions">
              <button class="bk-btn-primary" id="bkSubmit">
                <i class="fa fa-calendar-check-o"></i> ${t.btn_submit}
              </button>
              <button class="bk-btn-back" id="bkBack2"><i class="fa fa-arrow-${isRTL?'right':'left'}"></i> ${t.btn_back}</button>
            </div>
          </div>

          <!-- ===== مرحله ۴: تأیید ===== -->
          <div class="bk-panel" id="bkPanel4">
            <div class="bk-success">
              <div class="bk-success-icon"><i class="fa fa-check"></i></div>
              <h3>${t.success_title}</h3>
              <p>${t.success_sub}</p>
              <div class="bk-confirm-card" id="bkConfirmCard"></div>
              <button class="bk-btn-new" id="bkNew">${t.btn_new}</button>
            </div>
          </div>

        </div>`;

        /* ـ رفرنس‌ها ـ */
        const $ = id => container.querySelector(id);
        const steps     = container.querySelectorAll('.bk-step');
        const panels    = container.querySelectorAll('.bk-panel');
        const calTitle  = $('#bkCalTitle');
        const calGrid   = $('#bkCalGrid');
        const calHdr    = $('#bkCalDaysHeader');
        const calLoad   = $('#bkCalLoading');
        const timeGrid  = $('#bkTimeGrid');
        const slotsLoad = $('#bkSlotsLoading');
        const noSlots   = $('#bkNoSlots');
        const summary2  = $('#bkSummary2');
        const summary3  = $('#bkSummary3');
        const confirmCard = $('#bkConfirmCard');
        const inName    = $('#bkName');
        const inPhone   = $('#bkPhone');
        const inNat     = $('#bkNational');
        const btnSubmit = $('#bkSubmit');

        /* ================================================================
           سوئیچ مرحله
        ================================================================ */
        function goTo(n) {
            panels.forEach((p, i) => p.classList.toggle('active', i+1 === n));
            steps.forEach((s, i) => {
                s.classList.remove('active', 'done');
                if (i+1 < n)  s.classList.add('done');
                if (i+1 === n) s.classList.add('active');
            });
            container.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }

        function showErr(id, msg) {
            const el = $(id);
            if (!el) return;
            el.innerHTML = `<i class="fa fa-exclamation-triangle"></i> ${msg}`;
            el.style.display = 'block';
        }
        function clearErr(id) { const el=$(id); if(el){el.style.display='none';el.innerHTML='';} }

        /* ================================================================
           ساخت هدر روزهای هفته
        ================================================================ */
        function buildWeekHeader() {
            /* fa/ar: شنبه اول (JS getDay: شنبه=6) → ترتیب: 6,0,1,2,3,4,5 */
            /* en: یکشنبه اول → ترتیب: 0,1,2,3,4,5,6 */
            const order = isRTL ? [6,0,1,2,3,4,5] : [0,1,2,3,4,5,6];
            calHdr.innerHTML = order.map(i =>
                `<div class="bk-cal-wd">${t.weekdays[isRTL ? [6,0,1,2,3,4,5].indexOf(i) : i]}</div>`
            ).join('');
        }

        /* ================================================================
           دریافت نوبت‌های یک ماه کامل از API
        ================================================================ */
        function fetchMonth(gy, gm) {
            const key = `${gy}-${pad(gm)}`;
            if (state.slotsCache[key] !== undefined) {
                renderCalendar();
                return;
            }
            calLoad.style.display = 'flex';
            calGrid.style.opacity = '0.4';

            fetch(`${proxyUrl}?action=month&year=${gy}&month=${gm}`)
                .then(r => r.json())
                .then(data => {
                    /* داده را نرمالایز می‌کنیم — هر API ممکن است ساختار متفاوتی داشته باشد */
                    const raw = Array.isArray(data) ? data : (data.data || data.appointments || []);
                    /* نگاشت: تاریخ → تعداد نوبت خالی */
                    const map = {};
                    raw.forEach(slot => {
                        const d = slot.date || (slot.time ? slot.time.split('T')[0] : null);
                        if (!d) return;
                        if (slot.available === false) return;
                        map[d] = (map[d] || 0) + 1;
                    });
                    state.slotsCache[key] = map;
                    calLoad.style.display = 'none';
                    calGrid.style.opacity = '1';
                    renderCalendar();
                })
                .catch(() => {
                    /* اگر API جواب نداد، ماه را خالی می‌گذاریم تا تقویم نمایش داده شود */
                    state.slotsCache[key] = {};
                    calLoad.style.display = 'none';
                    calGrid.style.opacity = '1';
                    renderCalendar();
                });
        }

        /* ================================================================
           رندر تقویم
        ================================================================ */
        function renderCalendar() {
            calGrid.innerHTML = '';
            let cacheKey, monthName, year;

            if (lang === 'fa') {
                const jy = state.viewJYear, jm = state.viewJMonth;
                const [gy, gm] = fromJalali(jy, jm, 1);
                cacheKey = `${gy}-${pad(gm)}`;
                /* ممکن است span به ماه بعدی Gregorian برسد */
                const [gy2, gm2] = fromJalali(jy, jm, jalaliDaysInMonth(jy, jm));
                const key2 = `${gy2}-${pad(gm2)}`;
                if (!state.slotsCache[key2]) state.slotsCache[key2] = {};
                if (!state.slotsCache[cacheKey]) { fetchMonth(gy, gm); return; }

                monthName = t.months[jm-1];
                year = jy;

                /* عنوان تقویم */
                calTitle.textContent = `${monthName} ${toFarsiNum(jy)}`;

                /* پیدا کردن روز اول ماه Jalali */
                const firstGreg = new Date(gy, gm-1, 1);
                /* روز هفته در حالت شنبه-اول: 6→0, 0→1, 1→2, ... */
                const firstWD = firstGreg.getDay(); /* 0=Sun..6=Sat */
                const offset = (firstWD + 1) % 7;  /* شنبه=6→0, یک‌شنبه=0→1 */

                /* سلول‌های خالی قبل */
                for (let i = 0; i < offset; i++) calGrid.appendChild(emptyCell());

                /* روزهای ماه */
                const totalDays = jalaliDaysInMonth(jy, jm);
                for (let jd = 1; jd <= totalDays; jd++) {
                    const iso = jalaliToISO(jy, jm, jd);
                    const slotsCount = (state.slotsCache[cacheKey] || {})[iso] ||
                                       (state.slotsCache[key2]     || {})[iso] || 0;
                    calGrid.appendChild(dayCell(iso, toFarsiNum(jd), slotsCount, jy, jm, jd));
                }

            } else {
                /* EN / AR: تقویم میلادی */
                const gy = state.viewGYear, gm = state.viewGMonth;
                cacheKey = `${gy}-${pad(gm)}`;
                if (!state.slotsCache[cacheKey]) { fetchMonth(gy, gm); return; }

                monthName = t.months[gm-1];
                year = gy;
                calTitle.textContent = `${monthName} ${year}`;

                const firstWD = new Date(gy, gm-1, 1).getDay(); /* 0=Sun */
                for (let i = 0; i < firstWD; i++) calGrid.appendChild(emptyCell());

                const daysInMonth = new Date(gy, gm, 0).getDate();
                for (let gd = 1; gd <= daysInMonth; gd++) {
                    const iso = `${gy}-${pad(gm)}-${pad(gd)}`;
                    const slotsCount = (state.slotsCache[cacheKey] || {})[iso] || 0;
                    calGrid.appendChild(dayCell(iso, gd, slotsCount));
                }
            }
        }

        function emptyCell() {
            const el = document.createElement('div');
            el.className = 'bk-cal-cell bk-cal-empty';
            return el;
        }

        function dayCell(iso, label, slotsCount, jy, jm, jd) {
            const el = document.createElement('div');
            const isToday   = (iso === todayISO);
            const isPast    = (iso < todayISO);
            const hasSlots  = (slotsCount > 0);
            const isSelected = (iso === state.selectedISO);

            el.className = 'bk-cal-cell' +
                (isPast    ? ' bk-past'    : '') +
                (isToday   ? ' bk-today'   : '') +
                (hasSlots  ? ' bk-has-slots' : ' bk-no-slots-day') +
                (isSelected ? ' bk-selected' : '') +
                (!isPast && hasSlots ? ' bk-clickable' : '');

            el.innerHTML = `<span class="bk-day-num">${label}</span>` +
                (hasSlots && !isPast ? `<span class="bk-slots-dot" title="${slotsCount} ${t.has_slots}"></span>` : '');

            if (!isPast && hasSlots) {
                el.addEventListener('click', () => onDayClick(iso));
            }
            return el;
        }

        function toFarsiNum(n) {
            return String(n).replace(/\d/g, d => '۰۱۲۳۴۵۶۷۸۹'[d]);
        }

        /* ================================================================
           ناوبری ماه
        ================================================================ */
        function prevMonth() {
            if (lang === 'fa') {
                state.viewJMonth--;
                if (state.viewJMonth < 1) { state.viewJMonth = 12; state.viewJYear--; }
                const [gy, gm] = fromJalali(state.viewJYear, state.viewJMonth, 1);
                fetchMonth(gy, gm);
            } else {
                state.viewGMonth--;
                if (state.viewGMonth < 1) { state.viewGMonth = 12; state.viewGYear--; }
                fetchMonth(state.viewGYear, state.viewGMonth);
            }
        }

        function nextMonth() {
            if (lang === 'fa') {
                state.viewJMonth++;
                if (state.viewJMonth > 12) { state.viewJMonth = 1; state.viewJYear++; }
                const [gy, gm] = fromJalali(state.viewJYear, state.viewJMonth, 1);
                fetchMonth(gy, gm);
            } else {
                state.viewGMonth++;
                if (state.viewGMonth > 12) { state.viewGMonth = 1; state.viewGYear++; }
                fetchMonth(state.viewGYear, state.viewGMonth);
            }
        }

        /* ================================================================
           کلیک روی روز → دریافت ساعت‌ها
        ================================================================ */
        function onDayClick(iso) {
            state.selectedISO = iso;
            renderCalendar(); /* re-render تا selected نمایش داده شود */
            loadSlots(iso);
        }

        function formatISODisplay(iso) {
            const d = new Date(iso + 'T00:00:00');
            if (lang === 'fa') {
                const [jy, jm, jd] = toJalali(d.getFullYear(), d.getMonth()+1, d.getDate());
                return `${toFarsiNum(jd)} ${t.months[jm-1]} ${toFarsiNum(jy)}`;
            } else if (lang === 'ar') {
                return d.toLocaleDateString('ar-SA', { year:'numeric', month:'long', day:'numeric' });
            }
            return d.toLocaleDateString('en-US', { year:'numeric', month:'long', day:'numeric' });
        }

        /* ================================================================
           دریافت ساعت‌های یک روز
        ================================================================ */
        function loadSlots(iso) {
            goTo(2);
            summary2.innerHTML = `<i class="fa fa-calendar"></i> ${formatISODisplay(iso)}`;
            timeGrid.innerHTML = '';
            noSlots.style.display = 'none';
            slotsLoad.style.display = 'flex';
            clearErr('#bkErr2');

            fetch(`${proxyUrl}?action=slots&date=${iso}`)
                .then(r => r.json())
                .then(data => {
                    slotsLoad.style.display = 'none';
                    const slots = Array.isArray(data) ? data : (data.data || data.appointments || []);
                    const avail = slots.filter(s => s.available !== false);
                    if (!avail.length) { noSlots.style.display = 'flex'; return; }
                    avail.forEach(slot => {
                        const btn = document.createElement('button');
                        btn.className = 'bk-time-slot';
                        btn.dataset.id   = slot.id || slot.appointment_id || '';
                        const timeLabel  = slot.time || slot.start_time || slot.display_time || '—';
                        btn.textContent  = lang === 'fa' ? toFarsiNum(timeLabel) : timeLabel;
                        btn.addEventListener('click', function() {
                            timeGrid.querySelectorAll('.bk-time-slot').forEach(b => b.classList.remove('selected'));
                            this.classList.add('selected');
                            state.selectedSlot = { id: this.dataset.id, display: this.textContent };
                            summary3.innerHTML =
                                `<i class="fa fa-calendar"></i> ${formatISODisplay(iso)} &nbsp;|&nbsp; ` +
                                `<i class="fa fa-clock-o"></i> ${state.selectedSlot.display}`;
                            goTo(3);
                        });
                        timeGrid.appendChild(btn);
                    });
                })
                .catch(() => { slotsLoad.style.display='none'; showErr('#bkErr2', t.err_service); });
        }

        /* ================================================================
           اعتبارسنجی + ثبت نوبت
        ================================================================ */
        function validate() {
            clearErr('#bkErr3');
            inName.classList.remove('error'); inPhone.classList.remove('error');
            if (!inName.value.trim())  { inName.classList.add('error');  showErr('#bkErr3', t.err_required); return false; }
            if (!/^09\d{9}$/.test(inPhone.value.trim())) { inPhone.classList.add('error'); showErr('#bkErr3', t.err_phone); return false; }
            return true;
        }

        function submitBooking() {
            if (!validate()) return;
            btnSubmit.disabled = true;
            btnSubmit.innerHTML = '<i class="fa fa-spinner fa-spin"></i>';
            const body = { appointment_id: state.selectedSlot.id, name: inName.value.trim(), phone: inPhone.value.trim(), national_code: inNat.value.trim() };
            fetch(`${proxyUrl}?action=book`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') },
                body: JSON.stringify(body),
            })
            .then(r => r.json())
            .then(data => {
                if (data.error) { showErr('#bkErr3', data.message || t.err_service); btnSubmit.disabled=false; btnSubmit.innerHTML=`<i class="fa fa-calendar-check-o"></i> ${t.btn_submit}`; return; }
                confirmCard.innerHTML =
                    `<div class="bk-confirm-row"><span>${t.lbl_date}</span><span>${formatISODisplay(state.selectedISO)}</span></div>` +
                    `<div class="bk-confirm-row"><span>${t.lbl_time}</span><span>${state.selectedSlot.display}</span></div>`;
                goTo(4);
            })
            .catch(() => { showErr('#bkErr3', t.err_service); btnSubmit.disabled=false; btnSubmit.innerHTML=`<i class="fa fa-calendar-check-o"></i> ${t.btn_submit}`; });
        }

        /* ================================================================
           رویدادها و راه‌اندازی
        ================================================================ */
        $('#bkPrevMonth').addEventListener('click', prevMonth);
        $('#bkNextMonth').addEventListener('click', nextMonth);
        $('#bkBack1').addEventListener('click', () => goTo(1));
        $('#bkBack2').addEventListener('click', () => goTo(2));
        btnSubmit.addEventListener('click', submitBooking);
        $('#bkNew').addEventListener('click', () => {
            state.selectedISO = null; state.selectedSlot = null;
            inName.value = ''; inPhone.value = ''; inNat.value = '';
            goTo(1);
            renderCalendar();
        });

        buildWeekHeader();
        /* دریافت نوبت‌های ماه جاری */
        if (lang === 'fa') {
            const [gy, gm] = fromJalali(state.viewJYear, state.viewJMonth, 1);
            fetchMonth(gy, gm);
        } else {
            fetchMonth(state.viewGYear, state.viewGMonth);
        }
    }

    /* ================================================================
       CSRF cookie
    ================================================================ */
    function getCookie(name) {
        const v = document.cookie.match('(^|;) ?' + name + '=([^;]*)(;|$)');
        return v ? decodeURIComponent(v[2]) : '';
    }

    document.addEventListener('DOMContentLoaded', () => {
        document.querySelectorAll('[data-booking-widget]').forEach(initBookingWidget);
    });

})();
