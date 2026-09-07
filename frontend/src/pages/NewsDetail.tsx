import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { ArrowLeft, Newspaper, TrendingUp } from "lucide-react";
import client from "../api/client";
import Skeleton from "../components/Skeleton";

export default function NewsDetail() {
  const { id } = useParams<{ id: string }>();
  const [item, setItem] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!id) return;
    client.get(`/news/${id}`).then(({ data }) => {
      setItem(data);
      document.title = `${data.title} - Finwize`;
    }).catch(() => {}).finally(() => setLoading(false));
  }, [id]);

  if (loading) return <Skeleton variant="page-detail" />;
  if (!item) return (
    <div className="px-4 py-20 text-center">
      <p className="text-gray-400">News not found</p>
      <Link to="/news" className="text-sky-500 text-sm mt-2 inline-block">&larr; Back to news</Link>
    </div>
  );

  return (
    <div className="px-4 py-6 max-w-lg mx-auto">
      <Link to="/news" className="inline-flex items-center gap-1 text-sm text-gray-400 hover:text-gray-600 mb-4"><ArrowLeft className="w-4 h-4" /> Back</Link>
      <div className="card">
        <div className="flex items-center gap-2 mb-3">
          <Newspaper className="w-4 h-4 text-orange-500" />
          {item.category && <span className="badge-orange">{item.category}</span>}
          {item.is_breaking && <span className="bg-rose-50 text-rose-600 text-xs font-medium px-2 py-0.5 rounded-full inline-flex items-center gap-1"><TrendingUp className="w-3 h-3" />Breaking</span>}
        </div>
        <h1 className="text-xl font-bold text-gray-800 mb-2">{item.title}</h1>
        <div className="flex items-center gap-2 text-xs text-gray-400 mb-4">
          {item.source && <span className="font-medium">{item.source}</span>}
          {item.date && <span>{new Date(item.date).toLocaleDateString()}</span>}
        </div>
        <div className="prose prose-sm text-gray-600 whitespace-pre-wrap">{item.content || item.summary}</div>
      </div>
    </div>
  );
}
