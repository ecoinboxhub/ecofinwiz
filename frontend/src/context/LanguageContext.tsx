import { createContext, useContext, useState, type ReactNode } from "react";

export interface Language {
  code: string;
  name: string;
  nativeName: string;
}

export const AFRICAN_LANGUAGES: Language[] = [
  { code: "en", name: "English", nativeName: "English" },
  { code: "ha", name: "Hausa", nativeName: "Hausa" },
  { code: "yo", name: "Yoruba", nativeName: "Yoruba" },
  { code: "ig", name: "Igbo", nativeName: "Igbo" },
  { code: "sw", name: "Swahili", nativeName: "Kiswahili" },
  { code: "am", name: "Amharic", nativeName: "Amharic" },
  { code: "zu", name: "Zulu", nativeName: "isiZulu" },
  { code: "xh", name: "Xhosa", nativeName: "isiXhosa" },
  { code: "tw", name: "Twi", nativeName: "Twi" },
  { code: "fr", name: "French", nativeName: "Francais" },
  { code: "wo", name: "Wolof", nativeName: "Wolof" },
  { code: "ff", name: "Fulfulde", nativeName: "Fulfulde" },
  { code: "pcm", name: "Nigerian Pidgin", nativeName: "Naija" },
];

interface LanguageContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
}

const LanguageContext = createContext<LanguageContextType>({
  language: AFRICAN_LANGUAGES[0],
  setLanguage: () => {},
});

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [language, setLanguageState] = useState<Language>(() => {
    const saved = localStorage.getItem("finwize_language");
    if (saved) {
      try { return JSON.parse(saved); } catch {}
    }
    return AFRICAN_LANGUAGES[0];
  });

  const setLanguage = (lang: Language) => {
    setLanguageState(lang);
    localStorage.setItem("finwize_language", JSON.stringify(lang));
  };

  return (
    <LanguageContext.Provider value={{ language, setLanguage }}>
      {children}
    </LanguageContext.Provider>
  );
}

export const useLanguage = () => useContext(LanguageContext);
