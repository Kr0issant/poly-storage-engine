# Intelligent Multi-Modal Storage System (Poly-Storage Engine)

A submission for the "Intelligent Multi-Modal Storage System" challenge. This project provides a single interface to upload media or JSON data. The backend analyzes the input and routes it to either MongoDB (GridFS/Collections) or SQLite based on the data structure and content.

-----

## The Challenge

> **Problem Statement 2: Intelligent Multi-Modal Storage System**
>
> Design a storage system with a single frontend interface that processes and stores different types of data.
>
> **Key Requirements:**
>
>   * **Media:** Accept files, categorize them, and organize them into directories.
>   * **JSON:** Accept objects, determine if they fit SQL or NoSQL, and generate schemas/tables.
>   * **General:** Handle batch inputs and metadata.

-----

## Features

### Media Handling (Images/Videos)

  * **Classification:** Uses the CLIP model (`openai/clip-vit-base-patch32`) for zero-shot classification on uploaded media.
  * **File Organization:** Creates directories based on classification labels (e.g., `/dogs`, `/portraits`) and sorts files accordingly.
  * **Metadata:** Saves classification tags as metadata.
  * **Viewer:** Includes a UI for browsing directories and viewing media.
  * **Offline Capability:** The CLIP model is cached locally after the first run.

### JSON Handling

  * **Routing Logic:**
      * **MongoDB:** Used for nested or variable-schema objects.
      * **SQLite:** Used for flat, structured data.
  * **Schema Inference:** Analyzes incoming JSON batches to infer field types and relationships for SQL table creation.

### Frontend & UI

  * **Upload:** Single drag-and-drop zone for all file types.
  * **Visualization:** Renders directory trees for files, HTML tables for SQL data, and collapsible trees for JSON.
  * **Search:** Filters files based on generated metadata keywords.

### Backend

  * **Async Processing:** Built with FastAPI to handle concurrent uploads.
  * **Status Tracking:** Uses a `task_id` system to poll upload status and processing status separately (network transfer vs. model analysis).

-----

## Tech Stack

  * **Backend:** Python (FastAPI), Uvicorn
  * **Databases:** MongoDB (GridFS/NoSQL), SQLite3 (SQL)
  * **ML:** Hugging Face `transformers` & `torch` (CLIP)
  * **Frontend:** HTML, CSS, JavaScript

-----


### Prerequisites

  * **Python 3.13.5+**
  * A running **MongoDB** instance

-----

### Backend Setup

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/Kr0issant/poly-storage-engine.git
    cd poly-storage-engine
    ```

2.  **Create a virtual environment:**

    ##### For Linux / MacOS
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```
    ##### For Windows
    ```bash
    python -m venv .venv
    .venv\Scripts\activate
    ```

3.  **Install dependencies:**
    (This project uses `pyproject.toml` to manage dependencies. The following command installs the project and all required packages from it.)

    ```bash
    pip install .
    ```
    OR
    ```bash
    uv sync
    ```

4.  **Configure MongoDB URI (if applicable):**

      * If your MongoDB URI is something other than `http://localhost:27017`, change `MONGODB_URI` in `server/main.py`.

5.  **Run the server:**

    ```bash
    cd server
    python -m uvicorn main:app --reload
    ```
----
### Frontend Setup

1.  **Navigate to the frontend directory:**

    ```bash
    cd ../src
    ```

2.  **Open the HTML file:**

      * Launch the `index.html` file to a live server or use `start_server.bat` to automatically do it.

3.  **Start uploading:** The frontend will connect to the backend server (running by default at `http://localhost:8000`).

-----
## To-Do

* Username-Password based Authentication and Data Isolation
* Filtering for SQL Tables and JSON Objects
* PDF and OCR Support
* More optimized video processing for large files
* Better code documentation

-----
## Screenshots
  <img src="screenshots/screenshot (2).png" alt="Screenshot 2" width="500">
  <img src="screenshots/screenshot (1).png" alt="Screenshot 1" width="500">
  <img src="screenshots/screenshot (3).png" alt="Screenshot 3" width="500">
  <img src="screenshots/screenshot (4).png" alt="Screenshot 4" width="500">
  <img src="screenshots/screenshot (5).png" alt="Screenshot 5" width="500">
  <img src="screenshots/screenshot (6).png" alt="Screenshot 6" width="500">

-----

## License

This project is licensed under the MIT License. See the [LICENSE](https://www.google.com/search?q=LICENSE) file for details.
