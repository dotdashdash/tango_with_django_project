document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("taskTitle").addEventListener("input", predictDifficulty);
    document.getElementById("taskPriority").addEventListener("change", predictDifficulty);
    document.getElementById("taskDueDate").addEventListener("change", calculateDuration);
    document.getElementById("taskStartDate").addEventListener("change", calculateDuration);
    document.getElementById("taskForm").addEventListener("submit", submitTask);
    fetchTasks(); // 初始加载任务
    document.querySelector(".task-list").addEventListener("click", function (event) {
        if (event.target.closest(".complete-task-btn")) {
            let taskId = event.target.closest(".complete-task-btn").dataset.taskId;
            completeTask(taskId, event);
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

/**
 * 显示/隐藏任务创建表单
 */
function toggleTaskModal() {
    let modal = document.getElementById("taskModal");
    modal.style.display = (modal.style.display === "none" || modal.style.display === "") ? "block" : "none";
}

/**
 * 计算任务时长（基于 Start Time 和 Due Date）
 */
function calculateDuration() {
    let startInput = document.getElementById("taskStartDate").value;
    let dueInput = document.getElementById("taskDueDate").value;

    if (!dueInput) return;  // 确保至少有 Due Date

    let startDate = startInput ? new Date(startInput) : new Date();
    let dueDate = new Date(dueInput);

    let durationMinutes = Math.round((dueDate - startDate) / 60000);

    predictDifficulty(durationMinutes);
    if (dueDate < startDate) {
        showToast("截止日期不能早于开始日期");
        document.getElementById("taskDueDate").value = "";
        return;
    }
}

/**
 * 根据任务标题、时长和优先级预测任务难度
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
 * 提交任务表单
 */
async function fetchTasks() {
    try {
        const response = await fetch("/api/tasks/", {
            method: "GET",
            headers: { "Authorization": `Bearer ${localStorage.getItem("token")}` } // 需要身份认证
        });

        if (!response.ok) throw new Error("Failed to load tasks");
        const tasks = await response.json();
        updateTaskBoard(tasks);
        updateTaskMap(tasks);
    } catch (error) {
        console.error("任务加载失败:", error);
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
            toggleTaskModal();
            fetchTasks();  // 重新加载任务
        } else {
            console.error("任务创建失败");
        }
    } catch (error) {
        console.error("任务提交失败:", error);
    }
}


/**
 * 任务完成
 */
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
        } else {
            console.error("Task completion failed");
        }
    } catch (error) {
        console.error("Task completion request error:", error);
    }
}

/**
 * 任务地图显示
 */
async function fetchTasks() {
    try {
        const response = await fetch("/api/tasks/",{
            method: "GET",
            headers:{
                "Authorization": "Bearer " + localStorage.getItem("token")
            }
        });
        const tasks = await response.json();
        updateTaskBoard(tasks);
        updateTaskMap(tasks);
    } catch (error) {
        console.error("fetch failed", error);
    }
}

/**
 * 更新任务面板
 */
function updateTaskBoard(tasks) {
    const taskList = document.querySelector(".task-list");
    taskList.innerHTML = ""; 

    tasks.forEach(task => {
        let taskElement = document.createElement("div");
        taskElement.className = `task-card ${task.is_completed ? "completed" : ""}`;
        taskElement.id = `task-${task.id}`;

        taskElement.innerHTML = `
            <div class="task-header">
                <span class="difficulty-${task.difficulty}">
                    ${["Easy", "Medium", "Hard"][task.difficulty - 1]}
                </span>
                ${task.is_completed ? `<span class="completed-text">✔️ Done</span>` : ""}
                <p class="task-title">${task.title}</p>
            </div>
            <div class="task-details" style="display: ${task.is_completed ? 'none' : 'block'};">
                ${task.start_date ? `<p class="task-start">🚀 Start: <span>${formatDate(task.start_date)}</span></p>` : ""}
                ${task.due_date ? `<p class="task-due">⏳ Due: <span>${formatDate(task.due_date)}</span></p>` : ""}
            </div>
            ${!task.is_completed ? `<button class="pixel-btn complete-task-btn" data-task-id="${task.id}">✅ Complete</button>` : ""}
        `;

        taskList.appendChild(taskElement);
    });
}

/**
 * 更新任务地图
 */
function updateTaskMap(tasks) {
    const map = document.querySelector(".pixel-map");
    map.innerHTML = ""; 

    tasks.forEach(task => {
        let mapTile = document.createElement("div");
        mapTile.className = `map-tile ${task.is_completed ? "completed" : ""}`;
        mapTile.dataset.taskId = task.id;
        mapTile.dataset.positionX = task.position_x || 1;
        mapTile.dataset.positionY = task.position_y || 1;

        mapTile.style.gridColumn = task.position_x || 1;
        mapTile.style.gridRow = task.position_y || 1;

        mapTile.innerHTML = task.difficulty === 3 ? "🔥" : "📜";
        map.appendChild(mapTile);
    });
}

/**
 * 粒子特效
 */
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

/**
 * 获取 CSRF 令牌
 */
function getCookie(name) {
    let cookieValue = null;
    document.cookie.split(";").forEach(cookie => {
        if (cookie.trim().startsWith(name + "=")) {
            cookieValue = decodeURIComponent(cookie.split("=")[1]);
        }
    });
    return cookieValue;
}

/**
 * 格式化日期
 */
function formatDate(isoString) {
    let date = new Date(isoString);
    return date.toLocaleString();
}
