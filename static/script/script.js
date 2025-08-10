
const navbR = document.querySelector(".navbar-d");
const drpDown = document.querySelector(".dropdown");

//buttons
const menuBtn = document.querySelector("#menu-btn");
const drpBtn = document.querySelector("#user-dropdown-btn")


menuBtn.addEventListener("click", function() {
    navbR.classList.toggle("active");
    document.addEventListener("click", function(e) {
        if(
            !e.composedPath().includes(menuBtn) &&
            !e.composedPath().includes(navbR)
         ) {
            navbR.classList.remove("active");
         }
    })
})

drpBtn.addEventListener("click", function() {
    drpDown.classList.toggle("active");
    document.addEventListener("click", function(e) {
        if(
            !e.composedPath().includes(drpBtn) &&
            !e.composedPath().includes(drpDown)
         ) {
            drpDown.classList.remove("active");
         }
    })
})


document.getElementById('book_title').addEventListener('input', function() {
    const query = this.value;
    if (query.length > 0) {
        fetch(`/book_list?query=${query}`)
            .then(response => response.json())
            .then(data => {
                const list = document.getElementById('autocomplete-list');
                list.innerHTML = '';
                data.forEach(item => {
                    const div = document.createElement('div');
                    div.classList.add('autocomplete-suggestion');
                    div.innerText = item.title;
                    div.addEventListener('click', function() {
                        document.getElementById('book_title').value = item.title;
                        list.innerHTML = '';
                    });
                    list.appendChild(div);
                });
            });
    } else {
        document.getElementById('autocomplete-list').innerHTML = '';
    }
});

document.getElementById('book-form').addEventListener('submit', function(event) {
    event.preventDefault();
    const bookTitle = document.getElementById('book_title').value;
    fetch('/recommend', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `book_title=${encodeURIComponent(bookTitle)}`
    })
    .then(response => response.json())
    .then(data => {
        const recommendationsList = document.getElementById('recommendations');
        recommendationsList.innerHTML = '';
        data.forEach(book => {
            const li = document.createElement('li');
            li.innerHTML = `
                <img src="${book.image_url}" alt="${book.title}" style="width: 50px; height: 75px;">
                <strong>${book.title}</strong><br>
                Yazar: ${book.authors}<br>
                Ortalama Puan: ${book.average_rating}<br>
                Oy Sayısı: ${book.ratings_count}
            `;
            recommendationsList.appendChild(li);
        });
    });
});
