
let currentYear, currentMonth;

function showPage1(pageId) {
    document.querySelectorAll('.content').forEach(p => p.classList.remove('active'));
    document.getElementById(pageId).classList.add('active');

    document.getElementById('pageTitle').textContent =
        pageId.charAt(0).toUpperCase() + pageId.slice(1);

    document.querySelectorAll('.sidebar ul li').forEach(link => link.classList.remove('active'));
    const activeLink = document.getElementById("link-" + pageId);
    if (activeLink) activeLink.classList.add('active');

    if (window.innerWidth <= 768) {
        document.getElementById('sidebar').classList.remove('show');
    }

    if (pageId === 'calendar') {
        const now = new Date();
        currentYear = now.getFullYear();
        currentMonth = now.getMonth();
        updateCalendar(currentYear, currentMonth);
    }
}

function showPage(page) {
    // Update page title dynamically
    const pageTitle = document.getElementById('pageTitle');
    pageTitle.innerText = page.charAt(0).toUpperCase() + page.slice(1); // Capitalize first letter

    // Update the browser's URL without reloading the page
    const url = document.getElementById(page + 'Url').dataset.url; // Fetch URL using data-url attribute
    if (url) {
        // Update the browser's address bar without reloading the page
        history.pushState(null, pageTitle.innerText, url);
    }

    // Show the selected page content
    const contentDivs = document.querySelectorAll('.content');
    contentDivs.forEach(div => {
        div.classList.remove('active');
    });

    const pageContent = document.getElementById(page);
    if (pageContent) {
        pageContent.classList.add('active');
    }
}

// Optional: Automatically show the correct page based on the URL
window.onload = () => {
    const page = window.location.pathname.split('/').pop(); // Extract page name from URL
    showPage(page || 'dashboard'); // Default to 'dashboard' if no page is found
};


// Optional: Automatically show the correct page based on the URL
window.onload = () => {
    const page = window.location.pathname.split('/').pop(); // Extract page name from URL
    showPage(page || 'dashboard'); // Default to 'dashboard' if no page is found
};

  

function updateCalendar(year, month) {
    const monthLabel = document.getElementById('monthLabel');
    const calendarGrid = document.getElementById('calendarGrid');
    calendarGrid.innerHTML = '';

    const monthNames = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ];
    monthLabel.textContent = `${monthNames[month]} ${year}`;

    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const startDay = firstDay.getDay();

    for (let i = 0; i < startDay; i++) {
        const empty = document.createElement('div');
        empty.className = 'calendar-day';
        calendarGrid.appendChild(empty);
    }

    for (let day = 1; day <= lastDay.getDate(); day++) {
        const dayBox = document.createElement('div');
        dayBox.className = 'calendar-day';
        dayBox.textContent = day;
        calendarGrid.appendChild(dayBox);
    }
}

function changeMonth(offset) {
    currentMonth += offset;
    if (currentMonth < 0) {
        currentMonth = 11;
        currentYear -= 1;
    } else if (currentMonth > 11) {
        currentMonth = 0;
        currentYear += 1;
    }
    updateCalendar(currentYear, currentMonth);
}

function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    sidebar.classList.toggle('show');
}

window.onload = () => {
    showPage('dashboard');
};
