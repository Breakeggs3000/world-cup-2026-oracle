import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import en from './locales/en.json';
import zh from './locales/zh.json';
import ko from './locales/ko.json';
import ja from './locales/ja.json';
import de from './locales/de.json';
import pt from './locales/pt.json';
import es from './locales/es.json';
import fr from './locales/fr.json';
import ar from './locales/ar.json';
import hi from './locales/hi.json';
import ru from './locales/ru.json';
import it from './locales/it.json';
import tr from './locales/tr.json';
import id from './locales/id.json';
import vi from './locales/vi.json';

const saved = typeof localStorage !== 'undefined' ? localStorage.getItem('wc_lang') : null;
const browser = typeof navigator !== 'undefined' ? navigator.language.split('-')[0] : 'en';

i18n.use(initReactI18next).init({
  resources: {
    en: { translation: en },
    zh: { translation: zh },
    ko: { translation: ko },
    ja: { translation: ja },
    de: { translation: de },
    pt: { translation: pt },
    es: { translation: es },
    fr: { translation: fr },
    ar: { translation: ar },
    hi: { translation: hi },
    ru: { translation: ru },
    it: { translation: it },
    tr: { translation: tr },
    id: { translation: id },
    vi: { translation: vi },
  },
  lng: saved || browser || 'en',
  fallbackLng: 'en',
  interpolation: { escapeValue: false },
});

export function setLanguage(code: string) {
  i18n.changeLanguage(code);
  localStorage.setItem('wc_lang', code);
  document.documentElement.lang = code;
  document.documentElement.dir = code === 'ar' ? 'rtl' : 'ltr';
}

document.documentElement.lang = i18n.language;
document.documentElement.dir = i18n.language === 'ar' ? 'rtl' : 'ltr';

export default i18n;
