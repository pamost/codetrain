// Инициализация иконок Lucide
lucide.createIcons();

// Мобильное меню
const mobileMenuBtn = document.getElementById('mobileMenuBtn');
const mobileMenu = document.getElementById('mobileMenu');
if (mobileMenuBtn && mobileMenu) {
    mobileMenuBtn.addEventListener('click', function() {
        mobileMenu.classList.toggle('open');
    });
    document.addEventListener('click', function(event) {
        if (!mobileMenu.contains(event.target) && !mobileMenuBtn.contains(event.target)) {
            mobileMenu.classList.remove('open');
        }
    });
}

// Модальное окно "Запомнить меня"
const userModal = document.getElementById('userModal');
const rememberBtn = document.getElementById('rememberMeBtn');
const closeModalBtn = document.getElementById('closeModalBtn');
const userForm = document.getElementById('userForm');
const formError = document.getElementById('formError');

function openUserModal() { if (userModal) userModal.classList.add('active'); }
function closeUserModal() {
    if (userModal) userModal.classList.remove('active');
    if (formError) formError.classList.add('hidden');
    if (userForm) userForm.reset();
}
if (rememberBtn) rememberBtn.addEventListener('click', openUserModal);
if (closeModalBtn) closeModalBtn.addEventListener('click', closeUserModal);
if (userModal) userModal.addEventListener('click', function(e) { if (e.target === userModal) closeUserModal(); });
if (userForm) {
    userForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const username = document.getElementById('username').value.trim();
        const email = document.getElementById('email').value.trim();
        if (!username) {
            if (formError) { formError.textContent = 'Имя обязательно.'; formError.classList.remove('hidden'); }
            return;
        }
        fetch('/set-user/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify({ username: username, email: email })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'ok') {
                location.reload();
            } else {
                if (formError) { formError.textContent = data.message || 'Ошибка сервера'; formError.classList.remove('hidden'); }
            }
        })
        .catch(error => { if (formError) { formError.textContent = 'Ошибка сети'; formError.classList.remove('hidden'); } });
    });
}

// Модальное окно "Редактировать профиль"
const editModal = document.getElementById('editProfileModal');
const editBtn = document.getElementById('editProfileBtn');
const closeEditBtn = document.getElementById('closeEditModalBtn');
const editForm = document.getElementById('editProfileForm');
const editError = document.getElementById('editFormError');
function openEditModal() {
    if (!editModal) return;
    fetch('/get-user-data/')
        .then(response => response.json())
        .then(data => {
            const usernameField = document.getElementById('editUsername');
            const emailField = document.getElementById('editEmail');
            if (usernameField) usernameField.value = data.username;
            if (emailField) emailField.value = data.email || '';
            editModal.classList.add('active');
        })
        .catch(() => {});
}
function closeEditModal() {
    if (editModal) editModal.classList.remove('active');
    if (editError) editError.classList.add('hidden');
}
if (editBtn) editBtn.addEventListener('click', function(e) { e.preventDefault(); openEditModal(); });
if (closeEditBtn) closeEditBtn.addEventListener('click', closeEditModal);
if (editModal) editModal.addEventListener('click', function(e) { if (e.target === editModal) closeEditModal(); });
if (editForm) {
    editForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const username = document.getElementById('editUsername').value.trim();
        const email = document.getElementById('editEmail').value.trim();
        if (!username) {
            if (editError) { editError.textContent = 'Имя обязательно.'; editError.classList.remove('hidden'); }
            return;
        }
        fetch('/update-user/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify({ username: username, email: email })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'ok') {
                location.reload();
            } else {
                if (editError) { editError.textContent = data.message || 'Ошибка'; editError.classList.remove('hidden'); }
            }
        })
        .catch(() => { if (editError) { editError.textContent = 'Ошибка сети'; editError.classList.remove('hidden'); } });
    });
}

// Выход
const logoutBtn = document.getElementById('logoutBtn');
if (logoutBtn) {
    logoutBtn.addEventListener('click', function(e) {
        e.preventDefault();
        fetch('/logout-user/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => { if (data.status === 'ok') location.reload(); });
    });
}

// Обработка переворота карточек
document.querySelectorAll('[data-flip-card]').forEach(card => {
    card.addEventListener('click', function(e) {
        if (e.target.classList.contains('remember-btn')) return;
        this.classList.toggle('flipped');
    });
});

// Обработка кнопок "Запомнил" на странице тем
document.querySelectorAll('.remember-btn').forEach(btn => {
    btn.addEventListener('click', function(e) {
        e.stopPropagation();
        const cardDiv = this.closest('[data-flip-card]');
        const cardId = cardDiv.getAttribute('data-card-id');
        if (!cardId) return;
        fetch('/remember-card/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify({ card_id: cardId })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'ok') {
                location.reload();
            } else {
                alert(data.message || 'Ошибка при запоминании');
            }
        })
        .catch(error => console.error('Error:', error));
    });
});

// Обработка кнопок "Забыть" на странице статистики (делегирование)
document.body.addEventListener('click', function(e) {
    const btn = e.target.closest('.unremember-btn');
    if (!btn) return;
    e.preventDefault();
    const cardId = btn.getAttribute('data-card-id');
    if (!cardId) return;
    fetch('/unremember-card/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify({ card_id: cardId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'ok') {
            location.reload();
        } else {
            alert('Ошибка при забывании');
        }
    });
});