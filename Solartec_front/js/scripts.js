document.addEventListener('DOMContentLoaded', function() {
    const URL = 'http://127.0.0.1:4042';
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');

    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const tabId = button.getAttribute('data-tab');

            tabButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');

            tabContents.forEach(content => {
                content.classList.remove('active');
                if (content.id === tabId) {
                    content.classList.add('active');
                }
            });
        });
    });

    // Отправка сообщений
    const messageForm = document.getElementById('message_form');
    messageForm.addEventListener('submit', function(event) {
        event.preventDefault();

        const chatId = document.getElementById('chatIdMessage').value;
        const message = document.getElementById('messageContent').value;

        if (!chatId || chatId.length < 10) {
            alert('Идентификатор чата (номера телефона) должен содержать не менее 10 символов');
            return;
        }

        if (!message) {
            console.log('Сообщение пустое');
            return;
        }
        
        fetch(URL + '/send_message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ chatId, message })
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById('response').textContent = JSON.stringify(data.status);
            document.getElementById('messageContent').value = '';
        })
        .catch(error => {
            document.getElementById('response').textContent = `Error: ${error}`;
        });
    });

    // Форма локации
    const locationForm = document.getElementById('location_form');
    locationForm.addEventListener('submit', function(event) {
        event.preventDefault();

        const chatId = document.getElementById('chatIdLocation').value;
        // const chatId = `${document.getElementById('chatIdLocation').value}@c.us`;
        
        console.log(chatId);
        
        const nameLocation = document.getElementById('nameLocation').value;
        const address = document.getElementById('address').value;
        const latitude = document.getElementById('latitude').value;
        const longitude = document.getElementById('longitude').value;

        if (!chatId || chatId.length < 10) {
            alert('Идентификатор чата (номера телефона) должен содержать не менее 10 символов');
            return;
        }

        fetch(URL + '/send_location', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                chatId,
                nameLocation,
                address,
                latitude,
                longitude
            })
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById('response').textContent = JSON.stringify(data.status);
        })
        .catch(error => {
            document.getElementById('response').textContent = `Error: ${error}`;
        });
    });

    // Форма медиа
    const mediaForm = document.getElementById('media_form');
    mediaForm.addEventListener('submit', function(event) {
        event.preventDefault();

        const chatId = document.getElementById('chatIdMedia').value;
        const mediaFile = document.getElementById('mediaFile').files[0];
        const caption = document.getElementById('caption').value;

        if (!chatId || chatId.length < 10) {
            alert('Идентификатор чата (номера телефона) должен содержать не менее 10 символов');
            return;
        }

        if (!mediaFile) {
            console.log('Файл отсутствует');
            return;
        }

        const formData = new FormData();
        formData.append('chatId', chatId);
        formData.append('file', mediaFile);
        formData.append('caption', caption);
        formData.append('fileName', mediaFile.name);

        // определение типа медиафайла
        // image, video, audio
        const fileType = mediaFile.type.split('/')[0];
        if (fileType === 'image' || fileType === 'video' || fileType === 'audio') {
            formData.append('mediaType', fileType);

            fetch(URL + '/send_media', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('response').textContent = JSON.stringify(data.status);
                mediaForm.reset();
            })
            .catch(error => {
                document.getElementById('response').textContent = `Error: ${error}`;
            });
        } else {
            alert('Unsupported media type');
        }
    });
});
