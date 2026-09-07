import type { CSSProperties } from "react";

type SkeletonVariant = "text" | "card" | "chart" | "avatar" | "list" | "paragraph" | "page-detail";

interface SkeletonProps {
  variant?: SkeletonVariant;
  className?: string;
  lines?: number;
}

function SkeletonBlock({ className, style }: { className?: string; style?: CSSProperties }) {
  return <div className={`bg-gray-200 dark:bg-gray-700 rounded-xl animate-pulse ${className ?? ""}`} style={style} />;
}

function TextSkeleton({ lines = 1, className }: { lines?: number; className?: string }) {
  return (
    <div className={`space-y-2 ${className ?? ""}`}>
      {Array.from({ length: lines }).map((_, i) => (
        <SkeletonBlock key={i} className={`h-3 ${i === lines - 1 ? "w-3/4" : "w-full"}`} />
      ))}
    </div>
  );
}

function ParagraphSkeleton({ lines = 4 }: { lines?: number }) {
  return (
    <div className="space-y-3">
      <SkeletonBlock className="h-3 w-1/4" />
      {Array.from({ length: lines }).map((_, i) => (
        <SkeletonBlock key={i} className={`h-3 ${i === lines - 1 ? "w-2/3" : "w-full"}`} />
      ))}
    </div>
  );
}

function CardSkeleton() {
  return (
    <div className="card space-y-3">
      <div className="flex items-center gap-2">
        <SkeletonBlock className="w-4 h-4 rounded" />
        <SkeletonBlock className="h-3 w-20" />
      </div>
      <SkeletonBlock className="h-7 w-24" />
      <SkeletonBlock className="h-3 w-32" />
      <SkeletonBlock className="h-2 w-full rounded-full" />
    </div>
  );
}

function ChartSkeleton() {
  return (
    <div className="card space-y-3">
      <SkeletonBlock className="h-4 w-28" />
      <div className="flex items-end gap-2 h-40">
        {Array.from({ length: 7 }).map((_, i) => (
          <SkeletonBlock key={i} className="flex-1" style={{ height: `${40 + Math.random() * 60}%` }} />
        ))}
      </div>
    </div>
  );
}

function AvatarSkeleton() {
  return (
    <div className="flex items-center gap-3">
      <SkeletonBlock className="w-10 h-10 rounded-full" />
      <div className="space-y-1.5 flex-1">
        <SkeletonBlock className="h-3 w-24" />
        <SkeletonBlock className="h-2.5 w-32" />
      </div>
    </div>
  );
}

function ListSkeleton({ items = 3 }: { items?: number }) {
  return (
    <div className="space-y-2">
      {Array.from({ length: items }).map((_, i) => (
        <div key={i} className="card !p-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <SkeletonBlock className="w-9 h-9 rounded-full" />
            <div className="space-y-1.5">
              <SkeletonBlock className="h-3 w-28" />
              <SkeletonBlock className="h-2.5 w-20" />
            </div>
          </div>
          <SkeletonBlock className="h-4 w-16" />
        </div>
      ))}
    </div>
  );
}

function PageDetailSkeleton() {
  return (
    <div className="px-4 py-6 max-w-lg mx-auto space-y-4">
      <SkeletonBlock className="h-3 w-16" />
      <div className="card space-y-4">
        <div className="flex items-center gap-2">
          <SkeletonBlock className="h-5 w-16 rounded-full" />
          <SkeletonBlock className="h-3 w-20" />
        </div>
        <SkeletonBlock className="h-6 w-full" />
        <SkeletonBlock className="h-6 w-3/4" />
        <div className="flex items-center gap-2">
          <SkeletonBlock className="w-3 h-3 rounded" />
          <SkeletonBlock className="h-3 w-24" />
          <SkeletonBlock className="h-3 w-20" />
        </div>
        <ParagraphSkeleton lines={6} />
      </div>
    </div>
  );
}

export default function Skeleton({ variant = "text", className, lines }: SkeletonProps) {
  switch (variant) {
    case "text": return <TextSkeleton lines={lines ?? 1} className={className} />;
    case "paragraph": return <ParagraphSkeleton lines={lines ?? 4} />;
    case "card": return <CardSkeleton />;
    case "chart": return <ChartSkeleton />;
    case "avatar": return <AvatarSkeleton />;
    case "list": return <ListSkeleton items={lines ?? 3} />;
    case "page-detail": return <PageDetailSkeleton />;
    default: return <TextSkeleton lines={lines ?? 1} />;
  }
}
