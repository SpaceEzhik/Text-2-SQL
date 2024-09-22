    document.getElementById('loginForm').addEventListener('submit', async function(e) {
        e.preventDefault();

        const formData = new FormData(e.target);

        try {
            const response = await fetch(loginURL, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw errorData;
            }

            const result = await response.text();
            console.log('Response:', result);

            window.location.href = redirectURL;
        } catch (error) {
            console.error('Error:', error);
            let errorMessage = error.detail || "Произошла неизвестная ошибка";
            alert("Попробуйте войти повторно, так как произошла ошибка:\n" + errorMessage);
        }
    });