let startTitleText = $('head title').text()
let startDescriptionText = $('head [name="description"]').attr('content').trim().replace(/[\n\r\t\s+]/g, " ").replace(/\/|\.\s+/g, ". ")
let startKeywordsText = $('head [name="keywords"]').attr('content').trim().replace(/[\n\r\t\s+]/g, " ")

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


// Ya metrica E-commerce
window.dataLayer = window.dataLayer || [];


// Buy button for goods
// TODO: optimize this function
let priceListModal = new bootstrap.Modal(
  document.getElementById('price-list')
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

    let objType = orderButton.data('obj-type')
    if (objType === 'Goods') {
      pushAddGoodsData(objId);
    } else if (objType === 'Service') {
      pushAddServiceData(objId)
    }


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

    checkGoodsDetailViewOpened()

  }
});


// Open service if URL param exists
window.addEventListener('load', function() {
  let urlParams = new URLSearchParams(window.location.search);
  let serviceId = urlParams.get('service_id');

  if (serviceId) {
    let accordionItem = new bootstrap.Collapse(document.getElementById(serviceId));
    let modalDom = document.getElementById(serviceId);
    modalDom.classList.remove('fade')
    accordionItem.show();
    setTimeout(function() {
      modalDom.classList.add('fade')
    }, 1000);

    // TODO: check ya-commerce for Services
    // checkGoodsDetailViewOpened()

  }
});



//Clear url parameters then modals are hidden
const modals = document.querySelectorAll('.modal')
for (let i = 0 ; i < modals.length; i++) {
  modals[i].addEventListener('hide.bs.modal', event => {
    let url = new URL(window.location.href);
    url.searchParams.delete('modal_id')
    url.searchParams.delete('service_id')
    window.history.replaceState({}, document.title, url.toString());

    $('head title').text(startTitleText)
    $('head [name="description"]').attr('content', startDescriptionText)
    $('head [name="keywords"]').attr('content', startKeywordsText)

  })
  modals[i].addEventListener('show.bs.modal', event => {
    var target = event.target;
    $('head title').text('CarKey Самара - ' + $(target).find('.modal-title').text().trim())
    $('head [name="keywords"]').attr('content', '')
    let itemProp = $(target).find([itemprop="description"])
    if (itemProp) {
      $('head [name="description"]').attr('content',
        'CarKey Самара - ' +
          $(target).find('.modal-title').text().trim() + ' - ' +
          $(target).find('[itemprop="description"]').text().trim().replace(/[\n\r\t]|\s+/g, " ").replace(/\.|\.\s+/g, ". "))
    }

    let urlParams = new URLSearchParams(window.location.search);
    if (!urlParams.has('modal_id')) {
      addUrlParam('modal_id', modals[i].getAttribute('id'))

      checkGoodsDetailViewOpened()
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


// Ya e-commerce analytics supporting
// TODO: check post data for services
function checkGoodsDetailViewOpened() {
  let urlParams = new URLSearchParams(window.location.search);
  let paramValue = urlParams.get('modal_id');
  if (paramValue && paramValue.includes('detail-view-modal')) {
      let modal = $('#' + paramValue)
        pushDetailViewGoodsData(modal)
    }
}

function pushDetailViewGoodsData(modal) {
  dataLayer.push({
    "ecommerce": {
        "currencyCode": "RUB",
        "detail": {
            "products": [
                {
                    "id": modal.find('.goods-name').data('goods-pk'),
                    "name" : modal.find('.goods-name').text().trim(),
                    "price": modal.find('.goods-price').data('goods-price'),
                    "category": modal.find('.goods-category').data('goods-category'),
                }
            ]
        }
    }
  });
  console.log(dataLayer)
}

function pushDetailViewServiceData(target) {
  let accordionItemID = target.id.replace('body', 'item')
  let accordionItem = $('#' + accordionItemID)
  dataLayer.push({
    "ecommerce": {
        "currencyCode": "RUB",
        "detail": {
            "products": [
                {
                    "id": accordionItem.find('.service-name').data('service-pk'),
                    "name" : accordionItem.find('.service-name').text().trim(),
                    "price": accordionItem.find('.service-price').data('service-price'),
                    "category": 'Service',
                }
            ]
        }
    }
  });
  console.log(dataLayer)
}

function pushAddGoodsData(objId) {
  let modal = $('#detail-view-modal-' + objId)
  dataLayer.push({
    "ecommerce": {
      "currencyCode": "RUB",
      "add": {
        "products": [
          {
            "id": modal.find('.goods-name').data('goods-pk'),
            "name": modal.find('.goods-name').text().trim(),
            "price": modal.find('.goods-price').data('goods-price'),
            "category": modal.find('.goods-category').data('goods-category'),
            "quantity": 1
          }
        ]
      }
    }
  });
  console.log(dataLayer)
}

function pushAddServiceData(objId) {
  let accordionItem = $('#accordion-item-' + objId)
  dataLayer.push({
    "ecommerce": {
      "currencyCode": "RUB",
      "add": {
        "products": [
          {
            "id": accordionItem.find('.service-name').data('service-pk'),
            "name": accordionItem.find('.service-name').text().trim(),
            "price": accordionItem.find('.service-price').data('service-price'),
            "category": 'Service',
            "quantity": 1
          }
        ]
      }
    }
  });
  console.log(dataLayer)
}


// Change page title and description then service is opened

$('#price-list-accordion').on('shown.bs.collapse', function (event) {
  var target = event.target;  // the panel that was shown
  pushDetailViewServiceData(target)
  $('head title').text('CarKey - ' + $(target).parent().find('.service-name').text().trim() + ' в Самаре и области')
  $('head [name="description"]').attr('content',
      'CarKey Самара - ' + $(target).parent().find('.service-name').text().trim() + ' - ' + $(target).find('[itemprop="description"]').text().trim())

  let urlParams = new URLSearchParams(window.location.search);
  if (urlParams.has('service_id')) {
    var params = new URLSearchParams( window.location.search );
    params.set( 'service_id', target.getAttribute('id') );
    var newUrl = window.location.origin + window.location.pathname + '?' + params.toString();
    window.history.replaceState( null, null, newUrl );
  } else {
    addUrlParam('service_id', target.getAttribute('id'))
  }

});

$('#price-list-accordion').on('hide.bs.collapse', event => {
    let url = new URL(window.location.href);
    url.searchParams.delete('service_id');
    window.history.replaceState({}, document.title, url.toString());
    $('head title').text('CarKey Самара - ' + $('#price-list').find('.modal-title').text().trim())
    $('head [name="description"]').attr('content',
        'CarKey Самара - ' +
          $('#price-list').find('.modal-title').text().trim() + ' - ' +
          $('#price-list').find('[itemprop="description"]').text().trim().replace(/[\n\r\t]|\s+/g, " ").replace(/\.|\.\s+/g, ". "))
  })