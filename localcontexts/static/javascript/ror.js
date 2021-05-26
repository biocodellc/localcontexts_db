// TODO: Add ROR functionality

// Steps: 
// Dropdown of countries
// Based on what was selected in the dropdown, enter into endpoint and fetch
const endpoint = 'https://raw.githubusercontent.com/biocodellc/ror-parser/main/data/afghanistan.json'
fetch(endpoint)
    .then(res => res.json())
    .then(data => console.log(data))

let countrySelect = document.getElementById('id_country')
console.log(countrySelect)

// Create Institution
// const endpoint = `http://api.ror.org/organizations`
// const institutions = []
// fetch(endpoint)
//     .then(res => res.json())
//     .then(data => institutions.push(...data.items))

// function findMatches(wordToMatch, institutions) {
//     return institutions.filter(org => {
//         const regex = new RegExp(wordToMatch, 'gi')
//         return org.name.match(regex)
//     })
// }

// function displayMatches() {
//     const matchArray = findMatches(this.value, institutions)
//     const html = matchArray.map(org => {
//         const regex = new RegExp(this.value, 'gi')
//         const orgName = org.name.replace(regex, `<span class="hl">${this.value}</span>`)
//         return `
//             <li onmouseover="getOrgName(this)">
//                 <span class="name">${orgName}</span>
//             </li>
//         `
//     }).join('')
//     suggestions.innerHTML = html
// }

// const searchInput = document.querySelector('.search')
// const suggestions = document.querySelector('.suggestions')

// searchInput.addEventListener('change', displayMatches);
// searchInput.addEventListener('keyup', displayMatches);

// function getOrgName(elem) {
//     // console.log(elem.innerText)
//     searchInput.value = elem.innerText
//     let ul = document.getElementById('institution-suggestions')
//     // console.log(searchInput)
// }