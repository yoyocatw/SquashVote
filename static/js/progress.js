document.addEventListener('DOMContentLoaded', function() {
    // Get references to elements on the page
    const progressBar = document.getElementById('progress-bar');
    const timeDisplay = document.getElementById('time-remaining');
    const progressPercentDisplay = document.getElementById('progress-percent');
    
    // Retrieve initial values from data attributes on the progress element.
    const total = parseInt(progressBar.getAttribute('data-total'));
    let remaining = parseInt(progressBar.getAttribute('data-remaining'));

    // Set up a timer to update the progress every second.
    const timer = setInterval(() => {
      if (remaining > 0) {
        remaining--;
        timeDisplay.innerText = remaining;
        
        // Calculate progress (percentage of the interval elapsed)
        const progressPercent = ((total - remaining) / total) * 100;
        progressBar.value = progressPercent;
        progressPercentDisplay.innerText = Math.floor(progressPercent);
      } else {
        clearInterval(timer);
        timeDisplay.innerText = '0';
        progressBar.value = 100;
        progressPercentDisplay.innerText = '100';
      }
    }, 1000);
});