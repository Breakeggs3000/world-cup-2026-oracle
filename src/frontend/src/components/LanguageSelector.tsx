import { useTranslation } from 'react-i18next';
import { setLanguage } from '../i18n';

const LANGUAGES = [
  ['en', 'English'],
  ['zh', '中文'],
  ['ko', '한국어'],
  ['ja', '日本語'],
  ['de', 'Deutsch'],
  ['pt', 'Português'],
  ['es', 'Español'],
  ['fr', 'Français'],
  ['ar', 'العربية'],
  ['hi', 'हिन्दी'],
  ['ru', 'Русский'],
  ['it', 'Italiano'],
  ['tr', 'Türkçe'],
  ['id', 'Indonesia'],
  ['vi', 'Tiếng Việt'],
] as const;

export function LanguageSelector() {
  const { i18n, t } = useTranslation();
  return (
    <label className="lang-select">
      {t('app.language')}
      <select
        value={i18n.language}
        onChange={(e) => setLanguage(e.target.value)}
        aria-label={t('app.language')}
      >
        {LANGUAGES.map(([code, label]) => (
          <option key={code} value={code}>{label}</option>
        ))}
      </select>
    </label>
  );
}
