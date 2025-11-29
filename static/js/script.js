// --- File Upload & Preview Handling ---
function handleFileSelect(input) {
    const label = document.getElementById('file-label');
    const container = document.getElementById('preview-container');

    // Reset container
    container.innerHTML = '';

    if (input.files && input.files.length > 0) {
        label.innerText = `${input.files.length} images selected`;

        // Generate Thumbnails
        Array.from(input.files).forEach(file => {
            const reader = new FileReader();
            reader.onload = function (e) {
                const img = document.createElement('img');
                img.src = e.target.result;
                img.className = 'preview-thumb';
                container.appendChild(img);
            };
            reader.readAsDataURL(file);
        });
    } else {
        label.innerText = "Click to Upload Images";
    }
}

// --- Form Submission ---
document.getElementById('upload-form')?.addEventListener('submit', async function (e) {
    e.preventDefault();

    const formData = new FormData(this);
    const loader = document.getElementById('loader');
    const msg = document.getElementById('status-msg');
    const submitBtn = this.querySelector('button[type="submit"]');

    loader.style.display = 'block';
    submitBtn.disabled = true;
    msg.innerText = "Stitching... This may take a moment.";

    try {
        const response = await fetch('/stitch', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            msg.innerText = "Stitching Complete!";
            loadSession(data.image_url, data.session_id);
            addSessionToSidebar(data.session_id, data.session_name, data.image_url);
        } else {
            // Trigger Custom Error Modal
            msg.innerText = ""; // Clear text status
            document.getElementById('error-message').innerText = data.error || "Stitching Failed.";
            openModal('error-modal');
        }
    } catch (error) {
        console.error(error);
        msg.innerText = "An error occurred.";
    } finally {
        loader.style.display = 'none';
        submitBtn.disabled = false;
    }
});

// --- Modal Handling ---
function openModal(modalId) {
    document.getElementById(modalId).style.display = 'flex';
}

function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

// --- Session Logic ---
function addSessionToSidebar(id, name, imageUrl) {
    const list = document.getElementById('history-list');
    const div = document.createElement('div');
    div.className = 'history-item active';
    div.id = `session-${id}`;
    div.onclick = function () { loadSession(imageUrl, id); };

    div.innerHTML = `
        <span>${name}</span>
        <span class="delete-btn" onclick="openDeleteModal(event, ${id})">✕</span>
    `;
    list.insertBefore(div, list.firstChild);
}

function loadSession(imageUrl, sessionId) {
    document.getElementById('upload-section').style.display = 'none';
    const resultSec = document.getElementById('result-section');
    resultSec.style.display = 'block';

    document.getElementById('result-img').src = imageUrl;
    document.getElementById('download-btn').href = imageUrl;

    document.querySelectorAll('.history-item').forEach(el => el.classList.remove('active'));
    const activeItem = document.getElementById(`session-${sessionId}`);
    if (activeItem) activeItem.classList.add('active');
}

function resetDashboard() {
    document.getElementById('upload-section').style.display = 'block';
    document.getElementById('result-section').style.display = 'none';
    document.getElementById('upload-form').reset();
    document.getElementById('file-label').innerText = "Click to Upload Images";
    document.getElementById('status-msg').innerText = "";
    document.getElementById('preview-container').innerHTML = ""; // Clear previews

    document.querySelectorAll('.history-item').forEach(el => el.classList.remove('active'));
}

// --- Delete Logic with Custom Modal ---
let sessionToDeleteId = null;

function openDeleteModal(event, id) {
    event.stopPropagation();
    sessionToDeleteId = id; // Store ID for the confirm button
    openModal('delete-modal');
}

document.getElementById('confirm-delete-btn')?.addEventListener('click', async function () {
    if (sessionToDeleteId === null) return;

    const id = sessionToDeleteId;
    closeModal('delete-modal'); // Close modal immediately

    const response = await fetch(`/delete_session/${id}`, { method: 'DELETE' });
    if (response.ok) {
        const item = document.getElementById(`session-${id}`);
        item.remove();

        if (item.classList.contains('active')) {
            resetDashboard();
        }
    }
    sessionToDeleteId = null; // Reset
});