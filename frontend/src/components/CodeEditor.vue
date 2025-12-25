<template>
  <div class="code-editor-container" ref="editorContainer"></div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import * as monaco from 'monaco-editor'
import { useAuditStore } from '../stores/audit'

const store = useAuditStore()
const editorContainer = ref(null)
let editor = null

onMounted(() => {
  editor = monaco.editor.create(editorContainer.value, {
    value: store.code,
    language: 'python',
    theme: 'vs-dark',
    automaticLayout: true,
    minimap: { enabled: false },
    scrollBeyondLastLine: false,
    fontSize: 14
  })

  // Sync content back to store
  editor.onDidChangeModelContent(() => {
    store.code = editor.getValue()
  })

  // Listen to vulnerabilities to add decorations
  watch(() => store.report, (newReport) => {
    if (newReport?.vulnerabilities) {
      const decorations = newReport.vulnerabilities.map(vuln => ({
        range: new monaco.Range(vuln.line, 1, vuln.line, 1),
        options: {
          isWholeLine: true,
          className: 'vuln-decoration-' + vuln.severity.toLowerCase(),
          glyphMarginClassName: 'vuln-glyph-' + vuln.severity.toLowerCase(),
          hoverMessage: { value: `**${vuln.severity.toUpperCase()}**: ${vuln.description}` }
        }
      }))
      
      editor.deltaDecorations([], decorations)
    } else {
        // Clear decorations
        editor.deltaDecorations([], [])
    }
  }, { deep: true })
})

onBeforeUnmount(() => {
  if (editor) {
    editor.dispose()
  }
})
</script>

<style>
.code-editor-container {
  width: 100%;
  height: 100%;
}

/* Decorations */
.vuln-decoration-high {
  background: rgba(255, 0, 0, 0.2);
}
.vuln-decoration-medium {
  background: rgba(255, 165, 0, 0.2);
}
</style>
