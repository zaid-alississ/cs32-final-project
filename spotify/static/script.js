const loginButton = document.getElementById("login-button");

if (loginButton) {
    loginButton.addEventListener("click", function () {
        alert("Spotify login is not connected yet. This button will later start the Spotify authorization flow.");
    });
}
