const dropArea = document.querySelector(".drop-area");
const fileInput = document.querySelector('#file-upload');
const fileNameDisplay = document.querySelector('#file-name-display');
const container = document.getElementById("gridContainer"); // to display SQL

const API_URL = "http://localhost:8000";

// Uploading
const allowedTypes = ['image/', 'video/', 'application/json'];

let files_list = [];

// storing json files
let table_list=[
  {
    "productId": "SKU-A-1034",
    "productName": "Ergonomic Office Chair",
    "category": "Furniture",
    "price": 249.99,
    "inStock": true,
    "stockCount": 85
  },
  {
    "productId": "SKU-B-2091",
    "productName": "Wireless Mechanical Keyboard",
    "category": "Electronics",
    "price": 129.50,
    "inStock": true,
    "stockCount": 150,
    "profit": 50
  },
  {
    "productId": "SKU-A-1035",
    "productName": "Adjustable Standing Desk",
    "category": "Furniture",
    "price": 499.00,
    "inStock": false,
    "stockCount": 0
  },
  {
    "productId": "SKU-C-8843",
    "productName": "4K Ultra-Wide Monitor",
    "category": "Electronics",
    "price": 799.99,
    "inStock": true,
    "stockCount": 42
  },
  {
    "productId": "SKU-B-2091",
    "productName": "Wireless Mechanical Keyboard",
    "category": "Electronics",
    "price": 129.50,
    "inStock": true,
    "stockCount": 150,
    "profit": 50
  },
  {
    "productId": "SKU-A-1035",
    "productName": "Adjustable Standing Desk",
    "category": "Furniture",
    "price": 499.00,
    "inStock": false,
    "stockCount": 0
  },
  {
    "productId": "SKU-C-8843",
    "productName": "4K Ultra-Wide Monitor",
    "category": "Electronics",
    "price": 799.99,
    "inStock": true,
    "stockCount": 42
  },
  {
    "productId": "SKU-B-2091",
    "productName": "Wireless Mechanical Keyboard",
    "category": "Electronics",
    "price": 129.50,
    "inStock": true,
    "stockCount": 150,
    "profit": 50
  },
  {
    "productId": "SKU-A-1035",
    "productName": "Adjustable Standing Desk",
    "category": "Furniture",
    "price": 499.00,
    "inStock": false,
    "stockCount": 0
  },
  {
    "productId": "SKU-C-8843",
    "productName": "4K Ultra-Wide Monitor",
    "category": "Electronics",
    "price": 799.99,
    "inStock": true,
    "stockCount": 42
  }
]

dropArea.addEventListener('click', () => {
    fileInput.click();
})

dropArea.addEventListener('dragover', (e) => {
  e.preventDefault();
    dropArea.classList.add('hover');
});

dropArea.addEventListener('dragleave', () => {
    dropArea.classList.remove('hover');
});

dropArea.addEventListener('drop', (e) => {
    e.preventDefault();
    dropArea.classList.remove('hover');
    const files = e.dataTransfer.files;

    for (const file of files) {
        if (allowedTypes.some(category => file.type.startsWith(category))) {
            files_list.push(file);
        }
    }

    displayFileNames();
});

fileInput.addEventListener('change', () => {
    files_list.push(...fileInput.files)
    displayFileNames();
});

function displayFileNames() {
    fileNameDisplay.innerHTML = '';
    
    files_list.forEach((file, index) => {
        const fileElement = document.createElement("p");
        fileElement.textContent = `${index}. ${file.name}`;
        fileElement.classList.add("file-item");

        fileElement.addEventListener('click', () => { removeFile(index); });

        fileNameDisplay.appendChild(fileElement);
    });
    
    if (files_list.length == 0) fileNameDisplay.innerHTML = "No file chosen";
}

function removeFile(index) {
    files_list.splice(index, 1);
    displayFileNames();
    fileInput.value = '';
}

const form = document.querySelector('.upload-form');
const resultsContainer = document.querySelector('#results-container');
const submitButton = document.querySelector('#submit-button');

const progressBar = document.querySelector("#progress-bar");

form.addEventListener('submit', async (event) => {
    event.preventDefault();

    if (files_list.length == 0) return;

    submitButton.disabled = true;
    submitButton.textContent = 'Uploading...';
    resultsContainer.style.display = 'none';

    const formData = new FormData();
    for (let i = 0; i < files_list.length; i++) {
        formData.append('files', files_list[i]);
    }

    const config = {
        onUploadProgress: (ProgressEvent) => {
            const percentCompleted = Math.round((ProgressEvent.loaded * 100) / ProgressEvent.total);

            progressBar.value = percentCompleted;
            progressBar.textContent = `${percentCompleted}%`;
        }
    }

    try {
        progressBar.classList.remove("hidden");
        progressBar.classList.add("upload");

        const response = await axios.post(`${API_URL}/upload`, formData, config);
        const task_id = response.data.task_id;

        progressBar.value = 0;
        progressBar.classList.remove("upload");
        progressBar.classList.add("process");
        submitButton.textContent = 'Processing...';

        await pollForProcessingProgress(task_id, 1000);
    
    } catch (error) {
        resultsContainer.innerHTML = `<p style="color: #ff5353;">Error: ${error.message}</p>`;
        resultsContainer.style.display = 'block';

        progressBar.classList.remove("upload");
        progressBar.classList.add("error");
        
        setTimeout(() => {
            files_list = [];
            displayFileNames()

            submitButton.disabled = false;
            submitButton.textContent = 'Upload Media';
            progressBar.classList.remove("error");
            progressBar.classList.add("hidden");
            resultsContainer.style.display = 'none';
        }, 1500);        
    }
});

// Processing
async function pollForProcessingProgress(task_id, poll_interval=1000) {
    const response = await fetch(`${API_URL}/progress/${task_id}`);
    
    if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
    }
    data = await response.json();

    if (data["status"] == "pending" || data["status"] == "processing") {
        progressBar.value = (100 * data["processed_files"]) / data["total_files"];

        // const progress = `Processing: ${data.processed_files}/${data.total_files} files complete.`;
        // const current = data.current_file ? `(Current: ${data.current_file})` : "";
        
        // if (processingStatus) { processingStatus.innerText = `${progress} ${current}`; }

        setTimeout(() => { pollForProcessingProgress(task_id); }, poll_interval);
    } else if (data["status"] == "complete") {
        console.log("complete");
        progressBar.value = 100;
        submitButton.textContent = "Upload Complete";
        getFilesystemAtUrl(currentUrl);
        setTimeout(() => {
            progressBar.classList.add("hidden");
            progressBar.classList.remove("process");

            files_list = [];
            displayFileNames()

            submitButton.disabled = false;
            submitButton.textContent = 'Upload Media';
            return;
        }, 1500);
    } else if (data["status"] == "error") {
        progressBar.classList.remove("process");
        progressBar.classList.add("error");
        throw new Error(`Something went wrong while processing file: ${data["current_file"]}`);
    }
}

// Searching
const searchForm = document.querySelector("#search-form");
const searchBar = document.querySelector("#search-bar");

searchForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    
    let response = await fetch(`${API_URL}/search?query=${searchBar.value}`);
    response = await response.json();
    let results = response["list"]

    filesystem.innerHTML = "";
    filesystem.classList.remove("file-open");

    if (results.length == 0) {

    } else {
        for (let obj of response["list"]) {
            const div = document.createElement("div");
            div.classList.add(obj["type"]);

            if (currentUrl.startsWith("media")) { div.textContent = obj["title"].replaceAll("_", " "); }
            else { div.textContent = obj["title"]; }

            div.addEventListener("dblclick", () => {getFilesystemAtUrl(obj["url"])});

            const deleteFileBtn = document.createElement("button");
            deleteFileBtn.textContent = "Delete";
            deleteFileBtn.classList.add("delete-file-btn");
            deleteFileBtn.addEventListener("click", async () => {await deleteFile(obj["url"].split("/").at(-1))});

            div.appendChild(deleteFileBtn);
            
            filesystem.appendChild(div);
        }
    }

    searchBar.value = "";
});

// View Options
const mediaBtn = document.querySelector("#view-media-btn");
const sqlBtn = document.querySelector("#view-sql-btn");
const nosqlBtn = document.querySelector("#view-nosql-btn");

mediaBtn.addEventListener("click", () => { currentUrl = "media"; getFilesystemAtUrl(); });
sqlBtn.addEventListener("click", () => { currentUrl = "sql"; getFilesystemAtUrl(); });
nosqlBtn.addEventListener("click", () => { currentUrl = "nosql"; getFilesystemAtUrl(); });

// File Explorer
const filesystem = document.querySelector(".filesystem");
const mediaBackBtn = document.querySelector(".media-back-btn");

let currentUrl = "media";

mediaBackBtn.addEventListener("click", () => {
    if (!["media", "sql", "nosql"].includes(currentUrl)) {
        const path = currentUrl.split("/");
        currentUrl = path.slice(0, -1).join("/");
        getFilesystemAtUrl(currentUrl);
    }
});

async function getFilesystemAtUrl(url=currentUrl) {
    let response = await fetch(`${API_URL}/explorer/${url}`);
    response = await response.json();

    console.log(response);

    currentUrl = url;
    filesystem.innerHTML = "";
    filesystem.classList.remove("file-open");

    if (response["list"].length == 0) { return; }

    const type = response["list"][0]["type"]

    if ("stream_url" in response["list"][0]) {
        const file_type = response["list"][0]["type"];
        if (file_type == "image") {
            console.log("image");
            const img = document.createElement("img");
            img.src = `${API_URL}/${response["list"][0]["stream_url"]}`;
            img.classList.add("view-image");
            
            filesystem.appendChild(img);
            filesystem.classList.add("file-open");
        } else if (file_type == "video") {
            console.log("video");
            const vid = document.createElement("video");
            vid.controls = true;
            vid.width = 600;
            vid.classList.add("view-video");
            
            const source = document.createElement("source");
            source.src = `${API_URL}/${response["list"][0]["stream_url"]}`;
            source.type = `${file_type}/${response["title"].split(".").at(-1)}`;
            
            vid.appendChild(source);
            filesystem.appendChild(vid);
            filesystem.classList.add("file-open");
        }
    } else if ("json_data" in response) {
        const json_data_type = response["json_data"]
        const data = response["list"]
        
        if (json_data_type == "table") {
            filesystem.appendChild(getTableDiv(data));
        } else if (json_data_type == "collection") {
            console.log("collection");
        }
    } else if (["folder", "table", "collection", "image", "video"].includes(type)) {
        for (let obj of response["list"]) {
            const div = document.createElement("div");
            div.classList.add(obj["type"]);

            if (currentUrl.startsWith("media")) { div.textContent = obj["title"].replaceAll("_", " "); }
            else { div.textContent = obj["title"]; }

            div.addEventListener("dblclick", () => {getFilesystemAtUrl(obj["url"])});

            if (obj["type"] != "folder") {
                const deleteFileBtn = document.createElement("button");
                deleteFileBtn.textContent = "Delete";
                deleteFileBtn.classList.add("delete-file-btn");
                deleteFileBtn.addEventListener("click", async () => {await deleteFile(obj["url"].split("/").at(-1))});

                div.appendChild(deleteFileBtn);
            }
            
            filesystem.appendChild(div);
        }
    }
}

 
function getTableDiv(json) {
    const columns = Object.keys(json[0]);

    const tableDiv = document.createElement("div");
    tableDiv.classList.add("table-div");
    tableDiv.style.gridTemplateColumns = `repeat(${columns.length}, minmax(100px, 1fr))`;

    columns.forEach(col => {
        const header = document.createElement("div");
        header.className = "grid-header";
        header.textContent = col;
        tableDiv.appendChild(header);
    });

    json.forEach(obj => {
        Object.keys(obj).forEach(col => {
            const cell = document.createElement("div");
            cell.className = "grid-cell";
            cell.textContent = obj[col] ?? "";
            tableDiv.appendChild(cell);
        });
    });

    return tableDiv;
}

async function deleteFile(object_id) {
    let response = await fetch(`${API_URL}/delete/${object_id}`);
    response = await response.json();
    getFilesystemAtUrl();
}

getFilesystemAtUrl();


function displayTableNames(){
    // Extract unique column names
    const columns = [...new Set(table_list.flatMap(obj => Object.keys(obj)))];

    // Set grid column count
    container.style.gridTemplateColumns = `repeat(${columns.length}, 1fr)`;

    // Add header cells
    columns.forEach(col => {
      const header = document.createElement("div");
      header.className = "grid-header";
      header.textContent = col;
      container.appendChild(header);
    });

    // Add rows
    table_list.forEach((obj, i) => {
      const rowDiv = document.createElement("div");
      rowDiv.className = "grid-row";
      columns.forEach(col => {
        const cell = document.createElement("div");
        cell.className = "grid-cell";
        cell.textContent = obj[col] ?? "";
        rowDiv.appendChild(cell);
      });
      // Append all cell DIVs inside row
      container.append(...rowDiv.children);
    });
}