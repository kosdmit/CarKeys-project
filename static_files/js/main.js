// Enable bootstrap tooltips
const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]')
const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl))


// Function to get the CSRF token from the cookie
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
          const cookie = cookies[i].trim();
          if (cookie.substring(0, name.length + 1) === (name + '=')) {
              cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
              break;
          }
      }
  }
  return cookieValue;
}


// Get the CSRF token from the cookie
const csrftoken = getCookie('csrftoken');


// Buy button for goods
// TODO: optimize this function
let priceListModal = new bootstrap.Modal(
  document.getElementById('price-list-modal')
);
$("button.order-button").each(function () {
  let objId = $(this).data('obj-id');
  let orderButton = $('#order-button-' + objId)
  let orderButtonModal = $('#order-button-modal-' + objId)
  let processingButton = $('#process-button-' + objId)
  let processingButtonModal = $('#process-button-modal-' + objId)
  let successButton = $('#success-button-' + objId)
  let successButtonModal = $('#success-button-modal-' + objId)
  let modal
  try {
    modal = new bootstrap.Modal(
      document.getElementById('detail-view-modal-' + objId)
    );
  } catch (error) {
    modal = priceListModal
  }
  $(this).click(function () {
    orderButton.hide()
    orderButtonModal.hide()
    processingButton.show()
    processingButtonModal.show()
    $.ajax({
      type: 'POST',
      headers: {'X-CSRFToken': csrftoken},
      url: '/goods/order_create/',
      data: {
        'obj_id': objId,
        'obj_type': $(this).data('obj-type'),
      },
      success: async function (response) {
        if (response.ok === true) {
          processingButton.hide()
          processingButtonModal.hide()
          successButton.show()
          successButtonModal.show()
          await new Promise(r => setTimeout(r, 1300));
          modal.hide();
          if (response.next === 'get-contacts-modal') {
            let getContactsModal = new bootstrap.Modal(document.getElementById('get-contacts-modal'));
            getContactsModal.show();
          } else if (response.next === 'success-modal') {
            let successModal = new bootstrap.Modal(document.getElementById('success-modal'));
            successModal.show();
          }

        } else {
          //  TODO
        }

      }
    });
  });
});


// Open modal if URL param exists
window.addEventListener('load', function() {
  let urlParams = new URLSearchParams(window.location.search);
  let modalId = urlParams.get('modal_id');

  if (modalId) {
    let modal = new bootstrap.Modal(document.getElementById(modalId));
    let modalDom = document.getElementById(modalId);
    modalDom.classList.remove('fade')
    modal.show();
    setTimeout(function() {
      modalDom.classList.add('fade')
    }, 1000);

  }
});


//Clear url parameters then modals are hidden
const modals = document.querySelectorAll('.modal')
for (let i = 0 ; i < modals.length; i++) {
  modals[i].addEventListener('hide.bs.modal', event => {
    let url = new URL(window.location.href);
    url.searchParams.delete('modal_id')
    window.history.replaceState({}, document.title, url.toString());
  })
  modals[i].addEventListener('show.bs.modal', event => {
    let urlParams = new URLSearchParams(window.location.search);
    if (!urlParams.has('modal_id')) {
      addUrlParam('modal_id', modals[i].getAttribute('id'))
    }
  })
}


function addUrlParam(key, value) {
    var url = new URL(window.location.href);
    url.searchParams.append(key, value);

    window.history.pushState({}, '', url.toString());
}


// Fix for success modal close button
$('#success-modal button[data-bs-dismiss="modal"]').click(function () {
  const modal = new bootstrap.Modal(document.getElementById('success-modal'))
  modal.hide()
  let modalDom = document.getElementById('success-modal')
  modalDom.style = ['display: none;']
  document.body.classList.remove('modal-open');  // allows body to scroll again
  document.body.removeAttribute('style')
  let backdrop = document.getElementsByClassName('modal-backdrop'); // gets the modal backdrop
  document.body.removeChild(backdrop[0]);  // removes the modal backdrop
  console.log('Try to close modal')
})
