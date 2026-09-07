import { useState, useEffect } from "react";
import { WifiOff } from "lucide-react";

export default function OfflineBanner() {
  const [offline, setOffline] = useState(!navigator.onLine);

  useEffect(() => {
    const on = () => setOffline(false);
    const off = () => setOffline(true);
    window.addEventListener("online", on);
    window.addEventListener("offline", off);
    return () => {
      window.removeEventListener("online", on);
      window.removeEventListener("offline", off);
    };
  }, []);

  if (!offline) return null;

  return (
    <div className="bg-amber-500 text-white text-center text-xs font-medium py-1.5 px-4 flex items-center justify-center gap-1.5">
      <WifiOff className="w-3 h-3" />
      You are offline. Some features may be unavailable.
    </div>
  );
}
