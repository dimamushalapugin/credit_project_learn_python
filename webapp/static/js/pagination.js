        // JavaScript код для пагинации
document.addEventListener("DOMContentLoaded", function () {
    const tableRows = document.getElementsByClassName("table-row");
    const rowsPerPage = 10;
    const pageCount = Math.ceil(tableRows.length / rowsPerPage);

    function showPage(page) {
        const startIndex = (page - 1) * rowsPerPage;
       const endIndex = startIndex + rowsPerPage;

        for (let i = 0; i < tableRows.length; i++) {
            if (i >= startIndex && i < endIndex) {
                tableRows[i].style.display = "table-row";
            } else {
                tableRows[i].style.display = "none";
            }
        }
    }

    function createPagination() {
        const paginationContainer = document.createElement("ul");
        paginationContainer.classList.add("pagination");

        for (let i = 1; i <= pageCount; i++) {
            const listItem = document.createElement("li");
            const link = document.createElement("a");
            link.classList.add("page-link");
            link.textContent = i;

            if (i === 1) {
                link.classList.add("active");
            }

            listItem.appendChild(link);
            paginationContainer.appendChild(listItem);

            link.addEventListener("click", function (event) {
                event.preventDefault();

                const activeLink = document.querySelector(".pagination .active");
                activeLink.classList.remove("active");

                link.classList.add("active");

                showPage(i);
            });
        }

        const table = document.querySelector(".table");
        table.parentNode.insertBefore(paginationContainer, table.nextSibling);
    }

    showPage(1);
    createPagination();
});
