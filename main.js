/* ============================================================
   FIXR — Main JavaScript
   Sections:
     1. Page Routing
     2. Auth (Login / Logout)
     3. Sign Up Flow
     4. Account Tabs
     5. Star Rating
     6. Booking Steps
     7. Calendar
     8. Time Slots
     9. Messages / Chat
   ============================================================ */


/* ── 1. PAGE ROUTING ── */

/**
 * showPage(name)
 * Hides all pages and activates the one matching `name`.
 * Matches elements with id="page-{name}".
 */
function showPage(name) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));

  const el = document.getElementById('page-' + name);
  if (el) {
    el.classList.add('active');
    window.scrollTo(0, 0);
  }
}


/* ── 2. AUTH (LOGIN / LOGOUT) ── */

let loggedIn = false;

/**
 * doLogin()
 * Simulates a successful login — swaps nav auth state and
 * redirects to the dashboard.
 */
function doLogin() {
  loggedIn = true;
  document.getElementById('nav-auth-loggedout').style.display = 'none';
  document.getElementById('nav-auth-loggedin').style.display  = 'flex';
  showPage('dashboard');
}

/**
 * logout()
 * Clears logged-in state and returns to the home page.
 */
function logout() {
  loggedIn = false;
  document.getElementById('nav-auth-loggedout').style.display = 'flex';
  document.getElementById('nav-auth-loggedin').style.display  = 'none';
  showPage('home');
}


/* ── 3. SIGN UP FLOW ── */

let selectedRole = 'client';

/**
 * selectRole(role)
 * Highlights the chosen role card ('client' | 'provider').
 */
function selectRole(role) {
  selectedRole = role;
  document.getElementById('role-client').classList.toggle('selected',   role === 'client');
  document.getElementById('role-provider').classList.toggle('selected', role === 'provider');
}

/**
 * nextSignupStep(step)
 * Advances or rewinds the sign-up multi-step form.
 * Step 1 = role selection, Step 2 = role-specific form.
 */
function nextSignupStep(step) {
  document.querySelectorAll('.signup-step').forEach(s => s.classList.remove('active'));

  if (step === 1) {
    document.getElementById('signup-s1').classList.add('active');
  } else if (step === 2) {
    const formId = selectedRole === 'provider' ? 'signup-s2-provider' : 'signup-s2-client';
    document.getElementById(formId).classList.add('active');
  }
}

/** Alias for the "Change role" link inside step 2 forms. */
function goSignupStep1() {
  nextSignupStep(1);
}


/* ── 4. ACCOUNT TABS ── */

/**
 * showAcctTab(name, btn)
 * Activates a tab panel and highlights the corresponding button.
 * @param {string} name  - matches id="acct-tab-{name}"
 * @param {HTMLElement} btn - the clicked tab button
 */
function showAcctTab(name, btn) {
  document.querySelectorAll('.acct-tab-content').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.acct-tab').forEach(t => t.classList.remove('active'));

  document.getElementById('acct-tab-' + name).classList.add('active');
  btn.classList.add('active');
}


/* ── 5. STAR RATING ── */

/**
 * setRating(n)
 * Lights up the first n star buttons in the review form.
 */
function setRating(n) {
  document.querySelectorAll('.star-btn').forEach((btn, i) => {
    btn.classList.toggle('lit', i < n);
  });
}


/* ── 6. BOOKING STEPS ── */

/**
 * nextBookStep(step)
 * Advances the 3-step booking wizard.
 * Updates both the step indicator and the content panel.
 */
function nextBookStep(step) {
  [1, 2, 3].forEach(i => {
    const content   = document.getElementById('bstep-content' + i);
    const indicator = document.getElementById('bstep' + i);

    if (content) {
      content.classList.toggle('active', i === step);
    }

    if (indicator) {
      const state = i < step ? 'done' : i === step ? 'active' : 'inactive';
      indicator.className = 'bstep ' + state;
    }
  });
}


/* ── 7. CALENDAR ── */

/**
 * buildCalendar()
 * Renders the April 2026 calendar grid inside the booking flow.
 * Days before today are disabled; clicking a valid day
 * updates the booking summary date.
 */
function buildCalendar() {
  const headerEl = document.getElementById('cal-days-header');
  if (!headerEl) return;

  const dayNames = ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa'];
  const YEAR     = 2026;
  const MONTH    = 3;       // April (0-indexed)
  const TODAY    = 10;      // April 10

  // Render day-name row
  dayNames.forEach(name => {
    const el = document.createElement('div');
    el.className   = 'cal-day-name';
    el.textContent = name;
    headerEl.appendChild(el);
  });

  // Render day cells
  const gridEl       = document.getElementById('cal-days');
  const firstWeekday = new Date(YEAR, MONTH, 1).getDay();
  const totalDays    = new Date(YEAR, MONTH + 1, 0).getDate();

  // Leading empty cells
  for (let i = 0; i < firstWeekday; i++) {
    const empty = document.createElement('div');
    empty.className = 'cal-day empty';
    gridEl.appendChild(empty);
  }

  // Day cells
  for (let day = 1; day <= totalDays; day++) {
    const el = document.createElement('div');
    el.className   = 'cal-day';
    el.textContent = day;

    if (day === TODAY)  el.classList.add('today');
    if (day < TODAY)    el.classList.add('disabled');
    else {
      el.addEventListener('click', function () {
        document.querySelectorAll('.cal-day').forEach(d => d.classList.remove('selected'));
        this.classList.add('selected');

        const sumDate = document.getElementById('sum-date');
        if (sumDate) sumDate.textContent = 'Apr ' + day + ', 2026';
      });
    }

    gridEl.appendChild(el);
  }
}


/* ── 8. TIME SLOTS ── */

/**
 * buildTimeSlots()
 * Renders clickable time-slot buttons in the booking flow.
 * Slots in the `taken` array are rendered as unavailable.
 */
function buildTimeSlots() {
  const container = document.getElementById('time-slots');
  if (!container) return;

  const times = [
    '8:00 AM', '9:00 AM', '10:00 AM', '11:00 AM',
    '12:00 PM', '1:00 PM', '2:00 PM', '3:00 PM',
    '4:00 PM', '5:00 PM', '6:00 PM', '7:00 PM',
  ];
  const taken = [1, 4, 7]; // indices of unavailable slots

  times.forEach((time, index) => {
    const el = document.createElement('div');
    el.className   = 'time-slot' + (taken.includes(index) ? ' taken' : '');
    el.textContent = time;

    if (!taken.includes(index)) {
      el.addEventListener('click', function () {
        document.querySelectorAll('.time-slot').forEach(s => s.classList.remove('selected'));
        this.classList.add('selected');

        const sumTime = document.getElementById('sum-time');
        if (sumTime) sumTime.textContent = time;
      });
    }

    container.appendChild(el);
  });
}


/* ── 9. MESSAGES / CHAT ── */

/**
 * selectConv(el, name)
 * Marks a conversation item as active, clears its unread badge,
 * and updates the chat header with the provider's name.
 *
 * @param {HTMLElement} el   - the clicked .conv-item
 * @param {string}      name - provider display name
 */
function selectConv(el, name) {
  document.querySelectorAll('.conv-item').forEach(c => c.classList.remove('active'));
  el.classList.add('active');

  // Clear unread badge
  const badge = el.querySelector('.conv-unread');
  if (badge) badge.remove();

  // Update chat header
  const header = document.getElementById('chat-prov-name');
  if (header) header.textContent = name;
}

/**
 * sendMsg()
 * Reads the chat input, appends a new outgoing message bubble,
 * clears the input, and scrolls to the bottom.
 */
function sendMsg() {
  const input = document.getElementById('chat-input');
  const text  = input ? input.value.trim() : '';
  if (!text) return;

  const feed = document.getElementById('chat-messages');
  const now  = new Date();
  const time = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

  const row = document.createElement('div');
  row.className = 'msg-row mine';
  row.innerHTML = `
    <div>
      <div class="msg-bubble mine">${text}</div>
      <div class="msg-time mine">${time}</div>
    </div>
  `;

  feed.appendChild(row);
  input.value    = '';
  feed.scrollTop = feed.scrollHeight;
}


/* ── INIT ── */

document.addEventListener('DOMContentLoaded', () => {
  // Build calendar and time slots on page load
  buildCalendar();
  buildTimeSlots();

  // Allow Enter key to send a chat message (Shift+Enter = newline)
  const chatInput = document.getElementById('chat-input');
  if (chatInput) {
    chatInput.addEventListener('keydown', e => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMsg();
      }
    });
  }
});
