document.addEventListener("DOMContentLoaded", function () {
    initEventListeners();
    fetchTasks();
    fetchAchievements();
});

/** 
 * 🚀 1️⃣ 事件监听初始化
 * 绑定事件到按钮和输入框
 */
function initEventListeners() {
    document.getElementById("taskForm").addEventListener("submit", submitTask);
    document.querySelector(".toggle-completed-btn").addEventListener("click", toggleCompletedTasks);
}

/** 
 * 📋 2️⃣ 获取任务数据
 * 从后端 API 加载任务
 */
async function fetchTasks() {
    try {
        const response = await fetch("/api/tasks/");
        if (!response.ok) throw new Error("任务加载失败");

        const tasks = await response.json();
        updateTaskBoard(tasks);
        updateTaskMap(tasks);
    } catch (error) {
        console.error("❌ 任务加载错误:", error);
    }
}

/** 
 * 🎯 3️⃣ 提交新任务
 * 处理任务创建表单提交
 */
async function submitTask(event) {
    event.preventDefault();
    const formData = new FormData(event.target);

    try {
        const response = await fetch("/api/tasks/", {
            method: "POST",
            headers: { "X-CSRFToken": getCookie("csrftoken") },
            body: formData
        });

        if (response.ok) {
            closeTaskModal();
            fetchTasks();
        } else {
            console.error("❌ 任务创建失败");
        }
    } catch (error) {
        console.error("❌ 任务提交错误:", error);
    }
}

/** 
 * ✅ 4️⃣ 完成任务
 * 向后端发送任务完成请求
 */
async function completeTask(taskId, event) {
    try {
        const response = await fetch(`/api/tasks/${taskId}/complete/`, {
            method: "POST",
            headers: { "X-CSRFToken": getCookie("csrftoken") }
        });

        if (response.ok) {
            console.log(`✔️ 任务 ${taskId} 完成`);
            fetchTasks();
            fetchAchievements();
        } else {
            console.error("❌ 任务完成失败");
        }
    } catch (error) {
        console.error("❌ 任务完成请求错误:", error);
    }
}

/** 
 * 🏆 5️⃣ 获取成就数据
 * 从后端 API 获取已解锁成就
 */
async function fetchAchievements() {
    try {
        const response = await fetch("/api/achievements/");
        if (!response.ok) throw new Error("成就加载失败");

        const achievements = await response.json();
        updateAchievementsUI(achievements);
    } catch (error) {
        console.error("❌ 成就加载错误:", error);
    }
}

/** 
 * 🗺️ 6️⃣ 更新成就 UI
 * 在前端显示已解锁的成就
 */
function updateAchievementsUI(achievements) {
    const map = document.querySelector(".achievements");
    map.innerHTML = achievements
        .filter(a => a.unlocked)
        .map(a => `<div class="map-tile unlocked">🏆 ${a.name}</div>`)
        .join("");
}

/** 
 * 🎯 7️⃣ 更新任务列表
 * 处理任务的显示逻辑
 */
function updateTaskBoard(tasks) {
    const activeTasksContainer = document.querySelector(".task-list");
    const completedTasksContainer = document.querySelector(".completed-task-list");

    activeTasksContainer.innerHTML = "";
    completedTasksContainer.innerHTML = "";

    tasks.forEach(task => {
        const taskHTML = `
            <div class="task-card ${task.is_completed ? "completed" : ""}" id="task-${task.id}">
                <div class="task-header">
                    <span class="difficulty-${task.difficulty}">
                        ${["Easy", "Medium", "Hard"][task.difficulty - 1]}
                    </span>
                    ${task.is_completed ? `<span class="completed-text">✔️ Done</span>` : ""}
                </div>
                <p class="task-title">${task.title}</p>
                <button class="pixel-btn complete-task-btn" data-task-id="${task.id}">✅ Complete</button>
            </div>
        `;

        if (task.is_completed) {
            completedTasksContainer.innerHTML += taskHTML;
        } else {
            activeTasksContainer.innerHTML += taskHTML;
        }
    });

    attachTaskCompletionListeners();
}

/** 
 * 🎯 8️⃣ 绑定完成任务按钮
 * 给新生成的任务按钮绑定事件
 */
function attachTaskCompletionListeners() {
    document.querySelectorAll(".complete-task-btn").forEach(button => {
        button.addEventListener("click", function () {
            completeTask(button.dataset.taskId);
        });
    });
}

/** 
 * 📍 9️⃣ 更新任务地图
 * 任务状态映射到地图
 */
function updateTaskMap(tasks) {
    const map = document.querySelector(".pixel-map");
    map.innerHTML = tasks
        .map(task => `
            <div class="map-tile ${task.is_completed ? "completed" : ""}" 
                 data-task-id="${task.id}" 
                 data-position-x="${task.position_x}" 
                 data-position-y="${task.position_y}">
                ${task.difficulty === 3 ? "🔥" : "📜"}
            </div>
        `)
        .join("");
}

/** 
 * 🎭 🔄 10️⃣ 显示/隐藏已完成任务
 */
function toggleCompletedTasks() {
    const completedTaskSection = document.querySelector(".completed-task-list");
    const toggleButton = document.querySelector(".toggle-completed-btn");

    completedTaskSection.style.display = completedTaskSection.style.display === "none" ? "block" : "none";
    toggleButton.innerHTML = completedTaskSection.style.display === "block"
        ? "📂 Hide Completed Tasks"
        : "📂 Show Completed Tasks";
}

/** 
 * 📝 11️⃣ 获取 CSRF 令牌
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
