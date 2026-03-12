/* LANG_NAMES는 index.html에서 인라인 스크립트로 주입됨 */
let lastResult = { translation: '', rough: '', refined: false };
let historyData = [];
let selectedFile = null;
let realtimeDebounceTimer = null;
let realtimeLastResult = '';
let conversationHistory = [];

function getTheme() {
    return document.documentElement.getAttribute('data-theme') || 'dark';
}

function setTheme(t) {
    document.documentElement.setAttribute('data-theme', t);
    document.getElementById('themeBtn').textContent = t === 'dark' ? '라이트 모드' : '다크 모드';
    localStorage.setItem('theme', t);
}

function getGlossary() {
    const g = {};
    document.querySelectorAll('.glossary-item').forEach(row => {
        const [a, b] = row.querySelectorAll('input');
        if (a?.value?.trim() && b?.value?.trim()) {
            g[a.value.trim()] = b.value.trim();
        }
    });
    return g;
}

function addHistory(orig, trans, source, target) {
    let h = JSON.parse(localStorage.getItem('transHistory') || '[]');
    h.unshift({ orig, trans, source, target, ts: Date.now() });
    h = h.slice(0, 50);
    localStorage.setItem('transHistory', JSON.stringify(h));
    renderHistory();
}

function renderHistory() {
    historyData = JSON.parse(localStorage.getItem('transHistory') || '[]');
    const el = document.getElementById('historyList');
    el.innerHTML = historyData.length
        ? historyData
              .map(
                  (x, i) =>
                      `<div class="history-item" data-idx="${i}">${x.orig.slice(0, 50)}${x.orig.length > 50 ? '...' : ''}</div>`
              )
              .join('')
        : '<div class="history-item" style="color:var(--text-muted)">히스토리 없음</div>';
    el.querySelectorAll('.history-item[data-idx]').forEach(i => {
        i.onclick = () => {
            document.getElementById('inputText').value = historyData[parseInt(i.dataset.idx)].orig;
        };
    });
}

function init() {
    document.getElementById('themeBtn').onclick = () =>
        setTheme(getTheme() === 'dark' ? 'light' : 'dark');
    if (localStorage.getItem('theme') === 'light') setTheme('light');

    document.querySelectorAll('.tab').forEach(t => {
        t.onclick = () => {
            document.querySelectorAll('.tab').forEach(x => x.classList.remove('active'));
            document.querySelectorAll('.panel').forEach(x => x.classList.remove('active'));
            t.classList.add('active');
            document.getElementById('panel-' + t.dataset.tab).classList.add('active');
        };
    });

    document.getElementById('clearHistory').onclick = () => {
        localStorage.removeItem('transHistory');
        renderHistory();
    };
    renderHistory();

    document.getElementById('addGlossary').onclick = () => {
        const div = document.createElement('div');
        div.className = 'glossary-item';
        div.innerHTML =
            '<input placeholder="원문"> <input placeholder="번역"> <button class="btn btn-outline btn-sm">삭제</button>';
        div.querySelector('button').onclick = () => div.remove();
        document.getElementById('glossaryList').appendChild(div);
    };

    async function translate() {
        const text = document.getElementById('inputText').value.trim();
        if (!text) {
            document.getElementById('errorMsg').textContent = '텍스트를 입력하세요.';
            document.getElementById('errorMsg').style.display = 'block';
            return;
        }
        document.getElementById('errorMsg').style.display = 'none';
        document.getElementById('translateBtn').disabled = true;
        document.getElementById('translateBtn').innerHTML = '<span class="loading"></span>번역 중...';
        try {
            const res = await fetch('/api/translate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    text,
                    source: document.getElementById('sourceLang').value,
                    target: document.getElementById('targetLang').value,
                    use_llm: document.getElementById('useLlm').checked,
                    glossary: Object.keys(getGlossary()).length ? getGlossary() : null,
                }),
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || data.error || '번역 실패');
            lastResult = data;
            document.getElementById('result').textContent = data.translation;
            document.getElementById('result').classList.remove('empty');
            document.getElementById('basicResultBtns').style.display = 'inline-flex';
            document.getElementById('compareTabs').style.display = 'flex';
            document.getElementById('badgeRefined').style.display = data.refined ? 'inline-block' : 'none';
            document.getElementById('badgeRough').style.display = data.refined ? 'none' : 'inline-block';
            addHistory(
                text,
                data.translation,
                document.getElementById('sourceLang').value,
                document.getElementById('targetLang').value
            );
        } catch (e) {
            document.getElementById('errorMsg').textContent = e.message;
            document.getElementById('errorMsg').style.display = 'block';
        } finally {
            document.getElementById('translateBtn').disabled = false;
            document.getElementById('translateBtn').textContent = '번역하기';
        }
    }

    document.getElementById('translateBtn').onclick = translate;
    document.getElementById('inputText').onkeydown = e => {
        if (e.ctrlKey && e.key === 'Enter') translate();
    };

    document.getElementById('ttsBtn').onclick = () => {
        speakText(document.getElementById('result').textContent, document.getElementById('targetLang').value);
    };

    document.getElementById('copyBtn').onclick = () => {
        navigator.clipboard.writeText(document.getElementById('result').textContent);
        document.getElementById('copyBtn').textContent = '복사됨!';
        setTimeout(() => (document.getElementById('copyBtn').textContent = '복사'), 1500);
    };

    document.getElementById('compareTabs').querySelectorAll('button').forEach(b => {
        b.onclick = () => {
            document
                .getElementById('compareTabs')
                .querySelectorAll('button')
                .forEach(x => x.classList.remove('active'));
            b.classList.add('active');
            const v = b.dataset.view;
            const r = document.getElementById('result');
            if (v === 'final') r.textContent = lastResult.translation;
            else if (v === 'rough') r.textContent = lastResult.rough;
            else r.textContent = lastResult.refined ? lastResult.translation : lastResult.rough;
        };
    });

    document.getElementById('batchTranslateBtn').onclick = async () => {
        const lines = document
            .getElementById('batchInput')
            .value.split('\n')
            .map(s => s.trim())
            .filter(Boolean);
        if (!lines.length) return;
        document.getElementById('batchTranslateBtn').disabled = true;
        document.getElementById('batchTranslateBtn').innerHTML =
            '<span class="loading"></span>번역 중...';
        try {
            const res = await fetch('/api/translate/batch', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    texts: lines,
                    source: document.getElementById('batchSource').value,
                    target: document.getElementById('batchTarget').value,
                    use_llm: document.getElementById('batchUseLlm').checked,
                }),
            });
            const data = await res.json();
            const batchTarget = document.getElementById('batchTarget').value;
            document.getElementById('batchResult').innerHTML = data.results
                .map(
                    (x) =>
                        `<div class="batch-item"><div class="orig">${escapeHtml(x.original)}</div><div class="trans">${escapeHtml(x.translation)}</div><div class="item-actions"><button class="tts-btn" data-text="${escapeHtml(x.translation)}" data-lang="${batchTarget}">🔊 듣기</button></div></div>`
                )
                .join('');
            document.getElementById('batchResult').querySelectorAll('.tts-btn').forEach(btn => {
                btn.onclick = () => speakText(btn.dataset.text || '', btn.dataset.lang);
            });
        } catch (e) {
            document.getElementById('batchResult').innerHTML =
                '<p class="error-msg">' + escapeHtml(e.message) + '</p>';
        } finally {
            document.getElementById('batchTranslateBtn').disabled = false;
            document.getElementById('batchTranslateBtn').textContent = '배치 번역';
        }
    };

    document.getElementById('fileDrop').onclick = () => document.getElementById('fileInput').click();
    document.getElementById('fileDrop').ondragover = e => {
        e.preventDefault();
        document.getElementById('fileDrop').classList.add('dragover');
    };
    document.getElementById('fileDrop').ondragleave = () => {
        document.getElementById('fileDrop').classList.remove('dragover');
    };
    document.getElementById('fileDrop').ondrop = e => {
        e.preventDefault();
        document.getElementById('fileDrop').classList.remove('dragover');
        if (e.dataTransfer.files.length) {
            selectedFile = e.dataTransfer.files[0];
            document.getElementById('fileTranslateBtn').disabled = false;
        }
    };
    document.getElementById('fileInput').onchange = e => {
        selectedFile = e.target.files?.[0];
        document.getElementById('fileTranslateBtn').disabled = !selectedFile;
    };

    document.getElementById('fileTranslateBtn').onclick = async () => {
        if (!selectedFile) return;
        const fd = new FormData();
        fd.append('file', selectedFile);
        fd.append('source', document.getElementById('fileSource').value);
        fd.append('target', document.getElementById('fileTarget').value);
        fd.append('use_llm', document.getElementById('fileUseLlm').checked);
        document.getElementById('fileTranslateBtn').disabled = true;
        document.getElementById('fileTranslateBtn').innerHTML =
            '<span class="loading"></span>번역 중...';
        try {
            const res = await fetch('/api/translate/file', { method: 'POST', body: fd });
            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || '실패');
            const fileTarget = document.getElementById('fileTarget').value;
            document.getElementById('fileResult').innerHTML = data.results
                .map(
                    (x) =>
                        `<div class="batch-item"><div class="orig">${escapeHtml(x.original)}</div><div class="trans">${escapeHtml(x.translation)}</div><div class="item-actions"><button class="tts-btn" data-text="${escapeHtml(x.translation)}" data-lang="${fileTarget}">🔊 듣기</button></div></div>`
                )
                .join('');
            document.getElementById('fileResult').querySelectorAll('.tts-btn').forEach(btn => {
                btn.onclick = () => speakText(btn.dataset.text || '', btn.dataset.lang);
            });
        } catch (e) {
            document.getElementById('fileResult').innerHTML =
                '<p class="error-msg">' + escapeHtml(e.message) + '</p>';
        } finally {
            document.getElementById('fileTranslateBtn').disabled = false;
            document.getElementById('fileTranslateBtn').textContent = '파일 번역';
        }
    };

    document.getElementById('emailTranslateBtn').onclick = async () => {
        const raw = document.getElementById('emailInput').value.trim();
        if (!raw) return;

        const parsed = parseEmail(raw);
        document.getElementById('emailTranslateBtn').disabled = true;
        document.getElementById('emailTranslateBtn').innerHTML =
            '<span class="loading"></span>번역 중...';

        try {
            const res = await fetch('/api/translate/email', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    from_addr: parsed.from,
                    subject: parsed.subject,
                    body: parsed.body,
                    source: document.getElementById('emailSource').value,
                    target: document.getElementById('emailTarget').value,
                    use_llm: document.getElementById('emailUseLlm').checked,
                }),
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || '번역 실패');

            const subjectDisplay = data.subject_translated || (parsed.subject && !data.subject_translated ? parsed.subject : '');
            const html = [
                data.from ? `발신: ${escapeHtml(data.from)}` : '',
                subjectDisplay ? `제목: ${escapeHtml(subjectDisplay)}` : '',
                '',
                escapeHtml(data.body_translated),
            ]
                .filter(Boolean)
                .join('\n');

            document.getElementById('emailResult').innerHTML = html;
            document.getElementById('emailResult').classList.remove('email-placeholder');
            document.getElementById('emailResultBtns').style.display = 'inline-flex';
            const copySubject = data.subject_translated || (parsed.subject ? parsed.subject : '');
            document.getElementById('emailCopyBtn').dataset.copyText =
                [data.from ? `발신: ${data.from}` : '', copySubject ? `제목: ${copySubject}` : '', '', data.body_translated].filter(Boolean).join('\n');
        } catch (e) {
            document.getElementById('emailResult').innerHTML =
                '<p class="error-msg">' + escapeHtml(e.message) + '</p>';
        } finally {
            document.getElementById('emailTranslateBtn').disabled = false;
            document.getElementById('emailTranslateBtn').textContent = '메일 번역';
        }
    };

    document.getElementById('emailTtsBtn').onclick = () => {
        const bodyText = document.getElementById('emailCopyBtn').dataset.copyText || document.getElementById('emailResult').innerText;
        speakText(bodyText, document.getElementById('emailTarget').value);
    };

    document.getElementById('emailCopyBtn').onclick = () => {
        const text = document.getElementById('emailCopyBtn').dataset.copyText || document.getElementById('emailResult').innerText;
        navigator.clipboard.writeText(text);
        document.getElementById('emailCopyBtn').textContent = '복사됨!';
        setTimeout(() => (document.getElementById('emailCopyBtn').textContent = '전체 복사'), 1500);
    };

    document.querySelectorAll('.mode-btn').forEach(btn => {
        btn.onclick = () => {
            document.querySelectorAll('.mode-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            const mode = btn.dataset.mode;
            document.getElementById('realtimeTypingArea').style.display = mode === 'typing' ? 'block' : 'none';
            document.getElementById('realtimeVoiceArea').style.display = mode === 'voice' ? 'block' : 'none';
            document.getElementById('realtimeConversationArea').style.display = mode === 'conversation' ? 'block' : 'none';
            document.getElementById('meetingNotesCard').style.display = mode === 'conversation' ? 'block' : 'none';
            if (mode === 'conversation') renderMeetingLog();
            clearTimeout(realtimeDebounceTimer);
            if (mode === 'voice' || mode === 'conversation') speechSynthesis?.cancel();
        };
    });

    document.getElementById('realtimeInput').oninput = () => {
        clearTimeout(realtimeDebounceTimer);
        const text = document.getElementById('realtimeInput').value.trim();
        if (!text) {
            document.getElementById('realtimeResult').textContent = '결과가 여기 표시됩니다.';
            document.getElementById('realtimeResult').classList.add('empty');
            document.getElementById('realtimeResultBtns').style.display = 'none';
            return;
        }
        realtimeDebounceTimer = setTimeout(async () => {
            try {
                const res = await fetch('/api/translate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        text,
                        source: document.getElementById('realtimeSource').value,
                        target: document.getElementById('realtimeTarget').value,
                        use_llm: document.getElementById('realtimeUseLlm').checked,
                    }),
                });
                const data = await res.json();
                if (!res.ok) throw new Error(data.detail || '번역 실패');
                realtimeLastResult = data.translation;
                document.getElementById('realtimeResult').textContent = data.translation;
                document.getElementById('realtimeResult').classList.remove('empty');
                document.getElementById('realtimeResultBtns').style.display = 'inline-flex';
            } catch (e) {
                document.getElementById('realtimeResult').textContent = '오류: ' + e.message;
                document.getElementById('realtimeResult').classList.remove('empty');
            }
        }, 800);
    };

    document.getElementById('realtimeTtsBtn').onclick = () => {
        speakText(document.getElementById('realtimeResult').textContent, document.getElementById('realtimeTarget').value);
    };

    document.getElementById('realtimeSpeakBtn').onclick = async () => {
        if (!('SpeechRecognition' in window) && !('webkitSpeechRecognition' in window)) {
            alert('이 브라우저는 음성 인식을 지원하지 않습니다. Chrome을 사용해 주세요.');
            return;
        }
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const rec = new SpeechRecognition();
        rec.lang = STT_LANG_MAP[document.getElementById('realtimeSource').value] || 'ko-KR';
        rec.continuous = false;
        rec.interimResults = false;
        const btn = document.getElementById('realtimeSpeakBtn');
        const hint = document.getElementById('voiceHint');
        btn.classList.add('listening');
        btn.textContent = '🎤 듣는 중...';
        hint.textContent = '말씀하세요...';
        rec.onresult = async (e) => {
            const transcript = e.results[e.results.length - 1][0].transcript;
            btn.classList.remove('listening');
            btn.textContent = '🎤 말하기';
            hint.textContent = '인식: ' + transcript;
            if (!transcript.trim()) return;
            try {
                const res = await fetch('/api/translate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        text: transcript,
                        source: document.getElementById('realtimeSource').value,
                        target: document.getElementById('realtimeTarget').value,
                        use_llm: document.getElementById('realtimeUseLlm').checked,
                    }),
                });
                const data = await res.json();
                if (!res.ok) throw new Error(data.detail || '번역 실패');
                realtimeLastResult = data.translation;
                document.getElementById('realtimeResult').textContent = data.translation;
                document.getElementById('realtimeResult').classList.remove('empty');
                document.getElementById('realtimeResultBtns').style.display = 'inline-flex';
                speakText(data.translation, document.getElementById('realtimeTarget').value);
            } catch (err) {
                document.getElementById('realtimeResult').textContent = '오류: ' + err.message;
                hint.textContent = '오류가 발생했습니다.';
            }
        };
        rec.onerror = (e) => {
            btn.classList.remove('listening');
            btn.textContent = '🎤 말하기';
            const errMap = {
                'no-speech': '음성이 감지되지 않았습니다. 마이크에 가까이서 다시 말해 주세요.',
                'audio-capture': '마이크를 찾을 수 없습니다. 마이크 연결을 확인해 주세요.',
                'not-allowed': '마이크 접근이 거부되었습니다. 브라우저 설정에서 마이크를 허용해 주세요.',
                'network': '네트워크 오류입니다. 인터넷 연결을 확인해 주세요.',
                'aborted': '음성 인식이 중단되었습니다.',
                'language-not-supported': '선택한 언어는 음성 인식을 지원하지 않습니다.',
                'service-not-allowed': '이 페이지에서는 음성 인식을 사용할 수 없습니다. (HTTPS 필요)',
                'bad-grammar': '인식에 실패했습니다. 다시 말해 주세요.',
            };
            hint.textContent = errMap[e.error] || '오류가 발생했습니다. 다시 시도해 주세요.';
        };
        rec.onend = () => {
            btn.classList.remove('listening');
            if (btn.textContent === '🎤 듣는 중...') btn.textContent = '🎤 말하기';
        };
        rec.start();
    };

    function getSpeakerLabel(speaker) {
        if (speaker === '나') {
            const n = document.getElementById('speakerMe').value.trim();
            return n || '나';
        }
        if (speaker === '상대') {
            const n = document.getElementById('speakerOther').value.trim();
            return n || '상대';
        }
        return speaker || '화자';
    }

    function runConversationTurn(speaker, speakLang, translateToLang) {
        if (!('SpeechRecognition' in window) && !('webkitSpeechRecognition' in window)) {
            alert('이 브라우저는 음성 인식을 지원하지 않습니다. Chrome을 사용해 주세요.');
            return;
        }
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const rec = new SpeechRecognition();
        rec.lang = STT_LANG_MAP[speakLang] || 'ko-KR';
        rec.continuous = false;
        rec.interimResults = false;
        const hint = document.getElementById('convHint');
        hint.textContent = speaker === '나' ? '말씀하세요...' : speaker === '상대' ? '상대방이 말하세요...' : '말씀하세요...';
        rec.onresult = async (e) => {
            const transcript = e.results[e.results.length - 1][0].transcript;
            if (!transcript.trim()) { hint.textContent = '말할 사람에 맞는 버튼을 누른 후 말하세요.'; return; }
            hint.textContent = '번역 중...';
            try {
                const res = await fetch('/api/translate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        text: transcript,
                        source: speakLang,
                        target: translateToLang,
                        use_llm: document.getElementById('realtimeUseLlm').checked,
                    }),
                });
                const data = await res.json();
                if (!res.ok) throw new Error(data.detail || '번역 실패');
                conversationHistory.push({
                    speaker: getSpeakerLabel(speaker),
                    original: transcript,
                    translation: data.translation,
                    time: new Date().toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' }),
                });
                renderMeetingLog();
                document.getElementById('realtimeResult').textContent = data.translation;
                document.getElementById('realtimeResult').classList.remove('empty');
                document.getElementById('realtimeResultBtns').style.display = 'inline-flex';
                speakText(data.translation, translateToLang);
                hint.textContent = '말할 사람에 맞는 버튼을 누른 후 말하세요.';
            } catch (err) {
                hint.textContent = '오류: ' + err.message;
            }
        };
        rec.onerror = (e) => {
            const errMap = {
                'no-speech': '음성이 감지되지 않았습니다. 다시 말해 주세요.',
                'audio-capture': '마이크를 확인해 주세요.',
                'not-allowed': '마이크 접근을 허용해 주세요.',
                'network': '인터넷 연결을 확인해 주세요.',
                'aborted': '인식이 중단되었습니다.',
                'language-not-supported': '해당 언어를 지원하지 않습니다.',
                'service-not-allowed': 'HTTPS에서 사용해 주세요.',
            };
            hint.textContent = errMap[e.error] || '오류가 발생했습니다.';
        };
        rec.onend = () => {
            if (hint.textContent.includes('말씀하세요') || hint.textContent.includes('상대방이')) {
                hint.textContent = '말할 사람에 맞는 버튼을 누른 후 말하세요.';
            }
        };
        rec.start();
    }

    function renderMeetingLog() {
        const LANG_NAMES = window.LANG_NAMES || {};
        const sourceName = LANG_NAMES[document.getElementById('realtimeSource').value] || '';
        const targetName = LANG_NAMES[document.getElementById('realtimeTarget').value] || '';
        const logEl = document.getElementById('meetingLog');
        if (conversationHistory.length === 0) {
            logEl.innerHTML = '<p style="color:var(--text-muted)">대화 내용이 여기에 표시됩니다.</p>';
            return;
        }
        logEl.innerHTML = conversationHistory.map(
            (x, i) =>
                `<div class="meeting-item" data-idx="${i}"><span class="speaker editable" title="클릭하여 화자 수정">[${x.time}] ${escapeHtml(x.speaker)}</span><div class="original">${escapeHtml(x.original)}</div><div class="translation">→ ${escapeHtml(x.translation)}</div></div>`
        ).join('');
        logEl.querySelectorAll('.speaker.editable').forEach(el => {
            el.onclick = () => {
                const idx = parseInt(el.closest('.meeting-item').dataset.idx);
                const newName = prompt('화자 이름:', conversationHistory[idx].speaker);
                if (newName !== null) {
                    conversationHistory[idx].speaker = newName.trim() || conversationHistory[idx].speaker;
                    renderMeetingLog();
                }
            };
        });
        logEl.scrollTop = logEl.scrollHeight;
    }

    document.getElementById('convMeBtn').onclick = () => {
        runConversationTurn('나', document.getElementById('realtimeSource').value, document.getElementById('realtimeTarget').value);
    };
    document.getElementById('convOtherBtn').onclick = () => {
        runConversationTurn('상대', document.getElementById('realtimeTarget').value, document.getElementById('realtimeSource').value);
    };

    document.getElementById('convUnknownBtn').onclick = () => {
        const src = document.getElementById('realtimeSource').value;
        const tgt = document.getElementById('realtimeTarget').value;
        const who = prompt('이 말을 한 사람 이름을 입력하세요 (원어로 말함):', '');
        runConversationTurn(who ? who.trim() : '화자', src, tgt);
    };

    document.getElementById('downloadMeetingTxt').onclick = () => {
        if (conversationHistory.length === 0) {
            alert('저장할 대화 내용이 없습니다.');
            return;
        }
        const LANG_NAMES = window.LANG_NAMES || {};
        const sourceName = LANG_NAMES[document.getElementById('realtimeSource').value] || '원어';
        const targetName = LANG_NAMES[document.getElementById('realtimeTarget').value] || '대상어';
        let txt = `=== 회의록 ===\n`;
        txt += `일시: ${new Date().toLocaleString('ko-KR')}\n`;
        txt += `언어: ${sourceName} ↔ ${targetName}\n`;
        txt += `\n--- 대화 내용 ---\n\n`;
        conversationHistory.forEach((x) => {
            txt += `[${x.time}] ${x.speaker}\n`;
            txt += `${x.original}\n`;
            txt += `→ ${x.translation}\n\n`;
        });
        const blob = new Blob([txt], { type: 'text/plain;charset=utf-8' });
        const a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = `회의록_${new Date().toISOString().slice(0, 10)}.txt`;
        a.click();
        URL.revokeObjectURL(a.href);
    };

    document.getElementById('clearMeetingBtn').onclick = () => {
        if (conversationHistory.length > 0 && !confirm('회의록을 초기화하시겠습니까?')) return;
        conversationHistory = [];
        renderMeetingLog();
        document.getElementById('realtimeResult').textContent = '결과가 여기 표시됩니다.';
        document.getElementById('realtimeResult').classList.add('empty');
        document.getElementById('realtimeResultBtns').style.display = 'none';
    };

    document.getElementById('multiTranslateBtn').onclick = async () => {
        const text = document.getElementById('multiInput').value.trim();
        const targets = [...document.getElementById('multiTargets').querySelectorAll('input:checked')].map(
            x => x.value
        );
        if (!text || !targets.length) return;
        document.getElementById('multiTranslateBtn').disabled = true;
        document.getElementById('multiTranslateBtn').innerHTML =
            '<span class="loading"></span>번역 중...';
        try {
            const res = await fetch('/api/translate/multi', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    text,
                    source: document.getElementById('multiSource').value,
                    targets,
                    use_llm: document.getElementById('multiUseLlm').checked,
                }),
            });
            const data = await res.json();
            const LANG_NAMES = window.LANG_NAMES || {};
            document.getElementById('multiResult').innerHTML = Object.entries(data.results)
                .map(
                    ([lang, r]) =>
                        `<div class="multi-item"><span class="lang">${escapeHtml(LANG_NAMES[lang] || lang)}</span><div class="text">${escapeHtml(r.translation)}</div><div class="item-actions"><button class="tts-btn" data-text="${escapeHtml(r.translation)}" data-lang="${lang}">🔊 듣기</button></div></div>`
                )
                .join('');
            document.getElementById('multiResult').querySelectorAll('.tts-btn').forEach(btn => {
                btn.onclick = () => speakText(btn.dataset.text || '', btn.dataset.lang);
            });
        } catch (e) {
            document.getElementById('multiResult').innerHTML =
                '<p class="error-msg">' + escapeHtml(e.message) + '</p>';
        } finally {
            document.getElementById('multiTranslateBtn').disabled = false;
            document.getElementById('multiTranslateBtn').textContent = '다국어 번역';
        }
    };
}

function escapeHtml(s) {
    if (!s) return '';
    const div = document.createElement('div');
    div.textContent = s;
    return div.innerHTML;
}

const TTS_LANG_MAP = {
    ko: 'ko-KR',
    en: 'en-US',
    ja: 'ja-JP',
    'zh-CN': 'zh-CN',
    'zh-TW': 'zh-TW',
    es: 'es-ES',
    fr: 'fr-FR',
    de: 'de-DE',
    ru: 'ru-RU',
};

const STT_LANG_MAP = {
    ko: 'ko-KR',
    en: 'en-US',
    ja: 'ja-JP',
    'zh-CN': 'zh-CN',
    'zh-TW': 'zh-TW',
    es: 'es-ES',
    fr: 'fr-FR',
    de: 'de-DE',
    ru: 'ru-RU',
};

function speakText(text, langCode) {
    if (!text?.trim()) return;
    if (!('speechSynthesis' in window)) {
        alert('이 브라우저는 음성 읽기를 지원하지 않습니다.');
        return;
    }
    speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(text.trim());
    u.lang = TTS_LANG_MAP[langCode] || langCode || 'en-US';
    u.rate = 0.9;
    speechSynthesis.speak(u);
}

function parseEmail(raw) {
    const lines = raw.split(/\r?\n/);
    let from = '';
    let subject = '';
    let bodyStart = -1;
    for (let i = 0; i < Math.min(lines.length, 30); i++) {
        const line = lines[i];
        if (/^From:\s*/i.test(line)) {
            from = line.replace(/^From:\s*/i, '').trim();
        } else if (/^Subject:\s*/i.test(line)) {
            subject = line.replace(/^Subject:\s*/i, '').trim();
        } else if (line.trim() === '' && i > 0) {
            bodyStart = i + 1;
            break;
        }
    }
    if (bodyStart < 0) bodyStart = 0;
    const body = lines.slice(bodyStart).join('\n').trim() || raw;
    return {
        from: from || null,
        subject: subject || null,
        body: body,
    };
}

document.addEventListener('DOMContentLoaded', init);
