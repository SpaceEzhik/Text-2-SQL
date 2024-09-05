document.addEventListener('DOMContentLoaded', function() {
    function redirect() {
        if (requestType.toLowerCase() === 'get') {
            window.location.href = redirectUrl;
        } else {
            var form = document.createElement('form');
            form.method = requestType;
            form.action = redirectUrl;
            document.body.appendChild(form);
            form.submit();
        }
    }

    // Redirect immediately
    redirect();
});