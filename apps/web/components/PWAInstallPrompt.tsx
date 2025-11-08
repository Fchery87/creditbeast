'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { usePWA } from '@/hooks/usePWA';

export function PWAInstallPrompt() {
  const {
    isInstallable,
    isInstalled,
    installPWA,
    requestNotificationPermission,
    showNotification
  } = usePWA();
  
  const [showInstallPrompt, setShowInstallPrompt] = useState(false);
  const [notificationsEnabled, setNotificationsEnabled] = useState(false);

  useEffect(() => {
    // Show install prompt after 30 seconds if not installed
    if (isInstallable && !isInstalled) {
      const timer = setTimeout(() => {
        setShowInstallPrompt(true);
      }, 30000);

      return () => clearTimeout(timer);
    }
  }, [isInstallable, isInstalled]);

  const handleInstall = async () => {
    const success = await installPWA();
    if (success) {
      setShowInstallPrompt(false);
      
      // Show success notification
      showNotification('CreditBeast installed!', {
        body: 'The app has been successfully installed on your device.',
        icon: '/icons/icon-192x192.png'
      });
    }
  };

  const handleNotifications = async () => {
    const granted = await requestNotificationPermission();
    setNotificationsEnabled(granted);
    
    if (granted) {
      showNotification('Notifications enabled!', {
        body: 'You will now receive updates about your credit repair progress.',
        icon: '/icons/icon-192x192.png'
      });
    }
  };

  if (!isInstallable || isInstalled || !showInstallPrompt) {
    return null;
  }

  return (
    <div className="fixed bottom-4 right-4 z-50 max-w-sm">
      <div className="bg-white rounded-lg shadow-lg border p-6">
        <div className="flex items-start gap-3">
          <div className="flex-shrink-0">
            <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center">
              <svg className="w-6 h-6 text-primary-600" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zm0 4a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1V8zm8 0a1 1 0 011-1h4a1 1 0 011 1v2a1 1 0 01-1 1h-4a1 1 0 01-1-1V8zm0 4a1 1 0 011-1h4a1 1 0 011 1v2a1 1 0 01-1 1h-4a1 1 0 01-1-1v-2z" clipRule="evenodd" />
              </svg>
            </div>
          </div>
          <div className="flex-1 min-w-0">
            <h3 className="text-sm font-semibold text-gray-900">
              Install CreditBeast
            </h3>
            <p className="text-sm text-gray-500 mt-1">
              Get the best experience by installing our app. Access your dashboard offline and receive push notifications.
            </p>
            <div className="flex gap-2 mt-4">
              <Button
                size="sm"
                onClick={handleInstall}
                className="flex-1"
              >
                Install
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowInstallPrompt(false)}
              >
                Later
              </Button>
            </div>
          </div>
          <button
            onClick={() => setShowInstallPrompt(false)}
            className="flex-shrink-0 text-gray-400 hover:text-gray-600"
          >
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
            </svg>
          </button>
        </div>
      </div>
      
      {/* Notifications prompt */}
      {!notificationsEnabled && (
        <div className="mt-3 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-blue-900">
                Enable notifications?
              </p>
              <p className="text-sm text-blue-700">
                Get updates about your clients and disputes
              </p>
            </div>
            <Button
              size="sm"
              variant="outline"
              onClick={handleNotifications}
              className="text-blue-700 border-blue-300 hover:bg-blue-100"
            >
              Enable
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}

export function PWAUpdatePrompt() {
  const { updateAvailable, updatePWA, serviceWorkerRegistration } = usePWA();
  const [showUpdatePrompt, setShowUpdatePrompt] = useState(false);

  useEffect(() => {
    if (updateAvailable && serviceWorkerRegistration) {
      setShowUpdatePrompt(true);
    }
  }, [updateAvailable, serviceWorkerRegistration]);

  if (!showUpdatePrompt) return null;

  return (
    <div className="fixed top-4 right-4 z-50 max-w-sm">
      <div className="bg-white rounded-lg shadow-lg border p-4">
        <div className="flex items-center gap-3">
          <div className="flex-shrink-0">
            <div className="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center">
              <svg className="w-4 h-4 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
            </div>
          </div>
          <div className="flex-1 min-w-0">
            <h3 className="text-sm font-semibold text-gray-900">
              Update Available
            </h3>
            <p className="text-sm text-gray-500">
              A new version of CreditBeast is ready to install.
            </p>
          </div>
        </div>
        <div className="flex gap-2 mt-3">
          <Button
            size="sm"
            onClick={() => {
              updatePWA();
              setShowUpdatePrompt(false);
            }}
            className="flex-1"
          >
            Update Now
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowUpdatePrompt(false)}
          >
            Later
          </Button>
        </div>
      </div>
    </div>
  );
}

export function OfflineIndicator() {
  const isOnline = usePWA().isOnline;

  if (isOnline) return null;

  return (
    <div className="fixed top-0 left-0 right-0 z-50 bg-yellow-500 text-white px-4 py-2 text-center text-sm">
      <div className="flex items-center justify-center gap-2">
        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
        </svg>
        <span>You're offline. Some features may be limited.</span>
      </div>
    </div>
  );
}