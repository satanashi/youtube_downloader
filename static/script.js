// Создаем анимированный фон
function createAnimatedBackground() {
    const container = document.createElement('div');
    container.className = 'background-container';
    document.body.appendChild(container);
    
    // Цветовая палитра для анимации
    const colors = [
        '#ff9a00', '#f44336', '#6a11cb', '#2575fc', 
        '#00e676', '#ff3366', '#9c27b0', '#00bcd4',
        '#ffeb3b', '#e91e63', '#3f51b5', '#009688'
    ];
    
    // Создаем массив для хранения кругов
    const circles = [];
    const positions = [];
    
    // Создаем 5 больших анимированных кругов
    for (let i = 0; i < 5; i++) {
        setTimeout(() => {
            createCircle(container, colors, positions, circles);
        }, i * 1000);
    }
}

// Проверяем минимальное расстояние между кругами
function checkMinDistance(newX, newY, existingPositions, minDistance = 250) {
    for (let pos of existingPositions) {
        const distance = Math.sqrt(Math.pow(newX - pos.x, 2) + Math.pow(newY - pos.y, 2));
        if (distance < minDistance) {
            return false;
        }
    }
    return true;
}

// Создаем один анимированный круг
function createCircle(container, colors, positions, circles) {
    const circle = document.createElement('div');
    circle.className = 'animated-circle';
    
    // Большие размеры кругов
    const size = Math.random() * 300 + 300; // 300-600px
    
    // Находим позицию с минимальным расстоянием от других кругов
    let validPosition = false;
    let attempts = 0;
    let x, y;
    
    while (!validPosition && attempts < 30) {
        // Генерируем случайную позицию в пределах экрана с отступами
        x = Math.random() * (window.innerWidth - size - 100) + 50;
        y = Math.random() * (window.innerHeight - size - 100) + 50;
        
        if (checkMinDistance(x, y, positions)) {
            validPosition = true;
        }
        attempts++;
    }
    
    if (!validPosition) {
        // Если не удалось найти хорошую позицию, используем любую с отступами
        x = Math.random() * (window.innerWidth - size - 100) + 50;
        y = Math.random() * (window.innerHeight - size - 100) + 50;
    }
    
    // Фиксируем цвет для этого круга
    let currentColorIndex = Math.floor(Math.random() * colors.length);
    let currentColor = colors[currentColorIndex];
    
    circle.style.width = `${size}px`;
    circle.style.height = `${size}px`;
    circle.style.left = `${x}px`;
    circle.style.top = `${y}px`;
    circle.style.backgroundColor = currentColor;
    
    container.appendChild(circle);
    
    // Плавное появление
    setTimeout(() => {
        circle.style.opacity = '0.6';
    }, 100);
    
    // Добавляем позицию в массив
    positions.push({x: x, y: y});
    const circleIndex = circles.length;
    circles.push({element: circle, x: x, y: y, positionsIndex: positions.length - 1});
    
    // Плавное изменение цвета каждые 8-12 секунд
    setInterval(() => {
        const newColorIndex = (currentColorIndex + 1) % colors.length;
        currentColor = colors[newColorIndex];
        circle.style.backgroundColor = currentColor;
        currentColorIndex = newColorIndex;
    }, Math.random() * 4000 + 8000);
    
    // Плавное перемещение круга
    function moveCircle() {
        setTimeout(() => {
            // Генерируем новую позицию с учетом минимального расстояния
            let newX, newY;
            let validNewPosition = false;
            let moveAttempts = 0;
            
            while (!validNewPosition && moveAttempts < 20) {
                const moveDistance = Math.random() * 80 + 40; // 40-120px
                const moveAngle = Math.random() * 2 * Math.PI;
                
                newX = Math.max(50, Math.min(window.innerWidth - size - 50, 
                    parseFloat(circle.style.left) + moveDistance * Math.cos(moveAngle)));
                newY = Math.max(50, Math.min(window.innerHeight - size - 50, 
                    parseFloat(circle.style.top) + moveDistance * Math.sin(moveAngle)));
                
                // Проверяем расстояние до других кругов
                validNewPosition = true;
                for (let i = 0; i < positions.length; i++) {
                    if (i !== circles[circleIndex]?.positionsIndex) {
                        const distance = Math.sqrt(Math.pow(newX - positions[i].x, 2) + Math.pow(newY - positions[i].y, 2));
                        if (distance < 200) {
                            validNewPosition = false;
                            break;
                        }
                    }
                }
                
                moveAttempts++;
            }
            
            if (!validNewPosition) {
                // Если не удалось найти хорошую позицию, используем любую с отступами
                const moveDistance = Math.random() * 60 + 30;
                const moveAngle = Math.random() * 2 * Math.PI;
                newX = Math.max(50, Math.min(window.innerWidth - size - 50, 
                    parseFloat(circle.style.left) + moveDistance * Math.cos(moveAngle)));
                newY = Math.max(50, Math.min(window.innerHeight - size - 50, 
                    parseFloat(circle.style.top) + moveDistance * Math.sin(moveAngle)));
            }
            
            // Обновляем позицию в массиве
            if (circles[circleIndex]) {
                positions[circles[circleIndex].positionsIndex] = {x: newX, y: newY};
            }
            
            circle.style.transition = 'all 2s ease-in-out';
            circle.style.left = `${newX}px`;
            circle.style.top = `${newY}px`;
            
            // После завершения анимации запускаем следующее перемещение
            setTimeout(moveCircle, Math.random() * 2000 + 1500);
        }, Math.random() * 1000 + 500);
    }
    
    // Начинаем плавное перемещение
    moveCircle();
    
    // Удаляем круг через 90-120 секунд и создаем новый
    setTimeout(() => {
        circle.style.transition = 'opacity 1s ease-in-out';
        circle.style.opacity = '0';
        setTimeout(() => {
            if (circle.parentNode) {
                circle.parentNode.removeChild(circle);
                // Удаляем из массивов
                if (circles[circleIndex]) {
                    positions.splice(circles[circleIndex].positionsIndex, 1);
                }
            }
            // Создаем новый круг
            createCircle(container, colors, positions, circles);
        }, 1000);
    }, Math.random() * 30000 + 90000);
}

// Функциональность выбора типа скачивания
let downloadType = 'video'; // 'video' или 'audio'

function setDownloadType(type) {
    downloadType = type;
    document.querySelectorAll('.type-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`[data-type="${type}"]`).classList.add('active');
}

// Функция скачивания видео
async function downloadVideo() {
    const url = document.getElementById('videoUrl').value.trim();
    const resultDiv = document.getElementById('result');
    const loader = document.getElementById('loader');

    if (!url) {
        resultDiv.textContent = "⚠️ Введите ссылку";
        return;
    }

    resultDiv.textContent = "";
    loader.style.display = "block"; // Показываем анимацию загрузки

    try {
        const response = await fetch('/download', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 
                url: url,
                type: downloadType
            })
        });

        // Проверяем статус ответа
        if (response.ok) {
            // Если всё хорошо, считаем, что файл скачан
            resultDiv.innerHTML = `<span class="success">✅ Файл успешно скачан!</span>`;
            loader.style.display = "none"; // Скрываем анимацию загрузки
        } else {
            // Если ошибка, показываем сообщение
            const data = await response.json();
            resultDiv.textContent = `❌ Ошибка: ${data.error}`;
            loader.style.display = "none"; // Скрываем анимацию загрузки
        }
    } catch (error) {
        loader.style.display = "none"; // Скрываем анимацию загрузки
        console.error("Ошибка:", error);
        resultDiv.textContent = `⚠️ Произошла ошибка. Попробуйте другое видео.`;
    }
}

// Инициализируем анимированный фон при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    createAnimatedBackground();
    
    // Устанавливаем обработчики событий для кнопок типа скачивания
    document.querySelectorAll('.type-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            setDownloadType(btn.dataset.type);
        });
    });
    
    // Устанавливаем обработчик для кнопки скачивания
    document.querySelector('button').addEventListener('click', downloadVideo);
});