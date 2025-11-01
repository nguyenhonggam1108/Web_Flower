document.addEventListener("DOMContentLoaded", function () {
  const hearts = document.querySelectorAll(".bookmark-heart");

  // Kiểm tra & đánh dấu các sản phẩm đã yêu thích
  hearts.forEach(heart => {
    const productId = heart.dataset.productId;
    fetch(`/wishlist/status/${productId}/`, { credentials: "include" })
      .then(res => res.json())
      .then(data => {
        if (data.liked) heart.classList.add("liked");
      });

    // Khi click trái tim
    heart.addEventListener("click", function () {
      fetch("/wishlist/toggle/", {
        method: "POST",
        credentials: "include",
        headers: {
          "X-CSRFToken": getCookie("csrftoken"),
          "Content-Type": "application/x-www-form-urlencoded"
        },
        body: `product_id=${productId}`
      })
      .then(res => res.json())
      .then(data => {
        if (data.status === "added") {
          heart.classList.add("liked");
        } else {
          heart.classList.remove("liked");
        }
      });
    });
  });

  // Lấy CSRF token
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
      const cookies = document.cookie.split(";");
      for (let cookie of cookies) {
        cookie = cookie.trim();
        if (cookie.startsWith(name + "=")) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
});
