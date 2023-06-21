from ..config import GOOGLE_CLIENT_ID, SWAP_TOKEN_ENDPOINT, API_LOCATION

google_login_javascript_client = f"""<!DOCTYPE html>
<html itemscope itemtype="http://schema.org/Article">
<head>
    <meta charset="UTF-8">
    <meta name="google-signin-client_id" content="{GOOGLE_CLIENT_ID}">
    <title>Google Login</title><script src="https://apis.google.com/js/platform.js" async defer></script>
    <body>
    <div class="g-signin2" data-onsuccess="onSignIn"></div>
    <script>function onSignIn(googleUser) {{
  
  var id_token = googleUser.getAuthResponse().id_token;
    var xhr = new XMLHttpRequest();
xhr.open('POST', '{API_LOCATION}{SWAP_TOKEN_ENDPOINT}');
xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
xhr.setRequestHeader('X-Google-OAuth2-Type', 'client');
xhr.onload = function() {{
   console.log('Signed in as: ' + xhr.responseText);
}};
xhr.send(id_token);
}}</script>
<div><br></div>
<a href="#" onclick="signOut();">Sign out</a>
<script>
  function signOut() {{
    var auth2 = gapi.auth2.getAuthInstance();
    auth2.signOut().then(function () {{
      console.log('User signed out.');
    }});
  }}
</script>
</body>
</html>"""