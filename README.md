# Prompt Saver

A lightweight prompt library manager built for the Invoke community.

* FOR MAC USERS ONLY ONCE MOVED TO THE APPLICATIONS FOLDER BUT BEFORE FIRST USE, RUN THIS COMMAND IN TERMINAL xattr -dr com.apple.quarantine "/Applications/Prompt Saver.app"

## 🪟 Windows SmartScreen Warning (First Launch)

When you first run **Prompt Saver** on Windows, you may see a message saying **“Windows protected your PC”**.

This is **normal behavior** for unsigned or newly built desktop applications and does **not** mean the app is unsafe.

### Why this happens

Microsoft Defender SmartScreen may block apps that:

* Are not code-signed yet
* Are newly built or not widely downloaded
* Are distributed outside the Microsoft Store

### How to run the app anyway

1. On the **Windows protected your PC** screen, click **More info**
2. Click **Run anyway**
3. The app will start normally

Windows usually remembers this choice, so you should not see the warning again for the same build.

### Is it safe?

* Prompt Saver runs entirely locally
* It does not install system services
* It does not require administrator access
* It only accesses files and dialogs you explicitly allow

If you built the app yourself or downloaded it from the official project source, this warning is expected and safe to bypass.

### For developers

To permanently remove this warning for end users, the application must be code-signed with a trusted Windows certificate or distributed via the Microsoft Store.
