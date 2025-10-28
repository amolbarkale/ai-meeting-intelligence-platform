"use client"

import { Badge } from "@/components/ui/badge"

interface TopicTagsBarProps {
  tags: string[]
  onTagClick?: (tag: string) => void
}

export default function TopicTagsBar({ tags, onTagClick }: TopicTagsBarProps) {
  return (
    <div className="flex flex-wrap gap-2">
      {tags.map((tag) => (
        <Badge
          key={tag}
          variant="secondary"
          className="cursor-pointer hover:bg-blue-100 transition"
          onClick={() => onTagClick?.(tag)}
        >
          {tag}
        </Badge>
      ))}
    </div>
  )
}
