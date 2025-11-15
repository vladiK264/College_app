document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("loginForm");
  const error = document.getElementById("loginError");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const data = {
      username: form.username.value,
      password: form.password.value
    };

    const res = await fetch("/auth", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data)
    });

    if (res.ok) {
      window.location.href = "/";
    } else {
      error.style.display = "block";
    }
  });
});