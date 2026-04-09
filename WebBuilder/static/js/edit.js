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


// ── PAGINADOR PREVIEW ─────────────────────────────────────────────────
(function () {
  const items = document.querySelectorAll('.pager-item');
  const dots  = document.querySelectorAll('.pager-dot');
  const label = document.getElementById('pager-label');
  const prev  = document.getElementById('pager-prev');
  const next  = document.getElementById('pager-next');

  if (!items.length) return;

  let cur = 0;
  const total = items.length;

  function render() {
    items.forEach((el, i) => el.classList.toggle('pager-item--active', i === cur));
    dots.forEach((el, i)  => el.classList.toggle('pager-dot--on', i === cur));
    label.textContent = `#${cur + 1} de ${total}`;
    prev.classList.toggle('pager-btn--disabled', cur === 0);
    next.classList.toggle('pager-btn--disabled', cur === total - 1);
  }

  window.pagerNav = function(dir) {
    cur = Math.max(0, Math.min(total - 1, cur + dir));
    render();
  };

  window.pagerGoTo = function(i) {
    cur = i;
    render();
  };

  render();
})();


// ── USUARIOS ─────────────────────────────────────────────────────────
(function () {
  const addBtn  = document.getElementById('users-add-btn');
  const saveBtn = document.getElementById('users-save-btn');
  const list    = document.getElementById('users-list');
  if (!list) return;

  function createUserRow() {
    const tr = document.createElement('tr');
    tr.className = 'site-user-row';
    tr.innerHTML = `
      <td><div class="user-avatar">?</div></td>
      <td><input type="text" class="user-input" placeholder="Usuario"></td>
      <td><input type="password" class="user-input" placeholder="Contraseña"></td>
      <td>
        <select class="user-select">
          <option value="normal">Normal</option>
          <option value="super">Superusuario</option>
        </select>
      </td>
      <td><button class="user-del-btn" type="button" data-user-remove>✕</button></td>
    `;
    const input  = tr.querySelector('input[type="text"]');
    const avatar = tr.querySelector('.user-avatar');
    input.addEventListener('input', () => {
      avatar.textContent = input.value.trim().slice(0, 1).toUpperCase() || '?';
    });
    return tr;
  }

  if (addBtn) addBtn.addEventListener('click', () => list.appendChild(createUserRow()));

  list.addEventListener('click', e => {
    const btn = e.target.closest('[data-user-remove]');
    if (btn) btn.closest('.site-user-row').remove();
  });

  function showFeedback(msg, ok) {
    const el = document.getElementById('users-feedback');
    if (!el) return;
    el.textContent = msg;
    el.style.display = 'block';
    el.style.color = ok ? '#4ade80' : '#f87171';
    setTimeout(() => { el.style.display = 'none'; }, 3000);
  }

  if (saveBtn) saveBtn.addEventListener('click', async () => {
    const rows = list.querySelectorAll('.site-user-row');
    const users = [];
    for (const row of rows) {
      const inputs = row.querySelectorAll('.user-input');
      const select = row.querySelector('.user-select');
      const username = inputs[0].value.trim();
      const password = inputs[1].value.trim();
      if (!username || !password) {
        showFeedback('Todos los usuarios deben tener usuario y contraseña.', false);
        return;
      }
      users.push({ username, password, role: select.value });
    }
    try {
      const res = await fetch(USERS_SAVE_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': CSRF_TOKEN,
        },
        body: JSON.stringify({ users }),
      });
      const data = await res.json();
      if (data.ok) {
        showFeedback(`✔ ${data.saved} usuario(s) guardados.`, true);
      } else {
        showFeedback(`✗ Error: ${data.error}`, false);
      }
    } catch (e) {
      showFeedback('✗ Error de conexión.', false);
    }
  });
})();