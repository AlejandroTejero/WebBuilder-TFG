# 🎨 Guía de Componentes Visuales - WebBuilder Wizard

## Sistema de Diseño

### Paleta de Colores

```css
:root {
  /* Primarios */
  --color-primary: #2563eb;        /* Azul para acciones principales */
  --color-primary-light: #60a5fa;
  --color-primary-dark: #1e40af;
  
  /* Estados */
  --color-success: #10b981;        /* Verde para completado */
  --color-warning: #f59e0b;        /* Naranja para warnings */
  --color-error: #ef4444;          /* Rojo para errores */
  --color-info: #3b82f6;           /* Azul claro para info */
  
  /* Neutrales */
  --color-gray-50: #f9fafb;
  --color-gray-100: #f3f4f6;
  --color-gray-200: #e5e7eb;
  --color-gray-300: #d1d5db;
  --color-gray-400: #9ca3af;
  --color-gray-500: #6b7280;
  --color-gray-600: #4b5563;
  --color-gray-700: #374151;
  --color-gray-800: #1f2937;
  --color-gray-900: #111827;
  
  /* Backgrounds */
  --bg-page: #ffffff;
  --bg-sidebar: var(--color-gray-50);
  --bg-card: #ffffff;
  --bg-hover: var(--color-gray-100);
  
  /* Borders */
  --border-color: var(--color-gray-200);
  --border-radius: 8px;
  --border-radius-lg: 12px;
  --border-radius-sm: 4px;
  
  /* Shadows */
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  
  /* Typography */
  --font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  --font-mono: "SF Mono", Monaco, "Cascadia Code", monospace;
  
  /* Spacing */
  --spacing-xs: 0.25rem;   /* 4px */
  --spacing-sm: 0.5rem;    /* 8px */
  --spacing-md: 1rem;      /* 16px */
  --spacing-lg: 1.5rem;    /* 24px */
  --spacing-xl: 2rem;      /* 32px */
  --spacing-2xl: 3rem;     /* 48px */
  
  /* Transitions */
  --transition-fast: 150ms ease;
  --transition-base: 200ms ease;
  --transition-slow: 300ms ease;
}
```

---

## Componentes del Wizard

### 1. Wizard Header

```css
.wizard-header {
  position: sticky;
  top: 0;
  z-index: 100;
  background: var(--bg-page);
  border-bottom: 1px solid var(--border-color);
  padding: var(--spacing-lg) var(--spacing-xl);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--spacing-xl);
}

.wizard-header__project {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  flex: 0 0 auto;
}

.project-name {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--color-gray-900);
  margin: 0;
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--border-radius-sm);
  transition: background var(--transition-fast);
}

.project-name:focus {
  outline: 2px solid var(--color-primary);
  background: var(--color-gray-50);
}

.wizard-header__progress {
  flex: 1;
  max-width: 400px;
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.progress-bar {
  flex: 1;
  height: 8px;
  background: var(--color-gray-200);
  border-radius: 999px;
  overflow: hidden;
  position: relative;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--color-primary), var(--color-primary-light));
  transition: width 400ms cubic-bezier(0.4, 0, 0.2, 1);
}

.progress-label {
  font-size: 0.875rem;
  color: var(--color-gray-600);
  white-space: nowrap;
}
```

**HTML:**
```html
<div class="wizard-header">
  <div class="wizard-header__project">
    <h1 class="project-name" contenteditable="true">Mi Proyecto</h1>
    <button class="edit-icon" aria-label="Editar nombre">
      <svg><!-- icono lápiz --></svg>
    </button>
  </div>
  
  <div class="wizard-header__progress">
    <div class="progress-bar">
      <div class="progress-fill" style="width: 33%"></div>
    </div>
    <span class="progress-label">Paso 2 de 6</span>
  </div>
</div>
```

---

### 2. Wizard Navigation

```css
.wizard-nav {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
  padding: var(--spacing-lg);
}

.wizard-nav__step {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-md);
  background: transparent;
  border: none;
  border-radius: var(--border-radius);
  cursor: pointer;
  transition: all var(--transition-base);
  text-align: left;
  position: relative;
}

.wizard-nav__step::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  background: transparent;
  transition: background var(--transition-base);
}

/* Estados */
.wizard-nav__step[data-state="pending"] {
  opacity: 0.5;
  cursor: not-allowed;
}

.wizard-nav__step[data-state="current"] {
  background: var(--color-primary);
  color: white;
}

.wizard-nav__step[data-state="current"]::before {
  background: var(--color-primary-dark);
}

.wizard-nav__step[data-state="completed"] {
  background: var(--bg-hover);
}

.wizard-nav__step[data-state="completed"]:hover {
  background: var(--color-gray-200);
}

.step-number {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--color-gray-200);
  font-weight: 600;
  font-size: 0.875rem;
  flex-shrink: 0;
}

.wizard-nav__step[data-state="current"] .step-number {
  background: rgba(255, 255, 255, 0.2);
  color: white;
}

.wizard-nav__step[data-state="completed"] .step-number {
  background: var(--color-success);
  color: white;
}

.step-label {
  flex: 1;
  font-size: 0.9375rem;
  font-weight: 500;
}

.step-icon {
  font-size: 1.125rem;
  margin-left: auto;
}
```

**HTML:**
```html
<nav class="wizard-nav">
  <button class="wizard-nav__step" data-step="1" data-state="completed">
    <span class="step-number">1</span>
    <span class="step-label">Fuente</span>
    <span class="step-icon">✓</span>
  </button>
  
  <button class="wizard-nav__step" data-step="2" data-state="current">
    <span class="step-number">2</span>
    <span class="step-label">Contenido</span>
    <span class="step-icon">●</span>
  </button>
  
  <button class="wizard-nav__step" data-step="3" data-state="pending">
    <span class="step-number">3</span>
    <span class="step-label">Páginas</span>
  </button>
  
  <!-- más pasos... -->
</nav>
```

---

### 3. Two-Column Workspace

```css
.wizard-workspace {
  display: grid;
  grid-template-columns: 40% 60%;
  gap: var(--spacing-xl);
  padding: var(--spacing-xl);
  height: calc(100vh - 140px); /* ajustar según header/footer */
}

.workspace-column {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
  overflow: hidden;
}

.workspace-column--data {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-lg);
  padding: var(--spacing-lg);
}

.workspace-column--preview {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-lg);
  padding: var(--spacing-lg);
}

.column-header {
  flex-shrink: 0;
}

.column-header h2 {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--color-gray-900);
  margin: 0 0 var(--spacing-xs) 0;
}

.column-subtitle {
  font-size: 0.875rem;
  color: var(--color-gray-600);
  margin: 0;
}

.column-content {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
}

/* Scrollbar styling */
.column-content::-webkit-scrollbar {
  width: 8px;
}

.column-content::-webkit-scrollbar-track {
  background: var(--color-gray-100);
  border-radius: 999px;
}

.column-content::-webkit-scrollbar-thumb {
  background: var(--color-gray-300);
  border-radius: 999px;
}

.column-content::-webkit-scrollbar-thumb:hover {
  background: var(--color-gray-400);
}

/* Responsive */
@media (max-width: 1024px) {
  .wizard-workspace {
    grid-template-columns: 1fr;
  }
  
  .workspace-column {
    min-height: 400px;
  }
}
```

---

### 4. Field Explorer

```css
.field-explorer {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
  height: 100%;
}

.field-explorer__search {
  position: sticky;
  top: 0;
  z-index: 10;
  background: var(--bg-card);
  padding-bottom: var(--spacing-md);
}

.field-explorer__search input {
  width: 100%;
  padding: var(--spacing-sm) var(--spacing-md);
  padding-left: 2.5rem;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  font-size: 0.9375rem;
  background: var(--bg-page);
  background-image: url('data:image/svg+xml,...'); /* icono lupa */
  background-repeat: no-repeat;
  background-position: 0.75rem center;
  background-size: 1rem;
}

.field-explorer__search input:focus {
  outline: 2px solid var(--color-primary);
  border-color: transparent;
}

.field-explorer__tree {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.field-item {
  background: var(--bg-page);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  padding: var(--spacing-md);
  transition: all var(--transition-base);
  position: relative;
}

.field-item:hover {
  border-color: var(--color-primary-light);
  box-shadow: var(--shadow-sm);
}

.field-item[data-dragging="true"] {
  opacity: 0.5;
  cursor: grabbing;
}

.field-item__header {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-sm);
}

.field-icon {
  font-size: 1.125rem;
  width: 24px;
  text-align: center;
}

.field-name {
  font-family: var(--font-mono);
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-gray-900);
  flex: 1;
}

.field-type {
  font-size: 0.75rem;
  padding: 2px 6px;
  background: var(--color-gray-100);
  border-radius: var(--border-radius-sm);
  color: var(--color-gray-600);
  font-weight: 500;
}

.field-item__examples {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 0.8125rem;
  color: var(--color-gray-600);
  margin-left: 32px;
}

.example {
  font-family: var(--font-mono);
  background: var(--color-gray-50);
  padding: 4px 8px;
  border-radius: var(--border-radius-sm);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.field-item__drag {
  position: absolute;
  top: 50%;
  right: var(--spacing-sm);
  transform: translateY(-50%);
  background: transparent;
  border: none;
  cursor: grab;
  padding: var(--spacing-sm);
  color: var(--color-gray-400);
  font-size: 1.25rem;
  opacity: 0;
  transition: opacity var(--transition-fast);
}

.field-item:hover .field-item__drag {
  opacity: 1;
}

.field-item__drag:active {
  cursor: grabbing;
}
```

---

### 5. Mapping Slot

```css
.mapping-slot {
  background: var(--bg-card);
  border: 2px solid var(--border-color);
  border-radius: var(--border-radius);
  padding: var(--spacing-lg);
  transition: all var(--transition-base);
  position: relative;
}

.mapping-slot[data-state="empty"] {
  border-style: dashed;
  background: var(--color-gray-50);
}

.mapping-slot[data-state="mapped"] {
  border-color: var(--color-success);
  background: rgba(16, 185, 129, 0.05);
}

.mapping-slot[data-state="error"] {
  border-color: var(--color-error);
  background: rgba(239, 68, 68, 0.05);
  animation: shake 0.3s;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-4px); }
  75% { transform: translateX(4px); }
}

.mapping-slot[data-state="warning"] {
  border-color: var(--color-warning);
}

/* Drag over effect */
.mapping-slot[data-drag-over="true"] {
  border-color: var(--color-primary);
  background: rgba(37, 99, 235, 0.05);
  transform: scale(1.02);
}

.slot-label {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-gray-900);
  margin-bottom: var(--spacing-md);
}

.required-badge {
  font-size: 0.75rem;
  padding: 2px 6px;
  background: var(--color-error);
  color: white;
  border-radius: var(--border-radius-sm);
  font-weight: 500;
}

.slot-input {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-md);
}

.slot-select {
  flex: 1;
  padding: var(--spacing-sm) var(--spacing-md);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  font-size: 0.9375rem;
  background: var(--bg-page);
  cursor: pointer;
}

.slot-select:focus {
  outline: 2px solid var(--color-primary);
  border-color: transparent;
}

.slot-suggest {
  padding: var(--spacing-sm) var(--spacing-md);
  background: linear-gradient(135deg, var(--color-primary-light), var(--color-primary));
  color: white;
  border: none;
  border-radius: var(--border-radius);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  white-space: nowrap;
  transition: all var(--transition-base);
}

.slot-suggest:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.slot-preview {
  background: var(--color-gray-50);
  border-radius: var(--border-radius);
  padding: var(--spacing-md);
}

.slot-preview__value {
  font-size: 0.875rem;
  color: var(--color-gray-900);
  margin-bottom: var(--spacing-xs);
  font-style: italic;
}

.slot-preview__path {
  font-size: 0.75rem;
  color: var(--color-gray-600);
}

.slot-preview__path code {
  font-family: var(--font-mono);
  background: var(--color-gray-200);
  padding: 2px 6px;
  border-radius: var(--border-radius-sm);
}

.slot-validation {
  margin-top: var(--spacing-sm);
  font-size: 0.8125rem;
}

.slot-validation--error {
  color: var(--color-error);
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
}

.slot-validation--warning {
  color: var(--color-warning);
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
}
```

---

### 6. Preview Panel

```css
.preview-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.preview-tabs {
  display: flex;
  gap: var(--spacing-xs);
  border-bottom: 2px solid var(--border-color);
  margin-bottom: var(--spacing-lg);
}

.preview-tab {
  padding: var(--spacing-sm) var(--spacing-lg);
  background: transparent;
  border: none;
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
  font-size: 0.9375rem;
  font-weight: 500;
  color: var(--color-gray-600);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.preview-tab:hover {
  color: var(--color-gray-900);
}

.preview-tab[data-active="true"] {
  color: var(--color-primary);
  border-bottom-color: var(--color-primary);
}

.preview-content {
  flex: 1;
  overflow-y: auto;
  padding: var(--spacing-md);
}

.preview-list {
  display: grid;
  gap: var(--spacing-lg);
}

.preview-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  overflow: hidden;
  transition: all var(--transition-base);
}

.preview-card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.card-image {
  width: 100%;
  height: 200px;
  object-fit: cover;
  background: var(--color-gray-100);
}

.card-image-placeholder {
  width: 100%;
  height: 200px;
  background: linear-gradient(135deg, var(--color-gray-100), var(--color-gray-200));
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-gray-500);
  font-size: 0.875rem;
}

.card-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--color-gray-900);
  margin: var(--spacing-md);
  margin-bottom: var(--spacing-sm);
}

.card-description {
  font-size: 0.9375rem;
  color: var(--color-gray-600);
  margin: 0 var(--spacing-md) var(--spacing-md);
  line-height: 1.5;
}

.card-link {
  display: inline-block;
  margin: 0 var(--spacing-md) var(--spacing-md);
  color: var(--color-primary);
  font-size: 0.875rem;
  font-weight: 500;
  text-decoration: none;
  transition: color var(--transition-fast);
}

.card-link:hover {
  color: var(--color-primary-dark);
  text-decoration: underline;
}

.preview-controls {
  display: flex;
  gap: var(--spacing-sm);
  padding: var(--spacing-md);
  border-top: 1px solid var(--border-color);
  background: var(--bg-card);
}

.preview-refresh,
.preview-test {
  flex: 1;
  padding: var(--spacing-sm) var(--spacing-md);
  background: var(--bg-page);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  font-size: 0.875rem;
  cursor: pointer;
  transition: all var(--transition-base);
}

.preview-refresh:hover,
.preview-test:hover {
  background: var(--bg-hover);
  border-color: var(--color-primary);
}
```

---

### 7. Wizard Footer

```css
.wizard-footer {
  position: sticky;
  bottom: 0;
  z-index: 100;
  background: var(--bg-page);
  border-top: 1px solid var(--border-color);
  padding: var(--spacing-lg) var(--spacing-xl);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.footer-actions {
  display: flex;
  gap: var(--spacing-md);
}

.btn {
  padding: var(--spacing-sm) var(--spacing-lg);
  border-radius: var(--border-radius);
  font-size: 0.9375rem;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-base);
  border: 1px solid transparent;
}

.btn-secondary {
  background: var(--bg-page);
  border-color: var(--border-color);
  color: var(--color-gray-700);
}

.btn-secondary:hover {
  background: var(--bg-hover);
  border-color: var(--color-gray-300);
}

.btn-primary {
  background: var(--color-primary);
  color: white;
}

.btn-primary:hover {
  background: var(--color-primary-dark);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn:disabled:hover {
  transform: none;
  box-shadow: none;
}
```

---

### 8. Messages / Alerts

```css
.wb-message {
  padding: var(--spacing-md) var(--spacing-lg);
  border-radius: var(--border-radius);
  border-left: 4px solid;
  margin-bottom: var(--spacing-md);
  display: flex;
  align-items: flex-start;
  gap: var(--spacing-sm);
  animation: slideIn 0.3s ease;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.wb-message--success {
  background: rgba(16, 185, 129, 0.1);
  border-color: var(--color-success);
  color: #065f46;
}

.wb-message--error {
  background: rgba(239, 68, 68, 0.1);
  border-color: var(--color-error);
  color: #991b1b;
}

.wb-message--warning {
  background: rgba(245, 158, 11, 0.1);
  border-color: var(--color-warning);
  color: #92400e;
}

.wb-message--info {
  background: rgba(59, 130, 246, 0.1);
  border-color: var(--color-info);
  color: #1e40af;
}

.message-icon {
  font-size: 1.25rem;
  flex-shrink: 0;
}

.message-content {
  flex: 1;
  font-size: 0.9375rem;
  line-height: 1.5;
}
```

---

## Animaciones y Transiciones

### Entrada de Pasos
```css
.wizard-step {
  animation: fadeIn 0.4s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
```

### Loading States
```css
.loading-spinner {
  display: inline-block;
  width: 20px;
  height: 20px;
  border: 2px solid var(--color-gray-300);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.skeleton {
  background: linear-gradient(
    90deg,
    var(--color-gray-100) 25%,
    var(--color-gray-200) 50%,
    var(--color-gray-100) 75%
  );
  background-size: 200% 100%;
  animation: loading 1.5s ease-in-out infinite;
}

@keyframes loading {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
```

---

## Responsive Design

```css
/* Mobile */
@media (max-width: 640px) {
  .wizard-header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-md);
  }
  
  .wizard-header__progress {
    width: 100%;
    max-width: none;
  }
  
  .wizard-workspace {
    grid-template-columns: 1fr;
    gap: var(--spacing-lg);
    padding: var(--spacing-md);
  }
  
  .wizard-footer {
    flex-direction: column;
    gap: var(--spacing-md);
  }
  
  .footer-actions {
    width: 100%;
  }
  
  .btn {
    flex: 1;
  }
}

/* Tablet */
@media (min-width: 641px) and (max-width: 1024px) {
  .wizard-workspace {
    grid-template-columns: 1fr;
  }
  
  .workspace-column {
    max-height: 500px;
  }
}
```

---

## Dark Mode (Opcional)

```css
@media (prefers-color-scheme: dark) {
  :root {
    --bg-page: #111827;
    --bg-sidebar: #1f2937;
    --bg-card: #1f2937;
    --bg-hover: #374151;
    --border-color: #374151;
    --color-gray-900: #f9fafb;
    --color-gray-800: #f3f4f6;
    --color-gray-700: #e5e7eb;
    --color-gray-600: #d1d5db;
  }
  
  .wizard-nav__step[data-state="current"] {
    background: var(--color-primary-dark);
  }
  
  .field-item {
    background: var(--color-gray-800);
  }
  
  .preview-card {
    background: var(--color-gray-800);
  }
}
```
