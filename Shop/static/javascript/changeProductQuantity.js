function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

function get_curr_prod_quantity() {
  const quantity = document.getElementById('product_quantity').value
  const csrftoken = getCookie('csrftoken')
  const c_p_in_cart_id = document.getElementById('cart_prod_in_cart_id').value         
          
  return {
    cart_prod_in_cart_id: c_p_in_cart_id,
    quantity: quantity,
    csrfmiddlewaretoken: csrftoken
  }
}

function set_new_prod_quantity(full_price, total_products, final_price) {
  document.getElementById('product_full_price').innerText = full_price;
  document.getElementById('total_products').innerText = total_products;
  document.getElementById('cart_total_products').innerText = total_products;
  document.getElementById('final_price').innerText = final_price;
}


let changeQuantityForm = document.getElementById('change_prod_quantity');
changeQuantityForm.addEventListener('submit', function(e) {
  data = get_curr_prod_quantity();
  form = document.getElementById('change_prod_quantity');

  $.ajax({
    type: form.method,
    url: form.action,
    data: data,

    success: function(data) {
      set_new_prod_quantity(
        data.full_price, 
        data.total_products, 
        data.final_price
      );                 
    },

    error: function(response) {
      alert('ERROR: ', response);
    }
  });

  e.preventDefault();
});

let changeQuantityInpt = document.getElementById('product_quantity');
changeQuantityInpt.addEventListener('click', function(e) {
  data = get_curr_prod_quantity();
  form = document.getElementById('change_prod_quantity');

  $.ajax({
    type: form.method,
    url: form.action,
    data: data,

    success: function(data) {
      set_new_prod_quantity(
        data.full_price, 
        data.total_products, 
        data.final_price
      );                 
    },

    error: function(response) {
      alert('ERROR: ', response);
    }
  });

  event.preventDefault();
})