import { useState, useRef, useCallback, useEffect } from "react";
import { Mic, MicOff, Volume2, VolumeX } from "lucide-react";
import { useTranslations } from "../i18n/useTranslations";

interface VoiceButtonProps {
  onTranscript?: (text: string) => void;
  speakText?: string;
  size?: "sm" | "md";
  language?: string;
}

const LANG_MAP: Record<string, string> = {
  en: "en-US",
  ha: "ha-NG",
  yo: "yo-NG",
  ig: "ig-NG",
  sw: "sw-KE",
  am: "am-ET",
  zu: "zu-ZA",
  xh: "xh-ZA",
  tw: "ak-GH",
  fr: "fr-FR",
  wo: "wo-SN",
  ff: "ff-SN",
  pcm: "en-NG",
};

export default function VoiceButton({ onTranscript, speakText, size = "md", language = "en" }: VoiceButtonProps) {
  const [listening, setListening] = useState(false);
  const [speaking, setSpeaking] = useState(false);
  const [supported, setSupported] = useState({ stt: false, tts: false });
  const recognitionRef = useRef<any>(null);
  const utteranceRef = useRef<SpeechSynthesisUtterance | null>(null);
  const { t } = useTranslations();

  useEffect(() => {
    const stt = typeof window !== "undefined" && ("SpeechRecognition" in window || "webkitSpeechRecognition" in window);
    const tts = typeof window !== "undefined" && "speechSynthesis" in window;
    setSupported({ stt, tts });
  }, []);

  const stopSpeaking = useCallback(() => {
    if (window.speechSynthesis.speaking) {
      window.speechSynthesis.cancel();
    }
    setSpeaking(false);
  }, []);

  const speak = useCallback((text: string) => {
    if (!supported.tts) return;
    window.speechSynthesis.cancel();
    const clean = text.replace(/[#*_`>\[\]]/g, "").replace(/\n{2,}/g, ". ").replace(/\n/g, " ");
    const utterance = new SpeechSynthesisUtterance(clean);
    utterance.lang = LANG_MAP[language] || "en-US";
    utterance.rate = 1.05;
    utterance.pitch = 1.0;
    utterance.onend = () => setSpeaking(false);
    utterance.onerror = () => setSpeaking(false);
    utteranceRef.current = utterance;
    setSpeaking(true);
    window.speechSynthesis.speak(utterance);
  }, [supported.tts, language]);

  useEffect(() => {
    if (speakText && speaking) {
      speak(speakText);
    }
  }, [speakText]);

  const toggleListening = useCallback(() => {
    if (!supported.stt) return;

    if (listening && recognitionRef.current) {
      recognitionRef.current.stop();
      setListening(false);
      return;
    }

    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    recognition.lang = LANG_MAP[language] || "en-US";
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.onresult = (event: any) => {
      const transcript = event.results[0][0].transcript;
      onTranscript?.(transcript);
      setListening(false);
    };

    recognition.onerror = () => setListening(false);
    recognition.onend = () => setListening(false);

    recognitionRef.current = recognition;
    recognition.start();
    setListening(true);
  }, [listening, onTranscript, supported.stt, language]);

  const iconSize = size === "sm" ? "w-4 h-4" : "w-5 h-5";
  const btnSize = size === "sm" ? "p-1.5" : "p-2";

  return (
    <div className="flex items-center gap-1">
      {supported.stt && (
        <button
          type="button"
          onClick={toggleListening}
          className={`${btnSize} rounded-lg transition-colors ${listening ? "bg-rose-100 text-rose-600 animate-pulse" : "hover:bg-gray-100 text-gray-400"}`}
          title={listening ? t("voice.stopListening") : t("voice.voiceInput")}
          aria-label={listening ? t("voice.stopListening") : t("voice.voiceInput")}
        >
          {listening ? <MicOff className={iconSize} /> : <Mic className={iconSize} />}
        </button>
      )}
      {supported.tts && speakText && (
        <button
          type="button"
          onClick={() => (speaking ? stopSpeaking() : speak(speakText))}
          className={`${btnSize} rounded-lg transition-colors ${speaking ? "bg-sky-100 text-sky-600" : "hover:bg-gray-100 text-gray-400"}`}
          title={speaking ? t("voice.stopSpeaking") : t("voice.readAloud")}
          aria-label={speaking ? t("voice.stopSpeaking") : t("voice.readAloud")}
        >
          {speaking ? <VolumeX className={iconSize} /> : <Volume2 className={iconSize} />}
        </button>
      )}
    </div>
  );
}
