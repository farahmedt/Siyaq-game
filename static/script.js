// --- سِـيــاق: Frontend with Backend Integration ---

// API Configuration
const API_BASE_URL = ''; // Empty for same-origin, or set to your Replit URL

// Game State
let totalGuesses = 0;
let totalHints = 0;
let isGameOver = false;
let guessesArray = [];
let lastWordGuessed = "";
let sessionId = generateSessionId();

// Generate unique session ID
function generateSessionId() {
    const stored = localStorage.getItem('siyaq_session_id');
    if (stored) return stored;
    
    const newId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    localStorage.setItem('siyaq_session_id', newId);
    return newId;
}

// --- Arabic Normalization ---
function normalizeArabic(text) {
    if (!text) return "";
    return text
        .replace(/[أإآ]/g, 'ا')
        .replace(/ة/g, 'ه')
        .replace(/ى/g, 'ي')
        .replace(/ئ/g, 'ي')
        .replace(/ؤ/g, 'و')
        .trim();
}

// --- Number Formatting ---
function toArabicDigits(num) {
    const id = ['٠','١','٢','٣','٤','٥','٦','٧','٨','٩'];
    return num.toString().replace(/[0-9]/g, w => id[+w]);
}

// --- UI Functions ---
function toggleMenu() {
    let menu = document.getElementById("menuDropdown");
    menu.style.display = menu.style.display === "block" ? "none" : "block";
}

function toggleTheme() {
    document.body.classList.toggle("dark-mode");
    toggleMenu();
    // Save preference
    const isDark = document.body.classList.contains("dark-mode");
    localStorage.setItem('siyaq_dark_mode', isDark);
}

function openHowToPlay() {
    toggleMenu();
    document.getElementById("howToPlayModal").style.display = "flex";
}

function closeModal(id) {
    document.getElementById(id).style.display = "none";
}

// --- Loading & Error States ---
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
    setTimeout(() => {
        errorEl.style.display = "none";
    }, 3000);
}

// --- API Functions ---
async function apiRequest(endpoint, method = 'GET', data = null) {
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json',
        }
    };
    
    if (data) {
        options.body = JSON.stringify(data);
    }
    
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

// --- Game Logic ---
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

    // Sort by rank
    let sortedGuesses = [...guessesArray].sort((a, b) => a.rank - b.rank);

    // Show last guess first (highlighted)
    if (lastWordGuessed) {
        let lastItem = guessesArray.find(i => i.word === lastWordGuessed);
        if (lastItem) {
            resultsDiv.innerHTML += createRowHtml(lastItem, true);
        }
    }

    // Show all guesses
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

    // Validate Arabic input
    if (!/[\u0600-\u06FF\s]+/.test(rawWord)) {
        showError("يرجى إدخال كلمات عربية فقط");
        input.value = "";
        return;
    }

    // Check for duplicates locally first
    let cleanInput = normalizeArabic(rawWord);
    let existingGuess = guessesArray.find(item => normalizeArabic(item.word) === cleanInput);
    
    if (existingGuess) {
        lastWordGuessed = rawWord;
        document.getElementById("duplicateMsg").style.display = "block";
        setTimeout(() => { 
            document.getElementById("duplicateMsg").style.display = "none"; 
        }, 2000);
        renderResults();
        input.value = "";
        return;
    }

    showLoading();

    try {
        const result = await apiRequest('/guess', 'POST', {
            word: rawWord,
            session_id: sessionId
        });

        hideLoading();

        if (result.duplicate) {
            lastWordGuessed = rawWord;
            document.getElementById("duplicateMsg").style.display = "block";
            setTimeout(() => { 
                document.getElementById("duplicateMsg").style.display = "none"; 
            }, 2000);
        } else {
            totalGuesses++;
            document.getElementById("guessCount").innerText = toArabicDigits(totalGuesses);
            
            let guessData = {
                word: rawWord,
                rank: result.rank,
                isHint: false
            };
            
            guessesArray.push(guessData);
            lastWordGuessed = rawWord;
            
            renderResults();
            
            if (result.is_correct || result.won) {
                showEndGame(true);
            }
        }
        
        input.value = "";
        
    } catch (error) {
        hideLoading();
        showError("حدث خطأ في الاتصال. حاول مرة أخرى.");
        console.error('Guess error:', error);
    }
}

async function getHint() {
    document.getElementById("menuDropdown").style.display = "none";
    if (isGameOver) return;

    showLoading();

    try {
        const result = await apiRequest('/hint', 'POST', {
            session_id: sessionId
        });

        hideLoading();

        if (result.success) {
            totalHints++;
            document.getElementById("hintStatWrapper").style.display = "inline";
            document.getElementById("hintCount").innerText = toArabicDigits(totalHints);
            
            let hintData = {
                word: result.hint,
                rank: result.rank,
                isHint: true
            };
            
            guessesArray.push(hintData);
            lastWordGuessed = result.hint;
            renderResults();
        }
        
    } catch (error) {
        hideLoading();
        showError("لا يوجد تلميح متاح حالياً");
        console.error('Hint error:', error);
    }
}

function confirmGiveUp() {
    document.getElementById("menuDropdown").style.display = "none";
    if (!isGameOver) {
        document.getElementById("confirmModal").style.display = "flex";
    }
}

async function giveUp() {
    closeModal("confirmModal");
    
    showLoading();
    
    try {
        const result = await apiRequest('/give-up', 'POST', {
            session_id: sessionId
        });

        hideLoading();

        if (result.success) {
            showEndGame(false, result.secret_word);
        }
        
    } catch (error) {
        hideLoading();
        showError("حدث خطأ. حاول مرة أخرى.");
        console.error('Give up error:', error);
    }
}

function showEndGame(isWin, revealedWord = null) {
    isGameOver = true;
    document.getElementById("guessInput").disabled = true;
    
    // Calculate color counts
    let green = 0, orange = 0, red = 0;
    guessesArray.forEach(g => {
        if (g.rank <= 300) green++;
        else if (g.rank <= 1000) orange++;
        else red++;
    });
    
    document.getElementById("greenCount").innerText = toArabicDigits(green);
    document.getElementById("orangeCount").innerText = toArabicDigits(orange);
    document.getElementById("redCount").innerText = toArabicDigits(red);
    
    // Get the secret word (from parameter or need to fetch)
    const secretWord = revealedWord || "???";
    document.getElementById("revealedWord").innerText = secretWord;
    
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
    document.getElementById("inputArea").style.display = "none";
    document.getElementById("gameOverStatsPlaceholder").appendChild(document.getElementById("statsContainer"));
}

async function resetGame() {
    showLoading();
    
    try {
        await apiRequest('/reset', 'POST', {
            session_id: sessionId
        });

        // Reset local state
        totalGuesses = 0;
        totalHints = 0;
        isGameOver = false;
        guessesArray = [];
        lastWordGuessed = "";
        
        // Reset UI
        document.getElementById("guessCount").innerText = "٠";
        document.getElementById("hintCount").innerText = "٠";
        document.getElementById("hintStatWrapper").style.display = "none";
        document.getElementById("results").innerHTML = "";
        document.getElementById("guessInput").disabled = false;
        document.getElementById("guessInput").value = "";
        document.getElementById("gameOverBox").style.display = "none";
        document.getElementById("inputArea").style.display = "block";
        document.getElementById("normalActionRow").prepend(document.getElementById("statsContainer"));
        
        hideLoading();
        document.getElementById("guessInput").focus();
        
    } catch (error) {
        hideLoading();
        showError("حدث خطأ في إعادة تعيين اللعبة");
        console.error('Reset error:', error);
    }
}

function shareResult() {
    let green = document.getElementById("greenCount").innerText;
    let orange = document.getElementById("orangeCount").innerText;
    let red = document.getElementById("redCount").innerText;
    
    let text = `لعبت سِـيــاق وجبت الكلمة بـ ${toArabicDigits(totalGuesses)} تخمين! 🎉\n`;
    text += `🟢 ${green}  🟠 ${orange}  🔴 ${red}\n`;
    text += `\n#سياق #Siyaq`;
    
    navigator.clipboard.writeText(text).then(() => {
        alert("تم نسخ النتيجة لمشاركتها! 📋");
    }).catch(() => {
        alert("تعذر نسخ النتيجة");
    });
}

// --- Event Listeners ---
document.getElementById("guessInput").addEventListener("keypress", (e) => {
    if (e.key === "Enter") checkGuess();
});

// Close menu when clicking outside
document.addEventListener('click', (e) => {
    const menu = document.getElementById("menuDropdown");
    const menuBtn = document.getElementById("menuBtn");
    
    if (menu.style.display === "block" && 
        !menu.contains(e.target) && 
        e.target !== menuBtn) {
        menu.style.display = "none";
    }
});

// --- Initialization ---
document.addEventListener('DOMContentLoaded', async () => {
    // Load theme preference
    const savedDarkMode = localStorage.getItem('siyaq_dark_mode');
    if (savedDarkMode === 'false') {
        document.body.classList.remove('dark-mode');
    }
    
    // Check server health
    try {
        const health = await apiRequest('/health');
        console.log('✅ Server connected:', health);
    } catch (error) {
        console.warn('⚠️ Server connection issue:', error);
        showError("تعذر الاتصال بالخادم. تحقق من اتصالك.");
    }
    
    // Focus input
    document.getElementById("guessInput").focus();
});

// Prevent losing focus on input (optional enhancement)
document.addEventListener('click', (e) => {
    if (!isGameOver && e.target.tagName !== 'INPUT' && e.target.tagName !== 'BUTTON') {
        // Don't auto-focus to avoid annoying mobile users
    }
});
