if (window.location.href.includes('create-institution')) {
        // Get value of dropdown of countries
    var countrySelect = document.getElementById('id_country')
    var institutionSelect = document.getElementById('institution-select')
    var institutionTypeSelect = document.getElementById('institution-type-select')

    var institutions = []

    var removeAllOptions = (selectBox) => {
        while (selectBox.options.length > 1) {
            selectBox.remove(1);
        }
    }

    var getCountry = () => {
        let countryCode = countrySelect.value.toLowerCase()

        // Based on what was selected in the dropdown, enter into endpoint and fetch
        const endpoint = `https://raw.githubusercontent.com/biocodellc/ror-parser/main/data/${countryCode}.json`
        fetch(endpoint)
            .then(res => {
                if (res.ok) {
                    return res.json()
                } else if (res.status === 404) {
                    // Catch error when institutions don't exist for a country / there is no JSON file. 
                    // Example: Anguilla and American Samoa has no json / no institutions
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

    var uniqueArray = (value, index, self) => {
        return self.indexOf(value) === index
    }

    var getType = () => {
        let typesArray = []
        institutions.forEach(item => {
            // If type is undefined, set type as Other
            if (item.types[0] == undefined) {
                item.types[0] = 'Other'
            }
            typesArray.push(item.types[0])
        })
        let uniqueTypes = typesArray.filter(uniqueArray).sort()

        uniqueTypes.forEach(type => {
            let option = document.createElement('option')
            option.value = type.toLowerCase()
            option.innerHTML = type
            institutionTypeSelect.appendChild(option)    
        })
    }

    var populateInstitutions = () => {
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

    if (countrySelect && institutionTypeSelect){
        countrySelect.addEventListener('change', getCountry)
        institutionTypeSelect.addEventListener('change', populateInstitutions)    
    }

}