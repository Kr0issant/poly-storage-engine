const dropArea = document.querySelector(".drop-area");
const fileInput = document.querySelector('#file-upload');
const fileNameDisplay = document.querySelector('#file-name-display');

let files_list = [];

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
  files_list.push(...files);
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

    try {
        const response = await fetch('http://localhost:8000/upload', {
            method: 'POST',
            body: formData,
        });

        // if (response.ok) {
        //     const data = await response.json();
            
        //     resultsContainer.innerHTML = '';
        //     resultsContainer.innerHTML += `<h3>${data.filename}</h3>`;
            
        //     data.predictions.forEach(pred => {
        //         const scorePercent = (pred.score * 100).toFixed(2);
        //         resultsContainer.innerHTML += `
        //             <div class="prediction">
        //                 <span class="prediction-label">${pred.label}</span>
        //                 <span class="prediction-score">${scorePercent}%</span>
        //             </div>
        //         `;
        //     });
            
        //     resultsContainer.style.display = 'block';

        // } else {
        //     const errorData = await response.json();
        //     resultsContainer.innerHTML = `<p style="color: red;">Error: ${errorData.detail || 'Failed to classify.'}</p>`;
        //     resultsContainer.style.display = 'block';
        // }
    
    } catch (error) {
        resultsContainer.innerHTML = `<p style="color: #ff5353;">Network Error: ${error.message}</p>`;
        resultsContainer.style.display = 'block';
    }

    submitButton.disabled = false;
    submitButton.textContent = 'Upload Media';
});