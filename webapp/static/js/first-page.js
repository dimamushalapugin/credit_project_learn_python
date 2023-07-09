function updateCreditContracts() {
                    var investorSelect = document.getElementById("exampleDropdownFormInvestor");
                    var contractSelect = document.getElementById("typeCreditDogovor");

                    contractSelect.innerHTML = "";

                    if (investorSelect.value === "mkb") {
                        contractSelect.innerHTML += '<option value="МКБ1">МКБ1</option>';
                        contractSelect.innerHTML += '<option value="МКБ2">МКБ2</option>';
                        contractSelect.innerHTML += '<option value="МКБ3">МКБ3</option>';
                        contractSelect.innerHTML += '<option value="МКБ5">МКБ5</option>';
                    }
                    else if (investorSelect.value === "abb") {
                        contractSelect.innerHTML += '<option value="АББ4">АББ4</option>';
                        contractSelect.innerHTML += '<option value="АББ5">АББ5</option>';
                        contractSelect.innerHTML += '<option value="АББ6">АББ6</option>';
                        contractSelect.innerHTML += '<option value="АББ7">АББ7</option>';
                        contractSelect.innerHTML += '<option value="АББ8">АББ8</option>';
                        contractSelect.innerHTML += '<option value="АББ9">АББ9</option>';
                    }
                     else if (investorSelect.value === "mib") {
                        contractSelect.innerHTML += '<option value="МИБ1">МИБ1</option>';
                        contractSelect.innerHTML += '<option value="МИБ2">МИБ2</option>';
                        contractSelect.innerHTML += '<option value="МИБ3">МИБ3</option>';
                        contractSelect.innerHTML += '<option value="МИБ4">МИБ4</option>';
                    }
                    else if (investorSelect.value === "alfa") {
                        contractSelect.innerHTML += '<option value="Альфа1">Альфа1</option>';
                    }
                    else if (investorSelect.value === "pub") {
                        contractSelect.innerHTML += '<option value="ПУБ1">ПУБ1</option>';
                        contractSelect.innerHTML += '<option value="ПУБ2">ПУБ2</option>';
                        contractSelect.innerHTML += '<option value="ПУБ3">ПУБ3</option>';
                        contractSelect.innerHTML += '<option value="ПУБ4">ПУБ4</option>';
                        contractSelect.innerHTML += '<option value="ПУБ5">ПУБ5</option>';
                        contractSelect.innerHTML += '<option value="ПУБ6">ПУБ6</option>';
                        contractSelect.innerHTML += '<option value="ПУБ7">ПУБ7</option>';
                        contractSelect.innerHTML += '<option value="ПУБ8">ПУБ8</option>';
                    }
                    else if (investorSelect.value === "ural_fd") {
                        contractSelect.innerHTML += '<option value="Урал1">Урал1</option>';
                        contractSelect.innerHTML += '<option value="Урал2">Урал2</option>';
                        contractSelect.innerHTML += '<option value="Урал3">Урал3</option>';
                    }
                    else if (investorSelect.value === "keb") {
                        contractSelect.innerHTML += '<option value="КЕБ1">КЕБ1</option>';
                        contractSelect.innerHTML += '<option value="КЕБ2">КЕБ2</option>';
                    }
                    else if (investorSelect.value === "solid") {
                        contractSelect.innerHTML += '<option value="СОЛ1">СОЛ1</option>';
                        contractSelect.innerHTML += '<option value="СОЛ2">СОЛ2</option>';
                        contractSelect.innerHTML += '<option value="СОЛ3">СОЛ3</option>';
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