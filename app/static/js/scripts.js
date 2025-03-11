document.addEventListener("DOMContentLoaded", function() {
    console.log("Сторінка завантажена!");

    const deleteButtons = document.querySelectorAll('.delete-button');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(event) {
            const confirmed = confirm("Ви впевнені, що хочете видалити це фото?");
            if (!confirmed) {
                event.preventDefault();
            }
        });
    });
});
