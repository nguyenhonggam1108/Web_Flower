document.addEventListener('DOMContentLoaded', function () {
    const buttons = document.querySelectorAll('.add-to-cart-btn');
    buttons.forEach(btn => {
        btn.addEventListener('click', function (event) {
            event.preventDefault(); // 🔥 Ngăn trình duyệt chuyển trang
            const productId = this.getAttribute('data-product-id');

            fetch(`/cart/add/${productId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCSRFToken(),
                },
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showToast(data.message);
                } else {
                    showToast('Có lỗi xảy ra!');
                }
            })
            .catch(() => {
                showToast('Không thể kết nối máy chủ.');
            });
        });
    });
});

// Lấy token CSRF trong cookie
function getCSRFToken() {
    const name = 'csrftoken';
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        cookie = cookie.trim();
        if (cookie.startsWith(name + '=')) {
            return cookie.substring(name.length + 1);
        }
    }
    return '';
}

// Tạo toast thông báo
function showToast(message) {
    let toast = document.createElement('div');
    toast.className = 'toast-message';
    toast.innerText = message;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}
