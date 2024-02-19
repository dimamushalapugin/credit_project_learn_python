function updateCreditContracts() {
                    var investorSelect = document.getElementById("exampleDropdownFormInvestor");
                    var contractSelect = document.getElementById("typeCreditDogovor");

                    contractSelect.innerHTML = "";

                    if (investorSelect.value === "bank1") {
                        contractSelect.innerHTML += '<option value="№ 4502/3/2022/5942 от 22.12.2022">№ 4502/3/2022/5942 от 22.12.2022</option>';
                        contractSelect.innerHTML += '<option value="№ 4502/3/2019/2182 от 13.06.2019">№ 4502/3/2019/2182 от 13.06.2019</option>';
                        contractSelect.innerHTML += '<option value="№ 4502/3/2019/4312 от 08.11.2019">№ 4502/3/2019/4312 от 08.11.2019</option>';
                        contractSelect.innerHTML += '<option value="№ 4502/3/2021/1129 от 06.05.2021">№ 4502/3/2021/1129 от 06.05.2021</option>';
                        contractSelect.innerHTML += '<option value="№ 4502/3/2021/2736 от 11.11.2021">№ 4502/3/2021/2736 от 11.11.2021</option>';
                    }
                    else if (investorSelect.value === "bank2") {
                        contractSelect.innerHTML += '<option value="№ 060Y2L от 26.07.2022">№ 060Y2L от 26.07.2022</option>';
                    }
                     else if (investorSelect.value === "bank3") {
                        contractSelect.innerHTML += '<option value="№ 000001007603 от 01.12.2021">№ 000001007603 от 01.12.2021</option>';
                    }
                    else if (investorSelect.value === "bank4") {
                        contractSelect.innerHTML += '<option value="№ 8365-К от 26.03.2021">№ 8365-К от 26.03.2021</option>';
                        contractSelect.innerHTML += '<option value="№ 8871-К от 05.10.2021">№ 8871-К от 05.10.2021</option>';
                        contractSelect.innerHTML += '<option value="№ 9365-К от 06.07.2022">№ 9365-К от 06.07.2022</option>';
                        contractSelect.innerHTML += '<option value="№ 9847-К от 27.02.2023">№ 9847-К от 27.02.2023</option>';
                    }
                    else if (investorSelect.value === "bank5") {
                        contractSelect.innerHTML += '<option value="№ 0114/23 от 02.03.2023">№ 0114/23 от 02.03.2023</option>';
                        contractSelect.innerHTML += '<option value="№ 0683/21 от 12.10.2021">№ 0683/21 от 12.10.2021</option>';
                        contractSelect.innerHTML += '<option value="№ 0909/20 от 15.10.2020">№ 0909/20 от 15.10.2020</option>';
                        contractSelect.innerHTML += '<option value="№ 0277/21 от 30.04.2021">№ 0277/21 от 30.04.2021</option>';
                    }
                    else if (investorSelect.value === "bank6") {
                        contractSelect.innerHTML += '<option value="№ ПУБ 130/2022-КД/ЮЛ от 16.05.2022">№ ПУБ 130/2022-КД/ЮЛ от 16.05.2022</option>';
                        contractSelect.innerHTML += '<option value="№ ПУБ 220/2022-КД/ЮЛ от 27.06.2022">№ ПУБ 220/2022-КД/ЮЛ от 27.06.2022</option>';
                        contractSelect.innerHTML += '<option value="№ ПУБ 227/2022-КД/ЮЛ от 28.06.2022">№ ПУБ 227/2022-КД/ЮЛ от 28.06.2022</option>';
                        contractSelect.innerHTML += '<option value="№ ПУБ 777-КД/ЮЛ от 23.09.2021">№ ПУБ 777-КД/ЮЛ от 23.09.2021</option>';
                        contractSelect.innerHTML += '<option value="№ ПУБ 842-КД/ЮЛ от 26.11.2021">№ ПУБ 842-КД/ЮЛ от 26.11.2021</option>';
                    }
                    else if (investorSelect.value === "bank7") {
                        contractSelect.innerHTML += '<option value="№ 1400100274.082022КЛ от 04.10.2022">№ 1400100274.082022КЛ от 04.10.2022</option>';
                    }
                    else if (investorSelect.value === "bank8") {
                        contractSelect.innerHTML += '<option value="№ 0504-2021-2010 от 23.08.2021">№ 0504-2021-2010 от 23.08.2021</option>';
                        contractSelect.innerHTML += '<option value="№ 0504-2022-2006 от 18.04.2022">№ 0504-2022-2006 от 18.04.2022</option>';
                        contractSelect.innerHTML += '<option value="№ 0504-2022-2011 от 25.11.2022">№ 0504-2022-2011 от 25.11.2022</option>';
                    }
                    else if (investorSelect.value === "bank9") {
                        contractSelect.innerHTML += '<option value="№ Ю-3994-КЛВ от 08.02.2022">№ Ю-3994-КЛВ от 08.02.2022</option>';
                        contractSelect.innerHTML += '<option value="№ Ю-4043-КЛВ от 08.07.2022">№ Ю-4043-КЛВ от 08.07.2022</option>';
                        contractSelect.innerHTML += '<option value="№ Ю-4179-КЛВ от 31.03.2023">№ Ю-4179-КЛВ от 31.03.2023</option>';
                    }
                    else if (investorSelect.value === "bank10") {
                        contractSelect.innerHTML += '<option value="№ 4518/81-РКЛ/23 от 10.11.2023">№ 4518/81-РКЛ/23 от 10.11.2023</option>';
                    }

                    else if (investorSelect.value === "bank11") {
                        contractSelect.innerHTML += '<option value="№ 420F00OUT от 10.11.2023">№ 420F00OUT от 10.11.2023</option>';
                    }

                    else if (investorSelect.value === "bank12") {
                        contractSelect.innerHTML += '<option value="№ 23/КЛВ-09 от 15.08.2023">№ 23/КЛВ-09 от 15.08.2023</option>';
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