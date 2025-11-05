'use client'

import { useState, useRef, useEffect } from 'react'
import { Send, Loader2, FolderOpen } from 'lucide-react'

interface Message {
  role: 'user' | 'assistant'
  content: string
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [sessionId, setSessionId] = useState<string>('')
  const [ws, setWs] = useState<WebSocket | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Auto-scroll to bottom
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Initialize WebSocket connection
  useEffect(() => {
    const websocket = new WebSocket('ws://localhost:8000/api/ws')

    websocket.onopen = () => {
      console.log('WebSocket connected')
    }

    websocket.onmessage = (event) => {
      const data = JSON.parse(event.data)

      if (data.type === 'ack') {
        setSessionId(data.session_id)
      } else if (data.type === 'chunk') {
        setMessages((prev) => {
          const newMessages = [...prev]
          const lastMessage = newMessages[newMessages.length - 1]

          if (lastMessage && lastMessage.role === 'assistant') {
            lastMessage.content += data.content
          } else {
            newMessages.push({
              role: 'assistant',
              content: data.content,
            })
          }

          return newMessages
        })
      } else if (data.type === 'done') {
        setIsLoading(false)
      } else if (data.type === 'error') {
        console.error('WebSocket error:', data.content)
        setIsLoading(false)
        setMessages((prev) => [
          ...prev,
          {
            role: 'assistant',
            content: `Error: ${data.content}`,
          },
        ])
      }
    }

    websocket.onerror = (error) => {
      console.error('WebSocket error:', error)
      setIsLoading(false)
    }

    websocket.onclose = () => {
      console.log('WebSocket disconnected')
    }

    setWs(websocket)

    return () => {
      websocket.close()
    }
  }, [])

  const sendMessage = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!input.trim() || !ws || ws.readyState !== WebSocket.OPEN) {
      return
    }

    const userMessage = input.trim()
    setInput('')
    setIsLoading(true)

    // Add user message to chat
    setMessages((prev) => [
      ...prev,
      {
        role: 'user',
        content: userMessage,
      },
    ])

    // Send message via WebSocket
    ws.send(
      JSON.stringify({
        message: userMessage,
        session_id: sessionId,
      })
    )
  }

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 shadow-md">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center space-x-3">
            <FolderOpen className="w-8 h-8 text-blue-600 dark:text-blue-400" />
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                Google Drive Chat
              </h1>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Talk to your Drive files with AI
              </p>
            </div>
          </div>
        </div>
      </header>

      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto">
        <div className="container mx-auto px-4 py-8 max-w-4xl">
          {messages.length === 0 ? (
            <div className="text-center py-16">
              <FolderOpen className="w-16 h-16 mx-auto mb-4 text-gray-400" />
              <h2 className="text-2xl font-semibold text-gray-700 dark:text-gray-300 mb-2">
                Welcome to Google Drive Chat
              </h2>
              <p className="text-gray-600 dark:text-gray-400 mb-8">
                Ask me anything about your Drive files!
              </p>
              <div className="grid gap-4 max-w-2xl mx-auto">
                <button
                  onClick={() =>
                    setInput('List all my files from Google Drive')
                  }
                  className="p-4 bg-white dark:bg-gray-800 rounded-lg shadow hover:shadow-md transition-shadow text-left"
                >
                  <p className="font-medium text-gray-900 dark:text-white">
                    List all my files
                  </p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    See what's in your Google Drive
                  </p>
                </button>
                <button
                  onClick={() =>
                    setInput('Find all PDF files from the last month')
                  }
                  className="p-4 bg-white dark:bg-gray-800 rounded-lg shadow hover:shadow-md transition-shadow text-left"
                >
                  <p className="font-medium text-gray-900 dark:text-white">
                    Find recent PDFs
                  </p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Search for specific file types
                  </p>
                </button>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              {messages.map((message, index) => (
                <div
                  key={index}
                  className={`flex ${
                    message.role === 'user' ? 'justify-end' : 'justify-start'
                  }`}
                >
                  <div
                    className={`max-w-3xl rounded-lg px-4 py-3 ${
                      message.role === 'user'
                        ? 'bg-blue-600 text-white'
                        : 'bg-white dark:bg-gray-800 text-gray-900 dark:text-white shadow'
                    }`}
                  >
                    <p className="whitespace-pre-wrap">{message.content}</p>
                  </div>
                </div>
              ))}
              {isLoading && (
                <div className="flex justify-start">
                  <div className="bg-white dark:bg-gray-800 rounded-lg px-4 py-3 shadow">
                    <Loader2 className="w-5 h-5 animate-spin text-blue-600" />
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>
      </div>

      {/* Input Form */}
      <div className="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700">
        <div className="container mx-auto px-4 py-4 max-w-4xl">
          <form onSubmit={sendMessage} className="flex space-x-4">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about your Drive files..."
              className="flex-1 px-4 py-3 bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600"
              disabled={isLoading || !ws || ws.readyState !== WebSocket.OPEN}
            />
            <button
              type="submit"
              disabled={!input.trim() || isLoading || !ws || ws.readyState !== WebSocket.OPEN}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-600 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
            >
              {isLoading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <Send className="w-5 h-5" />
              )}
              <span>Send</span>
            </button>
          </form>
          {(!ws || ws.readyState !== WebSocket.OPEN) && (
            <p className="text-sm text-red-600 dark:text-red-400 mt-2">
              Connecting to server...
            </p>
          )}
        </div>
      </div>
    </div>
  )
}
