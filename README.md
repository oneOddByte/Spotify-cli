# 🎵 Spotify CLI (PKCE Auth) — *Discontinued*

A command-line tool to authenticate with the Spotify Web API using the **PKCE flow** (no client secret required), fetch saved tracks, and (formerly) analyze audio features to create playlists based on user **mood**.

## 💡 Original Idea

The project was designed to:
- Analyze the **audio features** (like energy, danceability, valence, etc.) of a user's saved tracks
- Detect a rough estimate of the user’s **current mood** or musical taste
- Automatically generate a **playlist** tailored to that mood

## 🔧 Features

- Authenticates via **PKCE** flow (no need to store client secret)
- Stores and refreshes access/refresh tokens securely
- Fetches:
  - User profile data
  - Saved songs
  - (Previously) audio features for tracks

## ⚠️ Status: Discontinued

This project has been discontinued due to the **deprecation of Spotify’s `audio-features` endpoint**, which was essential for mood-based playlist generation.

The code still works for basic authentication and fetching user data, and may be useful as a reference for:
- Implementing PKCE with `requests`
- Manually handling access/refresh tokens
- Interacting with REST APIs via Python

## 📁 Structure

- `auth()`: Starts PKCE login flow
- `storeTokens() / getTokens()`: Handles saving/loading tokens
- `refreshAccessToken()`: Refreshes expired access token
- `getAllSavedTracks()`: Fetches all liked/saved tracks
- `getAudioFeaturesWithIds()`: (⚠️ Deprecated)

## 📌 Notes

- No external Spotify SDK used — built purely with `requests` and `pkce`
- Tokens are stored at: `~/.config/spotify-cli/tokens.txt`
- Custom redirect URI: `https://krishs-site.netlify.app/test`

## 📚 Learnings

This project helped me understand:
- OAuth2 PKCE authentication flow
- Manual API calls without SDKs
- Token storage and refresh logic
- Spotify Web API structure

## 📦 Dependencies

- `requests`
- `pkce`
- `webbrowser`
- `urllib.parse`
- `pathlib`

## 🔚 Final Thoughts

While the mood-based playlist generator idea couldn’t be fully realized due to API limitations, this repo stands as a useful reference for future CLI and API-based experiments.

---

> _Made by Krishanth — 2025_
