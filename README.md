
# 🧪 PDFApp

A **Streamlit web application** that provides an interactive interface to preprocess and analyze `.chi` files using [PDFgetX3](https://www.diffpy.org/products/pdfgetx.html). The app enables file upload, parameter customization, plotting, and visualization of processed outputs such as **S(q)**, **F(q)**, and **G(r)**.

---

## 📋 Features

- Upload `.chi` data and background files
- Select and preview uploaded files
- Customize preprocessing parameters:
  - Data format, wavelength, Q-range, R-range, etc.
- Interactive **Q vs I plot**
- Automatically generate `pdfgetx3.cfg`
- Run `pdfgetx3` via the app backend
- Visualize and download processed outputs:
  - `.fq`, `.sq`, and `.gr` plots
- One-click cleanup for uploaded data

---

## 🚀 Getting Started

### 🔧 Prerequisites

Make sure you have the following installed:

- [Python ≥ 3.7](https://www.python.org/downloads/)
- [PDFgetX3](https://www.diffpy.org/products/pdfgetx.html)
- [Streamlit](https://streamlit.io/)
- Required Python packages:

```bash
pip install streamlit plotly numpy
```

You must also ensure `pdfgetx3` is available in your system’s `$PATH` or installed via conda:

```bash
conda install -c diffpy pdfgetx3
```

---

## 📁 File Structure

```
pdf_processor_app/
│
├── pdfapp.py              # Streamlit app (this file)
├── pdfgetx3.cfg           # Template config file (will be modified per run)
├── pdfgetx3_temp/         # Temporary directory for processing (created automatically)
├── data_chi_files/        # Stores uploaded data files (created automatically)
└── README.md              # You're reading it!
```

---

## 💻 Usage

### 1. Run the app:

```bash
streamlit run pdfapp.py
```

### 2. Upload Files:

- Upload **multiple data files** (`.chi`) and a **background file** (`.chi`).
- Select one of the data files from the dropdown.

### 3. Set Parameters:

- Input material **composition** (e.g., `C8N2H22PbI6`)
- Choose:
  - Data format: `twotheta`, `QA`, or `Qnm`
  - Wavelength
  - Q-range and R-range
  - Background scale, rstep, rpoly, qmaxinst

### 4. Run:

Click the **"Run"** button to:

- Apply background subtraction
- Modify and apply `pdfgetx3.cfg`
- Run `pdfgetx3`
- Display:
  - **Q vs I** plot
  - **F(q)**, **S(q)**, **G(r)** plots
  - Downloadable output files

### 5. Clear Uploads:

Click **"Clear uploaded data files"** to clean up temporary files and reset the session.

---

## 📊 Output Files

The app generates:

- `.fq` → Fourier transformed function F(Q)
- `.sq` → Structure factor S(Q)
- `.gr` → Real-space pair distribution function G(r)

These files can be visualized directly within the app and downloaded.

---

## 🛠️ Under the Hood

### Key Components

- `st.file_uploader()` – Upload and store data/background files
- `pdfgetx3.cfg` – Configuration file for PDFgetX3, auto-modified
- `run_command()` – Executes shell command for `pdfgetx3`
- `plot_chi_file()` and `plot_gr_file()` – Plotting utilities for uploaded and processed data

---

## 📌 Notes

- `pdfgetx3` must be installed and callable in the shell.
- The `pdfgetx3.cfg` file should be available in the app directory and will be modified on-the-fly.
- This app creates two working folders:
  - `pdfgetx3_temp/` – Temporary for each run
  - `data_chi_files/` – Stores uploaded `.chi` files

---

## 🧹 Cleanup

All temporary data files are stored locally and can be deleted manually or via the **Clear uploaded data files** button.

---

## 📄 License

This project is open-source and free to use for academic or personal research purposes.
