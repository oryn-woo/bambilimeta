window.addEventListener('scroll', function(){
  const nav = document.getElementById('mainNavbar');
  if (window.scrollY > document.getElementById('heroCarousel').offsetHeight) {
    nav.classList.add('fixed-top');
  } else {
    nav.classList.remove('fixed-top');
  }
});
