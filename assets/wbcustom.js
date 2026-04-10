// Dropdown Hover
$(document).on("click", function(event){
    var $trigger = $(".dropdown");
    if($trigger !== event.target && !$trigger.has(event.target).length){
        $(".dropdown-menu").slideUp("fast");
    }            
});
$(document).ready(function() {

    // Show hide popover
    $(document).on('click', '.hmuser,.wbcollscart', function(e) {
        $(this).toggleClass('active');
        $(this).next().slideToggle('fast');
        $(".dropdown-menu").not($(this).next()).slideUp('fast');
    });


    // Collapse Toggle
    $(document).on('click', '.toggle.collapsed', function(e) {
        $(this).toggleClass('active');
        $(this).next().slideToggle('fast');
    });

    // Scroll To top
    $("#scroll").addClass("scrollhide");
        $(window).scroll(function () {
        if ($(this).scrollTop() === 0) {
            $("#scroll").addClass("scrollhide")
        } else {
            $("#scroll").removeClass("scrollhide")
        }
    });
    $(document).on('click', '#scroll', function(e) {
        $("html, body").animate({scrollTop: 0}, 600);
        return false;
    });
}); // Document Ready Div End


// Countdown section
setInterval(countDown, 1000);
function countDown() {
  const countCardSections = document.querySelectorAll('.countd_all');
  countCardSections.forEach((countdownSection) => {
      var countDownDate = countdownSection.getAttribute('data-date');
      var now = new Date().getTime();
      if (!countDownDate) {
          countdownSection.querySelector('.main_cdays .wb_cdays').textContent = '00';
          countdownSection.querySelector('.main_chours .wb_chours').textContent = '00';
          countdownSection.querySelector('.main_cminutes .wb_cminutes').textContent = '00';
          countdownSection.querySelector('.main_cseconds .wb_cseconds').textContent = '00';
      } else {
          countDownDate = new Date(countDownDate).getTime();
          var distance = countDownDate - now;

          if (distance < 0 || isNaN(countDownDate)) {
              countdownSection.style.display = 'none';
              let c = countdownSection.parentElement.querySelector('p.countdownMessage');
              if(c) c.style.display = 'block';
          } else {
              countdownSection.querySelector('.main_cdays .wb_cdays').textContent = Math.floor(distance / (1000 * 60 * 60 * 24));
              countdownSection.querySelector('.main_chours .wb_chours').textContent = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
              countdownSection.querySelector('.main_cminutes .wb_cminutes').textContent = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
              countdownSection.querySelector('.main_cseconds .wb_cseconds').textContent = Math.floor((distance % (1000 * 60)) / 1000);
          }
      }
  });
}