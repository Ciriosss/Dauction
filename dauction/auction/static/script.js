const date = document.getElementById('expiration')
const remaining = document.getElementById('remaining')
const expiration =  Date.parse(date.textContent)

console.log(remaining)
console.log(expiration)
setInterval(()=>{

    const now = new Date().getTime()
    const diff = expiration - now

    const d = Math.floor(expiration / (1000 * 60 * 60 *24) - (now / (1000 * 60 * 60 *24)))
    const h = Math.floor((expiration / (1000 * 60 * 60 ) - (now / (1000 * 60 * 60 ))) %24)
    const m = Math.floor((expiration / (1000 * 60 ) - (now / (1000 * 60 ))) %60)
    const s = Math.floor((expiration / (1000 ) - (now / (1000))) %60)

    console.log(diff)
    if (diff > 0) {
        remaining.innerHTML =  d + " Days " + h + " Hours " + m + " Minutes " + s + " Seconds ";
    }else{
        remaining.innerHTML = "This auction is expirated";
    }

},1000)