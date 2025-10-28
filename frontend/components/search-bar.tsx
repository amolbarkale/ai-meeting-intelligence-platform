"use client"

import type React from "react"

import { useState } from "react"
import { Search, Loader2 } from "lucide-react"

interface SearchBarProps {
  onSearch: (results: any) => void
}

export default function SearchBar({ onSearch }: SearchBarProps) {
  const [query, setQuery] = useState("")
  const [isLoading, setIsLoading] = useState(false)

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!query.trim()) return

    setIsLoading(true)
    try {
      const response = await fetch(`http://localhost:8000/search?q=${encodeURIComponent(query)}`)
      if (response.ok) {
        const data = await response.json()
        onSearch(data)
      }
    } catch (err) {
      console.error("Search error:", err)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <form onSubmit={handleSearch} className="w-full">
      <div className="relative">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search across all meetings..."
          className="w-full px-4 py-3 pl-12 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-slate-900 focus:border-transparent"
        />
        <Search className="absolute left-4 top-3.5 w-5 h-5 text-slate-400" />
        <button
          type="submit"
          disabled={isLoading || !query.trim()}
          className="absolute right-2 top-2.5 px-3 py-1 bg-slate-900 text-white rounded text-sm font-medium hover:bg-slate-800 disabled:opacity-50 disabled:cursor-not-allowed transition"
        >
          {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : "Search"}
        </button>
      </div>
    </form>
  )
}
