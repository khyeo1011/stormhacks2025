const friends = document.getElementById("frlist")
const aligning = document.getElementById("align")
let sigmavariable = false
friends.addEventListener('click', () => {
    if(sigmavariable === false){
        sigmavariable = true
        friends.classList.add("popup")
        aligning.innerHTML = "Friends List (click to minimize)"
    }
    else if(sigmavariable === true){
        sigmavariable = false
        friends.classList.remove("popup")
        aligning.innerHTML = "Click to check friends"
    }
})