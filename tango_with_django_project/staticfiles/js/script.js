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

// 打开任务创建模态框
function openTaskModal() {
    document.getElementById("taskModal").style.display = "flex";
}

// 关闭任务创建模态框
function closeTaskModal() {
    document.getElementById("taskModal").style.display = "none";
}

// 监听 ESC 键，按下后关闭模态框
window.addEventListener("keydown", function (event) {
    if (event.key === "Escape") {
        closeTaskModal();
    }
});


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
            closeTaskModal();
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
            const data = await response.json();
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
            if (data.level !== undefined) {
                document.getElementById("level").textContent = data.level;
            }
            if (Array.isArray(data.all_achievements) && data.all_achievements.length > 0) {
                updateTaskMap(data.all_achievements);  // ✅ 改用 `all_achievements`
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

document.addEventListener("DOMContentLoaded", function() {
    // 页面加载后自动调用 fetchAchievements()
    fetchAchievements();
});

async function fetchAchievements() {
    try {
        const response = await fetch("/api/user/achievements/", {
            method: "GET",
            headers: {
                // 如果你需要 CSRF 或 Token，写在这里
                "X-CSRFToken": getCookie("csrftoken")
                // "Authorization": `Bearer ${localStorage.getItem("token")}`
            }
        });

        if (!response.ok) {
            throw new Error("❌ 获取成就失败");
        }

        // 解析后端返回的 JSON
        const data = await response.json();
        console.log("🎉 成就数据:", data);

        // data.achievements 应该是一个字符串数组
        if (Array.isArray(data.achievements)) {
            updateTaskMap(data.achievements);
        } else {
            console.warn("❌ 后端返回的成就不是数组:", data.achievements);
        }
    } catch (error) {
        console.error("❌ 加载成就失败:", error);
    }
}

function updateTaskMap(allAchievements) {
    console.log("📌 解析解锁的成就 (原始数据):", allAchievements);

    // 获取 #achievements-container 容器
    const container = document.getElementById("achievements-container");
    if (!container) {
        console.error("❌ 找不到 `#achievements-container`，无法显示成就");
        return;
    }

    // 不清空容器，避免覆盖旧成就
    // 如果想每次都只显示最新，可以取消注释下面这行
    // container.innerHTML = "";

    // 遍历所有成就，追加到页面
    allAchievements.forEach(feature => {
        console.log("🔹 解析的成就内容:", feature, "| 类型:", typeof feature);

        if (typeof feature === "string") {
            // 创建一个 div，用于显示单条成就
            const featureDiv = document.createElement("div");
            featureDiv.className = "achievement-item";
            featureDiv.textContent = `🏅 ${feature}`;

            // 避免重复插入相同成就
            if (![...container.children].some(child => child.textContent === featureDiv.textContent)) {
                container.appendChild(featureDiv);
                console.log("✅ 成就已添加:", feature);
            } else {
                console.warn("⚠️ 该成就已存在，跳过:", feature);
            }
        } else {
            console.warn("❌ 无效的成就数据 (不是字符串):", feature);
        }
    });

    console.log("✅ 成就显示更新完成！");
}



// function updateTaskMap(allAchievements) {
//     console.log("📌 解析解锁的成就 (原始数据):", allAchievements);

//     // ✅ 确保 `allAchievements` 是数组
//     if (!Array.isArray(allAchievements)) {
//         console.error("❌ `allAchievements` 不是数组: ", allAchievements);
//         return;
//     }

//     // 🚀 **获取正确的容器**
//     const achievementsContainer = document.getElementById("achievements-container");
//     if (!achievementsContainer) {
//         console.error("❌ 找不到 `#achievements-container`，无法更新任务地图");
//         return;
//     }

//     // ✅ **不清空** `achievements-container`，防止覆盖旧成就
//     // achievementsContainer.innerHTML = ""; ❌ **不要清空**

//     // ✅ 遍历 `allAchievements`，追加新成就
//     allAchievements.forEach(feature => {
//         console.log("🔹 解析的成就内容:", feature, "| 类型:", typeof feature);

//         if (typeof feature === "string") {  // ✅ 只接受字符串
//             let featureElement = document.createElement("div");
//             featureElement.className = "map-tile achievement";
//             featureElement.textContent = `🏅 ${feature}`;

//             // **避免重复插入相同成就**
//             if (![...achievementsContainer.children].some(child => child.textContent === featureElement.textContent)) {
//                 achievementsContainer.appendChild(featureElement);
//                 console.log("✅ 成就已添加:", feature);
//             } else {
//                 console.warn("⚠️ 该成就已存在，跳过:", feature);
//             }
//         } else {
//             console.warn("❌ 无效的成就数据 (不是字符串):", feature);
//         }
//     });

//     console.log("✅ 任务地图更新完成！");
// }


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
document.addEventListener("DOMContentLoaded", function () {
    if (navigator.language.startsWith("zh")) {
        document.documentElement.lang = "en";
    }
});

/**
 * 格式化日期
 */
function formatDate(isoString) {
    let date = new Date(isoString);
    return date.toLocaleString("en-GB", { year: "numeric", month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit" });
}

/**
 * 确保 datetime-local 格式一致
 */
document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll('input[type="datetime-local"]').forEach(input => {
        input.addEventListener("focus", () => forceISOFormat(input));
        forceISOFormat(input); // 确保格式
    });
});

function forceISOFormat(input) {
    if (!input || !input.value) return;
    let date = new Date(input.value);
    if (!isNaN(date.getTime())) {
        input.value = date.toISOString().slice(0, 16);
    }
}
