function populateAreaDropdown(stateDropdownID, areaDropdownID, areaCovered=null, hiddenStateID, API_KEY){

    const stateDropdown = document.getElementById(stateDropdownID)
    const areaDropdown = document.getElementById(areaDropdownID)

    const sisoCode = stateDropdown.value

    const selectedArea = areaCovered

    const selectedStateText = stateDropdown.options[stateDropdown.selectedIndex].text;
    document.getElementById(hiddenStateID).value = selectedStateText;

    var headers = new Headers();
    headers.append("X-CSCAPI-KEY", API_KEY);

    var requestOptions = {
        method: 'GET',
        headers: headers,
        redirect: 'follow'
    };

    fetch(`https://api.countrystatecity.in/v1/countries/MY/states/${sisoCode}/cities`, requestOptions)
        .then(response => response.json())
        .then(data => {
            areaDropdown.innerHTML = ''; // Reset area dropdown

            if (data && Object.keys(data).length > 1 ) {
                areaDropdown.disabled = false;

                // Populate the area dropdown
                data.forEach(area => {
                    const option = document.createElement("option");
                    option.value = area.name;
                    option.textContent = area.name;
                    areaDropdown.appendChild(option);
                });

                if (selectedArea) {
            // Find the option that matches the selected area and set it as selected
                const selectedOption = Array.from(areaDropdown.options).find(option => option.value === selectedArea);
                if (selectedOption) {
                    selectedOption.selected = true;
                }
            }

            } else {
                areaDropdown.disabled = true;
                areaDropdown.innerHTML = '<option value="">No area available for this state</option>';
            }
        })
        .catch(error => {
        console.error("Error fetching areas:", error);
        areaDropdown.innerHTML = '<option value="">Error loading areas</option>';
    });
}