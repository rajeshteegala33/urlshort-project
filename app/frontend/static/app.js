const API = (window.location.hostname === 'localhost' || window.location.hostname === '') ? 'http://localhost:8000' : '';

function setAuth(token) {
  localStorage.setItem('token', token);
  document.getElementById('auth-result').innerText = 'Authenticated';
  document.getElementById('shorten-card').style.display = 'block';
  document.getElementById('analytics-card').style.display = 'block';
}

async function signup() {
  const username = document.getElementById('username').value;
  const password = document.getElementById('password').value;
  const res = await fetch(API + '/signup', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({username, password})
  });
  const data = await res.json();
  if (res.ok) setAuth(data.access_token);
  else document.getElementById('auth-result').innerText = JSON.stringify(data);
}

async function login() {
  const username = document.getElementById('username').value;
  const password = document.getElementById('password').value;
  const res = await fetch(API + '/login', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({username, password})
  });
  const data = await res.json();
  if (res.ok) setAuth(data.access_token);
  else document.getElementById('auth-result').innerText = JSON.stringify(data);
}

async function shorten() {
  const original = document.getElementById('original').value;
  const custom = document.getElementById('custom').value;
  const token = localStorage.getItem('token');
  const res = await fetch(API + '/shorten', {
    method: 'POST',
    headers: {'Content-Type':'application/json', 'Authorization': 'Bearer ' + token},
    body: JSON.stringify({original_url: original, custom_short: custom || null})
  });
  const data = await res.json();
  if (res.ok) {
    const url = window.location.origin + '/' + data.short;
    document.getElementById('short-result').innerHTML = `Short URL: <a href="${url}" target="_blank">${url}</a>`;
  } else {
    document.getElementById('short-result').innerText = JSON.stringify(data);
  }
}

async function viewAnalytics() {
  const short = document.getElementById('short-to-view').value;
  const token = localStorage.getItem('token');
  const res = await fetch(API + '/analytics/' + short, {
    headers: {'Authorization': 'Bearer ' + token}
  });
  const data = await res.json();
  document.getElementById('analytics-result').innerText = JSON.stringify(data, null, 2);
}
