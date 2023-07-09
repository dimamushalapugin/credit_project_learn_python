function updateCreditContracts() {
                    var investorSelect = document.getElementById("exampleDropdownFormInvestor");
                    var contractSelect = document.getElementById("typeCreditDogovor");

                    contractSelect.innerHTML = "";

                    if (investorSelect.value === "bank1") {
                        contractSelect.innerHTML += '<option value="Банк1 Договор1">Банк1 Договор1</option>';
                        contractSelect.innerHTML += '<option value="Банк1 Договор2">Банк1 Договор2</option>';
                    }
                    else if (investorSelect.value === "bank2") {
                        contractSelect.innerHTML += '<option value="Банк2 Договор1">Банк2 Договор1</option>';
                        contractSelect.innerHTML += '<option value="Банк2 Договор2">Банк2 Договор2</option>';
                    }
                     else if (investorSelect.value === "bank3") {
                        contractSelect.innerHTML += '<option value="Банк3 Договор1">Банк3 Договор1</option>';
                        contractSelect.innerHTML += '<option value="Банк3 Договор2">Банк3 Договор2</option>';
                        contractSelect.innerHTML += '<option value="Банк3 Договор3">Банк3 Договор3</option>';
                    }
                    else if (investorSelect.value === "bank4") {
                        contractSelect.innerHTML += '<option value="Банк4 Договор1">Банк4 Договор1</option>';
                    }
                    else if (investorSelect.value === "bank5") {
                        contractSelect.innerHTML += '<option value="Банк5 Договор1">Банк5 Договор1</option>';
                        contractSelect.innerHTML += '<option value="Банк5 Договор2">Банк5 Договор2</option>';
                    }
                    else if (investorSelect.value === "bank6") {
                        contractSelect.innerHTML += '<option value="Банк6 Договор1">Банк6 Договор1</option>';
                    }
                    else if (investorSelect.value === "bank7") {
                        contractSelect.innerHTML += '<option value="Банк7 Договор1">Банк7 Договор1</option>';
                    }
                    else if (investorSelect.value === "bank8") {
                        contractSelect.innerHTML += '<option value="Банк8 Договор1">Банк8 Договор1</option>';
                    }
                }

                window.onload = function() {
                    updateCreditContracts();
                };

function handleFile() {
                    const fileInput = document.getElementById('exampleFileInput');
                    const file = fileInput.files[0];

                    if (file) {
                        const formData = new FormData();
                        formData.append('uploaded_file', file);

                        fetch('/total_amount_from_xlsx', {
                            method: 'POST',
                            body: formData
                        })
                        .then(response => response.json())
                        .then(data => {
                        })
                        .catch(error => {
                            console.error('Ошибка:', error);
                        });
                    }
                }