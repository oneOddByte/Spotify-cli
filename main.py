import json
import webbrowser
from pathlib import Path
from pprint import pprint
from typing import List
from urllib import parse

import pkce
import requests

# client_id for the app registered in the dev-dashboard
client_id = "4fef09bdb7c74a278129cc8304da0986"

# uri where spotify's login screen redirects to
redirect_uri = "https://krishs-site.netlify.app/test"

token_file = Path.home() / ".config" / "spotify-cli" / "tokens.txt"


def storeTokens(tokens: tuple[str, str]) -> None:
    """
    Stores the given tokens in the token_file

    Parameters:
    tuple[str, str]: access_token, refresh_token
    """

    # unpacking the tokens
    accTok, refTok = tokens

    tokens_json = {"access_token": accTok, "refresh_token": refTok}

    if token_file.exists():
        with open(token_file, "w", encoding="utf-8") as file:
            json.dump(tokens_json, file)
    else:
        print("token file doesnt exist! Returning empty tokens")


def getTokens() -> tuple[str, str]:
    """
    Reads and returns the tokens from the file

    Returns:
    tuple[str, str]: access_token, refresh_token
    """

    if token_file.exists():
        with open(token_file, "r", encoding="utf-8") as file:
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

    # Constructing the data as per spotify's API
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
        "scope": "user-library-read user-read-private user-read-email user-read-playback-state",
    }

    # Build the entire url by appending the params
    auth_url = "https://accounts.spotify.com/authorize?" + parse.urlencode(params)

    # Open the auth url in the browser
    print("Opening browser")
    webbrowser.open(auth_url)

    # Get the redirect response as the input
    redirect_response = input("Paste the entire url after login: \n")

    # Parse the query string to get the code
    parsed: parse.ParseResult = parse.urlparse(redirect_response)
    auth_code = parse.parse_qs(parsed.query).get("code", [None])[0]

    if not auth_code:
        print("Received no code")
        error = parse.parse_qs(parsed.query).get("error", [None])[0]
        print("error: ", error)
    else:
        print("Received code")

    #
    # Requesting an access token using the authentication code
    token_params = {
        "grant_type": "authorization_code",
        "code": auth_code,
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

        # Get the tokens from the response
        access_token = data["access_token"]
        refresh_token = data["refresh_token"]

        # Store the tokens
        storeTokens((access_token, refresh_token))

        return (access_token, refresh_token)

    else:
        print("Access token response failed!")
        print("Error: ", token_response.status_code)

        return ("", "")


def GETRequestAsDict(endpoint, name="obj", params={}) -> dict:
    """
    Template for getting GET requests from spotify
    """

    (accTok, _) = getTokens()

    response: requests.Response = requests.request(
        "GET",
        f"https://api.spotify.com/v1/{endpoint}",
        headers={"Authorization": f"Bearer {accTok}"},
        params=params,
        timeout=10,
    )

    if response.ok:
        return response.json()
    else:
        print(f"Error obtaining {name} data!")
        print("Error: ", response.status_code, " - ", response.text)
        return {"": ""}


def getCurrentUserData() -> dict[str, str]:
    """
    Returns current users data

    Returns:
    dict[str, str]: JSON format of the data
    """

    (accTok, _) = getTokens()

    response: requests.Response = requests.request(
        "GET",
        "https://api.spotify.com/v1/me",
        headers={"Authorization": f"Bearer {accTok}"},
        timeout=10,
    )

    if response.ok:
        print("obtained current user data!")
        print()
        return response.json()
    else:
        print("Error obtaining user data!")
        print("Error: ", response.status_code)
        return {"": ""}


def getAllSavedTracks() -> list:
    """
    Fetches all saved tracks from the current user's Spotify library. Also handles pagination to get all the tracks.

    Returns:
        List of track names.
    """

    tracks = []
    offset = 0
    limit = 50

    while True:
        userTracks = GETRequestAsDict(
            "me/tracks", name="user tracks", params={"limit": limit, "offset": offset}
        )

        if "items" not in userTracks:
            break  # Something went wrong

        for item in userTracks["items"]:
            track = item["track"]
            if track:  # Safety check
                tracks.append(track)

        # next contains the url to the next page of items
        # if it is none, there are no more items
        if userTracks["next"] is None:
            break

        offset += limit

    return tracks


# ISSUE: This feature is depreciated!!!
def getAudioFeaturesWithIds(ids: List[str]) -> List[str]:
    """
    !! THIS FEATURE IS DEPRECIATED !!
    Returns the audio-features of the songs with given IDs

    Returns:
    List[str]: list containing the audio-features
    """

    ids_param = ",".join(ids)

    response = GETRequestAsDict(
        "audio-features", name="audio features", params={"ids": ids_param}
    )

    if "audio_features" not in response:
        print("something went wrong: audio features")

    return list(response.get("audio_features", []))


# Authenticate and store the access and refresh tokens
# storeTokens(auth())

# Refresh and store the tokens
(currentAccTok, currentRefTok) = getTokens()
newAccTok, newRefTok = refreshAccessToken(currentRefTok)
storeTokens((newAccTok, newRefTok))

tracks = getAllSavedTracks()

trackNames = [track["name"] for track in tracks]
pprint(trackNames)

trackIds = [track["id"] for track in tracks]
# BUG: This causes issues as the api is depreciated
pprint(getAudioFeaturesWithIds(trackIds[:5]))
