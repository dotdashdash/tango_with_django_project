document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("taskTitle").addEventListener("input", predictDifficulty);
    document.getElementById("taskPriority").addEventListener("change", predictDifficulty);
    document.getElementById("taskDueDate").addEventListener("change", calculateDuration);
    document.getElementById("taskStartDate").addEventListener("change", calculateDuration);
    document.getElementById("taskForm").addEventListener("submit", submitTask);
    fetchTasks();
    document.querySelector(".task-list").addEventListener("click", function (event) {
        if (event.target.closest(".complete-task-btn")) {
            let taskId = event.target.closest(".complete-task-btn").dataset.taskId;
            completeTask(taskId, event);
        }
    });
    document.querySelector(".achievements-button").addEventListener("click", async function () {
        const achievements = await fetchAchievements();
        if (achievements.length > 0) {
            achievements.forEach((achievement, index) => {
                setTimeout(() => showAchievementPopup(achievement), index * 500);
            });
        }
    });
});

function showToast(message, duration = 3000) {
    const toast = document.createElement("div");
    toast.className = "toast";
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), duration);
}

function openTaskModal() {
    document.getElementById("taskModal").style.display = "flex";
}

function closeTaskModal() {
    document.getElementById("taskModal").style.display = "none";
}

window.addEventListener("keydown", function (event) {
    if (event.key === "Escape") {
        closeTaskModal();
    }
});


/**
 * Start Time 和 Due Date
 */
function calculateDuration() {
    let startInput = document.getElementById("taskStartDate").value;
    let dueInput = document.getElementById("taskDueDate").value;

    if (!dueInput) return;  // must have due date

    let startDate = startInput ? new Date(startInput) : new Date();
    let dueDate = new Date(dueInput);

    let durationMinutes = Math.round((dueDate - startDate) / 60000);

    predictDifficulty(durationMinutes);
    if (dueDate < startDate) {
        showToast("due date must be later than start date")
        document.getElementById("taskDueDate").value = "";
        return;
    }
}

/**
 * based on task title, duration, and priority to predict difficulty
 */
function predictDifficulty(duration = 30) {
    let title = document.getElementById("taskTitle").value.toLowerCase();
    let isHighPriority = document.getElementById("taskPriority").checked;
    let difficulty = 1;

    const keywordsHard = ["report", "study", "presentation", "deadline", "research"];
    const keywordsMedium = ["exercise", "meeting", "cleaning", "shopping"];

    if (keywordsHard.some(word => title.includes(word))) {
        difficulty = 3;
    } else if (keywordsMedium.some(word => title.includes(word))) {
        difficulty = 2;
    }

    if (duration > 120) {
        difficulty = Math.max(difficulty, 3);
    } else if (duration > 60) {
        difficulty = Math.max(difficulty, 2);
    }

    if (isHighPriority) {
        difficulty = Math.min(3, difficulty + 1);
    }

    let difficultyDisplay = ["Easy", "Medium", "Hard"];
    document.getElementById("difficultyDisplay").textContent = difficultyDisplay[difficulty - 1];
    document.getElementById("taskDifficulty").value = difficulty;
}

/**
 * submit task
 */
async function fetchTasks() {
    try {
        const response = await fetch("/api/tasks/", {
            method: "GET",
            headers: { "Authorization": `Bearer ${localStorage.getItem("token")}` }
        });

        if (!response.ok) throw new Error("Failed to load tasks");
        const tasks = await response.json();
        updateTaskBoard(tasks);
        updateTaskMap(tasks);
    } catch (error) {
        console.error("load failed:", error);
    }
}

async function submitTask(event) {
    event.preventDefault();
    const formData = new FormData(event.target);

    try {
        const response = await fetch("/api/tasks/", {
            method: "POST",
            headers: {
                "X-CSRFToken": getCookie("csrftoken"),
            },
            body: formData
        });

        if (response.ok) {
            closeTaskModal();
            fetchTasks();
        } else {
            console.error("任务创建失败");
        }
    } catch (error) {
        console.error("任务提交失败:", error);
    }
}


/**
 * complete task
 */
let currentLevel = null;
async function completeTask(taskId, event) {
    try {
        const response = await fetch(`/api/tasks/${taskId}/complete/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json'
            }
        });

        if (response.ok) {
            const data = await response.json();
            console.log("✅ task completion:", data);
            let taskCard = document.getElementById(`task-${taskId}`);
            if (taskCard) {
                let details = taskCard.querySelector(".task-details");
                if (details) details.style.display = "none";

                let completeButton = taskCard.querySelector(".complete-task-btn");
                if (completeButton) completeButton.remove();

                let doneBadge = document.createElement("span");
                doneBadge.className = "completed-text";
                doneBadge.textContent = "✔️ Done";
                taskCard.querySelector(".task-header").appendChild(doneBadge);
            }

            if (event) createParticles(event.clientX, event.clientY);
            if (data.exp !== undefined) {
                document.getElementById("exp").textContent = data.exp;
            }
            fetchTasks();  // reload tasks
            if (data.new_level !== undefined) {
                let levelElement = document.getElementById("level");
                if (levelElement) {
                    levelElement.textContent = `Lv.${data.new_level}`;
                }
            }
            if (Array.isArray(data.unlocked_features) && data.unlocked_features.length > 0) {
                console.log("📢 UNLOCK!:", data.unlocked_features);
                data.unlocked_features.forEach((achievement, index) => {
                    setTimeout(() => showAchievementPopup(achievement), index * 800);
                });
            } else {
                console.log("ℹ️ no new achievements");
            }

            fetchTasks();  // reload tasks
        } else {
            console.error("❌ task completion failed");
        }
    } catch (error) {
        console.error("❌ task request failed:", error);
    }
}

/**
 * achiev dashboard
 */
async function fetchTasks() {
    try {
        const response = await fetch("/api/tasks/", {
            method: "GET",
            headers: {
                "Authorization": "Bearer " + localStorage.getItem("token")
            }
        });
        const tasks = await response.json();
        updateTaskBoard(tasks);
        // updateTaskMap(tasks);
    } catch (error) {
        console.error("fetch failed", error);
    }
}

function updateTaskBoard(tasks) {
    const activeTasksContainer = document.querySelector(".task-list");
    const completedTasksContainer = document.querySelector(".completed-task-list");

    activeTasksContainer.innerHTML = "";
    completedTasksContainer.innerHTML = "";

    let hasCompletedTasks = false;

    tasks.forEach(task => {
        console.log("Task ID:", task.id, "Completed:", task.is_completed);

        let taskHTML = `
            <div class="task-card ${task.is_completed ? "completed" : ""}" id="task-${task.id}">
                <div class="task-header">
                    <span class="difficulty-${task.difficulty}">
                        ${["Easy", "Medium", "Hard"][task.difficulty - 1]}
                    </span>
                    ${task.is_completed ? `<span class="completed-text">✔️ Done</span>` : ""}
                </div>
                <p class="task-title">${task.title}</p>

                <div class="task-details">
                    ${task.start_date ? `<p class="task-start">🕒 Start: ${formatDate(task.start_date)}</p>` : ""}
                    ${task.due_date ? `<p class="task-due">⏳ Due: ${formatDate(task.due_date)}</p>` : ""}
                    ${task.tags && task.tags.trim() ? `<p class="task-tags">🏷️ Tags: ${task.tags.split(",").map(tag => `<span class="tag">#${tag.trim()}</span>`).join(" ")}</p>` : ""}
                    ${task.checklist && task.checklist.trim() ? `<p class="task-checklist">✅ Checklist:<br><ul>${task.checklist.split("\n").map(item => `<li>✅ ${item.trim()}</li>`).join("")}</ul></p>` : ""}
                    ${task.notes && task.notes.trim() ? `<p class="task-notes">📝 Notes:<br> ${task.notes}</p>` : ""}
                </div>

                ${!task.is_completed ? `<button class="pixel-btn complete-task-btn" data-task-id="${task.id}">✅ Complete</button>` : ""}
            </div>
        `;

        if (task.is_completed) {
            completedTasksContainer.innerHTML += taskHTML;
            hasCompletedTasks = true;
        } else {
            activeTasksContainer.innerHTML += taskHTML;
        }
    });

    if (!hasCompletedTasks) {
        completedTasksContainer.innerHTML = "<p>No completed tasks yet ✅</p>";
    }
}

function toggleCompletedTasks() {
    var completedTasks = document.getElementById("completed-tasks");
    var btn = document.querySelector(".toggle-completed-btn");

    if (completedTasks.style.display === "none") {
        completedTasks.style.display = "block";
        btn.textContent = "📂 Hide Completed Tasks";
    } else {
        completedTasks.style.display = "none";
        btn.textContent = "📂 Show Completed Tasks";
    }
}

// document.addEventListener("DOMContentLoaded", function () {
//     // 页面加载后自动调用 fetchAchievements()
//     fetchAchievements();
// });

async function fetchAchievements() {
    try {
        const response = await fetch("/api/user/achievements/", {
            method: "GET",
            headers: {
                "X-CSRFToken": getCookie("csrftoken")
            }
        });

        if (!response.ok) {
            throw new Error("❌ fetch fails");
        }

        const data = await response.json();


        if (Array.isArray(data.achievements)) {
            return data.achievements;
        } else {
            console.warn("❌ invalid format:", data.achievements);
            return [];
        }
    } catch (error) {
        console.error("❌ load fails:", error);
        return [];
    }
}

/**
 * 🎖️ single achie popup
 */
function showAchievementPopup(achievement) {
    const popupContainer = document.querySelector(".achievements-popup");
    console.log("📢 UNLOCK!:", achievement);


    if (!popupContainer) {
        console.error("❌ can't find `.achievements-popup`");
        return;
    }

    if (!achievement || !achievement.name) {
        console.warn("⚠️ invalid data:", achievement);
        return;
    }

    let unlockedTime = achievement.unlocked_at && achievement.unlocked_at !== "unknown"
        ? new Date(achievement.unlocked_at).toLocaleString("en-GB", { year: "numeric", month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit" })
        : "Invalid Date";

    const toast = document.createElement("div");
    toast.className = "achievement-toast";
    toast.innerHTML = `🏅 ${achievement.name} <br> <small>unlocked at: ${unlockedTime}</small>`;
    popupContainer.appendChild(toast);

    setTimeout(() => toast.classList.add("show"), 100);
    setTimeout(() => {
        toast.classList.remove("show");
        setTimeout(() => toast.remove(), 500);
    }, 5000);
}

function createParticles(x, y) {
    for (let i = 0; i < 20; i++) {
        const particle = document.createElement("div");
        particle.className = "pixel-particle";
        particle.style.left = `${x}px`;
        particle.style.top = `${y}px`;

        document.body.appendChild(particle);
        setTimeout(() => particle.remove(), 1000);
    }
}

function getCookie(name) {
    let cookieValue = null;
    document.cookie.split(";").forEach(cookie => {
        if (cookie.trim().startsWith(name + "=")) {
            cookieValue = decodeURIComponent(cookie.split("=")[1]);
        }
    });
    return cookieValue;
}
document.addEventListener("DOMContentLoaded", function () {
    if (navigator.language.startsWith("zh")) {
        document.documentElement.lang = "en";
    }
});

function formatDate(isoString) {
    let date = new Date(isoString);
    return date.toLocaleString("en-GB", { year: "numeric", month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit" });
}

document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll('input[type="datetime-local"]').forEach(input => {
        input.addEventListener("focus", () => forceISOFormat(input));
        forceISOFormat(input); 
    });
});

function forceISOFormat(input) {
    if (!input || !input.value) return;
    let date = new Date(input.value);
    if (!isNaN(date.getTime())) {
        input.value = date.toISOString().slice(0, 16);
    }
}
// function updateRanking() {
//     fetch('/api/get_ranking/')
//         .then(response => response.json())
//         .then(data => {
//             let table = document.getElementById("ranking-table");
//             table.innerHTML = ""; 

//             data.forEach((user, index) => {
//                 let row = `<tr>
//             <td>${index + 1}</td>
//             <td>${user.username}</td>
//             <td>${user.experience} XP</td>
//         </tr>`;
//                 table.innerHTML += row;
//             });
//         });
// }
// setInterval(updateRanking, 5000);  // refresh every 5 seconds
// updateRanking();
function updateCountdown() {
    fetch('/api/get_competition_timer/')
        .then(response => response.json())
        .then(data => {
            let endTime = new Date(data.end_date);
            let now = new Date();
            let timeDiff = endTime - now;

            let days = Math.floor(timeDiff / (1000 * 60 * 60 * 24));
            document.getElementById("countdown").innerHTML =days + " days left!";
        });
}
setInterval(updateCountdown, 60000);  // refresh every minute
updateCountdown();

document.querySelectorAll('.complete-task-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        const taskId = btn.dataset.taskId;
        fetch(`/tasks/${taskId}/complete/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': '{{ csrf_token }}'
            }
        })
        .then(res => res.json())
        .then(data => {
            console.log('Task complete response:', data);
        // refresh the task list
        })
        .catch(err => console.error('Error completing task:', err));
    });
});

function updateRanking() {
    fetch('/api/get_ranking/')
    .then(response => response.json())
    .then(data => {
        let table = document.getElementById("ranking-table");
        table.innerHTML = "";  // clear current content

        data.forEach(entry => {
            if (entry.is_ellipsis) {
                // show ellipsis row
                let row = `<tr><td>...</td><td>...</td><td>...</td></tr>`;
                table.innerHTML += row;
            } else {
                // normal row
                // highlight current user
                let highlightClass = entry.is_current_user ? 'highlight-row' : '';
                let row = `<tr class="${highlightClass}">
                    <td>${entry.rank}</td>
                    <td>${entry.username}</td>
                    <td>${entry.experience} XP</td>
                </tr>`;
                table.innerHTML += row;
            }
        });
    });
}
setInterval(updateRanking, 5000);
updateRanking();
