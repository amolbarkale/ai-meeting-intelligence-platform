// API service for backend integration
const API_BASE_URL = 'http://localhost:8000/api/v1'

export interface MeetingResponse {
  id: string
  original_filename: string
  status: 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'FAILED'
  created_at: string
  updated_at?: string
}

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

export interface MeetingChatRequest {
  message: string
  history?: ChatMessage[]
}

export interface MeetingChatResponse {
  meeting_id: string
  reply: string
  context: Record<string, any>
}

export interface JobStatusResponse {
  meeting_id: string
  status: 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'FAILED'
  message: string
}

export interface MeetingDetailsResponse extends MeetingResponse {
  transcript?: string
  summary?: string
  key_points?: string
  action_items?: string
  sentiment?: string
  tags?: string
  knowledge_graph?: string
}

export interface SearchResult {
  content: string
  metadata: Record<string, any>
  distance: number
}

export interface SearchResponse {
  query: string
  results: SearchResult[]
}

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message)
    this.name = 'ApiError'
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }))
    throw new ApiError(response.status, errorData.detail || 'Request failed')
  }
  return response.json()
}

export const api = {
  // Upload meeting file
  async uploadMeeting(file: File): Promise<MeetingResponse> {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await fetch(`${API_BASE_URL}/meetings/upload`, {
      method: 'POST',
      body: formData,
    })
    
    return handleResponse<MeetingResponse>(response)
  },

  // List meetings with optional status filter
  async listMeetings(params: { limit?: number; status?: MeetingResponse['status'] } = {}): Promise<MeetingResponse[]> {
    const searchParams = new URLSearchParams()
    if (params.limit) {
      searchParams.set('limit', params.limit.toString())
    }
    if (params.status) {
      searchParams.set('status', params.status)
    }

    const url = searchParams.toString()
      ? `${API_BASE_URL}/meetings?${searchParams.toString()}`
      : `${API_BASE_URL}/meetings`

    const response = await fetch(url)
    return handleResponse<MeetingResponse[]>(response)
  },

  // Get meeting status
  async getMeetingStatus(meetingId: string): Promise<JobStatusResponse> {
    const response = await fetch(`${API_BASE_URL}/meetings/${meetingId}/status`)
    return handleResponse<JobStatusResponse>(response)
  },

  // Get meeting details
  async getMeetingDetails(meetingId: string): Promise<MeetingDetailsResponse> {
    const response = await fetch(`${API_BASE_URL}/meetings/${meetingId}`)
    return handleResponse<MeetingDetailsResponse>(response)
  },

  // Search meetings
  async searchMeetings(query: string, topK: number = 5): Promise<SearchResponse> {
    const params = new URLSearchParams({ query, top_k: topK.toString() })
    const response = await fetch(`${API_BASE_URL}/search?${params}`)
    return handleResponse<SearchResponse>(response)
  },

  // Health check
  async healthCheck(): Promise<{ status: string; service: string }> {
    const response = await fetch(`${API_BASE_URL.replace('/api/v1', '')}/health`)
    return handleResponse<{ status: string; service: string }>(response)
  },

  // Readiness check
  async readinessCheck(): Promise<{ status: string; checks: Record<string, string> }> {
    const response = await fetch(`${API_BASE_URL.replace('/api/v1', '')}/ready`)
    return handleResponse<{ status: string; checks: Record<string, string> }>(response)
  },

  async chatWithMeeting(meetingId: string, payload: MeetingChatRequest): Promise<MeetingChatResponse> {
    const response = await fetch(`${API_BASE_URL}/meetings/${meetingId}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    })
    return handleResponse<MeetingChatResponse>(response)
  },
}

export { ApiError }
