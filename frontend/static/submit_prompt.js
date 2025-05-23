document.getElementById("myForm").addEventListener("submit", function(event) {
    event.preventDefault();
    var prompt = document.getElementById("prompt").value;
    var data = {prompt: prompt};

    var buttonText = document.querySelector(".button-text");
    var loadingText = document.querySelector(".loading-text");
    var dots = document.querySelector(".dots");

    buttonText.style.display = "none";
    loadingText.style.display = "inline";

    var dotCount = 0;
    var dotAnimation = setInterval(function() {
    dots.textContent = ".".repeat(dotCount);
    dotCount = (dotCount + 1) % 4;
    }, 500);

    fetch(generateURL, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        const contentType = response.headers.get("content-type");
        if (contentType && contentType.indexOf("text/html") !== -1) {
            // If the response is HTML, open it in a new window
            return response.text().then(html => {
                const newWindow = window.open("", "_blank");
                newWindow.document.write(html);
                newWindow.document.close();
                throw new Error("Redirected to HTML page");
            });
        }
        if (!response.ok) {
            return response.json().then(err => { throw err; });
        }
        return response.json();
    })
    .then(data => {
        console.log(data);
        var sqlQuery = data.sql_query;
        document.getElementById("response").value = sqlQuery;
    })
    .catch(error => {
        console.error("Error:", error);
        if (error.message === "Redirected to HTML page") {
            // This is not a real error, just a way to break out of the promise chain
            return;
        }
        let errorMessage = error.detail || "Произошла неизвестная ошибка";
        alert("Вам необходимо изменить запрос, так как произошла ошибка:\n" + errorMessage);
    })
    .finally(() => {
      clearInterval(dotAnimation);
      buttonText.style.display = "inline";
      loadingText.style.display = "none";
    });
});

document.getElementById("execute-button").addEventListener("click", function(event) {
    event.preventDefault();
    var sql_query = document.getElementById("response").value;

    if (sql_query.trim() === "") {
        alert("Ошибка: Отсутствует SQL запрос");
        return;
    }

    var data = {sql_query: sql_query};
    var buttonText = document.querySelector("#execute-button .button-text");
    var loadingText = document.querySelector("#execute-button .loading-text");
    var dots = document.querySelector("#execute-button .dots");

    buttonText.style.display = "none";
    loadingText.style.display = "inline";

    var dotCount = 0;
    var dotAnimation = setInterval(function() {
        dots.textContent = ".".repeat(dotCount);
        dotCount = (dotCount + 1) % 4;
    }, 500);

    fetch(executeURL, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(err => { throw err; });
        }
        return response.text();
    })
    .then(html => {
        var newWindow = window.open("", "_blank");
        newWindow.document.write(html);
        newWindow.document.close();
    })
    .catch(error => {
        console.error("Error:", error);
        let errorMessage = error.detail || "Произошла неизвестная ошибка";
        alert("Вам необходимо изменить запрос, так как произошла ошибка:\n" + errorMessage);
    })
    .finally(() => {
        clearInterval(dotAnimation);
        buttonText.style.display = "inline";
        loadingText.style.display = "none";
    });
});

document.getElementById("logout-button").addEventListener("click", function(event) {
        event.preventDefault();

        fetch(logoutURL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
        })
        .then(response => {
            if (response.ok) {
                console.log("Logout successful");
                window.location.href = redirectURL;
            } else {
                console.error("Logout failed");
            }
        })
        .catch(error => {
            console.error("Error during logout:", error);
        });
});
