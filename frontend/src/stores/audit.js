import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'

export const useAuditStore = defineStore('audit', () => {
  const code = ref('import os\n\ndef dangerous(user_input):\n    os.system(user_input)')
  const language = ref('python')
  const isAnalyzing = ref(false)
  const report = ref(null)
  const streamText = ref('')
  const error = ref(null)

  // Reset state
  const reset = () => {
    report.value = null
    streamText.value = ''
    error.value = null
  }

  // Analyze code using SSE
  const analyzeCode = async () => {
    if (!code.value.trim()) return

    isAnalyzing.value = true
    reset()

    try {
      const response = await fetch('http://localhost:8000/api/v1/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          code: code.value,
          language: language.value,
          stream: true
        })
      })

      if (!response.ok) {
        throw new Error(`API Error: ${response.statusText}`)
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let accumulatedJson = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const chunk = decoder.decode(value, { stream: true })
        streamText.value += chunk
        accumulatedJson += chunk
      }

      // Try to parse the final JSON
      try {
        report.value = JSON.parse(accumulatedJson)
      } catch (e) {
        console.warn('Final JSON parse failed, might be incomplete:', e)
        // Fallback: show raw text if JSON fails
        report.value = { 
            summary: "Analysis complete but raw output parsing failed.", 
            vulnerabilities: [] 
        }
      }

    } catch (e) {
      error.value = e.message
    } finally {
      isAnalyzing.value = false
    }
  }

  return {
    code,
    language,
    isAnalyzing,
    report,
    streamText,
    error,
    analyzeCode
  }
})
