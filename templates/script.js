let startButton = document.getElementById('start-button');
let processButton = document.getElementById('process-button');
let restartButton = document.getElementById('restart-button');
let timerElement = document.getElementById('timer');
let ecosystemStatus = document.getElementById('ecosystem-status');
let fishCount = 0;
let trashCount = 0;
let timerInterval = null;

// Crear y mover una imagen dentro de un contenedor específico
function createAndMoveImage(src, containerId) {
    const img = document.createElement('img');
    img.src = src;
    img.alt = 'Elemento';
    img.style.width = '150px';
    img.style.height = '150px';
    img.style.position = 'absolute';
    document.getElementById(containerId).appendChild(img);

    let posX = Math.random() * (window.innerWidth - 150);
    let posY = Math.random() * (window.innerHeight - 150);
    let speedX = Math.random() * 2 + 1;
    let speedY = Math.random() * 2 + 1;
    let directionX = Math.random() > 0.5 ? 1 : -1;
    let directionY = Math.random() > 0.5 ? 1 : -1;

    img.style.left = posX + 'px';
    img.style.top = posY + 'px';

    const moveInterval = setInterval(() => {
        posX += speedX * directionX;
        posY += speedY * directionY;

        if (posX >= window.innerWidth - 150 || posX <= 0) directionX *= -1;
        if (posY >= window.innerHeight - 150 || posY <= 0) directionY *= -1;

        img.style.left = posX + 'px';
        img.style.top = posY + 'px';
    }, 20);

    img.moveInterval = moveInterval;
    return img;
}

// Iniciar el temporizador del juego
function startTimer() {
    let countdown = 10;
    startButton.style.display = 'none';
    processButton.style.display = 'none';
    timerElement.style.display = 'block';

    timerInterval = setInterval(() => {
        countdown--;
        timerElement.textContent = `Tiempo restante: ${countdown}s`;

        if (countdown <= 0) {
            clearInterval(timerInterval);
            endGame();
        }
    }, 1000);
}

// Determinar y mostrar el estado del ecosistema al finalizar el juego
function endGame() {
    const result = fishCount > trashCount ? "animals" : "trash";
    updateEcosystemState(result);
    timerElement.style.display = 'none';
    restartButton.style.display = 'block';
}

// Función para reiniciar el juego y procesar imágenes en el servidor
function restartGame() {
    fetch('http://127.0.0.1:5000/process_images', { method: 'POST' })
        .then(response => response.text())
        .then(result => updateEcosystemState(result))
        .catch(error => {
            console.error('Error al procesar las imágenes:', error);
            alert('Hubo un error al procesar las imágenes.');
        });
}

// Cargar imágenes de peces y basura en el contenedor y hacer que se muevan
function loadImages() {
const fishImages = ["/static/processed/fish/BlenderLogo.png", "/static/processed/fish/ChatGPT_logo.png", "/static/processed/fish/equipo.png", "/static/processed/fish/polyh.png"];
const trashImages = ["/static/processed/trash/turbosquid.png"];

    fishImages.forEach(src => {
        createAndMoveImage(src, 'fish-container');
        fishCount++;
    });

    trashImages.forEach(src => {
        createAndMoveImage(src, 'trash-container');
        trashCount++;
    });
}

// Actualizar el estado del ecosistema según el resultado recibido del servidor
function updateEcosystemState(result) {
    const isHealthy = result === "animals";
    document.body.style.backgroundImage = isHealthy ? "url('/static/RIOPECES.jpg')" : "url('/static/RIOBASURA.jpg')";
    ecosystemStatus.textContent = isHealthy
        ? 'El ecosistema está sano. ¡Más peces que basura!'
        : 'El ecosistema está enfermo. ¡Más basura que peces!';
    ecosystemStatus.style.color = isHealthy ? '#4CAF50' : '#FF6347';
    ecosystemStatus.style.display = 'block';

    document.getElementById('trash-container').style.display = isHealthy ? 'none' : 'block';
    document.getElementById('fish-container').style.display = isHealthy ? 'block' : 'none';
}

// Evento para procesar imágenes y actualizar el estado del ecosistema
processButton.addEventListener('click', () => {
    fetch('http://127.0.0.1:5000/process_images', { method: 'POST' })
        .then(response => response.text())
        .then(result => updateEcosystemState(result))
        .catch(error => {
            console.error('Error al procesar las imágenes:', error);
            alert('Hubo un error al procesar las imágenes.');
        });
});

// Configurar eventos de inicio y reinicio, y cargar las imágenes al iniciar el juego
startButton.addEventListener('click', startTimer);
restartButton.addEventListener('click', restartGame);
loadImages();
// Agregar este código después de tu código existente en script.js

// Evento para manejar la subida de imágenes
document.getElementById('upload-button').addEventListener('click', () => {
    const fileInput = document.getElementById('file-input');
    const files = fileInput.files;

    if (files.length === 0) {
        alert('Por favor, selecciona al menos una imagen.');
        return;
    }

    const formData = new FormData();

    // Agregar las imágenes al FormData
    for (let i = 0; i < files.length; i++) {
        formData.append('file', files[i]); // 'file' es la clave que se usará en el servidor
    }

    // Enviar las imágenes al servidor
    fetch('http://127.0.0.1:5000/upload', {
        method: 'POST',
        body: formData,
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Error en la subida de imágenes');
        }
        return response.json();
    })
    .then(data => {
        console.log(data.message);
        // Aquí puedes llamar a la función para procesar las imágenes después de subirlas
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Hubo un error al subir las imágenes.');
    });
});