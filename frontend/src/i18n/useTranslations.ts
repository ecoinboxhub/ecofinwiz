import { useLanguage } from "../context/LanguageContext";
import { t } from "./translations";

export function useTranslations() {
  const { language } = useLanguage();

  const translate = (key: string, ...args: (string | number)[]) => {
    return t(language.code, key, ...args);
  };

  return { t: translate, lang: language.code };
}
