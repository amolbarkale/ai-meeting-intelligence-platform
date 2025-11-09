import { useState, useEffect, useCallback, useRef } from 'react'
import {
  api,
  MeetingResponse,
  MeetingDetailsResponse,
  JobStatusResponse,
  ApiError,
  ChatMessage,
  MeetingChatResponse,
  GraphContextResponse,
} from '@/lib/api'

const ACTIVE_POLL_INTERVAL = 3000
const IDLE_POLL_INTERVAL = 10000

export interface MeetingChatTurn extends ChatMessage {
  id: string
}

export function useMeetingUpload() {
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [uploadedMeeting, setUploadedMeeting] = useState<MeetingResponse | null>(null)

  const uploadFile = useCallback(async (file: File) => {
    setIsLoading(true)
    setError(null)
    setUploadedMeeting(null)

    try {
      const result = await api.uploadMeeting(file)
      setUploadedMeeting(result)
      return result
    } catch (err) {
      const errorMessage = err instanceof ApiError 
        ? err.message 
        : 'Upload failed. Please try again.'
      setError(errorMessage)
      throw err
    } finally {
      setIsLoading(false)
    }
  }, [])

  const reset = useCallback(() => {
    setError(null)
    setUploadedMeeting(null)
  }, [])

  return {
    uploadFile,
    isLoading,
    error,
    uploadedMeeting,
    reset
  }
}

export function useMeetingsList(limit: number = 20) {
  const [meetings, setMeetings] = useState<MeetingResponse[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [pollInterval, setPollInterval] = useState(IDLE_POLL_INTERVAL)
  const isMountedRef = useRef(true)

  useEffect(() => {
    return () => {
      isMountedRef.current = false
    }
  }, [])

  const fetchMeetings = useCallback(async (showSpinner: boolean = false) => {
    if (showSpinner) {
      setIsLoading(true)
    }

    try {
      const result = await api.listMeetings({ limit })
      if (!isMountedRef.current) return

      setMeetings(result)
      setError(null)

      const hasActive = result.some((meeting) => meeting.status === 'PENDING' || meeting.status === 'PROCESSING')
      setPollInterval(hasActive ? ACTIVE_POLL_INTERVAL : IDLE_POLL_INTERVAL)
    } catch (err) {
      if (!isMountedRef.current) return

      const errorMessage = err instanceof ApiError ? err.message : 'Failed to load meetings'
      setError(errorMessage)
    } finally {
      if (showSpinner && isMountedRef.current) {
        setIsLoading(false)
      }
    }
  }, [limit])

  useEffect(() => {
    fetchMeetings(true)
  }, [fetchMeetings])

  useEffect(() => {
    const interval = setInterval(() => {
      fetchMeetings(false)
    }, pollInterval)

    return () => clearInterval(interval)
  }, [fetchMeetings, pollInterval])

  const refresh = useCallback(() => {
    fetchMeetings(true)
  }, [fetchMeetings])

  return {
    meetings,
    isLoading,
    error,
    refresh
  }
}

export function useMeetingStatus(meetingId: string | null) {
  const [status, setStatus] = useState<JobStatusResponse | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchStatus = useCallback(async () => {
    if (!meetingId) return

    try {
      setIsLoading(true)
      const result = await api.getMeetingStatus(meetingId)
      setStatus(result)
      setError(null)
    } catch (err) {
      const errorMessage = err instanceof ApiError 
        ? err.message 
        : 'Failed to fetch status'
      setError(errorMessage)
    } finally {
      setIsLoading(false)
    }
  }, [meetingId])

  useEffect(() => {
    fetchStatus()
    
    // Poll for status updates if processing
    const interval = setInterval(() => {
      if (status?.status === 'PROCESSING' || status?.status === 'PENDING') {
        fetchStatus()
      }
    }, 2000)

    return () => clearInterval(interval)
  }, [fetchStatus, status?.status])

  return {
    status,
    isLoading,
    error,
    refetch: fetchStatus
  }
}

export function useMeetingDetails(meetingId: string | null) {
  const [meeting, setMeeting] = useState<MeetingDetailsResponse | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchDetails = useCallback(async () => {
    if (!meetingId) return

    try {
      setIsLoading(true)
      const result = await api.getMeetingDetails(meetingId)
      setMeeting(result)
      setError(null)
    } catch (err) {
      const errorMessage = err instanceof ApiError 
        ? err.message 
        : 'Failed to fetch meeting details'
      setError(errorMessage)
    } finally {
      setIsLoading(false)
    }
  }, [meetingId])

  useEffect(() => {
    fetchDetails()
  }, [fetchDetails])

  return {
    meeting,
    isLoading,
    error,
    refetch: fetchDetails
  }
}

export function useMeetingChat(meetingId: string | null) {
  const [messages, setMessages] = useState<MeetingChatTurn[]>([])
  const [context, setContext] = useState<MeetingChatResponse['context'] | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const messagesRef = useRef<MeetingChatTurn[]>([])

  useEffect(() => {
    messagesRef.current = messages
  }, [messages])

  useEffect(() => {
    setMessages([])
    setContext(null)
    setError(null)
    messagesRef.current = []
  }, [meetingId])

  const sendMessage = useCallback(
    async (content: string) => {
      if (!meetingId || !content.trim()) return

      const historyPayload: ChatMessage[] = messagesRef.current.map(({ role, content }) => ({
        role,
        content,
      }))

      const userMessage: MeetingChatTurn = {
        id: `${Date.now()}-user`,
        role: 'user',
        content: content.trim(),
      }

      const optimisticMessages = [...messagesRef.current, userMessage]
      messagesRef.current = optimisticMessages
      setMessages(optimisticMessages)
      setIsLoading(true)
      setError(null)

      try {
        const response = await api.chatWithMeeting(meetingId, {
          message: content.trim(),
          history: historyPayload,
        })
        setContext(response.context)

        const assistantMessage: MeetingChatTurn = {
          id: `${Date.now()}-assistant`,
          role: 'assistant',
          content: response.reply,
        }

        const updatedMessages = [...messagesRef.current, assistantMessage]
        messagesRef.current = updatedMessages
        setMessages(updatedMessages)
      } catch (err) {
        const errorMessage = err instanceof ApiError ? err.message : 'Chat request failed'
        setError(errorMessage)
        // rollback optimistic user message
        const rollback = messagesRef.current.filter((msg) => msg.id !== userMessage.id)
        messagesRef.current = rollback
        setMessages(rollback)
      } finally {
        setIsLoading(false)
      }
    },
    [meetingId]
  )

  const resetChat = useCallback(() => {
    messagesRef.current = []
    setMessages([])
    setContext(null)
    setError(null)
  }, [])

  return {
    messages,
    context,
    isLoading,
    error,
    sendMessage,
    resetChat,
  }
}

export function useMeetingGraphContext(meetingId: string | null) {
  const [context, setContext] = useState<GraphContextResponse | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchContext = useCallback(async () => {
    if (!meetingId) {
      setContext(null)
      setError(null)
      setIsLoading(false)
      return
    }
    setIsLoading(true)
    setError(null)
    try {
      const response = await api.getMeetingGraphContext(meetingId)
      setContext(response)
    } catch (err) {
      const message = err instanceof ApiError ? err.message : 'Failed to load graph context'
      setError(message)
      setContext(null)
    } finally {
      setIsLoading(false)
    }
  }, [meetingId])

  useEffect(() => {
    fetchContext()
  }, [fetchContext])

  return {
    context,
    isLoading,
    error,
    refresh: fetchContext,
  }
}

export function useMeetingSearch() {
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const search = useCallback(async (query: string, topK: number = 5) => {
    if (!query.trim()) return { query, results: [] }

    setIsLoading(true)
    setError(null)

    try {
      const result = await api.searchMeetings(query, topK)
      return result
    } catch (err) {
      const errorMessage = err instanceof ApiError 
        ? err.message 
        : 'Search failed'
      setError(errorMessage)
      return { query, results: [] }
    } finally {
      setIsLoading(false)
    }
  }, [])

  return {
    search,
    isLoading,
    error
  }
}
