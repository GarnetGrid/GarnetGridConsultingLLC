# JGPT Development & Distribution Workflow

This guide explains how to continue developing **JGPT** and update the **Secure Distribution Node** on the website.

## 1. The Architecture
*   **Live Website**: Does NOT run JGPT. It only hosts the *Source Code* for download.
*   **Development Workspace**: Located at `products/JGPT/JGPTa`. This is your "Source of Truth".
*   **Secure Vault**: Located at `secure-assets/`. This contains the encrypted `.zip` that clients download.

## 2. How to Develop (The Cycle)
To add features or fix bugs in JGPT:

1.  **Navigate to Source**:
    ```bash
    cd products/JGPT/JGPTa
    ```
2.  **Run Locally** (for testing):
    ```bash
    # Example (depending on your setup):
    docker-compose up
    # OR
    npm run dev
    ```
3.  **Code & Verify**: Make your changes in this folder.

## 3. How to Publish a New Version
Once your changes are tested and ready for "Enterprise Release":

1.  **Run the Publisher Script** (from the website root):
    ```bash
    ./scripts/publish_jgpt.sh
    ```
    *   *What this does*: It zips the entire contents of `products/JGPT/JGPTa`, excludes junk files (git, node_modules), and overwrites `secure-assets/JGPT_Enterprise_Source_v1.0.zip`.

2.  **Deploy Website**:
    *   Deploy the `GarnetGridConsultingLLC-website` folder to your host (Netlify/Vercel/FTP).
    *   The new `.zip` will now be available to anyone with the Portal Key (`Garnet2026`).

## 4. Emergency Patching
If you need to hotfix the downloadable asset without code changes (e.g., adding a README):
1.  Edit the file in `products/JGPT/JGPTa`.
2.  Run `./scripts/publish_jgpt.sh`.
