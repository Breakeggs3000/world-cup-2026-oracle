import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';

const STORAGE_KEY = 'wc_disclaimer_accepted';

export function DisclaimerBanner() {
  const { t } = useTranslation();
  const [showModal, setShowModal] = useState(false);

  useEffect(() => {
    if (!localStorage.getItem(STORAGE_KEY)) {
      setShowModal(true);
    }
  }, []);

  const accept = () => {
    localStorage.setItem(STORAGE_KEY, '1');
    setShowModal(false);
  };

  return (
    <>
      <footer className="disclaimer-footer">{t('disclaimer.short')}</footer>
      {showModal && (
        <div className="disclaimer-modal-backdrop" role="dialog" aria-modal="true">
          <div className="disclaimer-modal">
            <h2>{t('disclaimer.title')}</h2>
            <p>{t('disclaimer.body')}</p>
            <button type="button" onClick={accept}>{t('disclaimer.accept')}</button>
          </div>
        </div>
      )}
    </>
  );
}
