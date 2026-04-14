// --- سِـيــاق: Frontend with Backend Integration ---

const API_BASE_URL = ''; 

let totalGuesses = 0;
let totalHints = 0;
let isGameOver = false;
let guessesArray = [];
let lastWordGuessed = "";
let sessionId = generateSessionId();

function generateSessionId() {
    const stored = localStorage.getItem('siyaq_session_id');
    if (stored) return stored;
    const newId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    localStorage.setItem('siyaq_session_id', newId);
    return newId;
}

function normalizeArabic(text) {
    if (!text) return "";
    return text.replace(/[أإآ]/g, 'ا').replace(/ة/g, 'ه').replace(/ى/g, 'ي').replace(/ئ/g, 'ي').replace(/ؤ/g, 'و').trim();
}

function toArabicDigits(num) {
    const id = ['٠','١','٢','٣','٤','٥','٦','٧','٨','٩'];
    return num.toString().replace(/[0-9]/g, w => id[+w]);
}

function toggleMenu() {
    let menu = document.getElementById("menuDropdown");
    menu.style.display = menu.style.display === "block" ? "none" : "block";
}

function toggleTheme() {
    document.body.classList.toggle("dark-mode");
    toggleMenu();
    localStorage.setItem('siyaq_dark_mode', document.body.classList.contains("dark-mode"));
}

function openHowToPlay() {
    toggleMenu();
    document.getElementById("howToPlayModal").style.display = "flex";
}

function closeModal(id) {
    document.getElementById(id).style.display = "none";
}

function showLoading() {
    document.getElementById("loadingMsg").style.display = "block";
    document.getElementById("guessInput").disabled = true;
}

function hideLoading() {
    document.getElementById("loadingMsg").style.display = "none";
    if (!isGameOver) {
        document.getElementById("guessInput").disabled = false;
        document.getElementById("guessInput").focus();
    }
}

function showError(message) {
    const errorEl = document.getElementById("errorMsg");
    errorEl.textContent = message;
    errorEl.style.display = "block";
    setTimeout(() => { errorEl.style.display = "none"; }, 3000);
}

async function apiRequest(endpoint, method = 'GET', data = null) {
    const options = { method: method, headers: { 'Content-Type': 'application/json' } };
    if (data) options.body = JSON.stringify(data);
    try {
        const response = await fetch(`${API_BASE_URL}/api${endpoint}`, options);
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.error || `HTTP ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

function createRowHtml(item, isHighlighted) {
    let barWidth = (item.rank === 1) ? 100 : (item.rank <= 1000 ? 100 - (item.rank / 10.5) : 8);
    let barColor = "var(--rank-far)";
    if (item.rank <= 300) barColor = "var(--rank-close)";
    else if (item.rank <= 1000) barColor = "var(--rank-mid)";

    let highlightClass = isHighlighted ? "last-guess" : "";
    let hintHtml = item.isHint ? `<span class="hint-tag">(تلميحة)</span>` : '';

    return `
        <div class="result-wrapper ${highlightClass}">
            <div class="progress-bar" style="width: ${barWidth}%; background-color: ${barColor};"></div>
            <div class="result-content">
                <span>${item.word}</span>
                <span style="display: flex; align-items: center; gap: 8px;">${hintHtml} <span>${toArabicDigits(item.rank)}</span></span>
            </div>
        </div>`;
}

function renderResults() {
    let resultsDiv = document.getElementById("results");
    resultsDiv.innerHTML = "";
    if (guessesArray.length === 0) return;

    let sortedGuesses = [...guessesArray].sort((a, b) => a.rank - b.rank);
    if (lastWordGuessed) {
        let lastItem = guessesArray.find(i => i.word === lastWordGuessed);
        if (lastItem) resultsDiv.innerHTML += createRowHtml(lastItem, true);
    }
    sortedGuesses.forEach(item => {
        let isLast = item.word === lastWordGuessed;
        resultsDiv.innerHTML += createRowHtml(item, isLast);
    });
}

async function checkGuess() {
    if (isGameOver) return;
    let input = document.getElementById("guessInput");
    let rawWord = input.value.trim();
    if (!rawWord) return;

    if (!/[\u0600-\u06FF\s]+/.test(rawWord)) {
        showError("يرجى إدخال كلمات عربية فقط");
        input.value = "";
        return;
    }

    let cleanInput = normalizeArabic(rawWord);
    let existingGuess = guessesArray.find(item => normalizeArabic(item.word) === cleanInput);
    
    if (existingGuess) {
        lastWordGuessed = rawWord;
        document.getElementById("duplicateMsg").style.display = "block";
        setTimeout(() => { document.getElementById("duplicateMsg").style.display = "none"; }, 2000);
        renderResults();
        input.value = "";
        return;
    }

    showLoading();
    try {
        const result = await apiRequest('/guess', 'POST', { word: rawWord, session_id: sessionId });
        hideLoading();

        if (result.duplicate) {
            lastWordGuessed = rawWord;
            document.getElementById("duplicateMsg").style.display = "block";
            setTimeout(() => { document.getElementById("duplicateMsg").style.display = "none"; }, 2000);
        } else {
            totalGuesses++;
            document.getElementById("guessCount").innerText = toArabicDigits(totalGuesses);
            
            guessesArray.push({ word: rawWord, rank: result.rank, isHint: false });
            lastWordGuessed = rawWord;
            renderResults();
            
            // التعديل: هنا نرسل الكلمة عشان تنطبع بدون علامات استفهام
            if (result.is_correct || result.won) showEndGame(true, rawWord);
        }
        input.value = "";
    } catch (error) {
        hideLoading();
        showError("حدث خطأ في الاتصال. الكلمة غير موجودة أو السيرفر مشغول.");
    }
}

async function getHint() {
    document.getElementById("menuDropdown").style.display = "none";
    if (isGameOver) return;
    showLoading();
    try {
        const result = await apiRequest('/hint', 'POST', { session_id: sessionId });
        hideLoading();
        if (result.success) {
            totalHints++;
            document.getElementById("hintStatWrapper").style.display = "inline";
            document.getElementById("hintCount").innerText = toArabicDigits(totalHints);
            
            guessesArray.push({ word: result.hint, rank: result.rank, isHint: true });
            lastWordGuessed = result.hint;
            renderResults();
        }
    } catch (error) {
        hideLoading();
        showError("لا يوجد تلميح متاح حالياً");
    }
}

function confirmGiveUp() {
    document.getElementById("menuDropdown").style.display = "none";
    if (!isGameOver) document.getElementById("confirmModal").style.display = "flex";
}

async function giveUp() {
    closeModal("confirmModal");
    showLoading();
    try {
        const result = await apiRequest('/give-up', 'POST', { session_id: sessionId });
        hideLoading();
        if (result.success) showEndGame(false, result.secret_word);
    } catch (error) {
        hideLoading();
        showError("حدث خطأ. حاول مرة أخرى.");
    }
}

function showEndGame(isWin, revealedWord = null) {
    isGameOver = true;
    document.getElementById("guessInput").disabled = true;
    
    let green = 0, orange = 0, red = 0;
    guessesArray.forEach(g => {
        if (g.rank <= 300) green++;
        else if (g.rank <= 1000) orange++;
        else red++;
    });
    
    document.getElementById("greenCount").innerText = toArabicDigits(green);
    document.getElementById("orangeCount").innerText = toArabicDigits(orange);
    document.getElementById("redCount").innerText = toArabicDigits(red);
    
    document.getElementById("revealedWord").innerText = revealedWord || "???";
    
    let titleEl = document.getElementById("endTitle");
    let subtextEl = document.getElementById("endSubtext");
    let surrenderHeader = document.getElementById("surrenderHeader");
    
    if (isWin) {
        surrenderHeader.style.display = "none";
        titleEl.innerText = "أحسنت صنعاً!";
        subtextEl.innerText = `وجدت الكلمة المجهولة في ${toArabicDigits(totalGuesses)} تخمينات و ${toArabicDigits(totalHints)} تلميحات.`;
    } else {
        surrenderHeader.style.display = "block";
        titleEl.innerText = "حظاً أوفر المرة القادمة!";
        subtextEl.innerText = `استسلمت بعد ${toArabicDigits(totalGuesses)} تخمينات و ${toArabicDigits(totalHints)} تلميحات.`;
    }
    
    document.getElementById("gameOverBox").style.display = "block";
    document.getElementById("closestWordsSection").style.display = "block"; // نظهر زر الكلمات القريبة
    document.getElementById("inputArea").style.display = "none";
    document.getElementById("gameOverStatsPlaceholder").appendChild(document.getElementById("statsContainer"));
}

async function resetGame() {
    showLoading();
    try {
        await apiRequest('/reset', 'POST', { session_id: sessionId });
        totalGuesses = 0; totalHints = 0; isGameOver = false; guessesArray = []; lastWordGuessed = "";
        
        document.getElementById("guessCount").innerText = "٠";
        document.getElementById("hintCount").innerText = "٠";
        document.getElementById("hintStatWrapper").style.display = "none";
        document.getElementById("results").innerHTML = "";
        document.getElementById("guessInput").disabled = false;
        document.getElementById("guessInput").value = "";
        
        document.getElementById("gameOverBox").style.display = "none";
        document.getElementById("closestWordsSection").style.display = "none";
        document.getElementById("closestWordsContainer").style.display = "none";
        
        document.getElementById("inputArea").style.display = "block";
        document.getElementById("normalActionRow").prepend(document.getElementById("statsContainer"));
        
        hideLoading();
        document.getElementById("guessInput").focus();
    } catch (error) {
        hideLoading();
        showError("حدث خطأ في إعادة تعيين اللعبة");
    }
}

// التعديل: برمجة زر الكلمات القريبة
async function toggleClosestWords() {
    const container = document.getElementById("closestWordsContainer");
    const listDiv = document.getElementById("closestWordsList");
    
    if (container.style.display === "block") {
        container.style.display = "none";
        return;
    }
    
    container.style.display = "block";
    listDiv.innerHTML = "<div style='text-align:center; padding: 10px;'>جاري تحميل الكلمات... ⏳</div>";
    
    try {
        const result = await apiRequest('/closest', 'POST', { session_id: sessionId });
        if (result.success && result.words) {
            listDiv.innerHTML = "";
            result.words.forEach(item => {
                let barWidth = (item.rank === 1) ? 100 : (item.rank <= 1000 ? 100 - (item.rank / 10.5) : 8);
                let barColor = "var(--rank-far)";
                if (item.rank <= 300) barColor = "var(--rank-close)";
                else if (item.rank <= 1000) barColor = "var(--rank-mid)";

                listDiv.innerHTML += `
                    <div class="result-wrapper" style="margin-bottom: 5px;">
                        <div class="progress-bar" style="width: ${barWidth}%; background-color: ${barColor};"></div>
                        <div class="result-content">
                            <span>${item.word}</span>
                            <span>${toArabicDigits(item.rank)}</span>
                        </div>
                    </div>`;
            });
        } else {
            listDiv.innerHTML = "<div style='text-align:center;'>تعذر تحميل الكلمات.</div>";
        }
    } catch (e) {
        listDiv.innerHTML = "<div style='text-align:center;'>حدث خطأ! تأكد من اتصالك.</div>";
    }
}

function shareResult() {
    let green = document.getElementById("greenCount").innerText;
    let orange = document.getElementById("orangeCount").innerText;
    let red = document.getElementById("redCount").innerText;
    
    let text = `لعبت سِـيــاق وجبت الكلمة بـ ${toArabicDigits(totalGuesses)} تخمين! 🎉\n`;
    text += `🟢 ${green}  🟠 ${orange}  🔴 ${red}\n`;
    text += `\n#سياق #Siyaq\nhttps://siyaq-game.onrender.com`;
    
    navigator.clipboard.writeText(text).then(() => { alert("تم نسخ النتيجة لمشاركتها! 📋"); })
    .catch(() => { alert("تعذر نسخ النتيجة"); });
}

// التعديل: برمجة العداد التنازلي لتوقيت السعودية
function startCountdown() {
    setInterval(() => {
        const now = new Date();
        const ksaString = now.toLocaleString("en-US", {timeZone: "Asia/Riyadh"});
        const ksaTime = new Date(ksaString);
        
        const midnight = new Date(ksaTime);
        midnight.setHours(24, 0, 0, 0);
        
        const diff = midnight - ksaTime;
        const h = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const m = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
        const s = Math.floor((diff % (1000 * 60)) / 1000);
        
        document.getElementById("countdownTimer").innerText = 
            `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
    }, 1000);
}

document.getElementById("guessInput").addEventListener("keypress", (e) => {
    if (e.key === "Enter") checkGuess();
});

document.addEventListener('click', (e) => {
    const menu = document.getElementById("menuDropdown");
    const menuBtn = document.getElementById("menuBtn");
    if (menu.style.display === "block" && !menu.contains(e.target) && e.target !== menuBtn) {
        menu.style.display = "none";
    }
});

document.addEventListener('DOMContentLoaded', async () => {
    const savedDarkMode = localStorage.getItem('siyaq_dark_mode');
    if (savedDarkMode === 'false') document.body.classList.remove('dark-mode');
    
    startCountdown(); // تشغيل العداد أول ما تفتح الصفحة
    
    try {
        await apiRequest('/health');
    } catch (error) {
        showError("تعذر الاتصال بالخادم. السيرفر نايم، جاري إيقاظه...");
    }
    document.getElementById("guessInput").focus();
});
