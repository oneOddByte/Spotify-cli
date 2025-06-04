import json
import webbrowser
from pathlib import Path
from urllib import parse

import pkce
import requests

client_id = "4fef09bdb7c74a278129cc8304da0986"
redirect_uri = "https://krishs-site.netlify.app/test"
# token_file = Path.home() / ".config" / "spotify-cli" / "tokens.txt"
token_file = Path.cwd() / "tokens.txt"


def storeTokens(tokens) -> None:
    if token_file.exists():
        with open(token_file, "w", encoding="utf-8") as file:
            json.dump(tokens, file)
    else:
        print("token file doesnt exist! Returning empty tokens")


def getTokens() -> tuple[str, str]:
    if token_file.exists():
        with open(token_file, "w", encoding="utf-8") as file:
            tokens = json.load(file)
            access_token = tokens["access_token"]
            refresh_token = tokens["refresh_token"]

            return (access_token, refresh_token)
    else:
        print("token file doesnt exist! Returning empty tokens")
        return ("", "")


def refreshAccessToken(refresh_token) -> tuple[str, str]:
    """
    Refreshes the access token using the refresh token

    Returns:
        str: New access token
        str: New refresh token
    """

    data = {
        "client_id": client_id,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }

    response = requests.request(
        "POST",
        "https://accounts.spotify.com/api/token",
        data=data,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
        },
        timeout=20,
    )

    if response.ok:
        print("Token refreshed!")
        data = response.json()

        access_token = data["access_token"]
        refresh_token = data["refresh_token"]

        return access_token, refresh_token

    else:
        print("Error refreshing token!")
        print("Error: ", response.status_code)

        return ("", "")


# Authentication using PKCE method (i cant store client-secret safely)
def auth() -> tuple[str, str]:
    """
    Authenticates the user with spotify using the PKCE flow and stores the tokens.

    Returns:
        tuple[str, str]: A tuple containing the access and refresh tokens.
    """

    # Get a code verifier
    codeVerifier = pkce.generate_code_verifier(64)

    # Get a code challenge
    codeChallenge = pkce.get_code_challenge(codeVerifier)

    # URL params
    params = {
        "client_id": client_id,
        "response_type": "code",
        "code_challenge_method": "S256",
        "code_challenge": codeChallenge,
        "redirect_uri": redirect_uri,
    }

    # Build the entire url by appending the params
    auth_url = "https://accounts.spotify.com/authorize?" + parse.urlencode(params)

    # Open the auth url in the browser
    print("Opening browser")
    webbrowser.open(auth_url)

    # Get the redirect response
    redirect_response = input("Paste the entire url after login: \n")

    # Parse the query string to get the code
    parsed: parse.ParseResult = parse.urlparse(redirect_response)
    code = parse.parse_qs(parsed.query).get("code", [None])[0]

    if not code:
        print("Received no code")
        error = parse.parse_qs(parsed.query).get("error", [None])[0]
        print("error: ", error)
    else:
        print("Received code")

    #
    # Requesting an access token
    token_params = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
        "client_id": client_id,
        "code_verifier": codeVerifier,
    }

    token_response: requests.Response = requests.request(
        "POST",
        "https://accounts.spotify.com/api/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data=token_params,
        timeout=10,
    )

    if token_response.ok:
        print("Got access token!")

        data = token_response.json()

        access_token = data["access_token"]
        refresh_token = data["refresh_token"]

        storeTokens({"access_token": access_token, "refresh_token": refresh_token})

        return access_token, refresh_token

    else:
        print("Access token response failed!")
        print("Error: ", token_response.status_code)

        return "", ""


getTokens()
# accTok, refTok = auth()
print()
print()
# accTok, refTok = refreshAccessToken(refTok)
