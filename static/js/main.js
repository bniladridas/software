document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const textModel = document.getElementById('text-model');
    const textPrompt = document.getElementById('text-prompt');
    const generateTextBtn = document.getElementById('generate-text-btn');
    const textOutput = document.getElementById('text-output');
    const copyTextBtn = document.getElementById('copy-text-btn');

    // Check for saved API key
    const savedApiKey = localStorage.getItem('togetherApiKey');

    // Add event listener for Enter key in the text prompt
    textPrompt.addEventListener('keydown', function(event) {
        // Check if the pressed key is Enter (key code 13)
        if (event.key === 'Enter' && !event.shiftKey) {
            // Prevent the default action (new line in textarea)
            event.preventDefault();

            // Trigger the generate button click
            generateTextBtn.click();
        }
    });

    const imageModel = document.getElementById('image-model');
    const imagePrompt = document.getElementById('image-prompt');
    const imageCount = document.getElementById('image-count');
    const generateImageBtn = document.getElementById('generate-image-btn');
    const imageOutput = document.getElementById('image-output');

    // Add event listener for Enter key in the image prompt
    imagePrompt.addEventListener('keydown', function(event) {
        // Check if the pressed key is Enter
        if (event.key === 'Enter' && !event.shiftKey) {
            // Prevent the default action (new line in textarea)
            event.preventDefault();

            // Trigger the generate button click
            generateImageBtn.click();
        }
    });

    // Loading overlay
    const loadingOverlay = document.getElementById('loading-overlay');
    const loadingText = document.getElementById('loading-text');

    // Show/hide loading overlay
    function showLoading(message = 'Processing') {
        loadingText.textContent = message;
        loadingOverlay.style.display = 'flex';

        // Update status bar if it exists
        const statusItem = document.querySelector('.software-status-item:first-child');
        if (statusItem) {
            statusItem.textContent = message;
        }
    }

    function hideLoading() {
        loadingOverlay.style.display = 'none';

        // Update status bar if it exists
        const statusItem = document.querySelector('.software-status-item:first-child');
        if (statusItem) {
            statusItem.textContent = 'Ready';
        }
    }

    // Text Generation
    async function generateText() {
        const prompt = textPrompt.value.trim();
        if (!prompt) {
            alert('Please enter a prompt');
            return null;
        }

        // Check if using Llama-4-Maverick model and if API key is needed
        if (textModel.value === "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8") {
            const apiKey = localStorage.getItem('togetherApiKey');
            if (!apiKey) {
                alert('To use the Llama-4-Maverick model, you need to set up your API key. Redirecting to API key setup page...');
                window.location.href = '/api-key';
                return null;
            }
        }

        showLoading('Generating text...');

        try {
            // Prepare request body
            const requestBody = {
                prompt: prompt,
                model: textModel.value
            };

            // Add API key if using Llama-4-Maverick
            if (textModel.value === "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8") {
                requestBody.apiKey = localStorage.getItem('togetherApiKey');
            }

            const response = await fetch('/api/generate-text', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestBody)
            });

            const data = await response.json();

            if (data.success) {
                textOutput.innerHTML = `<p>${data.text.replace(/\n/g, '<br>')}</p>`;
                return data;
            } else {
                textOutput.innerHTML = `<p class="error">Error: ${data.error}</p>`;
                return null;
            }
        } catch (error) {
            textOutput.innerHTML = `<p class="error">Error: ${error.message}</p>`;
            return null;
        } finally {
            hideLoading();
        }
    }

    // Attach generate text button event
    generateTextBtn.addEventListener('click', generateText);

    // Copy Text
    copyTextBtn.addEventListener('click', () => {
        const text = textOutput.innerText;
        if (text && !text.includes('Output will appear here')) {
            navigator.clipboard.writeText(text)
                .then(() => {
                    // Show copied notification
                    const originalIcon = copyTextBtn.innerHTML;
                    copyTextBtn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="green" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>';
                    setTimeout(() => {
                        copyTextBtn.innerHTML = originalIcon;
                    }, 2000);
                })
                .catch(err => {
                    console.error('Failed to copy text: ', err);
                });
        }
    });

    // Image Generation
    generateImageBtn.addEventListener('click', async () => {
        const prompt = imagePrompt.value.trim();
        if (!prompt) {
            alert('Please enter a prompt');
            return;
        }

        // Check if using FLUX.1-dev model and if API key is needed
        if (imageModel.value === "black-forest-labs/FLUX.1-dev") {
            const apiKey = localStorage.getItem('togetherApiKey');
            if (!apiKey) {
                alert('To use the FLUX.1-dev model, you need to set up your API key. Redirecting to API key setup page...');
                window.location.href = '/api-key';
                return;
            }
        }

        showLoading('Generating image...');

        try {
            // Prepare request body
            const requestBody = {
                prompt: prompt,
                model: imageModel.value,
                n: parseInt(imageCount ? imageCount.value : 1)
            };

            // Add API key if using FLUX.1-dev
            if (imageModel.value === "black-forest-labs/FLUX.1-dev") {
                requestBody.apiKey = localStorage.getItem('togetherApiKey');
            }

            const response = await fetch('/api/generate-image', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestBody)
            });

            const data = await response.json();

            if (data.success) {
                imageOutput.innerHTML = '';

                // Process base64 images if available
                if (data.images && data.images.length > 0) {
                    data.images.forEach((base64Image, index) => {
                        createImageItem(`data:image/png;base64,${base64Image}`, index, true);
                    });
                }

                // Process image URLs if available
                if (data.image_urls && data.image_urls.length > 0) {
                    data.image_urls.forEach((imageUrl, index) => {
                        createImageItem(imageUrl, index, false);
                    });
                }

                // If no images were generated, show an error
                if ((!data.images || data.images.length === 0) && (!data.image_urls || data.image_urls.length === 0)) {
                    imageOutput.innerHTML = '<p class="error">No images were generated. Please try again.</p>';
                }
            } else {
                imageOutput.innerHTML = `<p class="error">Error: ${data.error}</p>`;
            }
        } catch (error) {
            imageOutput.innerHTML = `<p class="error">Error: ${error.message}</p>`;
        } finally {
            hideLoading();
        }
    });

    // Helper Functions
    function createImageItem(imageSrc, index, isBase64) {
        const imageItem = document.createElement('div');
        imageItem.className = 'software-image-item';

        const img = document.createElement('img');
        img.src = imageSrc;
        img.alt = `Generated image ${index + 1}`;

        // Handle image loading errors
        img.onerror = () => {
            img.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgZmlsbD0iI2VlZSIvPjx0ZXh0IHg9IjUwJSIgeT0iNTAlIiBmb250LWZhbWlseT0iQXJpYWwsIHNhbnMtc2VyaWYiIGZvbnQtc2l6ZT0iMTQiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGRvbWluYW50LWJhc2VsaW5lPSJtaWRkbGUiIGZpbGw9IiM5OTkiPkltYWdlIGxvYWQgZXJyb3I8L3RleHQ+PC9zdmc+';
        };

        // Add download button
        const downloadBtn = document.createElement('button');
        downloadBtn.className = 'software-toolbar-button';
        downloadBtn.innerHTML = 'Download';
        downloadBtn.style.margin = '8px 0';
        downloadBtn.addEventListener('click', () => {
            downloadImage(imageSrc, `synthara-image-${index + 1}.png`);
        });

        imageItem.appendChild(img);
        imageItem.appendChild(downloadBtn);
        imageOutput.appendChild(imageItem);
    }

    function downloadImage(dataUrl, filename) {
        const link = document.createElement('a');
        link.href = dataUrl;
        link.download = filename;
        link.click();
    }
});
