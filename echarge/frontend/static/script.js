const progressBar = document.getElementsByClassName('progress-bar')[0]
var duration = parseFloat(document.getElementById('duration').getAttribute('value'))*60000
var connection = document.getElementById('connection').getAttribute('value')
  
function start() {
  startedAt = connection
  updateTarget(0)
  requestAnimationFrame(update)
}
  
function update() {
  let elapsedTime = Date.now() - startedAt
  
  // playback is a value between 0 and 1
  // being 0 the start of the charge and 1 its end
  let playback = elapsedTime / duration
  
  updateTarget(playback)
  requestAnimationFrame(update)

}
  
function updateTarget(playback) {
  // Update the width of the bar based on the playback position
  progressBar.style.setProperty('--width', playback*100)
  }
  
  start()
