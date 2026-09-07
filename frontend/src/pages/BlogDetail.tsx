import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { ArrowLeft, Heart, MessageSquare } from "lucide-react";
import client from "../api/client";
import Skeleton from "../components/Skeleton";

export default function BlogDetail() {
  const { id } = useParams<{ id: string }>();
  const [post, setPost] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!id) return;
    client.get(`/blog/${id}`).then(({ data }) => {
      setPost(data);
      document.title = `${data.title} - Finwize`;
    }).catch(() => {}).finally(() => setLoading(false));
  }, [id]);

  if (loading) return <Skeleton variant="page-detail" />;
  if (!post) return (
    <div className="px-4 py-20 text-center">
      <p className="text-gray-400">Post not found</p>
      <Link to="/blog" className="text-sky-500 text-sm mt-2 inline-block">&larr; Back to blog</Link>
    </div>
  );

  return (
    <div className="px-4 py-6 max-w-lg mx-auto">
      <Link to="/blog" className="inline-flex items-center gap-1 text-sm text-gray-400 hover:text-gray-600 mb-4"><ArrowLeft className="w-4 h-4" /> Back</Link>
      <div className="card">
        <h1 className="text-xl font-bold text-gray-800 mb-2">{post.title}</h1>
        <div className="flex items-center gap-3 text-xs text-gray-400 mb-4">
          <span>{post.author || "Anonymous"}</span>
          <span className="flex items-center gap-1"><Heart className="w-3 h-3" />{post.likes || 0}</span>
          <span className="flex items-center gap-1"><MessageSquare className="w-3 h-3" />{post.comment_count || 0}</span>
        </div>
        <div className="prose prose-sm text-gray-600 whitespace-pre-wrap">{post.content}</div>
      </div>
    </div>
  );
}
