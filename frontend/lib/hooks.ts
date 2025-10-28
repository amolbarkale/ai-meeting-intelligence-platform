import { useState, useEffect, useCallback } from 'react'
import { api, MeetingResponse, MeetingDetailsResponse, JobStatusResponse, ApiError } from '@/lib/api'

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
