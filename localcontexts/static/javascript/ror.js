// Get value of dropdown of countries
const countrySelect = document.getElementById('id_country')
const institutionSelect = document.getElementById('institution-select')
const institutionTypeSelect = document.getElementById('institution-type-select')

const institutions = []

let removeAllOptions = (selectBox) => {
    while (selectBox.options.length > 1) {
        selectBox.remove(1);
    }
}

let getCountry = () => {
    let countryCode = countrySelect.value.toLowerCase()
    // TODO: Catch error when institutions don't exist for a country / there is no JSON file. 
    // Example: Anguilla and American Samoa has no json and no institutions

    // Based on what was selected in the dropdown, enter into endpoint and fetch
    const endpoint = `https://raw.githubusercontent.com/biocodellc/ror-parser/main/data/${countryCode}.json`
    fetch(endpoint)
        .then(res => {
            if (res.ok) {
                return res.json()
            } else if (res.status === 404) {
                return Promise.reject('404 Not Found')
            }
        })
        .then(data => {
            institutions.push(...data)
            // Sort institution list alphabetically by name
            institutions.sort((a,b) => (a.name > b.name) ? 1 : -1)
            getType()
        })
        .catch((error) => {console.error('Error:', error)})

    // Clear other dropdowns on country change    
    institutionTypeSelect.selectedIndex = 0
    institutionSelect.selectedIndex = 0

    removeAllOptions(institutionTypeSelect)
    removeAllOptions(institutionSelect)
}

let uniqueArray = (value, index, self) => {
    return self.indexOf(value) === index
}

let getType = () => {
    let typesArray = []
    institutions.forEach(item => {
        // If type is undefined, set type as Other
        if (item.types[0] == undefined) {
            item.types[0] = 'Other'
        }
        typesArray.push(item.types[0])
    })
    let uniqueTypes = typesArray.filter(uniqueArray)

    uniqueTypes.forEach(type => {
        let option = document.createElement('option')
        option.value = type.toLowerCase()
        option.innerHTML = type
        institutionTypeSelect.appendChild(option)    
    })
}

let populateInstitutions = () => {
    // Removes previous institution options
    removeAllOptions(institutionSelect)
    institutions.forEach(object => {
        if (object.types[0].toLowerCase() == institutionTypeSelect.value) {
            let option = document.createElement('option')
            option.value = object.name
            option.innerHTML = object.name
            institutionSelect.appendChild(option)
        }
    })
    // Resets institution options
    institutionSelect.selectedIndex = 0
}

countrySelect.addEventListener('change', getCountry)
institutionTypeSelect.addEventListener('change', populateInstitutions)


// Search by typing something in
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