import { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import client from "../api/client";
import { ExternalLink, Crown } from "lucide-react";
import { Link } from "react-router-dom";

interface Ad {
  id: string; image_url: string; target_url: string;
  sponsor_name: string; label: string;
}

export default function AdBanner({ pageContext }: { pageContext: string }) {
  const { user } = useAuth();
  const [ad, setAd] = useState<Ad | null>(null);

  useEffect(() => {
    if (!user || user.plan !== "free") return;
    client.get(`/ads/${pageContext}`).then(({ data }) => {
      if (data.length > 0) setAd(data[0]);
    }).catch(() => {});
  }, [user, pageContext]);

  if (!user || user.plan !== "free") return null;
  if (!ad) return (
    <div className="mx-4 my-2 p-3 border border-dashed border-gray-200 rounded-lg bg-gray-50/50 text-center">
      <p className="text-xs text-gray-400">
        Ad-free with{" "}
        <Link to="/pricing" className="text-sky-500 font-medium inline-flex items-center gap-1">
           <Crown className="w-3 h-3" /> EcoFinwize Pro
        </Link>
      </p>
    </div>
  );

  return (
    <div className="mx-4 my-2">
      <a
        href={ad.target_url}
        target="_blank"
        rel="noopener noreferrer"
        onClick={() => client.post("/ads/impression", { campaign_id: ad.id }).catch(() => {})}
        className="block p-3 border border-sky-100 rounded-lg bg-gradient-to-r from-sky-50 to-white hover:shadow-sm transition-shadow"
      >
        <div className="flex items-start justify-between gap-2">
          <div className="flex-1 min-w-0">
            <p className="text-xs text-gray-400 mb-1 flex items-center gap-1">
              <span className="inline-block w-1.5 h-1.5 rounded-full bg-sky-400" />
              {ad.label} by {ad.sponsor_name}
            </p>
            <img src={ad.image_url} alt={ad.sponsor_name} className="rounded w-full h-auto max-h-16 object-contain" />
          </div>
          <ExternalLink className="w-3 h-3 text-gray-300 mt-1 shrink-0" />
        </div>
      </a>
    </div>
  );
}
