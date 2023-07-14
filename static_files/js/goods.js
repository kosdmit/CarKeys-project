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
var getContactsModal = new bootstrap.Modal(document.getElementById('get-contacts-modal'));
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
      url: '/goods/send_message/',
      data: {
        'obj_id': objId,
        'obj_type': 'Goods',
        'message_type': 'preorder',
      },
      success: async function (response) {
        if (response.ok == true) {
          processingButton.hide();
          successButton.show();
          await new Promise(r => setTimeout(r, 1300));
          detailViewModal.hide();
          getContactsModal.show();
        } else {
          //  TODO
        }

      }
    });
  });
});
