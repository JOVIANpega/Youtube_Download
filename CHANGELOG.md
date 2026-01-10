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
