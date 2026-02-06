# Garnet Grid Developer & Analyst Toolkit

A comprehensive arsenal of "missing tools" for high-performance development, analysis, and operations. These utilities are designed to be globally usable and solve recurring pain points.

> **Usage**: Scripts are located in the `tools/` directory. Run them from the project root.

## 🚀 Ops & Infrastructure (`tools/ops/`)
| Tool | Description | Status |
|------|-------------|--------|
| **[Git Nuke](file:///Users/Anonymous/Desktop/JGPTa/tools/ops/git_nuke.sh)** | `git_nuke.sh`<br>Radioactive reset. Removes all untracked files, resets to HEAD, and clears git hooks. Use when everything is broken. | ✅ Ready |
| **[Docker Reimagine](file:///Users/Anonymous/Desktop/JGPTa/tools/ops/docker_reimagine.sh)** | `docker_reimagine.sh`<br>Atomic reconstruction. Stops containers, prunes volumes, removes orphans, and rebuilds fresh. | ✅ Ready |
| **[Port Killer](file:///Users/Anonymous/Desktop/JGPTa/tools/ops/port_killer.sh)** | `port_killer.sh`<br>Finds and kills whatever process is hogging a specific port (e.g., 3000, 8000). | ✅ Ready |
| **[Log Sentinel](file:///Users/Anonymous/Desktop/JGPTa/tools/ops/log_sentinel.sh)** | `log_sentinel.sh`<br>Tails logs from all containers, highlights errors in red, and filters out noise. | ✅ Ready |

## 🕸️ Web & API (`tools/web/`)
| Tool | Description | Status |
|------|-------------|--------|
| **[JWT Decoder](file:///Users/Anonymous/Desktop/JGPTa/tools/web/jwt_decoder.html)** | `jwt_decoder.html`<br>Offline, privacy-focused token inspector. Paste a token to see claims, expiry, and roles. | ✅ Ready |
| **[API Stress Tester](file:///Users/Anonymous/Desktop/JGPTa/tools/web/stress_test.sh)** | `stress_test.sh`<br>Simple `ab` or `k6` wrapper to hammer an endpoint and report latency percentiles. | ✅ Ready |
| **[React Component Scanner](file:///Users/Anonymous/Desktop/JGPTa/tools/web/scan_components.js)** | `scan_components.js`<br>Audits React components for missing accessibility props or non-standard imports. | ✅ Ready |
| **[Local CORS Proxy](file:///Users/Anonymous/Desktop/JGPTa/tools/web/cors_proxy.js)** | `cors_proxy.js`<br>Lightweight Node server to bypass CORS during local development. | ✅ Ready |

## 📊 Power BI & Data Analysis (`tools/powerbi/`)
| Tool | Description | Status |
|------|-------------|--------|
| **[DAX Logic Generator](file:///Users/Anonymous/Desktop/JGPTa/tools/powerbi/dax_gen.py)** | `dax_gen.py`<br>Generates YTD/YoY/MOM measure formulas for a given base metric. | ✅ Ready |
| **[Theme Architect](file:///Users/Anonymous/Desktop/JGPTa/tools/powerbi/theme_gen.html)** | `theme_gen.html`<br>Visual color picker that outputs a valid Power BI JSON theme file. | ✅ Ready |
| **[PBIX Exploder](file:///Users/Anonymous/Desktop/JGPTa/tools/powerbi/pbix_extract.ps1)** | `pbix_extract.ps1`<br>Unzips .pbix files (they are zip archives!) to inspect Layout and DataMashup manually. | ✅ Ready |
| **[Measure Documenter](file:///Users/Anonymous/Desktop/JGPTa/tools/powerbi/doc_measures.py)** | `doc_measures.py`<br>Parses `.bim` or PBIP files to generate a Markdown dictionary of all metrics. | ✅ Ready |

## 🏢 Dynamics 365 (X++) (`tools/d365/`)
| Tool | Description | Status |
|------|-------------|--------|
| **[SysOperation Scaffolder](file:///Users/Anonymous/Desktop/JGPTa/tools/d365/scaffold_sysop.ps1)** | `scaffold_sysop.ps1`<br>Generates the Controller, Service, and DataContract class files from a template. | ✅ Ready |
| **[SQL-to-X++](file:///Users/Anonymous/Desktop/JGPTa/tools/d365/sql_to_xpp.py)** | `sql_to_xpp.py`<br>Translates standard SQL `SELECT * FROM T WHERE X=Y` into `select forcePlaceholders t where t.x == y`. | ✅ Ready |
| **[Label Hunter](file:///Users/Anonymous/Desktop/JGPTa/tools/d365/find_labels.ps1)** | `find_labels.ps1`<br>Scans source folder for clear-text strings that should be labels. | ✅ Ready |
| **[Table Browser Linker](file:///Users/Anonymous/Desktop/JGPTa/tools/d365/tbl_link.html)** | `tbl_link.html`<br>Bookmarklet to instantly open the Table Browser for the current form's datasource. | ✅ Ready |

## 🔒 Security & Secrets (`tools/sec/`)
| Tool | Description | Status |
|------|-------------|--------|
| **[Secret Generator](file:///Users/Anonymous/Desktop/JGPTa/tools/sec/gen_secret.py)** | `gen_secret.py`<br>Generates high-entropy 64-char strings for JWT_SECRET or API keys. | ✅ Ready |
| **[Env Var Auditor](file:///Users/Anonymous/Desktop/JGPTa/tools/sec/audit_env.sh)** | `audit_env.sh`<br>Checks `.env` against `.env.example` to find missing keys. | ✅ Ready |
