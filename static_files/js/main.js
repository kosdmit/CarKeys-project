// Enable bootstrap tooltips
const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]')
const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl))


"use strict";

var elem = document.querySelector('.testimonial-carousel');
var flkty = new Flickity( elem, {
    // options
	contain: true,
	wrapAround: true,
	autoPlay: true,
	percentPosition: false, //carousel-cell is using px width
  
});
