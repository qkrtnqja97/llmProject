import React, { useState, useEffect, useCallback } from "react";
import * as LucideIcons from "lucide-react";
import {
  useTranslation,
  useBatchTranslation,
  useFileTranslation,
  useEmailTranslation,
  useMultiTranslation,
} from "@hooks/useTranslation";
import { useRealtimeTranslation } from "@hooks/useRealtimeTranslation";
import { useTTS } from "@hooks/useSpeech";
import { parseEmail } from "@services/emailService";
import styles from "./TranslationModal.module.css";

type TranslationTab =
  | "basic"
  | "realtime"
  | "batch"
  | "file"
  | "email"
  | "multi";

interface TranslationModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const languages = [
  { code: "ko", name: "한국어" },
  { code: "en", name: "영어" },
  { code: "ja", name: "일본어" },
  { code: "zh-CN", name: "중국어(간체)" },
  { code: "zh-TW", name: "중국어(번체)" },
  { code: "es", name: "스페인어" },
  { code: "fr", name: "프랑스어" },
  { code: "de", name: "독일어" },
];

const TranslationModal: React.FC<TranslationModalProps> = ({
  isOpen,
  onClose,
}) => {
  const [activeTab, setActiveTab] = useState<TranslationTab>("basic");
  const [sourceLang, setSourceLang] = useState("ko");
  const [targetLang, setTargetLang] = useState("en");
  const [useLlm, setUseLlm] = useState(true);
  const [selectedTargets, setSelectedTargets] = useState<string[]>([]);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [manualInput, setManualInput] = useState("");
  // 배치 번역 결과를 담을 별도 상태 추가
  const [batchResultText, setBatchResultText] = useState("");

  const {
    translate: basicTranslate,
    result: basicResult,
    isLoading: basicLoading,
    clear: clearBasic,
  } = useTranslation();

  const {
    text: rtInput,
    result: rtResult,
    isLoading: rtLoading,
    handleTextChange: rtHandleChange,
    clear: clearRt,
  } = useRealtimeTranslation(800);

  const { translate: batchTranslate, isLoading: batchLoading } =
    useBatchTranslation();
  const { translate: fileTranslate, isLoading: fileLoading } =
    useFileTranslation();
  const {
    translate: emailTranslate,
    result: emailResult,
    isLoading: emailLoading,
    clear: clearEmail,
  } = useEmailTranslation();
  const {
    translate: multiTranslate,
    results: multiResults,
    isLoading: multiLoading,
    clear: clearMulti,
  } = useMultiTranslation();

  const { speak } = useTTS();

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    if (isOpen) window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose]);

  const resetAllStates = useCallback(() => {
    setManualInput("");
    setBatchResultText("");
    setSelectedFile(null);
    setSelectedTargets([]);
    if (clearBasic) clearBasic();
    if (clearRt) clearRt();
    if (clearEmail) clearEmail();
    if (clearMulti) clearMulti();
  }, [clearBasic, clearRt, clearEmail, clearMulti]);

  const handleTabChange = (tabId: TranslationTab) => {
    setActiveTab(tabId);
    resetAllStates();
  };

  useEffect(() => {
    if (!isOpen) resetAllStates();
  }, [isOpen, resetAllStates]);

  if (!isOpen) return null;

  const handleManualTranslate = async () => {
    if (activeTab === "realtime") return;
    if (!manualInput.trim()) return;

    if (activeTab === "basic") {
      await basicTranslate(manualInput, sourceLang, targetLang, useLlm);
    } else if (activeTab === "batch") {
      // 마침표(.) 기준으로 분리
      const sentenceDelimiter =
        /([.?!](?=(?:[^"']*["'][^"']*["'])*[^"']*$)\s*)/g;

      // 기호를 보존하며 분할 (split에 캡처 그룹을 쓰면 기호도 배열에 남습니다)
      const rawParts = manualInput
        .split(sentenceDelimiter)
        .filter((p) => p.trim());
      const sentences: string[] = [];
      for (let i = 0; i < rawParts.length; i++) {
        let part = rawParts[i];
        // 만약 현재 파트가 구분 기호([.?!])라면 이전 문장에 붙여줌
        if (/^[.?!]\s*$/.test(part) && sentences.length > 0) {
          sentences[sentences.length - 1] += part;
        } else {
          sentences.push(part);
        }
      }

      const response = (await batchTranslate(
        sentences,
        sourceLang,
        targetLang,
        useLlm,
      )) as any;

      if (response) {
        let interleavedText = "";
        sentences.forEach((original, index) => {
          const translated = Array.isArray(response)
            ? response[index]
            : response.translations?.[index] ||
              response.result?.[index] ||
              response.data?.[index];

          const finalStr =
            typeof translated === "object"
              ? translated.text || translated.translation || ""
              : translated || "";

          interleavedText += `${original.trim()}\n${finalStr.trim()}\n\n`;
        });
        // 📍 입력란을 건드리지 않고 결과 상태에만 저장
        setBatchResultText(interleavedText.trim());
      }
    } else if (activeTab === "email") {
      const parsed = parseEmail(manualInput);
      await emailTranslate(
        parsed.from,
        parsed.subject,
        parsed.body,
        sourceLang,
        targetLang,
        useLlm,
      );
    } else if (activeTab === "multi") {
      if (selectedTargets.length === 0) return alert("대상 언어를 선택하세요.");
      await multiTranslate(manualInput, sourceLang, selectedTargets, useLlm);
    }
  };

  const isAnyLoading =
    basicLoading ||
    batchLoading ||
    emailLoading ||
    multiLoading ||
    fileLoading ||
    rtLoading;

  return (
    <div className={styles.overlay}>
      <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
        <div className={styles.header}>
          <h2>
            <LucideIcons.Languages size={22} /> 하이브리드 번역기
          </h2>
          <button className={styles.closeBtn} onClick={onClose}>
            <LucideIcons.X size={24} />
          </button>
        </div>

        <div className={styles.tabs}>
          {[
            {
              id: "basic",
              icon: <LucideIcons.Type size={16} />,
              label: "기본",
            },
            {
              id: "realtime",
              icon: <LucideIcons.Zap size={16} />,
              label: "실시간",
            },
            {
              id: "batch",
              icon: <LucideIcons.Layers size={16} />,
              label: "배치",
            },
            {
              id: "email",
              icon: <LucideIcons.Mail size={16} />,
              label: "메일",
            },
            { id: "file", icon: <LucideIcons.File size={16} />, label: "파일" },
            {
              id: "multi",
              icon: <LucideIcons.Globe size={16} />,
              label: "다국어",
            },
          ].map((tab) => (
            <button
              key={tab.id}
              className={`${styles.tab} ${activeTab === tab.id ? styles.active : ""}`}
              onClick={() => handleTabChange(tab.id as TranslationTab)}
            >
              {tab.icon} {tab.label}
            </button>
          ))}
        </div>

        <div className={styles.content}>
          <div className={styles.usageCard}>
            <div className={styles.usageTitle}>
              <LucideIcons.BookOpen size={14} style={{ marginRight: 6 }} />
              {activeTab === "batch"
                ? "배치 번역: 마침표 단위로 문장을 분석하여 대역문을 생성합니다."
                : "번역 모드에 맞춰 내용을 입력하세요."}
            </div>
          </div>

          <div className={styles.controls}>
            <div className={styles.controlGroup}>
              <label>원문 언어</label>
              <select
                value={sourceLang}
                onChange={(e) => setSourceLang(e.target.value)}
              >
                {languages.map((l) => (
                  <option key={l.code} value={l.code}>
                    {l.name}
                  </option>
                ))}
              </select>
            </div>
            {activeTab !== "multi" && (
              <>
                <button
                  className={styles.swapBtn}
                  onClick={() => {
                    const temp = sourceLang;
                    setSourceLang(targetLang);
                    setTargetLang(temp);
                  }}
                >
                  <LucideIcons.ArrowRightLeft size={16} />
                </button>
                <div className={styles.controlGroup}>
                  <label>대상 언어</label>
                  <select
                    value={targetLang}
                    onChange={(e) => setTargetLang(e.target.value)}
                  >
                    {languages.map((l) => (
                      <option key={l.code} value={l.code}>
                        {l.name}
                      </option>
                    ))}
                  </select>
                </div>
              </>
            )}
            <div className={styles.toggleRow}>
              <input
                type="checkbox"
                id="useLlm"
                checked={useLlm}
                onChange={(e) => setUseLlm(e.target.checked)}
              />
              <label htmlFor="useLlm">AI 보정</label>
            </div>
          </div>

          {activeTab !== "file" && (
            <div className={styles.inputWrapper}>
              <textarea
                className={styles.textarea}
                style={{
                  width: "100%",
                  boxSizing: "border-box",
                  overflowWrap: "break-word",
                  whiteSpace: "pre-wrap",
                }}
                value={activeTab === "realtime" ? rtInput : manualInput}
                onChange={(e) => {
                  const val = e.target.value;
                  if (activeTab === "realtime")
                    rtHandleChange(val, sourceLang, targetLang, useLlm);
                  else setManualInput(val);
                }}
                placeholder="번역할 내용을 입력하세요..."
              />

              {activeTab === "multi" && (
                <div className={styles.multiLangCheckboxes}>
                  <span className={styles.subTitle}>출력 언어 선택</span>
                  <div className={styles.checkboxGrid}>
                    {languages
                      .filter((l) => l.code !== sourceLang)
                      .map((lang) => (
                        <label key={lang.code} className={styles.langCheckbox}>
                          <input
                            type="checkbox"
                            checked={selectedTargets.includes(lang.code)}
                            onChange={() =>
                              setSelectedTargets((prev) =>
                                prev.includes(lang.code)
                                  ? prev.filter((c) => c !== lang.code)
                                  : [...prev, lang.code],
                              )
                            }
                          />{" "}
                          {lang.name}
                        </label>
                      ))}
                  </div>
                </div>
              )}

              {activeTab === "realtime" ? (
                <div className={styles.rtStatus}>
                  {rtLoading ? (
                    <>
                      <span className={styles.loadingSpin} /> 번역 중...
                    </>
                  ) : (
                    <span className={styles.autoBadge}>자동 번역 활성</span>
                  )}
                </div>
              ) : (
                <button
                  className={styles.translateBtn}
                  onClick={handleManualTranslate}
                  disabled={isAnyLoading || !manualInput.trim()}
                >
                  {isAnyLoading ? (
                    <>
                      <span className={styles.loadingSpin} /> 처리 중...
                    </>
                  ) : (
                    "번역하기"
                  )}
                </button>
              )}
            </div>
          )}

          {activeTab === "file" && (
            <div className={styles.fileSection}>
              <div
                className={styles.fileDrop}
                onClick={() => document.getElementById("fileInput")?.click()}
              >
                <input
                  type="file"
                  id="fileInput"
                  hidden
                  onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
                />
                <LucideIcons.UploadCloud size={40} />
                <p>
                  {selectedFile ? selectedFile.name : "클릭하여 파일 업로드"}
                </p>
              </div>
              <button
                className={styles.translateBtn}
                disabled={!selectedFile || fileLoading}
                onClick={() =>
                  selectedFile &&
                  fileTranslate(selectedFile, sourceLang, targetLang, useLlm)
                }
              >
                {fileLoading ? "번역 중..." : "파일 번역 시작"}
              </button>
            </div>
          )}

          <div className={styles.resultContainer}>
            {/* 📍 배치 결과 렌더링 추가 */}
            {((activeTab === "basic" && basicResult) ||
              (activeTab === "realtime" && rtResult) ||
              (activeTab === "email" && emailResult) ||
              (activeTab === "batch" && batchResultText)) && (
              <div className={styles.resultCard}>
                <div className={styles.resultHeader}>
                  <span>번역 결과</span>
                  <button
                    className={styles.iconBtn}
                    onClick={() =>
                      speak(
                        activeTab === "email"
                          ? emailResult?.body_translated || ""
                          : activeTab === "batch"
                            ? batchResultText
                            : basicResult?.translation ||
                              rtResult?.translation ||
                              "",
                        targetLang,
                      )
                    }
                  >
                    <LucideIcons.Volume2 size={18} />
                  </button>
                </div>
                <div className={styles.resultText}>
                  {activeTab === "email" ? (
                    <>
                      <div className={styles.emailSubject}>
                        <strong>제목:</strong> {emailResult?.subject_translated}
                      </div>
                      <div className={styles.emailDivider} />
                      <div>{emailResult?.body_translated}</div>
                    </>
                  ) : activeTab === "batch" ? (
                    <div style={{ whiteSpace: "pre-wrap" }}>
                      {batchResultText}
                    </div>
                  ) : (
                    <p>
                      {activeTab === "realtime"
                        ? rtResult?.translation
                        : basicResult?.translation}
                    </p>
                  )}
                </div>
              </div>
            )}

            {activeTab === "multi" && multiResults && (
              <div className={styles.multiResultGrid}>
                {Object.entries(multiResults).map(
                  ([lang, data]: [string, any]) => (
                    <div key={lang} className={styles.miniResultCard}>
                      <div className={styles.miniHeader}>
                        {languages.find((l) => l.code === lang)?.name}
                      </div>
                      <p>{data?.translation || data?.text || ""}</p>
                    </div>
                  ),
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default TranslationModal;
