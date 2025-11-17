document.addEventListener("DOMContentLoaded", () => {
  console.log("✅ DOM загружен, скрипт активен");

  const overlay = document.getElementById("modalOverlay");
  if (overlay) overlay.style.display = "none";

  loadTeachers();
  setupForm();
  setupButtons();
});

async function loadTeachers() {
  console.log("📥 Загружаем преподавателей...");
  try {
    const response = await fetch("/teachers");
    if (!response.ok) throw new Error("Ошибка загрузки преподавателей");
    const teachers = await response.json();

    const list = document.getElementById("teacherList");
    list.innerHTML = "";

    teachers.forEach((t) => {
      const li = document.createElement("li");

      const name = t.name || "Без имени";
      const text = document.createTextNode(`${name} — ${t.specialization}, ${t.qualification}, макс: ${t.max_hours} ч.`);
      const deleteBtn = createButton("🗑 Удалить", "delete", () => deleteTeacher(t.id));
      const editBtn = createButton("✏️ Изменить", "edit", () => showEditModal(t));

      li.appendChild(text);
      li.appendChild(editBtn);
      li.appendChild(deleteBtn);
      list.appendChild(li);
    });
  } catch (err) {
    console.error("❌ Ошибка в loadTeachers:", err);
    alert("Не удалось загрузить преподавателей");
  }
}

function setupForm() {
  const form = document.getElementById("teacherForm");
  if (!form) {
    console.warn("⚠️ Форма teacherForm не найдена");
    return;
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    console.log("✅ Обработчик формы сработал");

    const formData = new FormData(form);
    const teacher = Object.fromEntries(formData.entries());
    console.log("📤 Добавление преподавателя:", teacher);

    try {
      const response = await fetch("/teachers", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(teacher),
      });

      if (response.ok) {
        form.reset();
        loadTeachers();
      } else {
        const errorText = await response.text();
        console.error("❌ Ошибка при добавлении:", errorText);
        alert("Ошибка при добавлении преподавателя");
      }
    } catch (err) {
      console.error("❌ Сбой при отправке:", err);
      alert("Ошибка сети");
    }
  });
}

function setupButtons() {
  const overlay = document.getElementById("modalOverlay");

  const pageRoutes = {
    distributeBtn: "/distribute.html",
    assignBtn: "/assign.html",
    removeLoadBtn: "/remove.html",
    checkOverloadBtn: "/check.html",
    reserveBtn: "/reserve.html",
    addGroupBtn: "/group_form.html",
  };

  const actions = {
    reportCurrentBtn: async () => {
      const res = await fetch("/report/current");
      const data = await res.json();
      alert(data?.report || "Нет данных");
    },
    reportSemesterBtn: async () => {
      const res = await fetch("/report/semester");
      const data = await res.json();
      alert(data?.report || "Нет данных");
    },
  };

  for (const [id, url] of Object.entries(pageRoutes)) {
    const btn = document.getElementById(id);
    if (btn) {
      btn.addEventListener("click", () => {
        console.log(`🔗 Переход по кнопке ${id} → ${url}`);
        if (overlay) overlay.style.display = "none";
        window.location.href = url;
      });
    }
  }

  for (const [id, handler] of Object.entries(actions)) {
    const btn = document.getElementById(id);
    if (btn) {
      btn.addEventListener("click", async () => {
        console.log(`🖱 Нажата кнопка: ${id}`);
        try {
          await handler();
        } catch (err) {
          console.error(`❌ Ошибка при выполнении ${id}:`, err);
          alert("Ошибка при выполнении действия");
        }
      });
    }
  }
}

async function deleteTeacher(id) {
  console.log("🗑 Удаление преподавателя:", id);
  try {
    const response = await fetch(`/teachers/${id}`, { method: "DELETE" });
    if (response.ok) {
      loadTeachers();
    } else {
      const errorText = await response.text();
      console.error("❌ Ошибка при удалении:", errorText);
      alert("Ошибка при удалении преподавателя");
    }
  } catch (err) {
    console.error("❌ Сбой при удалении:", err);
    alert("Ошибка сети");
  }
}


function showEditModal(teacher) {
  if (!teacher || !teacher.id) {
    console.warn("⚠️ Невалидный объект teacher");
    return;
  }

  console.log("✏️ showEditModal вызван для:", teacher);
  const overlay = document.getElementById("modalOverlay");
  const modal = document.getElementById("modalContent");

  if (!overlay || !modal) {
    console.warn("⚠️ Модальные элементы не найдены");
    return;
  }

  modal.innerHTML = `
    <h3>Редактировать: ${teacher.name}</h3>
    <form id="editForm">
      <input name="specialization" value="${teacher.specialization}" placeholder="Специализация" required />
      <input name="qualification" value="${teacher.qualification}" placeholder="Квалификация" required />
      <input name="max_hours" type="number" value="${teacher.max_hours}" placeholder="Макс. часы" required />
      <button type="submit">💾 Сохранить</button>
      <button type="button" id="cancelEdit">Отмена</button>
    </form>
  `;

  overlay.style.display = "flex";
  console.log("✅ overlay открыт");

  const editForm = document.getElementById("editForm");
  if (editForm) editForm.querySelector("input")?.focus();

  editForm.onsubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData(editForm);
    const updated = Object.fromEntries(formData.entries());
    console.log("💾 Сохраняем изменения:", updated);

    try {
      const response = await fetch(`/teachers/${teacher.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(updated),
      });

      if (response.ok) {
        overlay.style.display = "none";
        loadTeachers();
      } else {
        const errorText = await response.text();
        console.error("❌ Ошибка при обновлении:", errorText);
        alert("Ошибка при обновлении преподавателя");
      }
    } catch (err) {
      console.error("❌ Сбой при обновлении:", err);
      alert("Ошибка сети");
    }
  };

  document.getElementById("cancelEdit").onclick = () => {
    console.log("❎ Отмена редактирования");
    overlay.style.display = "none";
  };
}


function createButton(text, type, onClick) {
  const btn = document.createElement("button");
  btn.className = `btn-action ${type}`;
  btn.textContent = text;
  btn.onclick = onClick;
  return btn;
}