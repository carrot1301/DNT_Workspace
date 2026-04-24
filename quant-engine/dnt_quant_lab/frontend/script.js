// ═══════════════════════════════════════════════════
// SUPABASE AUTHENTICATION
// ═══════════════════════════════════════════════════
const SUPABASE_URL = 'https://ojgbkfpoaozpvzmlerth.supabase.co';
const SUPABASE_ANON_KEY = 'sb_publishable_dSJ250bZQ28ejtkz_de9jw_9Kk_1ay5';
let supabaseClient = null;

if (window.supabase) {
    supabaseClient = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
    
    supabaseClient.auth.onAuthStateChange((event, session) => {
        if (event === 'PASSWORD_RECOVERY') {
            setTimeout(() => {
                const modal = document.getElementById('change-pw-modal');
                if (modal) modal.style.display = 'flex';
            }, 500);
        }
    });
}

let currentUser = null;
let userProfile = null;
let authMode = 'login'; // 'login' or 'signup'

function openAuthModal() {
    document.getElementById('auth-modal').style.display = 'flex';
    document.getElementById('auth-msg').style.display = 'none';
}

function closeAuthModal() {
    document.getElementById('auth-modal').style.display = 'none';
    if (authMode === 'forgot') {
        authMode = 'login'; // Reset back to login mode if closed
    }
}

function togglePasswordVisibility(inputId, iconElement) {
    const input = document.getElementById(inputId);
    if (input.type === 'password') {
        input.type = 'text';
        iconElement.textContent = '👁️‍🗨️';
        iconElement.style.color = '#00FFAA';
    } else {
        input.type = 'password';
        iconElement.textContent = '👁️';
        iconElement.style.color = '#94a3b8';
    }
}

function showForgotPassword() {
    authMode = 'forgot';
    document.getElementById('auth-msg').style.display = 'none';
    document.getElementById('password-container').style.display = 'none';
    document.getElementById('signup-fields').style.display = 'none';
    document.getElementById('forgot-pw-container').style.display = 'none';
    
    document.getElementById('auth-title').setAttribute('data-i18n', 'auth_forgot_title');
    document.getElementById('auth-submit-btn').setAttribute('data-i18n', 'auth_forgot_btn');
    document.getElementById('auth-switch-text').setAttribute('data-i18n', 'auth_forgot_back');
    document.getElementById('auth-switch-link').setAttribute('data-i18n', 'auth_switch_link_login');
    
    if (window.updateLanguageGlobal) window.updateLanguageGlobal();
}

function checkPasswordStrength() {
    if (authMode === 'login') return;
    
    const pw = document.getElementById('auth-password').value;
    const bar = document.getElementById('pw-strength-bar');
    const text = document.getElementById('pw-strength-text');
    
    const hasUpper = /[A-Z]/.test(pw);
    const hasLower = /[a-z]/.test(pw);
    const hasNum = /[0-9]/.test(pw);
    const hasSpec = /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(pw);
    
    let score = 0;
    if (pw.length > 0) score += 1;
    if (pw.length >= 8) score += 1;
    if (hasUpper && hasLower) score += 1;
    if (hasNum) score += 1;
    if (hasSpec) score += 1;
    
    if (pw.length === 0) {
        bar.style.width = '0%';
        text.innerText = window.getCurrentLang && window.getCurrentLang() === 'en' ? 'Strength: None' : 'Độ mạnh: Chưa nhập';
        text.style.color = '#94a3b8';
        return;
    }
    
    bar.style.width = (score * 20) + '%';
    if (score <= 2) {
        bar.style.background = '#FF3B30';
        text.innerText = window.getCurrentLang && window.getCurrentLang() === 'en' ? 'Strength: Weak' : 'Độ mạnh: Yếu';
        text.style.color = '#FF3B30';
    } else if (score <= 4) {
        bar.style.background = '#F59E0B';
        text.innerText = window.getCurrentLang && window.getCurrentLang() === 'en' ? 'Strength: Medium' : 'Độ mạnh: Trung bình';
        text.style.color = '#F59E0B';
    } else {
        bar.style.background = '#00FFAA';
        text.innerText = window.getCurrentLang && window.getCurrentLang() === 'en' ? 'Strength: Strong' : 'Độ mạnh: Rất mạnh';
        text.style.color = '#00FFAA';
    }
}

function switchAuthMode() {
    if (authMode === 'forgot') {
        authMode = 'login';
    } else {
        authMode = authMode === 'login' ? 'signup' : 'login';
    }
    document.getElementById('auth-msg').style.display = 'none';
    document.getElementById('password-container').style.display = 'block';
    document.getElementById('forgot-pw-container').style.display = authMode === 'login' ? 'block' : 'none';
    document.getElementById('signup-fields').style.display = authMode === 'login' ? 'none' : 'block';
    
    document.getElementById('auth-title').setAttribute('data-i18n', authMode === 'login' ? 'auth_title_login' : 'auth_title_signup');
    document.getElementById('auth-submit-btn').setAttribute('data-i18n', authMode === 'login' ? 'auth_btn_login' : 'auth_btn_signup');
    document.getElementById('auth-switch-text').setAttribute('data-i18n', authMode === 'login' ? 'auth_switch_to_signup' : 'auth_switch_to_login');
    document.getElementById('auth-switch-link').setAttribute('data-i18n', authMode === 'login' ? 'auth_switch_link_signup' : 'auth_switch_link_login');
    
    if (window.updateLanguageGlobal) window.updateLanguageGlobal();
    checkPasswordStrength();
}

async function handleAuth() {
    const email = document.getElementById('auth-email').value;
    const password = document.getElementById('auth-password').value;
    const confirm = document.getElementById('auth-confirm-password').value;
    const msgEl = document.getElementById('auth-msg');
    const dict = I18N[window.getCurrentLang ? window.getCurrentLang() : 'vi'];
    
    if (authMode === 'signup') {
        if (!email || !password || !confirm) {
            msgEl.innerText = dict['auth_err_empty'];
            msgEl.style.display = 'block';
            return;
        }
        if (password !== confirm) {
            msgEl.innerText = dict['auth_err_pw_match'];
            msgEl.style.display = 'block';
            return;
        }
        
        const hasUpper = /[A-Z]/.test(password);
        const hasLower = /[a-z]/.test(password);
        const hasNum = /[0-9]/.test(password);
        const hasSpec = /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password);
        const isValidLen = password.length >= 8 && password.length <= 36;
        
        if (!hasUpper || !hasLower || !hasNum || !hasSpec || !isValidLen) {
            msgEl.innerText = dict['auth_err_pw_weak'];
            msgEl.style.display = 'block';
            return;
        }
    } else if (authMode === 'login') {
        if (!email || !password) {
            msgEl.innerText = dict['auth_err_empty'];
            msgEl.style.display = 'block';
            return;
        }
    } else if (authMode === 'forgot') {
        if (!email) {
            msgEl.innerText = 'Vui lòng nhập Email!';
            msgEl.style.display = 'block';
            return;
        }
    }
    
    msgEl.innerText = dict['auth_msg_processing'];
    msgEl.style.color = '#00FFAA';
    msgEl.style.display = 'block';
    
    let error = null;
    
    try {
        if (authMode === 'signup') {
            const { data, error: err } = await supabaseClient.auth.signUp({ email, password });
            error = err;
            if (!error && data.user) {
                msgEl.innerText = dict['auth_msg_success'];
                msgEl.style.color = '#00FFAA';
                setTimeout(() => { switchAuthMode(); }, 1500);
                return;
            }
        } else if (authMode === 'login') {
            const { data, error: err } = await supabaseClient.auth.signInWithPassword({ email, password });
            error = err;
        } else if (authMode === 'forgot') {
            const { error: err } = await supabaseClient.auth.resetPasswordForEmail(email, {
                redirectTo: window.location.origin + window.location.pathname
            });
            error = err;
            if (!error) {
                msgEl.innerText = 'Đã gửi liên kết khôi phục! Vui lòng kiểm tra hộp thư (cả thư rác).';
                msgEl.style.color = '#00FFAA';
                return;
            }
        }
    } catch(e) {
        error = e;
    }
    
    if (error) {
        let errorMsg = error.message;
        if (errorMsg.includes('Email not confirmed')) {
            errorMsg = dict['auth_err_unconfirmed'] || 'Vui lòng kiểm tra hộp thư và Xác nhận Email trước khi đăng nhập!';
        } else if (errorMsg.includes('Invalid login credentials')) {
            errorMsg = dict['auth_err_invalid_creds'] || 'Sai Email hoặc Mật khẩu!';
        } else if (errorMsg.includes('User already registered')) {
            errorMsg = dict['auth_err_already_registered'] || 'Email này đã được đăng ký!';
        }
        msgEl.innerText = 'Lỗi: ' + errorMsg;
        msgEl.style.color = '#FF3B30';
    } else {
        closeAuthModal();
        checkUserSession();
    }
}

async function handleLogout() {
    await supabaseClient.auth.signOut();
    currentUser = null;
    userProfile = null;
    updateAuthUI();
}

async function checkUserSession() {
    if (!supabaseClient) return;
    try {
        const { data: { session } } = await supabaseClient.auth.getSession();
        if (session) {
        currentUser = session.user;
        await fetchUserProfile(currentUser.id);
    } else {
        currentUser = null;
        userProfile = null;
    }
    } catch(e) { console.error("Session Error", e); }
    updateAuthUI();
}

async function fetchUserProfile(userId) {
    const { data, error } = await supabaseClient.from('profiles').select('*').eq('id', userId).single();
    if (data) userProfile = data;
}

function updateAuthUI() {
    const authBtn = document.getElementById('auth-btn');
    const logoutBtn = document.getElementById('logout-btn');
    const profileContainer = document.getElementById('user-profile-container');
    const emailDisplay = document.getElementById('user-email-display');
    const tokensDisplay = document.getElementById('user-tokens-display');
    
    const overlay = document.getElementById('login-overlay');
    if (currentUser) {
        if(overlay) overlay.style.display = 'none';
        if(authBtn) authBtn.style.display = 'none';
        if(logoutBtn) logoutBtn.style.display = 'inline-block';
        
        if(profileContainer) profileContainer.style.display = 'flex';
        if(emailDisplay && currentUser.email) emailDisplay.textContent = currentUser.email.split('@')[0];
        
        if (userProfile && tokensDisplay) {
            tokensDisplay.style.display = 'inline-block';
            tokensDisplay.innerHTML = `💎 <span class="hide-mobile">Free: </span>${userProfile.free_credits} | 🪙 <span class="hide-mobile">Paid: </span>${userProfile.paid_tokens}`;
        }
    } else {
        if(overlay) overlay.style.display = 'flex';
        if(authBtn) authBtn.style.display = 'inline-block';
        if(logoutBtn) logoutBtn.style.display = 'none';
        if(profileContainer) profileContainer.style.display = 'none';
        if(tokensDisplay) tokensDisplay.style.display = 'none';
    }
}

function toggleProfileDropdown(event) {
    if (event.target.closest('#user-profile-dropdown')) return;
    const dropdown = document.getElementById('user-profile-dropdown');
    dropdown.style.display = dropdown.style.display === 'flex' ? 'none' : 'flex';
}

document.addEventListener('click', function(e) {
    const container = document.getElementById('user-profile-container');
    if (container && !container.contains(e.target)) {
        const dropdown = document.getElementById('user-profile-dropdown');
        if (dropdown) dropdown.style.display = 'none';
    }
});

function openChangePasswordModal() {
    document.getElementById('change-pw-modal').style.display = 'flex';
    document.getElementById('change-pw-msg').style.display = 'none';
    document.getElementById('change-pw-input').value = '';
    const dropdown = document.getElementById('user-profile-dropdown');
    if (dropdown) dropdown.style.display = 'none';
}

function closeChangePasswordModal() {
    document.getElementById('change-pw-modal').style.display = 'none';
}

async function handleChangePassword() {
    const pw = document.getElementById('change-pw-input').value;
    const msgEl = document.getElementById('change-pw-msg');
    
    if (!pw) {
        msgEl.innerText = window.getCurrentLang() === 'en' ? "Please enter a new password" : "Vui lòng nhập mật khẩu mới";
        msgEl.style.display = 'block';
        return;
    }
    
    msgEl.innerText = window.getCurrentLang() === 'en' ? "Processing..." : "Đang xử lý...";
    msgEl.style.color = '#00FFAA';
    msgEl.style.display = 'block';
    
    const { data, error } = await supabaseClient.auth.updateUser({ password: pw });
    
    if (error) {
        msgEl.innerText = 'Lỗi: ' + error.message;
        msgEl.style.color = '#FF3B30';
    } else {
        msgEl.innerText = window.getCurrentLang() === 'en' ? "Password updated successfully!" : "Đổi mật khẩu thành công!";
        msgEl.style.color = '#00FFAA';
        setTimeout(() => { closeChangePasswordModal(); }, 1500);
    }
}


async function apiFetch(url, options = {}) {
    if (!options.headers) options.headers = {};
    if (currentUser) {
        const { data: { session } } = await supabaseClient.auth.getSession();
        if (session) {
            options.headers['Authorization'] = `Bearer ${session.access_token}`;
        } else {
            currentUser = null;
            userProfile = null;
            updateAuthUI();
            alert(window.getCurrentLang() === 'en' ? 'Your session has expired. Please log in again.' : 'Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.');
            openAuthModal();
            throw new Error('Session Expired');
        }
    }
    return fetch(url, options);
}

const I18N = {
    'en': {
        'nav_login': 'Login',
        'nav_change_pw': 'Change Password',
        'auth_ph_new_pw': 'New Password',
        'btn_update': 'Update',
        'nav_portfolio': 'Portfolio Allocation',
        'nav_health': 'Portfolio Health',
        'lock_title': 'Login to Unlock',
        'lock_desc': 'Access all Technical Analysis tools, AI Advisor, and Portfolio Optimization.',
        'nav_logout': 'Logout',
        'subtitle': 'AI Quant Assistant',
        'auth_title_login': 'System Login',
        'auth_title_signup': 'Create Account',
        'auth_ph_email': 'Email',
        'auth_ph_pw': 'Password',
        'auth_ph_confirm': 'Confirm Password',
        'auth_pw_strength': 'Strength: None',
        'auth_pw_note': '⚠️ Password must be 8-36 chars, including: uppercase, lowercase, number, and special char.',
        'auth_btn_login': 'Login',
        'auth_btn_signup': 'Sign Up',
        'auth_switch_to_signup': 'No account yet?',
        'auth_switch_link_signup': 'Sign up now',
        'auth_switch_to_login': 'Already have an account?',
        'auth_switch_link_login': 'Login here',
        'auth_err_empty': 'Please enter all fields!',
        'auth_err_pw_match': 'Passwords do not match!',
        'auth_err_pw_weak': 'Password does not meet the requirements!',
        'auth_err_unconfirmed': 'Please check your inbox and verify your email before logging in!',
        'auth_err_invalid_creds': 'Invalid Email or Password!',
        'auth_err_already_registered': 'This email is already registered!',
        'auth_msg_processing': 'Processing...',
        'auth_msg_success': 'Registration successful! Please check your email to verify your account.',
        'nav_opt': 'Portfolio Optimizer',
        'nav_eval': 'Portfolio Evaluator',
        'params_title': 'Investment Parameters',
        'eval_title': 'My Custom Portfolio',
        'label_tickers': 'Stock Tickers (comma separated)',
        'ph_tickers': 'e.g. FPT, VCB',
        'label_capital': 'Initial Capital (VND)',
        'ph_capital': 'e.g. 1,000,000,000',
        'label_return': 'Target Return (%)',
        'btn_run': 'Run Simulation (-2 Tokens)',
        'btn_eval': 'Evaluate Portfolio 🔍 (-2 Tokens)',
        'btn_stress': '🔥 Stress Test',
        'btn_add_stock': '+ Add Stock',
        'label_timeframe': 'Timeframe',
        'tf_1m': '1 Month (21 Days)',
        'tf_3m': '3 Months (63 Days)',
        'tf_6m': '6 Months (126 Days)',
        'tf_9m': '9 Months (189 Days)',
        'tf_1y': '1 Year (252 Days)',
        'tf_2y': '2 Years (504 Days)',
        'tf_3y': '3 Years (756 Days)',
        'main_title': 'Portfolio Status',
        'status_connected': 'Server Connected',
        'chart_title': 'Analysis & Projections',
        'chart_desc': 'High-performance API: Calculated natively via Python arrays.',
        'metric_proj': 'Projected Expected Value',
        'metric_risk': 'Max Risk (VaR 95%)',
        'var_profitable_label': 'Still Profitable',
        'var_positive_tooltip': 'Even in the worst 5% scenario, portfolio is estimated to remain profitable – excellent portfolio quality!',
        'var_negative_tooltip': 'Maximum estimated loss at 95% confidence level.',
        'err_conn': 'Server Connection Failed',
        'err_wait': 'Waiting for Python Backend (FastAPI).<br>Run: uvicorn main:app --reload',
        'err_input': 'Alert: Please double check your numerical inputs!',
        'err_tokens': 'You do not have enough Tokens. Please top up!',
        'loader_title': 'PROCESSING DATA...',
        'loader_sub': 'Running algorithmic simulation & portfolio optimization.',
        'disclaimer_title': '⚠️ Disclaimer:',
        'ai_disclaimer': 'AI analysis is strictly based on historical data and the latest financial reports. It cannot forecast sudden or unprecedented future events. Past performance is no guarantee of future results.',
        'ci_text': '95% Prob. Range:',
        'persona_label': 'AI Persona',
        'persona_value': 'Value Investor (Fundamentals)',
        'persona_speculator': 'Speculator (Momentum & Flow)',
        'persona_quant': 'Pure Quant (Probability & Risk)',
        'nav_leaderboard': '🏆 Leaderboard',
        'lb_title': '🏆 Quant Leaderboard',
        'lb_sub': 'Top simulated portfolios by weekly Sharpe Ratio',
        'lb_rank': 'Rank',
        'lb_user': 'User',
        'lb_portfolio': 'Portfolio (Weights)',
        'lb_sharpe': 'Sharpe',
        'btn_export': '📸 Export Report',
        'adv_constraints_title': '⚙️ Custom Risk Constraints',
        'const_min_weight': 'Minimum Weight (%)',
        'const_max_weight': 'Maximum Weight (%)',
        'const_desc': 'Set limits for asset allocation to ensure safer risk distribution.',
        'radar_title': '📡 AI Sentiment Radar',
        'radar_desc': 'Real-time market sentiment analysis via NLP.',
        'stress_drop': 'Crash -5% VN-Index: ',
        'loading_api': 'Computing...',
        'label_backtest': 'Time Machine (Backtest Date)',
        'backtest_desc': 'Leave empty for current data. If a past date is selected, AI will optimize based on data up to that date, and forward-test performance to today.',
        'ai_title': 'Gemini AI — Investment Insights',
        'ai_subtitle': 'Deep analysis based on 10,000 Monte Carlo scenarios',
        'ai_analyzing': 'Analyzing...',
        'ai_thinking': 'Gemini is processing data...',
        'ai_done': 'Analysis Complete',
        'backtest_title': 'Historical Performance (Backtest)',
        'backtest_desc': 'Portfolio historical cumulative returns compared to VNINDEX.',
        'allocation_title': 'Optimal Asset Allocation',
        'allocation_desc': 'Optimized capital distribution across selected stocks.',
        'raw_price_title': 'Closing Prices Table',
        'adv_metrics_title': 'Advanced Quant Metrics',
        'live_capital_label': 'Estimated Total Capital',
        'last_updated': 'Last updated: ',
        'welcome_title': 'Welcome to DNT Quant Lab',
        'welcome_desc': 'Enter your investment parameters and run the simulation to generate an AI-optimized portfolio.',
        'nav_fin': 'Financial Reports 📄',
        'fin_title': 'Search Financials',
        'fin_ticker_label': 'Ticker Symbol',
        'fin_ticker_ph': 'e.g. FPT',
        'btn_fetch_fin': 'Fetch Data',
        'fin_card_title': 'Financial Report: ',
        'fin_desc': 'Fundamental data from TCBS. Unlock for valuation & performance metrics.',
        'fin_ind': 'Industry',
        'fin_mc': 'Market Cap (Billion VND)',
        'fin_pepb': 'P/E | P/B',
        'fin_roeroa': 'ROE | ROA Margin',
        'fin_debt': 'Debt / Equity',
        'fin_profit': 'Profit Growth',
        'btn_unlock': 'Unlock',
        'btn_donate_sb': 'Buy Tokens 🪙',
        'donate_title': 'Purchase Tokens 🪙',
        'donate_msg': 'Buy tokens to unlock advanced features like Deep AI Analysis (2 Tokens/request) and VIP Financial Reports. Tokens will be automatically added to your account after successful payment.',
        'donate_custom': 'Custom',
        'donate_custom_ph': 'Enter amount (VND)',
        'btn_gen_qr': 'Generate QR Code',
        'donate_scan_title': 'Scan QR Code',
        'donate_thanks_title': 'Transaction Successful!',
        'donate_thanks_msg': 'Thank you so much! I am very grateful and will continue to develop and perfect this project as best as I can ❤️',
        'btn_close_qr': 'Cancel / Close',
        'polling_text': 'Waiting for payment (Polling)...',
        'btn_export_pdf': '⬇️ Download PDF',
        'pdf_title': 'VIP QUANTITATIVE ANALYSIS REPORT',
        'use_bctc_cb': 'Include RAG Document in Prompt (Costs AI ~15s)',
        'sig_col_ticker': 'Ticker',
        'sig_col_signal': 'Signal',
        'sig_col_vol': 'Suggested Volume',
        'sig_col_action': 'Execution',
        'btn_vps_cta': 'Open VPS Trading ↗',
        'signals_title': 'Real-Time Trading Signals',
        'signals_desc': 'Technical Analysis (SMA Crossover) & Direct Broker Integration.',
        'use_ai_report': 'Enable AI Analysis Report (+2 Tokens)',
        'auth_forgot_pw': 'Forgot password?',
        'auth_forgot_title': 'Reset Password',
        'auth_forgot_btn': 'Send Recovery Link',
        'auth_forgot_back': 'Remembered password?',
        'ai_radar_hint': 'Suggestions today',
        'ai_radar_scanning': 'Scanning VN30...',
        'ai_radar_updated': 'Updated (VN30)',
        'ai_radar_not_found': 'Not found',
        'ai_radar_err': 'Connection Error',
        'ai_radar_add_all': '💯 Add ALL',
        'rag_badge': '✨ [BETA] AI ASSISTED DOCS (RAG)',
        'rag_found': 'Found deep-dive financial analysis database for:',
        'sig_col_price': 'Current Price',
        'btn_ta_detail': 'TA Details'
    },
    'vi': {
        'nav_login': 'Đăng nhập',
        'nav_change_pw': 'Đổi mật khẩu',
        'auth_ph_new_pw': 'Mật khẩu mới',
        'btn_update': 'Cập nhật',
        'nav_portfolio': 'Phân bổ danh mục',
        'nav_health': 'Sức khỏe danh mục',
        'lock_title': 'Đăng nhập để Mở khóa',
        'lock_desc': 'Truy cập toàn bộ công cụ Phân tích Kỹ thuật, Trợ lý AI và Tối ưu hóa Danh mục.',
        'nav_logout': 'Thoát',
        'subtitle': 'Trợ lý Dữ liệu AI',
        'auth_title_login': 'Đăng nhập hệ thống',
        'auth_title_signup': 'Tạo tài khoản',
        'auth_ph_email': 'Email',
        'auth_ph_pw': 'Mật khẩu',
        'auth_ph_confirm': 'Xác nhận Mật khẩu',
        'auth_pw_strength': 'Độ mạnh: Chưa nhập',
        'auth_pw_note': '⚠️ Mật khẩu từ 8-36 ký tự, gồm: chữ hoa, chữ thường, số và ký tự đặc biệt. Vui lòng ghi nhớ mật khẩu!',
        'auth_btn_login': 'Đăng nhập',
        'auth_btn_signup': 'Đăng ký',
        'auth_switch_to_signup': 'Chưa có tài khoản?',
        'auth_switch_link_signup': 'Đăng ký ngay',
        'auth_switch_to_login': 'Đã có tài khoản?',
        'auth_switch_link_login': 'Đăng nhập',
        'auth_err_empty': 'Vui lòng nhập đầy đủ thông tin!',
        'auth_err_pw_match': 'Mật khẩu xác nhận không khớp!',
        'auth_err_pw_weak': 'Mật khẩu chưa đạt yêu cầu độ mạnh!',
        'auth_err_unconfirmed': 'Vui lòng kiểm tra hộp thư và Xác nhận Email trước khi đăng nhập!',
        'auth_err_invalid_creds': 'Sai Email hoặc Mật khẩu!',
        'auth_err_already_registered': 'Email này đã được đăng ký!',
        'auth_msg_processing': 'Đang xử lý...',
        'auth_msg_success': 'Đăng ký thành công! Vui lòng kiểm tra Email để xác nhận tài khoản.',
        'nav_opt': 'Tối ưu hóa Danh mục',
        'nav_eval': 'Đánh giá Danh mục',
        'params_title': 'Thông số đầu vào',
        'eval_title': 'Danh mục hiện tại',
        'label_tickers': 'Mã cổ phiếu (ngăn cách bằng dấu phẩy)',
        'ph_tickers': 'Ví dụ: FPT, MWG, VCB',
        'label_capital': 'Vốn ban đầu (VNĐ)',
        'ph_capital': 'Ví dụ: 1.000.000.000',
        'label_return': 'Lợi nhuận kỳ vọng (%)',
        'btn_run': '🚀 Chạy mô phỏng (-2 Token)',
        'btn_eval': '🔍 Đánh giá Danh mục (-2 Token)',
        'btn_stress': '🔥 Stress Test',
        'btn_add_stock': '+ Thêm mã',
        'label_timeframe': 'Kỳ hạn',
        'tf_1m': '1 tháng (21 ngày giao dịch)',
        'tf_3m': '3 tháng (63 ngày giao dịch)',
        'tf_6m': '6 tháng (126 ngày giao dịch)',
        'tf_9m': '9 tháng (189 ngày giao dịch)',
        'tf_1y': '1 năm (252 ngày giao dịch)',
        'tf_2y': '2 năm (504 ngày giao dịch)',
        'tf_3y': '3 năm (756 ngày giao dịch)',
        'main_title': 'Tổng quan Danh mục',
        'status_connected': 'Đã kết nối máy chủ',
        'chart_title': 'Phân tích & Dự phóng',
        'chart_desc': 'Tính toán Monte Carlo qua Python API — 10.000 kịch bản ngẫu nhiên.',
        'metric_proj': 'Giá trị kỳ vọng',
        'metric_risk': 'Rủi ro tối đa (VaR 95%)',
        'var_profitable_label': 'Vẫn sinh lời',
        'var_positive_tooltip': 'Ở kịch bản xấu nhất 5% xác suất, danh mục ước tính vẫn có lãi – chất lượng danh mục tốt!',
        'var_negative_tooltip': 'Mức lỗ tối đa ước tính ở ngưỡng tin cậy 95%.',
        'err_conn': 'Mất kết nối với máy chủ',
        'err_wait': 'Không thể kết nối Backend Python (FastAPI).<br>Chạy lệnh: uvicorn main:app --reload',
        'err_input': 'Vui lòng kiểm tra lại dữ liệu nhập — cần ít nhất 2 mã cổ phiếu hợp lệ!',
        'err_tokens': 'Bạn không đủ Token. Vui lòng nạp thêm!',
        'loader_title': 'ĐANG XỬ LÝ DỮ LIỆU...',
        'loader_sub': 'Đang chạy thuật toán mô phỏng & phân tích danh mục.',
        'disclaimer_title': '⚠️ Lưu ý quan trọng:',
        'ai_disclaimer': 'Kết quả phân tích chỉ dựa trên dữ liệu lịch sử và không phải là lời khuyên đầu tư. Hiệu suất trong quá khứ không đảm bảo cho kết quả tương lai. Nhà đầu tư tự chịu trách nhiệm về quyết định của mình.',
        'ci_text': 'Khoảng tin cậy 95%:',
        'persona_label': 'Hệ tư tưởng AI (Persona)',
        'persona_value': 'Đầu tư Giá trị (Cơ bản)',
        'persona_speculator': 'Đầu Cơ (Dòng tiền)',
        'persona_quant': 'Thuần Định Lượng (Xác suất)',
        'nav_leaderboard': '🏆 Bảng Xếp Hạng',
        'lb_title': '🏆 Bảng Xếp Hạng Quant',
        'lb_sub': 'Top các danh mục mô phỏng có Sharpe Ratio cao nhất tuần',
        'lb_rank': 'Hạng',
        'lb_user': 'Người dùng',
        'lb_portfolio': 'Danh mục (Tỷ trọng)',
        'lb_sharpe': 'Sharpe',
        'btn_export': '📸 Xuất Báo Cáo',
        'adv_constraints_title': '⚙️ Tùy Biến Rủi Ro (Nâng cao)',
        'const_min_weight': 'Tỷ trọng Tối thiểu (%)',
        'const_max_weight': 'Tỷ trọng Tối đa (%)',
        'const_desc': 'Thiết lập giới hạn mua cho từng cổ phiếu để phân bổ rủi ro an toàn hơn.',
        'radar_title': '📡 AI Sentiment Radar',
        'radar_desc': 'Phân tích tâm lý thị trường thời gian thực qua NLP.',
        'stress_drop': 'VN-Index -5%: tổn thất ước tính ',
        'loading_api': 'Đang tính toán...',
        'label_backtest': 'Cỗ Máy Thời Gian (Backtest Date)',
        'backtest_desc': 'Để trống để chạy với dữ liệu tới hiện tại. Nếu chọn ngày quá khứ, AI sẽ tối ưu dựa trên dữ liệu tới ngày đó, và kiểm thử hiệu suất từ đó đến nay.',
        'ai_title': 'Gemini AI — Lời khuyên Đầu tư',
        'ai_subtitle': 'Phân tích chuyên sâu dựa trên 10.000 kịch bản Monte Carlo',
        'ai_analyzing': 'Đang phân tích...',
        'ai_thinking': 'Gemini đang xử lý dữ liệu...',
        'ai_done': 'Hoàn tất phân tích',
        'backtest_title': 'Hiệu suất Lịch sử (Backtest)',
        'backtest_desc': 'So sánh lợi nhuận tích lũy của danh mục với VN-Index.',
        'allocation_title': 'Phân bổ Tài sản Tối ưu',
        'allocation_desc': 'Tỉ trọng phân bổ vốn chi tiết cho từng mã cổ phiếu.',
        'raw_price_title': 'Bảng Giá Đóng cửa',
        'adv_metrics_title': 'Chỉ số Quant Nâng cao',
        'live_capital_label': 'Tổng Vốn Ước Tính',
        'last_updated': 'Cập nhật lần cuối: ',
        'welcome_title': 'Chào mừng đến với DNT Quant Lab',
        'welcome_desc': 'Nhập các thông số đầu tư và chạy mô phỏng để tạo danh mục được tối ưu hóa bởi AI.',
        'nav_fin': 'Báo cáo Tài chính 📄',
        'fin_title': 'Tra Cứu BCTC',
        'fin_ticker_label': 'Mã Cổ phiếu',
        'fin_ticker_ph': 'VD: FPT',
        'btn_fetch_fin': 'Lấy Dữ Liệu',
        'fin_card_title': 'Báo Cáo Tài Chính: ',
        'fin_desc': 'Dữ liệu cơ bản từ TCBS. Mở khóa để xem các chỉ số định giá & hiệu quả HĐKD.',
        'fin_ind': 'Ngành nghề',
        'fin_mc': 'Vốn hóa (Tỷ VND)',
        'fin_pepb': 'P/E | P/B',
        'fin_roeroa': 'Biên ROE | ROA',
        'fin_debt': 'Nợ / Vốn CSH',
        'fin_profit': 'Tăng trưởng LN',
        'btn_unlock': 'Mở khóa',
        'btn_donate_sb': 'Nạp Token 🪙',
        'donate_title': 'Nạp Token Hệ Thống 🪙',
        'donate_msg': 'Nạp Token để mở khóa các tính năng nâng cao như Trợ lý AI Phân tích chuyên sâu (2 Token/lần) và Mô phỏng Khuyến nghị. Token sẽ tự động cộng vào tài khoản sau khi thanh toán thành công.',
        'donate_custom': 'Tùy chọn',
        'donate_custom_ph': 'Nhập số tiền (VNĐ)',
        'btn_gen_qr': 'Tạo Mã QR',
        'donate_scan_title': 'Quét mã QR',
        'donate_thanks_title': 'Giao dịch Thành công!',
        'donate_thanks_msg': 'Cảm ơn, rất biết ơn anh chị, em sẽ cố gắng phát triển hoàn thiện dự án này tốt nhất có thể ❤️',
        'btn_close_qr': 'Hủy / Đóng',
        'polling_text': 'Đang chờ nhận thanh toán (Polling)...',
        'btn_export_pdf': '⬇️ Tải PDF',
        'pdf_title': 'BÁO CÁO PHÂN TÍCH QUANTRIP V.I.P',
        'use_bctc_cb': 'Đính kèm vào Prompt (AI tốn thêm ~15s)',
        'sig_col_ticker': 'Mã CP',
        'sig_col_signal': 'Tín Hiệu',
        'sig_col_vol': 'Khối Lượng Đề Xuất',
        'sig_col_action': 'Khớp Lệnh',
        'btn_vps_cta': 'Mở VPS Đặt Lệnh ↗',
        'signals_title': 'Tín Hiệu Giao Dịch Thời Gian Thực',
        'signals_desc': 'Tín hiệu Phân tích Kỹ thuật (SMA Crossover) & Đặt lệnh mua bán liên thông VPS.',
        'use_ai_report': 'Bật Trợ Lý AI Phân Tích (Tốn thêm 2 Token)',
        'auth_forgot_pw': 'Quên mật khẩu?',
        'auth_forgot_title': 'Khôi phục mật khẩu',
        'auth_forgot_btn': 'Gửi liên kết khôi phục',
        'auth_forgot_back': 'Đã nhớ mật khẩu?',
        'ai_radar_hint': 'Gợi ý hôm nay',
        'ai_radar_scanning': 'Đang quét VN30...',
        'ai_radar_updated': 'Đã cập nhật (VN30)',
        'ai_radar_not_found': 'Không tìm thấy',
        'ai_radar_err': 'Lỗi kết nối AI',
        'ai_radar_add_all': '💯 Thêm TẤT CẢ',
        'rag_badge': '✨ [BETA] TÀI LIỆU AI CỐ TRỢ (RAG)',
        'rag_found': 'Phát hiện kho dữ liệu có sẵn BCTC phân tích chuyên sâu cho:',
        'sig_col_price': 'Giá Hiện Hành',
        'btn_ta_detail': 'Chi tiết TA'
    }
};

// ═══════════════════════════════════════════════════
// GLOBAL: Open TA Modal (called from inline onclick)
// ═══════════════════════════════════════════════════
function openTAModal(ticker) {
    const signals = window.globalTradingSignals;
    if (!signals || !signals[ticker] || !signals[ticker].ta_analysis) return;

    const ta = signals[ticker].ta_analysis;
    const modal = document.getElementById('ta-modal');
    const title = document.getElementById('ta-modal-title');
    const body = document.getElementById('ta-modal-body');

    title.textContent = `${ticker} - Phân tích kỹ thuật`;

    function fmt(v) {
        if (v === undefined || v === null) return '--';
        return typeof v === 'number' ? v.toLocaleString('vi-VN', { maximumFractionDigits: 2 }) : v;
    }

    function txColor(text) {
        if (!text) return '#94a3b8';
        if (text.includes('MUA') || text.includes('Mua')) return '#34C759'; // Xanh lá
        if (text.includes('BÁN') || text.includes('Bán')) return '#FF3B30'; // Đỏ
        return '#8e95a5';
    }

    function sigBgColor(text) {
        if (!text) return '#8e95a5';
        if (text.includes('MUA MẠNH')) return '#28a745';
        if (text.includes('MUA')) return '#34C759';
        if (text.includes('BÁN MẠNH')) return '#dc3545';
        if (text.includes('BÁN')) return '#FF3B30';
        return '#6c757d';
    }

    // Chuyển score [-1, 1] sang rotation degree [0, 180] cho Needle (-1 = 0deg, 1 = 180deg)
    // -1 = Bán Mạnh, 1 = Mua Mạnh
    function needleRot(score) {
        let sc = parseFloat(score) || 0;
        // sc range: -1 to 1. Map to 0 to 180 degrees.
        // Actually, css starts from left to right. 0 deg = left (Bán mạnh), 180 deg = right (Mua mạnh)
        let deg = (sc + 1) * 90; 
        // Need to offset by -90 since rotate starts from top in standard transform, 
        // but if we rotate a bottom-origin stick, 0deg is vertical.
        // Let's adjust stick rotation mapping: -90deg is full left (Sell), +90deg is full right (Buy).
        let r = sc * 90;
        if (r > 90) r = 90;
        if (r < -90) r = -90;
        return r;
    }

    // Render Pivot Rows
    function pivotRows(arr) {
        return arr.map(p => `
            <tr style="border-bottom: 1px solid rgba(255,255,255,0.05);">
                <td style="padding: 12px; text-align: left; font-weight: bold;">${p.name}</td>
                <td style="padding: 12px;">${p.S3 > 0 ? fmt(p.S3) : ''}</td>
                <td style="padding: 12px;">${p.S2 > 0 ? fmt(p.S2) : ''}</td>
                <td style="padding: 12px;">${p.S1 > 0 ? fmt(p.S1) : ''}</td>
                <td style="padding: 12px; font-weight: bold;">${p.Points > 0 ? fmt(p.Points) : ''}</td>
                <td style="padding: 12px;">${p.R1 > 0 ? fmt(p.R1) : ''}</td>
                <td style="padding: 12px;">${p.R2 > 0 ? fmt(p.R2) : ''}</td>
                <td style="padding: 12px;">${p.R3 > 0 ? fmt(p.R3) : ''}</td>
            </tr>
        `).join('');
    }

    // Render Indicators
    function indRows(arr) {
        return arr.map(i => `
            <tr style="border-bottom: 1px solid rgba(255,255,255,0.05);">
                <td style="padding: 12px; font-weight: bold; text-align: left;">${i.name}</td>
                <td style="padding: 12px; text-align: right;">${fmt(i.value)}</td>
                <td style="padding: 12px; text-align: center; color: ${txColor(i.action)};">${i.action}</td>
            </tr>
        `).join('');
    }

    // Render Moving Averages
    function maRows(arr) {
        return arr.map(m => `
            <tr style="border-bottom: 1px solid rgba(255,255,255,0.05);">
                <td style="padding: 12px; font-weight: bold; text-align: left;">${m.name}</td>
                <td style="padding: 12px; text-align: center;">
                    <div>${fmt(m.sma_val)}</div>
                    <div style="font-size: 11px; color: ${txColor(m.sma_action)};">${m.sma_action}</div>
                </td>
                <td style="padding: 12px; text-align: center;">
                    <div>${fmt(m.ema_val)}</div>
                    <div style="font-size: 11px; color: ${txColor(m.ema_action)};">${m.ema_action}</div>
                </td>
            </tr>
        `).join('');
    }

    body.innerHTML = `
        <div style="padding: 0 8px; font-family: 'Inter', sans-serif;">
            
            <div style="display: flex; gap: 8px; margin-bottom: 16px;">
                <span style="font-weight: bold; color: white;">Chu kỳ:</span>
                <span style="background: rgba(255,255,255,0.1); padding: 2px 8px; border-radius: 4px; font-size: 12px; cursor: pointer;">1 phút</span>
                <span style="background: rgba(255,255,255,0.1); padding: 2px 8px; border-radius: 4px; font-size: 12px; cursor: pointer;">5 phút</span>
                <span style="background: rgba(255,255,255,0.1); padding: 2px 8px; border-radius: 4px; font-size: 12px; cursor: pointer;">15 phút</span>
                <span style="background: rgba(255,255,255,0.1); padding: 2px 8px; border-radius: 4px; font-size: 12px; cursor: pointer;">1 giờ</span>
                <span style="background: #00B8FF; color: white; padding: 2px 8px; border-radius: 4px; font-size: 12px; cursor: pointer;">1 ngày</span>
                <span style="background: rgba(255,255,255,0.1); padding: 2px 8px; border-radius: 4px; font-size: 12px; cursor: pointer;">1 tuần</span>
            </div>

            <!-- Top Summary -->
            <div style="display: flex; justify-content: space-between; background: #232838; border-radius: 8px; padding: 20px; margin-bottom: 20px;">
                <!-- Left Details -->
                <div style="flex: 1; max-width: 400px;">
                    <div style="display: flex; align-items: center; margin-bottom: 16px;">
                        <span style="font-size: 14px; font-weight: bold; width: 140px; color: white;">TỔNG HỢP:</span>
                        <span style="background: ${sigBgColor(ta.summary.overall_vi)}; color: white; border-radius: 20px; padding: 6px 14px; font-weight: bold; font-size: 13px;">${ta.summary.overall_vi}</span>
                    </div>
                    
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 12px 0; border-top: 1px solid rgba(255,255,255,0.05);">
                        <span style="font-size: 13px; width: 140px; color: white;">Đường trung bình:</span>
                        <span style="color: ${txColor(ta.summary.ma_signal)}; font-weight: bold; flex: 1; font-size: 14px;">${ta.summary.ma_signal}</span>
                        <div style="display: flex; gap: 12px; font-size: 13px; color: white;">
                            <span>Mua (<b style="color: white;">${ta.summary.ma_buy}</b>)</span>
                            <span>Bán (<b style="color: white;">${ta.summary.ma_sell}</b>)</span>
                        </div>
                    </div>

                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 12px 0; border-top: 1px solid rgba(255,255,255,0.05);">
                        <span style="font-size: 13px; width: 140px; color: white;">Chỉ số kỹ thuật:</span>
                        <span style="color: ${txColor(ta.summary.ind_signal)}; font-weight: bold; flex: 1; font-size: 14px;">${ta.summary.ind_signal}</span>
                        <div style="display: flex; gap: 12px; font-size: 13px; color: white;">
                            <span>Mua (<b style="color: white;">${ta.summary.ind_buy}</b>)</span>
                            <span>Bán (<b style="color: white;">${ta.summary.ind_sell}</b>)</span>
                        </div>
                    </div>
                    
                    <div style="font-size: 11px; color: #8e95a5; margin-top: 12px;">* Dữ liệu được tính toán tự động theo thời gian thực</div>
                </div>
                
                <!-- Speedometer / Gauge -->
                <div style="width: 250px; display: flex; align-items: center; justify-content: center; position: relative; margin-right: 20px;">
                    <div style="position: relative; width: 180px; height: 90px; overflow: hidden;">
                        <!-- Semi-circle arcs -->
                        <div style="position: absolute; top: 0; left: 0; width: 180px; height: 180px; border-radius: 50%; background: conic-gradient(from -90deg at 50% 50%, #FF3B30 0%, #FF3B30 30%, #8E8E93 45%, #8E8E93 55%, #34C759 70%, #34C759 100%); clip-path: polygon(0% 0%, 100% 0%, 100% 50%, 0% 50%); transform: rotate(180deg);"></div>
                        <!-- Inner cut-out -->
                        <div style="position: absolute; top: 12px; left: 12px; width: 156px; height: 156px; border-radius: 50%; background: #232838;"></div>
                        <!-- Dash marks to look like Fireant -->
                        <div style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border-radius: 50%; border-top: 8px dashed #232838; box-sizing: border-box; opacity: 0.5;"></div>
                        
                        <!-- Needle Pivot -->
                        <div style="position: absolute; bottom: -8px; left: 50%; transform: translateX(-50%); width: 16px; height: 16px; background: #34C759; border-radius: 50%; z-index: 2;"></div>
                        <!-- Needle stick -->
                        <div style="position: absolute; bottom: 0px; left: 50%; width: 4px; height: 65px; background: #34C759; transform-origin: bottom center; transform: translateX(-50%) rotate(${needleRot(ta.summary.score)}deg); border-radius: 4px 4px 0 0; z-index: 1;">
                            <div style="position:absolute; top:-12px; left:-6px; width:0; height:0; border-left:8px solid transparent; border-right:8px solid transparent; border-bottom:12px solid #34C759;"></div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Pivot Points Table -->
            <div style="margin-bottom: 20px;">
                <div style="font-weight: bold; margin-bottom: 12px; font-size: 14px; color: white;">Pivot Points</div>
                <div style="overflow-x: auto;">
                    <table style="width: 100%; border-collapse: collapse; font-size: 13px; text-align: right; background: #1f2231; border-radius: 6px; overflow: hidden; color: white;">
                        <tr style="color: #cbd5e1; border-bottom: 1px solid rgba(255,255,255,0.05); background: rgba(0,0,0,0.2);">
                            <th style="padding: 12px; text-align: left;">Tên</th>
                            <th style="padding: 12px;">S3</th>
                            <th style="padding: 12px;">S2</th>
                            <th style="padding: 12px;">S1</th>
                            <th style="padding: 12px;">Points</th>
                            <th style="padding: 12px;">R1</th>
                            <th style="padding: 12px;">R2</th>
                            <th style="padding: 12px;">R3</th>
                        </tr>
                        ${pivotRows(ta.pivot_points)}
                    </table>
                </div>
            </div>

            <!-- Two Columns -->
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                <!-- Column 1: Chỉ số kỹ thuật -->
                <div>
                    <div style="font-weight: bold; margin-bottom: 12px; font-size: 14px; color: white;">Chỉ số kỹ thuật</div>
                    <table style="width: 100%; border-collapse: collapse; font-size: 13px; background: #1f2231; border-radius: 6px; color: white;">
                        <tr style="color: #cbd5e1; border-bottom: 1px solid rgba(255,255,255,0.05); background: rgba(0,0,0,0.2);">
                            <th style="padding: 12px; text-align: left;">Tên</th>
                            <th style="padding: 12px; text-align: right;">Giá trị</th>
                            <th style="padding: 12px; text-align: center;">Hành động</th>
                        </tr>
                        ${indRows(ta.technical_indicators)}
                    </table>
                </div>
                
                <!-- Column 2: Đường trung bình -->
                <div>
                    <div style="font-weight: bold; margin-bottom: 12px; font-size: 14px; color: white;">Đường trung bình</div>
                    <table style="width: 100%; border-collapse: collapse; font-size: 13px; background: #1f2231; border-radius: 6px; color: white;">
                        <tr style="color: #cbd5e1; border-bottom: 1px solid rgba(255,255,255,0.05); background: rgba(0,0,0,0.2);">
                            <th style="padding: 12px; text-align: left;">Tên</th>
                            <th style="padding: 12px; text-align: center;">Simple</th>
                            <th style="padding: 12px; text-align: center;">Exponential</th>
                        </tr>
                        ${maRows(ta.moving_averages)}
                    </table>
                </div>
            </div>
            
        </div>
    `;

    modal.style.display = 'flex';
}

// Close modal on background click
document.addEventListener('click', function(e) {
    const modal = document.getElementById('ta-modal');
    if (e.target === modal) {
        modal.style.display = 'none';
    }
});

document.addEventListener("DOMContentLoaded", () => {
    
    // Check auth state on load
    checkUserSession();
    
    // --- Ngôn ngữ (i18n) ---
    const langSelector = document.getElementById("lang-selector");
    let currentLang = 'vi';
    window.getCurrentLang = () => currentLang;

    async function updateTickerTape() {
        const tape = document.getElementById("ticker-tape-content");
        if(!tape) return;
        
        try {
            const aiSignalText = currentLang === 'en' ? 'AI Signal: Uptrend confirmed for VCB' : 'Tín hiệu AI: Xác nhận xu hướng tăng cho VCB';
            const aiEvalText = currentLang === 'en' ? 'AI Evaluation: HPG shows strong fundamentals' : 'Đánh giá AI: HPG có nền tảng cơ bản vững chắc';
            const warningText = currentLang === 'en' ? 'AI Alert: High volatility detected in Real Estate sector' : 'Cảnh báo AI: Phát hiện biến động cao ở nhóm Bất động sản';
            
            const res = await apiFetch('/api/ticker-tape');
            const data = await res.json();
            
            let html = '';
            for (const [ticker, info] of Object.entries(data)) {
                const colorClass = info.change_pct >= 0 ? 'ticker-up' : 'ticker-down';
                const sign = info.change_pct >= 0 ? '+' : '';
                
                let formatPrice = '';
                if(ticker === 'VNINDEX' || ticker === 'VN30') {
                    formatPrice = info.price.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2});
                } else {
                    formatPrice = info.price.toLocaleString();
                }
                
                const formatPct = `${sign}${info.change_pct.toFixed(1)}%`;
                
                html += `<span class="ticker-item">${ticker} <span class="${colorClass}">${formatPrice} (${formatPct})</span></span>`;
                
                if(ticker === 'MWG') html += `<span class="ticker-item"><span class="ticker-ai">🤖 ${aiSignalText}</span></span>`;
                if(ticker === 'HPG') html += `<span class="ticker-item"><span class="ticker-ai">💡 ${aiEvalText}</span></span>`;
                if(ticker === 'SSI') html += `<span class="ticker-item"><span class="ticker-ai">⚠️ ${warningText}</span></span>`;
            }
            if(html) {
                tape.innerHTML = html;
            }
        } catch(e) {
            console.error("Ticker tape fetch error", e);
        }
    }

    function updateLanguage() {
        currentLang = langSelector.value;
        const dict = I18N[currentLang];
        document.querySelectorAll("[data-i18n]").forEach(el => {
            const key = el.getAttribute("data-i18n");
            if (dict[key]) el.textContent = dict[key];
        });
        document.querySelectorAll("[data-i18n-ph]").forEach(el => {
            const key = el.getAttribute("data-i18n-ph");
            if (dict[key]) el.setAttribute("placeholder", dict[key]);
        });
        updateTickerTape();
        if (document.getElementById('leaderboard-modal').style.display === 'flex') {
            renderLeaderboard();
        }
    }
    
    window.updateLanguageGlobal = updateLanguage;
    langSelector.addEventListener("change", updateLanguage);
    updateLanguage();

    // --- Leaderboard Logic ---
    function openLeaderboard() {
        document.getElementById('leaderboard-modal').style.display = 'flex';
        renderLeaderboard();
    }
    window.openLeaderboard = openLeaderboard;
    
    function closeLeaderboard() {
        document.getElementById('leaderboard-modal').style.display = 'none';
    }
    window.closeLeaderboard = closeLeaderboard;
    
    function renderLeaderboard() {
        const lbBody = document.getElementById('leaderboard-body');
        if(!lbBody) return;
        
        const mockData = [
            { rank: 1, user: 'alex***@gmail.com', port: 'FPT (40%), VCB (35%), HPG (25%)', sharpe: '2.84' },
            { rank: 2, user: 'nguy***@dnt.com', port: 'MWG (50%), MBB (30%), SSI (20%)', sharpe: '2.51' },
            { rank: 3, user: 'tran***@yahoo.com', port: 'VNM (60%), VIC (40%)', sharpe: '1.92' },
            { rank: 4, user: 'phan***@gmail.com', port: 'TCB (45%), VHM (30%), REE (25%)', sharpe: '1.75' },
            { rank: 5, user: 'leho***@outlook.com', port: 'VND (50%), SHB (50%)', sharpe: '1.42' }
        ];
        
        let html = '';
        mockData.forEach((item, index) => {
            const rowColor = index === 0 ? 'rgba(0, 255, 170, 0.1)' : 'transparent';
            const rankStyle = index === 0 ? 'color: #00FFAA; font-weight: bold; font-size: 1.2rem;' : '';
            html += `
                <tr style="border-bottom: 1px solid rgba(255,255,255,0.05); background: ${rowColor};">
                    <td style="padding: 15px 10px; ${rankStyle}">${index === 0 ? '🏆 1' : item.rank}</td>
                    <td style="padding: 15px 10px;">${item.user}</td>
                    <td style="padding: 15px 10px; font-size: 0.8rem; color: #00B8FF;">${item.port}</td>
                    <td style="padding: 15px 10px; text-align: right; color: #00FFAA; font-weight: bold;">${item.sharpe}</td>
                </tr>
            `;
        });
        lbBody.innerHTML = html;
    }

    // --- Copilot Chat Logic ---
    window.sendCopilotMessage = async function() {
        const inputEl = document.getElementById("copilot-input");
        const msg = inputEl.value.trim();
        if(!msg) return;
        
        const chatWindow = document.getElementById("copilot-messages");
        
        // Add User Message
        const userMsgHtml = `<div style="align-self: flex-end; background: rgba(0,255,170,0.1); border: 1px solid rgba(0,255,170,0.3); padding: 10px 14px; border-radius: 12px; border-top-right-radius: 2px; color: #00FFAA; max-width: 85%; word-wrap: break-word;">${msg}</div>`;
        chatWindow.insertAdjacentHTML("beforeend", userMsgHtml);
        inputEl.value = "";
        
        // Add Loading Indicator
        const loadingId = "msg-" + Date.now();
        const botMsgHtml = `<div id="${loadingId}" style="align-self: flex-start; background: rgba(255,255,255,0.05); padding: 10px 14px; border-radius: 12px; border-top-left-radius: 2px; color: #e2e8f0; max-width: 85%; line-height: 1.4;">⏳ Đang phân tích...</div>`;
        chatWindow.insertAdjacentHTML("beforeend", botMsgHtml);
        chatWindow.scrollTop = chatWindow.scrollHeight;
        
        const context = window.lastSimulationData ? {
            monte_carlo: window.lastSimulationData.monte_carlo,
            stress_test: window.lastSimulationData.stress_test,
            advanced_metrics: window.lastSimulationData.advanced_metrics
        } : { note: "User haven't run any simulation yet." };
        
        try {
            let token = "";
            if (window.supabaseClient) {
                const { data: { session } } = await window.supabaseClient.auth.getSession();
                if (session) token = session.access_token;
            }
            const res = await fetch('/api/copilot-chat', {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'Authorization': token ? `Bearer ${token}` : ''
                },
                body: JSON.stringify({
                    message: msg,
                    context: context,
                    lang: window.getCurrentLang()
                })
            });
            
            if (!res.ok) {
                if(res.status === 401) {
                    document.getElementById(loadingId).innerHTML = "Vui lòng đăng nhập để sử dụng Copilot.";
                    return;
                }
                document.getElementById(loadingId).innerHTML = "API Error: " + res.status;
                return;
            }
            
            const reader = res.body.getReader();
            const decoder = new TextDecoder("utf-8");
            let firstChunk = true;
            let fullText = "";
            
            while (true) {
                const { done, value } = await reader.read();
                if (done) break;
                const chunkText = decoder.decode(value, { stream: true });
                if (firstChunk) {
                    document.getElementById(loadingId).innerHTML = "";
                    firstChunk = false;
                }
                fullText += chunkText;
                // Basic markdown parsing for bold
                let displayHtml = fullText.replace(/\*\*(.*?)\*\*/g, '<b>$1</b>');
                document.getElementById(loadingId).innerHTML = displayHtml;
                chatWindow.scrollTop = chatWindow.scrollHeight;
            }
        } catch(e) {
            document.getElementById(loadingId).innerHTML = "Lỗi kết nối: " + e.message;
        }
    };

    // --- AI Sentiment Radar Logic ---
    async function fetchAndRenderSentimentRadar(tickersArray) {
        try {
            document.getElementById("sentiment-radar-card").style.display = "block";
            document.getElementById("radar-chart-container").innerHTML = `<div style="color:#94a3b8; text-align:center; margin-top:50px;">${I18N[currentLang]['loading_api']}</div>`;
            
            const res = await apiFetch(`/api/sentiment-radar?tickers=${tickersArray.join(',')}&lang=${currentLang}`);
            const data = await res.json();
            
            if(!data || Object.keys(data).length === 0) {
                document.getElementById("radar-chart-container").innerHTML = "<div style='color:red;'>Failed to load sentiment.</div>";
                return;
            }
            
            const labels = Object.keys(data);
            const values = Object.values(data);
            
            const trace = {
                type: 'scatterpolar',
                r: values,
                theta: labels,
                fill: 'toself',
                fillcolor: 'rgba(0, 255, 170, 0.2)',
                line: { color: '#00FFAA' },
                marker: { color: '#00FFAA', size: 8 }
            };
            
            const layout = {
                polar: {
                    radialaxis: {
                        visible: true,
                        range: [0, 1], // Since backend returns 0.0 to 1.0
                        tickfont: { color: '#94a3b8' }
                    },
                    angularaxis: {
                        tickfont: { color: 'white', size: 12 }
                    },
                    bgcolor: 'rgba(0,0,0,0)'
                },
                paper_bgcolor: 'rgba(0,0,0,0)',
                plot_bgcolor: 'rgba(0,0,0,0)',
                margin: { t: 30, b: 30, l: 30, r: 30 },
                showlegend: false
            };
            
            Plotly.newPlot('radar-chart-container', [trace], layout, {displayModeBar: false});
        } catch(e) {
            console.error("Radar Error", e);
            document.getElementById("radar-chart-container").innerHTML = "<div style='color:red;'>Error fetching sentiment radar.</div>";
        }
    }

    // --- Export Logic ---
    async function exportReport() {
        const btn = document.getElementById('btn-export-report');
        const originalText = btn.innerHTML;
        btn.innerHTML = currentLang === 'en' ? '⏳ Processing...' : '⏳ Đang xử lý...';
        btn.disabled = true;

        const content = document.getElementById('view-quant');
        if (!content) return;
        
        try {
            const canvas = await html2canvas(content, {
                backgroundColor: '#05050A',
                scale: 2, 
                logging: false,
                useCORS: true
            });
            
            const link = document.createElement('a');
            link.download = `DNT_Quant_Report_${new Date().toISOString().slice(0,10)}.png`;
            link.href = canvas.toDataURL('image/png');
            link.click();
        } catch (e) {
            console.error("Export failed:", e);
            alert("Export failed: " + e.message);
        } finally {
            btn.innerHTML = originalText;
            btn.disabled = false;
        }
    }
    window.exportReport = exportReport;

    // --- Tab Switch Logic ---
    let currentMode = 'optimizer';
    const navItems = document.querySelectorAll(".nav-menu .nav-item");
    const modeOpts = document.getElementById("mode-optimizer");
    const modeEval = document.getElementById("mode-evaluator");
    const modeFin = document.getElementById("mode-financial");
    
    function hideAllModes() {
        modeOpts.style.display = 'none';
        modeEval.style.display = 'none';
        if(modeFin) modeFin.style.display = 'none';
        navItems.forEach(el => el.classList.remove('active'));
        document.getElementById("view-quant").style.display = 'none';
        document.getElementById("view-financial").style.display = 'none';
    }

    navItems[0].addEventListener("click", () => {
        hideAllModes(); navItems[0].classList.add('active');
        modeOpts.style.display = 'block'; currentMode = 'optimizer';
        document.getElementById("view-quant").style.display = 'block';
    });
    navItems[1].addEventListener("click", () => {
        hideAllModes(); navItems[1].classList.add('active');
        modeEval.style.display = 'block'; currentMode = 'evaluator';
        document.getElementById("view-quant").style.display = 'block';
    });
    if(navItems[2]) {
        navItems[2].addEventListener("click", () => {
            hideAllModes(); navItems[2].classList.add('active');
            modeFin.style.display = 'block'; currentMode = 'financial';
            document.getElementById("view-financial").style.display = 'block';
        });
    }

    // --- Evaluator Dynamic Rows ---
    const addRowBtn = document.getElementById("add-holding-btn");
    const holdingsList = document.getElementById("holdings-list");
    addRowBtn.addEventListener("click", () => {
        const div = document.createElement("div");
        div.className = "holding-row";
        div.style.cssText = "display: flex; gap: 5px; margin-bottom: 5px;";
        div.innerHTML = `
            <input type="text" class="glass-input t-input" placeholder="Ticker" style="width: 50%;">
            <input type="number" class="glass-input v-input" placeholder="Qty" style="width: 40%;">
            <button class="remove-btn" style="background:var(--neon-alert); color:white; border:none; border-radius:4px; width: 10%; font-weight:bold; cursor:pointer;">X</button>
        `;
        div.querySelector('.remove-btn').onclick = () => { div.remove(); onInputChanged(); };
        holdingsList.appendChild(div);
        attachInputListeners();
    });

    // --- Live Capital (Debounce Live Pricing) ---
    let typingTimer;
    let cachedPrices = {};
    
    function attachInputListeners() {
        const inputs = document.querySelectorAll(".holding-row input");
        inputs.forEach(input => {
            input.removeEventListener('input', onInputChanged); // prevent duplicate bindings
            input.addEventListener('input', onInputChanged);
        });
    }

    function onInputChanged() {
        clearTimeout(typingTimer);
        document.getElementById("live-capital-display").textContent = "...";
        typingTimer = setTimeout(calculateLiveCapital, 600);
    }

    async function calculateLiveCapital() {
        const rows = document.querySelectorAll(".holding-row");
        let queryTickers = [];
        let holdings = [];
        
        for(let row of rows) {
            let t = row.querySelector('.t-input').value.trim().toUpperCase();
            let v = parseFloat(row.querySelector('.v-input').value);
            if (t) {
                queryTickers.push(t);
                if (!isNaN(v)) holdings.push({t, v});
            }
        }
        
        if (queryTickers.length === 0) {
            document.getElementById("live-capital-display").textContent = "0₫";
            return;
        }
        
        let tickersQueryStr = queryTickers.join(",");
        try {
            let res = await apiFetch('/api/current-prices?tickers=' + tickersQueryStr);
            let prices = await res.json();
            
            Object.assign(cachedPrices, prices);
            
            let total = 0;
            for (let h of holdings) {
                if (cachedPrices[h.t]) {
                    total += cachedPrices[h.t] * h.v;
                }
            }
            document.getElementById("live-capital-display").textContent = formatVND(total);
        } catch (e) {
            console.error("Lỗi cập nhật giá realtime:", e);
        }
    }

    // --- Currency Formatting for Capital Input ---
    const capitalInput = document.getElementById("capital-input");
    if (capitalInput) {
        capitalInput.addEventListener("input", (e) => {
            let value = e.target.value.replace(/[^0-9]/g, "");
            if (value) {
                e.target.value = parseInt(value).toLocaleString("vi-VN");
            } else {
                e.target.value = "";
            }
        });
    }
    
    // Call initial listener
    attachInputListeners();

    // --- Common API Handlers ---
    const apiStatus = document.getElementById("api-status");
    const statusDot = document.querySelector(".status-dot");
    const runBtn = document.getElementById("run-btn");
    const evalBtn = document.getElementById("eval-btn");
    const stressBtn = document.getElementById("stress-btn");

    let latestSimulationData = null;

    function formatVND(value) {
        return Math.floor(value).toLocaleString('vi-VN') + '₫';
    }

    window.lastSimulationData = null;

    function handleApiResponse(data) {
        window.lastSimulationData = data;
        if (data.error) {
            alert(data.error);
            return;
        }
        
        latestSimulationData = data;
        
        // Hide welcome message on first result
        const welcome = document.getElementById("welcome-message");
        if (welcome) welcome.style.display = "none";

        if (data.chart) {
            Plotly.react('chart-container', data.chart.data, data.chart.layout, { responsive: true, displayModeBar: false });
            document.getElementById('main-chart-card').style.display = 'block';
            const exportBtn = document.getElementById('btn-export-report');
            if(exportBtn) exportBtn.style.display = 'inline-block';
        } else {
            // Hide main chart on Evaluator Mode
            const mainCard = document.getElementById('main-chart-card');
            if(mainCard) mainCard.style.display = 'none';
        }
        
        if (data.backtest_chart) {
            const btCard = document.getElementById('backtest-chart-card');
            if(btCard) btCard.style.display = 'block';
            Plotly.react('backtest-chart-container', data.backtest_chart.data, data.backtest_chart.layout, { responsive: true, displayModeBar: false });
        }
        
        if (data.pie_chart) {
            document.getElementById('pie-card').style.display = 'block';
            Plotly.react('pie-chart-container', data.pie_chart.data, data.pie_chart.layout, { responsive: true, displayModeBar: false });
        }
        
        if (data.raw_prices) {
            document.getElementById('raw-prices-card').style.display = 'block';
            if (data.last_updated_date) {
                document.getElementById('timestamp-date').textContent = data.last_updated_date;
            }
            const tbody = document.getElementById('raw-prices-tbody');
            tbody.innerHTML = '';
            for (const [ticker, price] of Object.entries(data.raw_prices)) {
                tbody.innerHTML += `<tr><td style="padding:8px; border-bottom:1px solid rgba(255,255,255,0.05);">${ticker}</td><td style="padding:8px; border-bottom:1px solid rgba(255,255,255,0.05); color:var(--neon);">${formatVND(price)}</td></tr>`;
            }
        }

        if (data.advanced_metrics) {
            document.getElementById('advanced-metrics-card').style.display = 'block';
            document.getElementById('metric-beta').textContent = data.advanced_metrics.beta != null ? data.advanced_metrics.beta.toFixed(2) : '--';
            document.getElementById('metric-sortino').textContent = data.advanced_metrics.sortino != null ? data.advanced_metrics.sortino.toFixed(2) : '--';
            document.getElementById('metric-treynor').textContent = data.advanced_metrics.treynor != null ? data.advanced_metrics.treynor.toFixed(4) : '--';
            document.getElementById('metric-rsq').textContent = data.advanced_metrics.r_squared != null ? data.advanced_metrics.r_squared.toFixed(2) : '--';
            document.getElementById('metric-calmar').textContent = data.advanced_metrics.calmar != null ? data.advanced_metrics.calmar.toFixed(2) : '--';
            document.getElementById('metric-mdd').textContent = data.advanced_metrics.max_drawdown != null ? (data.advanced_metrics.max_drawdown * 100).toFixed(2) + '%' : '--';
        }
        
        // --- Trading Signals ---
        if (data.trading_signals) {
            window.globalTradingSignals = data.trading_signals; // Save for modal
            const signalsCard = document.getElementById('trading-signals-card');
            const signalsTbody = document.getElementById('trading-signals-tbody');
            if (signalsCard && signalsTbody) {
                signalsTbody.innerHTML = '';
                for (const [ticker, sig] of Object.entries(data.trading_signals)) {
                    let badgeClass = 'badge-hold';
                    if (sig.action.includes('BUY')) badgeClass = 'badge-buy';
                    else if (sig.action.includes('SELL')) badgeClass = 'badge-sell';
                    
                    let taBtn = '';
                    if (sig.ta_analysis && !sig.ta_analysis.error) {
                         const taDetailText = I18N[currentLang]['btn_ta_detail'] || 'Chi tiết TA';
                         taBtn = `<button onclick="openTAModal('${ticker}')" style="margin-top: 5px; padding: 4px 8px; font-size: 0.75rem; background: rgba(139, 92, 246, 0.2); border: 1px solid #8b5cf6; color: white; border-radius: 4px; cursor: pointer;">${taDetailText}</button>`;
                    }

                    signalsTbody.innerHTML += `
                        <tr style="border-bottom: 1px solid rgba(255,255,255,0.05);">
                            <td style="padding: 10px; font-weight: bold; color: white;">${ticker}</td>
                            <td style="padding: 10px;">
                                <span class="signal-badge ${badgeClass}">${sig.action}</span>
                                <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 5px; max-width: 250px;">${sig.detail || ''}</div>
                            </td>
                            <td style="padding: 10px; color: var(--text-muted);">${sig.volume.toLocaleString('vi-VN')} CP<br><small style="font-size: 0.75rem;">@ ${formatVND(sig.price)}</small></td>
                            <td style="padding: 10px; text-align: right;">
                                <a href="${sig.broker_url}" target="_blank" class="btn-vps-cta mb-1">${I18N[currentLang]['btn_vps_cta']}</a><br>
                                ${taBtn}
                            </td>
                        </tr>
                    `;
                }
                signalsCard.style.display = 'block';
            }
        }
        
        const mc = data.monte_carlo;
        const values = mc.monetary_values;
        
        const displayCap = document.getElementById("display-capital");
        displayCap.style.transform = "scale(1.1)";
        displayCap.textContent = formatVND(values.expected_value);
        
        const ciText = document.getElementById("ci-text");
        ciText.textContent = `${I18N[currentLang]['ci_text']} [${formatVND(values.ci_lower_value)} -> ${formatVND(values.ci_upper_value)}]`;
        
        const displayRisk = document.getElementById("display-risk");
        const varLoss = values.var_value_loss;
        const varLossAbs = Math.abs(varLoss);
        if (varLoss >= 0) {
            // VaR dương: ở kịch bản xấu nhất 5%, danh mục vẫn có lãi
            displayRisk.textContent = varLossAbs < 1 ? I18N[currentLang]['var_profitable_label'] : "+" + formatVND(varLoss);
            displayRisk.style.color = "var(--neon-green)";
            displayRisk.title = I18N[currentLang]['var_positive_tooltip'];
        } else {
            // VaR âm: ở kịch bản xấu nhất 5%, danh mục bị lỗ
            const lossDisplay = varLossAbs < 1 ? "~0₫" : "-" + formatVND(varLossAbs);
            displayRisk.textContent = lossDisplay;
            displayRisk.style.color = "var(--neon-alert)";
            displayRisk.title = I18N[currentLang]['var_negative_tooltip'];
        }

        stressBtn.style.display = "inline-block";
        document.getElementById("stress-text").style.display = "none";
        
        apiStatus.textContent = I18N[currentLang]['status_connected'] + " (100%)";
        statusDot.style.background = "var(--neon-green)";
        statusDot.style.boxShadow = "0 0 8px var(--neon-green)";

        setTimeout(() => { displayCap.style.transform = "scale(1)"; }, 200);

        // --- Render Live News ---
        const newsCard = document.getElementById("live-news-card");
        const newsList = document.getElementById("live-news-list");
        const newsTickersLabel = document.getElementById("news-tickers-list");
        
        if (data.news_data && Object.keys(data.news_data).length > 0) {
            newsList.innerHTML = "";
            let fetchedTickers = [];
            for (const [t, newsArr] of Object.entries(data.news_data)) {
                if (newsArr.length > 0) {
                    fetchedTickers.push(t);
                    newsArr.forEach(nItem => {
                        const itemDiv = document.createElement("div");
                        itemDiv.style.background = "rgba(255,255,255,0.05)";
                        itemDiv.style.padding = "10px";
                        itemDiv.style.borderRadius = "6px";
                        itemDiv.style.borderLeft = "3px solid #00B8FF";
                        itemDiv.innerHTML = `
                            <div style="font-size: 0.75rem; color: #9ca3af; margin-bottom: 3px;">
                                <strong style="color: #00B8FF;">${t}</strong> • ${nItem.publishDate}
                            </div>
                            <div style="font-size: 0.9rem; color: white; font-weight: 500;">
                                ${nItem.title}
                            </div>
                        `;
                        newsList.appendChild(itemDiv);
                    });
                }
            }
            if (fetchedTickers.length > 0) {
                newsTickersLabel.textContent = fetchedTickers.join(", ");
                newsCard.style.display = "block";
            } else {
                newsCard.style.display = "none";
            }
        } else {
            newsCard.style.display = "none";
        }

        // --- NEW: Trigger AI Advice Automatically ---
        const aiCheckbox = document.getElementById("generate-ai-report-checkbox");
        if (aiCheckbox && aiCheckbox.checked) {
            fetchAIAdvice(data);
        } else {
            const aiCard = document.getElementById("ai-advice-card");
            if (aiCard) aiCard.style.display = "none";
        }
    }

    async function fetchAIAdvice(data) {
        const aiCard = document.getElementById("ai-advice-card");
        const aiText = document.getElementById("ai-text");
        const aiLoading = document.getElementById("ai-loading");
        const aiBadge = document.getElementById("ai-badge");
        const aiBadgeText = document.getElementById("ai-badge-text");

        // Reset & Show Card
        aiCard.style.display = "block";
        aiText.innerHTML = "";
        aiLoading.style.display = "flex";
        aiBadge.classList.remove("done");
        aiBadgeText.textContent = I18N[currentLang]['ai_analyzing'];

        let manualBctcPayload = [];
        if (document.getElementById("manual-bctc-alert").style.display !== "none" && document.getElementById("use-manual-bctc-checkbox").checked) {
            manualBctcPayload = availableManualBCTC;
            aiBadgeText.textContent = "Gemini AI đang đọc BCTC chuyên sâu (RAG)...";
        }

        try {
            const response = await apiFetch('/api/ai-advice', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    monte_carlo: data.monte_carlo,
                    stress_test: data.stress_test,
                    advanced_metrics: data.advanced_metrics,
                    fundamentals: data.fundamentals,
                    manual_bctc_tickers: manualBctcPayload,
                    news_data: data.news_data,
                    lang: currentLang
                })
            });

            if (!response.ok) throw new Error("AI API Error");

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            
            aiLoading.style.display = "none";
            
            // Add typing cursor
            const cursor = document.createElement("span");
            cursor.className = "ai-cursor";
            aiText.appendChild(cursor);

            let fullText = "";

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;
                
                const chunk = decoder.decode(value, { stream: true });
                fullText += chunk;
                
                // Simple Markdown-ish formatting as we stream
                // Replacing **bold** and *italic* and newlines
                let formatted = fullText
                    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                    .replace(/\*(.*?)\*/g, '<em>$1</em>')
                    .replace(/\n/g, '<br>');
                
                aiText.innerHTML = formatted;
                aiText.appendChild(cursor);
                
                // Auto-scroll to bottom if needed
                aiCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }

            // Finish
            cursor.remove();
            aiBadge.classList.add("done");
            aiBadgeText.textContent = I18N[currentLang]['ai_done'];
            
            // Hiện nút Download PDF
            document.getElementById('btn-export-pdf').style.display = 'inline-block';
            checkUserSession();

        } catch (err) {
            console.error("AI Advice Error:", err);
            aiLoading.style.display = "none";
            aiText.innerHTML = `<span style="color: var(--neon-alert)">⚠️ Error: Không thể kết nối Gemini AI. Kiểm tra .env hoặc API Key.</span>`;
        }
    }

    // --- Giấy Phép / Export PDF Logic ---
    const btnExportPdf = document.getElementById('btn-export-pdf');
    if (btnExportPdf) {
        btnExportPdf.addEventListener('click', () => {
            const element = document.getElementById('pdf-content-wrapper');
            const title = document.getElementById('pdf-report-title');
            
            // Hiện tiêu đề ẩn chuyên cho PDF
            title.style.display = 'block';
            
            // Tùy chỉnh Options cho HTML2PDF
            const opt = {
              margin:       [15, 15, 15, 15],
              filename:     `DNT_Quant_VIP_Report_${new Date().toISOString().split('T')[0]}.pdf`,
              image:        { type: 'jpeg', quality: 1 },
              html2canvas:  { 
                  scale: 2, 
                  useCORS: true, 
                  backgroundColor: '#0f172a',
                  windowWidth: 1024 // Đảm bảo html2canvas lấy được width hợp lý để ko bị bóp méo
              }, 
              jsPDF:        { unit: 'mm', format: 'a4', orientation: 'portrait' }
            };

            // Ép màu chữ trắng và background ciem để HTML2Canvas ko tự convert thành màu trắng xoá
            const originalColor = element.style.color;
            const originalBg = element.style.backgroundColor;
            const originalPadding = element.style.padding;
            
            element.style.color = '#cbd5e1';
            element.style.backgroundColor = '#0f172a';
            element.style.padding = '20px';

            // Trạng thái nút tải
            btnExportPdf.textContent = 'Đang render...';
            btnExportPdf.disabled = true;

            html2pdf().set(opt).from(element).save().then(() => {
                // Phục hồi lại state cũ
                title.style.display = 'none';
                element.style.color = originalColor;
                element.style.backgroundColor = originalBg;
                element.style.padding = originalPadding;
                
                btnExportPdf.textContent = '⬇️ Tải PDF';
                btnExportPdf.disabled = false;
            }).catch(err => {
                console.error("Lỗi xuất PDF: ", err);
                btnExportPdf.textContent = 'Lỗi Render! Thử lại';
                btnExportPdf.disabled = false;
                title.style.display = 'none';
            });
        });
    }

    function handleError(error) {
        console.error(error);
        apiStatus.textContent = I18N[currentLang]['err_conn'];
        statusDot.style.background = "var(--neon-alert)";
        statusDot.style.boxShadow = "0 0 8px var(--neon-alert)";
        document.getElementById('chart-container').innerHTML = `<p style="color: var(--neon-alert); text-align: center; margin-top: 50px;">${I18N[currentLang]['err_wait']}</p>`;
    }

    // --- RAG BCTC Checker ---
    const bctcAlert = document.getElementById("manual-bctc-alert");
    const bctcAlertTickers = document.getElementById("bctc-alert-tickers");
    let availableManualBCTC = [];

    async function evaluateTickersForManualBCTC() {
        let tickers = [];
        const activeNav = document.querySelector('.nav-item.active');
        if (!activeNav) return;

        if (activeNav.getAttribute('data-i18n') === 'nav_opt') {
            const raw = document.getElementById("tickers-input").value;
            tickers = raw.split(',').map(t => t.trim().toUpperCase()).filter(t => t);
        } else if (activeNav.getAttribute('data-i18n') === 'nav_eval') {
            document.querySelectorAll('.t-input').forEach(input => {
                let val = input.value.trim().toUpperCase();
                if(val) tickers.push(val);
            });
        }
        
        if (tickers.length === 0) {
            bctcAlert.style.display = "none";
            availableManualBCTC = [];
            return;
        }

        try {
            const res = await apiFetch(`/api/check-manual-bctc?tickers=${tickers.join(',')}`);
            const data = await res.json();
            const matched = Object.keys(data);
            
            if (matched.length > 0) {
                availableManualBCTC = matched;
                bctcAlertTickers.textContent = matched.join(', ');
                bctcAlert.style.display = "block";
            } else {
                availableManualBCTC = [];
                bctcAlert.style.display = "none";
            }
        } catch (e) {
            console.error(e);
        }
    }

    document.getElementById("tickers-input").addEventListener("blur", evaluateTickersForManualBCTC);
    document.getElementById("holdings-list").addEventListener("blur", (e) => {
        if (e.target && e.target.classList.contains("t-input")) {
            evaluateTickersForManualBCTC();
        }
    }, true);


    function showTokenDeduction(buttonElement, cost) {
        if (!currentUser) return;
        
        const rect = buttonElement.getBoundingClientRect();
        const floating = document.createElement("div");
        floating.className = "token-float";
        floating.textContent = `-${cost} Token${cost > 1 ? 's' : ''}`;
        
        floating.style.left = `${rect.left + rect.width / 2 - 40}px`;
        floating.style.top = `${rect.top + window.scrollY - 20}px`;
        
        document.body.appendChild(floating);
        
        setTimeout(() => {
            floating.remove();
        }, 1000);
    }
    function showQuantLoader(containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;
        
        container.innerHTML = `
            <div class="ai-loader-container" id="ai-loader-element">
                <div class="ai-loader-spinner"></div>
                <div class="ai-loader-text" data-i18n="loader_title">${I18N[currentLang]['loader_title']}</div>
                <div class="ai-loader-subtext" data-i18n="loader_sub">${I18N[currentLang]['loader_sub']}</div>
                <div class="ai-loader-progress"></div>
            </div>
        `;
    }

    function clearQuantLoader() {
        const loader = document.getElementById('ai-loader-element');
        if (loader) loader.remove();
    }

    // Execution Mode: Optimizer
    runBtn.addEventListener("click", () => {
        const rawCap = document.getElementById("capital-input").value.replace(/\./g, "");
        const capInput = parseFloat(rawCap);
        const retInput = parseFloat(document.getElementById("target-return").value) / 100;
        const tickersStr = document.getElementById("tickers-input").value;
        let tickersArray = tickersStr.split(',').map(s => s.trim().toUpperCase()).filter(s => s.length > 0);

        if (isNaN(capInput) || isNaN(retInput) || tickersArray.length < 2) {
            alert(I18N[currentLang]['err_input']); return;
        }

        let totalCost = 2;
        const aiCheckbox = document.getElementById("generate-ai-report-checkbox");
        if (aiCheckbox && aiCheckbox.checked) totalCost += 2;
        
        if (!currentUser) {
            alert(currentLang === 'en' ? 'Please Login first!' : 'Vui lòng Đăng nhập trước!');
            openAuthModal();
            return;
        }
        let userTotalTokens = (userProfile ? (userProfile.free_credits + userProfile.paid_tokens) : 0);
        if (userTotalTokens < totalCost) {
            alert(I18N[currentLang]['err_tokens']);
            return;
        }

        showTokenDeduction(runBtn, totalCost);

        runBtn.textContent = I18N[currentLang]['loading_api']; runBtn.disabled = true;
        showQuantLoader('chart-container');

        const tfSelect = document.getElementById("opt-timeframe-select");
        const tfValue = tfSelect ? parseInt(tfSelect.value) : 252;
        const personaSelect = document.getElementById("ai-persona-select");
        const personaValue = personaSelect ? personaSelect.value : 'quant';
        
        const minWeightInput = document.getElementById("opt-min-weight");
        const maxWeightInput = document.getElementById("opt-max-weight");
        const minWeight = minWeightInput ? parseFloat(minWeightInput.value) / 100 : 0.05;
        const maxWeight = maxWeightInput ? parseFloat(maxWeightInput.value) / 100 : 0.40;
        
        const backtestDateInput = document.getElementById("opt-backtest-date");
        const backtestDate = backtestDateInput ? backtestDateInput.value : "";

        Promise.all([
            apiFetch('/api/run-simulation', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    capital: capInput, 
                    target_return: retInput, 
                    tickers: tickersArray, 
                    lang: currentLang, 
                    timeframe_days: tfValue, 
                    persona: personaValue,
                    min_weight: minWeight,
                    max_weight: maxWeight,
                    backtest_date: backtestDate
                })
            }).then(res => {
                if (!res.ok) throw new Error("Simulation API Error");
                return res.json();
            }),
            apiFetch(`/api/news?tickers=${tickersArray.join(',')}`).then(r => r.json()).catch(() => ({})),
            fetchAndRenderSentimentRadar(tickersArray)
        ])
        .then(([simData, newsData, _]) => {
            simData.news_data = newsData;
            handleApiResponse(simData);
        })
        .catch(handleError)
        .finally(() => { clearQuantLoader(); runBtn.textContent = I18N[currentLang]['btn_run']; runBtn.disabled = false; checkUserSession(); });
    });

    // Execution Mode: Evaluator
    evalBtn.addEventListener("click", () => {
        const rows = document.querySelectorAll(".holding-row");
        let holdings = {};
        for(let row of rows) {
            let t = row.querySelector('.t-input').value.trim().toUpperCase();
            let v = parseFloat(row.querySelector('.v-input').value);
            if(t && !isNaN(v)) holdings[t] = v;
        }

        const tf = parseInt(document.getElementById("timeframe-select").value);

        if (Object.keys(holdings).length === 0) {
            alert(I18N[currentLang]['err_input']); return;
        }

        let totalCost = 2;
        const aiCheckbox = document.getElementById("generate-ai-report-checkbox");
        if (aiCheckbox && aiCheckbox.checked) totalCost += 2;
        
        if (!currentUser) {
            alert(currentLang === 'en' ? 'Please Login first!' : 'Vui lòng Đăng nhập trước!');
            openAuthModal();
            return;
        }
        let userTotalTokens = (userProfile ? (userProfile.free_credits + userProfile.paid_tokens) : 0);
        if (userTotalTokens < totalCost) {
            alert(I18N[currentLang]['err_tokens']);
            return;
        }

        showTokenDeduction(evalBtn, totalCost);

        evalBtn.textContent = I18N[currentLang]['loading_api']; evalBtn.disabled = true;
        showQuantLoader('chart-container');

        const personaSelect = document.getElementById("ai-persona-select");
        const personaValue = personaSelect ? personaSelect.value : 'quant';

        Promise.all([
            apiFetch('/api/evaluate-portfolio', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({holdings: holdings, days: tf, lang: currentLang, persona: personaValue})
            }).then(res => {
                if (!res.ok) throw new Error("Evaluate API Error");
                return res.json();
            }),
            apiFetch(`/api/news?tickers=${Object.keys(holdings).join(',')}`).then(r => r.json()).catch(() => ({}))
        ])
        .then(([simData, newsData]) => {
            simData.news_data = newsData;
            handleApiResponse(simData);
        })
        .catch(handleError)
        .finally(() => { clearQuantLoader(); evalBtn.textContent = I18N[currentLang]['btn_eval']; evalBtn.disabled = false; checkUserSession(); });
    });

    // Stress Test Button
    stressBtn.addEventListener("click", () => {
        if (!latestSimulationData || !latestSimulationData.stress_test) return;
        const lossVnd = latestSimulationData.stress_test.estimated_loss_vnd;
        
        const stressText = document.getElementById("stress-text");
        stressText.style.display = "block";
        stressText.style.transform = "scale(1.1)";
        stressText.textContent = `${I18N[currentLang]['stress_drop']} -${formatVND(Math.abs(lossVnd))}`;
        
        setTimeout(() => { stressText.style.transform = "scale(1)"; }, 300);
    });

    // --- Financial Reports & SePay Paywall Logic ---
    let currentSessionId = localStorage.getItem('dnt_session_id');
    if (!currentSessionId) {
        currentSessionId = 'S' + Math.random().toString(36).substr(2, 9).toUpperCase();
        localStorage.setItem('dnt_session_id', currentSessionId);
    }
    let pollingInterval = null;

    const finBtn = document.getElementById('fin-view-btn');
    if (finBtn) {
        finBtn.addEventListener('click', async () => {
            const ticker = document.getElementById('fin-ticker-input').value.trim();
            if (!ticker) return alert("Vui lòng nhập mã cổ phiếu!");
            
            finBtn.textContent = 'Fetching...';
            try {
                const res = await apiFetch(`/api/financials/${ticker}?session_id=${currentSessionId}`);
                const data = await res.json();
                
                if (data.error) throw new Error(data.error);

                document.getElementById('fin-report-card').style.display = 'block';
                document.getElementById('fin-ticker').textContent = data.ticker;
                document.getElementById('fin-pepb').textContent = `${data.pe.toFixed(2)} | ${data.pb.toFixed(2)}`;
                document.getElementById('fin-industry').textContent = data.industry || '--';
                document.getElementById('fin-marketcap').textContent = data.marketCap ? (data.marketCap).toLocaleString() : '--';
                
                // Fields
                document.getElementById('fin-roe').textContent = `${Number(data.roe).toFixed(2)}% | ${Number(data.roa).toFixed(2)}%`;
                document.getElementById('fin-debt').textContent = `${Number(data.debt_on_equity).toFixed(2)} Lần`;
                document.getElementById('fin-profit').textContent = `${Number(data.profit_growth).toFixed(2)}% (YoY)`;
                
            } catch (err) {
                alert(err.message);
            } finally {
                finBtn.textContent = I18N[currentLang]['btn_fetch_fin'];
            }
        });
    }

    // --- Payment Paywall Logic ---
    const btnDonateSidebar = document.getElementById('btn-donate-sidebar');
    const qrModal = document.getElementById('qr-modal');
    const closeQr = document.getElementById('close-qr-btn');
    const qrImg = document.getElementById('vietqr-img');
    
    const donateSetupView = document.getElementById('donate-setup-view');
    const donateQrView = document.getElementById('donate-qr-view');
    const donateThanksView = document.getElementById('donate-thanks-view');
    
    const btnGenQr = document.getElementById('btn-generate-qr');
    let selectedAmount = 10000;

    if (btnDonateSidebar) {
        btnDonateSidebar.addEventListener('click', () => {
            if (!currentUser) {
                alert(window.getCurrentLang() === 'en' ? 'Please Login first to purchase tokens!' : 'Vui lòng Đăng nhập trước khi nạp Token!');
                openAuthModal();
                return;
            }
            qrModal.style.display = 'flex';
            donateSetupView.style.display = 'block';
            donateQrView.style.display = 'none';
            donateThanksView.style.display = 'none';
            selectedAmount = 10000;
            
            document.querySelectorAll('.donate-amt-btn').forEach(b => b.style.background = 'rgba(255,255,255,0.1)');
            document.querySelector('.donate-amt-btn[data-amt="10000"]').style.background = 'rgba(245,158,11,0.5)';
        });
    }

    document.querySelectorAll('.donate-amt-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            selectedAmount = parseInt(e.currentTarget.getAttribute('data-amt'));
            document.querySelectorAll('.donate-amt-btn').forEach(b => b.style.background = 'rgba(255,255,255,0.1)');
            e.currentTarget.style.background = 'rgba(245,158,11,0.5)';
        });
    });

    if (btnGenQr) {
        btnGenQr.addEventListener('click', async () => {
            btnGenQr.textContent = 'Đang tạo...';
            btnGenQr.disabled = true;
            try {
                const res = await apiFetch('/api/payment/create-intent', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({amount: selectedAmount})
                });
                if (!res.ok) {
                    let errTxt = await res.text();
                    if (errTxt.length > 150) errTxt = errTxt.substring(0, 150) + '...';
                    throw new Error(`HTTP ${res.status}: ${errTxt}`);
                }
                const data = await res.json();
                const code = data.payment_code;
                
                const qrUrl = `https://img.vietqr.io/image/VPB-1001213140604-compact2.jpg?amount=${selectedAmount}&addInfo=DNT%20${code}&accountName=DOAN%20NGUYEN%20TRI`;
                qrImg.src = qrUrl;
                
                donateSetupView.style.display = 'none';
                donateQrView.style.display = 'block';
                
                startPaymentPolling(code);
            } catch (e) {
                alert('Lỗi tạo mã thanh toán: ' + e.message);
            } finally {
                btnGenQr.textContent = 'Tạo mã QR';
                btnGenQr.disabled = false;
            }
        });
    }

    if (closeQr) {
        closeQr.addEventListener('click', () => {
            qrModal.style.display = 'none';
            if(pollingInterval) clearInterval(pollingInterval);
        });
    }

    async function startPaymentPolling(code) {
        if(pollingInterval) clearInterval(pollingInterval);
        
        pollingInterval = setInterval(async () => {
            try {
                const res = await fetch(`/api/payment-status?payment_code=${code}`);
                const data = await res.json();
                
                if(data.paid) {
                    clearInterval(pollingInterval);
                    donateQrView.style.display = 'none';
                    donateThanksView.style.display = 'block';
                    checkUserSession(); // Reload tokens
                }
            } catch(e) {}
        }, 3000);
    }

    // --- AI Radar Screener Auto-Fetch ---
    async function fetchAiRadar() {
        const radarStatus = document.getElementById("ai-radar-status");
        const pillsContainer = document.getElementById("ai-radar-pills");
        if (!radarStatus || !pillsContainer) return;

        try {
            const res = await apiFetch('/api/ai-radar');
            if (!res.ok) throw new Error("Backend error: " + res.status);
            const data = await res.json();
            
            radarStatus.setAttribute('data-i18n', 'ai_radar_updated');
            radarStatus.textContent = I18N[currentLang]['ai_radar_updated'] || "Đã cập nhật (VN30)";
            radarStatus.classList.remove("loading-dots");
            radarStatus.style.color = "#00FFAA";
            pillsContainer.innerHTML = "";

            if (data && data.length > 0) {
                let allTickers = data.map(i => i.ticker).join(", ");
                const allPill = document.createElement("button");
                allPill.className = "radar-pill radar-pill-all";
                
                // Set inner HTML using current language
                const addAllText = I18N[currentLang]['ai_radar_add_all'] || '💯 Thêm TẤT CẢ';
                const suffix = currentLang === 'en' ? 'tickers' : 'mã';
                allPill.innerHTML = `<span data-i18n="ai_radar_add_all">${addAllText}</span> (${data.length} ${suffix})`;
                
                allPill.style.cssText = "background: rgba(0, 255, 170, 0.1); border: 1px solid rgba(0, 255, 170, 0.5); color: #00FFAA; padding: 4px 8px; border-radius: 4px; cursor: pointer; margin-right: 5px; transition: all 0.2s;";
                allPill.onclick = (e) => {
                    e.preventDefault();
                    document.getElementById("tickers-input").value = allTickers;
                    evaluateTickersForManualBCTC();
                };
                pillsContainer.appendChild(allPill);

                // Các mã đơn lẻ
                data.forEach(item => {
                    const pill = document.createElement("button");
                    pill.className = "radar-pill";
                    pill.textContent = `+ ${item.ticker}`;
                    pill.style.cssText = "background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); color: white; padding: 4px 8px; border-radius: 4px; cursor: pointer; transition: all 0.2s;";
                    pill.title = `Score: ${item.score.toFixed(2)}`;
                    
                    pill.onmouseover = () => { pill.style.background = "rgba(255,255,255,0.1)"; };
                    pill.onmouseout = () => { pill.style.background = "rgba(255,255,255,0.05)"; };
                    
                    pill.onclick = (e) => {
                        e.preventDefault();
                        const input = document.getElementById("tickers-input");
                        let currentVals = input.value.split(",").map(s => s.trim()).filter(s => s.length > 0);
                        if (!currentVals.includes(item.ticker)) {
                            currentVals.push(item.ticker);
                            input.value = currentVals.join(", ");
                            evaluateTickersForManualBCTC();
                        }
                    };
                    pillsContainer.appendChild(pill);
                });
            } else {
                radarStatus.setAttribute('data-i18n', 'ai_radar_not_found');
                radarStatus.textContent = I18N[currentLang]['ai_radar_not_found'] || "Không tìm thấy";
            }
        } catch (e) {
            console.error("AI Radar Fetch Error:", e);
            radarStatus.setAttribute('data-i18n', 'ai_radar_err');
            radarStatus.textContent = I18N[currentLang]['ai_radar_err'] || "Lỗi kết nối AI";
            radarStatus.style.color = "var(--neon-alert)";
        }
    }
    
    // Khởi động AI Radar khi tải trang
    fetchAiRadar();

});

