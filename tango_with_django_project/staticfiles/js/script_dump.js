// document.addEventListener("DOMContentLoaded", function () {
//     document.getElementById("taskTitle").addEventListener("input", predictDifficulty);
//     document.getElementById("taskPriority").addEventListener("change", predictDifficulty);
//     document.getElementById("taskDueDate").addEventListener("change", calculateDuration);
//     document.getElementById("taskStartDate").addEventListener("change", calculateDuration);
//     document.getElementById("taskForm").addEventListener("submit", submitTask);
//     fetchTasks(); // 初始加载任务
//     document.querySelector(".task-list").addEventListener("click", function (event) {
//         if (event.target.closest(".complete-task-btn")) {
//             let taskId = event.target.closest(".complete-task-btn").dataset.taskId;
//             completeTask(taskId, event);
//         }
//     });
// });

// function showToast(message, duration = 3000) {
//     const toast = document.createElement("div");
//     toast.className = "toast";
//     toast.textContent = message;
//     document.body.appendChild(toast);
//     setTimeout(() => toast.remove(), duration);
// }

// /**
//  * 显示/隐藏任务创建表单
//  */
// // function toggleTaskModal() {
// //     let modal = document.getElementById("taskModal");
// //     modal.style.display = (modal.style.display === "none" || modal.style.display === "") ? "block" : "none";
// // }
// // 打开任务创建模态框
// function openTaskModal() {
//     document.getElementById("taskModal").style.display = "flex";
// }

// // 关闭任务创建模态框
// function closeTaskModal() {
//     document.getElementById("taskModal").style.display = "none";
// }

// // 监听 ESC 键，按下后关闭模态框
// window.addEventListener("keydown", function (event) {
//     if (event.key === "Escape") {
//         closeTaskModal();
//     }
// });


// /**
//  * 计算任务时长（基于 Start Time 和 Due Date）
//  */
// function calculateDuration() {
//     let startInput = document.getElementById("taskStartDate").value;
//     let dueInput = document.getElementById("taskDueDate").value;

//     if (!dueInput) return;  // 确保至少有 Due Date

//     let startDate = startInput ? new Date(startInput) : new Date();
//     let dueDate = new Date(dueInput);

//     let durationMinutes = Math.round((dueDate - startDate) / 60000);

//     predictDifficulty(durationMinutes);
//     if (dueDate < startDate) {
//         showToast("截止日期不能早于开始日期");
//         document.getElementById("taskDueDate").value = "";
//         return;
//     }
// }

// /**
//  * 根据任务标题、时长和优先级预测任务难度
//  */
// function predictDifficulty(duration = 30) {
//     let title = document.getElementById("taskTitle").value.toLowerCase();
//     let isHighPriority = document.getElementById("taskPriority").checked;
//     let difficulty = 1;

//     const keywordsHard = ["report", "study", "presentation", "deadline", "research"];
//     const keywordsMedium = ["exercise", "meeting", "cleaning", "shopping"];

//     if (keywordsHard.some(word => title.includes(word))) {
//         difficulty = 3;
//     } else if (keywordsMedium.some(word => title.includes(word))) {
//         difficulty = 2;
//     }

//     if (duration > 120) {
//         difficulty = Math.max(difficulty, 3);
//     } else if (duration > 60) {
//         difficulty = Math.max(difficulty, 2);
//     }

//     if (isHighPriority) {
//         difficulty = Math.min(3, difficulty + 1);
//     }

//     let difficultyDisplay = ["Easy", "Medium", "Hard"];
//     document.getElementById("difficultyDisplay").textContent = difficultyDisplay[difficulty - 1];
//     document.getElementById("taskDifficulty").value = difficulty;
// }

// /**
//  * 提交任务表单
//  */
// async function fetchTasks() {
//     try {
//         const response = await fetch("/api/tasks/", {
//             method: "GET",
//             headers: { "Authorization": `Bearer ${localStorage.getItem("token")}` } // 需要身份认证
//         });

//         if (!response.ok) throw new Error("Failed to load tasks");
//         const tasks = await response.json();
//         updateTaskBoard(tasks);
//         updateTaskMap(tasks);
//     } catch (error) {
//         console.error("任务加载失败:", error);
//     }
// }

// async function submitTask(event) {
//     event.preventDefault();
//     const formData = new FormData(event.target);

//     try {
//         const response = await fetch("/api/tasks/", {
//             method: "POST",
//             headers: {
//                 "X-CSRFToken": getCookie("csrftoken"),
//             },
//             body: formData
//         });

//         if (response.ok) {
//             closeTaskModal();
//             fetchTasks();  // 重新加载任务
//         } else {
//             console.error("任务创建失败");
//         }
//     } catch (error) {
//         console.error("任务提交失败:", error);
//     }
// }


// /**
//  * 任务完成
//  */
// async function completeTask(taskId, event) {
//     try {
//         const response = await fetch(`/api/tasks/${taskId}/complete/`, {
//             method: 'POST',
//             headers: {
//                 'X-CSRFToken': getCookie('csrftoken'),
//                 'Content-Type': 'application/json'
//             }
//         });

//         if (response.ok) {
//             let taskCard = document.getElementById(`task-${taskId}`);
//             if (taskCard) {
//                 let details = taskCard.querySelector(".task-details");
//                 if (details) details.style.display = "none";

//                 let completeButton = taskCard.querySelector(".complete-task-btn");
//                 if (completeButton) completeButton.remove();

//                 let doneBadge = document.createElement("span");
//                 doneBadge.className = "completed-text";
//                 doneBadge.textContent = "✔️ Done";
//                 taskCard.querySelector(".task-header").appendChild(doneBadge);
//             }

//             if (event) createParticles(event.clientX, event.clientY);
//             if (data.exp !== undefined) {
//                 document.getElementById("exp").textContent = data.exp;
//             }
//         } else {
//             console.error("Task completion failed");
//         }
//     } catch (error) {
//         console.error("Task completion request error:", error);
//     }
// }

// /**
//  * 任务地图显示
//  */
// async function fetchTasks() {
//     try {
//         const response = await fetch("/api/tasks/", {
//             method: "GET",
//             headers: {
//                 "Authorization": "Bearer " + localStorage.getItem("token")
//             }
//         });
//         const tasks = await response.json();
//         updateTaskBoard(tasks);
//         updateTaskMap(tasks);
//     } catch (error) {
//         console.error("fetch failed", error);
//     }
// }

// // function updateTaskBoard(tasks) {
// //     const activeTasksContainer = document.querySelector(".task-list");
// //     const completedTasksContainer = document.querySelector(".completed-task-list");

// //     activeTasksContainer.innerHTML = "";
// //     completedTasksContainer.innerHTML = "";

// //     let hasCompletedTasks = false;

// //     tasks.forEach(task => {
// //         console.log("Task ID:", task.id, "Completed:", task.is_completed);

// //         let taskHTML = `
// //             <div class="task-card ${task.is_completed ? "completed" : ""}" id="task-${task.id}">
// //                 <div class="task-header">
// //                     <span class="difficulty-${task.difficulty}">
// //                         ${["Easy", "Medium", "Hard"][task.difficulty - 1]}
// //                     </span>
// //                     ${task.is_completed ? `<span class="completed-text">✔️ Done</span>` : ""}
// //                 </div>
// //                 <p class="task-title">${task.title}</p>

// //                 <div class="task-details">
// //                     ${task.start_date ? `<p class="task-start">🕒 Start: ${formatDate(task.start_date)}</p>` : ""}
// //                     ${task.due_date ? `<p class="task-due">⏳ Due: ${formatDate(task.due_date)}</p>` : ""}
// //                     ${task.tags && task.tags.trim() ? `<p class="task-tags">🏷️ Tags: ${task.tags.split(",").map(tag => `<span class="tag">#${tag.trim()}</span>`).join(" ")}</p>` : ""}
// //                     ${task.checklist && task.checklist.trim() ? `<p class="task-checklist">✅ Checklist:<br><ul>${task.checklist.split("\n").map(item => `<li>✅ ${item.trim()}</li>`).join("")}</ul></p>` : ""}
// //                     ${task.notes && task.notes.trim() ? `<p class="task-notes">📝 Notes:<br> ${task.notes}</p>` : ""}
// //                 </div>

// //                 ${!task.is_completed ? `<button class="pixel-btn complete-task-btn" data-task-id="${task.id}">✅ Complete</button>` : ""}
// //             </div>
// //         `;

// //         if (task.is_completed) {
// //             completedTasksContainer.innerHTML += taskHTML;
// //             hasCompletedTasks = true;
// //         } else {
// //             activeTasksContainer.innerHTML += taskHTML;
// //         }
// //     });

// //     if (!hasCompletedTasks) {
// //         completedTasksContainer.innerHTML = "<p>No completed tasks yet ✅</p>";
// //     }
// // }
// function updateTaskBoard(tasks) {
//     const activeTasksContainer = document.querySelector(".task-list");
//     const completedTasksContainer = document.querySelector(".completed-task-list");

//     activeTasksContainer.innerHTML = "";
//     completedTasksContainer.innerHTML = "";

//     tasks.forEach(task => {
//         let checklistHTML = "";
//         if (task.checklist && task.checklist.trim() !== "") {
//             checklistHTML = `
//                 <p class="task-checklist">✅ Checklist:</p>
//                 <ul>
//                     ${task.checklist.split("\n").map(item => {
//                 const isChecked = item.startsWith("[x] "); // 解析已完成任务项
//                 const cleanItem = isChecked ? item.replace("[x] ", "") : item;

//                 return `
//                             <li>
//                                 <input type="checkbox" class="checklist-item" data-task-id="${task.id}" 
//                                     data-item-text="${cleanItem}" ${isChecked ? "checked" : ""}>
//                                 ${cleanItem}
//                             </li>
//                         `;
//             }).join("")}
//                 </ul>
//             `;
//         }

//         let taskHTML = `
//             <div class="task-card ${task.is_completed ? "completed" : ""}" id="task-${task.id}">
//                 <div class="task-header">
//                     <span class="difficulty-${task.difficulty}">
//                         ${["Easy", "Medium", "Hard"][task.difficulty - 1]}
//                     </span>
//                     ${task.is_completed ? `<span class="completed-text">✔️ Done</span>` : ""}
//                 </div>
//                 <p class="task-title">${task.title}</p>

//                 <div class="task-details">
//                     ${task.start_date ? `<p class="task-start">🕒 Start: ${formatDate(task.start_date)}</p>` : ""}
//                     ${task.due_date ? `<p class="task-due">⏳ Due: ${formatDate(task.due_date)}</p>` : ""}
//                     ${checklistHTML}
//                     <p class="task-notes">📝 Notes:</p>
//                     <textarea class="editable-notes" data-task-id="${task.id}">${task.notes || ""}</textarea>
//                 </div>

//                 ${!task.is_completed ? `<button class="pixel-btn complete-task-btn" data-task-id="${task.id}">✅ Complete</button>` : ""}
//             </div>
//         `;

//         if (task.is_completed) {
//             completedTasksContainer.innerHTML += taskHTML;
//         } else {
//             activeTasksContainer.innerHTML += taskHTML;
//         }
//     });

//     // 监听勾选 Checklist 事件
//     document.querySelectorAll(".checklist-item").forEach(checkbox => {
//         checkbox.addEventListener("change", event => toggleChecklistItem(event.target));
//     });

//     // 监听编辑 Notes 事件
//     document.querySelectorAll(".editable-notes").forEach(el => {
//         el.addEventListener("change", event => updateTaskField(event.target.dataset.taskId, "notes", event.target.value));
//     });
// }


// // function updateTaskBoard(tasks) {
// //     const taskList = document.querySelector(".task-list");
// //     taskList.innerHTML = "";

// //     tasks.forEach(task => {
// //         let taskElement = document.createElement("div");
// //         taskElement.className = `task-card ${task.is_completed ? "completed" : ""}`;
// //         taskElement.id = `task-${task.id}`;

// //         // 构建任务详情
// //         let taskHTML = `
// //             <div class="task-header">
// //                 <span class="difficulty-${task.difficulty}">
// //                     ${["Easy", "Medium", "Hard"][task.difficulty - 1]}
// //                 </span>
// //                 ${task.is_completed ? `<span class="completed-text">✔️ Done</span>` : ""}
// //                 <p class="task-title">${task.title}</p>
// //             </div>
// //             <div class="task-details" style="display: ${task.is_completed ? 'none' : 'block'};">
// //                 ${task.start_date ? `<p class="task-start">🚀 Start: <span>${formatDate(task.start_date)}</span></p>` : ""}
// //                 ${task.due_date ? `<p class="task-due">⏳ Due: <span>${formatDate(task.due_date)}</span></p>` : ""}
// //         `;

// //         // **渲染 Tags（如果有的话）**
// //         if (task.tags && task.tags.trim() !== "") {
// //             let tagsHTML = task.tags.split(",").map(tag => `#${tag.trim()}`).join(" ");
// //             taskHTML += `<p class="task-tags">🏷️ Tags: ${tagsHTML}</p>`;
// //         }

// //         // **渲染 Checklist（如果有的话）**
// //         if (task.checklist && task.checklist.trim() !== "") {
// //             let checklistHTML = task.checklist.split("\n").map(item => `✅ ${item.trim()}`).join("<br>");
// //             taskHTML += `<p class="task-checklist">✅ Checklist:<br>${checklistHTML}</p>`;
// //         }

// //         // **渲染 Notes（如果有的话）**
// //         if (task.notes && task.notes.trim() !== "") {
// //             taskHTML += `<p class="task-notes">📝 Notes:<br>${task.notes}</p>`;
// //         }

// //         taskHTML += `</div>`;  // 关闭 `task-details`

// //         // **渲染 "Complete" 按钮**
// //         if (!task.is_completed) {
// //             taskHTML += `<button class="pixel-btn complete-task-btn" data-task-id="${task.id}">✅ Complete</button>`;
// //         }

// //         taskElement.innerHTML = taskHTML;
// //         taskList.appendChild(taskElement);
// //     });

// //     taskList.innerHTML = `
// //     <div id="active-tasks">
// //         ${activeTasksHTML || "<p>No active tasks 🎯</p>"}
// //     </div>
// //     <button class="pixel-btn toggle-completed-btn" onclick="toggleCompletedTasks()">📂 Show Completed Tasks</button>
// //     <div id="completed-tasks" style="display: none;">
// //         ${completedTasksHTML || "<p>No completed tasks yet ✅</p>"}
// //     </div>
// // `;
// // }
// function toggleCompletedTasks() {
//     var completedTasks = document.getElementById("completed-tasks");
//     var btn = document.querySelector(".toggle-completed-btn");

//     if (completedTasks.style.display === "none") {
//         completedTasks.style.display = "block";
//         btn.textContent = "📂 Hide Completed Tasks";
//     } else {
//         completedTasks.style.display = "none";
//         btn.textContent = "📂 Show Completed Tasks";
//     }
// }
// /**
//  * 更新任务地图
//  */
// function updateTaskMap(tasks) {
//     const map = document.querySelector(".pixel-map");
//     map.innerHTML = "";

//     tasks.forEach(task => {
//         let mapTile = document.createElement("div");
//         mapTile.className = `map-tile ${task.is_completed ? "completed" : ""}`;
//         mapTile.dataset.taskId = task.id;
//         mapTile.dataset.positionX = task.position_x || 1;
//         mapTile.dataset.positionY = task.position_y || 1;

//         mapTile.style.gridColumn = task.position_x || 1;
//         mapTile.style.gridRow = task.position_y || 1;

//         mapTile.innerHTML = task.difficulty === 3 ? "🔥" : "📜";
//         map.appendChild(mapTile);
//     });
// }

// /**
//  * 粒子特效
//  */
// function createParticles(x, y) {
//     for (let i = 0; i < 20; i++) {
//         const particle = document.createElement("div");
//         particle.className = "pixel-particle";
//         particle.style.left = `${x}px`;
//         particle.style.top = `${y}px`;

//         document.body.appendChild(particle);
//         setTimeout(() => particle.remove(), 1000);
//     }
// }

// /**
//  * 获取 CSRF 令牌
//  */
// function getCookie(name) {
//     let cookieValue = null;
//     document.cookie.split(";").forEach(cookie => {
//         if (cookie.trim().startsWith(name + "=")) {
//             cookieValue = decodeURIComponent(cookie.split("=")[1]);
//         }
//     });
//     return cookieValue;
// }

// /**
//  * 格式化日期
//  */
// function formatDate(isoString) {
//     let date = new Date(isoString);
//     return date.toLocaleString();
// }
// async function toggleChecklistItem(taskId, itemText, checkbox) {
//     try {
//         const response = await fetch(`/api/tasks/${taskId}/toggle-checklist/`, {
//             method: "PATCH",
//             headers: {
//                 "Content-Type": "application/json",
//                 "X-CSRFToken": getCookie("csrftoken")
//             },
//             body: JSON.stringify({
//                 item_text: itemText,
//                 completed: checkbox.checked
//             })
//         });

//         if (response.ok) {
//             showToast("Checklist item updated!");
//         } else {
//             throw new Error("Failed to update checklist item");
//         }
//     } catch (error) {
//         console.error("Error updating checklist item:", error);
//     }
// }

// async function updateChecklist(taskId) {
//     try {
//         let checklistContainer = document.querySelector(`#checklist-${taskId}`);
//         let checklistItems = Array.from(checklistContainer.querySelectorAll("li input")).map(checkbox => ({
//             text: checkbox.nextSibling.nodeValue.trim(),
//             completed: checkbox.checked
//         }));

//         const response = await fetch(`/api/tasks/${taskId}/update-checklist/`, {
//             method: "PATCH",
//             headers: {
//                 "Content-Type": "application/json",
//                 "X-CSRFToken": getCookie("csrftoken")
//             },
//             body: JSON.stringify({ checklist_items: checklistItems })
//         });

//         if (response.ok) {
//             showToast("Checklist updated successfully!");
//         } else {
//             throw new Error("Failed to update checklist");
//         }
//     } catch (error) {
//         console.error("Error updating checklist:", error);
//     }
// }

