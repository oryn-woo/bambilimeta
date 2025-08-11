
  document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".favorite-btn").forEach(btn => {
      btn.addEventListener("click", async () => {
        const houseId = btn.dataset.houseId;
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        const response = await fetch("{% url 'housing:favorite_toggle' %}", {
          method: "POST",
          headers: {
            "Content-Type": "application/x-www-form-urlencoded",
            "X-CSRFToken": csrftoken
          },
          body: new URLSearchParams({ house_id: houseId })
        });

        if (!response.ok) return;

        const data = await response.json();
        const icon = btn.querySelector("i");

        if (data.is_favorited) {
          icon.classList.remove("bi-heart");
          icon.classList.add("bi-heart-fill", "text-danger");
          btn.dataset.favorited = "true";
        } else {
          icon.classList.remove("bi-heart-fill", "text-danger");
          icon.classList.add("bi-heart");
          btn.dataset.favorited = "false";
        }
      });
    });
  });
