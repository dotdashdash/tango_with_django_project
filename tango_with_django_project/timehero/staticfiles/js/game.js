// 完成任务
async function completeTask(taskId) {
    try {
      const response = await fetch(`/api/tasks/${taskId}/complete/`, {
        method: 'POST',
        headers: {
          'X-CSRFToken': getCookie('csrftoken'),
          'Content-Type': 'application/json'
        }
      });
      
      if(response.ok) {
        // 粒子特效
        createParticles(event.clientX, event.clientY);
        // 刷新数据
        setTimeout(() => location.reload(), 800);
      }
    } catch (error) {
      console.error('任务完成失败:', error);
    }
  }
  
  // 像素粒子特效
  function createParticles(x, y) {
    for(let i = 0; i < 20; i++) {
      const particle = document.createElement('div');
      particle.className = 'pixel-particle';
      particle.style.left = `${x}px`;
      particle.style.top = `${y}px`;
      
      // 随机运动轨迹
      const angle = (Math.PI * 2 * i) / 20;
      const speed = Math.random() * 5 + 3;
      const vx = Math.cos(angle) * speed;
      const vy = Math.sin(angle) * speed;
      
      particle.style.setProperty('--vx', vx);
      particle.style.setProperty('--vy', vy);
      
      document.body.appendChild(particle);
      setTimeout(() => particle.remove(), 1000);
    }
  }
  
  // 辅助函数：获取Cookie
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }