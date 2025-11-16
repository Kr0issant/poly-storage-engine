# Intelligent Multi-Modal Storage System (Poly-Storage Engine)

A smart storage solution designed for the "Intelligent Multi-Modal Storage System" challenge. This project provides a single, unified frontend that intelligently accepts, analyzes, categorizes, and stores multiple types of data - whether it's media files (images, videos) or structured data (JSON) - into the most appropriate database (MongoDB/GridFS or SQLite) with zero user friction.

-----

## The Challenge

> **Problem Statement 2: Intelligent Multi-Modal Storage System**
>
> Design a smart storage system with a single frontend interface that intelligently processes and stores any type of data.
>
> **Key Requirements:**
>
>   * **For Media Files (Images/Videos):**
>       * Accept any media type through a unified frontend.
>       * Automatically analyze and categorize content.
>       * Place files with related existing media in appropriate directories.
>       * Create new directories for unique content categories.
>       * Organize subsequent related media into existing directories.
>   * **For Structured Data (JSON Objects):**
>       * Accept JSON objects through the same frontend.
>       * Intelligently determine whether SQL or NoSQL is more appropriate.
>       * Create the appropriate database entity automatically.
>       * For multiple JSON objects: analyze structure and generate complete schema with proper relationships.
>   * **Additional Considerations:**
>       * System should accept optional comments/metadata to aid in schema generation.
>       * Must handle both single and batch data inputs.
>       * Should maintain consistency and optimize for query performance.

-----

## Key Features

This system successfully implements all challenge requirements and adds several key enhancements for a robust, user-friendly experience.

### Intelligent Media Handling (Images/Videos)

  * **AI-Powered Categorization:** Utilizes a lightweight but highly accurate **CLIP model (`openai/clip-vit-base-patch32`)** to perform zero-shot classification on all uploaded media.
  * **Automatic Directory Management:** Automatically creates new directories (e.g., `/dogs`, `/beach_vacations`, `/technical_diagrams`) based on the AI's content analysis.
  * **Smart Sorting:** Subsequent related media is automatically filed into the correct existing directory, keeping the storage clean and organized.
  * **Metadata Generation:** The classification keywords (e.g., "dog", "park", "sunny") are saved as metadata with the file.
  * **Integrated Media Viewer:** A clean UI for browsing directories, viewing images, and streaming videos directly.

  #### Note:
  * No data leaves the server.
  * The CLIP Image classification model is downloaded to cache and saved during the first run. After that, internet is optional as the entire system can run completely offline.

### Smart Data Handling (JSON)

  * **Polyglot Persistence:** The system intelligently decides where to store incoming JSON data:
      * **MongoDB (NoSQL):** Used for complex, nested, or variable-schema objects.
      * **SQLite3 (SQL):** Used for flat, structured, relational data that fits a tabular model.
  * **Automatic Schema Generation:** When multiple JSON objects are uploaded, the system analyzes their complete structure to infer field types, relationships, and constraints, automatically creating the new table or collection.
  * Protections against SQL Injection Attacks

### Unified Frontend & Rich UI

  * **Single Upload Interface:** One simple drag-and-drop zone or file picker handles all data types.
  * **Data-Aware UI:** The frontend intelligently renders stored data:
      * **Files:** Displays directories, image thumbnails, and video player icons.
      * **SQL Tables:** Renders data in a clean, sortable HTML table.
      * **JSON Objects:** Displays nested JSON with collapsible/expandable fields for easy inspection.
  * **Powerful Smart Search:** A global search bar allows users to find files by matching search queries against the metadata keywords.

### High-Performance Asynchronous Backend

  * **Non-Blocking Endpoints:** The entire backend is built asynchronously, allowing it to handle many simultaneous uploads and requests without blocking.
  * **Real-Time Progress Tracking:** Every upload session (especially for batch uploads) is associated with a unique `task_id`.
  * **Dual Progress Bars:** The frontend uses this `task_id` to poll the backend, showing:
    1.  An **Upload Progress Bar** for the network transfer.
    2.  A **Processing Progress Bar** for the classification, database insertion, etc.

-----

## Tech Stack

  * **Backend:** Python (FastAPI), Uvicorn
  * **Databases:**
      * **MongoDB:** For NoSQL JSON storage and GridFS for file/media storage.
      * **SQLite3:** For relational SQL data storage.
  * **AI/ML:** Hugging Face `transformers` & `torch` for the CLIP model.
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

* []("screenshots/screenshot.png")
* []("screenshots/screenshot (2).png")
* []("screenshots/screenshot (3).png")
* []("screenshots/screenshot (4).png")
* []("screenshots/screenshot (5).png")

-----

## License

This project is licensed under the MIT License. See the [LICENSE](https://www.google.com/search?q=LICENSE) file for details.