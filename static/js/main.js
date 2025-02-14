/**
* Template Name: NiceAdmin
* Template URL: https://bootstrapmade.com/nice-admin-bootstrap-admin-html-template/
* Updated: Apr 20 2024 with Bootstrap v5.3.3
* Author: BootstrapMade.com
* License: https://bootstrapmade.com/license/
*/

(function() {
  "use strict";

  /**
   * Easy selector helper function
   */
  const select = (el, all = false) => {
    el = el.trim()
    if (all) {
      return [...document.querySelectorAll(el)]
    } else {
      return document.querySelector(el)
    }
  }

  /**
   * Easy event listener function
   */
  const on = (type, el, listener, all = false) => {
    if (all) {
      select(el, all).forEach(e => e.addEventListener(type, listener))
    } else {
      select(el, all).addEventListener(type, listener)
    }
  }

  /**
   * Easy on scroll event listener 
   */
  const onscroll = (el, listener) => {
    el.addEventListener('scroll', listener)
  }

  /**
   * Sidebar toggle
   */
  if (select('.toggle-sidebar-btn')) {
    on('click', '.toggle-sidebar-btn', function(e) {
      select('body').classList.toggle('toggle-sidebar')
    })
  }

  /**
   * Search bar toggle
   */
  if (select('.search-bar-toggle')) {
    on('click', '.search-bar-toggle', function(e) {
      select('.search-bar').classList.toggle('search-bar-show')
    })
  }

  /**
   * Navbar links active state on scroll
   */
  let navbarlinks = select('#navbar .scrollto', true)
  const navbarlinksActive = () => {
    let position = window.scrollY + 200
    navbarlinks.forEach(navbarlink => {
      if (!navbarlink.hash) return
      let section = select(navbarlink.hash)
      if (!section) return
      if (position >= section.offsetTop && position <= (section.offsetTop + section.offsetHeight)) {
        navbarlink.classList.add('active')
      } else {
        navbarlink.classList.remove('active')
      }
    })
  }
  window.addEventListener('load', navbarlinksActive)
  onscroll(document, navbarlinksActive)

  /**
   * Toggle .header-scrolled class to #header when page is scrolled
   */
  let selectHeader = select('#header')
  if (selectHeader) {
    const headerScrolled = () => {
      if (window.scrollY > 100) {
        selectHeader.classList.add('header-scrolled')
      } else {
        selectHeader.classList.remove('header-scrolled')
      }
    }
    window.addEventListener('load', headerScrolled)
    onscroll(document, headerScrolled)
  }

  /**
   * Back to top button
   */
  let backtotop = select('.back-to-top')
  if (backtotop) {
    const toggleBacktotop = () => {
      if (window.scrollY > 100) {
        backtotop.classList.add('active')
      } else {
        backtotop.classList.remove('active')
      }
    }
    window.addEventListener('load', toggleBacktotop)
    onscroll(document, toggleBacktotop)
  }

  /**
   * Initiate tooltips
   */
  var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
  var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl)
  })

  /**
   * Initiate quill editors
   */
  if (select('.quill-editor-default')) {
    new Quill('.quill-editor-default', {
      theme: 'snow'
    });
  }

  if (select('.quill-editor-bubble')) {
    new Quill('.quill-editor-bubble', {
      theme: 'bubble'
    });
  }

  if (select('.quill-editor-full')) {
    new Quill(".quill-editor-full", {
      modules: {
        toolbar: [
          [{
            font: []
          }, {
            size: []
          }],
          ["bold", "italic", "underline", "strike"],
          [{
              color: []
            },
            {
              background: []
            }
          ],
          [{
              script: "super"
            },
            {
              script: "sub"
            }
          ],
          [{
              list: "ordered"
            },
            {
              list: "bullet"
            },
            {
              indent: "-1"
            },
            {
              indent: "+1"
            }
          ],
          ["direction", {
            align: []
          }],
          ["link", "image", "video"],
          ["clean"]
        ]
      },
      theme: "snow"
    });
  }

  /**
   * Initiate TinyMCE Editor
   */

  const useDarkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;
  const isSmallScreen = window.matchMedia('(max-width: 1023.5px)').matches;

/*tinymace*/

  /**
   * Initiate Bootstrap validation check
   */
  var needsValidation = document.querySelectorAll('.needs-validation')

  Array.prototype.slice.call(needsValidation)
    .forEach(function(form) {
      form.addEventListener('submit', function(event) {
        if (!form.checkValidity()) {
          event.preventDefault()
          event.stopPropagation()
        }

        form.classList.add('was-validated')
      }, false)
    })

  /**
   * Initiate Datatables
   */
  const datatables = select('.datatable', true)
  datatables.forEach(datatable => {
    new simpleDatatables.DataTable(datatable, {
      perPageSelect: [5, 10, 15, ["All", -1]],
      columns: [{
          select: 2,
          sortSequence: ["desc", "asc"]
        },
        {
          select: 3,
          sortSequence: ["desc"]
        },
        {
          select: 4,
          cellClass: "green",
          headerClass: "red"
        }
      ]
    });
  })

  /**
   * Autoresize echart charts
   */
  const mainContainer = select('#main');
  if (mainContainer) {
    setTimeout(() => {
      new ResizeObserver(function() {
        select('.echart', true).forEach(getEchart => {
          echarts.getInstanceByDom(getEchart).resize();
        })
      }).observe(mainContainer);
    }, 200);
  }

})();

document.addEventListener("DOMContentLoaded", () => {
  const links = document.querySelectorAll('.sidebar-nav .nav-link');
  //const currentPath = window.location.pathname.split('/').pop(); // Mendapatkan path terakhir dari URL
  const currentPath = window.location.pathname.replace(/^\//, '').replace(/\/$/, ''); // Hilangkan slash awal & akhir

  links.forEach(link => {
      if (link.getAttribute('data-href') === currentPath) {
          link.classList.remove('collapsed');
          link.classList.add('active');
      } else {
          link.classList.add('collapsed');
          link.classList.remove('active');
      }
  });
});

document.addEventListener("DOMContentLoaded", function() {
  // Ambil semua tombol edit
  const editButtons = document.querySelectorAll(".edit-btn");

  editButtons.forEach(button => {
      button.addEventListener("click", function() {
          const customerId = this.getAttribute("data-id");
          console.log("data-id")
          // Ambil data dari server
          console.log("Fetching data..."); // Debugging

          fetch(`/getedit/${customerId}`)
              .then(response => response.json())
              .then(data => {
                console.log("Fetched Data:", data);

                // Pastikan elemen ada sebelum diisi
                // Konversi format tanggal dari server ke format yang valid untuk input HTML
                const formatDatetimeLocal = (datetime) => {
                    const date = new Date(datetime);
                    return date.toISOString().slice(0, 16); // Format: "YYYY-MM-DDTHH:mm"
                };

                const formatDate = (dateString) => {
                    const date = new Date(dateString);
                    return date.toISOString().split("T")[0]; // Format: "YYYY-MM-DD"
                };

                  document.getElementById("editForm").setAttribute("action", `/edit/${data.id}`);
                  document.getElementById("edit_namacustomer").value = data.namacustomer;
                  document.getElementById("edit_namaperusahaan").value = data.namaperusahaan;
                  document.getElementById("edit_tanggalinput").value = formatDatetimeLocal(data.tanggalinput);
                  document.getElementById("edit_tanggal_kirim").value = formatDate(data.tanggalkirim);
                  document.getElementById("edit_telp").value = data.telp;
                  document.getElementById("edit_alamat").value = data.alamat;
                  document.getElementById("edit_latitude").value = data.latitude;
                  document.getElementById("edit_longitude").value = data.longitude;

                  updateMap(data.latitude, data.longitude);
              })
              .catch(error => console.error("Error fetching customer data:", error));
      });
  });

  


  
  
  function updateMap(lat, lng) {
      // Periksa apakah Leaflet sudah terinisialisasi
      if (typeof L !== "undefined") {
          map = L.map("map").setView([lat, lng], 15);
          L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png").addTo(map);
          L.marker([lat, lng]).addTo(map);
      }else{
        map.invalidateSize();
      }
  }
});

setTimeout(function() {
  var flashMessages = document.getElementsByClassName('flash');
  
  // Periksa apakah flashMessages ada sebelum mengaksesnya
  if (flashMessages.length > 0) {
      flashMessages[0].style.transition = "opacity 0.5s ease";
      flashMessages[0].style.opacity = "0";
      setTimeout(() => flashMessages[0].remove(), 500);
  }
}, 5000);

