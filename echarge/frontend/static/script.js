const progressBar = document.getElementsByClassName('progress-bar')[0]
var duration = parseFloat(document.getElementById('duration').innerHTML.substr(50))*60
  
  setInterval(() => {
    const computedStyle = getComputedStyle(progressBar)
    const width = parseFloat(computedStyle.getPropertyValue('--width')) || 0
    progressBar.style.setProperty('--width', width + 2/duration)
    if (width >= 100) {   
      //nothing  
    }
  }, 20)


