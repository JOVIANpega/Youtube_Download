# Update Log v2.7.3

## Bug Fixes & Stability
- **🔥 Critical: iOS Client Support**:
  - **Fixed "Requested format is not available" error** - Switched from Android to iOS client for better cookie compatibility.
  - Android client doesn't support cookies properly, causing authentication failures.
  - iOS client provides more stable format extraction with authenticated sessions.
- **Enhanced Format Selector**:
  - Added multiple fallback options for format selection (separate streams → combined formats → best available).
  - Improved compatibility with iOS client which typically provides combined video+audio formats.
  - Prevents "Only images are available" errors by providing more flexible format matching.
- **Enhanced Cookie Validation**:
  - Added automatic validation for cookie files (checks if empty or too old).
  - Warns users if cookie file is older than 7 days (likely expired).
  - Provides clearer error messages when cookie files are invalid or unreadable.
- **JavaScript Runtime Support**:
  - Configured yt-dlp to use Node.js for YouTube extraction (resolves "No supported JavaScript runtime" warnings).
  - Improved player client selection strategy for better compatibility.
- **Better Error Diagnostics**:
  - Enhanced HTTP 403 error messages with specific troubleshooting steps.
  - Added debug logging for cookie file usage and validation.

---

# Update Log v2.7.0

## Bug Fixes & Stability
- **HTTP 403 Forbidden Fix**: 
  - Enhanced error handling for "Forbidden" errors with clear user guidance.
  - Added smart detection for 403 errors, prompting users to use the **"Cookies Authorization"** feature.
- **Maintenance Tools**:
  - **Clear Download Cache**: Added a button in Settings to clear `yt-dlp` cache, resolving stuck connections.
  - **Update Downloader**: Added a button to manually trigger `yt-dlp` updates directly from the GUI.
- **UX Improvements**:
  - Detailed error messages now provide actionable steps (Cookies, Proxy, Cache).
  - Improved button layout in the "Advanced Settings" section.


---

# Update Log v2.6.0

## New Features
- **Dynamic Theme System**: 
  - Added "Soft Indigo", "Classic Blue", and "Carbon Grey" professional themes.
  - **Instant Preview**: Themes now apply immediately upon selection for easier comparison.
  - Persist only after clicking "Save" to prevent accidental changes.
- **UI & Settings Optimization**:
  - **Editable Versioning**: Users can now manually set the version number in Settings, which automatically updates all internal metadata.
  - **Clean UI**: Removed the redundant "External Download" tab and clutter from the Settings page.
- **Packaging/Distribution**:
  - **Simplified Packaging**: Renamed `build_exe.bat` to **`EXE.bat`**.
  - **Smart Naming**: The resulting EXE file is now automatically named with the current version number (e.g., `YouTube_Downloader_v2.6.0.exe`).

## Bug Fixes
- Fixed file encoding/character corruption issues in `ui_settings.py`.
- Fixed `FontManager.get_font` argument mismatch.
- Standardized UI component spacing and color consistency across all tabs.

---

# Update Log v2.5.0

## New Features
- **Rate-Limit Bypass**: 
  - Added **Random Delay** option in Settings. This inserts a random 5-15s pause between requests and rotates User-Agents to mimic human behavior.
  - Added **Proxy Server** support. Users can now input a proxy/VPN URL (e.g., `http://127.0.0.1:7890`) to bypass IP blocks.
- **UI & Accessibility**:
  - Replaced the "Save Log" button with a much more useful **"Copy Name"** button.
  - **Copy Name** automatically strips file extensions (like `.mp4`) and ID tags, calculating the clean title for easy searching.
  - Enhanced Log Visibility: "Captured Filename" is now highlighted with a **Light Blue background** and **Dark Blue text** for better readability.
- **Performance**:
  - **Force IPv4**: All connections now force IPv4 to prevent hanging on some ISPs where IPv6 to YouTube is unstable.
  - **Skip Redundant Extraction**: Fixed a logic flaw where the app would re-download the webpage after parsing, saving ~1 minute per download.

## Known Issues & Usage Notes
- **YouTube Rate-Limiting (429 Errors)**:
  - If you see "This content isn't available... rate-limited", your IP is temporarily blocked by YouTube (usually for 1 hour).
  - **Solution 1**: Use the new "Proxy" setting if you have a VPN.
  - **Solution 2**: Enable "Random Delay" and wait for the block to expire.
- **Filename Display**:
  - The app creates temporary `.part` files during download. We have added logic to hide this extension from the UI and History once the merge is complete, so you only see the final filename.

## Technical Changes
- Switched default downloader client to `['android', 'ios', 'web']` priority to minimize 429 errors.
- Reduced extraction socket timeout to 15s to fail fast on bad proxies.
