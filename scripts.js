const axios = require('axios');
// Fetch services data and populate table
axios.get('http://localhost:8000/list_services')
  .then(response => {
    const tableBody = document.querySelector('#services-table tbody');
    response.data.forEach(service => {
      const row = tableBody.insertRow(-1);
      const nameCell = row.insertCell(0);
      const urlCell = row.insertCell(1);
      nameCell.textContent = service.name;
      urlCell.textContent = service.url;
    });
  })
  .catch(error => {
    console.error('Error fetching services:', error);
  });

// Register service form submit event
const form = document.querySelector('#register-form');
form.addEventListener('submit', event => {
  event.preventDefault();
  const name = form.elements['name'].value;
  const url = form.elements['url'].value;
  const data = {name, url};
  axios.post('http://localhost:8000/register_service', data)
    .then(response => {
      alert(response.data.message);
      form.reset();
      location.reload(); // Refresh table after registration
    })
    .catch(error => {
      console.error('Error registering service:', error);
    });
});

