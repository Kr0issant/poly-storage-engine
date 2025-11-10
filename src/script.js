const fileInput = document.querySelector('#file-upload');
const fileNameDisplay = document.querySelector('#file-name-display');

fileInput.addEventListener('change', () => {
    let fileNames = []
    for (const file of fileInput.files) {
        fileNames.push(file ? file.name : 'No file chosen');
    }
    fileNameDisplay.innerHTML = fileNames.join("<br>");
});

const form = document.querySelector('.upload-form');
const resultsContainer = document.querySelector('#results-container');
const submitButton = document.querySelector('#submit-button');

form.addEventListener('submit', async (event) => {
    event.preventDefault();

    submitButton.disabled = true;
    submitButton.textContent = 'Uploading...';
    resultsContainer.style.display = 'none';

    const formData = new FormData();
    for (let i = 0; i < fileInput.files.length; i++) {
        formData.append('files', fileInput.files[i]);
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
        resultsContainer.innerHTML = `<p style="color: red;">Network Error: ${error.message}</p>`;
        resultsContainer.style.display = 'block';
    }

    submitButton.disabled = false;
    submitButton.textContent = 'Upload Media';
});