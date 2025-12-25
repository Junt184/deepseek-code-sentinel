<template>
  <div class="audit-report">
    <div v-if="store.isAnalyzing" class="status-bar analyzing">
      <span class="loader"></span> 正在深度审计中...
    </div>
    
    <div v-if="store.error" class="status-bar error">
      ⚠️ {{ store.error }}
    </div>

    <!-- Live Stream Output (while analyzing) -->
    <div v-if="store.isAnalyzing && !store.report" class="stream-output">
      <pre>{{ store.streamText }}</pre>
    </div>

    <!-- Final Report -->
    <div v-if="store.report" class="report-content">
      <div class="summary-card">
        <h3>🛡️ 审计总结</h3>
        <p>{{ store.report.summary }}</p>
      </div>

      <div class="vuln-list">
        <div 
          v-for="(vuln, index) in store.report.vulnerabilities" 
          :key="index"
          :class="['vuln-card', vuln.severity]"
        >
          <div class="vuln-header">
            <span class="badge">{{ vuln.severity }}</span>
            <span class="line-num">Line {{ vuln.line }}</span>
          </div>
          <p class="description">{{ vuln.description }}</p>
          <div class="suggestion">
            <strong>💡 修复建议:</strong>
            <p>{{ vuln.suggestion }}</p>
          </div>
        </div>
      </div>
    </div>

    <div v-if="!store.isAnalyzing && !store.report" class="placeholder">
      <p>点击“开始审计”以查看结果</p>
    </div>
  </div>
</template>

<script setup>
import { useAuditStore } from '../stores/audit'

const store = useAuditStore()
</script>

<style scoped>
.audit-report {
  padding: 20px;
  height: 100%;
  overflow-y: auto;
  background: #1e1e1e;
  color: #d4d4d4;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.status-bar {
  padding: 10px;
  margin-bottom: 20px;
  border-radius: 4px;
}
.analyzing { background: #2d2d2d; color: #61dafb; }
.error { background: #3e1b1b; color: #ff6b6b; }

.stream-output pre {
  white-space: pre-wrap;
  color: #888;
  font-size: 0.9em;
}

.summary-card {
  background: #252526;
  padding: 15px;
  border-radius: 6px;
  margin-bottom: 20px;
  border-left: 4px solid #61dafb;
}

.vuln-card {
  background: #252526;
  margin-bottom: 15px;
  padding: 15px;
  border-radius: 6px;
  border: 1px solid #333;
}

.vuln-card.high { border-left: 4px solid #ff4d4f; }
.vuln-card.medium { border-left: 4px solid #faad14; }
.vuln-card.low { border-left: 4px solid #52c41a; }

.badge {
  text-transform: uppercase;
  font-weight: bold;
  font-size: 0.8em;
  padding: 2px 6px;
  border-radius: 3px;
  margin-right: 10px;
}
.high .badge { background: #ff4d4f; color: white; }
.medium .badge { background: #faad14; color: black; }

.suggestion {
  background: #1e1e1e;
  padding: 10px;
  margin-top: 10px;
  border-radius: 4px;
  font-size: 0.9em;
}
</style>
