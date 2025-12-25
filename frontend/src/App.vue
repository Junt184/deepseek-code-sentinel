<template>
  <div class="app-container">
    <header class="header">
      <div class="logo">🛡️ DeepSeek Code Sentinel</div>
      <button 
        class="audit-btn" 
        @click="store.analyzeCode"
        :disabled="store.isAnalyzing"
      >
        {{ store.isAnalyzing ? '审计中...' : '开始审计' }}
      </button>
    </header>
    
    <main class="main-content">
      <div class="editor-pane">
        <CodeEditor />
      </div>
      <div class="report-pane">
        <AuditReport />
      </div>
    </main>
  </div>
</template>

<script setup>
import CodeEditor from './components/CodeEditor.vue'
import AuditReport from './components/AuditReport.vue'
import { useAuditStore } from './stores/audit'

const store = useAuditStore()
</script>

<style>
html, body, #app {
  margin: 0;
  padding: 0;
  height: 100%;
  width: 100%;
  background: #1e1e1e;
  color: #fff;
}

.app-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.header {
  height: 60px;
  background: #252526;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  border-bottom: 1px solid #333;
}

.logo {
  font-weight: bold;
  font-size: 1.2rem;
}

.audit-btn {
  background: #007acc;
  color: white;
  border: none;
  padding: 8px 20px;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
}

.audit-btn:disabled {
  background: #444;
  cursor: not-allowed;
}

.main-content {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.editor-pane {
  flex: 1;
  border-right: 1px solid #333;
}

.report-pane {
  flex: 1;
  overflow-y: auto;
}
</style>
