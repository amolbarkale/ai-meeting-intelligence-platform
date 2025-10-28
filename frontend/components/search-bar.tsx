"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Search, Loader2, AlertCircle, FileText } from "lucide-react"
import { useMeetingSearch } from "@/lib/hooks"
import { SearchResult } from "@/lib/api"

interface SearchBarProps {
  onSearchResults?: (results: SearchResult[]) => void
}

export default function SearchBar({ onSearchResults }: SearchBarProps) {
  const [query, setQuery] = useState("")
  const [results, setResults] = useState<SearchResult[]>([])
  const [hasSearched, setHasSearched] = useState(false)
  const { search, isLoading, error } = useMeetingSearch()

  const handleSearch = async () => {
    if (!query.trim()) return

    setHasSearched(true)
    const searchResults = await search(query.trim())
    setResults(searchResults.results)
    onSearchResults?.(searchResults.results)
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch()
    }
  }

  const formatDistance = (distance: number) => {
    return (distance * 100).toFixed(1) + '%'
  }

  return (
    <div className="space-y-4">
      {/* Search Input */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
        <Input
          placeholder="Search meetings, topics, or transcripts..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyPress={handleKeyPress}
          className="pl-10 bg-slate-50 border-slate-200"
          disabled={isLoading}
        />
        <Button 
          onClick={handleSearch}
          disabled={!query.trim() || isLoading}
          className="absolute right-2 top-1/2 -translate-y-1/2"
          size="sm"
        >
          {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : "Search"}
        </Button>
      </div>

      {/* Search Results */}
      {hasSearched && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Search className="w-5 h-5" />
              Search Results
              {results.length > 0 && (
                <Badge variant="secondary">{results.length} found</Badge>
              )}
            </CardTitle>
            <CardDescription>
              {query ? `Results for "${query}"` : "Enter a search term"}
            </CardDescription>
          </CardHeader>
          <CardContent>
            {error ? (
              <div className="flex items-center gap-2 text-red-600 py-4">
                <AlertCircle className="w-5 h-5" />
                <p>{error}</p>
              </div>
            ) : results.length === 0 ? (
              <div className="text-center py-8">
                <FileText className="w-12 h-12 text-slate-300 mx-auto mb-4" />
                <p className="text-slate-500">No results found</p>
                <p className="text-sm text-slate-400 mt-1">Try different keywords</p>
              </div>
            ) : (
              <div className="space-y-4">
                {results.map((result, index) => (
                  <div key={index} className="border border-slate-200 rounded-lg p-4">
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <FileText className="w-4 h-4 text-slate-500" />
                        <span className="text-sm font-medium text-slate-700">
                          Meeting {result.metadata.meeting_id}
                        </span>
                      </div>
                      <Badge variant="outline" className="text-xs">
                        {formatDistance(result.distance)} match
                      </Badge>
                    </div>
                    <p className="text-slate-600 text-sm leading-relaxed">
                      {result.content}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  )
}
