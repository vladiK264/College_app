document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("teacherForm");
  const list = document.getElementById("teacherList");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const data = {
      name: form.name.value.trim(),
      specialization: form.specialization.value.trim(),
      qualification: form.qualification.value.trim(),
      max_hours: parseInt(form.max_hours.value) || 0
    };

    try {
      const res = await fetch("/teachers", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
      });

      if (!res.ok) throw new Error("Ошибка при добавлении");

      form.reset();
      await loadTeachers();
    } catch (err) {
      alert("Не удалось добавить преподавателя: " + err.message);
    }
  });

  async function loadTeachers() {
    try {
      const res = await fetch("/teachers");
      if (!res.ok) throw new Error("Ошибка при загрузке списка");

      const teachers = await res.json();
      list.innerHTML = "";

      teachers.sort((a, b) => a.name.localeCompare(b.name));

      teachers.forEach(t => {
        const li = document.createElement("li");
        li.textContent = `${t.name} (${t.specialization}) `;

        const delBtn = document.createElement("button");
        delBtn.textContent = "Удалить";
        delBtn.style.marginLeft = "10px";
        delBtn.onclick = async () => {
          if (confirm(`Удалить ${t.name}?`)) {
            await fetch(`/teachers/${t.id}`, { method: "DELETE" });
            await loadTeachers();
          }
        };

        li.appendChild(delBtn);
        list.appendChild(li);
      });
    } catch (err) {
      list.innerHTML = "<li style='color:red;'>Ошибка загрузки списка</li>";
      console.error(err);
    }
  }

  loadTeachers();
});

document.getElementById("distributeBtn").addEventListener("click", async () => {
  const res = await fetch("/distribute", { method: "POST" });
  if (res.ok) {
    alert("✅ Распределение выполнено!");
  } else {
    alert("❌ Ошибка при распределении.");
  }
});