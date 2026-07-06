/**
 * Connects this portfolio's frontend to the FastAPI backend.
 * IMPORTANT: change API_BASE_URL below once you deploy your backend
 * (e.g. to Render). While testing locally, leave it as the localhost URL.
 */
const API_BASE_URL = "http://127.0.0.1:8000";

document.addEventListener("DOMContentLoaded", () => {
  registerVisit();
  loadBlogPosts();
  loadTestimonials();
  wireContactForm();
  wireTestimonialForm();
});

/* -------------------- Visitor counter -------------------- */
async function registerVisit() {
  const el = document.getElementById("visit-count");
  if (!el) return;
  try {
    const res = await fetch(`${API_BASE_URL}/api/visit`, { method: "POST" });
    const data = await res.json();
    el.textContent = data.count.toLocaleString();
  } catch (err) {
    el.textContent = "—";
  }
}

/* -------------------- Blog / updates section -------------------- */
async function loadBlogPosts() {
  const container = document.getElementById("blog-posts-container");
  if (!container) return;

  try {
    const res = await fetch(`${API_BASE_URL}/api/blog`);
    const posts = await res.json();

    if (!posts.length) {
      container.innerHTML = `<p class="text-center">No posts yet. Check back soon!</p>`;
      return;
    }

    container.innerHTML = posts
      .map(
        (post) => `
        <div class="col-lg-4 col-md-6 d-flex align-items-stretch" data-aos="fade-up">
          <div class="blog-card">
            ${
              post.cover_image_url
                ? `<img src="${escapeHtml(post.cover_image_url)}" class="img-fluid" alt="">`
                : ""
            }
            <div class="blog-card-body">
              <h4>${escapeHtml(post.title)}</h4>
              <p class="blog-date">${formatDate(post.created_at)}</p>
              <p>${escapeHtml(post.content)}</p>
            </div>
          </div>
        </div>`
      )
      .join("");
  } catch (err) {
    container.innerHTML = `<p class="text-center">Could not load posts right now.</p>`;
  }
}

/* -------------------- Testimonials -------------------- */
async function loadTestimonials() {
  const container = document.getElementById("testimonials-container");
  if (!container) return;

  try {
    const res = await fetch(`${API_BASE_URL}/api/testimonials`);
    const items = await res.json();

    if (!items.length) {
      container.innerHTML = `<p class="text-center">No testimonials yet — be the first!</p>`;
      return;
    }

    container.innerHTML = items
      .map(
        (t) => `
        <div class="col-lg-4 col-md-6" data-aos="fade-up">
          <div class="testimonial-card">
            <p>"${escapeHtml(t.message)}"</p>
            <h5>${escapeHtml(t.name)}</h5>
            ${t.role ? `<span>${escapeHtml(t.role)}</span>` : ""}
          </div>
        </div>`
      )
      .join("");
  } catch (err) {
    container.innerHTML = `<p class="text-center">Could not load testimonials right now.</p>`;
  }
}

function wireTestimonialForm() {
  const form = document.getElementById("testimonial-form");
  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const statusEl = form.querySelector(".form-status");
    statusEl.textContent = "Submitting...";

    const payload = {
      name: form.name.value,
      role: form.role.value || null,
      message: form.message.value,
    };

    try {
      const res = await fetch(`${API_BASE_URL}/api/testimonials`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Something went wrong");
      statusEl.textContent = data.message;
      form.reset();
    } catch (err) {
      statusEl.textContent = "Could not submit right now. Please try again later.";
    }
  });
}

/* -------------------- Contact form -------------------- */
function wireContactForm() {
  const form = document.querySelector(".php-email-form");
  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const loading = form.querySelector(".loading");
    const errorMessage = form.querySelector(".error-message");
    const sentMessage = form.querySelector(".sent-message");

    loading.style.display = "block";
    errorMessage.style.display = "none";
    sentMessage.style.display = "none";

    const payload = {
      name: form.name.value,
      email: form.email.value,
      subject: form.subject.value,
      message: form.message.value,
    };

    try {
      const res = await fetch(`${API_BASE_URL}/api/contact`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Could not send message");

      loading.style.display = "none";
      sentMessage.style.display = "block";
      form.reset();
    } catch (err) {
      loading.style.display = "none";
      errorMessage.textContent = err.message;
      errorMessage.style.display = "block";
    }
  });
}

/* -------------------- Helpers -------------------- */
function formatDate(iso) {
  return new Date(iso).toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}
