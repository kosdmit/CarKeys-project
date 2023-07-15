// Stop propagation for category links in accordion header
const categoryAccordionPanel = document.querySelector('#categoryAccordionPanel')
const accordionHeaderLinks = categoryAccordionPanel.querySelectorAll('.accordion-header a')
for (let i = 0; i < accordionHeaderLinks.length; i++) {
  accordionHeaderLinks[i].addEventListener('click', function (event) {
    event.stopPropagation();
    window.location.href = accordionHeaderLinks[i].getAttribute('href')
  });
}


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
let getContactsModal = new bootstrap.Modal(document.getElementById('get-contacts-modal'));
let successModal = new bootstrap.Modal(document.getElementById('success-modal'));
$("button.order-button").each(function(){
  let processingButton = $(this).next();
  let successButton = processingButton.next();
  let objId = $(this).data('obj-id');
  let detailViewModal = new bootstrap.Modal(
      document.getElementById('detail-view-modal-' + objId)
  );
  $(this).click(function () {
    $(this).hide()
    processingButton.show()
    $.ajax({
      type: 'POST',
      headers: {'X-CSRFToken': csrftoken},
      url: '/goods/order_create/',
      data: {
        'obj_id': objId,
        'obj_type': 'Goods',
        'message_type': 'preorder',
      },
      success: async function (response) {
        if (response.ok === true) {
          processingButton.hide();
          successButton.show();
          await new Promise(r => setTimeout(r, 1300));
          if (response.next === 'get-contacts-modal') {
            detailViewModal.hide();
            getContactsModal.show();
          } else if (response.next === 'success-modal') {
            detailViewModal.hide();
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
    removeUrlParameters()
  })
}

function removeUrlParameters() {
  let urlWithoutParameters = window.location.origin + window.location.pathname;
  window.history.replaceState({}, document.title, urlWithoutParameters);
}


// Fix for success modal close button
$('#success-modal button[data-bs-dismiss="modal"]').click(function () {
  let modal = new bootstrap.Modal(document.getElementById('success-modal'));
  modal.hide()
})