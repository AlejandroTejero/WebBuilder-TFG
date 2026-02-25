/**
 * WebBuilder — Editor de schema (edit.js)
 * Gestiona: drag & drop para reordenar campos,
 *           añadir campos disponibles,
 *           loading overlay al publicar.
 */

// ── DRAG & DROP ──────────────────────────────────────────────────────
(function () {
  const list = document.getElementById('fields-list');
  if (!list) return;

  let dragged = null;

  list.addEventListener('dragstart', e => {
    dragged = e.target.closest('.edit-field-row');
    if (dragged) {
      dragged.classList.add('dragging');
      // Necesario para Firefox
      e.dataTransfer.effectAllowed = 'move';
      e.dataTransfer.setData('text/plain', '');
    }
  });

  list.addEventListener('dragend', () => {
    if (dragged) dragged.classList.remove('dragging');
    dragged = null;
    list.querySelectorAll('.edit-field-row').forEach(r => r.classList.remove('drag-over'));
    renumberFields();
  });

  list.addEventListener('dragover', e => {
    e.preventDefault();
    const target = e.target.closest('.edit-field-row');
    if (target && target !== dragged) {
      list.querySelectorAll('.edit-field-row').forEach(r => r.classList.remove('drag-over'));
      target.classList.add('drag-over');
    }
  });

  list.addEventListener('dragleave', e => {
    const target = e.target.closest('.edit-field-row');
    if (target) target.classList.remove('drag-over');
  });

  list.addEventListener('drop', e => {
    e.preventDefault();
    const target = e.target.closest('.edit-field-row');
    if (target && target !== dragged && dragged) {
      const rows  = [...list.querySelectorAll('.edit-field-row')];
      const dragIdx   = rows.indexOf(dragged);
      const targetIdx = rows.indexOf(target);
      if (dragIdx < targetIdx) {
        target.after(dragged);
      } else {
        target.before(dragged);
      }
    }
  });

  /**
   * Renumera los atributos name de cada fila tras reordenar
   * para que el POST llegue en el orden correcto.
   */
  function renumberFields() {
    list.querySelectorAll('.edit-field-row').forEach((row, i) => {
      row.querySelectorAll('[name]').forEach(el => {
        el.name = el.name.replace(/_\d+$/, `_${i}`);
      });
      const chk = row.querySelector('.edit-checkbox');
      if (chk) {
        chk.id   = `active_${i}`;
        chk.name = `field_active_${i}`;
      }
    });
  }
})();

// ── AÑADIR CAMPO DISPONIBLE ──────────────────────────────────────────
(function () {
  const list = document.getElementById('fields-list');
  if (!list) return;

  document.querySelectorAll('.add-field-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const key = btn.dataset.key;
      const idx = list.querySelectorAll('.edit-field-row').length;

      const row = document.createElement('div');
      row.className   = 'edit-field-row';
      row.draggable   = true;
      row.innerHTML = `
        <span class="edit-field-row__handle" title="Arrastrar para reordenar">⠿</span>
        <div class="edit-field-row__check">
          <input type="checkbox" class="edit-checkbox"
                 name="field_active_${idx}" id="active_${idx}" checked>
        </div>
        <input type="hidden" name="field_key_${idx}" value="${key}">
        <code class="edit-field-row__key">${key}</code>
        <input type="text" class="edit-field-row__label"
               name="field_label_${idx}" value="${key}" placeholder="Etiqueta...">
      `;
      list.appendChild(row);

      // Deshabilitar el chip para no añadir duplicados
      btn.disabled = true;
    });
  });
})();

// ── LOADING OVERLAY AL PUBLICAR ──────────────────────────────────────
function showPublishLoading() {
  const overlay = document.getElementById('loading-overlay');
  if (!overlay) return;

  overlay.classList.add('active');

  const stepIds = ['ls-1', 'ls-2', 'ls-3'];
  const steps   = stepIds.map(id => document.getElementById(id));

  steps.forEach((step, i) => {
    setTimeout(() => {
      if (i > 0 && steps[i - 1]) {
        steps[i - 1].classList.remove('active');
        steps[i - 1].classList.add('done');
      }
      if (step) step.classList.add('active');
    }, i * 3000);
  });
}
