import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { ArrowLeft, FileText, Calendar } from "lucide-react";
import client from "../api/client";
import Skeleton from "../components/Skeleton";

export default function ArticleDetail() {
  const { id } = useParams<{ id: string }>();
  const [article, setArticle] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!id) return;
    client.get(`/articles/${id}`).then(({ data }) => {
      setArticle(data);
      document.title = `${data.title} - EcoFinwize`;
    }).catch(() => {}).finally(() => setLoading(false));
  }, [id]);

  if (loading) return <Skeleton variant="page-detail" />;
  if (!article) return (
    <div className="px-4 py-20 text-center">
      <p className="text-gray-400">Article not found</p>
      <Link to="/articles" className="text-sky-500 text-sm mt-2 inline-block">&larr; Back to articles</Link>
    </div>
  );

  return (
    <div className="px-4 py-6 max-w-lg mx-auto">
      <Link to="/articles" className="inline-flex items-center gap-1 text-sm text-gray-400 hover:text-gray-600 mb-4"><ArrowLeft className="w-4 h-4" /> Back</Link>
      <div className="card">
        <div className="flex items-center gap-2 mb-3">
          {article.category && <span className="badge-sky">{article.category}</span>}
          {article.read_time && <span className="text-xs text-gray-400 flex items-center gap-1"><Calendar className="w-3 h-3" />{article.read_time}</span>}
        </div>
        <h1 className="text-xl font-bold text-gray-800 mb-3">{article.title}</h1>
        <div className="flex items-center gap-2 text-xs text-gray-400 mb-4">
          <FileText className="w-3 h-3" />
          {article.author && <span>{article.author}</span>}
          {article.date && <span>{new Date(article.date).toLocaleDateString()}</span>}
        </div>
        <div className="prose prose-sm text-gray-600 whitespace-pre-wrap">{article.content || article.summary}</div>
      </div>
    </div>
  );
}
