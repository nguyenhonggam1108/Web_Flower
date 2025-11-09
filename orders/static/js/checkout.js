document.addEventListener("DOMContentLoaded", function () {
  const pickupBtn = document.getElementById("pickup-btn");
  const form = pickupBtn ? pickupBtn.closest("form") : null;
  const shippingAddr = document.getElementById("shipping_address");
  const sameAddress = document.getElementById("same_address");
  const customerAddr = document.getElementById("customer_address");

  // ✅ Xử lý checkbox “Dùng lại địa chỉ”
  if (sameAddress && customerAddr && shippingAddr) {
    sameAddress.addEventListener("change", function () {
      if (this.checked) {
        shippingAddr.value = customerAddr.value;
        shippingAddr.readOnly = true;
      } else {
        shippingAddr.readOnly = false;
      }
    });

    customerAddr.addEventListener("input", function () {
      if (sameAddress.checked) shippingAddr.value = this.value;
    });
  }
// ✅ Nút “Nhận hàng tại cửa hàng”
      if (pickupBtn && form) {
      pickupBtn.addEventListener("click", function () {
        if (shippingAddr) {
          shippingAddr.value = "";
          shippingAddr.removeAttribute("required");
          shippingAddr.closest(".mb-3").style.display = "none";
        }
        // Không cần form.submit() — để form tự submit
      });
    }

// Khi người dùng reload lại hoặc bấm chọn "Đặt hàng giao tận nơi", hiện lại ô địa chỉ
    const deliveryBtn = document.querySelector('button[name="order_type"][value="delivery"]');
    if (deliveryBtn) {
      deliveryBtn.addEventListener("click", function () {
        if (shippingAddr) {
          shippingAddr.closest(".mb-3").style.display = "block";
          shippingAddr.setAttribute("required", "true");
        }
      });
    }

  // ✅ Xử lý chọn mã khuyến mãi
  const coupons = document.querySelectorAll(".coupon-card");
  const subtotalEl = document.getElementById("subtotal");
  const discountRow = document.getElementById("discount-row");
  const discountEl = document.getElementById("discount-amount");
  const finalTotalEl = document.getElementById("final-total");

  if (!subtotalEl || !coupons.length) return;

  let subtotal = parseInt(subtotalEl.innerText.replace(/[^\d]/g, ""));
  let currentDiscount = 0;

  coupons.forEach((coupon) => {
    coupon.addEventListener("click", () => {
      // Bỏ chọn các mã khác
      coupons.forEach((c) => c.classList.remove("selected"));
      coupon.classList.add("selected");

      // Lấy giá trị giảm
      const badge = coupon.querySelector(".badge").innerText;
      let discountValue = 0;

      if (badge.includes("%")) {
        const percent = parseFloat(badge);
        currentDiscount = Math.round(subtotal * percent / 100);
      } else {
        discountValue = parseInt(badge.replace(/[^\d]/g, ""));
        currentDiscount = discountValue;
      }

      // Hiển thị kết quả
      discountEl.innerText = `-₫${currentDiscount.toLocaleString()}`;
      discountRow.style.display = "flex";
      finalTotalEl.innerText = `₫${(subtotal - currentDiscount).toLocaleString()}`;
    });
  });
});
