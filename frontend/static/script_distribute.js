document.addEventListener("DOMContentLoaded", async () => {
  const teacherSelect = document.getElementById("teacherSelect");
  const groupSelect = document.getElementById("groupSelect");
  const assignBtn = document.getElementById("assignBtn");
  const removeBtn = document.getElementById("removeBtn");
  const statusDiv = document.getElementById("status");

  // Загрузка преподавателей
  async function loadTeachers() {
    try {
      const res = await fetch("/teachers");
      const teachers = await res.json();
      teachers.forEach(t => {
        const option = document.createElement("option");
        option.value = t.id;
        option.textContent = `${t.name} (${t.specialization})`;
        teacherSelect.appendChild(option);
      });
    } catch (err) {
      statusDiv.textContent = "❌ Ошибка загрузки преподавателей";
    }
  }

  // Загрузка групп
  async function loadGroups() {
    try {
      const res = await fetch("/groups");
      const groups = await res.json();
      groups.forEach(g => {
        const option = document.createElement("option");
        option.value = g.id;
        option.textContent = `${g.name} (${g.year})`;
        groupSelect.appendChild(option);
      });
    } catch (err) {
      statusDiv.textContent = "❌ Ошибка загрузки групп";
    }
  }

  // Назначение нагрузки
  assignBtn.addEventListener("click", async () => {
    const teacherId = teacherSelect.value;
    const groupId = groupSelect.value;
    if (!teacherId || !groupId) return alert("Выберите преподавателя и группу");

    const res = await fetch("/assign_load", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ teacher_id: teacherId, group_id: groupId })
    });

    const data = await res.json();
    statusDiv.textContent = data.message || "✅ Назначение выполнено";
  });

  // Снятие нагрузки
  removeBtn.addEventListener("click", async () => {
    const teacherId = teacherSelect.value;
    const groupId = groupSelect.value;
    if (!teacherId || !groupId) return alert("Выберите преподавателя и группу");

    const res = await fetch("/remove_load", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ teacher_id: teacherId, group_id: groupId })
    });

    const data = await res.json();
    statusDiv.textContent = data.message || "✅ Снятие выполнено";
  });

  await loadTeachers();
  await loadGroups();
});