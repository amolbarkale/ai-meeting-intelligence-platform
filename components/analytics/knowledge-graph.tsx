"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

interface KnowledgeGraphProps {
  data: {
    nodes: Array<{
      id: string
      label: string
      size: number
      frequency: number
    }>
    edges: Array<{
      source: string
      target: string
      weight: number
    }>
  }
}

export default function KnowledgeGraph({ data }: KnowledgeGraphProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Topic Network</CardTitle>
        <CardDescription>Relationships between frequently discussed topics</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="bg-slate-50 rounded-lg p-6 min-h-96">
          <div className="space-y-4">
            <div>
              <h3 className="font-semibold text-slate-900 mb-3">Top Topics</h3>
              <div className="flex flex-wrap gap-2">
                {data.nodes.slice(0, 10).map((node) => (
                  <div
                    key={node.id}
                    className="px-3 py-2 bg-blue-100 text-blue-900 rounded-full text-sm font-medium"
                    style={{ opacity: Math.min(node.frequency / 10, 1) }}
                  >
                    {node.label} ({node.frequency})
                  </div>
                ))}
              </div>
            </div>

            <div>
              <h3 className="font-semibold text-slate-900 mb-3">Topic Connections</h3>
              <div className="space-y-2">
                {data.edges.slice(0, 8).map((edge, idx) => (
                  <div key={idx} className="flex items-center justify-between text-sm">
                    <span className="text-slate-700">
                      {edge.source} ↔ {edge.target}
                    </span>
                    <span className="text-slate-600 font-medium">{edge.weight} co-occurrences</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
