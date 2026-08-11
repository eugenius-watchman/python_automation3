/**
 * BSS YouTube Downloader
 * Client-side JavaScript for UI interactivity
 */

// DOM elts
const form = document.getElementById('downloadForm');
const videoUrl = document.getElementById('videoUrl');
const quality = document.getElementById('quality');
const outputName = document.getElementById('outputName');
const getInfo = document.getElementById('getInfo');
const videoInfo = document.getElementById('videoInfo');
const infoContent = document.getElementById('infoContent');
const progressSection = document.getElementById('progressSection');
const progressBar = document.getElementById('progressBar');
const progressText = document.getElementById('progressText');
const statusMessage = document.getElementById('statusMessage');

// stats elts
const totalDownloads = document.getElementById('totalDownloads');
const successfulDownloads = document.getElementById('successfulDownloads');
const failedDownloads = document.getElementById('failedDownloads');
const successRate = document.getElementById('successRate');

// initialise stats
let stats = {
    total: 0,
    successful: 0,
    failed: 0
}

/**
 * show toast notification
 */

function showToast(message, type = 'info'){
    // remove existing toast if any
    const existing = document.querySelector('.toast');
    if (existing) existing.remove();

    // create toast
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);

    // show animation
    setTimeout(() => toast.classList.add('show'), 100);

    //auto hide after 3 secs
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 400);
    }, 3000)
}

/**
 * update download stats for ui
 */
function updateStats(){
    totalDownloads.textContent = stats.total;
    successfulDownloads.textContent = stats.successful;
    failedDownloads.textContent = stats.failed;

    const rate = stats.total > 0
        ? Math.round((stats.successful / stats.total) * 100)
        : 0;
    successRate.textContent = `${rate}%`;
}

/**
 * upate progress bar
 */
function updateProgressBar(percentage, message) {
    const clamped = Math.min(100, Math.max(0, percentage));
    progressBar.style.width = `${clamepd}%`;
    progressText.textContent = `${Math.round(clamped)}%`;
    if (message) statusMessage.textContent = message;
}

/**
 * simulate...handle actual download progress
 * ...use websockets or polling
 */
function simulateProgress(){
    let progress = 0;
    const interval = setInterval(() => {
        progress += Math.random() * 15 + 5;
        if(progress >= 100){
            progress = 100;
            clearInterval(interval);
            statusMessage.textContent = 'Download Complete';
            progressBar.style.background = 'linear-gradient(90deg, #00e676, #00d4ff)';
            showToast('Download completed successfully!', 'success');

            // update stats
            stats.total++;
            stats.successful++;
            updateStats();

            setTimeout(() => {
                progressSection.style.display = 'none';
            }, 2000);
        }
        updateProgressBar(progress, `Downloading... ${Math.round(progress)}`)
    }, 300)

}

/**
 * handle form submission
 */
async function handleDownload(e) {
    e.preventDefault();

    const url = videoUrl.value.trim();
    if (!url) {
        showToast('Please enter YouTube URL', 'error');
        return;
    }

    // validate URL
    if (!url.includes('youtube/watch') && !url.includes('youtu.be/')) {
        showToast('Please enter a valid YouTube URL', 'error');
        return;
    }

    // show progress section
    progressSection.style.display = 'block';
    updateProgressBar(0, 'Initialising download...');

    // disable form
    const submitBtn = form.querySelector('button[type="submit"]');
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Downloading...';

    try {
        // get form data
        const qualityValue = quality.value;
        const outputNameValue = outputName.value.trim() || null;
        const getInfoValue = getInfo.checked;

        //in a real loop ...send this to backend API
        //...simulate the download

        if (getInfoValue) {
            statusMessage.textContent = 'Fetching video information...';
            await simulateInfoFetch(url);
        }

        statusMessage.textContent = 'Startinf download...';
        await simulateDownload(url, qualityValue, outputNameValue);

    }catch (error) {
        showToast(`Error: ${error.message}`, 'error');
        stats.total++;
        stats.failed++;
        updateStats();
        progressSection.style.display = 'none';
    }finally {
        // re-enable form
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="fas fa-download"></i> Download';
    }
}

/**
 * simulate fetching video info
 */
async function simulateInfoFetch(url) {
    // show info section
    videoInfo.style.display = 'block';

    // simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1000));

    //display mock info
    infoContent.innerHTML = `
        <div class="info-item"><span class="label">Title</span><span class="value">Sample YouTube Video</span></div>
        <div class="info-item"><span class="label">Views</span><span class="value">1,234,567</span></div>
        <div class="info-item"><span class="label">Duration</span><span class="value">5:00</span></div>
        <div class="info-item"><span class="label">Author</span><span class="value">BSS Gh.</span></div>
        <div class="info-item"><span class="label">Rating</span><span class="value">4.8*</span></div>
        <div class="info-item"><span class="label">Description</span><span class="value">Sample YouTube video description...</span></div>
        `;
    showToast('Video info retrieved!', 'success');
}

/**
 * simulate actual download
 */
async function simulateDownload(url, quality, outputName) {
    // show progress
    const steps = [
        {progress: 10, message: 'Connecting to YouTube...'},
        {progress: 25, message: 'Fetching video data...'},
        {progress: 40, message: `Preparing ${quality} quality stream...`},
        {progress: 60, message: 'Downloading video...'},
        {progress: 80, message: 'Almost through...'},
        {progress: 95, message: 'Finalising download...'}
    
    ];

    for (const step of steps) {
        await new Promise(resolve => setTimeout(resolve, 500));
        updateProgressBar(step.progress, step.message)
    }

    // complete
    updateProgressBar(100, 'Download complete!');
}

/**
 * handle Enter key in URL input
 */
videoUrl.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        form.dispatchEvent(new Event('submit'))
    }
});

/***
 * reset from clear
 */
videoUrl.addEventListener('input', () => {
    if(!videoUrl.value.trim()) {
        videoInfo.style.display = 'none';
        progressSection.style.display = 'none';
    }
});

// add form submit handler
form.addEventListener('submit', handleDownload);

// update stats
updateStats();

// console info
console.log('BSS YouTube Downloader loaded!')
console.log('Enter a YouTube URL to start downloading.')