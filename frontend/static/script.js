document.getElementById("teacherForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const formData = new FormData(e.target);
  const teacher = Object.fromEntries(formData.entries());

  const response = await fetch("/teachers", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(teacher),
  });

  if (response.ok) {
    loadTeachers();
    e.target.reset();
  }
});

async function loadTeachers() {
  const response = await fetch("/teachers");
  const teachers = await response.json();
  const list = document.getElementById("teacherList");
  list.innerHTML = "";
  teachers.forEach((t) => {
    const li = document.createElement("li");
    li.textContent = `${t.name} — ${t.specialization}, ${t.qualification}, макс: ${t.max_hours} ч.`;
    list.appendChild(li);
  });
}

loadTeachers();

document.getElementById("distributeBtn").onclick = () => fetch("/distribute", { method: "POST" });
document.getElementById("assignBtn").onclick = () => fetch("/assign_load", { method: "POST" });
document.getElementById("removeLoadBtn").onclick = () => fetch("/remove_load", { method: "POST" });
document.getElementById("checkOverloadBtn").onclick = () => fetch("/check_overload");
document.getElementById("reserveBtn").onclick = () => fetch("/assign_from_reserve", { method: "POST" });

document.getElementById("currentReportBtn").onclick = async () => {
  const res = await fetch("/report/current");
  const data = await res.json();
  alert(data.report);
};

document.getElementById("semesterReportBtn").onclick = async () => {
  const res = await fetch("/report/semester");
  const data = await res.json();
  alert(data.report);
};